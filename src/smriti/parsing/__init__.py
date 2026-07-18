"""
parsing/__init__.py — Public API for Phase 2.

External callers (PipelineRunner, main.py) import from here:

    from smriti.parsing import run_extraction, ExtractionResult

They never import from individual submodules (loader, markdown, pdf, etc.).
Those remain internal implementation details.

Orchestration:
    1. Accept List[SourceDocument] from Phase 1
    2. For each document: dispatch loader.load_document()
    3. Collect successful Document objects
    4. Record failures (one failure never stops the batch)
    5. Write dataset.json artifact
    6. Write manifest
    7. Update pipeline state
    8. Return ExtractionResult

Phase 2 Golden Rule: Extract text. Never interpret text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import Document, ExtractionMethod, SourceDocument
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import ParsingError

from smriti.parsing.loader import load_document

logger = structlog.get_logger(__name__)


@dataclass
class ExtractionStats:
    """Statistics from one Phase 2 run."""
    total_documents: int = 0
    successful: int = 0
    failed: int = 0
    total_characters: int = 0
    total_words: int = 0
    documents_with_warnings: int = 0

    def summary(self) -> str:
        return (
            f"total={self.total_documents} "
            f"success={self.successful} "
            f"failed={self.failed} "
            f"chars={self.total_characters} "
            f"words={self.total_words} "
            f"with_warnings={self.documents_with_warnings}"
        )


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 2.
    This is what Phase 3 receives.

    Attributes:
        documents:     All successfully extracted Document objects.
        failed:        (SourceDocument, error_message) pairs for failures.
        stats:         Summary statistics.
        run_id:        Pipeline run identifier.
        manifest_path: Path to the written manifest.json.
        dataset_path:  Path to the written dataset.json.
    """
    documents: List[Document]
    failed: List[Tuple[SourceDocument, str]]
    stats: ExtractionStats
    run_id: str
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None

    def to_dataset_json(self) -> str:
        """
        Serialize extracted documents to JSON.
        Written to artifacts/run_{id}/phase2/dataset.json for Phase 3.

        Includes only normalized_text and structural metadata.
        Never includes raw_text (too large, not needed by Phase 3).
        """
        records = []
        for doc in self.documents:
            records.append({
                "doc_id": doc.doc_id,
                "schema_version": doc.schema_version,
                "path": str(doc.source_document.path),
                "relative_path": str(doc.source_document.relative_path),
                "format": doc.source_document.format.value,
                "extraction_method": doc.extraction_method.value,
                "encoding_used": doc.encoding_used,
                "normalized_text": doc.normalized_text,
                "extraction_warnings": [w.value for w in doc.extraction_warnings],
                "text_statistics": {
                    "character_count": doc.text_statistics.character_count,
                    "word_count": doc.text_statistics.word_count,
                    "line_count": doc.text_statistics.line_count,
                    "blank_line_count": doc.text_statistics.blank_line_count,
                    "paragraph_count": doc.text_statistics.paragraph_count,
                },
                "modified_at": doc.source_document.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_extraction(
    source_documents: List[SourceDocument],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Execute the complete Phase 2 extraction pipeline.

    Args:
        source_documents:  List of SourceDocument from Phase 1 (canonical only).
        run_id:            Unique pipeline run identifier.
        manifest_manager:  For writing phase manifest.
        state_manager:     For updating pipeline state.

    Returns:
        ExtractionResult containing Document list and statistics.

    Raises:
        ParsingError: Only for pipeline-fatal errors (config missing, artifact dir
                      unavailable). Individual document failures do NOT raise.
    """
    config = get_config()
    stats = ExtractionStats(total_documents=len(source_documents))

    with Timer("phase2_extraction"):

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=2)
        logger.info(
            "phase 2 starting",
            run_id=run_id,
            total_documents=stats.total_documents,
        )

        # ── Step 2: Process each document ─────────────────────────────────────
        documents: List[Document] = []
        failed: List[Tuple[SourceDocument, str]] = []

        for source in source_documents:
            doc, error = load_document(source)

            if doc is not None:
                documents.append(doc)
                stats.successful += 1
                stats.total_characters += doc.text_statistics.character_count
                stats.total_words += doc.text_statistics.word_count
                if doc.has_warnings:
                    stats.documents_with_warnings += 1
            else:
                failed.append((source, error or "unknown error"))
                stats.failed += 1

        logger.info("phase 2 extraction complete", **{
            k: v for k, v in [
                ("successful", stats.successful),
                ("failed", stats.failed),
                ("total_chars", stats.total_characters),
                ("total_words", stats.total_words),
            ]
        })

        # ── Step 3: Write dataset artifact ────────────────────────────────────
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase2"
        phase_dir.mkdir(parents=True, exist_ok=True)

        output_filename = config.get("parsing", {}).get(
            "output_dataset_filename", "dataset.json"
        )
        dataset_path = phase_dir / output_filename

        result = ExtractionResult(
            documents=documents,
            failed=failed,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
        result.dataset_path = dataset_path

        logger.info(
            "phase 2 dataset written",
            path=str(dataset_path),
            documents=len(documents),
        )

        # ── Step 4: Write manifest ─────────────────────────────────────────────
        failed_paths = [str(src.path) for src, _ in failed]

        manifest_path = manifest_manager.end_phase(
            phase=2,
            start_time=start_time,
            inputs={
                "source_documents": stats.total_documents,
                "run_id": run_id,
            },
            outputs={
                "successful_documents": stats.successful,
                "failed_documents": stats.failed,
                "total_characters": stats.total_characters,
                "total_words": stats.total_words,
                "documents_with_warnings": stats.documents_with_warnings,
                "dataset_path": str(dataset_path),
                "failed_paths": failed_paths,
            },
            status="success" if stats.failed == 0 else "partial",
        )
        result.manifest_path = manifest_path

        # ── Step 5: Update pipeline state ─────────────────────────────────────
        state_manager.complete_phase(phase=2)

    logger.info("phase 2 complete", **{k: v for k, v in vars(stats).items()})

    return result