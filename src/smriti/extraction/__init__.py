"""
extraction/__init__.py — Public API for Phase 3.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.extraction import build_semantic_sentences, ExtractionResult

They never import from individual submodules.
All internal modules (scanner, context, normalizer, segmenter, builder, validator)
are implementation details.

Public contract:
    build_semantic_sentences(document: Document) → ExtractionResult

That is the only function that crosses the phase boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import structlog

from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Document,
    Phase3Stats,
    SegmentationWarning,
    SemanticSentence,
)
from smriti.core.state import StateManager
from smriti.exceptions import SentenceValidationError
from smriti.extraction.builder import build_sentence
from smriti.extraction.context import ContextStack
from smriti.extraction.normalizer import normalize_event
from smriti.extraction.scanner import BlockType, scan_document
from smriti.extraction.segmenter import SentenceSegmenter
from smriti.extraction.statistics import Phase3StatsCollector
from smriti.extraction.validator import validate_sentences

logger = structlog.get_logger(__name__)


# ── Public result types ───────────────────────────────────────────────────────


@dataclass
class DocumentExtractionResult:
    """
    Phase 3 result for a single Document.
    """

    document_id: str
    sentences: list[SemanticSentence]
    stats: Phase3Stats
    warnings: list[SegmentationWarning]
    error: str | None = None

    @property
    def sentence_count(self) -> int:
        return len(self.sentences)


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 3 — all documents processed.
    This is what Phase 4 receives.
    """

    document_results: list[DocumentExtractionResult]
    run_id: str
    rules_version: str = "3.1.0"  # <-- ADDED FINGERPRINT
    manifest_path: Path | None = None

    @property
    def all_sentences(self) -> list[SemanticSentence]:
        """Flat list of all sentences across all documents."""
        result = []
        for dr in self.document_results:
            result.extend(dr.sentences)
        return result

    @property
    def total_sentences(self) -> int:
        return sum(dr.sentence_count for dr in self.document_results)

    @property
    def successful_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is None)

    @property
    def failed_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is not None)

    def to_dataset_json(self) -> str:
        """
        Serialise all SemanticSentences to JSON for Phase 4.
        Written to artifacts/run_{id}/phase3/dataset.json.
        """
        records = []
        for sentence in self.all_sentences:
            records.append(
                {
                    "sentence_id": sentence.sentence_id,
                    "document_id": sentence.document_id,
                    "text": sentence.text,
                    "context": sentence.context,
                    "position": sentence.position,
                    "char_start": sentence.char_start,
                    "char_end": sentence.char_end,
                    "source_path": str(sentence.source_path),
                    "origin_block_type": sentence.origin_block_type,  # <-- FIX: Remove .value
                    "schema_version": sentence.schema_version,
                }
            )
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ──────────────────────────────────────────────────────


def build_semantic_sentences(document: Document) -> DocumentExtractionResult:
    """
    Transform one Document into an ordered collection of SemanticSentences.

    This is Phase 3's single public function.
    Internal modules (scanner, context, normalizer, segmenter, builder, validator)
    are never exposed.

    Args:
        document: A Document from Phase 2 with validated normalized_text.

    Returns:
        DocumentExtractionResult with sentences, stats, and warnings.
        On error, returns a result with error set and empty sentences.
    """
    document_id = document.doc_id

    try:
        sentences, stats, warnings = _process_document(document)
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=sentences,
            stats=stats,
            warnings=warnings,
        )

    except SentenceValidationError as e:
        logger.error(
            "fatal sentence validation error",
            document_id=document_id,
            error=str(e),
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in phase 3",
            document_id=document_id,
            error=str(e),
            exc_info=True,
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )


def _process_document(
    document: Document,
) -> tuple[list[SemanticSentence], Phase3Stats, list[SegmentationWarning]]:
    """
    Internal orchestration of Phase 3 for one Document.

    Pipeline:
        1. scan_document      → ScannerEvent[]
        2. Normalise each event → NormalizedBlock[]
        3. Associate context (from heading events) to each block
        4. segmenter.segment   → SentenceCandidate[]
        5. build_sentence      → SemanticSentence (one per candidate)
        6. validate_sentences  → validated list

    Complexity: O(n) where n = length of normalized_text
    """
    normalized_text = document.normalized_text
    document_id = document.doc_id
    source_path = document.source_document.path

    # Step 1: Structural scan
    events = scan_document(normalized_text)

    # Step 2: Initialise components
    context_stack = ContextStack()
    segmenter = SentenceSegmenter()
    stats_collector = Phase3StatsCollector()

    sentences: list[SemanticSentence] = []
    all_warnings: list[SegmentationWarning] = []
    position = 0  # Global position counter across all sentences in document

    # Step 3: Process each structural event
    for event in events:
        stats_collector.accumulate_event(event)

        # 3a: Update context if this is a heading event
        # MUST happen before normalization because headings set skip=True
        if event.block_type == BlockType.HEADING and event.heading_level is not None:
            context_stack.push(event.text, event.heading_level)

        # 3b: Normalise event to prose (context-agnostic)
        normalized_block = normalize_event(event)
        if normalized_block.warnings:
            all_warnings.extend(normalized_block.warnings)
            stats_collector.record_warnings(normalized_block.warnings)

        # Skip blocks that produce no sentences (headings, code, etc.)
        if normalized_block.skip or not normalized_block.prose.strip():
            if event.block_type == BlockType.CODE_BLOCK:
                stats_collector.record_sentence_discarded()
            continue

        # 3c: Attach current context to this block
        current_context = context_stack.current_context()

        # 3d: Segment prose into sentence candidates
        candidates = segmenter.segment(
            normalized_block.prose,
            block_char_start=normalized_block.char_start,
        )

        if not candidates:
            stats_collector.record_sentence_discarded()
            continue

        # 3e: Build SemanticSentence for each candidate
        for candidate in candidates:
            if candidate.warnings:
                all_warnings.extend(candidate.warnings)
                stats_collector.record_warnings(candidate.warnings)

            sentence = build_sentence(
                text=candidate.text,
                document_id=document_id,
                source_path=source_path,
                context=current_context,
                position=position,
                char_start=candidate.char_start,
                char_end=candidate.char_end,
                origin_block_type=event.block_type,
            )
            sentences.append(sentence)
            stats_collector.record_sentence_produced()
            position += 1

    # Step 4: Validate the complete sentence collection
    validated_sentences, val_warnings = validate_sentences(sentences, document_id)
    all_warnings.extend(val_warnings)

    discarded = len(sentences) - len(validated_sentences)
    for _ in range(discarded):
        stats_collector.record_sentence_discarded()

    stats = stats_collector.finalize()

    logger.info(
        "document processed",
        document_id=document_id[:8],
        sentences=len(validated_sentences),
        warnings=len(all_warnings),
    )

    return validated_sentences, stats, all_warnings


# ── Batch runner (called by PipelineRunner) ───────────────────────────────────


def run_extraction(
    documents: list[Document],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Run Phase 3 on all Documents from Phase 2.

    Args:
        documents:        List[Document] from Phase 2's ExtractionResult.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.

    Returns:
        ExtractionResult containing all SemanticSentences.
    """
    logger.info("phase 3 starting", run_id=run_id, documents=len(documents))
    start_time = manifest_manager.start_phase(phase=3)

    document_results: list[DocumentExtractionResult] = []

    for document in documents:
        if document.is_empty:
            logger.debug("skipping empty document", document_id=document.doc_id[:8])
            continue

        doc_result = build_semantic_sentences(document)
        document_results.append(doc_result)

    result = ExtractionResult(
        document_results=document_results,
        run_id=run_id,
    )

    # Write dataset artifact
    phase_dir = (
        manifest_manager.run_dir / "phase3"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        sentences=result.total_sentences,
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=3,
        start_time=start_time,
        inputs={"documents": len(documents)},
        outputs={
            "total_sentences": result.total_sentences,
            "successful_documents": result.successful_documents,
            "failed_documents": result.failed_documents,
            "dataset_path": str(dataset_path),
            "rules_version": result.rules_version,
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=3)

    logger.info(
        "phase 3 complete",
        sentences=result.total_sentences,
        docs_ok=result.successful_documents,
        docs_failed=result.failed_documents,
    )

    return result
