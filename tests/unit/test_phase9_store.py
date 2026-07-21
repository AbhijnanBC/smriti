"""Unit tests for api/store/memory_store.py."""

import pytest
from pathlib import Path
from smriti.api.store.memory_store import InMemoryReadStore
from smriti.api.domain.predicates import Predicate, SortSpec, Pagination
from smriti.core.models import (
    ScoredKnowledgeGraph, KnowledgeGraph, ClaimNode, RelationshipEdge,
    KnowledgePartition, GraphStatistics, ValidationReport,
    SemanticRole, TopologyMetrics, SupportAggregate, TemporalMetadata,
    TemporalStatus, RelationshipType, RelationshipDirection,
    ReliabilityMetadata, CalibrationLabel, SignalVector,
    ComponentScore, ReliabilityExplanation, ReliabilityAudit,
    NodeAnnotations, ScoringGlobalStats, PredicateOperator, SortOrder,
)


def make_test_scored_graph():
    """Build a minimal ScoredKnowledgeGraph for store tests."""
    ann_a = NodeAnnotations(
        semantic_role=SemanticRole.FOUNDATIONAL_CLAIM,
        topology=TopologyMetrics(
            degree=3, in_degree=2, out_degree=1,
            is_bridge=False, is_hub=False, partition_id="p001", centrality=0.65,
        ),
        support_aggregate=SupportAggregate(
            support_count=3, weighted_confidence=0.82,
            supporting_claim_ids=("c002",),
            evidence_summary="3 supporting claims",
        ),
        temporal_metadata=TemporalMetadata(
            status=TemporalStatus.STATIC_PARTITION,
            earlier_claim_id=None, later_claim_id=None,
            time_delta_days=None, temporal_confidence=0.0,
        ),
        partition_id="p001",
    )
    ann_b = NodeAnnotations(
        semantic_role=SemanticRole.PERIPHERAL_CLAIM,
        topology=TopologyMetrics(
            degree=1, in_degree=0, out_degree=1,
            is_bridge=False, is_hub=False, partition_id="p002", centrality=0.10,
        ),
        support_aggregate=None, temporal_metadata=None, partition_id="p002",
    )

    def make_node(nid, text, ann):
        return ClaimNode(
            node_id=nid, claim_id=nid, claim_text=text,
            context="Python > ML", source_path=Path("note.md"),
            document_id=f"d_{nid}", annotations=ann,
        )

    def make_reliability(claim_id, ri, label):
        sv = SignalVector(
            evidence_strength=0.5, evidence_independence=0.7, source_diversity=0.4,
            topology_strength=0.3, conflict_pressure=0.1, temporal_stability=0.5,
            evidence_completeness=1.0, statuses={},
        )
        return ReliabilityMetadata(
            claim_id=claim_id,
            reliability_index=ri,
            uncertainty_score=15.0,
            evidence_completeness=1.0,
            signal_vector=sv,
            signal_manifests=(),
            component_scores=(),
            decision_record=None,
            explanation=ReliabilityExplanation(
                summary="Reliable.", strengths=(), weaknesses=(),
                dominant_signal="evidence_strength", limiting_signal="none",
                recommendations=(),
            ),
            calibration_label=label,
            audit=ReliabilityAudit(
                policy_version="1.0", policy_profile="balanced",
                graph_schema_version="7.0", fusion_algorithm="v2",
                normalization_version="1.1", computed_at_run_id="r1",
                signal_extractor_versions={}, registry_order=(),
            ),
            policy_version="1.0",
        )

    nodes = {
        "c001": make_node("c001", "Always normalize features before PCA.", ann_a),
        "c002": make_node("c002", "Normalization is often unnecessary.", ann_b),
    }
    edges = {
        "r1": RelationshipEdge(
            edge_id="r1", source_node_id="c001", target_node_id="c002",
            relationship_type=RelationshipType.CONTRADICTS,
            direction=RelationshipDirection.SYMMETRIC,
            calibrated_confidence=0.88, cosine_similarity=0.82,
            nli_confidence=0.88, candidate_rank=1,
        ),
    }
    partitions = {
        "p001": KnowledgePartition(
            partition_id="p001", stable_partition_label="c001",
            node_ids=frozenset(["c001"]), internal_edge_ids=frozenset(),
            node_count=1, edge_count=0, supports_count=0, refines_count=0,
            density=0.0, longest_support_chain=0,
        ),
        "p002": KnowledgePartition(
            partition_id="p002", stable_partition_label="c002",
            node_ids=frozenset(["c002"]), internal_edge_ids=frozenset(),
            node_count=1, edge_count=0, supports_count=0, refines_count=0,
            density=0.0, longest_support_chain=0,
        ),
    }
    stats = GraphStatistics(
        node_count=2, edge_count=1, partition_count=2,
        contradiction_count=1, supports_count=0, refines_count=0,
        isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
        evolution_chains=0, unresolved_conflicts=0,
        construction_time_seconds=0.1, enrichment_time_seconds=0.2,
    )
    vr = ValidationReport(
        is_valid=True, node_violations=(), edge_violations=(),
        graph_violations=(), semantic_violations=(), validation_time_seconds=0.01,
    )
    kg = KnowledgeGraph(
        graph_id="g001", nodes=nodes, edges=edges, partitions=partitions,
        statistics=stats, validation_report=vr, run_id="r1",
        config_hash="test", schema_version="7.0",
    )
    reliability = {
        "c001": make_reliability("c001", 78.5, CalibrationLabel.HIGH),
        "c002": make_reliability("c002", 32.0, CalibrationLabel.LOW),
    }
    return ScoredKnowledgeGraph(
        graph=kg, reliability=reliability,
        policy_snapshot={}, policy_profile="balanced",
        global_stats=ScoringGlobalStats(
            max_support_count=3, avg_support_count=1.5, max_in_degree=2,
            avg_degree=2.0, max_contradiction_partners=1, avg_contradiction_partners=0.5,
            max_source_diversity=3, max_temporal_confidence=1.0,
            node_count=2, partition_count=2, contradiction_count=1, supports_count=0,
        ),
        run_id="r1", schema_version="8.0",
    )


@pytest.fixture
def store():
    return InMemoryReadStore(make_test_scored_graph())


def test_node_count(store):
    assert store.node_count == 2


def test_lookup_claim_found(store):
    record = store.lookup("c001")
    assert record is not None
    assert record["claim_id"] == "c001"


def test_lookup_claim_not_found(store):
    assert store.lookup("nonexistent") is None


def test_fetch_relationship_found(store):
    record = store.fetch_relationship("c001")
    assert record is not None
    assert record["reliability_index"] == 78.5


def test_scan_returns_all_without_predicates(store):
    records, total = store.scan(predicates=[], sort=SortSpec("claim_id"), pagination=Pagination(limit=100))
    assert total == 2


def test_scan_with_predicate(store):
    p = Predicate("calibration_label", PredicateOperator.EQ, "high")
    records, total = store.scan(predicates=[p], sort=SortSpec("claim_id"), pagination=Pagination())
    assert total == 1
    assert records[0]["claim_id"] == "c001"


def test_scan_sorted_desc(store):
    records, _ = store.scan(
        predicates=[],
        sort=SortSpec("reliability_index", SortOrder.DESC),
        pagination=Pagination(limit=10),
    )
    assert len(records) == 2
    assert records[0]["reliability_index"] >= records[1]["reliability_index"]


def test_scan_pagination(store):
    records, total = store.scan(predicates=[], sort=SortSpec("claim_id"), pagination=Pagination(limit=1, offset=0))
    assert len(records) == 1 and total == 2


def test_stream_returns_all(store):
    all_records = list(store.stream())
    assert len(all_records) == 2


def test_get_adjacency(store):
    adj = store.get_adjacency()
    assert isinstance(adj, dict)


def test_get_edge_records(store):
    edges = store.get_edge_records()
    assert len(edges) == 1  # One CONTRADICTS edge (+ symmetric reverse may be included)


def test_run_id(store):
    assert store.run_id == "r1"


def test_read_store_has_no_aggregate_statistics_method():
    """RECTIFIED (P0-1): ReadStore must NOT have aggregate_statistics method."""
    from smriti.api.store.read_store import ReadStore
    assert not hasattr(ReadStore, "aggregate_statistics"), (
        "aggregate_statistics must NOT be in ReadStore. "
        "Aggregation belongs in StatisticsService."
    )


def test_read_store_has_no_traverse_graph_method():
    """RECTIFIED (P0-1): ReadStore must NOT have traverse_graph method."""
    from smriti.api.store.read_store import ReadStore
    assert not hasattr(ReadStore, "traverse_graph"), (
        "traverse_graph must NOT be in ReadStore. "
        "Traversal belongs in NavigationService."
    )