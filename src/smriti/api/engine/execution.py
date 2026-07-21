"""
engine/execution.py — QueryExecutionEngine and ServiceResolver for Phase 9.

RECTIFIED: Extracts execution logic from ApplicationService.
ServiceResolver resolves a KnowledgeRequest to the appropriate domain service.
QueryExecutionEngine handles caching, service dispatch, and timing.
"""

from __future__ import annotations

import time
import dataclasses
from typing import Type
import structlog

from smriti.core.models import ExecutionContext
from smriti.api.domain.requests import (
    KnowledgeRequest, ClaimRequest, SearchRequest, TraversalRequest,
    StatisticsRequest, ExplanationRequest, ExportRequest,
)
from smriti.api.domain.responses import KnowledgeResponse
from smriti.api.cache.knowledge_cache import KnowledgeViewCache
from smriti.api.services.query_service import QueryService
from smriti.api.services.navigation_service import NavigationService
from smriti.api.services.statistics_service import StatisticsService
from smriti.api.services.explain_service import ExplainabilityService
from smriti.api.services.export_service import ExportService
from smriti.exceptions import QueryPlanError

logger = structlog.get_logger(__name__)


class ServiceResolver:
    """
    Resolves a KnowledgeRequest to the appropriate domain service.

    This decouples the execution engine from the specific request types.
    Adding a new service requires:
        1. Adding the service to the constructor.
        2. Adding a case to resolve().
    No other code changes.
    """

    def __init__(
        self,
        query_service: QueryService,
        navigation_service: NavigationService,
        statistics_service: StatisticsService,
        explain_service: ExplainabilityService,
        export_service: ExportService,
    ):
        self._query_service = query_service
        self._navigation_service = navigation_service
        self._statistics_service = statistics_service
        self._explain_service = explain_service
        self._export_service = export_service

    def resolve(self, request: KnowledgeRequest):
        """
        Return the service that can handle the request.

        Raises:
            QueryPlanError: If no service is registered for the request type.
        """
        if isinstance(request, (ClaimRequest, SearchRequest)):
            return self._query_service
        elif isinstance(request, TraversalRequest):
            return self._navigation_service
        elif isinstance(request, StatisticsRequest):
            return self._statistics_service
        elif isinstance(request, ExplanationRequest):
            return self._explain_service
        elif isinstance(request, ExportRequest):
            return self._export_service
        else:
            raise QueryPlanError(f"No service available for: {type(request).__name__}")


class QueryExecutionEngine:
    """
    Single runtime engine that executes PhysicalPlans.

    Responsibilities:
        - Cache check (view-level, before execution)
        - Service dispatch via ServiceResolver
        - Cache write (after execution)
        - Execution timing and context updates

    This engine is stateless and thread‑safe (read‑only cache operations).
    """

    def __init__(self, resolver: ServiceResolver, cache: KnowledgeViewCache):
        self._resolver = resolver
        self._cache = cache

    def execute(self, request: KnowledgeRequest, physical_plan, context: ExecutionContext) -> KnowledgeResponse:
        """
        Execute a PhysicalPlan for a KnowledgeRequest.

        Args:
            request:        The validated, normalized request.
            physical_plan:  The plan to execute.
            context:        ExecutionContext (mutated and returned via ResponseMeta).

        Returns:
            KnowledgeResponse with data, meta, and cache_hit flag.
        """
        t0 = time.monotonic()

        # 1. Cache lookup (if the plan is cacheable)
        if physical_plan.cacheable:
            cached_view = self._cache.get_view(physical_plan.plan_id, physical_plan.projection_level)
            if cached_view is not None:
                # Cache hit – update context and return
                context = dataclasses.replace(
                    context,
                    cache_hit=True,
                    total_ms=round((time.monotonic() - t0) * 1000, 2),
                )
                # Return the cached response (but update its meta to reflect cache_hit)
                cached_meta = dataclasses.replace(cached_view.meta, cache_hit=True)
                return dataclasses.replace(cached_view, meta=cached_meta)

        # 2. Resolve service and execute
        service = self._resolver.resolve(request)
        response = service.execute(request, physical_plan, context)

        # 3. Cache the response (if cacheable)
        if physical_plan.cacheable:
            self._cache.set_view(physical_plan.plan_id, physical_plan.projection_level, response)

        # 4. Final timing
        total_ms = round((time.monotonic() - t0) * 1000, 2)
        final_meta = dataclasses.replace(response.meta, total_ms=total_ms)
        return dataclasses.replace(response, meta=final_meta)