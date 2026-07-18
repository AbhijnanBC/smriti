"""
Unit tests for embedding/builders.py.
Tests Vector, Embedding, EmbeddingQuality, and EmbeddedClaim construction.
"""

import pytest
import math
from smriti.core.models import (
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, Embedding, EmbeddedClaim,
)
from smriti.embedding.builders import (
    build_vector, build_embedding, build_embedding_quality, build_embedded_claim,
)


@pytest.fixture
def descriptor():
    return EmbeddingModelDescriptor(
        provider="sentence-transformers",
        model_name="all-MiniLM-L6-v2",
        model_revision="default",
        dimension=4,
        model_signature="test_signature",
        embedding_family="SentenceTransformer",
    )


@pytest.fixture
def provenance():
    return EmbeddingProvenance(
        pipeline_version="1.0",
        normalization_mode="l2",
        device="cpu",
        config_hash="test_hash",
    )


# ── build_vector ──────────────────────────────────────────────────────────────

def test_build_vector_returns_vector(descriptor):
    vec = build_vector([0.25, 0.25, 0.25, 0.25], descriptor.dimension, normalized=True)
    assert isinstance(vec, Vector)


def test_build_vector_values_are_tuple(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert isinstance(vec.values, tuple)


def test_build_vector_dimension_matches(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert vec.dimension == 4
    assert len(vec.values) == 4


def test_build_vector_normalized_flag_set(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension, normalized=True)
    assert vec.normalized is True


def test_build_vector_normalized_flag_false_by_default(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension)
    assert vec.normalized is False


def test_build_vector_dimension_mismatch_raises(descriptor):
    """Defensive assertion: dimension mismatch must raise."""
    with pytest.raises(AssertionError):
        build_vector([0.1, 0.2, 0.3], descriptor.dimension)  # 3 values, expected 4


# ── build_embedding ───────────────────────────────────────────────────────────

def test_build_embedding_returns_embedding(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb, Embedding)


def test_build_embedding_has_no_status_field(descriptor, provenance):
    """Embedding must NOT have a status attribute (timeless semantic artifact)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert not hasattr(emb, "status")


def test_build_embedding_vector_is_vector_type(descriptor, provenance):
    """Embedding.vector must be a Vector domain object (not a raw tuple)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb.vector, Vector)


def test_build_embedding_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    with pytest.raises(Exception):
        emb.claim_id = "modified"


# ── build_embedding_quality ───────────────────────────────────────────────────

def test_build_embedding_quality_fresh(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    assert isinstance(quality, EmbeddingQuality)
    assert quality.dimension_ok is True
    assert quality.normalized is True
    assert quality.finite is True
    assert quality.cache_used is False


def test_build_embedding_quality_cached(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=True)
    assert quality.cache_used is True


def test_build_embedding_quality_is_frozen(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    with pytest.raises(Exception):
        quality.dimension_ok = False


# ── build_embedded_claim ──────────────────────────────────────────────────────

def test_build_embedded_claim_returns_embedded_claim(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec, EmbeddedClaim)


def test_build_embedded_claim_has_quality(descriptor, provenance):
    """EmbeddedClaim must carry EmbeddingQuality."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=True)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec.quality, EmbeddingQuality)
    assert ec.quality.cache_used is True


def test_build_embedded_claim_schema_version(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.schema_version == "5.0"


def test_build_embedded_claim_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    with pytest.raises(Exception):
        ec.claim_id = "modified"


def test_embedded_claim_values_property(descriptor, provenance):
    """EmbeddedClaim.values must return the float tuple directly."""
    raw = [0.1, 0.2, 0.3, 0.4]
    vec = build_vector(raw, descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.values == tuple(float(x) for x in raw)