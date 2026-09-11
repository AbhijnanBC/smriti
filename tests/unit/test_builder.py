"""
Unit tests for discovery/builder.py.
"""

from pathlib import Path

import pytest
from smriti.core.models import FileFormat
from smriti.discovery.builder import SourceDocument, build_source_document
from smriti.discovery.metadata import extract_metadata


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("Python is great for data science.")
    return f


def test_builder_produces_source_document(sample_file, tmp_path):
    """Builder must return a SourceDocument."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="a" * 64,
        source_root=tmp_path,
    )

    assert isinstance(doc, SourceDocument)


def test_builder_sets_correct_format_md(sample_file, tmp_path):
    """Markdown file gets MARKDOWN format."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="b" * 64,
        source_root=tmp_path,
    )

    assert doc.format == FileFormat.MARKDOWN


def test_builder_doc_is_immutable(sample_file, tmp_path):
    """SourceDocument is frozen — mutation must raise."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="c" * 64,
        source_root=tmp_path,
    )

    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_builder_relative_path(tmp_path):
    """relative_path must be relative to source_root."""
    subdir = tmp_path / "notes"
    subdir.mkdir()
    f = subdir / "deep.md"
    f.write_text("Some content.")

    meta = extract_metadata(f)

    doc = build_source_document(
        metadata=meta,
        content_hash="d" * 64,
        source_root=tmp_path,
    )

    assert doc.relative_path == Path("notes/deep.md")


def test_builder_doc_id_is_content_hash(sample_file, tmp_path):
    """doc_id must equal content_hash."""
    meta = extract_metadata(sample_file)
    content_hash = "e" * 64
    doc = build_source_document(meta, content_hash, tmp_path)
    assert doc.doc_id == content_hash


def test_builder_doc_id_is_deterministic(sample_file, tmp_path):
    """Same input must produce same doc_id every time."""
    meta = extract_metadata(sample_file)

    doc1 = build_source_document(
        metadata=meta,
        content_hash="f" * 64,
        source_root=tmp_path,
    )
    doc2 = build_source_document(
        metadata=meta,
        content_hash="f" * 64,
        source_root=tmp_path,
    )

    assert doc1.doc_id == doc2.doc_id
