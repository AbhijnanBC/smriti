"""Unit tests for retrieval/candidate_generator.py."""

import pytest
from smriti.core.models import CandidatePair, EmbeddedClaim
from smriti.retrieval.candidate_generator import CandidateGenerator
from smriti.retrieval.index import EmbeddingIndex, SearchResult
from typing import List, Optional


class MockIndex(EmbeddingIndex):
    def __init__(self, results: dict):
        self._results = results
        self._dimension = 4
        self._size = 0

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def size(self) -> int:
        return self._size

    def add(self, claim_ids, vectors):
        self._size += len(claim_ids)

    def search(self, query_id, query_vector, k, exclude_ids=None):
        return self._results.get(query_id, [])


def make_embedded_claim(claim_id: str, values=(0.1, 0.2, 0.3, 0.4)):
    from smriti.core.models import (
        EmbeddedClaim, Embedding, EmbeddingModelDescriptor,
        EmbeddingProvenance, EmbeddingQuality, Vector, VectorDType,
    )
    vec = Vector(values=tuple(values), dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="test_sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2",
        device="cpu", config_hash="test",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=True, normalized=True, finite=True, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


@pytest.fixture
def generator():
    return CandidateGenerator()


def test_generates_candidate_pairs(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    mock_index = MockIndex({
        "c001": [SearchResult(claim_id="c002", score=0.85, rank=1)],
        "c002": [SearchResult(claim_id="c001", score=0.85, rank=1)],
    })
    candidates = generator.generate([ec_a, ec_b], mock_index)
    assert len(candidates) == 1


def test_self_comparison_excluded(generator):
    ec_a = make_embedded_claim("c001")
    mock_index = MockIndex({
        "c001": [SearchResult(claim_id="c001", score=1.0, rank=1)],
    })
    candidates = generator.generate([ec_a], mock_index)
    assert len(candidates) == 0


def test_symmetric_deduplication(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    mock_index = MockIndex({
        "c001": [SearchResult("c002", 0.90, 1), SearchResult("c003", 0.80, 2)],
        "c002": [SearchResult("c001", 0.90, 1)],
        "c003": [],
    })
    candidates = generator.generate([ec_a, ec_b, ec_c], mock_index)
    pair_keys = {c.pair_key() for c in candidates}
    assert len(pair_keys) == len(candidates)


def test_output_is_sorted(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    mock_index = MockIndex({
        "c001": [SearchResult("c003", 0.85, 1)],
        "c002": [SearchResult("c001", 0.80, 1)],
        "c003": [],
    })
    candidates = generator.generate([ec_a, ec_b, ec_c], mock_index)
    keys = [c.pair_key() for c in candidates]
    assert keys == sorted(keys)


def test_retrieval_provenance_attached(generator):
    """RECTIFIED: CandidatePair must have retrieval provenance fields."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    mock_index = MockIndex({
        "c001": [SearchResult("c002", 0.85, 1)],
        "c002": [],
    })
    candidates = generator.generate([ec_a, ec_b], mock_index)
    assert len(candidates) == 1
    pair = candidates[0]
    assert pair.retrieval_backend is not None
    assert pair.index_version is not None
    assert pair.search_parameters is not None
    assert pair.retrieval_quality is not None