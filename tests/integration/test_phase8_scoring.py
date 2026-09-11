"""Integration test for Phase 8 end-to-end."""

import json
from pathlib import Path

import pytest
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    CalibrationLabel,
    ClaimNode,
    GraphStatistics,
    KnowledgeGraph,
    KnowledgePartition,
    NodeAnnotations,
    RelationshipDirection,
    RelationshipEdge,
    RelationshipType,
    ScoredKnowledgeGraph,
    SemanticRole,
    SupportAggregate,
    TemporalMetadata,
    TemporalStatus,
    TopologyMetrics,
    ValidationReport,
)
from smriti.core.state import StateManager
from smriti.scoring import score_knowledge_graph


def make_minimal_graph(run_id="test_run") -> KnowledgeGraph:
    topo_a = TopologyMetrics(
        degree=3,
        in_degree=2,
        out_degree=1,
        is_bridge=False,
        is_hub=False,
        partition_id="p001",
        centrality=0.65,
    )
    support_a = SupportAggregate(
        support_count=3,
        weighted_confidence=0.82,
        supporting_claim_ids=("c002", "c003"),
        evidence_summary="3 supporting claims",
    )
    temporal_a = TemporalMetadata(
        status=TemporalStatus.STATIC_PARTITION,
        earlier_claim_id=None,
        later_claim_id=None,
        time_delta_days=None,
        temporal_confidence=0.0,
    )
    topo_b = TopologyMetrics(
        degree=1,
        in_degree=0,
        out_degree=1,
        is_bridge=False,
        is_hub=False,
        partition_id="p002",
        centrality=0.10,
    )
    ann_a = NodeAnnotations(
        semantic_role=SemanticRole.FOUNDATIONAL_CLAIM,
        topology=topo_a,
        support_aggregate=support_a,
        temporal_metadata=temporal_a,
        partition_id="p001",
    )
    ann_b = NodeAnnotations(
        semantic_role=SemanticRole.PERIPHERAL_CLAIM,
        topology=topo_b,
        support_aggregate=None,
        temporal_metadata=None,
        partition_id="p002",
    )
    nodes = {
        "c001": ClaimNode(
            node_id="c001",
            claim_id="c001",
            claim_text="Always normalize features before PCA.",
            context="Python > ML",
            source_path=Path("note.md"),
            document_id="d001",
            annotations=ann_a,
        ),
        "c002": ClaimNode(
            node_id="c002",
            claim_id="c002",
            claim_text="Normalization is often unnecessary.",
            context="Python > ML",
            source_path=Path("note2.md"),
            document_id="d002",
            annotations=ann_b,
        ),
    }
    edges = {
        "r1": RelationshipEdge(
            edge_id="r1",
            source_node_id="c001",
            target_node_id="c002",
            relationship_type=RelationshipType.CONTRADICTS,
            direction=RelationshipDirection.SYMMETRIC,
            calibrated_confidence=0.88,
            cosine_similarity=0.82,
            nli_confidence=0.88,
            candidate_rank=1,
        ),
    }
    partitions = {
        "p001": KnowledgePartition(
            partition_id="p001",
            stable_partition_label="c001",
            node_ids=frozenset(["c001"]),
            internal_edge_ids=frozenset(),
            node_count=1,
            edge_count=0,
            supports_count=0,
            refines_count=0,
            density=0.0,
            longest_support_chain=0,
        ),
        "p002": KnowledgePartition(
            partition_id="p002",
            stable_partition_label="c002",
            node_ids=frozenset(["c002"]),
            internal_edge_ids=frozenset(),
            node_count=1,
            edge_count=0,
            supports_count=0,
            refines_count=0,
            density=0.0,
            longest_support_chain=0,
        ),
    }
    stats = GraphStatistics(
        node_count=2,
        edge_count=1,
        partition_count=2,
        contradiction_count=1,
        supports_count=0,
        refines_count=0,
        isolated_nodes=0,
        bridge_nodes=0,
        hub_nodes=0,
        evolution_chains=0,
        unresolved_conflicts=0,
        construction_time_seconds=0.1,
        enrichment_time_seconds=0.2,
    )
    vr = ValidationReport(
        is_valid=True,
        node_violations=(),
        edge_violations=(),
        graph_violations=(),
        semantic_warnings=(),
        validation_time_seconds=0.01,
    )
    return KnowledgeGraph(
        graph_id="test_graph_001",
        nodes=nodes,
        edges=edges,
        partitions=partitions,
        statistics=stats,
        validation_report=vr,
        run_id=run_id,
        config_hash="test_hash",
        schema_version="7.0",
    )


@pytest.fixture
def run_id():
    return "test_phase8_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


@pytest.fixture
def graph():
    return make_minimal_graph()


# ── Original 15 tests ─────────────────────────────────────────────────────────


def test_returns_scored_knowledge_graph(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    assert isinstance(result, ScoredKnowledgeGraph)


def test_every_node_is_scored(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    assert result.total_scored == graph.node_count
    for claim_id in graph.nodes:
        assert claim_id in result.reliability


def test_original_graph_not_modified(graph, run_id, test_managers):
    original_count = graph.node_count
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    assert result.graph is graph
    assert result.graph.node_count == original_count


def test_reliability_index_in_range(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert 0.0 <= meta.reliability_index <= 100.0


def test_uncertainty_in_range(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert 0.0 <= meta.uncertainty_score <= 100.0


def test_calibration_label_assigned(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert isinstance(meta.calibration_label, CalibrationLabel)


def test_explanation_is_populated(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert meta.explanation.summary


def test_schema_version_correct(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    assert result.schema_version == "8.0"
    for meta in result.reliability.values():
        assert meta.schema_version == "8.0"


def test_component_scores_sum_approximates_ri(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        comp_sum = sum(c.contribution for c in meta.component_scores)
        assert abs(comp_sum - meta.reliability_index) <= 30.0


def test_deterministic_scoring(graph, run_id, test_managers, tmp_path):
    manifest_mgr, state_mgr = test_managers
    result1 = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    manifest_mgr2 = ManifestManager(run_id=f"{run_id}_2", artifacts_dir=tmp_path / "artifacts2")
    state_mgr2 = StateManager(state_file=tmp_path / "state2.json")
    result2 = score_knowledge_graph(
        graph=graph, run_id=f"{run_id}_2", manifest_manager=manifest_mgr2, state_manager=state_mgr2
    )
    for claim_id in graph.nodes:
        ri1 = result1.reliability[claim_id].reliability_index
        ri2 = result2.reliability[claim_id].reliability_index
        assert ri1 == ri2, f"Non-deterministic: {claim_id} got {ri1} vs {ri2}"


def test_dataset_json_written(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    phase_dir = manifest_mgr.run_dir / "phase8"
    dataset_path = phase_dir / "dataset.json"
    assert dataset_path.exists()
    data = json.loads(dataset_path.read_text())
    assert "reliability" in data and len(data["reliability"]) == graph.node_count


def test_manifest_written(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    manifest_path = manifest_mgr.run_dir / "phase8" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["phase"] == 8 and manifest["status"] == "success"


def test_pipeline_state_updated(graph, run_id, test_managers):
    _, state_mgr = test_managers
    manifest_mgr, _ = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    state = state_mgr.load()
    assert state is not None and 8 in state.completed_phases


def test_well_supported_claim_higher_than_unsupported(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    ri_c001 = result.reliability["c001"].reliability_index
    ri_c002 = result.reliability["c002"].reliability_index
    assert ri_c001 > ri_c002


def test_audit_trail_populated(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert meta.audit.policy_version
        assert meta.audit.fusion_algorithm
        assert meta.audit.computed_at_run_id == run_id


# ── 4 new rectified integration tests ────────────────────────────────────────


def test_signal_manifests_in_dataset_json(graph, run_id, test_managers):
    """RECTIFIED (P0-4): Signal manifests must be written to dataset.json."""
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    dataset_path = manifest_mgr.run_dir / "phase8" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for claim_id, meta in data["reliability"].items():
        assert "signal_manifests" in meta, (
            f"signal_manifests missing for claim {claim_id}. "
            "Every claim must have a full derivation trace."
        )
        assert len(meta["signal_manifests"]) > 0


def test_decision_record_in_dataset_json(graph, run_id, test_managers):
    """RECTIFIED (P0-5): ReliabilityDecisionRecord must be in dataset.json."""
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    dataset_path = manifest_mgr.run_dir / "phase8" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for claim_id, meta in data["reliability"].items():
        assert "decision_record" in meta, (
            f"decision_record missing for claim {claim_id}. "
            "Every claim must have a ReliabilityDecisionRecord."
        )
        dr = meta["decision_record"]
        assert "policy_interactions" in dr
        assert "constraints_activated" in dr
        assert "contribution_order" in dr
        assert "final_reliability" in dr


def test_policy_profile_recorded(graph, run_id, test_managers):
    """RECTIFIED (P1-3): PolicyProfile must be recorded in ScoredKnowledgeGraph and dataset."""
    from smriti.scoring.policies import PolicyProfile

    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        policy_profile=PolicyProfile.BALANCED,
    )
    assert result.policy_profile == "balanced"
    for meta in result.reliability.values():
        assert meta.audit.policy_profile == "balanced"


def test_hub_and_bridge_scored_separately(graph, run_id, test_managers):
    """RECTIFIED (P0-3): hub_score and bridge_score must appear in component scores.

    RECTIFIED (P1-4): hub_score/bridge_score are IMPORTANCE-family signals
    (graph centrality), so since the reliability/importance split they live
    in importance_component_scores, not component_scores (which is now
    evidence-family only -- see core.models.ReliabilityMetadata).
    """
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    # At least one claim must have hub_score and bridge_score in its importance_component_scores
    all_signal_names = set()
    for meta in result.reliability.values():
        for comp in meta.importance_component_scores:
            all_signal_names.add(comp.signal_name)
    assert "hub_score" in all_signal_names or "bridge_score" in all_signal_names, (
        "hub_score and bridge_score must appear as separate ComponentScores. "
        "They must not be merged into topology_strength."
    )


# ── P1-4: reliability vs. graph importance split (external "reality check" review) ──


def test_importance_index_in_range(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert 0.0 <= meta.importance_index <= 100.0


def test_reliability_index_excludes_topology_family_signals(graph, run_id, test_managers):
    """RECTIFIED (P1-4): component_scores backing reliability_index must be
    entirely evidence-family -- topology_strength/hub_score/bridge_score
    must never appear there any more (they belong to importance_index)."""
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    importance_only = {"topology_strength", "hub_score", "bridge_score"}
    for meta in result.reliability.values():
        reliability_signal_names = {c.signal_name for c in meta.component_scores}
        assert not (reliability_signal_names & importance_only), (
            f"reliability_index component_scores leaked importance signals: "
            f"{reliability_signal_names & importance_only}"
        )


def test_importance_component_scores_exclude_evidence_family_signals(graph, run_id, test_managers):
    """The reverse of the above: importance_index's components must be
    entirely topology-family, never evidence signals."""
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    evidence_only = {
        "evidence_strength",
        "evidence_independence",
        "source_diversity",
        "conflict_pressure",
        "temporal_stability",
    }
    for meta in result.reliability.values():
        importance_signal_names = {c.signal_name for c in meta.importance_component_scores}
        assert not (importance_signal_names & evidence_only), (
            f"importance_index component_scores leaked evidence signals: "
            f"{importance_signal_names & evidence_only}"
        )


def test_importance_decision_record_populated(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert meta.importance_decision_record is not None
        assert meta.importance_decision_record.final_reliability == meta.importance_index


def test_high_topology_no_longer_caps_reliability_index(graph, run_id, test_managers):
    """RECTIFIED (P1-4): the retired TopologyWithoutEvidenceConstraint used
    to cap reliability_index to 60.0 whenever evidence_strength < 0.20 AND
    topology_strength > 0.80 -- a graph-structure fact suppressing an
    evidence-based score. c001 in the fixture has centrality=0.65 (high-ish
    topology) but real support; this test's real assertion is structural:
    reliability_index's own decision record must never contain
    'topology_without_evidence_cap', regardless of the claim's topology,
    because that constraint is no longer wired into the evidence pipeline."""
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    for meta in result.reliability.values():
        assert not any(
            "topology_without_evidence_cap" in c for c in meta.decision_record.constraints_activated
        )
        assert not any(
            "topology_without_evidence_cap" in c
            for c in meta.importance_decision_record.constraints_activated
        )


def test_importance_index_written_to_dataset_json(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(
        graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr
    )
    dataset_path = manifest_mgr.run_dir / "phase8" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for claim_id, meta in data["reliability"].items():
        assert "importance_index" in meta
        assert "importance_decision_record" in meta
        assert "importance_components" in meta
