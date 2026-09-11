"""Unit tests for api/cache/knowledge_cache.py."""

import pytest
from smriti.api.cache.knowledge_cache import KnowledgeViewCache


@pytest.fixture
def cache():
    return KnowledgeViewCache(max_size=5, run_id="test_run")


def test_miss_on_empty(cache):
    assert cache.get_view("plan1", "summary") is None


def test_store_and_retrieve(cache):
    cache.set_view("plan1", "summary", "view_data")
    result = cache.get_view("plan1", "summary")
    assert result == "view_data"


def test_different_projection_different_key(cache):
    cache.set_view("plan1", "summary", "summary_view")
    cache.set_view("plan1", "detailed", "detailed_view")
    assert cache.get_view("plan1", "summary") == "summary_view"
    assert cache.get_view("plan1", "detailed") == "detailed_view"


def test_eviction_on_full(cache):
    for i in range(5):
        cache.set_view(f"plan{i}", "summary", f"data{i}")
    assert cache.size == 5
    cache.set_view("plan5", "summary", "data5")
    assert cache.size == 5


def test_clear_cache(cache):
    cache.set_view("plan1", "summary", "data")
    cache.clear()
    assert cache.size == 0
    assert cache.get_view("plan1", "summary") is None


def test_hit_rate_tracking(cache):
    cache.set_view("p1", "summary", "data")
    cache.get_view("p1", "summary")  # hit
    cache.get_view("p2", "summary")  # miss
    assert 0.0 < cache.hit_rate < 1.0


def test_run_scoped_keys(cache):
    """Same plan_id in different run_ids should not collide."""
    cache_a = KnowledgeViewCache(max_size=10, run_id="run_A")
    cache_b = KnowledgeViewCache(max_size=10, run_id="run_B")
    cache_a.set_view("plan1", "summary", "data_A")
    assert cache_b.get_view("plan1", "summary") is None


def test_cache_stores_views_not_dtos():
    """RECTIFIED (P0-4): Cache must store views (not DTOs). Type is opaque — any non-DTO works."""
    cache = KnowledgeViewCache(max_size=10, run_id="run1")
    # Store a ClaimView-like object (not a DTO)

    from smriti.api.domain.views import ClaimView

    view = ClaimView(
        claim_id="c001",
        claim_text="Test.",
        context="",
        document_id="d1",
        source_path="test.md",
        partition_id="p1",
        semantic_role="unclassified",
        reliability_index=80.0,
        uncertainty_score=10.0,
        evidence_completeness=1.0,
        calibration_label="very_high",
        policy_version="1.0",
    )
    cache.set_view("plan1", "standard", view)
    retrieved = cache.get_view("plan1", "standard")
    assert isinstance(retrieved, ClaimView), (
        "Cache must store ClaimView, not ClaimDTO. "
        "DTOs are produced AFTER cache retrieval by DTOMapper."
    )


def test_cache_is_class_knowledge_view_cache():
    """RECTIFIED (P0-4): Cache class must be KnowledgeViewCache, not KnowledgeCache."""
    cache = KnowledgeViewCache(max_size=5, run_id="r1")
    assert (
        "View" in type(cache).__name__
    ), "Cache class must be KnowledgeViewCache to signal View-level storage."
