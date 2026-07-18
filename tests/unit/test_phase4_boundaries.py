"""
Unit tests for claims/boundaries.py – boundary detection logic.

These tests verify that BoundaryDetector correctly identifies claim boundaries
in various syntactic structures, and that it uses the BoundaryReason enum
and produces AssertionCandidate objects without the confidence field.
"""

import pytest
from pathlib import Path

from smriti.core.models import SemanticSentence, BoundaryReason
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.models import AssertionCandidate


@pytest.fixture(scope="module")
def parser():
    """Load the linguistic parser once for all tests."""
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def detector():
    """BoundaryDetector with default configuration (split_conjunctions=True)."""
    return BoundaryDetector()


def make_sentence(text: str, sentence_id: str = "s001") -> SemanticSentence:
    """Helper to create a SemanticSentence."""
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


# ── Basic functionality ───────────────────────────────────────────────────────

def test_single_sentence_returns_one_candidate(parser, detector):
    """A simple sentence with no coordination must yield exactly one candidate."""
    sent = make_sentence("Python is a high-level language.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert isinstance(candidates[0], AssertionCandidate)
    assert candidates[0].text == sent.text
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION
    # 'confidence' no longer exists – test removed


def test_parse_failure_returns_whole_sentence(parser, detector):
    """When parsing fails, detect() must fall back to whole-sentence candidate."""
    sent = make_sentence("@@@ ??? weird !!!")
    parsed = parser.parse(sent)
    # It may or may not parse, but if parse_ok is False, we expect fallback.
    if not parsed.parse_ok:
        candidates = detector.detect(parsed)
        assert len(candidates) == 1
        assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
        assert candidates[0].text == sent.text


# ── Coordinated predicates (shared subject) ─────────────────────────────────

def test_coordinated_predicate_splits(parser, detector):
    """'Python supports X and Y' → two candidates with COORDINATED_PREDICATE."""
    sent = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Expect two claims: "Python supports generators" and "Python supports decorators"
    # The exact text may vary; we check count and reasons.
    assert len(candidates) == 2
    for cand in candidates:
        assert cand.boundary_reason == BoundaryReason.COORDINATED_PREDICATE
    # Verify text contains both parts (approximate)
    texts = [c.text for c in candidates]
    assert any("generators" in t for t in texts)
    assert any("decorators" in t for t in texts)


def test_coordinated_predicate_with_shared_subject_works(parser, detector):
    """Coordination of verbs sharing subject: 'Python runs and compiles quickly'."""
    sent = make_sentence("Python runs and compiles quickly.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Should produce two: "Python runs quickly" and "Python compiles quickly"
    assert len(candidates) == 2


# ── Independent clauses ──────────────────────────────────────────────────────

def test_independent_clauses_splits(parser, detector):
    """'X is fast and Y is slow' → two independent clause candidates."""
    sent = make_sentence("Python is fast and Java is slow.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 2
    assert all(c.boundary_reason == BoundaryReason.INDEPENDENT_CLAUSE for c in candidates)
    texts = [c.text for c in candidates]
    assert any("Python" in t for t in texts)
    assert any("Java" in t for t in texts)


# ── Complex cases – no split when not appropriate ───────────────────────────

def test_conditional_not_split(parser, detector):
    """Conditional 'if X then Y' should remain as one claim (split_conditionals=False)."""
    sent = make_sentence("If CUDA is installed, PyTorch uses the GPU.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # We expect one candidate (whole sentence) because we do not split conditionals.
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_relative_clause_not_split(parser, detector):
    """Relative clause should not be split; remains one claim."""
    sent = make_sentence("Python, which was released in 1991, supports generators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_empty_text(parser, detector):
    """Empty text -> parse_ok=False -> fallback with PARSE_FAILED."""
    sent = make_sentence("   ")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
    assert candidates[0].text == sent.text


def test_no_coordination_still_returns_one(parser, detector):
    """Sentence without coordinator yields single candidate."""
    sent = make_sentence("Deep learning is powerful.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_detector_never_returns_empty(parser, detector):
    """detect() must always return at least one candidate."""
    sent = make_sentence("This is a test.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) >= 1


# ── Configuration: split_conjunctions = False ──────────────────────────────

def test_split_disabled_returns_single(parser):
    """When split_conjunctions is False, no splitting occurs."""
    # We need to create a detector with split_conjunctions=False.
    # Since we can't easily override config, we'll patch or instantiate with custom config.
    # For simplicity, we assume the default config has split_conjunctions=True.
    # If you want to test, you can modify the config or use a custom BoundaryDetector.
    # We'll skip this test or demonstrate by setting attribute directly.
    detector_no_split = BoundaryDetector()
    # Set internal flag to False (hack for testing)
    detector_no_split._split_conjunctions = False
    sent = make_sentence("Python supports X and Y.")
    parsed = parser.parse(sent)
    candidates = detector_no_split.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION