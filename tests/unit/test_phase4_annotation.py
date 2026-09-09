"""
Unit tests for claims/annotation.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, Modality, ExtractionMode
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.parser import SpaCyParser
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def annotator():
    return AssertionAnnotator()


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_structured_candidate(parser, extractor, text):
    from smriti.claims.models import AssertionCandidate
    sentence = SemanticSentence(
        sentence_id="s001", document_id="d001", text=text,
        context="", position=0, char_start=0, char_end=len(text),
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = parser.parse(sentence)
    candidate = AssertionCandidate(
        text=text, span_start=0, span_end=len(text),
        source=parsed, boundary_reason="test",
    )
    return extractor.extract(candidate, parser)


def test_negation_detected(parser, extractor, annotator):
    """'Python does not support X' → is_negated=True."""
    sc = make_structured_candidate(parser, extractor, "Python does not support this feature.")
    annotated = annotator.annotate(sc)
    assert annotated.linguistic_metadata.is_negated is True


def test_no_negation_in_positive(parser, extractor, annotator):
    """'Python supports X' → is_negated=False."""
    sc = make_structured_candidate(parser, extractor, "Python supports generators.")
    annotated = annotator.annotate(sc)
    assert annotated.linguistic_metadata.is_negated is False


def test_modality_possible(parser, extractor, annotator):
    """'Python may be faster' → modality=POSSIBLE."""
    sc = make_structured_candidate(parser, extractor, "Python may be faster than Java.")
    annotated = annotator.annotate(sc)
    assert annotated.linguistic_metadata.modality == Modality.POSSIBLE


def test_modality_certain(parser, extractor, annotator):
    """'Python is fast' → modality=CERTAIN."""
    sc = make_structured_candidate(parser, extractor, "Python is fast.")
    annotated = annotator.annotate(sc)
    assert annotated.linguistic_metadata.modality == Modality.CERTAIN


def test_conditional_detected(parser, extractor, annotator):
    """'If X is installed, Y works' → is_conditional=True."""
    sc = make_structured_candidate(parser, extractor,
                                   "If CUDA is installed, PyTorch uses the GPU.")
    annotated = annotator.annotate(sc)
    assert annotated.semantic_metadata.is_conditional is True


def test_text_not_modified_by_annotation(parser, extractor, annotator):
    """Annotation MUST NOT modify claim text."""
    text = "Python does not support this feature."
    sc = make_structured_candidate(parser, extractor, text)
    annotated = annotator.annotate(sc)
    assert annotated.text == text


def test_annotation_never_raises(parser, extractor, annotator):
    """Annotation must never raise regardless of input."""
    sc = make_structured_candidate(parser, extractor, "!!! weird ?? input !!!")
    annotated = annotator.annotate(sc)
    assert annotated is not None    