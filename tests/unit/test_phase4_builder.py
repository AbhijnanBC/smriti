"""
Unit tests for claims/builder.py.
"""

import pytest
from pathlib import Path

from smriti.core.models import (
    SemanticSentence,
    ExtractionMode,
    Modality,
    StructuredAssertion,
    Claim,
    BoundaryReason,
)
from smriti.claims.builder import build_claim, _compute_claim_id
from smriti.claims.rules import RULE_VERSION


def make_validated(text: str, sentence_id: str = "sent001", doc_id: str = "doc001"):
    """Create a minimal ValidatedAssertion for testing."""
    from smriti.claims.models import (
        ValidatedAssertion,
        AnnotatedAssertion,
        StructuredAssertionCandidate,
        AssertionCandidate,
        ParsedSentence,
        LinguisticMetadata,
        SemanticMetadata,
    )
    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=doc_id,
        text=text,
        context="Python > Generators",
        position=3,
        char_start=100,
        char_end=100 + len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason=BoundaryReason.SINGLE_ASSERTION,
    )
    structured_cand = StructuredAssertionCandidate(
        candidate=candidate,
        structured_assertion=None,
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
    )

    # Split metadata
    linguistic = LinguisticMetadata(
        is_negated=False,
        modality=Modality.CERTAIN,
        is_quoted=False,
    )
    semantic = SemanticMetadata(
        is_conditional=False,
        is_comparative=False,
        is_attributed=False,
        attributed_to=None,
    )

    annotated = AnnotatedAssertion(
        structured_candidate=structured_cand,
        linguistic_metadata=linguistic,
        semantic_metadata=semantic,
        additional_warnings=[],
    )

    return ValidatedAssertion(annotated=annotated, all_warnings=[])


def test_build_returns_claim():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert isinstance(claim, Claim)
    assert claim.content_hash is not None
    assert len(claim.content_hash) == 16
    assert claim.rule_version == RULE_VERSION
    assert claim.rule_version == "1.0"


def test_claim_id_is_16_chars():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert len(claim.claim_id) == 16


def test_claim_id_is_deterministic():
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s1")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id == claim2.claim_id
    assert claim1.content_hash == claim2.content_hash


def test_different_text_different_id():
    v1 = make_validated("Python is great.")
    v2 = make_validated("Julia is faster.")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id != claim2.claim_id
    assert claim1.content_hash != claim2.content_hash


def test_claim_text_is_exact():
    """Text must be author's exact wording — no modification."""
    text = "Python does NOT support this feature."
    v = make_validated(text)
    claim = build_claim(v)
    assert claim.text == text


def test_claim_is_frozen():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    with pytest.raises(Exception):
        claim.text = "modified"


def test_claim_has_provenance():
    v = make_validated("Python is fast.", sentence_id="sent_x", doc_id="doc_y")
    claim = build_claim(v)
    assert claim.provenance is not None
    assert claim.provenance.sentence_id == "sent_x"
    assert claim.provenance.document_id == "doc_y"


def test_claim_schema_version():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    assert claim.schema_version == "4.0"


def test_claim_context_from_sentence():
    """Claim must inherit context from source SemanticSentence."""
    v = make_validated("Python supports generators.", sentence_id="s1")
    claim = build_claim(v)
    assert claim.context == "Python > Generators"


# ── New test: content_hash depends only on text ──────────────────────────────

def test_content_hash_depends_only_on_text():
    """content_hash must be identical for identical text, regardless of sentence_id."""
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s2")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.content_hash == claim2.content_hash
    # claim_id includes sentence_id, so it should differ
    assert claim1.claim_id != claim2.claim_id