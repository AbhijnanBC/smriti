"""Unit tests for retrieval/validator.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    CandidatePair, Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    EmbeddedClaim, Embedding, EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, VectorDType, LifecycleStage,
)
from smriti.retrieval.validator import validate_candidates, RejectionReason


def make_claim(claim_id: str, text: str = "Test claim."):
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=text, content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_embedded_claim(claim_id: str, finite: bool = True, dim_ok: bool = True):
    vec = Vector(values=(0.1, 0.2, 0.3, 0.4), dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2", device="cpu", config_hash="hash",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=dim_ok, normalized=True, finite=finite, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


def make_pair(id_a: str, id_b: str, score: float = 0.85):
    a, b = sorted([id_a, id_b])
    return CandidatePair(claim_id_a=a, claim_id_b=b, cosine_similarity=score, candidate_rank=1)


def test_valid_pair_passes():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.85)]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 1
    assert not rejections


def test_self_comparison_rejected():
    claims = {"c001": make_claim("c001")}
    embs = {"c001": make_embedded_claim("c001")}
    pair = CandidatePair(claim_id_a="c001", claim_id_b="c001", cosine_similarity=1.0, candidate_rank=0)
    valid, rejections = validate_candidates([pair], claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.SELF_COMPARISON.value in rejections


def test_missing_claim_rejected():
    claims = {"c001": make_claim("c001")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002")]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.MISSING_CLAIM.value in rejections


def test_invalid_embedding_rejected():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001", finite=False), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002")]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.INVALID_EMBEDDING.value in rejections


def test_below_threshold_rejected():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.60)]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.BELOW_THRESHOLD.value in rejections


def test_empty_input():
    valid, rejections = validate_candidates([], {}, {}, sim_threshold=0.75)
    assert valid == []
    assert not rejections


def test_valid_pair_promoted_to_validated_candidate_lifecycle():
    """RECTIFIED: valid pairs must carry VALIDATED_CANDIDATE lifecycle stage."""
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.85)]
    valid, _ = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert valid[0].lifecycle_stage == LifecycleStage.VALIDATED_CANDIDATE