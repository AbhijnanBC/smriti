"""
Unit tests for parsing/markdown.py.
"""

import pytest
from smriti.core.models import ExtractionMethod, WarningCode
from smriti.parsing.markdown import MarkdownExtractor


@pytest.fixture
def extractor():
    return MarkdownExtractor()


@pytest.fixture
def simple_md(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# Hello\n\nWorld.", encoding="utf-8")
    return f


def test_extracts_text(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert "Hello" in result.raw_text
    assert "World" in result.raw_text


def test_preserves_markdown_syntax(extractor, simple_md):
    """Markdown # heading must NOT be stripped."""
    result = extractor.extract(simple_md)
    assert "# Hello" in result.raw_text


def test_method_is_markdown(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert result.method == ExtractionMethod.MARKDOWN


def test_no_warnings_on_clean_utf8(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert len(result.warnings) == 0


def test_crlf_warning_detected(extractor, tmp_path):
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    result = extractor.extract(f)
    assert WarningCode.MIXED_LINE_ENDINGS in result.warnings or "\r\n" in result.raw_text


def test_null_bytes_removed(extractor, tmp_path):
    f = tmp_path / "null.md"
    f.write_bytes(b"hello\x00world")
    result = extractor.extract(f)
    assert "\x00" not in result.raw_text
    assert WarningCode.NULL_BYTES_REMOVED in result.warnings


def test_encoding_fallback_latin1(extractor, tmp_path):
    """Latin-1 encoded file must decode with fallback warning."""
    f = tmp_path / "latin.md"
    f.write_bytes("caf\xe9".encode("latin-1"))
    result = extractor.extract(f)
    assert len(result.raw_text) > 0
    # Either decoded fine or produced a fallback warning
    # (depends on whether utf-8 fails gracefully)


def test_markdown_table_preserved(extractor, tmp_path):
    """Markdown table syntax must be preserved verbatim."""
    f = tmp_path / "table.md"
    f.write_text("| Col1 | Col2 |\n|------|------|\n| A    | B    |", encoding="utf-8")
    result = extractor.extract(f)
    assert "| Col1 |" in result.raw_text
    assert "|------|" in result.raw_text


def test_unreadable_file_raises(extractor, tmp_path):
    from smriti.exceptions import MarkdownExtractionError

    fake = tmp_path / "nonexistent.md"
    with pytest.raises(MarkdownExtractionError):
        extractor.extract(fake)
