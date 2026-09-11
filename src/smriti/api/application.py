"""
application.py — ApplicationService for Phase 9.

RECTIFIED (P0-big): ApplicationService sits between the thin façade
(KnowledgeAccessService) and the domain services.

Architecture:
    KnowledgeAccessService (thin façade)
        ↓
    ApplicationService (orchestration + caching)
        ↓
    QueryNormalizer → LogicalPlanner → QueryOptimizer → PhysicalPlan
        ↓
    QueryExecutionEngine → ServiceResolver → Domain Services → ReadStore

KnowledgeAccessService is thin:
    - Builds requests from kwargs
    - Calls ApplicationService.execute(request)
    - Returns result

ApplicationService owns:
    - Request validation
    - Request normalization
    - Planning pipeline (logical → physical)
    - ExecutionContext lifecycle (with ExecutionBudget)
    - Delegates execution to QueryExecutionEngine
    - Cache clearing

No business logic lives in the façade.
"""

from __future__ import annotations

import dataclasses
import time

import structlog

from smriti.api.domain.requests import (
    ClaimRequest,
    ExplanationRequest,
    ExportRequest,
    KnowledgeRequest,
    SearchRequest,
    StatisticsRequest,
    TraversalRequest,
)
from smriti.api.domain.responses import KnowledgeResponse, make_execution_context
from smriti.api.engine.execution import QueryExecutionEngine
from smriti.api.planner.logical_planner import LogicalPlanner
from smriti.api.planner.normalizer import QueryNormalizer
from smriti.api.planner.optimizer import QueryOptimizer
from smriti.api.store.snapshot import KnowledgeSnapshot
from smriti.api.validation.request_validator import RequestValidator
from smriti.core.models import ExecutionBudget, QueryFamily

logger = structlog.get_logger(__name__)

API_VERSION = "1.0"


class ApplicationService:
    """
    Orchestrates the complete request pipeline.

    This is the single place where:
        1. Validation runs
        2. Normalization runs
        3. Planning (logical + physical) runs
        4. ExecutionContext is built (with execution budget)
        5. Execution is delegated to QueryExecutionEngine
        6. Response is assembled (final total_ms)
    """

    def __init__(
        self,
        validator: RequestValidator,
        normalizer: QueryNormalizer,
        logical_planner: LogicalPlanner,
        optimizer: QueryOptimizer,
        snapshot: KnowledgeSnapshot,
        engine: QueryExecutionEngine,
    ) -> None:
        """
        Args:
            validator:       Centralized request validator.
            normalizer:      Canonicalizes requests (order-independent planning).
            logical_planner: Produces LogicalPlan from request.
            optimizer:       Converts LogicalPlan → PhysicalPlan.
            snapshot:        Immutable data layer (store, index registry, cache, schema, run_id).
            engine:          Runtime execution engine (caching, service dispatch, timing).
        """
        self._validator = validator
        self._normalizer = normalizer
        self._logical_planner = logical_planner
        self._optimizer = optimizer
        self._snapshot = snapshot
        self._engine = engine

    def execute(self, request: KnowledgeRequest) -> KnowledgeResponse:
        """
        Execute one request through the full pipeline.

        Returns:
            KnowledgeResponse with ResponseMeta (includes total pipeline time).
        """
        pipeline_start = time.monotonic()

        # Stage 1: Validate
        self._validator.validate(request)

        # Stage 2: Normalize (order-independent)
        request = self._normalizer.normalize(request)

        # Stage 3: Logical planning
        query_family = self._determine_family(request)
        logical, planner_ms = self._logical_planner.plan(request)

        # Stage 4: Physical planning (optimization)
        physical = self._optimizer.optimize(logical, request)

        # Stage 4b: Build ExecutionContext with budget from config
        ctx = make_execution_context(
            run_id=self._snapshot.run_id,
            query_family=query_family,
            projection_level=physical.projection_level,
            explain_level=request.explainability_level.value,
            api_version=API_VERSION,
            budget=ExecutionBudget.from_config(),
        )
        ctx = dataclasses.replace(ctx, plan_id=physical.plan_id, planner_ms=round(planner_ms, 2))

        # Stages 5–9: Delegate to QueryExecutionEngine (caching, dispatch, execution timing)
        response = self._engine.execute(request, physical, ctx)

        # Stage 10: Final total_ms (overwrite to include full pipeline duration)
        final_meta = dataclasses.replace(
            response.meta,
            total_ms=round((time.monotonic() - pipeline_start) * 1000, 2),
        )
        return dataclasses.replace(response, meta=final_meta)

    def _determine_family(self, request: KnowledgeRequest) -> str:
        """Map request type to QueryFamily string."""
        mapping = {
            ClaimRequest: QueryFamily.POINT.value,
            SearchRequest: QueryFamily.FILTER.value,
            TraversalRequest: QueryFamily.TRAVERSAL.value,
            StatisticsRequest: QueryFamily.AGGREGATION.value,
            ExplanationRequest: QueryFamily.EXPLAINABILITY.value,
            ExportRequest: QueryFamily.AGGREGATION.value,
        }
        return mapping.get(type(request), "unknown")

    def clear_cache(self) -> None:
        """Clear the knowledge view cache."""
        self._snapshot.cache.clear()
