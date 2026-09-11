"""Unit tests for retrieval/builder.py."""

import dataclasses

import pytest
from smriti.core.models import (
    CandidatePair,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    Relationship,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipType,
)
from smriti.retrieval.builder import build_relationship, build_relationship_set


def make_evidence(claim_id_a="c001", claim_id_b="c002"):
    pair = CandidatePair(
        claim_id_a=claim_id_a,
        claim_id_b=claim_id_b,
        cosine_similarity=0.85,
        candidate_rank=1,
    )
    nli_scores = NLIScores(
        entailment_score=0.05,
        neutral_score=0.03,
        contradiction_score=0.92,
        predicted_label="contradiction",
        raw_confidence=0.92,
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=0.85,
        nli_scores=nli_scores,
        calibrated_confidence=0.88,  # Slightly different from raw (calibrated)
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


def test_build_relationship_returns_relationship():
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert isinstance(rel, Relationship)


def test_relationship_id_is_16_chars():
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert len(rel.relationship_id) == 16


def test_relationship_id_is_deterministic():
    evidence = make_evidence()
    rel1 = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    rel2 = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel1.relationship_id == rel2.relationship_id


def test_relationship_is_frozen():
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        rel.claim_id_a = "modified"


def test_relationship_provenance_populated():
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel.provenance is not None
    assert rel.provenance.run_id == "run1"
    assert rel.provenance.config_hash == "hash"


def test_relationship_schema_version():
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel.schema_version == "7.0"


def test_relationship_set_contradictions_property():
    e1 = make_evidence("c001", "c002")
    e2 = make_evidence("c003", "c004")
    rel1 = build_relationship(
        e1, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1"
    )
    rel2 = build_relationship(
        e2, RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B, 0.80, "hash", "run1"
    )
    rel_set = build_relationship_set(
        relationships=[rel1, rel2],
        total_candidates=10,
        total_validated=5,
        total_rejected=5,
        rejected_reasons={"below_threshold": 5},
        run_id="run1",
    )
    assert len(rel_set.contradictions) == 1
    assert len(rel_set.supports) == 1


def test_schema_version_info_populated():
    """RECTIFIED: SchemaVersionInfo must be populated on every Relationship."""
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel.version_info is not None
    assert rel.version_info.schema_version == "7.0"
    assert rel.version_info.migration_version == "7.0"
    assert rel.version_info.compatibility_version == "7.0"


def test_calibration_applied_flag_set_when_scores_differ():
    """RECTIFIED: calibration_applied must be True when raw != calibrated."""
    evidence = make_evidence()  # raw_confidence=0.92, calibrated_confidence=0.88
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel.quality.calibration_applied is True


def test_lifecycle_stage_is_relationship():
    """RECTIFIED: built relationships must carry RELATIONSHIP lifecycle stage."""
    evidence = make_evidence()
    rel = build_relationship(
        evidence,
        RelationshipType.CONTRADICTS,
        RelationshipDirection.SYMMETRIC,
        0.80,
        "hash",
        "run1",
    )
    assert rel.lifecycle_stage == LifecycleStage.RELATIONSHIP
