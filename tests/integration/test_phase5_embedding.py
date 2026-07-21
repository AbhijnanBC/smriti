"""
Integration test for Phase 5 end-to-end.

Tests the complete pipeline:
    List[Claim] → embed_claims() → Phase5Result

Uses a mock embedder so tests run without sentence-transformers installed.
All assertions reflect the rectified API:
    - EmbeddedClaim.vector returns Vector (not tuple)
    - EmbeddedClaim.values returns tuple of floats
    - EmbeddedClaim.quality is EmbeddingQuality
    - Embedding has no status field
"""

import pytest
import math
import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Modality, EmbeddedClaim,
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.embedding import embed_claims, Phase5Result
from smriti.embedding.embedder import BaseEmbedder, EmbedderCapabilities
from smriti.embedding.models import EmbeddingStatus 


# ── Mock embedder ─────────────────────────────────────────────────────────────

class MockEmbedder(BaseEmbedder):
    """Mock embedder that returns deterministic fake vectors."""

    DIMENSION = 4

    def __init__(self):
        self._descriptor = EmbeddingModelDescriptor(
            provider="mock",
            model_name="mock-embedder",
            model_revision="test",
            dimension=self.DIMENSION,
            model_signature="mock_signature_abc123",
            embedding_family="Mock",
        )

    @property
    def descriptor(self) -> EmbeddingModelDescriptor:
        return self._descriptor

    @property
    def capabilities(self) -> EmbedderCapabilities:
        return EmbedderCapabilities(
            supports_batching=True,
            supports_instruction_prefix=False,
            supports_multilingual=False,
            supports_long_context=False,
        )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Deterministic: hash of text → 4 floats."""
        import hashlib
        results = []
        for text in texts:
            h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
            vector = [(h >> (i * 8) & 0xFF) / 255.0 for i in range(self.DIMENSION)]
            if all(v == 0.0 for v in vector):
                vector[0] = 0.1
            results.append(vector)
        return results


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_embedder():
    return MockEmbedder()


@pytest.fixture
def run_id():
    return "test_phase5_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


def make_claim(
    claim_id: str,
    text: str,
    context: str = "",
    document_id: str = "doc001",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id=document_id,
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=document_id,
            source_path=Path("test.md"), sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=claim_id[:16],
        rule_version="1.0",
    )


def run_embedding(mock_embedder, claims, run_id, test_managers, **kwargs):
    manifest_mgr, state_mgr = test_managers
    return embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=mock_embedder,
        **kwargs,
    )


# ── Basic production ──────────────────────────────────────────────────────────

def test_empty_claims_produces_empty_result(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [], run_id, test_managers)
    assert isinstance(result, Phase5Result)
    assert result.total_embedded == 0


def test_single_claim_produces_embedded_claim(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.failed == 0


def test_embedded_claims_reference_correct_claim_ids(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    ids = {ec.claim_id for ec in result.embedded_claims}
    assert ids == {"c001", "c002"}


def test_empty_text_claim_is_skipped(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Valid claim."), make_claim("c002", "   ")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.skipped == 1


# ── Immutability and purity ───────────────────────────────────────────────────

def test_embedded_claims_are_immutable(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    with pytest.raises(Exception):
        result.embedded_claims[0].claim_id = "modified"


def test_original_claims_not_modified(mock_embedder, run_id, test_managers):
    claim = make_claim("c001", "Python is fast.")
    original_text = claim.text
    run_embedding(mock_embedder, [claim], run_id, test_managers)
    assert claim.text == original_text


def test_embedding_has_no_status_field(mock_embedder, run_id, test_managers):
    """Critical fix: Embedding must not have a status field."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert not hasattr(ec.embedding, "status"), (
        "Embedding should not have status — it's a pure semantic artifact"
    )


# ── EmbeddingQuality ──────────────────────────────────────────────────────────

def test_embedded_claim_has_quality(mock_embedder, run_id, test_managers):
    """EmbeddedClaim must carry EmbeddingQuality."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.quality, EmbeddingQuality)


def test_quality_fresh_embedding(mock_embedder, run_id, test_managers):
    """Fresh embedding: cache_used=False, normalized=True."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.quality.cache_used is False
    assert ec.quality.normalized is True
    assert ec.quality.finite is True
    assert ec.quality.dimension_ok is True


# ── Vector domain object ──────────────────────────────────────────────────────

def test_vector_is_vector_type(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.vector must return a Vector domain object."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector, Vector)


def test_vector_values_is_tuple(mock_embedder, run_id, test_managers):
    """Vector.values must be an immutable tuple."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector.values, tuple)


def test_embedded_claim_values_shortcut(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.values must return the same as ec.vector.values."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.values == ec.vector.values


def test_vector_has_correct_dimension(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.dimension == MockEmbedder.DIMENSION
        assert ec.vector.dimension == MockEmbedder.DIMENSION


def test_normalized_vectors_are_unit_length(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        norm = math.sqrt(sum(x * x for x in ec.values))
        assert abs(norm - 1.0) < 1e-5, f"Norm was {norm}"


# ── Schema and provenance ─────────────────────────────────────────────────────

def test_schema_version_is_50(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.schema_version == "5.0"


def test_embedding_descriptor_family(mock_embedder, run_id, test_managers):
    """EmbeddingModelDescriptor must include embedding_family."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert hasattr(ec.embedding.descriptor, "embedding_family")
    assert ec.embedding.descriptor.embedding_family == "Mock"


# ── Batch retry ───────────────────────────────────────────────────────────────

def test_batch_failure_triggers_individual_retry(run_id, test_managers):
    """
    When a batch fails, the pipeline must retry each claim individually.
    Only the claims that individually fail are marked as failed.
    """
    call_count = {"n": 0}

    class FailFirstBatchEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            call_count["n"] += 1
            # Fail on the first call (the full batch)
            if call_count["n"] == 1 and len(texts) > 1:
                raise RuntimeError("Simulated batch failure")
            return super().encode_batch(texts)

    failing_embedder = FailFirstBatchEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]

    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=failing_embedder,
    )

    # Both claims should succeed via individual retry
    assert result.total_embedded == 2
    # A warning should have been added about the batch failure
    assert any("batch" in w.lower() for w in result.warnings)


def test_one_bad_vector_does_not_abort_batch(run_id, test_managers):
    """NaN in one vector must not fail the other claims in the batch."""
    class NaNSecondEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            vectors = super().encode_batch(texts)
            if len(vectors) > 1:
                vectors[1] = [float("nan")] * self.DIMENSION
            return vectors

    embedder = NaNSecondEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]
    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=embedder,
    )

    assert result.total_embedded >= 1  # c001 succeeds
    assert result.stats.failed >= 1    # c002 fails validation


# ── Warnings and errors ───────────────────────────────────────────────────────

def test_result_has_warnings_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose a warnings list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "warnings")
    assert isinstance(result.warnings, list)


def test_result_has_errors_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose an errors list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "errors")
    assert isinstance(result.errors, list)


# ── Artifacts ─────────────────────────────────────────────────────────────────

def test_dataset_json_written(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()


def test_dataset_json_has_quality_section(mock_embedder, run_id, test_managers):
    """dataset.json must include the quality diagnostic block."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    assert len(records) == 1
    record = records[0]
    assert "quality" in record
    assert "dimension_ok" in record["quality"]
    assert "normalized" in record["quality"]
    assert "cache_used" in record["quality"]


def test_dataset_json_no_status_field_from_embedding(mock_embedder, run_id, test_managers):
    """
    dataset.json 'status' field is derived from quality.cache_used,
    not from an Embedding.status attribute.
    """
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    record = records[0]
    # Status is "success" for fresh, "cached" for cache hits
    assert record["status"] in ("success", "cached")


def test_manifest_has_cache_lifecycle_metrics(mock_embedder, run_id, test_managers):
    """manifest.json must include cache lifecycle counters."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    manifest = json.loads(result.manifest_path.read_text())
    assert "cache_entries_reused" in manifest.get("outputs", {})
    assert "cache_entries_regenerated" in manifest.get("outputs", {})


def test_pipeline_state_updated(mock_embedder, run_id, test_managers):
    _, state_mgr = test_managers
    run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    state = state_mgr.load()
    assert 5 in state.completed_phases


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_claims_same_vectors(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    manifest_mgr, state_mgr = test_managers

    r1 = embed_claims(claims=claims, run_id=run_id, manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)
    r2 = embed_claims(claims=claims, run_id=run_id + "_2", manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)

    v1 = {ec.claim_id: ec.values for ec in r1.embedded_claims}
    v2 = {ec.claim_id: ec.values for ec in r2.embedded_claims}
    assert v1 == v2


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_has_throughput_field(mock_embedder, run_id, test_managers):
    """Phase5Stats must include vectors_per_second."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "vectors_per_second")
    assert result.stats.vectors_per_second >= 0.0


def test_stats_has_cache_lifecycle_fields(mock_embedder, run_id, test_managers):
    """Phase5Stats must include cache lifecycle counts."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "cache_entries_reused")
    assert hasattr(result.stats, "cache_entries_regenerated")