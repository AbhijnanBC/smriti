"""
claims/__init__.py — Public API for Phase 4: Claim Construction.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.claims import extract_claims, Phase4Result

They NEVER import from internal modules:
    claims.parser, claims.boundaries, claims.structure,
    claims.annotation, claims.degradation, claims.builder,
    claims.validator, claims.statistics, claims.models, claims.rules

Public contract:
    extract_claims(semantic_sentences: List[SemanticSentence]) → Phase4Result

That is the ONLY function that crosses the Phase 4 boundary.

Everything inside this module (parser, boundaries, structure, annotation,
degradation, builder, validator) is an implementation detail.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import structlog

from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.builder import build_claim
from smriti.claims.classifier import AssertionClassifier
from smriti.claims.degradation import DegradationHandler
from smriti.claims.parser import BaseParser, SpaCyParser  # <-- REPLACED
from smriti.claims.statistics import Phase4StatsCollector
from smriti.claims.structure import StructureExtractor
from smriti.claims.validator import validate_claims
from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    AssertionType,
    Claim,
    ClaimWarning,
    DiscardedCandidate,
    ExtractionMode,
    Phase4Stats,
    SemanticSentence,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import ClaimValidationError, Phase4Error

logger = structlog.get_logger(__name__)


# ── Public result types ────────────────────────────────────────────────────────


@dataclass
class SentenceExtractionResult:
    """Phase 4 result for a single SemanticSentence."""

    sentence_id: str
    claims: list[Claim]
    warnings: list[ClaimWarning]
    error: str | None = None
    # NEW: sentences classified as something other than DECLARATIVE_ASSERTION
    # never reach Claim construction, but are never silently dropped either —
    # they are recorded here in full (text + classified type + reason).
    discarded_candidates: list[DiscardedCandidate] = field(default_factory=list)

    @property
    def claim_count(self) -> int:
        return len(self.claims)


@dataclass
class Phase4Result:
    """
    Complete output of Phase 4 — all claims extracted from all sentences.
    This is what Phase 5 (Embedding) receives.
    """

    sentence_results: list[SentenceExtractionResult]
    stats: Phase4Stats
    run_id: str
    manifest_path: Path | None = None

    @property
    def all_claims(self) -> list[Claim]:
        """Flat list of all claims across all sentences."""
        result = []
        for sr in self.sentence_results:
            result.extend(sr.claims)
        return result

    @property
    def all_discarded_candidates(self) -> list[DiscardedCandidate]:
        """
        Flat list of every sentence that was classified as something other
        than DECLARATIVE_ASSERTION, across all sentences. Nothing filtered
        out of the knowledge graph is lost — it is all here, with its
        classified AssertionType and text intact.
        """
        result = []
        for sr in self.sentence_results:
            result.extend(sr.discarded_candidates)
        return result

    @property
    def total_claims(self) -> int:
        return sum(sr.claim_count for sr in self.sentence_results)

    @property
    def successful_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is None)

    @property
    def failed_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is not None)

    def to_discarded_dataset_json(self) -> str:
        """
        Serialize every DiscardedCandidate to JSON for audit purposes.
        Written to artifacts/run_{id}/phase4/discarded_candidates.json.

        This is the lossless side-channel: any sentence that did not become
        a Claim is fully recoverable from this file, along with why.
        """
        records = []
        for dc in self.all_discarded_candidates:
            records.append(
                {
                    "sentence_id": dc.sentence_id,
                    "document_id": dc.document_id,
                    "text": dc.text,
                    "assertion_type": dc.assertion_type.value,
                    "origin_block_type": dc.origin_block_type,
                    "reason": dc.reason,
                    "source_path": str(dc.source_path),
                    "context": dc.context,
                }
            )
        return json.dumps(records, indent=2, ensure_ascii=False)

    def to_dataset_json(self) -> str:
        """
        Serialize all Claims to JSON for Phase 5.
        Written to artifacts/run_{id}/phase4/dataset.json.
        """
        records = []
        for claim in self.all_claims:
            record = {
                "claim_id": claim.claim_id,
                "sentence_id": claim.sentence_id,
                "document_id": claim.document_id,
                "text": claim.text,
                "content_hash": claim.content_hash,  # NEW
                "context": claim.context,
                "source_path": str(claim.source_path),
                "extraction_mode": claim.extraction_mode.value,
                "schema_version": claim.schema_version,
                "rule_version": claim.rule_version,  # NEW
                "is_negated": claim.assertion_metadata.is_negated,
                "modality": claim.assertion_metadata.modality.value,
                "is_conditional": claim.assertion_metadata.is_conditional,
                "is_comparative": claim.assertion_metadata.is_comparative,
                "is_attributed": claim.assertion_metadata.is_attributed,
                "attributed_to": claim.assertion_metadata.attributed_to,
                "provenance": {
                    "sentence_id": claim.provenance.sentence_id,
                    "document_id": claim.provenance.document_id,
                    "source_path": str(claim.provenance.source_path),
                    "sentence_context": claim.provenance.sentence_context,
                    "sentence_position": claim.provenance.sentence_position,
                    "source_char_spans": list(claim.provenance.source_char_spans),  # NEW
                    "source_token_ids": list(claim.provenance.source_token_ids),  # NEW
                    "reconstruction_rule": claim.provenance.reconstruction_rule,  # NEW
                },
            }
            # Include SVO if available
            if claim.structured_assertion:
                record["svo"] = {
                    "subject": claim.structured_assertion.subject,
                    "predicate": claim.structured_assertion.predicate,
                    "object": claim.structured_assertion.object,
                }
            else:
                record["svo"] = None

            records.append(record)

        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ───────────────────────────────────────────────────────


def extract_claims_from_sentence(
    sentence: SemanticSentence,
    parser: BaseParser,
    boundary_detector: BoundaryDetector,
    structure_extractor: StructureExtractor,
    annotator: AssertionAnnotator,
    degradation_handler: DegradationHandler,
    stats_collector: Phase4StatsCollector,
    max_claims: int,
    global_seen_ids: dict,
    classifier: AssertionClassifier | None = None,
) -> SentenceExtractionResult:
    """
    Extract claims from a single SemanticSentence.

    This is the 8-stage compiler pipeline applied to one sentence: a
    classification gate now runs before Stage 2 (boundary detection). Only
    sentences classified as AssertionType.DECLARATIVE_ASSERTION proceed into
    claim construction; everything else (metadata lines, headings, list
    items, table cells, questions, procedural instructions, fragments, code,
    quotes) is recorded as a DiscardedCandidate and never becomes a Claim.

    Args:
        classifier: AssertionClassifier to use. Defaults to a fresh instance
            when omitted (the classifier is stateless and cheap to build) —
            callers that process many sentences should pass a shared instance.

    Returns:
        SentenceExtractionResult (never raises — errors are captured).
    """
    sentence_id = sentence.sentence_id
    all_warnings: list[ClaimWarning] = []
    classifier = classifier or AssertionClassifier()

    try:
        stats_collector.record_sentence_processed()

        # Stage 1: Linguistic Analysis
        parsed = parser.parse(sentence)
        if not parsed.parse_ok:
            stats_collector.record_parser_failure()
            all_warnings.append(ClaimWarning.CLM_PARSER_FAILURE)

        # Stage 1.5: Assertion-type classification (the gate).
        # This MUST happen before any Claim is ever constructed. Only
        # DECLARATIVE_ASSERTION proceeds; everything else is discarded here,
        # fully recorded, and returned to the caller instead of a claim list.
        assertion_type, classify_reason = classifier.classify(sentence, parsed)
        stats_collector.record_classification(assertion_type)

        if assertion_type != AssertionType.DECLARATIVE_ASSERTION:
            discarded = DiscardedCandidate(
                sentence_id=sentence.sentence_id,
                document_id=sentence.document_id,
                text=sentence.text,
                assertion_type=assertion_type,
                origin_block_type=sentence.origin_block_type,
                reason=classify_reason,
                source_path=sentence.source_path,
                context=sentence.context,
            )
            stats_collector.record_warnings(all_warnings)
            return SentenceExtractionResult(
                sentence_id=sentence_id,
                claims=[],
                warnings=all_warnings,
                discarded_candidates=[discarded],
            )

        # Stage 2–3: Assertion Analysis + Boundary Detection
        candidates = boundary_detector.detect(parsed)
        stats_collector.record_boundary_split(len(candidates))

        # Enforce max claims per sentence
        if len(candidates) > max_claims:
            candidates = candidates[:max_claims]
            all_warnings.append(ClaimWarning.CLM_EXCEEDED_MAX_CLAIMS)

        claims: list[Claim] = []

        for candidate in candidates:
            # Stage 4: Structured Extraction
            structured = structure_extractor.extract(candidate, parser)

            # Stage 5: Assertion Annotation
            annotated = annotator.annotate(structured)

            # Stage 6: Failure Degradation
            validated = degradation_handler.apply(annotated)
            all_warnings.extend(validated.all_warnings)

            # Stage 7: Build Claim
            claim = build_claim(validated)

            # Record statistics
            stats_collector.record_claim(
                mode=claim.extraction_mode,
                is_negated=claim.is_negated,
                is_modal=claim.assertion_metadata.modality.value != "certain",
                is_attributed=claim.assertion_metadata.is_attributed,
            )

            claims.append(claim)

        # Validate the complete claim collection
        validated_claims, val_warnings = validate_claims(
            claims, sentence.document_id, global_seen_ids
        )
        all_warnings.extend(val_warnings)
        stats_collector.record_warnings(all_warnings)

        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=validated_claims,
            warnings=all_warnings,
        )

    except ClaimValidationError as e:
        logger.error(
            "fatal claim validation error",
            sentence_id=sentence_id[:8],
            error=str(e),
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in claim extraction",
            sentence_id=sentence_id[:8],
            error=str(e),
            exc_info=True,
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )


def extract_claims(
    semantic_sentences: list[SemanticSentence],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> Phase4Result:
    """
    Extract claims from all SemanticSentences.

    This is the sole public function of Phase 4.
    All internal pipeline components are created here and hidden from callers.

    Args:
        semantic_sentences: All SemanticSentences from Phase 3.
        run_id:             Current pipeline run identifier.
        manifest_manager:   For writing phase manifest.
        state_manager:      For updating pipeline state.

    Returns:
        Phase4Result containing all Claims and statistics.
    """
    config = get_config()
    ce_cfg = config.get("claim_extraction", {})
    max_claims = ce_cfg.get("max_claims_per_sentence", 10)

    logger.info(
        "phase 4 starting",
        run_id=run_id,
        sentences=len(semantic_sentences),
    )
    start_time = manifest_manager.start_phase(phase=4)

    # Initialize all pipeline components once
    parser = SpaCyParser()  # <-- REPLACED (instantiate concrete class)
    classifier = AssertionClassifier()
    boundary_detector = BoundaryDetector()
    structure_extractor = StructureExtractor()
    annotator = AssertionAnnotator()
    degradation_handler = DegradationHandler()
    stats_collector = Phase4StatsCollector()

    sentence_results: list[SentenceExtractionResult] = []
    global_seen_ids: dict = {}

    with Timer("phase4_claim_construction"):
        for sentence in semantic_sentences:
            result = extract_claims_from_sentence(
                sentence=sentence,
                parser=parser,
                boundary_detector=boundary_detector,
                structure_extractor=structure_extractor,
                annotator=annotator,
                degradation_handler=degradation_handler,
                stats_collector=stats_collector,
                max_claims=max_claims,
                global_seen_ids=global_seen_ids,
                classifier=classifier,
            )
            sentence_results.append(result)

    stats = stats_collector.finalize()

    phase4_result = Phase4Result(
        sentence_results=sentence_results,
        stats=stats,
        run_id=run_id,
    )

    # Write dataset artifact for Phase 5
    phase_dir = (
        manifest_manager.run_dir / "phase4"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(phase4_result.to_dataset_json(), encoding="utf-8")

    # Write the lossless audit side-channel: every sentence that was
    # classified as non-DECLARATIVE_ASSERTION and therefore never became a
    # Claim, in full, with its classified type and reason.
    discarded_path = phase_dir / "discarded_candidates.json"
    discarded_path.write_text(phase4_result.to_discarded_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        claims=phase4_result.total_claims,
        discarded_candidates=len(phase4_result.all_discarded_candidates),
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=4,
        start_time=start_time,
        inputs={"sentences": len(semantic_sentences)},
        outputs={
            "total_claims": phase4_result.total_claims,
            "structured": stats.structured_claims,
            "partial": stats.partial_claims,
            "lexical": stats.lexical_claims,
            "whole_sentence": stats.whole_sentence_claims,
            "parser_failures": stats.parser_failures,
            "dataset_path": str(dataset_path),
            "discarded_non_assertions": stats.total_discarded_non_assertions,
            "discarded_by_type": stats.discarded_by_type,
            "discarded_path": str(discarded_path),
        },
        status="success",
    )
    phase4_result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=4)

    logger.info(
        "phase 4 complete",
        total_claims=phase4_result.total_claims,
        structured=stats.structured_claims,
        fallbacks=stats.whole_sentence_claims,
        parser_failures=stats.parser_failures,
        discarded_non_assertions=stats.total_discarded_non_assertions,
    )

    return phase4_result
