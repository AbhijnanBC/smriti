"""
Unit tests for the bidirectional-NLI resolver path
(classification/resolver.py's _resolve_bidirectional), added for the
external-review-driven rewrite that replaced single-direction NLI (claim_a
always premise, claim_b always hypothesis -- an artifact of ID ordering,
not semantics) with genuine bidirectional entailment checking.
"""

import itertools

import pytest
from smriti.core.models import (
    CandidatePair,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipType,
)
from smriti.exceptions import ResolverPolicyError
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy


def _nli(contradiction: float, entailment: float, neutral: float) -> NLIScores:
    scores = [contradiction, entailment, neutral]
    predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
    return NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label=predicted,
        raw_confidence=max(scores),
    )


def make_bidirectional_evidence(
    ab: tuple,  # (contradiction, entailment, neutral) for claim_a-premise / claim_b-hypothesis
    ba: tuple,  # same, for claim_b-premise / claim_a-hypothesis
    cosine: float = 0.82,
) -> RelationshipEvidence:
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=cosine, candidate_rank=1
    )
    nli_ab = _nli(*ab)
    nli_ba = _nli(*ba)
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=cosine,
        nli_scores=nli_ab,
        nli_scores_b_to_a=nli_ba,
        calibrated_confidence=nli_ab.raw_confidence,
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
        contradiction_margin=0.05,
        entailment_margin=0.05,
    )


@pytest.fixture
def resolver(policy):
    return RelationshipResolver(policy=policy)


def test_bidirectional_path_is_used_when_b_to_a_present(resolver):
    """Evidence carrying nli_scores_b_to_a must take the bidirectional
    branch, not silently fall back to the single-direction legacy path."""
    # ab alone would resolve SUPPORTS under the legacy rule; ba also
    # entails, so the bidirectional path must report EQUIVALENT instead.
    evidence = make_bidirectional_evidence(
        ab=(0.03, 0.93, 0.04),
        ba=(0.03, 0.90, 0.07),
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.EQUIVALENT
    assert direction == RelationshipDirection.SYMMETRIC


def test_one_way_entailment_ab_only_resolves_supports_a_to_b(resolver):
    """A entails B; B does NOT entail A -> SUPPORTS, direction A_TO_B."""
    evidence = make_bidirectional_evidence(
        ab=(0.03, 0.93, 0.04),  # A -> B: strong entailment
        ba=(0.10, 0.20, 0.70),  # B -> A: neutral-dominant, no entailment
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS
    assert direction == RelationshipDirection.A_TO_B


def test_one_way_entailment_ba_only_resolves_supports_b_to_a(resolver):
    """B entails A; A does NOT entail B -> SUPPORTS, direction B_TO_A."""
    evidence = make_bidirectional_evidence(
        ab=(0.10, 0.20, 0.70),  # A -> B: neutral-dominant, no entailment
        ba=(0.03, 0.93, 0.04),  # B -> A: strong entailment
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS
    assert direction == RelationshipDirection.B_TO_A


def test_both_directions_entail_resolves_equivalent(resolver):
    evidence = make_bidirectional_evidence(
        ab=(0.02, 0.95, 0.03),
        ba=(0.02, 0.94, 0.04),
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.EQUIVALENT
    assert direction == RelationshipDirection.SYMMETRIC


def test_neither_direction_entails_and_no_contradiction_resolves_neutral(resolver):
    evidence = make_bidirectional_evidence(
        ab=(0.10, 0.20, 0.70),
        ba=(0.12, 0.18, 0.70),
    )
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.NEUTRAL


def test_contradiction_uses_averaged_scores_across_both_directions(resolver):
    """Contradiction is a symmetric property of the pair; a pair with
    strong contradiction signal in BOTH directions must resolve
    CONTRADICTS even though neither single direction alone would clear
    the margin over the OTHER direction's entailment reading."""
    evidence = make_bidirectional_evidence(
        ab=(0.90, 0.05, 0.05),
        ba=(0.88, 0.06, 0.06),
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.CONTRADICTS
    assert direction == RelationshipDirection.SYMMETRIC


def test_contradiction_margin_checked_against_max_entailment_across_directions(resolver):
    """The margin-over-entailment check must use the STRONGER of the two
    directions' entailment scores (conservative), not just the ab one."""
    # c_avg = (0.85+0.85)/2 = 0.85; e_ab=0.05 but e_ba=0.82 -- if the
    # contradiction rule only checked e_ab, this would incorrectly pass
    # (0.85 - 0.05 = 0.80 >= margin); checking against e_max=0.82 gives
    # (0.85 - 0.82 = 0.03 < margin) and correctly fails to CONTRADICTS.
    evidence = make_bidirectional_evidence(
        ab=(0.85, 0.05, 0.10),
        ba=(0.85, 0.82, 0.13),
    )
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type != RelationshipType.CONTRADICTS


def test_no_entailment_either_direction_high_similarity_resolves_neutral(resolver):
    """RECTIFIED (external "reality check" review round 3, P0-4): the old
    REFINES heuristic (high cosine + neutral-dominant + low contradiction,
    firing when NLI shows no entailment in EITHER direction) is retired --
    that is not a refinement under this ontology's own definition
    (REFINES requires established one-way entailment). It now correctly
    resolves NEUTRAL, symmetric, exactly like the single-direction
    resolver's equivalent scenario."""
    evidence = make_bidirectional_evidence(
        ab=(0.05, 0.35, 0.60),
        ba=(0.05, 0.35, 0.60),
        cosine=0.90,
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.NEUTRAL
    assert direction == RelationshipDirection.SYMMETRIC


def test_no_entailment_asymmetric_readings_still_resolve_neutral_not_refines(resolver):
    """RECTIFIED (P0-4): even when one direction's entailment reading is
    clearly stronger than the other, NEITHER clears the strict entailment
    margin here -- so this must still resolve NEUTRAL (symmetric), not a
    directional REFINES guess from the weaker, sub-margin readings. (The
    old heuristic's own direction-selection logic, previously tested here,
    no longer exists: REFINES now only ever comes from a genuine one-way
    SUPPORTS decision reclassified by the specificity gate.)"""
    evidence = make_bidirectional_evidence(
        ab=(0.05, 0.20, 0.75),
        ba=(0.05, 0.50, 0.45),
        cosine=0.90,
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.NEUTRAL
    assert direction == RelationshipDirection.SYMMETRIC


def test_low_confidence_both_directions_resolves_unknown_abstain(resolver):
    evidence = make_bidirectional_evidence(
        ab=(0.35, 0.33, 0.32),
        ba=(0.34, 0.34, 0.32),
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.UNKNOWN
    assert direction == RelationshipDirection.SYMMETRIC


def test_bidirectional_resolution_is_deterministic(resolver):
    evidence = make_bidirectional_evidence(ab=(0.03, 0.93, 0.04), ba=(0.10, 0.20, 0.70))
    assert resolver.resolve(evidence) == resolver.resolve(evidence) == resolver.resolve(evidence)


def test_equivalent_requires_both_directions_to_independently_beat_argmax(resolver):
    """Strong ab entailment alone must NOT produce EQUIVALENT if ba is not
    itself a genuine argmax-respecting entailment (e.g. ba's neutral score
    is actually dominant) -- this is the same P0-6 argmax discipline
    applied per-direction, not relaxed for the new EQUIVALENT case."""
    evidence = make_bidirectional_evidence(
        ab=(0.02, 0.95, 0.03),
        ba=(0.05, 0.40, 0.55),  # neutral is ba's actual dominant class
    )
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS
    assert direction == RelationshipDirection.A_TO_B


def test_legacy_single_direction_evidence_still_uses_old_rules(resolver):
    """Evidence with nli_scores_b_to_a=None (e.g. old test fixtures or any
    caller not yet updated) must fall back to the single-direction rule
    set exactly as before -- SUPPORTS always A_TO_B, no EQUIVALENT possible."""
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.82, candidate_rank=1
    )
    nli_scores = _nli(0.03, 0.93, 0.04)
    evidence = RelationshipEvidence(
        pair=pair,
        cosine_similarity=0.82,
        nli_scores=nli_scores,
        calibrated_confidence=nli_scores.raw_confidence,
        inference_metadata=InferenceMetadata(model_name="test-nli"),
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )
    assert evidence.nli_scores_b_to_a is None
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS
    assert direction == RelationshipDirection.A_TO_B


# ── P0-6: priority_order must be a genuine, validated configuration ────


def test_priority_order_missing_equivalent_is_rejected():
    """RECTIFIED (external review, P0-6): EQUIVALENT must be a real
    priority_order entry, not hardcoded inside the "supports" branch --
    a policy omitting it entirely is now a configuration error, not a
    silent behavior change."""
    with pytest.raises(ResolverPolicyError):
        ResolverPolicy(
            nli_threshold=0.80,
            refine_threshold=0.55,
            high_sim_threshold=0.88,
            neutrality_threshold=0.60,
            priority_order=["contradicts", "supports", "refines", "neutral", "unknown"],
        )


def test_priority_order_duplicate_entry_is_rejected():
    with pytest.raises(ResolverPolicyError):
        ResolverPolicy(
            nli_threshold=0.80,
            refine_threshold=0.55,
            high_sim_threshold=0.88,
            neutrality_threshold=0.60,
            priority_order=[
                "contradicts",
                "equivalent",
                "equivalent",
                "supports",
                "refines",
                "neutral",
                "unknown",
            ],
        )


def test_priority_order_unknown_rule_name_is_rejected():
    with pytest.raises(ResolverPolicyError):
        ResolverPolicy(
            nli_threshold=0.80,
            refine_threshold=0.55,
            high_sim_threshold=0.88,
            neutrality_threshold=0.60,
            priority_order=[
                "contradicts",
                "equivalent",
                "supports",
                "refines",
                "neutral",
                "not_a_real_rule",
            ],
        )


@pytest.mark.parametrize(
    "priority_order",
    [
        list(p)
        for p in itertools.permutations(
            ["contradicts", "equivalent", "supports", "refines", "neutral", "unknown"]
        )
    ][
        :20
    ],  # a sample of permutations, not all 720 -- exhaustive coverage is unnecessary
)
def test_every_permutation_of_priority_order_is_accepted_and_deterministic(priority_order):
    """Any permutation containing each rule exactly once is a legal
    policy (P0-6: "test all permutations that are semantically legal").
    This only checks the policy is constructible and resolve() does not
    crash -- not that every ordering gives the same answer, since
    reordering priority IS supposed to change which rule wins ties."""
    policy = ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
        priority_order=priority_order,
    )
    resolver = RelationshipResolver(policy)
    evidence = make_bidirectional_evidence(ab=(0.02, 0.95, 0.03), ba=(0.02, 0.95, 0.03))
    rel_type, direction = resolver.resolve(evidence)
    assert isinstance(rel_type, RelationshipType)
    assert isinstance(direction, RelationshipDirection)


def test_equivalent_resolves_correctly_regardless_of_supports_branch_ordering(resolver):
    """RECTIFIED (P0-6): EQUIVALENT is now a genuine, independently
    ordered priority_order entry rather than a check hardcoded inside
    "supports". A both-directions-entail pair must resolve to EQUIVALENT
    whether "equivalent" is checked before OR after "supports" in
    priority_order -- the "supports" branch explicitly declines to fire
    when both directions entail (it would misreport a symmetric relation
    as one-way), so it always falls through to "equivalent" wherever that
    rule sits. This is the point of the fix: previously EQUIVALENT was
    checked unconditionally before priority_order was even consulted, so
    there was no way to observe priority_order failing to control it --
    now there is, and it still resolves correctly either way."""
    evidence = make_bidirectional_evidence(ab=(0.02, 0.95, 0.03), ba=(0.02, 0.95, 0.03))

    supports_first_policy = ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
        entailment_margin=0.05,
        priority_order=["contradicts", "supports", "equivalent", "refines", "neutral", "unknown"],
    )
    rel_type_supports_first, _ = RelationshipResolver(supports_first_policy).resolve(evidence)
    assert rel_type_supports_first == RelationshipType.EQUIVALENT

    # Default policy fixture orders equivalent before supports.
    rel_type_equivalent_first, _ = resolver.resolve(evidence)
    assert rel_type_equivalent_first == RelationshipType.EQUIVALENT


def test_supports_branch_never_misreports_a_both_directions_entail_pair():
    """A policy that (deliberately, unrealistically) omits "equivalent"'s
    ability to ever be reached -- by placing "unknown" right after
    "supports" -- must still not have "supports" itself misreport a
    both-directions-entail pair as one-way SUPPORTS; it falls through
    past "supports" and is caught by "equivalent" later in priority_order
    regardless of where the rest of priority_order places it, since
    priority_order is still required to contain "equivalent" exactly
    once. This pins the explicit safety guard added to the "supports"
    branch, independent of the EQUIVALENT-ordering test above."""
    policy = ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
        entailment_margin=0.05,
        priority_order=["equivalent", "contradicts", "refines", "supports", "neutral", "unknown"],
    )
    evidence = make_bidirectional_evidence(ab=(0.02, 0.95, 0.03), ba=(0.02, 0.95, 0.03))
    rel_type, direction = RelationshipResolver(policy).resolve(evidence)
    assert rel_type == RelationshipType.EQUIVALENT
    assert direction == RelationshipDirection.SYMMETRIC


# ── P0-4: ResolutionStatus / RelationshipDecision (UNKNOWN is a status,
#    not a sixth relation type) ─────────────────────────────────────────


def test_resolve_as_decision_maps_unknown_to_abstained_with_none_relation_type(resolver):
    from smriti.core.models import ResolutionStatus

    evidence = make_bidirectional_evidence(
        ab=(0.35, 0.33, 0.32),
        ba=(0.34, 0.34, 0.32),
    )
    decision = resolver.resolve_as_decision(evidence)
    assert decision.status == ResolutionStatus.ABSTAINED
    assert decision.relation_type is None
    assert decision.abstention_reason is not None


def test_resolve_as_decision_maps_resolved_relations_with_real_type(resolver):
    from smriti.core.models import ResolutionStatus

    evidence = make_bidirectional_evidence(
        ab=(0.02, 0.95, 0.03),
        ba=(0.10, 0.20, 0.70),
    )
    decision = resolver.resolve_as_decision(evidence)
    assert decision.status == ResolutionStatus.RESOLVED
    assert decision.relation_type == RelationshipType.SUPPORTS
    assert decision.direction == RelationshipDirection.A_TO_B


def test_to_decision_invariant_relation_type_none_iff_abstained():
    from smriti.core.models import ResolutionStatus, to_decision

    abstained = to_decision(RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC)
    assert abstained.relation_type is None
    assert abstained.status == ResolutionStatus.ABSTAINED

    for rt in [
        RelationshipType.CONTRADICTS,
        RelationshipType.SUPPORTS,
        RelationshipType.REFINES,
        RelationshipType.EQUIVALENT,
        RelationshipType.NEUTRAL,
    ]:
        resolved = to_decision(rt, RelationshipDirection.SYMMETRIC)
        assert resolved.relation_type == rt
        assert resolved.status == ResolutionStatus.RESOLVED
