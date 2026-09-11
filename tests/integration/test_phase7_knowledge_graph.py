"""Integration tests for Phase 7 end-to-end."""

import json
from pathlib import Path

import pytest
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    AssertionMetadata,
    CandidatePair,
    Claim,
    ClaimProvenance,
    ExtractionMode,
    InferenceMetadata,
    KnowledgeGraph,
    LifecycleStage,
    NLIScores,
    Relationship,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipProvenance,
    RelationshipQuality,
    RelationshipSet,
    RelationshipType,
    SchemaVersionInfo,
)
from smriti.core.state import StateManager
from smriti.evolution import build_knowledge_graph


def make_claim(cid, text="Test.", doc_id="d001"):
    return Claim(
        claim_id=cid,
        sentence_id="s001",
        document_id=doc_id,
        text=text,
        content_hash=cid[:16],
        context="Python",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001",
            document_id=doc_id,
            source_path=Path("test.md"),
            sentence_context="",
            sentence_position=0,
        ),
        schema_version="4.0",
        rule_version="1.0",
    )


def make_rel(rel_id, cid_a, cid_b, rel_type, confidence=0.88):
    pair = CandidatePair(
        claim_id_a=cid_a, claim_id_b=cid_b, cosine_similarity=0.85, candidate_rank=1
    )
    nli = NLIScores(
        entailment_score=0.05,
        neutral_score=0.05,
        contradiction_score=0.90,
        predicted_label="contradiction",
        raw_confidence=confidence,
    )
    evidence = RelationshipEvidence(
        pair=pair,
        cosine_similarity=0.85,
        nli_scores=nli,
        calibrated_confidence=confidence,
        inference_metadata=InferenceMetadata(model_name="test"),
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )
    prov = RelationshipProvenance(
        retrieval_backend="faiss_flat_ip",
        retrieval_version="1.0",
        index_version="1.0",
        search_parameters=None,
        classifier_model="test",
        classifier_version="1.0",
        resolver_version="1.0",
        calibrator_version="1.0",
        cosine_similarity=0.85,
        candidate_rank=1,
        raw_nli_confidence=confidence,
        calibrated_confidence=confidence,
        config_hash="test",
        run_id="run1",
    )
    quality = RelationshipQuality(
        cosine_above_threshold=True,
        nli_above_threshold=True,
        evidence_consistent=True,
        calibration_applied=False,
    )
    version = SchemaVersionInfo(
        schema_version="6.0", migration_version="6.0", compatibility_version="6.0"
    )
    return Relationship(
        relationship_id=rel_id,
        claim_id_a=cid_a,
        claim_id_b=cid_b,
        relationship_type=rel_type,
        direction=RelationshipDirection.SYMMETRIC,
        evidence=evidence,
        quality=quality,
        provenance=prov,
        version_info=version,
    )


def make_rel_set(rels, run_id="test_run"):
    return RelationshipSet(
        relationships=rels,
        total_candidates=len(rels),
        total_validated=len(rels),
        total_rejected=0,
        rejected_reasons={},
        run_id=run_id,
    )


@pytest.fixture
def run_id():
    return "test_phase7_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Original 12 tests (all preserved) ────────────────────────────────────────


def test_basic_knowledge_graph_construction(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert isinstance(graph, KnowledgeGraph)
    assert graph.node_count == 2 and graph.edge_count == 1


def test_contradiction_produces_two_partitions(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert graph.partition_count == 2 and graph.statistics.contradiction_count == 1


def test_supports_keeps_claims_in_same_partition(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert graph.partition_count == 1
    assert graph.nodes["c001"].partition_id == graph.nodes["c002"].partition_id


def test_knowledge_graph_is_immutable(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    with pytest.raises(Exception):
        graph.run_id = "modified"


def test_validation_report_passes(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert (
        graph.validation_report.is_valid is True and graph.validation_report.total_violations == 0
    )


def test_schema_version_correct(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert graph.schema_version == "7.0"
    for node in graph.nodes.values():
        assert node.schema_version == "7.0"
    for edge in graph.edges.values():
        assert edge.schema_version == "7.0"


def test_nodes_have_semantic_roles(run_id, test_managers):
    from smriti.core.models import SemanticRole

    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    for node in graph.nodes.values():
        assert node.semantic_role is not None and isinstance(node.semantic_role, SemanticRole)


def test_manifest_written(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    manifest_path = manifest_mgr.run_dir / "phase7" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["phase"] == 7 and manifest["status"] == "success"


def test_dataset_json_written(run_id, test_managers, tmp_path):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase7" / "dataset.json"
    assert dataset_path.exists()
    data = json.loads(dataset_path.read_text())
    assert all(k in data for k in ("graph_id", "nodes", "edges", "partitions"))


def test_pipeline_state_updated(run_id, test_managers):
    _, state_mgr = test_managers
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, _ = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    state = state_mgr.load()
    assert state is not None and 7 in state.completed_phases


def test_deterministic_construction(run_id, test_managers, tmp_path):
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c001", "c003", RelationshipType.SUPPORTS),
    ]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002"), "c003": make_claim("c003")}
    manifest_mgr, state_mgr = test_managers
    graph1 = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    manifest_mgr2 = ManifestManager(run_id=f"{run_id}_2", artifacts_dir=tmp_path / "artifacts2")
    state_mgr2 = StateManager(state_file=tmp_path / "state2.json")
    graph2 = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr2, state_mgr2
    )
    assert graph1.graph_id == graph2.graph_id
    assert graph1.node_count == graph2.node_count
    assert graph1.partition_count == graph2.partition_count


def test_unknown_relationships_excluded_from_graph(run_id, test_managers):
    from smriti.core.models import RelationshipType

    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.UNKNOWN),
        make_rel("r2", "c001", "c003", RelationshipType.CONTRADICTS),
    ]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002"), "c003": make_claim("c003")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    for edge in graph.edges.values():
        assert edge.relationship_type != RelationshipType.UNKNOWN


def test_realistic_knowledge_graph(run_id, test_managers):
    """Full test with realistic structure."""
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c003", "c001", RelationshipType.SUPPORTS),
        make_rel("r3", "c004", "c001", RelationshipType.REFINES),
    ]
    claims = {
        "c001": make_claim("c001", "Always normalize features before PCA."),
        "c002": make_claim("c002", "Normalization before PCA is often unnecessary."),
        "c003": make_claim("c003", "Use StandardScaler for consistent preprocessing."),
        "c004": make_claim("c004", "Normalization improves PCA convergence on numerical data."),
    }
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    assert graph.node_count == 4 and graph.edge_count == 3
    assert graph.statistics.contradiction_count == 1
    node_c001 = graph.nodes["c001"]
    node_c002 = graph.nodes["c002"]
    assert node_c001.partition_id != node_c002.partition_id
    partition_c001 = graph.partitions[node_c001.partition_id]
    assert "c003" in partition_c001.node_ids and "c004" in partition_c001.node_ids
    assert node_c001.support_aggregate is not None
    assert node_c001.support_aggregate.support_count >= 1
    assert graph.schema_version == "7.0" and graph.validation_report.is_valid
    for node in graph.nodes.values():
        assert node.semantic_role is not None


# ── 3 new rectified integration tests ────────────────────────────────────────


def test_shared_support_target_partitioned_correctly(run_id, test_managers):
    """
    RECTIFIED (P0-1): Critical test — shared SUPPORTS target must not
    merge contradicting nodes into the same partition.

    A SUPPORTS X, C SUPPORTS X, A CONTRADICTS C.
    A and C must be in DIFFERENT partitions.
    """
    rels = [
        make_rel("r1", "A", "X", RelationshipType.SUPPORTS),
        make_rel("r2", "C", "X", RelationshipType.SUPPORTS),
        make_rel("r3", "A", "C", RelationshipType.CONTRADICTS),
    ]
    claims = {
        "A": make_claim("A", "Claim A."),
        "X": make_claim("X", "Claim X."),
        "C": make_claim("C", "Claim C."),
    }
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )

    partition_of_A = graph.nodes["A"].partition_id
    partition_of_C = graph.nodes["C"].partition_id
    assert partition_of_A != partition_of_C, (
        "A and C contradict each other. Even though they both support X, "
        "they must be in different partitions."
    )


def test_stable_partition_label_in_dataset_json(run_id, test_managers):
    """RECTIFIED (P2-5): stable_partition_label must be written to dataset.json."""
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase7" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for partition_data in data["partitions"].values():
        assert (
            "stable_partition_label" in partition_data
        ), "stable_partition_label must be written to dataset.json for incremental comparison."


def test_bridge_nodes_counted_in_statistics(run_id, test_managers):
    """RECTIFIED (P0-3): bridge_nodes stat must use articulation-point count."""
    # A → B → C: B is an articulation point
    rels = [
        make_rel("r1", "A", "B", RelationshipType.SUPPORTS),
        make_rel("r2", "B", "C", RelationshipType.SUPPORTS),
    ]
    claims = {"A": make_claim("A"), "B": make_claim("B"), "C": make_claim("C")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(
        make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr
    )
    # B is the true articulation point
    assert (
        graph.statistics.bridge_nodes >= 1
    ), "B is an articulation point. bridge_nodes stat must reflect this."
