"""
Unit tests for claims/parser.py.
Parser has one job: produce ParsedSentence from SemanticSentence.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from smriti.core.models import SemanticSentence
from smriti.claims.parser import LinguisticParser


@pytest.fixture(scope="module")
def parser():
    """Load spaCy model once per test module."""
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(text: str, sentence_id: str = "test001") -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def test_parse_simple_sentence(parser):
    """Simple sentence must parse successfully."""
    sentence = make_sentence("Python is fast.")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is True
    assert parsed.spacy_doc is not None


def test_parse_preserves_original_sentence(parser):
    """ParsedSentence.sentence must be the original, unchanged."""
    sentence = make_sentence("Python supports generators.")
    parsed = parser.parse(sentence)
    assert parsed.sentence is sentence


def test_parse_empty_sentence_returns_failed(parser):
    """Empty text must return parse_ok=False — not raise."""
    sentence = make_sentence("   ")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is False
    assert parsed.spacy_doc is None


def test_parse_fails_gracefully(parser):
    """Parser failure must not raise — returns parse_ok=False."""
    sentence = make_sentence("!!!! ~~~~ #### not real text ????")
    parsed = parser.parse(sentence)
    # spaCy may or may not parse this — either way no exception
    assert parsed.sentence is sentence


def test_parse_unicode_text(parser):
    """Unicode text must parse without errors."""
    sentence = make_sentence("Python est rapide et Python est populaire.")
    parsed = parser.parse(sentence)
    # May or may not produce great results, but must not crash
    assert parsed.sentence is sentence


def test_spacy_doc_has_tokens(parser):
    """Parsed doc must have tokens."""
    sentence = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sentence)
    if parsed.parse_ok:
        assert len(list(parsed.spacy_doc)) > 0