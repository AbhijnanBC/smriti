"""
Unit tests for classification/validator.py's direction-invariant checking,
focused on the EQUIVALENT addition (bidirectional-NLI rewrite).
"""

from smriti.core.models import (
    CandidatePair,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipType,
)
from smriti.retrieval.classification.validator import (
    RelRejectionReason,
    validate_relationship,
)


def make_evidence(
    entailment=0.02, contradiction=0.02, neutral=0.96, confidence=0.90
) -> RelationshipEvidence:
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.85, candidate_rank=1
    )
    nli_scores = NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label="neutral",
        raw_confidence=confidence,
    )
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=0.85,
        nli_scores=nli_scores,
        calibrated_confidence=confidence,
        inference_metadata=InferenceMetadata(model_name="test-nli"),
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


def test_equivalent_with_symmetric_direction_is_valid():
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.EQUIVALENT,
        RelationshipDirection.SYMMETRIC,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
    )
    assert result.is_valid


def test_equivalent_with_a_to_b_direction_is_invalid():
    """EQUIVALENT must always be SYMMETRIC -- a resolver bug that emitted
    it with a directional tag must be caught, not silently accepted."""
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.EQUIVALENT,
        RelationshipDirection.A_TO_B,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
    )
    assert not result.is_valid
    assert result.rejection_reason == RelRejectionReason.DIRECTION_INVARIANT


def test_supports_with_b_to_a_direction_is_valid():
    """RECTIFIED (bidirectional-NLI rewrite): SUPPORTS must accept BOTH
    A_TO_B and B_TO_A now that direction reflects genuine NLI evidence
    rather than being hardcoded A_TO_B."""
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.SUPPORTS,
        RelationshipDirection.B_TO_A,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
    )
    assert result.is_valid


# ── skip_neutral (external review, P0-7-class defect: this config key
#    was documented but never actually consumed anywhere) ─────────────


def test_neutral_relationship_rejected_when_skip_neutral_true():
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.NEUTRAL,
        RelationshipDirection.SYMMETRIC,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
        skip_neutral=True,
    )
    assert not result.is_valid
    assert result.rejection_reason == RelRejectionReason.NEUTRAL_RELATIONSHIP


def test_neutral_relationship_accepted_when_skip_neutral_false():
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.NEUTRAL,
        RelationshipDirection.SYMMETRIC,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
        skip_neutral=False,
    )
    assert result.is_valid


def test_skip_neutral_defaults_to_false_for_backward_compatibility():
    """RECTIFIED: skip_neutral must default to False (i.e. NOT skip) at
    this function's own signature level, matching the behavior every
    caller silently had before this fix existed -- callers that want
    skip_neutral_relationships:true from config must pass it explicitly
    (retrieval/__init__.py does); this default only protects any other
    caller that has not been updated to pass it."""
    evidence = make_evidence()
    result = validate_relationship(
        evidence,
        RelationshipType.NEUTRAL,
        RelationshipDirection.SYMMETRIC,
        min_confidence=0.5,
        nli_threshold=0.80,
        skip_unknown=True,
    )
    assert result.is_valid
