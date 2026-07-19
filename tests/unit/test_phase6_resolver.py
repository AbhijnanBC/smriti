"""Unit tests for classification/resolver.py."""

import pytest
from smriti.core.models import (
    CandidatePair, RelationshipEvidence, RelationshipType,
    RelationshipDirection, NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy


def make_evidence(contradiction: float, entailment: float, neutral: float, cosine: float = 0.82):
    pair = CandidatePair(claim_id_a="c001", claim_id_b="c002", cosine_similarity=cosine, candidate_rank=1)
    scores = [contradiction, entailment, neutral]
    predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
    raw_confidence = max(scores)
    nli_scores = NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label=predicted,
        raw_confidence=raw_confidence,
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=cosine,
        nli_scores=nli_scores,
        calibrated_confidence=raw_confidence,
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


@pytest.fixture
def policy():
    return ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
    )


@pytest.fixture
def resolver(policy):
    return RelationshipResolver(policy=policy)


def test_strong_contradiction_resolves_contradicts(resolver):
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.CONTRADICTS


def test_strong_entailment_resolves_supports(resolver):
    evidence = make_evidence(contradiction=0.03, entailment=0.93, neutral=0.04)
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS


def test_weak_contradiction_high_cosine_resolves_refines(resolver):
    evidence = make_evidence(contradiction=0.60, entailment=0.20, neutral=0.20, cosine=0.90)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.REFINES


def test_high_neutral_resolves_neutral(resolver):
    evidence = make_evidence(contradiction=0.15, entailment=0.20, neutral=0.65)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.NEUTRAL


def test_low_confidence_resolves_unknown(resolver):
    evidence = make_evidence(contradiction=0.35, entailment=0.33, neutral=0.32)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.UNKNOWN


def test_resolver_is_deterministic(resolver):
    evidence = make_evidence(contradiction=0.88, entailment=0.08, neutral=0.04)
    assert resolver.resolve(evidence) == resolver.resolve(evidence) == resolver.resolve(evidence)


def test_contradicts_is_symmetric(resolver):
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    _, direction = resolver.resolve(evidence)
    assert direction == RelationshipDirection.SYMMETRIC


def test_supports_is_directional(resolver):
    evidence = make_evidence(contradiction=0.03, entailment=0.93, neutral=0.04)
    _, direction = resolver.resolve(evidence)
    assert direction == RelationshipDirection.A_TO_B


def test_resolver_policy_is_configurable():
    """RECTIFIED: resolver must use policy, not hard-coded values."""
    # Custom policy with much higher threshold
    strict_policy = ResolverPolicy(
        nli_threshold=0.99,
        refine_threshold=0.90,
        high_sim_threshold=0.99,
        neutrality_threshold=0.99,
    )
    strict_resolver = RelationshipResolver(policy=strict_policy)
    # 0.92 contradiction won't exceed 0.99 threshold
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    rel_type, _ = strict_resolver.resolve(evidence)
    assert rel_type == RelationshipType.UNKNOWN


def test_resolver_policy_validates_on_construction():
    """RECTIFIED: invalid policy must raise ResolverPolicyError."""
    from smriti.exceptions import ResolverPolicyError
    with pytest.raises(ResolverPolicyError):
        ResolverPolicy(
            nli_threshold=0.80,
            refine_threshold=0.90,   # Violation: refine_threshold >= nli_threshold
            high_sim_threshold=0.88,
            neutrality_threshold=0.60,
        )


def test_resolver_contradiction_margin_enforced():
    """RECTIFIED: contradiction_margin must widen the gap requirement."""
    policy_with_margin = ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
        contradiction_margin=0.20,   # C must exceed E by 0.20
    )
    resolver = RelationshipResolver(policy=policy_with_margin)
    # C=0.85, E=0.10 → gap=0.75 > 0.20 → CONTRADICTS
    evidence_pass = make_evidence(contradiction=0.85, entailment=0.10, neutral=0.05)
    rel_type, _ = resolver.resolve(evidence_pass)
    assert rel_type == RelationshipType.CONTRADICTS

    # C=0.82, E=0.75 → gap=0.07 < 0.20 → not CONTRADICTS
    evidence_fail = make_evidence(contradiction=0.82, entailment=0.75, neutral=0.03)
    rel_type, _ = resolver.resolve(evidence_fail)
    assert rel_type != RelationshipType.CONTRADICTS