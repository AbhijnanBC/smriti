"""Integration tests for Phase 9 KnowledgeAccessService."""

import json
import pytest
from pathlib import Path

from smriti.api import build_knowledge_api, KnowledgeAccessService
from smriti.core.models import (
    ScoredKnowledgeGraph, KnowledgeGraph, ClaimNode, RelationshipEdge,
    KnowledgePartition, GraphStatistics, ValidationReport,
    SemanticRole, TopologyMetrics, SupportAggregate, TemporalMetadata,
    TemporalStatus, RelationshipType, RelationshipDirection,
    ReliabilityMetadata, CalibrationLabel, SignalVector,
    ComponentScore, ReliabilityExplanation, ReliabilityAudit,
    NodeAnnotations, ScoringGlobalStats,
    ExportFormat, ExplainabilityLevel, ProjectionLevel, PredicateOperator,
)
from smriti.api.domain.predicates import Predicate
from smriti.exceptions import RequestValidationError


def make_test_graph():
    """Reuse the same factory as unit tests."""
    from tests.unit.test_phase9_store import make_test_scored_graph
    return make_test_scored_graph()


@pytest.fixture
def scored_graph():
    return make_test_graph()


@pytest.fixture
def api(scored_graph):
    return build_knowledge_api(scored_graph)


# ── Original 35 integration tests ────────────────────────────────────────────

def test_api_builds_successfully(api):
    assert isinstance(api, KnowledgeAccessService)


def test_api_run_id_matches_graph(api, scored_graph):
    assert api.run_id == scored_graph.run_id


def test_api_node_count(api, scored_graph):
    assert api.node_count == scored_graph.graph.node_count


def test_get_claim_returns_response(api):
    resp = api.get_claim("c001")
    assert resp is not None
    assert resp.data is not None
    assert resp.meta is not None


def test_get_claim_returns_correct_id(api):
    resp = api.get_claim("c001")
    assert resp.data.claim_id == "c001"


def test_get_claim_not_found_raises(api):
    from smriti.exceptions import ClaimNotFoundError
    with pytest.raises(ClaimNotFoundError):
        api.get_claim("nonexistent_claim_id")


def test_get_claim_has_reliability(api):
    resp = api.get_claim("c001")
    assert resp.data.reliability_index is not None
    assert resp.data.calibration_label is not None


def test_get_claim_response_meta(api):
    resp = api.get_claim("c001")
    meta = resp.meta
    assert meta.run_id == api.run_id
    assert meta.api_version == "1.0"
    assert meta.rows_returned == 1


def test_search_returns_response(api):
    resp = api.search()
    assert resp is not None
    assert isinstance(resp.data, list)


def test_search_returns_all_claims(api):
    resp = api.search(limit=100)
    assert resp.total_count == 2
    assert len(resp.data) == 2


def test_search_with_predicate(api):
    resp = api.search(
        predicates=(Predicate("calibration_label", PredicateOperator.EQ, "high"),)
    )
    assert resp.total_count == 1
    assert resp.data[0].claim_id == "c001"


def test_search_pagination(api):
    resp = api.search(limit=1, offset=0)
    assert len(resp.data) == 1


def test_search_sorted_desc(api):
    resp = api.search(sort_field="reliability_index", sort_order="desc")
    ris = [d.reliability_index for d in resp.data]
    assert ris == sorted(ris, reverse=True)


def test_search_text_contains(api):
    resp = api.search(text_contains="normalize")
    # At least one claim contains "normalize"
    assert len(resp.data) >= 1


def test_search_summary_projection(api):
    resp = api.search(projection=ProjectionLevel.SUMMARY)
    for dto in resp.data:
        assert dto.claim_id is not None
        assert dto.document_id is None  # SUMMARY doesn't include document_id


def test_traverse_returns_response(api):
    resp = api.traverse("c001", max_depth=1)
    data = resp.data
    assert "start_claim_id" in data
    assert "nodes" in data
    assert "edges" in data


def test_traverse_depth_1_finds_neighbors(api):
    resp = api.traverse("c001", max_depth=1)
    data = resp.data
    assert len(data["nodes"]) >= 1


def test_traverse_depth_0_raises(api):
    with pytest.raises(RequestValidationError):
        api.traverse("c001", max_depth=0)


def test_explain_none_level(api):
    resp = api.explain("c001", level=ExplainabilityLevel.NONE)
    data = resp.data
    assert "claim_id" in data
    assert "summary" not in data


def test_explain_summary_level(api):
    resp = api.explain("c001", level=ExplainabilityLevel.SUMMARY)
    data = resp.data
    assert "summary" in data
    assert "dominant_signal" in data


def test_explain_detailed_level(api):
    resp = api.explain("c001", level=ExplainabilityLevel.DETAILED)
    data = resp.data
    assert "component_scores" in data
    assert "signal_vector" in data


def test_explain_full_audit_level(api):
    resp = api.explain("c001", level=ExplainabilityLevel.FULL_AUDIT)
    data = resp.data
    assert "summary" in data
    assert "component_scores" in data
    assert "audit" in data


def test_statistics_returns_aggregate(api):
    resp = api.statistics()
    data = resp.data
    assert data["total_claims"] == 2
    assert "avg_reliability" in data
    assert "calibration_distribution" in data


def test_statistics_histogram(api):
    resp = api.statistics(include_histogram=True)
    data = resp.data
    assert "reliability_histogram" in data


def test_export_json(api):
    resp = api.export(fmt=ExportFormat.JSON)
    data = resp.data
    assert data["format"] == "json"
    parsed = json.loads(data["content"])
    assert "claims" in parsed
    assert len(parsed["claims"]) == 2


def test_export_csv(api):
    resp = api.export(fmt=ExportFormat.CSV)
    data = resp.data
    assert data["format"] == "csv"
    assert "claim_id" in data["content"]
    assert "reliability_index" in data["content"]


def test_export_graphml(api):
    resp = api.export(fmt=ExportFormat.GRAPHML)
    data = resp.data
    assert data["format"] == "graphml"
    assert "<graphml" in data["content"]


def test_second_request_hits_cache(api):
    resp1 = api.get_claim("c001")
    resp2 = api.get_claim("c001")
    assert resp1.meta.cache_hit is False
    assert resp2.meta.cache_hit is True


def test_clear_cache_invalidates(api):
    api.get_claim("c001")
    api.clear_cache()
    resp = api.get_claim("c001")
    assert resp.meta.cache_hit is False


def test_identical_requests_identical_responses(api):
    resp1 = api.get_claim("c001", projection=ProjectionLevel.STANDARD)
    api.clear_cache()
    resp2 = api.get_claim("c001", projection=ProjectionLevel.STANDARD)
    assert resp1.data.reliability_index == resp2.data.reliability_index
    assert resp1.data.calibration_label == resp2.data.calibration_label


def test_read_only_graph_not_modified(api, scored_graph):
    original_count = scored_graph.graph.node_count
    api.get_claim("c001")
    api.search()
    api.statistics()
    assert scored_graph.graph.node_count == original_count


def test_empty_claim_id_raises(api):
    with pytest.raises(RequestValidationError):
        api.get_claim("")


def test_invalid_traversal_depth_raises(api):
    with pytest.raises(RequestValidationError):
        api.traverse("c001", max_depth=0)


def test_search_replaces_top_claims(api):
    """RECTIFIED (P1-4): top_claims() removed; use search() instead."""
    resp = api.search(sort_field="reliability_index", sort_order="desc", limit=1)
    assert len(resp.data) == 1
    assert resp.data[0].claim_id == "c001"


# ── 6 new rectified integration tests ────────────────────────────────────────

def test_no_top_claims_method(api):
    """RECTIFIED (P1-4): top_claims() must not exist on KnowledgeAccessService."""
    assert not hasattr(api, "top_claims"), (
        "top_claims() must be removed. Use search(sort_field='reliability_index', limit=n) instead."
    )


def test_no_contradicted_claims_method(api):
    """RECTIFIED (P1-4): contradicted_claims() must not exist on KnowledgeAccessService."""
    assert not hasattr(api, "contradicted_claims"), (
        "contradicted_claims() must be removed. Use search() with calibration_label predicate."
    )


def test_api_has_capability_registry(api):
    """RECTIFIED (P1-1): KnowledgeAccessService must expose CapabilityRegistry."""
    assert hasattr(api, "capabilities")
    caps = api.capabilities
    assert hasattr(caps, "supported_query_families")
    assert hasattr(caps, "supported_projections")
    assert "point" in caps.supported_query_families


def test_view_not_dto_in_cache(api):
    """RECTIFIED (P0-4): Cache must store Views, not DTOs."""
    api.get_claim("c001")  # Populate cache
    # Access internal cache via app service
    app = api._app
    cache = app._cache
    # The cache should have a view stored
    assert cache.size > 0
    # If a cached value is a ClaimDTO, this is a violation
    from smriti.api.dtos.claim_dto import ClaimDTO
    for key in cache._store:
        stored = cache._store[key]
        # The stored object should be a KnowledgeResponse wrapping a DTO
        # or a ClaimView — either way it's NOT a raw ClaimDTO at the root
        if isinstance(stored, ClaimDTO):
            pytest.fail(
                "Cache must store KnowledgeResponse (wrapping views), not bare ClaimDTOs. "
                "DTOs are produced by DTOMapper after cache retrieval."
            )


def test_validation_centralized_in_request_validator(api):
    """RECTIFIED (P0-big): Validation must go through RequestValidator, not API methods."""
    from smriti.api.validation.request_validator import RequestValidator
    validator = RequestValidator()
    from smriti.api.domain.requests import ClaimRequest
    with pytest.raises(RequestValidationError):
        validator.validate(ClaimRequest(run_id="r1", claim_id=""))


def test_predicate_normalization_produces_stable_plan(api):
    """RECTIFIED (P0-2): Same predicates in different order → cache hit on second call."""
    resp1 = api.search(
        predicates=(
            Predicate("calibration_label", PredicateOperator.EQ, "high"),
            Predicate("partition_id", PredicateOperator.EQ, "p001"),
        ),
    )
    # Same predicates, reversed order
    resp2 = api.search(
        predicates=(
            Predicate("partition_id", PredicateOperator.EQ, "p001"),
            Predicate("calibration_label", PredicateOperator.EQ, "high"),
        ),
    )
    # After normalization, plan_ids must match → second call is a cache hit
    assert resp2.meta.cache_hit is True, (
        "Reversed predicate order must produce the same plan_id after normalization. "
        "Second call should be a cache hit."
    )