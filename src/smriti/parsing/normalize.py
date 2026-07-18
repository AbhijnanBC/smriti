"""
normalize.py — Text normalization pipeline.

Responsibility:
    Transform raw extracted text into a canonical, deterministic form.
    This is the ONLY module that performs normalization.

Normalization order (NEVER reorder — order matters):
    1. Unicode NFC normalization
    2. Remove BOM (if present after decoding)
    3. Normalize line endings → LF
    4. Remove trailing whitespace per line
    5. Normalize tabs (if configured)
    6. Collapse consecutive blank lines
    7. Strip leading/trailing whitespace from entire document

Rules:
    ✅ Make equivalent text identical
    ✅ Never change meaning
    ✅ Record every transformation as a warning

    ❌ Do NOT change words (colour → color)
    ❌ Do NOT expand contractions (can't → cannot)
    ❌ Do NOT stem or lemmatize
    ❌ Do NOT remove stopwords
    ❌ Do NOT remove indentation
    ❌ Do NOT remove code block content

Determinism guarantee:
    Given identical input, this function always produces identical output.
    No timestamps, no randomness, no locale-dependent behavior.
"""

import re
import unicodedata
from typing import List
import structlog

from smriti.core.config import get_config
from smriti.exceptions import NormalizationError
from smriti.core.models import NormalizationResult, WarningCode

logger = structlog.get_logger(__name__)


def normalize_text(raw_text: str) -> NormalizationResult:
    """
    Apply the full normalization pipeline to raw extracted text.

    Args:
        raw_text: Text exactly as decoded from the source file.

    Returns:
        NormalizationResult(normalized_text, warnings)
        where warnings is a tuple of WarningCode enums describing transformations applied.

    Raises:
        NormalizationError: If normalization itself fails unexpectedly.
    """
    if not isinstance(raw_text, str):
        raise NormalizationError(f"raw_text must be str, got {type(raw_text)}")

    config = get_config()
    parsing_cfg = config.get("parsing", {})

    unicode_form: str = parsing_cfg.get("unicode_normalization", "NFC")
    collapse_blank_lines: int = parsing_cfg.get("collapse_blank_lines", 2)
    remove_trailing_ws: bool = parsing_cfg.get("remove_trailing_whitespace", True)

    warnings: List[WarningCode] = []
    text = raw_text

    try:
        # ── Step 1: Unicode normalization ────────────────────────────────
        text_before = text
        text = unicodedata.normalize(unicode_form, text)
        if text != text_before:
            warnings.append(WarningCode.UNICODE_NORMALIZED)

        # ── Step 2: Remove UTF-8 BOM ─────────────────────────────────────
        if text.startswith("\ufeff"):
            text = text[1:]
            warnings.append(WarningCode.BOM_REMOVED)

        # ── Step 3: Normalize line endings → LF ──────────────────────────
        has_crlf = "\r\n" in text
        has_cr_only = "\r" in text.replace("\r\n", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if has_crlf or has_cr_only:
            warnings.append(WarningCode.LINE_ENDINGS_NORMALIZED)

        # ── Step 4: Remove trailing whitespace per line ──────────────────
        if remove_trailing_ws:
            lines = text.split("\n")
            stripped_lines = [line.rstrip() for line in lines]
            if stripped_lines != lines:
                warnings.append(WarningCode.TRAILING_WHITESPACE_REMOVED)
            text = "\n".join(stripped_lines)

        # ── Step 5: Remove control characters (except LF and TAB) ────────
        control_char_pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
        text_before = text
        text = control_char_pattern.sub("", text)
        if text != text_before:
            warnings.append(WarningCode.CONTROL_CHARS_REMOVED)

        # ── Step 6: Collapse consecutive blank lines ─────────────────────
        if collapse_blank_lines >= 0:
            max_newlines = collapse_blank_lines + 1
            pattern = re.compile(r"\n{" + str(max_newlines + 1) + r",}")
            replacement = "\n" * max_newlines
            text_before = text
            text = pattern.sub(replacement, text)
            if text != text_before:
                warnings.append(WarningCode.BLANK_LINES_COLLAPSED)

        # ── Step 7: Strip leading/trailing whitespace ────────────────────
        text = text.strip()

    except NormalizationError:
        raise
    except Exception as e:
        raise NormalizationError(f"Normalization failed unexpectedly: {e}") from e

    logger.debug(
        "normalization complete",
        original_chars=len(raw_text),
        normalized_chars=len(text),
        warnings=len(warnings),
    )

    return NormalizationResult(normalized_text=text, warnings=tuple(warnings))
