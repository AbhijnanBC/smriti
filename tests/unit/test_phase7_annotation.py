"""Unit tests for evolution/annotation.py."""

import pytest
from smriti.core.models import SemanticRole, TopologyMetrics
from smriti.evolution.annotation import _classify_role, AnnotationPolicy
from smriti.exceptions import AnnotationPolicyError


def make_topology(degree, in_degree, out_degree, centrality, is_bridge=False, is_hub=False):
    return TopologyMetrics(
        degree=degree, in_degree=in_degree, out_degree=out_degree,
        is_bridge=is_bridge, is_hub=is_hub,
        partition_id="p001", centrality=centrality,
    )


DEFAULT_POLICY = AnnotationPolicy()


def test_foundational_claim_annotation():
    topo = make_topology(5, 3, 2, centrality=0.75)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.FOUNDATIONAL_CLAIM


def test_bridge_claim_annotation():
    topo = make_topology(1, 1, 0, centrality=0.10, is_bridge=True)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.BRIDGE_CLAIM


def test_evidence_hub_annotation():
    topo = make_topology(5, 4, 1, centrality=0.40)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.EVIDENCE_HUB


def test_refinement_root_annotation():
    topo = make_topology(4, 1, 3, centrality=0.20)
    assert _classify_role(topo, 3, DEFAULT_POLICY) == SemanticRole.REFINEMENT_ROOT


def test_leaf_claim_annotation():
    topo = make_topology(2, 2, 0, centrality=0.30)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.LEAF_CLAIM


def test_peripheral_claim_annotation():
    topo = make_topology(1, 0, 1, centrality=0.05)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.PERIPHERAL_CLAIM


def test_annotation_policy_thresholds_respected():
    """RECTIFIED (P1-4): Annotation thresholds must come from policy, not hardcode."""
    strict_policy = AnnotationPolicy(
        foundational_centrality_threshold=0.90,  # Very strict
        foundational_min_in_degree=5,
    )
    # centrality=0.75, in_degree=3 — would be FOUNDATIONAL with default but not with strict
    topo = make_topology(5, 3, 2, centrality=0.75)
    role_default = _classify_role(topo, 0, DEFAULT_POLICY)
    role_strict = _classify_role(topo, 0, strict_policy)
    assert role_default == SemanticRole.FOUNDATIONAL_CLAIM
    assert role_strict != SemanticRole.FOUNDATIONAL_CLAIM


def test_annotation_policy_validates_on_construction():
    """RECTIFIED (P1-4): Invalid policy must raise AnnotationPolicyError."""
    with pytest.raises(AnnotationPolicyError):
        AnnotationPolicy(foundational_centrality_threshold=1.5)  # Out of range