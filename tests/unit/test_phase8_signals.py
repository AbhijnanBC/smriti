"""Unit tests for scoring/signals/*.py."""

import pytest
import dataclasses
from pathlib import Path
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, ScoringGlobalStats, GraphStatistics,
    ValidationReport, SemanticRole, TopologyMetrics, SupportAggregate,
    TemporalMetadata, TemporalStatus, SignalStatus, NodeAnnotations,
)
from smriti.scoring.policies import load_policy
from smriti.scoring.signals import (
    EvidenceStrengthExtractor, EvidenceIndependenceExtractor,
    TopologyStrengthExtractor, HubScoreExtractor, BridgeScoreExtractor,
    ConflictPressureExtractor, SourceDiversityExtractor, TemporalStabilityExtractor,
)


def make_global_stats(**kwargs):
    defaults = dict(
        max_support_count=10, avg_support_count=3.0, max_in_degree=5,
        avg_degree=2.5, max_contradiction_partners=3, avg_contradiction_partners=0.5,
        max_source_diversity=5, max_temporal_confidence=1.0,
        node_count=10, partition_count=2, contradiction_count=2, supports_count=8,
    )
    defaults.update(kwargs)
    return ScoringGlobalStats(**defaults)


def make_node(claim_id="c001", support_count=0, in_degree=1,
              degree=2, centrality=0.5, is_hub=False, is_bridge=False,
              temporal_status=None) -> ClaimNode:
    support = None
    if support_count > 0:
        supporting_ids = [f"supporter_{i}" for i in range(support_count)]
        support = SupportAggregate(
            support_count=support_count, weighted_confidence=0.80,
            supporting_claim_ids=tuple(supporting_ids),
            evidence_summary=f"{support_count} supporters",
        )
    topo = TopologyMetrics(
        degree=degree, in_degree=in_degree, out_degree=degree - in_degree,
        is_bridge=is_bridge, is_hub=is_hub, partition_id="p001", centrality=centrality,
    )
    temporal = None
    if temporal_status:
        temporal = TemporalMetadata(
            status=temporal_status, earlier_claim_id=None, later_claim_id=None,
            time_delta_days=30.0, temporal_confidence=0.80,
        )
    annotations = NodeAnnotations(
        semantic_role=SemanticRole.UNCLASSIFIED,
        topology=topo, support_aggregate=support, temporal_metadata=temporal,
        partition_id="p001",
    )
    return ClaimNode(
        node_id=claim_id, claim_id=claim_id, claim_text="Test.",
        context="", source_path=Path("test.md"), document_id="d001",
        annotations=annotations,
    )


def make_empty_graph():
    stats = GraphStatistics(
        node_count=1, edge_count=0, partition_count=1,
        contradiction_count=0, supports_count=0, refines_count=0,
        isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
        evolution_chains=0, unresolved_conflicts=0,
        construction_time_seconds=0.0, enrichment_time_seconds=0.0,
    )
    vr = ValidationReport(
        is_valid=True, node_violations=(), edge_violations=(),
        graph_violations=(), semantic_warnings=(), validation_time_seconds=0.0,
    )
    return KnowledgeGraph(
        graph_id="test", nodes={}, edges={}, partitions={},
        statistics=stats, validation_report=vr, run_id="test", config_hash="test",
    )


@pytest.fixture
def policy(): return load_policy()

@pytest.fixture
def global_stats(): return make_global_stats()

@pytest.fixture
def graph(): return make_empty_graph()


class TestEvidenceStrengthExtractor:
    def test_no_support_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001", support_count=0)
        ext = EvidenceStrengthExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_high_support_returns_high_value(self, policy, global_stats, graph):
        node = make_node("c001", support_count=10)
        ext = EvidenceStrengthExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.5

    def test_value_in_range(self, policy, global_stats, graph):
        for count in [0, 1, 3, 10, 20]:
            node = make_node("c001", support_count=count)
            ext = EvidenceStrengthExtractor()
            signal = ext.extract(node, graph, global_stats, policy)
            assert 0.0 <= signal.normalized_value <= 1.0

    def test_status_is_measured(self, policy, global_stats, graph):
        node = make_node("c001", support_count=5)
        signal = EvidenceStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.MEASURED


class TestTopologyStrengthExtractor:
    def test_high_centrality_gives_high_value(self, policy, global_stats, graph):
        node = make_node("c001", centrality=0.90)
        signal = TopologyStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.70

    def test_no_topology_returns_unavailable(self, policy, global_stats, graph):
        node = ClaimNode(
            node_id="c001", claim_id="c001", claim_text="Test.",
            context="", source_path=Path("test.md"), document_id="d001",
            annotations=None,
        )
        signal = TopologyStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.UNAVAILABLE
        assert signal.normalized_value == 0.0


class TestConflictPressureExtractor:
    def test_no_contradictions_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001")
        signal = ConflictPressureExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_value_always_in_range(self, policy, global_stats, graph):
        node = make_node("c001")
        signal = ConflictPressureExtractor().extract(node, graph, global_stats, policy)
        assert 0.0 <= signal.normalized_value <= 1.0


class TestTemporalStabilityExtractor:
    def test_evolution_chain_gives_high_stability(self, policy, global_stats, graph):
        node = make_node("c001", temporal_status=TemporalStatus.EVOLUTION_CHAIN)
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.50

    def test_no_temporal_data_uses_default(self, policy, global_stats, graph):
        node = make_node("c001", temporal_status=None)
        node = dataclasses.replace(
            node, annotations=dataclasses.replace(node.annotations, temporal_metadata=None)
        )
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.DEFAULT
        assert signal.normalized_value == policy.temporal.default_stability


class TestHubAndBridgeExtractors:
    """RECTIFIED (P0-3): hub_score and bridge_score are now separate signals."""

    def test_hub_node_returns_one(self, policy, global_stats, graph):
        node = make_node("c001", is_hub=True)
        signal = HubScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 1.0

    def test_non_hub_node_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001", is_hub=False)
        signal = HubScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_bridge_node_returns_one(self, policy, global_stats, graph):
        node = make_node("c001", is_bridge=True)
        signal = BridgeScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 1.0

    def test_topology_strength_has_no_hub_bonus(self, policy, global_stats, graph):
        """RECTIFIED (P0-3): TopologyStrengthExtractor must NOT apply hub bonus."""
        node_hub = make_node("c001", centrality=0.50, is_hub=True)
        node_normal = make_node("c002", centrality=0.50, is_hub=False)
        ext = TopologyStrengthExtractor()
        sig_hub = ext.extract(node_hub, graph, global_stats, policy)
        sig_normal = ext.extract(node_normal, graph, global_stats, policy)
        # With hub bonus removed, both should produce the same value for same centrality
        assert abs(sig_hub.normalized_value - sig_normal.normalized_value) < 1e-6, (
            "TopologyStrengthExtractor must not apply hub bonus. "
            "Hub importance is handled by HubScoreExtractor as a separate signal."
        )

    def test_signal_manifest_has_normalization_strategy(self, policy, global_stats, graph):
        """RECTIFIED (P0-4): Every signal must expose normalization_strategy."""
        for ext_class in [
            EvidenceStrengthExtractor, HubScoreExtractor, BridgeScoreExtractor,
            ConflictPressureExtractor, TemporalStabilityExtractor,
        ]:
            ext = ext_class()
            assert hasattr(ext, "normalization_strategy")
            assert isinstance(ext.normalization_strategy, str)
            assert len(ext.normalization_strategy) > 0