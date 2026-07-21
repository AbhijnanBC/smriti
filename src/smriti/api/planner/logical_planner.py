"""
logical_planner.py — LogicalPlanner for Phase 9.

RECTIFIED (P0-2): Produces LogicalPlans only (intent, strategy).
Does NOT consult hardcoded indexed_fields — asks IndexSelector instead.
Optimization (step reordering) is QueryOptimizer's job.

Rules:
    ✅ Deterministic: same request → same plan_id
    ✅ Asks IndexSelector for index availability (never hardcodes)
    ✅ Every plan includes a cost estimate
    ❌ Never executes queries directly
    ❌ Never accesses the ReadStore
    ❌ Never hardcodes indexed field names
"""

from __future__ import annotations

import json
import time
from typing import Tuple
import structlog

from smriti.api.domain.requests import (
    KnowledgeRequest, ClaimRequest, SearchRequest,
    TraversalRequest, StatisticsRequest, ExplanationRequest, ExportRequest,
)
from smriti.api.planner.plan import LogicalPlan, PhysicalPlan, ExecutionStrategy
from smriti.core.models import QueryFamily
from smriti.exceptions import QueryPlanError

logger = structlog.get_logger(__name__)

API_VERSION = "1.0"
PLANNER_VERSION = "1.0"


class LogicalPlanner:
    """
    Produces LogicalPlans from KnowledgeRequests.
    Delegates index selection to IndexSelector — never hardcodes.
    """

    def __init__(self, index_selector=None) -> None:
        """
        Args:
            index_selector: IndexSelector instance. If None, assumes no indexes.
        """
        self._index_selector = index_selector

    def plan(self, request: KnowledgeRequest) -> Tuple[LogicalPlan, float]:
        """
        Produce a LogicalPlan for a KnowledgeRequest.

        Returns:
            (LogicalPlan, planner_ms)
        """
        t0 = time.monotonic()
        logical = self._dispatch(request)
        planner_ms = (time.monotonic() - t0) * 1000

        logger.debug(
            "logical plan produced",
            plan_id=logical.plan_id[:8],
            strategy=logical.strategy.value,
            cacheable=logical.cacheable,
        )
        return logical, planner_ms

    def _dispatch(self, request: KnowledgeRequest) -> LogicalPlan:
        if isinstance(request, ClaimRequest):
            return self._plan_point_lookup(request)
        elif isinstance(request, SearchRequest):
            return self._plan_filter(request)
        elif isinstance(request, TraversalRequest):
            return self._plan_traversal(request)
        elif isinstance(request, StatisticsRequest):
            return self._plan_aggregation(request)
        elif isinstance(request, ExplanationRequest):
            return self._plan_explanation(request)
        elif isinstance(request, ExportRequest):
            return self._plan_export(request)
        else:
            raise QueryPlanError(f"No plan available for: {type(request).__name__}")

    def _plan_point_lookup(self, req: ClaimRequest) -> LogicalPlan:
        query_repr = json.dumps({
            "type": "point", "claim_id": req.claim_id,
            "projection": req.projection.level.value,
            "explain": req.explainability_level.value,
        }, sort_keys=True)
        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.POINT.value,
            query_repr=query_repr,
            strategy=ExecutionStrategy.POINT_LOOKUP,
            cacheable=True,
            projection_level=req.projection.level.value,
            estimated_rows=1,
        )

    def _plan_filter(self, req: SearchRequest) -> LogicalPlan:
        pred_repr = json.dumps(
            sorted([(p.field, p.operator.value, str(p.value)) for p in req.predicates]),
            sort_keys=True,
        )
        sort_repr = f"{req.sort.field}:{req.sort.order.value}"
        query_repr = json.dumps({
            "type": "filter", "predicates": pred_repr, "sort": sort_repr,
            "limit": req.pagination.limit, "offset": req.pagination.offset,
            "projection": req.projection.level.value,
            "text": req.text_contains or "",
        }, sort_keys=True)

        # Ask IndexSelector whether any predicate fields are indexed
        # RECTIFIED: never hardcode indexed_fields here
        has_index = False
        if self._index_selector:
            for p in req.predicates:
                if self._index_selector.has_index(p.field):
                    has_index = True
                    break

        strategy = (
            ExecutionStrategy.INDEXED_FILTER if has_index
            else ExecutionStrategy.FULL_SCAN
        )

        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.FILTER.value,
            query_repr=query_repr,
            strategy=strategy,
            cacheable=True,
            projection_level=req.projection.level.value,
            estimated_rows=req.pagination.limit,
        )

    def _plan_traversal(self, req: TraversalRequest) -> LogicalPlan:
        query_repr = json.dumps({
            "type": "traversal",
            "start": req.start_claim_id,
            "mode": req.navigation_mode.value,
            "depth": req.max_depth,
            "rel_types": sorted(str(r) for r in req.relationship_types),
            "target": req.target_claim_id or "",
        }, sort_keys=True)
        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.TRAVERSAL.value,
            query_repr=query_repr,
            strategy=ExecutionStrategy.GRAPH_TRAVERSAL,
            cacheable=True,
            projection_level=req.projection.level.value,
            estimated_rows=min(50, 2 ** req.max_depth),
        )

    def _plan_aggregation(self, req: StatisticsRequest) -> LogicalPlan:
        query_repr = json.dumps({
            "type": "aggregation",
            "histogram": req.include_histogram,
            "partition_stats": req.include_partition_stats,
            "signal_dist": req.include_signal_distribution,
        }, sort_keys=True)
        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.AGGREGATION.value,
            query_repr=query_repr,
            strategy=ExecutionStrategy.AGGREGATION,
            cacheable=True,
            projection_level=req.projection.level.value,
            estimated_rows=1,
        )

    def _plan_explanation(self, req: ExplanationRequest) -> LogicalPlan:
        query_repr = json.dumps({
            "type": "explanation",
            "claim_id": req.claim_id,
            "level": req.explainability_level.value,
        }, sort_keys=True)
        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.EXPLAINABILITY.value,
            query_repr=query_repr,
            strategy=ExecutionStrategy.POINT_LOOKUP,
            cacheable=True,
            projection_level=req.projection.level.value,
            estimated_rows=1,
        )

    def _plan_export(self, req: ExportRequest) -> LogicalPlan:
        query_repr = json.dumps({
            "type": "export",
            "format": req.export_format.value,
            "include_reliability": req.include_reliability,
        }, sort_keys=True)
        return LogicalPlan(
            plan_id=PhysicalPlan.compute_plan_id(req.run_id, query_repr),
            run_id=req.run_id,
            query_family=QueryFamily.AGGREGATION.value,
            query_repr=query_repr,
            strategy=ExecutionStrategy.FULL_SCAN,
            cacheable=False,
            projection_level=req.projection.level.value,
            estimated_rows=-1,
        )