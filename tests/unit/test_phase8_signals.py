"""Unit tests for scoring/signals/*.py."""

import dataclasses
from pathlib import Path

import pytest
from smriti.core.models import (
    ClaimNode,
    DocumentProvenance,
    GraphStatistics,
    KnowledgeGraph,
    NodeAnnotations,
    ScoringGlobalStats,
    SemanticRole,
    SignalStatus,
    SupportAggregate,
    TemporalMetadata,
    TemporalStatus,
    TopologyMetrics,
    ValidationReport,
)
from smriti.scoring.policies import load_policy
from smriti.scoring.signals import (
    BridgeScoreExtractor,
    ConflictPressureExtractor,
    EvidenceIndependenceExtractor,
    EvidenceStrengthExtractor,
    HubScoreExtractor,
    SourceDiversityExtractor,
    TemporalStabilityExtractor,
    TopologyStrengthExtractor,
)


def make_supporter_node(claim_id: str, document_id: str) -> ClaimNode:
    return ClaimNode(
        node_id=claim_id,
        claim_id=claim_id,
        claim_text="Supporter.",
        context="",
        source_path=Path(f"{document_id}.md"),
        document_id=document_id,
    )


def make_graph_with_supporters(
    doc_by_claim: dict, document_provenance: dict | None = None
) -> KnowledgeGraph:
    """A KnowledgeGraph populated with real supporter nodes, one per
    (claim_id, document_id) pair. Unlike make_empty_graph (nodes={}), this
    lets SourceDiversityExtractor/EvidenceIndependenceExtractor actually
    resolve supporter document_ids instead of silently no-op'ing on a
    graph.nodes.get(cid) miss."""
    stats = GraphStatistics(
        node_count=len(doc_by_claim),
        edge_count=0,
        partition_count=1,
        contradiction_count=0,
        supports_count=0,
        refines_count=0,
        isolated_nodes=0,
        bridge_nodes=0,
        hub_nodes=0,
        evolution_chains=0,
        unresolved_conflicts=0,
        construction_time_seconds=0.0,
        enrichment_time_seconds=0.0,
    )
    vr = ValidationReport(
        is_valid=True,
        node_violations=(),
        edge_violations=(),
        graph_violations=(),
        semantic_warnings=(),
        validation_time_seconds=0.0,
    )
    nodes = {cid: make_supporter_node(cid, doc) for cid, doc in doc_by_claim.items()}
    return KnowledgeGraph(
        graph_id="test",
        nodes=nodes,
        edges={},
        partitions={},
        statistics=stats,
        validation_report=vr,
        run_id="test",
        config_hash="test",
        document_provenance=document_provenance or {},
    )


def make_global_stats(**kwargs):
    defaults = dict(
        max_support_count=10,
        avg_support_count=3.0,
        max_in_degree=5,
        avg_degree=2.5,
        max_contradiction_partners=3,
        avg_contradiction_partners=0.5,
        max_source_diversity=5,
        max_temporal_confidence=1.0,
        node_count=10,
        partition_count=2,
        contradiction_count=2,
        supports_count=8,
    )
    defaults.update(kwargs)
    return ScoringGlobalStats(**defaults)


def make_node(
    claim_id="c001",
    support_count=0,
    in_degree=1,
    degree=2,
    centrality=0.5,
    is_hub=False,
    is_bridge=False,
    temporal_status=None,
) -> ClaimNode:
    support = None
    if support_count > 0:
        supporting_ids = [f"supporter_{i}" for i in range(support_count)]
        support = SupportAggregate(
            support_count=support_count,
            weighted_confidence=0.80,
            supporting_claim_ids=tuple(supporting_ids),
            evidence_summary=f"{support_count} supporters",
        )
    topo = TopologyMetrics(
        degree=degree,
        in_degree=in_degree,
        out_degree=degree - in_degree,
        is_bridge=is_bridge,
        is_hub=is_hub,
        partition_id="p001",
        centrality=centrality,
    )
    temporal = None
    if temporal_status:
        temporal = TemporalMetadata(
            status=temporal_status,
            earlier_claim_id=None,
            later_claim_id=None,
            time_delta_days=30.0,
            temporal_confidence=0.80,
        )
    annotations = NodeAnnotations(
        semantic_role=SemanticRole.UNCLASSIFIED,
        topology=topo,
        support_aggregate=support,
        temporal_metadata=temporal,
        partition_id="p001",
    )
    return ClaimNode(
        node_id=claim_id,
        claim_id=claim_id,
        claim_text="Test.",
        context="",
        source_path=Path("test.md"),
        document_id="d001",
        annotations=annotations,
    )


def make_empty_graph():
    stats = GraphStatistics(
        node_count=1,
        edge_count=0,
        partition_count=1,
        contradiction_count=0,
        supports_count=0,
        refines_count=0,
        isolated_nodes=0,
        bridge_nodes=0,
        hub_nodes=0,
        evolution_chains=0,
        unresolved_conflicts=0,
        construction_time_seconds=0.0,
        enrichment_time_seconds=0.0,
    )
    vr = ValidationReport(
        is_valid=True,
        node_violations=(),
        edge_violations=(),
        graph_violations=(),
        semantic_warnings=(),
        validation_time_seconds=0.0,
    )
    return KnowledgeGraph(
        graph_id="test",
        nodes={},
        edges={},
        partitions={},
        statistics=stats,
        validation_report=vr,
        run_id="test",
        config_hash="test",
    )


@pytest.fixture
def policy():
    return load_policy()


@pytest.fixture
def global_stats():
    return make_global_stats()


@pytest.fixture
def graph():
    return make_empty_graph()


class TestEvidenceIndependenceExtractor:
    def test_no_support_does_not_reward_absence_of_evidence(self, policy, global_stats, graph):
        """
        RECTIFIED (P0-8): a claim with zero supporting evidence must NOT
        receive a maximal (1.0) independence score. There is nothing to be
        independent OF -- the correct signal is UNAVAILABLE with value 0.0,
        so this claim never gets a positive contribution from a signal that
        had nothing real to measure.
        """
        node = make_node("c001", support_count=0)
        ext = EvidenceIndependenceExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0
        assert signal.raw_value == 0.0
        assert signal.status == SignalStatus.UNAVAILABLE

    def test_single_supporter_is_measured_not_default(self, policy, global_stats, graph):
        node = make_node("c001", support_count=1)
        ext = EvidenceIndependenceExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.MEASURED


class TestEvidenceGroupCollapsing:
    """
    RECTIFIED (provenance/reliability redesign): a claim linked to another
    supporter via an EQUIVALENT edge (a paraphrase) is semantic-duplicate
    evidence, not a second independent corroboration. Phase 7's aggregation
    step (aggregation.py) now collapses EQUIVALENT-linked supporters into
    evidence groups (SupportAggregate.independent_evidence_group_ids), and
    SourceDiversityExtractor / EvidenceIndependenceExtractor must measure
    over that collapsed set, not the raw supporting_claim_ids -- otherwise
    a paraphrase living in a second document silently inflates apparent
    source diversity for what is actually one piece of evidence.
    """

    def _node_with_aggregate(self, supporting_ids, group_ids):
        support = SupportAggregate(
            support_count=len(supporting_ids),
            weighted_confidence=0.85,
            supporting_claim_ids=tuple(supporting_ids),
            evidence_summary=f"{len(supporting_ids)} supporters",
            independent_evidence_group_ids=tuple(group_ids),
            independent_evidence_group_count=len(group_ids),
        )
        annotations = NodeAnnotations(
            semantic_role=SemanticRole.UNCLASSIFIED,
            topology=None,
            support_aggregate=support,
            temporal_metadata=None,
            partition_id="p001",
        )
        return ClaimNode(
            node_id="c001",
            claim_id="c001",
            claim_text="Test.",
            context="",
            source_path=Path("test.md"),
            document_id="d000",
            annotations=annotations,
        )

    def test_source_diversity_collapses_equivalent_paraphrase(self, policy, global_stats):
        """A (doc1) and B (doc2) are EQUIVALENT paraphrases collapsed to one
        evidence group ('A'); C (doc3) is independent. Raw supporting_claim_ids
        would suggest 3 unique documents; the correct, group-collapsed count
        is 2 (doc1 via the 'A' representative, doc3 via C) -- B's doc2 must
        not be double-counted as a second independent source."""
        graph = make_graph_with_supporters({"A": "doc1", "B": "doc2", "C": "doc3"})
        node = self._node_with_aggregate(
            supporting_ids=["A", "B", "C"],
            group_ids=["A", "C"],
        )
        signal = SourceDiversityExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_documents"] == 2, (
            "SourceDiversityExtractor must count documents over the "
            "EQUIVALENT-collapsed evidence groups, not every raw supporter."
        )
        assert signal.metadata["raw_supporter_count"] == 3
        assert signal.metadata["evidence_group_count"] == 2

    def test_evidence_independence_collapses_equivalent_paraphrase(self, policy, global_stats):
        graph = make_graph_with_supporters({"A": "doc1", "B": "doc2", "C": "doc3"})
        node = self._node_with_aggregate(
            supporting_ids=["A", "B", "C"],
            group_ids=["A", "C"],
        )
        signal = EvidenceIndependenceExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_documents"] == 2
        assert signal.metadata["total_supporters"] == 2
        assert signal.metadata["raw_supporter_count"] == 3

    def test_legacy_aggregate_without_group_ids_falls_back_to_raw(self, policy, global_stats):
        """A SupportAggregate built before this rectification (no
        independent_evidence_group_ids set) must fall back to the old,
        uncollapsed behavior exactly -- this is a legacy-fixture signature,
        not a claim that zero evidence groups exist."""
        graph = make_graph_with_supporters({"A": "doc1", "B": "doc2", "C": "doc3"})
        node = self._node_with_aggregate(
            supporting_ids=["A", "B", "C"],
            group_ids=[],
        )
        signal = SourceDiversityExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_documents"] == 3


class TestDeclaredSourceIdentity:
    """
    RECTIFIED (external review, P1-1 "provenance/source lineage"): two
    documents that both declare the SAME source_id (e.g. the same wire
    article saved as two files) are copies of one source, not two
    independent ones -- source_identity() / graph.document_provenance
    must collapse them for diversity/independence purposes even though
    their document_ids differ.
    """

    def _node_with_aggregate(self, supporting_ids, group_ids):
        support = SupportAggregate(
            support_count=len(supporting_ids),
            weighted_confidence=0.85,
            supporting_claim_ids=tuple(supporting_ids),
            evidence_summary=f"{len(supporting_ids)} supporters",
            independent_evidence_group_ids=tuple(group_ids),
            independent_evidence_group_count=len(group_ids),
        )
        annotations = NodeAnnotations(
            semantic_role=SemanticRole.UNCLASSIFIED,
            topology=None,
            support_aggregate=support,
            temporal_metadata=None,
            partition_id="p001",
        )
        return ClaimNode(
            node_id="c001",
            claim_id="c001",
            claim_text="Test.",
            context="",
            source_path=Path("test.md"),
            document_id="d000",
            annotations=annotations,
        )

    def test_source_diversity_collapses_two_documents_sharing_a_declared_source_id(
        self, policy, global_stats
    ):
        # doc1 and doc2 both declare source_id "wire-42" -- they are the
        # SAME source republished as two files; doc3 declares nothing.
        provenance = {
            "doc1": DocumentProvenance(source_id="wire-42", extraction_method="yaml_frontmatter"),
            "doc2": DocumentProvenance(source_id="wire-42", extraction_method="yaml_frontmatter"),
        }
        graph = make_graph_with_supporters(
            {"A": "doc1", "B": "doc2", "C": "doc3"},
            document_provenance=provenance,
        )
        node = self._node_with_aggregate(supporting_ids=["A", "B", "C"], group_ids=["A", "B", "C"])
        signal = SourceDiversityExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_documents"] == 2, (
            "A (doc1) and B (doc2) declare the same source_id and must "
            "collapse to one source; only C (doc3, no declared source) is "
            "genuinely distinct -- expected 2 unique sources, not 3."
        )

    def test_no_declared_source_id_falls_back_to_document_id(self, policy, global_stats):
        graph = make_graph_with_supporters({"A": "doc1", "B": "doc2", "C": "doc3"})
        node = self._node_with_aggregate(supporting_ids=["A", "B", "C"], group_ids=["A", "B", "C"])
        signal = SourceDiversityExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_documents"] == 3

    def test_evidence_independence_prefers_declared_publisher_over_path_heuristic(
        self, policy, global_stats
    ):
        # A and B live under different path directories (so the OLD
        # path-based heuristic would have called them different
        # publishers), but both declare the SAME publisher explicitly.
        provenance = {
            "doc1": DocumentProvenance(publisher="Reuters", extraction_method="yaml_frontmatter"),
            "doc2": DocumentProvenance(publisher="Reuters", extraction_method="yaml_frontmatter"),
        }
        graph = make_graph_with_supporters(
            {"A": "doc1", "B": "doc2", "C": "doc3"},
            document_provenance=provenance,
        )
        node = self._node_with_aggregate(supporting_ids=["A", "B", "C"], group_ids=["A", "B", "C"])
        signal = EvidenceIndependenceExtractor().extract(node, graph, global_stats, policy)
        assert signal.metadata["unique_publishers"] == 2, (
            "A and B declare the same publisher (Reuters) and must "
            "collapse to one, overriding the path-directory heuristic "
            "that would otherwise treat every distinct document_id's "
            "path as its own publisher."
        )


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

    def test_hop_distance_discount_lowers_raw_value_relative_to_all_direct(
        self, policy, global_stats, graph
    ):
        """RECTIFIED (external review, P1-2): with the SAME raw
        support_count of 3, a node whose evidence is one direct + one
        derived + one multi-hop supporter must score LOWER than a node
        with three direct supporters -- discounting must actually change
        the signal's output, not just annotate metadata."""

        def make_node_with_groups(direct, derived, multi_hop):
            all_ids = tuple(direct + derived + multi_hop)
            support = SupportAggregate(
                support_count=len(all_ids),
                weighted_confidence=0.80,
                supporting_claim_ids=all_ids,
                evidence_summary="test",
                independent_evidence_group_ids=all_ids,
                independent_evidence_group_count=len(all_ids),
                direct_evidence_group_ids=tuple(direct),
                derived_evidence_group_ids=tuple(derived),
                multi_hop_evidence_group_ids=tuple(multi_hop),
                discounted_evidence_strength=(
                    1.0 * len(direct) + 0.6 * len(derived) + 0.3 * len(multi_hop)
                ),
                discounted_weighted_confidence=0.80,
            )
            annotations = NodeAnnotations(
                semantic_role=SemanticRole.UNCLASSIFIED,
                topology=None,
                support_aggregate=support,
                temporal_metadata=None,
                partition_id="p001",
            )
            return ClaimNode(
                node_id="c001",
                claim_id="c001",
                claim_text="Test.",
                context="",
                source_path=Path("test.md"),
                document_id="d000",
                annotations=annotations,
            )

        all_direct = make_node_with_groups(["A", "B", "C"], [], [])
        mixed = make_node_with_groups(["A"], ["B"], ["C"])

        ext = EvidenceStrengthExtractor()
        signal_all_direct = ext.extract(all_direct, graph, global_stats, policy)
        signal_mixed = ext.extract(mixed, graph, global_stats, policy)

        assert signal_mixed.raw_value < signal_all_direct.raw_value
        assert signal_mixed.metadata["discounted_evidence_strength"] == 1.9


class TestTopologyStrengthExtractor:
    def test_high_centrality_gives_high_value(self, policy, global_stats, graph):
        node = make_node("c001", centrality=0.90)
        signal = TopologyStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.70

    def test_no_topology_returns_unavailable(self, policy, global_stats, graph):
        node = ClaimNode(
            node_id="c001",
            claim_id="c001",
            claim_text="Test.",
            context="",
            source_path=Path("test.md"),
            document_id="d001",
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

    def test_no_temporal_data_is_unavailable_not_defaulted(self, policy, global_stats, graph):
        """RECTIFIED (external review item 21): absence of temporal evidence
        must not be scored as a real, moderate-stability measurement."""
        node = make_node("c001", temporal_status=None)
        node = dataclasses.replace(
            node, annotations=dataclasses.replace(node.annotations, temporal_metadata=None)
        )
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.UNAVAILABLE
        assert signal.normalized_value == 0.0

    def test_no_timestamp_status_is_unavailable_not_defaulted(self, policy, global_stats, graph):
        node = make_node("c001", temporal_status=TemporalStatus.NO_TIMESTAMP)
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.UNAVAILABLE
        assert signal.normalized_value == 0.0


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
            EvidenceStrengthExtractor,
            HubScoreExtractor,
            BridgeScoreExtractor,
            ConflictPressureExtractor,
            TemporalStabilityExtractor,
        ]:
            ext = ext_class()
            assert hasattr(ext, "normalization_strategy")
            assert isinstance(ext.normalization_strategy, str)
            assert len(ext.normalization_strategy) > 0
