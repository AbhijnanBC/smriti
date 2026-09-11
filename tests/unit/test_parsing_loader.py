"""
Unit tests for parsing/loader.py.
"""

from datetime import UTC, datetime
from pathlib import Path

from smriti.core.models import FileFormat, SourceDocument
from smriti.parsing.loader import load_document


def make_source(path: Path, fmt: FileFormat, doc_id: str = "a" * 64) -> SourceDocument:
    return SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=path.name,
        source_root=path.parent,
        format=fmt,
        content_hash=doc_id,
        size_bytes=path.stat().st_size if path.exists() else 0,
        modified_at=datetime.now(tz=UTC),
    )


def test_markdown_document_succeeds(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# AI\n\nAI is transforming everything.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None
    assert "AI" in doc.normalized_text


def test_text_document_succeeds(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("Plain text content here.", encoding="utf-8")
    source = make_source(f, FileFormat.TEXT)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None


def test_nonexistent_file_returns_none_not_raise(tmp_path):
    """Missing file must return (None, error) — NOT raise."""
    source = make_source(tmp_path / "ghost.md", FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None
    assert "Error" in error or "error" in error.lower()


def test_corrupted_pdf_returns_none_not_raise(tmp_path):
    """Corrupted PDF must return (None, error) — NOT raise, batch continues."""
    f = tmp_path / "bad.pdf"
    f.write_bytes(b"not a pdf")
    source = make_source(f, FileFormat.PDF)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None


def test_doc_id_preserved(tmp_path):
    """doc_id must equal source_document.doc_id — identity invariant."""
    f = tmp_path / "note.md"
    f.write_text("hello world", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert doc.doc_id == source.doc_id


def test_normalized_text_strips_crlf(tmp_path):
    """CRLF in source file must become LF in normalized_text."""
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "\r\n" not in doc.normalized_text


def test_markdown_headings_preserved(tmp_path):
    """# headings must survive extraction (not stripped)."""
    f = tmp_path / "headings.md"
    f.write_text("# Main Topic\n\n## Subtopic\n\nContent.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "# Main Topic" in doc.normalized_text
    assert "## Subtopic" in doc.normalized_text


def test_unicode_content_handled(tmp_path):
    """Unicode content (CJK, emoji, accented) must be preserved."""
    f = tmp_path / "unicode.md"
    f.write_text("# 日本語\n\nCafé résumé naïve.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "日本語" in doc.normalized_text
    assert "Café" in doc.normalized_text
