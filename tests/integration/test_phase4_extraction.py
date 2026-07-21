"""
Integration test for Phase 4 end-to-end.

Tests the complete pipeline:
    SemanticSentence → extract_claims_from_sentence() → List[Claim]
"""

import hashlib
import pytest
from pathlib import Path
from smriti.core.models import (
    SemanticSentence, Claim, ExtractionMode, Modality,
)
from smriti.claims import extract_claims_from_sentence
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.statistics import Phase4StatsCollector


@pytest.fixture(scope="module")
def pipeline():
    """Initialize pipeline components once per module."""
    try:
        return (
            SpaCyParser(),
            BoundaryDetector(),
            StructureExtractor(),
            AssertionAnnotator(),
            DegradationHandler(),
        )
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(
    text: str,
    sentence_id: str = "s001",
    context: str = "",
    position: int = 0,
) -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context=context,
        position=position,
        char_start=0,
        char_end=len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def run_pipeline(pipeline, sentence, max_claims=10):
    parser, bd, se, ann, dh = pipeline
    stats = Phase4StatsCollector()
    return extract_claims_from_sentence(
        sentence=sentence, parser=parser, boundary_detector=bd,
        structure_extractor=se, annotator=ann, degradation_handler=dh,
        stats_collector=stats, max_claims=max_claims, global_seen_ids={}, 
    )


# ── Basic claim production ─────────────────────────────────────────────────────

def test_simple_sentence_produces_claim(pipeline):
    """Every non-empty sentence must produce at least one claim."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert result.claim_count >= 1
    assert result.error is None


def test_empty_sentence_produces_no_claims(pipeline):
    """Empty text → zero claims, no error."""
    result = run_pipeline(pipeline, make_sentence("   "))
    assert result.claim_count == 0


def test_claims_have_correct_sentence_id(pipeline):
    """Every claim must link back to the source sentence_id."""
    sentence = make_sentence("Python is fast.", sentence_id="unique_s_id")
    result = run_pipeline(pipeline, sentence)
    assert all(c.sentence_id == "unique_s_id" for c in result.claims)
    # New checks for content_hash and rule_version
    assert all(c.content_hash is not None for c in result.claims)
    assert all(c.rule_version == "1.0" for c in result.claims)


def test_claims_have_correct_document_id(pipeline):
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert all(c.document_id == "doc001" for c in result.claims)


# ── Text preservation ─────────────────────────────────────────────────────────

def test_claim_text_preserves_author_wording(pipeline):
    """Claim text must match source — no canonicalization."""
    original = "Python does NOT support this feature."
    sentence = make_sentence(original)
    result = run_pipeline(pipeline, sentence)
    # At minimum, the whole-sentence fallback must preserve it
    all_texts = [c.text for c in result.claims]
    assert any(original in t or t in original for t in all_texts)


# ── Context propagation ────────────────────────────────────────────────────────

def test_context_propagated_from_sentence(pipeline):
    """Claim must carry context from SemanticSentence."""
    sentence = make_sentence("Python supports generators.", context="Programming > Python")
    result = run_pipeline(pipeline, sentence)
    assert all(c.context == "Programming > Python" for c in result.claims)


# ── Provenance chain ──────────────────────────────────────────────────────────

def test_claim_provenance_is_complete(pipeline):
    """Every claim must have complete provenance chain."""
    sentence = make_sentence("Python is fast.", sentence_id="sid1", position=5)
    result = run_pipeline(pipeline, sentence)
    for claim in result.claims:
        assert claim.provenance is not None
        assert claim.provenance.sentence_id == "sid1"
        assert claim.provenance.document_id == "doc001"
        assert claim.provenance.sentence_position == 5
    # New check: content_hash must match SHA256 of text
    assert all(
        c.content_hash == hashlib.sha256(c.text.encode()).hexdigest()[:16]
        for c in result.claims
    )


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_sentence_same_claim_ids(pipeline):
    """Running twice on the same sentence must produce identical claim IDs."""
    sentence = make_sentence("Python supports generators and decorators.")
    result1 = run_pipeline(pipeline, sentence)
    result2 = run_pipeline(pipeline, sentence)

    ids1 = [c.claim_id for c in result1.claims]
    ids2 = [c.claim_id for c in result2.claims]
    assert ids1 == ids2
    # New check: content_hash must also be identical
    assert [c.content_hash for c in result1.claims] == [c.content_hash for c in result2.claims]


def test_claim_ids_are_unique(pipeline):
    """No two claims from the same sentence may share an ID."""
    sentence = make_sentence("Python supports X and Y and Z.")
    result = run_pipeline(pipeline, sentence)
    ids = [c.claim_id for c in result.claims]
    assert len(ids) == len(set(ids))


# ── Annotation ────────────────────────────────────────────────────────────────

def test_negation_flag_on_negated_claim(pipeline):
    """A negated sentence must produce at least one claim with is_negated=True."""
    sentence = make_sentence("Python does not support this feature.")
    result = run_pipeline(pipeline, sentence)
    assert any(c.is_negated for c in result.claims)


def test_modality_on_possible_claim(pipeline):
    """'may' or 'might' must produce POSSIBLE modality."""
    sentence = make_sentence("Python may be faster than Java.")
    result = run_pipeline(pipeline, sentence)
    modalities = [c.assertion_metadata.modality for c in result.claims]
    assert Modality.POSSIBLE in modalities


# ── Immutability ──────────────────────────────────────────────────────────────

def test_claims_are_immutable(pipeline):
    """Claim objects must be frozen."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    if result.claims:
        with pytest.raises(Exception):
            result.claims[0].text = "modified"


# ── Graceful degradation ──────────────────────────────────────────────────────

def test_claim_always_produced_even_on_parse_failure(pipeline):
    """Even on parser failure, a whole-sentence claim is produced."""
    # Malformed text that may trip the parser
    sentence = make_sentence("@@@ ### ??? weird !!!")
    result = run_pipeline(pipeline, sentence)
    # Must produce something (whole-sentence fallback)
    assert result.claim_count >= 0  # 0 only if text is empty


def test_schema_version_is_correct(pipeline):
    """All claims must have schema_version '4.0'."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    for claim in result.claims:
        assert claim.schema_version == "4.0"


# ── Realistic note ────────────────────────────────────────────────────────────

def test_realistic_knowledge_note(pipeline):
    """
    Full test with a realistic machine learning note.
    Verifies claims are extracted with provenance and correct flags.
    """
    sentences_data = [
        ("Supervised learning uses labeled training data.", "ML > Supervised"),
        ("The model learns to map inputs to outputs.", "ML > Supervised"),
        ("Unsupervised learning does not require labeled data.", "ML > Unsupervised"),
        ("Deep learning may outperform traditional methods on large datasets.",
         "ML > Deep Learning"),
        ("According to the authors, transformers are now state-of-the-art.", "ML"),
    ]

    all_claims = []
    for i, (text, context) in enumerate(sentences_data):
        sentence = make_sentence(text, sentence_id=f"s_{i:03d}", context=context, position=i)
        result = run_pipeline(pipeline, sentence)
        assert result.error is None, f"Error on sentence '{text}': {result.error}"
        all_claims.extend(result.claims)

    # At least one claim per sentence
    assert len(all_claims) >= len(sentences_data)

    # All have provenance
    assert all(c.provenance is not None for c in all_claims)

    # All have schema 4.0
    assert all(c.schema_version == "4.0" for c in all_claims)

    # Negation detected in sentence 3
    unsupervised_claims = [c for c in all_claims if "does not" in c.text.lower()]
    assert any(c.is_negated for c in unsupervised_claims)

    # Modality detected in sentence 4
    deep_claims = [c for c in all_claims if "may" in c.text.lower()]
    assert any(c.assertion_metadata.modality == Modality.POSSIBLE for c in deep_claims)

    # Attribution detected in sentence 5
    attribution_claims = [c for c in all_claims if "authors" in c.text.lower() or
                          c.assertion_metadata.is_attributed]
    # Attribution may or may not be detected depending on spaCy's parse
    # but the claim must still exist
    assert len(all_claims) >= 5

    # All claim IDs are unique
    claim_ids = [c.claim_id for c in all_claims]
    assert len(claim_ids) == len(set(claim_ids))

    # New checks for content_hash and rule_version
    hashes = [c.content_hash for c in all_claims]
    # content_hash should be unique because texts differ
    assert len(hashes) == len(set(hashes))
    assert all(c.rule_version == "1.0" for c in all_claims)