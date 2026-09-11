"""
builder.py — Document construction.

Responsibility:
    The ONLY module allowed to create Document objects.

    Enforces all Document invariants before construction:
      - doc_id must equal source_document.doc_id (identity preserved)
      - raw_text must be str
      - normalized_text must be str
      - warnings is a tuple of WarningCode
      - text_statistics is a TextStatistics instance

    Returns a frozen (immutable) Document.

Rules:
    ✅ Validate all inputs before construction
    ✅ Enforce doc_id identity invariant
    ✅ Produce immutable Document
    ✅ Warn if document appears to be empty (using WarningCode.NO_EXTRACTABLE_TEXT)

    ❌ No extraction logic
    ❌ No normalization logic
    ❌ No filesystem access

RECTIFIED (external review, P1-1): this module now also calls
parsing.provenance.extract_document_provenance() on the already-extracted
raw_text to populate Document.provenance. This is read-only metadata
parsing (source_id/author/publisher/date, when the document discloses
them), not text extraction or normalization -- raw_text and
normalized_text themselves are untouched, so this does not violate the
"no extraction/normalization logic" rules above.
"""

import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Document,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.exceptions import BuilderError, DocumentError
from smriti.parsing.provenance import extract_document_provenance

logger = structlog.get_logger(__name__)


def build_document(
    source_document: SourceDocument,
    extraction_result: RawExtractionResult,
    normalized_text: str,
    normalization_warnings: tuple[WarningCode, ...],
    text_statistics: TextStatistics,
) -> Document:
    """
    Construct an immutable Document from its component parts.

    Args:
        source_document:        The Phase 1 SourceDocument (must remain unchanged).
        extraction_result:      Raw extraction output (raw_text, warnings, method).
        normalized_text:        Text after full normalization pipeline.
        normalization_warnings: Warnings produced during normalization (WarningCode tuple).
        text_statistics:        Structural statistics from statistics.py.

    Returns:
        Immutable Document with doc_id == source_document.doc_id.

    Raises:
        BuilderError: If any input is invalid.
        DocumentError: If the constructed Document violates an invariant.
    """
    config = get_config()
    min_extractable_chars: int = config.get("parsing", {}).get("min_extractable_chars", 10)

    # ── Input validation ──────────────────────────────────────────────────────
    if not isinstance(source_document, SourceDocument):
        raise BuilderError(f"source_document must be SourceDocument, got {type(source_document)}")
    if not isinstance(extraction_result, RawExtractionResult):
        raise BuilderError("extraction_result must be RawExtractionResult")
    if not isinstance(normalized_text, str):
        raise BuilderError(f"normalized_text must be str, got {type(normalized_text)}")
    if not isinstance(normalization_warnings, tuple):
        raise BuilderError("normalization_warnings must be tuple")
    if not isinstance(text_statistics, TextStatistics):
        raise BuilderError("text_statistics must be TextStatistics")

    # ── Merge all warnings (both are tuples of WarningCode) ──────────────────
    all_warnings: list[WarningCode] = list(extraction_result.warnings) + list(
        normalization_warnings
    )

    # ── Check for empty extraction ────────────────────────────────────────────
    if len(normalized_text.strip()) < min_extractable_chars:
        all_warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)

    # ── Extract disclosed source identity (P1-1), if any ─────────────────────
    # Read-only: parses extraction_result.raw_text, never modifies it.
    provenance = extract_document_provenance(extraction_result.raw_text)

    # ── Build Document ────────────────────────────────────────────────────────
    try:
        doc = Document(
            doc_id=source_document.doc_id,  # Identity inherited, never changed
            source_document=source_document,
            raw_text=extraction_result.raw_text,
            normalized_text=normalized_text,
            extraction_method=extraction_result.method,
            extraction_warnings=tuple(all_warnings),  # tuple of WarningCode
            text_statistics=text_statistics,
            encoding_used=extraction_result.encoding_used,  # <-- ADDED
            schema_version="2.0",
            provenance=provenance,
        )
    except ValueError as e:
        raise DocumentError(f"Document invariant violated: {e}") from e
    except Exception as e:
        raise BuilderError(f"Document construction failed: {e}") from e

    logger.debug(
        "document built",
        doc_id=doc.doc_id[:8],
        method=doc.extraction_method.value,
        chars=text_statistics.character_count,
        words=text_statistics.word_count,
        warnings=len(all_warnings),
    )

    return doc
