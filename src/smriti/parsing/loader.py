"""
loader.py — Format dispatcher.

Responsibility:
    Choose the correct extractor based on SourceDocument.format.
    Coordinate extraction → normalization → statistics → builder pipeline.
    Return a Document or record the failure.

Rules:
    ✅ Dispatch based on FileFormat enum
    ✅ Coordinate the full single-document pipeline
    ✅ Catch document-level errors (one failure must not stop the batch)
    ✅ Return (Document | None, error_message | None)

    ❌ Never extract text itself (delegates to format-specific extractors)
    ❌ Never create Document directly (delegates to builder.py)
    ❌ Never access filesystem beyond passing path to extractor

Pipeline for each document:
    SourceDocument
        ↓
    Format-specific extractor → RawExtractionResult
        ↓
    normalize.normalize_text() → NormalizationResult (normalized_text, warnings)
        ↓
    statistics.compute_statistics() → TextStatistics
        ↓
    builder.build_document() → Document
"""

import structlog

from smriti.core.models import (
    Document,
    FileFormat,
    NormalizationResult,
    SourceDocument,
)
from smriti.exceptions import (
    BuilderError,
    DocumentError,
    EncodingError,
    LoaderError,
    MarkdownExtractionError,
    NormalizationError,
    PdfExtractionError,
    StatisticsError,
    TextExtractionError,
)
from smriti.parsing.builder import build_document
from smriti.parsing.markdown import MarkdownExtractor
from smriti.parsing.normalize import normalize_text
from smriti.parsing.pdf import PdfExtractor
from smriti.parsing.statistics import compute_statistics
from smriti.parsing.text import TextExtractor

logger = structlog.get_logger(__name__)

# Instantiate extractors once — they are stateless after init
_markdown_extractor = MarkdownExtractor()
_pdf_extractor = PdfExtractor()
_text_extractor = TextExtractor()


def load_document(source: SourceDocument) -> tuple[Document | None, str | None]:
    """
    Execute the full extraction pipeline for a single SourceDocument.

    Args:
        source: Immutable SourceDocument produced by Phase 1.

    Returns:
        (Document, None)       — success
        (None, error_message)  — document-level failure, batch continues

    This function never raises. All exceptions are caught and returned as
    error strings. The pipeline continues with the next document.
    """
    logger.info("loading document", doc_id=source.doc_id[:8], format=source.format.value)

    try:
        # ── Step 1: Dispatch to format-specific extractor ─────────────────────
        extraction_result = _dispatch(source)

        # ── Step 2: Normalize text ────────────────────────────────────────────
        norm_result: NormalizationResult = normalize_text(extraction_result.raw_text)

        # ── Step 3: Compute statistics ────────────────────────────────────────
        stats = compute_statistics(norm_result.normalized_text)

        # ── Step 4: Build Document ────────────────────────────────────────────
        doc = build_document(
            source_document=source,
            extraction_result=extraction_result,
            normalized_text=norm_result.normalized_text,
            normalization_warnings=norm_result.warnings,  # tuple of WarningCode
            text_statistics=stats,
        )

        logger.info(
            "document loaded",
            doc_id=source.doc_id[:8],
            chars=stats.character_count,
            words=stats.word_count,
            warnings=len(doc.extraction_warnings),
        )
        return doc, None

    # ── Document-level failures: log, continue batch ──────────────────────────
    except (
        MarkdownExtractionError,
        PdfExtractionError,
        TextExtractionError,
        EncodingError,
        NormalizationError,
        StatisticsError,
        BuilderError,
        DocumentError,
        LoaderError,
    ) as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error(
            "document extraction failed",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
        )
        return None, error_msg

    except Exception as e:
        # Unexpected error — still document-level, not pipeline-fatal
        error_msg = f"UnexpectedError: {type(e).__name__}: {e}"
        logger.error(
            "unexpected error during extraction",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
            exc_info=True,
        )
        return None, error_msg


def _dispatch(source: SourceDocument):
    """
    Select and call the correct extractor based on FileFormat.

    Raises:
        LoaderError: If the format is unsupported (should never happen post Phase 1).
    """
    match source.format:
        case FileFormat.MARKDOWN:
            return _markdown_extractor.extract(source.path)
        case FileFormat.PDF:
            return _pdf_extractor.extract(source.path)
        case FileFormat.TEXT:
            return _text_extractor.extract(source.path)
        case _:
            raise LoaderError(
                f"Unsupported format {source.format!r} for document {source.doc_id[:8]}. "
                f"Supported: {[f.value for f in FileFormat]}"
            )
