"""
text.py — Plain-text extractor.

Responsibility:
    Read a .txt file and return its raw decoded text.
    Simplest extractor — reads bytes, decodes, returns.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ No semantic processing
    ❌ No format-specific parsing
"""

from pathlib import Path

import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import EncodingError, TextExtractionError

logger = structlog.get_logger(__name__)


class TextExtractor:
    """Extracts raw text from a plain-text (.txt) file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: list[str] = config["parsing"].get(
            "encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"]
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a plain-text file.

        Args:
            path: Absolute path to a .txt file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=TEXT.

        Raises:
            TextExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: list[WarningCode] = []

        logger.debug("reading text file", path=str(path))

        try:
            raw_bytes = path.read_bytes()
        except OSError as e:
            raise TextExtractionError(f"Cannot read {path}: {e}") from e

        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect mixed line endings before normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "text extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.TEXT,
            encoding_used=encoding_used,
        )

    def _decode(self, raw_bytes: bytes, path: Path) -> tuple[str, WarningCode | None, str]:
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
            f"Cannot decode {path} with any supported encoding: " f"{self._encoding_fallbacks}"
        )
