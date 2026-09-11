"""
metadata.py — Filesystem metadata extraction.

Responsibility: Extract essential filesystem facts about a validated file.
                This is the ONLY module that calls path.stat().

Input:  Validated Path
Output: FileMetadata dataclass

Rules:
  - Never read file contents (that is hashing.py's job)
  - Never infer semantic meaning from metadata
  - Only keep fields needed by future phases:
      path, size_bytes, extension, modified_at (UTC)
  - MIME type, read‑only, creation time are removed (not used later)
  - Encoding detection is deferred to Phase 2
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class FileMetadata:
    """
    Immutable essential filesystem metadata for a single file.
    Produced by Phase 1 and used to build SourceDocument.
    """

    path: Path
    size_bytes: int
    extension: str  # Normalised lowercase (.md / .pdf / .txt)
    modified_at: datetime  # UTC (last modification time)


def extract_metadata(path: Path) -> FileMetadata:
    """
    Extract filesystem metadata from a validated file.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        Immutable FileMetadata.

    Raises:
        OSError: If stat() fails (should not happen post-validation, but guard anyway).
    """
    stat = path.stat()

    # Modified time as UTC-aware datetime
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

    extension = path.suffix.lower()

    metadata = FileMetadata(
        path=path,
        size_bytes=stat.st_size,
        extension=extension,
        modified_at=modified_at,
    )

    logger.debug(
        "metadata extracted",
        path=str(path),
        size_bytes=stat.st_size,
        modified_at=modified_at.isoformat(),
    )

    return metadata
