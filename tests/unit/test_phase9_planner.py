"""Unit tests for api/planner/."""

import pytest
from smriti.api.domain.predicates import Predicate
from smriti.api.domain.requests import (
    ClaimRequest,
    ExplanationRequest,
    SearchRequest,
    StatisticsRequest,
    TraversalRequest,
)
from smriti.api.index.registry import IndexRegistry
from smriti.api.index.selector import IndexSelector
from smriti.api.planner.logical_planner import LogicalPlanner
from smriti.api.planner.normalizer import QueryNormalizer
from smriti.api.planner.optimizer import QueryOptimizer
from smriti.api.planner.plan import ExecutionStrategy
from smriti.core.models import (
    PredicateOperator,
)


@pytest.fixture
def index_registry():
    """Registry with reliability_index_bucket and calibration_label indexed."""
    reg = IndexRegistry()
    reg.register("reliability_index_bucket", {80: ["c001"], 70: ["c002"]})
    reg.register("calibration_label", {"high": ["c001"]})
    return reg


@pytest.fixture
def index_selector(index_registry):
    from smriti.api.index.statistics import IndexStatistics

    stats = IndexStatistics().compute(index_registry)
    return IndexSelector(registry=index_registry, statistics=stats)


@pytest.fixture
def planner(index_selector):
    return LogicalPlanner(index_selector=index_selector)


@pytest.fixture
def optimizer(index_selector):
    return QueryOptimizer(index_selector=index_selector)


@pytest.fixture
def normalizer():
    return QueryNormalizer()


def test_point_lookup_plan(planner, optimizer):
    req = ClaimRequest(run_id="run1", claim_id="c001")
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.POINT_LOOKUP
    assert physical.cacheable is True


def test_filter_plan_indexed_when_index_available(planner, optimizer):
    req = SearchRequest(
        run_id="run1",
        predicates=(Predicate("calibration_label", PredicateOperator.EQ, "high"),),
    )
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.INDEXED_FILTER


def test_filter_plan_full_scan_on_non_indexed_field(planner, optimizer):
    req = SearchRequest(
        run_id="run1",
        predicates=(Predicate("claim_text", PredicateOperator.EQ, "test"),),
    )
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.FULL_SCAN


def test_traversal_plan(planner, optimizer):
    req = TraversalRequest(run_id="run1", start_claim_id="c001", max_depth=2)
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.GRAPH_TRAVERSAL
    assert physical.cost.traversal_depth == 2


def test_statistics_plan(planner, optimizer):
    req = StatisticsRequest(run_id="run1")
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.AGGREGATION
    assert physical.cacheable is True


def test_plan_is_deterministic(planner, optimizer):
    req = ClaimRequest(run_id="run1", claim_id="c001")
    l1, _ = planner.plan(req)
    l2, _ = planner.plan(req)
    assert l1.plan_id == l2.plan_id


def test_different_requests_different_plan_ids(planner):
    req1 = ClaimRequest(run_id="run1", claim_id="c001")
    req2 = ClaimRequest(run_id="run1", claim_id="c002")
    l1, _ = planner.plan(req1)
    l2, _ = planner.plan(req2)
    assert l1.plan_id != l2.plan_id


def test_planner_returns_ms(planner):
    req = ClaimRequest(run_id="run1", claim_id="c001")
    _, ms = planner.plan(req)
    assert ms >= 0.0


def test_explanation_plan(planner, optimizer):
    req = ExplanationRequest(run_id="run1", claim_id="c001")
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert physical.cost.strategy == ExecutionStrategy.POINT_LOOKUP
    assert physical.cacheable is True


def test_planner_never_hardcodes_indexed_fields():
    """RECTIFIED (P0-3): planner with no IndexSelector → all filter = FULL_SCAN."""
    planner_no_idx = LogicalPlanner(index_selector=None)
    optimizer = QueryOptimizer(index_selector=None)
    req = SearchRequest(
        run_id="run1",
        predicates=(Predicate("calibration_label", PredicateOperator.EQ, "high"),),
    )
    logical, _ = planner_no_idx.plan(req)
    physical = optimizer.optimize(logical, req)
    # Without index_selector, strategy falls to FULL_SCAN — no hardcoded fields
    assert physical.cost.strategy == ExecutionStrategy.FULL_SCAN


def test_query_normalizer_makes_order_independent_plan_ids(normalizer, planner):
    """RECTIFIED (P0-2): Different predicate order → same plan_id after normalization."""
    req1 = SearchRequest(
        run_id="run1",
        predicates=(
            Predicate("reliability_index", PredicateOperator.GTE, 80.0),
            Predicate("calibration_label", PredicateOperator.EQ, "high"),
        ),
    )
    req2 = SearchRequest(
        run_id="run1",
        predicates=(
            Predicate("calibration_label", PredicateOperator.EQ, "high"),
            Predicate("reliability_index", PredicateOperator.GTE, 80.0),
        ),
    )
    norm1 = normalizer.normalize(req1)
    norm2 = normalizer.normalize(req2)
    plan1, _ = planner.plan(norm1)
    plan2, _ = planner.plan(norm2)
    assert (
        plan1.plan_id == plan2.plan_id
    ), "Same predicates in different order must produce the same plan_id after normalization."


def test_logical_and_physical_plans_are_separate_objects(planner, optimizer):
    """RECTIFIED (P0-2): LogicalPlan and PhysicalPlan must be separate types."""
    from smriti.api.planner.plan import LogicalPlan, PhysicalPlan

    req = ClaimRequest(run_id="run1", claim_id="c001")
    logical, _ = planner.plan(req)
    physical = optimizer.optimize(logical, req)
    assert isinstance(logical, LogicalPlan)
    assert isinstance(physical, PhysicalPlan)
    assert type(logical) is not type(physical)
