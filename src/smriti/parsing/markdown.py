"""
markdown.py — Markdown text extractor.

Responsibility:
    Read a Markdown file and return its raw decoded text.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Preserve ALL Markdown syntax (headings, lists, code blocks, tables)
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ Do NOT parse Markdown AST
    ❌ Do NOT strip Markdown syntax
    ❌ Do NOT extract YAML front matter
    ❌ Do NOT render HTML
    ❌ Do NOT detect language
    ❌ Do NOT split sentences

Why preserve Markdown syntax?
    "# AI is transforming" is richer context than "AI is transforming".
    Phase 3 uses headings as semantic signals.
    Removing '#' changes information — that belongs to interpretation, not extraction.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import MarkdownExtractionError, EncodingError

logger = structlog.get_logger(__name__)


class MarkdownExtractor:
    """Extracts raw text from a Markdown file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: List[str] = (
            config["parsing"].get("encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a Markdown file.

        Args:
            path: Absolute path to a .md file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=MARKDOWN.

        Raises:
            MarkdownExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: List[WarningCode] = []

        logger.debug("reading markdown", path=str(path))

        raw_bytes = self._read_bytes(path)
        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect and warn about mixed line endings BEFORE normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "markdown extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.MARKDOWN,
            encoding_used=encoding_used,
        )

    def _read_bytes(self, path: Path) -> bytes:
        """Read raw bytes from file."""
        try:
            return path.read_bytes()
        except OSError as e:
            raise MarkdownExtractionError(f"Cannot read {path}: {e}") from e

    def _decode(self, raw_bytes: bytes, path: Path) -> Tuple[str, Optional[WarningCode], str]:
        """
        Decode bytes using the encoding fallback chain.

        Returns:
            (decoded_text, warning_code_or_None, encoding_used)
        """
        for i, encoding in enumerate(self._encoding_fallbacks):
            try:
                text = raw_bytes.decode(encoding)
                warning = WarningCode.ENCODING_FALLBACK if i > 0 else None
                return text, warning, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        raise EncodingError(
            f"Cannot decode {path} with any supported encoding: "
            f"{self._encoding_fallbacks}"
        )