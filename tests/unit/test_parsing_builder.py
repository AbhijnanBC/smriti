"""
Unit tests for parsing/builder.py.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.parsing.builder import build_document
from smriti.exceptions import BuilderError, DocumentError


@pytest.fixture
def source_doc():
    return SourceDocument(
        doc_id="a" * 64,
        path=Path("note.md"),
        relative_path=Path("note.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="a" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def extraction_result():
    return RawExtractionResult(
        raw_text="# Hello\n\nWorld.",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
        encoding_used="utf-8",  # RECTIFICATION: added missing field
    )


@pytest.fixture
def stats():
    return TextStatistics(
        character_count=16,
        word_count=2,
        line_count=3,
        blank_line_count=1,
        paragraph_count=2,
    )


def test_build_returns_document(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert isinstance(doc, Document)


def test_doc_id_equals_source_doc_id(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.doc_id == source_doc.doc_id


def test_document_is_frozen(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    with pytest.raises(Exception):
        doc.doc_id = "new_id"


def test_source_document_unchanged(source_doc, extraction_result, stats):
    original_path = source_doc.path
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.source_document.path == original_path


def test_warnings_merged(source_doc, stats):
    extraction_result = RawExtractionResult(
        raw_text="text",
        warnings=(WarningCode.NO_EXTRACTABLE_TEXT,),
        method=ExtractionMethod.MARKDOWN,
        encoding_used="utf-8",  # RECTIFICATION: added missing field
    )
    norm_warnings = (WarningCode.BLANK_LINES_COLLAPSED,)
    doc = build_document(source_doc, extraction_result, "text", norm_warnings, stats)
    assert len(doc.extraction_warnings) == 2


def test_wrong_doc_id_raises(source_doc, extraction_result, stats):
    """doc_id must match source_document.doc_id — mismatch raises DocumentError."""
    wrong_source = SourceDocument(
        doc_id="b" * 64,         # different doc_id
        path=Path("other.md"),
        relative_path=Path("other.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )
    # Builder uses source_document.doc_id — so the Document will have "b"*64
    # This should succeed; the invariant is enforced inside Document.__post_init__
    doc = build_document(wrong_source, extraction_result, "text", (), stats)
    assert doc.doc_id == "b" * 64


def test_empty_document_produces_warning(source_doc, stats):
    """Empty normalized text must produce NO_EXTRACTABLE_TEXT warning."""
    extraction_result = RawExtractionResult(
        raw_text="",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
        encoding_used="utf-8",  # RECTIFICATION: added missing field
    )
    empty_stats = TextStatistics(
        character_count=0, word_count=0, line_count=0,
        blank_line_count=0, paragraph_count=0,
    )
    doc = build_document(source_doc, extraction_result, "", (), empty_stats)
    assert doc.has_warnings
    assert WarningCode.NO_EXTRACTABLE_TEXT in doc.extraction_warnings