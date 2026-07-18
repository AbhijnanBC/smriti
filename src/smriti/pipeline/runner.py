"""
pipeline/runner.py — PipelineRunner with Phases 1, 2, 3, and 4 registered.

Phases 5–13 will be added as they are built.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.exceptions import PipelineError, Phase5Error

logger = structlog.get_logger(__name__)


def _make_run_id() -> str:
    """Produce a timestamp-based run_id. Unique per execution."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class PipelineRunner:
    """
    Orchestrates pipeline phases.

    Usage:
        runner = PipelineRunner(input_dirs=[Path("data/raw")])
        runner.run()
    """

    def __init__(self, input_dirs: List[Path]):
        self.input_dirs = [Path(d) for d in input_dirs]
        self.run_id = _make_run_id()
        self.manifest_manager = ManifestManager(
            run_id=self.run_id,
            artifacts_dir=ARTIFACTS_DIR,
        )
        self.state_manager = StateManager()
        logger.info("pipeline runner initialized", run_id=self.run_id)

    def run(
        self,
        start_from: int = 1,
        stop_at: Optional[int] = None,
        force_full: bool = False,
    ) -> bool:
        """
        Run pipeline phases start_from through stop_at.

        Args:
            start_from:  First phase to run (default 1).
            stop_at:     Last phase to run (default: run all registered).
            force_full:  Ignore caches and re-process everything.

        Returns:
            True if all phases succeeded.
        """
        logger.info(
            "pipeline run starting",
            run_id=self.run_id,
            start_from=start_from,
            stop_at=stop_at,
        )

        # Check for resumable state
        state = self.state_manager.load()
        if state and not force_full:
            completed = state.completed_phases
            if completed:
                resume_from = max(completed) + 1
                if resume_from > start_from:
                    logger.info(
                        "resuming from checkpoint",
                        completed_phases=completed,
                        resuming_at=resume_from,
                    )
                    start_from = resume_from

        try:
            # ── Phase 1: Input Discovery ───────────────────────────────────────
            phase1_result = None
            if start_from <= 1 and (stop_at is None or stop_at >= 1):
                phase1_result = self._run_phase_1(force_full=force_full)

            # ── Phase 2: Text Extraction ───────────────────────────────────────
            phase2_result = None
            if start_from <= 2 and (stop_at is None or stop_at >= 2):
                if phase1_result is None:
                    # Resuming from Phase 2 — load Phase 1 dataset from artifact
                    phase1_result = self._load_phase1_result()

                phase2_result = self._run_phase_2(phase1_result)

            # ── Phase 3: Semantic Sentence Construction ──────────────────────
            phase3_result = None
            if start_from <= 3 and (stop_at is None or stop_at >= 3):
                if phase2_result is None:
                    phase2_result = self._load_phase2_result()
                phase3_result = self._run_phase_3(phase2_result)

            # ── Phase 4: Claim Construction ────────────────────────────────────
            phase4_result = None
            if start_from <= 4 and (stop_at is None or stop_at >= 4):
                if phase3_result is None:
                    phase3_result = self._load_phase3_result()
                phase4_result = self._run_phase_4(phase3_result)


            phase5_result = None
            if start_from <= 5 and (stop_at is None or stop_at >= 5):
                if phase4_result is None:
                    phase4_result = self._load_phase4_result()
                phase5_result = self._run_phase_5(phase4_result)

            # Phases 5–13 will be registered here as they are built.

        except Exception as e:
            logger.error("pipeline failed", error=str(e), exc_info=True)
            return False

        logger.info("pipeline run complete", run_id=self.run_id)
        return True

    # ── Phase 1 implementation ────────────────────────────────────────────────

    def _run_phase_1(self, force_full: bool = False):
        """Execute Phase 1: Input Discovery."""
        from smriti.discovery import run_discovery, DiscoveryResult

        logger.info("running phase 1")
        result = run_discovery(
            input_dirs=self.input_dirs,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            force_full=force_full,
        )
        logger.info(
            "phase 1 complete",
            canonical_docs=result.canonical_count,
            duplicates=len(result.duplicate_documents),
            skipped=len(result.skipped),
        )
        return result

    def _load_phase1_result(self):
        """
        Load Phase 1 dataset from artifact when resuming at Phase 2.
        Reconstructs SourceDocument list from dataset.json.
        """
        import json
        from datetime import datetime, timezone
        from smriti.core.models import FileFormat, SourceDocument
        from smriti.discovery import DiscoveryResult, DiscoveryStats, DuplicateRegistry

        # Find the most recent run's phase1 dataset
        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase1" / "dataset.json"
        if not dataset_path.exists():
            # Try to find any existing phase1 artifact
            phase1_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase1/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase1_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 2: no Phase 1 dataset.json found. "
                    "Run from Phase 1 first."
                )
            dataset_path = phase1_dirs[0]
            logger.info("loading phase1 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        source_documents = []
        for r in records:
            source_documents.append(
                SourceDocument(
                    doc_id=r["doc_id"],
                    path=Path(r["path"]),
                    relative_path=Path(r["relative_path"]),
                    source_root=Path(r["source_root"]),
                    format=FileFormat(r["format"]),
                    content_hash=r["content_hash"],
                    size_bytes=r["size_bytes"],
                    modified_at=datetime.fromisoformat(r["modified_at"]),
                )
            )

        # Reconstruct a minimal DiscoveryResult for Phase 2
        return type("DiscoveryResult", (), {
            "canonical_documents": source_documents,
        })()

    # ── Phase 2 implementation ────────────────────────────────────────────────

    def _run_phase_2(self, phase1_result):
        """
        Execute Phase 2: Text Extraction.
        Returns the extraction result so it can be used by later phases.
        """
        from smriti.parsing import run_extraction

        logger.info("running phase 2")
        result = run_extraction(
            source_documents=phase1_result.canonical_documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 2 complete",
            successful=result.stats.successful,
            failed=result.stats.failed,
            total_chars=result.stats.total_characters,
        )
        return result   # <-- return the result so Phase 3 can consume it

    # ── Phase 3 implementation ────────────────────────────────────────────────

    def _load_phase2_result(self):
        """Load Phase 2 dataset from artifact when resuming at Phase 3."""
        import json
        from smriti.core.models import (
            Document, SourceDocument, FileFormat, ExtractionMethod,
            TextStatistics, WarningCode, RawExtractionResult,
        )
        from datetime import datetime, timezone

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase2" / "dataset.json"
        if not dataset_path.exists():
            phase2_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase2/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase2_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 3: no Phase 2 dataset.json found. "
                    "Run from Phase 2 first."
                )
            dataset_path = phase2_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        documents = []
        for r in records:
            source_doc = SourceDocument(
                doc_id=r["doc_id"],
                path=Path(r["path"]),
                relative_path=Path(r["relative_path"]),
                source_root=Path(r["source_root"]),
                format=FileFormat(r["format"]),
                content_hash=r["content_hash"],
                size_bytes=r["size_bytes"],
                modified_at=datetime.fromisoformat(r["modified_at"]),
            )
            stats = TextStatistics(
                character_count=r["stats"]["character_count"],
                word_count=r["stats"]["word_count"],
                line_count=r["stats"]["line_count"],
                blank_line_count=r["stats"]["blank_line_count"],
                paragraph_count=r["stats"]["paragraph_count"],
            )
            documents.append(Document(
                doc_id=r["doc_id"],
                source_document=source_doc,
                raw_text=r["raw_text"],
                normalized_text=r["normalized_text"],
                extraction_method=ExtractionMethod(r["extraction_method"]),
                extraction_warnings=tuple(WarningCode(w) for w in r.get("warnings", [])),
                text_statistics=stats,
                encoding_used=r.get("encoding_used", "utf-8"),
            ))
        return type("Phase2Result", (), {"documents": documents})()

    def _run_phase_3(self, phase2_result):
        """Execute Phase 3: Semantic Sentence Construction."""
        from smriti.extraction import run_extraction

        logger.info("running phase 3")
        result = run_extraction(
            documents=phase2_result.documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 3 complete",
            total_sentences=result.total_sentences,
            docs_ok=result.successful_documents,
            docs_failed=result.failed_documents,
        )
        return result   # return for future phases if needed

    # ── Phase 4 implementation ────────────────────────────────────────────────

    def _load_phase3_result(self):
        """Load Phase 3 dataset from artifact when resuming at Phase 4."""
        import json
        from smriti.core.models import SemanticSentence
        from pathlib import Path

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase3" / "dataset.json"
        if not dataset_path.exists():
            phase3_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase3/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase3_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 4: no Phase 3 dataset.json found. "
                    "Run from Phase 3 first."
                )
            dataset_path = phase3_dirs[0]
            logger.info("loading phase3 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        sentences = []
        for r in records:
            sentences.append(SemanticSentence(
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r["context"],
                position=r["position"],
                char_start=r["char_start"],
                char_end=r["char_end"],
                source_path=Path(r["source_path"]),
                origin_block_type=r.get("origin_block_type", "paragraph"),
                schema_version=r.get("schema_version", "3.0"),
            ))

        return type("Phase3Result", (), {"all_sentences": sentences})()

    def _run_phase_4(self, phase3_result):
        """Execute Phase 4: Claim Construction."""
        from smriti.claims import extract_claims
        from smriti.claims import Phase4Result

        logger.info("running phase 4")
        result = extract_claims(
            semantic_sentences=phase3_result.all_sentences,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 4 complete",
            total_claims=result.total_claims,
            structured=result.stats.structured_claims,
            parser_failures=result.stats.parser_failures,
        )
        return result
    
        # ── Phase 5 implementation ────────────────────────────────────────────────

    def _load_phase4_result(self):
        """
        Load Phase 4 dataset from artifact when resuming at Phase 5.

        Validates schema_version before deserializing to avoid silently
        processing data from an incompatible Phase 4 implementation.
        """
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        SUPPORTED_PHASE4_SCHEMA = "4.0"

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 5: no Phase 4 dataset.json found. "
                    "Run from Phase 4 first."
                )
            dataset_path = phase4_dirs[0]
            logger.info("loading phase4 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))

        # Validate schema_version before deserializing.
        schema_versions = {r.get("schema_version", "unknown") for r in records if records}
        unsupported = schema_versions - {SUPPORTED_PHASE4_SCHEMA}
        if unsupported:
            logger.warning(
                "unexpected schema_version in phase4 dataset",
                found=sorted(unsupported),
                expected=SUPPORTED_PHASE4_SCHEMA,
            )

        claims = []
        for r in records:
            prov_data = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov_data.get("sentence_id", ""),
                document_id=prov_data.get("document_id", ""),
                source_path=Path(prov_data.get("source_path", "unknown")),
                sentence_context=prov_data.get("sentence_context", ""),
                sentence_position=prov_data.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claims.append(Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                content_hash=r.get("content_hash", ""),
                rule_version=r.get("rule_version", "1.0"),
            ))

        return type("Phase4Result", (), {"all_claims": claims})()

    def _run_phase_5(self, phase4_result):
        """Execute Phase 5: Semantic Embedding."""
        from smriti.embedding import embed_claims
        from smriti.exceptions import Phase5Error

        logger.info("running phase 5")
        try:
            result = embed_claims(
                claims=phase4_result.all_claims,
                run_id=self.run_id,
                manifest_manager=self.manifest_manager,
                state_manager=self.state_manager,
            )
        except Phase5Error as e:
            logger.error("phase 5 failed with Phase5Error", error=str(e))
            raise  # Let the runner handle it cleanly

        if result.warnings:
            logger.warning(
                "phase 5 completed with warnings",
                warning_count=len(result.warnings),
                first_warning=result.warnings[0],
            )
        if result.errors:
            logger.error(
                "phase 5 completed with errors",
                error_count=len(result.errors),
            )

        logger.info(
            "phase 5 complete",
            total_embedded=result.total_embedded,
            cached=result.stats.cached,
            failed=result.stats.failed,
            cache_hit_rate=f"{result.stats.cache_hit_rate:.1%}",
            throughput=f"{result.stats.vectors_per_second:.1f} vec/s",
        )
        return result    
    


