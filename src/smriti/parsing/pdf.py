"""
pdf.py — PDF text extractor.

Responsibility:
    Extract the embedded text layer from a PDF file.
    Concatenate pages into a single string.
    Record warnings for pages with no extractable text.

Rules:
    ✅ Extract text layer from each page
    ✅ Concatenate pages with explicit page break marker
    ✅ Record per-page warnings for empty pages (as WarningCode enums)
    ✅ Respect max_pdf_pages config limit

    ❌ No OCR (ever)
    ❌ No page rendering
    ❌ No layout detection
    ❌ No table inference
    ❌ No image extraction

If a PDF has no text layer at all (image-only PDF):
    → Record WarningCode.NO_EXTRACTABLE_TEXT
    → Return empty string (do NOT fail the pipeline)
    → Phase 3 will produce 0 claims from this document

Library: pypdf (replaces deprecated PyPDF2)
"""

from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import PdfExtractionError

logger = structlog.get_logger(__name__)

# Explicit page break marker – used to separate text from different pages.
# This helps downstream phases know where page boundaries occur.
PAGE_BREAK_MARKER = "\n\n--- PAGE BREAK ---\n\n"


class PdfExtractor:
    """Extracts raw text from a PDF file using the embedded text layer."""

    def __init__(self) -> None:
        config = get_config()
        parsing_cfg = config.get("parsing", {})
        self._max_pages: int = parsing_cfg.get("max_pdf_pages", 500)
        self._max_text_length: int = parsing_cfg.get("max_text_length_chars", 5_000_000)

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Extract text from all pages of a PDF.

        Args:
            path: Absolute path to a .pdf file (already validated by Phase 1).

        Returns:
            RawExtractionResult with concatenated page text, warnings (as WarningCode), method=PDF.

        Raises:
            PdfExtractionError: If the PDF cannot be opened or is fatally corrupted.
        """
        try:
            import pypdf
        except ImportError as e:
            raise PdfExtractionError("pypdf is required for PDF extraction") from e

        warnings: List[WarningCode] = []
        page_texts: List[str] = []

        logger.debug("reading pdf", path=str(path))

        try:
            reader = pypdf.PdfReader(str(path))
        except Exception as e:
            raise PdfExtractionError(f"Cannot open PDF {path}: {e}") from e

        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, self._max_pages)

        if total_pages > self._max_pages:
            warnings.append(WarningCode.PAGE_LIMIT_REACHED)

        empty_pages: List[int] = []

        for page_num in range(pages_to_process):
            try:
                page = reader.pages[page_num]
                text = page.extract_text() or ""
            except Exception as e:
                warnings.append(WarningCode.PAGE_EXTRACTION_FAILED)
                text = ""

            if text.strip():
                page_texts.append(text)
            else:
                empty_pages.append(page_num + 1)

        if empty_pages:
            # Batch warning — don't produce one warning per empty page
            if len(empty_pages) == pages_to_process:
                warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)
            else:
                warnings.append(WarningCode.EMPTY_PDF_PAGE)

        # Join pages with explicit page break marker
        raw_text = PAGE_BREAK_MARKER.join(page_texts)

        # Guard against pathologically large PDFs
        if len(raw_text) > self._max_text_length:
            raw_text = raw_text[: self._max_text_length]
            warnings.append(WarningCode.TEXT_TRUNCATED)

        logger.debug(
            "pdf extracted",
            path=str(path),
            total_pages=total_pages,
            processed_pages=pages_to_process,
            empty_pages=len(empty_pages),
            chars=len(raw_text),
            warnings=len(warnings),
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.PDF,
            encoding_used="pdf-native",
        )