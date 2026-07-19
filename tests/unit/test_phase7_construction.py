"""Unit tests for evolution/construction.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Relationship, RelationshipSet, RelationshipType, RelationshipDirection,
    RelationshipEvidence, RelationshipProvenance, RelationshipQuality,
    NLIScores, InferenceMetadata, CandidatePair, SchemaVersionInfo, LifecycleStage,
)
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.construction import run_construction
from smriti.exceptions import GraphConstructionError


def make_claim(claim_id, text="Test.", doc_id="d001"):
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id=doc_id,
        text=text, content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None, assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=doc_id,
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_rel(rel_id, cid_a, cid_b, rel_type, confidence=0.88):
    pair = CandidatePair(claim_id_a=cid_a, claim_id_b=cid_b, cosine_similarity=0.85, candidate_rank=1)
    nli = NLIScores(
        entailment_score=0.05, neutral_score=0.05, contradiction_score=0.90,
        predicted_label="contradiction", raw_confidence=confidence,
    )
    inf = InferenceMetadata(model_name="test-nli")
    evidence = RelationshipEvidence(
        pair=pair, cosine_similarity=0.85, nli_scores=nli,
        calibrated_confidence=confidence, inference_metadata=inf,
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )
    prov = RelationshipProvenance(
        retrieval_backend="faiss_flat_ip", retrieval_version="1.0", index_version="1.0",
        search_parameters=None, classifier_model="test", classifier_version="1.0",
        resolver_version="1.0", calibrator_version="1.0", cosine_similarity=0.85,
        candidate_rank=1, raw_nli_confidence=confidence, calibrated_confidence=confidence,
        config_hash="test", run_id="run1",
    )
    quality = RelationshipQuality(
        cosine_above_threshold=True, nli_above_threshold=True,
        evidence_consistent=True, calibration_applied=False,
    )
    version = SchemaVersionInfo(schema_version="6.0", migration_version="6.0", compatibility_version="6.0")
    return Relationship(
        relationship_id=rel_id, claim_id_a=cid_a, claim_id_b=cid_b,
        relationship_type=rel_type, direction=RelationshipDirection.SYMMETRIC,
        evidence=evidence, quality=quality, provenance=prov, version_info=version,
    )


def make_rel_set(relationships, run_id="run1"):
    return RelationshipSet(
        relationships=relationships, total_candidates=len(relationships),
        total_validated=len(relationships), total_rejected=0,
        rejected_reasons={}, run_id=run_id,
    )


def make_claims_map(*claim_ids):
    return {cid: make_claim(cid) for cid in claim_ids}


def test_constructs_nodes_for_all_claims():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend())
    assert "c001" in result.nodes and "c002" in result.nodes
    assert len(result.nodes) == 2


def test_constructs_edges_for_relationships():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend())
    assert "r1" in result.edges


def test_unknown_relationships_filtered():
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.UNKNOWN),
        make_rel("r2", "c001", "c003", RelationshipType.CONTRADICTS),
    ]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002", "c003"), NetworkXBackend())
    assert "r1" not in result.edges and "r2" in result.edges


def test_missing_claim_raises_construction_error():
    rels = [make_rel("r1", "c001", "c_MISSING", RelationshipType.CONTRADICTS)]
    with pytest.raises(GraphConstructionError):
        run_construction(make_rel_set(rels), {"c001": make_claim("c001")}, NetworkXBackend())


def test_duplicate_claim_ids_produce_one_node():
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c001", "c003", RelationshipType.SUPPORTS),
    ]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002", "c003"), NetworkXBackend())
    assert len(result.nodes) == 3


def test_neutral_filtered_by_default():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.NEUTRAL)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend(), include_neutral=False)
    assert "r1" not in result.edges and result.relationships_filtered == 1


def test_neutral_included_when_configured():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.NEUTRAL)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend(), include_neutral=True)
    assert "r1" in result.edges


def test_empty_relationship_set_produces_empty_graph():
    result = run_construction(make_rel_set([]), {}, NetworkXBackend())
    assert len(result.nodes) == 0 and len(result.edges) == 0