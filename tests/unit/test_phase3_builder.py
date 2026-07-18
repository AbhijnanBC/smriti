"""
Unit tests for extraction/builder.py.
"""

import pytest
from pathlib import Path
from smriti.extraction.builder import build_sentence, _compute_sentence_id


def test_build_returns_semantic_sentence():
    from smriti.core.models import SemanticSentence
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="Technology",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert isinstance(s, SemanticSentence)


def test_sentence_id_is_16_chars():
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert len(s.sentence_id) == 16


def test_sentence_id_is_deterministic():
    """Same inputs must always produce the same ID."""
    s1 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    s2 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    assert s1.sentence_id == s2.sentence_id


def test_different_text_different_id():
    s1 = build_sentence("Python is great.", "doc1", Path("a.md"), "", 0, 0, 16)
    s2 = build_sentence("Julia is faster.", "doc1", Path("a.md"), "", 0, 0, 16)
    assert s1.sentence_id != s2.sentence_id


def test_different_position_different_id():
    """Same text at different char_start must produce different ID."""
    s1 = build_sentence("same text.", "doc1", Path("a.md"), "", 0, 0, 10)
    s2 = build_sentence("same text.", "doc1", Path("a.md"), "", 1, 50, 60)
    assert s1.sentence_id != s2.sentence_id


def test_semantic_sentence_is_frozen():
    """SemanticSentence must be immutable."""
    s = build_sentence("Python.", "doc1", Path("a.md"), "", 0, 0, 7)
    with pytest.raises(Exception):
        s.text = "Julia."


def test_context_stored_separately():
    """Context must be stored as-is, never fused into text."""
    s = build_sentence("Supports tensors.", "doc1", Path("a.md"), "CUDA", 0, 0, 17)
    assert s.text == "Supports tensors."
    assert s.context == "CUDA"
    assert "CUDA" not in s.text


def test_empty_context_allowed():
    """Sentences at document root have no context."""
    s = build_sentence("Introduction.", "doc1", Path("a.md"), "", 0, 0, 13)
    assert s.context == ""


def test_builder_adds_provenance_and_version():
    """Test that origin_block_type and schema_version are correctly set."""
    from smriti.extraction.scanner import BlockType

    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
        origin_block_type=BlockType.PARAGRAPH,
    )
    assert s.origin_block_type == BlockType.PARAGRAPH
    assert s.schema_version == "3.0"