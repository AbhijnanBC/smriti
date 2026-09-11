"""
engine/execution.py — QueryExecutionEngine for Phase 9.

RECTIFIED: Extracts execution logic from ApplicationService.
QueryExecutionEngine handles caching, service dispatch (via ServiceResolver,
defined in engine/resolver.py), and timing.
"""

from __future__ import annotations

import dataclasses
import time

import structlog
from smriti.api.cache.knowledge_cache import KnowledgeViewCache
from smriti.api.domain.requests import KnowledgeRequest
from smriti.api.domain.responses import KnowledgeResponse
from smriti.api.engine.resolver import ServiceResolver
from smriti.core.models import ExecutionContext

logger = structlog.get_logger(__name__)


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

    def execute(
        self, request: KnowledgeRequest, physical_plan, context: ExecutionContext
    ) -> KnowledgeResponse:
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
            cached_view = self._cache.get_view(
                physical_plan.plan_id, physical_plan.projection_level
            )
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
