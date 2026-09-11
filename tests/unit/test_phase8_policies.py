"""Unit tests for scoring/policies.py."""

import pytest
from smriti.core.models import SignalID
from smriti.scoring.policies import (
    FusionPolicy,
    PolicyError,
    PolicyProfile,
    load_policy,
)


def test_policy_loads_without_error():
    policy = load_policy()
    assert policy is not None
    assert policy.version is not None


def test_fusion_weights_sum_to_one():
    policy = load_policy()
    total = sum(policy.fusion.signal_weights.values())
    assert abs(total - 1.0) < 0.001


def test_invalid_weights_raise_policy_error():
    fp = FusionPolicy(
        signal_weights={
            "evidence_strength": 0.90,
            "evidence_independence": 0.15,
            "source_diversity": 0.15,
            "topology_strength": 0.10,
            "hub_score": 0.05,
            "bridge_score": 0.05,
            "conflict_pressure": 0.20,
            "temporal_stability": 0.05,
        },
        signal_directions={
            "evidence_strength": "positive",
            "evidence_independence": "positive",
            "source_diversity": "positive",
            "topology_strength": "positive",
            "hub_score": "positive",
            "bridge_score": "positive",
            "conflict_pressure": "negative",
            "temporal_stability": "positive",
        },
    )
    with pytest.raises(PolicyError):
        # active_registry_ids matches signal_weights' keys exactly (all 8
        # canonical signals), so this exercises the sum-to-1.0 check
        # specifically: 0.90 + 0.15 + 0.15 + 0.10 + 0.05 + 0.05 + 0.05 - 0.20 = 1.25 != 1.0
        fp.validate(set(SignalID))


def test_policy_config_hash_is_deterministic():
    policy = load_policy()
    h1 = policy.config_hash()
    h2 = policy.config_hash()
    assert h1 == h2 and len(h1) == 16


def test_policy_to_dict_serializable():
    import json

    policy = load_policy()
    d = policy.to_dict()
    json_str = json.dumps(d)
    assert len(json_str) > 0


def test_topology_policy_has_no_hub_bridge_bonus():
    """RECTIFIED (P0-3): TopologyPolicy must not have hub_bonus or bridge_bonus."""
    policy = load_policy()
    tp = policy.topology
    assert not hasattr(tp, "hub_bonus"), (
        "hub_bonus must not be in TopologyPolicy. "
        "Hub is now a separate signal (hub_score) in the registry."
    )
    assert not hasattr(tp, "bridge_bonus"), (
        "bridge_bonus must not be in TopologyPolicy. "
        "Bridge is now a separate signal (bridge_score) in the registry."
    )
    assert hasattr(tp, "centrality_scale")


def test_policy_profile_loads_correct_weights():
    """RECTIFIED (P1-3): PolicyProfile presets must produce different weights."""
    balanced = load_policy(PolicyProfile.BALANCED)
    research = load_policy(PolicyProfile.RESEARCH)
    # Research profile emphasizes independence and source diversity more
    assert (
        research.fusion.signal_weights.get("evidence_independence", 0)
        > balanced.fusion.signal_weights.get("evidence_independence", 0)
    ) or (
        research.fusion.signal_weights.get("source_diversity", 0)
        > balanced.fusion.signal_weights.get("source_diversity", 0)
    )


def test_fusion_policy_has_no_dead_topology_floor():
    """RECTIFIED (P0 external review — dead config sweep): FusionPolicy must
    not carry min_reliability_for_high_topology. No FusionConstraint ever
    read it, and reintroducing it as a reliability_index floor would
    reconflate reliability with importance (see P1-4 evidence/importance
    split). A topology-native constraint belongs in
    constraints.IMPORTANCE_CONSTRAINT_PIPELINE, not FusionPolicy, if one is
    ever justified.
    """
    policy = load_policy()
    assert not hasattr(policy.fusion, "min_reliability_for_high_topology")


def test_hub_bridge_have_separate_weights():
    """RECTIFIED (P0-3): hub_score and bridge_score must have weights in fusion."""
    policy = load_policy()
    weights = policy.fusion.signal_weights
    assert "hub_score" in weights, "hub_score must be a registered weight in fusion policy"
    assert "bridge_score" in weights, "bridge_score must be a registered weight in fusion policy"
    assert weights["hub_score"] > 0
    assert weights["bridge_score"] > 0
