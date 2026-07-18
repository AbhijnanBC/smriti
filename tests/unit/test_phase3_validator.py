"""
Unit tests for extraction/validator.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.validator import validate_sentences
from smriti.exceptions import SentenceValidationError


def make_sentence(sid, doc_id, text, position, char_start=0, char_end=10, context=""):
    return SemanticSentence(
        sentence_id=sid,
        document_id=doc_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=Path("note.md"),
    )


def test_valid_sentences_pass():
    sentences = [
        make_sentence("aaa", "doc1", "First sentence.", 0, 0, 15),
        make_sentence("bbb", "doc1", "Second sentence.", 1, 16, 32),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 2
    assert warnings == []


def test_empty_sentence_is_discarded():
    sentences = [
        make_sentence("aaa", "doc1", "   ", 0),
        make_sentence("bbb", "doc1", "Real sentence.", 1),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 1
    assert SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED in warnings


def test_duplicate_id_raises():
    sentences = [
        make_sentence("dup", "doc1", "First.", 0),
        make_sentence("dup", "doc1", "Second.", 1),  # Same ID!
    ]
    with pytest.raises(SentenceValidationError, match="Duplicate"):
        validate_sentences(sentences, "doc1")


def test_non_monotonic_position_raises():
    sentences = [
        make_sentence("aaa", "doc1", "First.", 2),  # Position 2
        make_sentence("bbb", "doc1", "Second.", 1), # Position 1 — goes backwards!
    ]
    with pytest.raises(SentenceValidationError):
        validate_sentences(sentences, "doc1")


def test_wrong_document_id_raises():
    sentences = [
        make_sentence("aaa", "wrong_doc", "Text.", 0),
    ]
    with pytest.raises(SentenceValidationError, match="document_id"):
        validate_sentences(sentences, "doc1")


def test_empty_input_returns_empty():
    valid, warnings = validate_sentences([], "doc1")
    assert valid == []
    assert warnings == []


def test_invalid_context_emits_warning():
    from smriti.extraction.rules import CONTEXT_SEPARATOR
    # context with illegal characters (e.g., "Python@CUDA")
    sentences = [
        make_sentence("aaa", "doc1", "text", 0, 0, 4, context="Python@CUDA"),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert SegmentationWarning.VAL_INVALID_CONTEXT in warnings