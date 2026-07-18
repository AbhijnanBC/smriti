"""
Unit tests for claims/structure.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, ExtractionMode
from smriti.claims.parser import LinguisticParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_parsed(parser, text):
    from smriti.claims.parser import LinguisticParser
    sentence = SemanticSentence(
        sentence_id="s001",
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    return parser.parse(sentence)


def make_candidate(parser, text):
    from smriti.claims.models import AssertionCandidate
    parsed = make_parsed(parser, text)
    return AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason="single_assertion",
    )


def test_svo_extraction_simple(parser, extractor):
    """'Python supports generators' → S=Python, P=supports, O=generators."""
    candidate = make_candidate(parser, "Python supports generators.")
    result = extractor.extract(candidate)
    if result.extraction_mode == ExtractionMode.STRUCTURED:
        assert result.structured_assertion is not None
        assert result.structured_assertion.predicate is not None


def test_failed_parse_produces_lexical(extractor):
    """If parse failed, mode must be LEXICAL."""
    from smriti.claims.models import ParsedSentence, AssertionCandidate
    from smriti.core.models import SemanticSentence
    sentence = SemanticSentence(
        sentence_id="s002", document_id="d001", text="test",
        context="", position=0, char_start=0, char_end=4,
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    failed_parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text="test", span_start=0, span_end=4,
        source=failed_parsed, boundary_reason="parse_failed",
    )
    result = extractor.extract(candidate)
    assert result.extraction_mode == ExtractionMode.LEXICAL


def test_extraction_never_raises(parser, extractor):
    """Extraction must NEVER raise regardless of input."""
    candidate = make_candidate(parser, "!!!! ~~~~ something very weird ????")
    result = extractor.extract(candidate)
    assert result is not None  # Always returns something
    assert result.candidate.text == "!!!! ~~~~ something very weird ????"