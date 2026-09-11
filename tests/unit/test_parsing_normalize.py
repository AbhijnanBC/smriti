"""
Unit tests for parsing/normalize.py.

Every normalization rule is tested in isolation.
Determinism is verified: same input → same output every time.
"""

import pytest
from smriti.core.models import WarningCode
from smriti.parsing.normalize import normalize_text

# ── Unicode normalization ─────────────────────────────────────────────────────


def test_nfc_normalization_makes_equivalent_sequences_identical():
    """é as NFC and NFD decomposed must both normalize to the same NFC form."""

    nfc_e = "\u00e9"  # é as single code point (NFC)
    nfd_e = "e\u0301"  # é as e + combining acute (NFD)
    assert nfc_e != nfd_e  # They start different
    result_nfc = normalize_text(nfc_e)
    result_nfd = normalize_text(nfd_e)
    assert (
        result_nfc.normalized_text == result_nfd.normalized_text
    )  # After normalization: identical


def test_bom_is_removed():
    """UTF-8 BOM character must be stripped."""
    text_with_bom = "\ufeffHello world"
    result = normalize_text(text_with_bom)
    assert not result.normalized_text.startswith("\ufeff")
    assert WarningCode.BOM_REMOVED in result.warnings


# ── Line ending normalization ─────────────────────────────────────────────────


def test_crlf_converted_to_lf():
    """Windows CRLF must become LF."""
    result = normalize_text("line1\r\nline2\r\nline3")
    assert "\r\n" not in result.normalized_text
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"
    assert WarningCode.LINE_ENDINGS_NORMALIZED in result.warnings


def test_cr_only_converted_to_lf():
    """Old Mac CR-only must become LF."""
    result = normalize_text("line1\rline2\rline3")
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"


def test_pure_lf_unchanged():
    """Files already using LF must not be modified (no spurious warning)."""
    text = "line1\nline2\nline3"
    result = normalize_text(text)
    assert result.normalized_text == text
    assert WarningCode.LINE_ENDINGS_NORMALIZED not in result.warnings


# ── Trailing whitespace ───────────────────────────────────────────────────────


def test_trailing_whitespace_removed_per_line():
    """Trailing spaces and tabs on each line must be removed."""
    result = normalize_text("hello   \nworld\t\n")
    lines = result.normalized_text.split("\n")
    for line in lines:
        assert not line.endswith(" ")
        assert not line.endswith("\t")
    assert WarningCode.TRAILING_WHITESPACE_REMOVED in result.warnings


def test_leading_indentation_preserved():
    """Leading whitespace (indentation) must NEVER be removed."""
    text = "    indented line\n        double indent"
    result = normalize_text(text)
    lines = result.normalized_text.split("\n")
    assert lines[0].startswith("    ")
    assert lines[1].startswith("        ")


# ── Blank line collapsing ─────────────────────────────────────────────────────


def test_excessive_blank_lines_collapsed():
    """100 consecutive blank lines must collapse to max configured blank lines."""
    text = "paragraph1\n" + "\n" * 100 + "paragraph2"
    result = normalize_text(text)
    # Should not have more than collapse_blank_lines (default=2) consecutive blank lines
    assert "\n\n\n\n" not in result.normalized_text  # More than 2 blank lines = 4+ newlines
    assert WarningCode.BLANK_LINES_COLLAPSED in result.warnings


def test_single_blank_line_preserved():
    """A single blank line between paragraphs must be preserved."""
    text = "paragraph1\n\nparagraph2"
    result = normalize_text(text)
    assert "paragraph1\n\nparagraph2" in result.normalized_text


# ── Control characters ────────────────────────────────────────────────────────


def test_control_characters_removed():
    """Non-printable control characters (except LF, TAB) must be removed."""
    text = "hello\x07world\x1btest"  # BEL, ESC
    result = normalize_text(text)
    assert "\x07" not in result.normalized_text
    assert "\x1b" not in result.normalized_text
    assert WarningCode.CONTROL_CHARS_REMOVED in result.warnings


def test_tab_preserved():
    """TAB characters must be preserved (carry indentation meaning)."""
    text = "\thello\tworld"
    result = normalize_text(text)
    assert "\t" in result.normalized_text


# ── Determinism ───────────────────────────────────────────────────────────────


def test_normalization_is_deterministic():
    """Same input must always produce same output."""
    text = "Hello\r\n\r\nWorld   \r\n"
    result1 = normalize_text(text)
    result2 = normalize_text(text)
    assert result1.normalized_text == result2.normalized_text
    assert result1.warnings == result2.warnings


def test_empty_string_handled():
    """Empty string must return empty string without errors."""
    result = normalize_text("")
    assert result.normalized_text == ""


def test_whitespace_only_string_handled():
    """Whitespace-only input must return empty string."""
    result = normalize_text("   \n\t\n   ")
    assert result.normalized_text == ""


# ── Error handling ────────────────────────────────────────────────────────────


def test_non_string_raises():
    """Passing non-string must raise NormalizationError."""
    from smriti.exceptions import NormalizationError

    with pytest.raises(NormalizationError):
        normalize_text(None)  # type: ignore
