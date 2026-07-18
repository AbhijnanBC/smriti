"""
builder.py — SourceDocument construction.

Responsibility: Assemble the final SourceDocument objects from
validated metadata and content hash.

Input:
  - FileMetadata (from metadata.py)
  - content_hash: str (from hashing.py)
  - source_root: Path (which root dir this file came from)

Output:
  - SourceDocument (immutable, file‑centric)
"""

from datetime import datetime
from pathlib import Path
import structlog

from smriti.core.models import FileFormat, SourceDocument
from smriti.discovery.metadata import FileMetadata

logger = structlog.get_logger(__name__)

# Map file extensions to FileFormat enum values
_EXTENSION_TO_FORMAT = {
    ".md": FileFormat.MARKDOWN,
    ".txt": FileFormat.TEXT,
    ".pdf": FileFormat.PDF,
}

def build_source_document(
    metadata: FileMetadata,
    content_hash: str,
    source_root: Path,
) -> SourceDocument:
    """
    Construct a SourceDocument from its component parts.

    Args:
        metadata:       Filesystem metadata from metadata.py
        content_hash:   SHA256 digest from hashing.py
        source_root:    The root directory this file was found under

    Returns:
        Immutable SourceDocument.
    """
    path = metadata.path
    format = _EXTENSION_TO_FORMAT.get(metadata.extension, FileFormat.TEXT)

    # ADR-7: doc_id is the content hash itself — content defines identity.
    doc_id = content_hash

    # Relative path for human-readable display
    try:
        relative_path = path.relative_to(source_root)
    except ValueError:
        relative_path = path  # Fallback if not under source_root

    doc = SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=relative_path,
        source_root=source_root,
        format=format,
        content_hash=content_hash,
        size_bytes=metadata.size_bytes,
        modified_at=metadata.modified_at,
    )

    logger.debug(
        "source document built",
        doc_id=doc_id[:8],
        path=str(relative_path),
        format=format.value,
    )

    return doc