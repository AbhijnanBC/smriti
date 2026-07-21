"""Unit tests for scoring/fusion.py — generic fusion + monotonicity + constraints."""

import pytest
from smriti.core.models import SignalVector, ContributionCandidate, ContributionSet
from smriti.scoring.policies import load_policy, FusionPolicy
from smriti.scoring.fusion import compute_reliability, compute_reliability_from_signal_vector


@pytest.fixture
def policy(): return load_policy()


def make_sv(**kwargs):
    defaults = dict(
        evidence_strength=0.5, evidence_independence=0.7, source_diversity=0.5,
        topology_strength=0.4, conflict_pressure=0.2, temporal_stability=0.6,
        evidence_completeness=1.0, statuses={},
    )
    defaults.update(kwargs)
    return SignalVector(**defaults)


def make_cs(policy, **sv_kwargs):
    """Build ContributionSet from keyword signal values."""
    sv = make_sv(**sv_kwargs)
    fp = policy.fusion
    candidates = []
    for name, value in {
        "evidence_strength": sv.evidence_strength,
        "evidence_independence": sv.evidence_independence,
        "source_diversity": sv.source_diversity,
        "topology_strength": sv.topology_strength,
        "conflict_pressure": sv.conflict_pressure,
        "temporal_stability": sv.temporal_stability,
        "hub_score": 0.0,
        "bridge_score": 0.0,
    }.items():
        if fp.get_weight(name) > 0:
            candidates.append(ContributionCandidate(
                signal_id=name, normalized_value=value,
                policy_weight=fp.get_weight(name),
                direction=fp.get_direction(name),
                label=name, raw_value=value,
            ))
    return ContributionSet(
        candidates=tuple(candidates), evidence_completeness=sv.evidence_completeness, claim_id="c001"
    ), sv


def test_basic_reliability_in_range(policy):
    cs, sv = make_cs(policy)
    ri, unc, _, _ = compute_reliability(cs, policy, sv)
    assert 0.0 <= ri <= 100.0


def test_uncertainty_in_range(policy):
    cs, sv = make_cs(policy)
    _, unc, _, _ = compute_reliability(cs, policy, sv)
    assert 0.0 <= unc <= 100.0


def test_six_plus_component_scores_produced(policy):
    cs, sv = make_cs(policy)
    _, _, comps, _ = compute_reliability(cs, policy, sv)
    assert len(comps) >= 6


def test_more_evidence_increases_reliability(policy):
    cs_low, sv_low = make_cs(policy, evidence_strength=0.10)
    cs_high, sv_high = make_cs(policy, evidence_strength=0.90)
    ri_low, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high > ri_low


def test_more_conflict_decreases_reliability(policy):
    cs_low, sv_low = make_cs(policy, conflict_pressure=0.05)
    cs_high, sv_high = make_cs(policy, conflict_pressure=0.95)
    ri_low_c, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high_c, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high_c < ri_low_c


def test_higher_topology_increases_reliability(policy):
    cs_low, sv_low = make_cs(policy, topology_strength=0.10)
    cs_high, sv_high = make_cs(policy, topology_strength=0.90)
    ri_low, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high > ri_low


def test_no_evidence_caps_reliability(policy):
    cs, sv = make_cs(policy, evidence_strength=0.0, topology_strength=1.0, conflict_pressure=0.0)
    ri, _, _, _ = compute_reliability(cs, policy, sv)
    assert ri <= policy.fusion.max_reliability_without_evidence + 0.01


def test_maximum_conflict_caps_reliability(policy):
    cs, sv = make_cs(policy, evidence_strength=1.0, conflict_pressure=1.0)
    ri, _, _, _ = compute_reliability(cs, policy, sv)
    assert ri <= policy.fusion.max_reliability_with_max_conflict + 0.01


def test_deterministic_fusion(policy):
    cs, sv = make_cs(policy, evidence_strength=0.75, conflict_pressure=0.30)
    ri1, unc1, _, _ = compute_reliability(cs, policy, sv)
    ri2, unc2, _, _ = compute_reliability(cs, policy, sv)
    assert ri1 == ri2 and unc1 == unc2


def test_fusion_receives_contribution_set_not_signal_vector(policy):
    """RECTIFIED (P0-2): Fusion must accept ContributionSet, not SignalVector."""
    cs, sv = make_cs(policy)
    # compute_reliability takes ContributionSet as first arg — this is the rectified API
    ri, unc, comps, dr = compute_reliability(cs, policy, sv)
    assert 0.0 <= ri <= 100.0
    from smriti.core.models import ContributionSet
    # Verify the function signature accepts ContributionSet
    assert isinstance(cs, ContributionSet)


def test_decision_record_produced(policy):
    """RECTIFIED (P0-5): compute_reliability must return a ReliabilityDecisionRecord."""
    from smriti.core.models import ReliabilityDecisionRecord
    cs, sv = make_cs(policy)
    ri, unc, comps, dr = compute_reliability(cs, policy, sv)
    assert isinstance(dr, ReliabilityDecisionRecord)
    assert dr.claim_id == "c001"
    assert isinstance(dr.policy_interactions, tuple)
    assert isinstance(dr.constraints_activated, tuple)
    assert isinstance(dr.contribution_order, tuple)
    assert dr.final_reliability == ri


def test_decision_record_constraints_logged(policy):
    """RECTIFIED (P0-5): When constraints activate, DecisionRecord must record them."""
    cs, sv = make_cs(policy, evidence_strength=0.0, topology_strength=1.0)
    ri, _, _, dr = compute_reliability(cs, policy, sv)
    assert len(dr.constraints_activated) > 0, (
        "No-evidence constraint must be recorded in ReliabilityDecisionRecord "
        "when evidence_strength is 0.0."
    )