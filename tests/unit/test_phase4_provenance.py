"""
Unit tests for multi-span claim provenance (Part 2).

Verifies that AssertionCandidate / ClaimProvenance record exactly which
source tokens (as character spans into the ORIGINAL sentence text, and as
spaCy token indices) produced each claim — including the case where a
coordinated-predicate/object split combines a shared subject+verb run with
only ONE of the two conjuncts.
"""

import pytest
from pathlib import Path

from smriti.core.models import SemanticSentence, BoundaryReason
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.builder import build_claim


@pytest.fixture(scope="module")
def parser():
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def detector():
    return BoundaryDetector()


def make_sentence(text: str, sentence_id: str = "s001") -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
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


def run_full_pipeline(parser, candidate):
    """Push a single AssertionCandidate through structure/annotation/degradation/build."""
    extractor = StructureExtractor()
    annotator = AssertionAnnotator()
    degrader = DegradationHandler()

    structured = extractor.extract(candidate, parser)
    annotated = annotator.annotate(structured)
    validated = degrader.apply(annotated)
    return build_claim(validated)


# ── Simple single-assertion case ──────────────────────────────────────────────

def test_single_assertion_has_one_full_sentence_span(parser, detector):
    """A simple sentence with no coordination: one span covering the whole text."""
    text = "Earth orbits the Sun."
    sent = make_sentence(text)
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1

    candidate = candidates[0]
    assert candidate.boundary_reason == BoundaryReason.SINGLE_ASSERTION
    assert candidate.source_char_spans == ((0, len(text)),)
    # All tokens in the sentence were used.
    assert len(candidate.source_token_ids) == len(parsed.spacy_doc)

    # And it must be wired all the way through to the built Claim's provenance.
    claim = run_full_pipeline(parser, candidate)
    assert claim.provenance.source_char_spans == ((0, len(text)),)
    assert claim.provenance.reconstruction_rule == "single_assertion"
    start, end = claim.provenance.source_char_spans[0]
    assert text[start:end] == text


def test_single_assertion_spans_reconstruct_original_text(parser, detector):
    text = "Deep learning is powerful."
    sent = make_sentence(text)
    parsed = parser.parse(sent)
    candidate = detector.detect(parsed)[0]
    for (start, end) in candidate.source_char_spans:
        assert text[start:end] in text


# ── Coordinated-predicate/object split ────────────────────────────────────────

def test_coordinated_predicate_object_split_has_two_spans(parser, detector):
    """
    'Python supports generators and decorators.' splits into two claims.
    The claim built from the SECOND conjunct ('decorators') must record TWO
    disjoint spans: the shared 'Python supports' run, and the 'decorators'
    run — never the tokens belonging to the other conjunct ('generators').
    """
    text = "Python supports generators and decorators."
    sent = make_sentence(text)
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 2
    for c in candidates:
        assert c.boundary_reason == BoundaryReason.COORDINATED_PREDICATE

    # Identify the candidate that actually reconstructed "decorators".
    decorators_candidate = next(c for c in candidates if "decorators" in c.text)
    assert "generators" not in decorators_candidate.text

    spans = decorators_candidate.source_char_spans
    assert len(spans) == 2, f"expected 2 contiguous spans, got {spans}"

    reconstructed_fragments = [text[a:b] for (a, b) in spans]
    # One span must be the shared subject+verb run...
    assert any("Python" in frag and "supports" in frag for frag in reconstructed_fragments)
    # ...and the other must be exactly the "decorators" token, not "generators".
    assert any(frag.strip() == "decorators" for frag in reconstructed_fragments)
    assert not any("generators" in frag for frag in reconstructed_fragments)

    # reconstruction_rule must be recorded through the full pipeline too.
    claim = run_full_pipeline(parser, decorators_candidate)
    assert claim.provenance.reconstruction_rule == "coordinated_predicate"
    assert len(claim.provenance.source_char_spans) == 2
    assert claim.provenance.source_char_spans == spans


def test_coordinated_predicate_token_ids_exclude_other_conjunct(parser, detector):
    """
    The token-id set used to build the 'decorators' claim must not include
    the token index of 'generators' (the OTHER conjunct).
    """
    text = "Python supports generators and decorators."
    sent = make_sentence(text)
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)

    decorators_candidate = next(c for c in candidates if "decorators" in c.text)
    doc = parsed.spacy_doc
    generators_token_id = next(t.i for t in doc if t.text == "generators")
    decorators_token_id = next(t.i for t in doc if t.text == "decorators")

    assert generators_token_id not in decorators_candidate.source_token_ids
    assert decorators_token_id in decorators_candidate.source_token_ids


def test_coordinated_predicate_spans_are_sorted_and_nonoverlapping(parser, detector):
    text = "Python supports generators and decorators."
    sent = make_sentence(text)
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)

    for c in candidates:
        spans = c.source_char_spans
        for (start, end) in spans:
            assert start <= end
        # Spans must be in increasing order and non-overlapping.
        for i in range(1, len(spans)):
            assert spans[i - 1][1] <= spans[i][0]


# ── Parse failure fallback ────────────────────────────────────────────────────

def test_parse_failure_has_no_token_ids_but_full_text_span(parser, detector):
    sent = make_sentence("   ")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.boundary_reason == BoundaryReason.PARSE_FAILED
    assert candidate.source_char_spans == ((0, len(sent.text)),)
    assert candidate.source_token_ids == ()
