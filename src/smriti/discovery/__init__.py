"""
discovery/__init__.py — Public API for Phase 1.

External callers (PipelineRunner) import from here:

    from smriti.discovery import run_discovery, DiscoveryResult

They never import from individual submodules.

Orchestration:
  1. Validate input directories           [validator.validate_directories]
  2. Discover candidate files             [scanner.discover_files]
  3. Validate each candidate file         [validator.validate_file]
  4. Extract metadata for valid files     [metadata.extract_metadata]
  5. Compute content hash                 [hashing.compute_hash + hash cache]
  6. Build duplicate registry             [duplicate.build_duplicate_registry]
  7. Build source documents               [builder.build_source_document]
  8. Write manifest                       [manifest.ManifestManager]
  9. Update pipeline state                [state.StateManager]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.hashing import ContentHasher
from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR, CACHE_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import DiscoveryError

from smriti.discovery.scanner import discover_files
from smriti.discovery.validator import validate_directories, validate_file
from smriti.discovery.metadata import extract_metadata, FileMetadata
from smriti.discovery.hashing import compute_hash
from smriti.discovery.duplicate import build_duplicate_registry, DuplicateRegistry
from smriti.discovery.builder import SourceDocument, build_source_document

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveryContext:
    """
    Immutable shared execution context for Phase 1.
    Carries configuration, run metadata, and managers.
    """
    run_id: str
    manifest_manager: ManifestManager
    state_manager: StateManager
    force_full: bool
    config: dict
    discovered_at: datetime


@dataclass
class DiscoveryStats:
    """Statistics from one discovery run."""

    total_candidates: int = 0
    valid_count: int = 0
    skipped_count: int = 0
    duplicate_count: int = 0
    # Incremental stats (based on hash cache)
    unchanged_count: int = 0
    new_count: int = 0
    modified_count: int = 0

    def summary(self) -> str:
        return (
            f"discovered={self.valid_count} "
            f"skipped={self.skipped_count} "
            f"duplicates={self.duplicate_count} "
            f"new={self.new_count} "
            f"unchanged={self.unchanged_count} "
            f"modified={self.modified_count}"
        )


@dataclass
class DiscoveryResult:
    """
    Complete output of Phase 1.
    This is what Phase 2 receives.

    Attributes:
        documents:          All valid SourceDocument objects (including duplicates).
        duplicate_registry: Mapping from content hash to duplicate info.
        skipped:            All paths that failed validation (with reasons).
        stats:              Summary statistics.
        run_id:             Pipeline run identifier.
        manifest_path:      Path to written manifest.json.
    """

    documents: List[SourceDocument]
    duplicate_registry: DuplicateRegistry
    skipped: List[Tuple[Path, str]]
    stats: DiscoveryStats
    run_id: str
    manifest_path: Optional[Path] = None

    @property
    def canonical_documents(self) -> List[SourceDocument]:
        """Return only canonical (non‑duplicate) documents."""
        return [d for d in self.documents if not self.duplicate_registry.is_duplicate(d.path)]

    @property
    def duplicate_documents(self) -> List[SourceDocument]:
        """Return only duplicate documents."""
        return [d for d in self.documents if self.duplicate_registry.is_duplicate(d.path)]

    @property
    def canonical_count(self) -> int:
        return len(self.canonical_documents)

    def to_dataset_json(self) -> str:
        """
        Serialize the canonical document dataset to JSON.
        Written to artifacts/run_{id}/phase1/dataset.json for Phase 2.
        """
        records = []
        for doc in self.canonical_documents:
            records.append({
                "doc_id": doc.doc_id,
                "path": str(doc.path),
                "relative_path": str(doc.relative_path),
                "source_root": str(doc.source_root),
                "format": doc.format.value,
                "content_hash": doc.content_hash,
                "size_bytes": doc.size_bytes,
                "modified_at": doc.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_discovery(
    input_dirs: List[Path],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    force_full: bool = False,
) -> DiscoveryResult:
    """
    Execute the complete Phase 1 discovery pipeline.

    Args:
        input_dirs:       Root directories to scan.
        run_id:           Unique pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        force_full:       If True, ignore hash cache and re-process all files.

    Returns:
        DiscoveryResult containing canonical documents and statistics.

    Raises:
        DiscoveryError: If input directories are invalid (fatal).
    """
    config = get_config()
    discovered_at = datetime.now(tz=timezone.utc)
    context = DiscoveryContext(
        run_id=run_id,
        manifest_manager=manifest_manager,
        state_manager=state_manager,
        force_full=force_full,
        config=config,
        discovered_at=discovered_at,
    )
    stats = DiscoveryStats()

    with Timer("phase1_discovery") as timer:

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=1)
        logger.info("phase 1 starting", run_id=run_id)

        # ── Step 2: Validate input directories ────────────────────────────────
        logger.info("validating input directories", count=len(input_dirs))
        validated_roots = validate_directories(input_dirs)

        # ── Step 3: Discover candidate files ──────────────────────────────────
        logger.info("scanning directories")
        candidate_paths = discover_files(validated_roots)
        stats.total_candidates = len(candidate_paths)
        logger.info("candidates found", count=stats.total_candidates)

        # ── Step 4: Validate individual files ─────────────────────────────────
        logger.info("validating files")
        valid_paths: List[Path] = []
        skipped: List[Tuple[Path, str]] = []

        for path in candidate_paths:
            result = validate_file(path)
            if result.is_valid:
                valid_paths.append(path)
            else:
                skipped.append((path, result.rejection_reason))
                logger.debug(
                    "file skipped",
                    path=str(path),
                    reason=result.rejection_reason,
                )

        stats.valid_count = len(valid_paths)
        stats.skipped_count = len(skipped)
        logger.info(
            "file validation complete",
            valid=stats.valid_count,
            skipped=stats.skipped_count,
        )

        # ── Step 5: Extract metadata ───────────────────────────────────────────
        logger.info("extracting metadata")
        metadata_map: Dict[Path, FileMetadata] = {}
        for path in valid_paths:
            try:
                metadata_map[path] = extract_metadata(path)
            except OSError as e:
                logger.warning("metadata extraction failed", path=str(path), error=str(e))
                skipped.append((path, f"metadata error: {e}"))
                stats.skipped_count += 1
                stats.valid_count -= 1

        valid_paths = [p for p in valid_paths if p in metadata_map]

        # ── Step 6: Compute content hashes (with incremental cache) ───────────
        logger.info("computing content hashes")
        hash_cache = ContentHasher(cache_file=CACHE_DIR / "hashes.json")
        path_hash_pairs: List[Tuple[Path, str]] = []
        
        new_active_hashes: Dict[str, str] = {}  # <-- ADDED: Initialize fresh dictionary

        for path in valid_paths:
            try:
                content_hash = compute_hash(path)  # reads once
            except OSError as e:
                logger.warning("hash computation failed", path=str(path), error=str(e))
                skipped.append((path, f"hash error: {e}"))
                stats.skipped_count += 1
                continue

            # Incremental classification (for stats only)
            if not force_full:
                cached = hash_cache.hashes.get(str(path))
                if cached is None:
                    stats.new_count += 1
                elif cached == content_hash:
                    stats.unchanged_count += 1
                else:
                    stats.modified_count += 1
            else:
                stats.new_count += 1

            # <-- CHANGED: Populate the fresh dictionary instead of updating old cache
            new_active_hashes[str(path)] = content_hash  
            path_hash_pairs.append((path, content_hash))

        # <-- ADDED: Overwrite the cache completely to prune deleted files
        hash_cache.hashes = new_active_hashes
        hash_cache._save()

        # ── Step 7: Detect duplicates ──────────────────────────────────────────
        logger.info("detecting duplicate content")
        duplicate_registry = build_duplicate_registry(path_hash_pairs)
        stats.duplicate_count = duplicate_registry.duplicate_count

        # ── Step 8: Build source documents ────────────────────────────────────
        logger.info("building source documents")
        hash_dict = dict(path_hash_pairs)
        all_documents: List[SourceDocument] = []

        for path in valid_paths:
            if path not in hash_dict:
                continue  # was skipped during hashing

            # Determine which root this file belongs to
            source_root = _find_source_root(path, validated_roots)

            doc = build_source_document(
                metadata=metadata_map[path],
                content_hash=hash_dict[path],
                source_root=source_root,
            )
            all_documents.append(doc)

        # ── Step 9: Write dataset artifact ────────────────────────────────────
        phase_dir = manifest_manager.run_dir / "phase1"  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
        phase_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = phase_dir / "dataset.json"

        result = DiscoveryResult(
            documents=all_documents,
            duplicate_registry=duplicate_registry,
            skipped=skipped,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(
            result.to_dataset_json(), encoding="utf-8"
        )
        logger.info("dataset written", path=str(dataset_path), count=result.canonical_count)

        # ── Step 10: Write manifest ────────────────────────────────────────────
        manifest_path = manifest_manager.end_phase(
            phase=1,
            start_time=start_time,
            inputs={
                "directories": [str(d) for d in input_dirs],
                "force_full": force_full,
            },
            outputs={
                "canonical_documents": result.canonical_count,
                "duplicate_documents": len(result.duplicate_documents),
                "skipped_files": len(skipped),
                "dataset_path": str(dataset_path),
            },
            status="success",
        )
        result.manifest_path = manifest_path

        # ── Step 11: Update pipeline state ────────────────────────────────────
        state_manager.complete_phase(phase=1)

    logger.info("phase 1 complete", **{k: v for k, v in vars(stats).items()})

    return result


def _find_source_root(path: Path, roots: List[Path]) -> Path:
    """Find which root directory a discovered file belongs to."""
    # Pre‑sort roots by length descending to match the most specific root.
    for root in sorted(roots, key=lambda r: len(str(r)), reverse=True):
        try:
            path.relative_to(root)
            return root
        except ValueError:
            continue
    return roots[0]  # Fallback