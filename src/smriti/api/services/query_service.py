"""query_service.py — Point and Filter query services."""

from __future__ import annotations

import time
from typing import List
import structlog

from smriti.api.domain.requests import ClaimRequest, SearchRequest
from smriti.api.domain.responses import KnowledgeResponse, make_response_meta
from smriti.api.planner.plan import PhysicalPlan
from smriti.api.store.read_store import ReadStore
from smriti.api.views.claim_view_builder import ClaimViewBuilder
from smriti.api.dtos.mapper import DTOMapper
from smriti.core.models import ExecutionContext, QueryFamily
from smriti.exceptions import ClaimNotFoundError

logger = structlog.get_logger(__name__)


class QueryService:
    """Point and filter query operations."""

    def __init__(self, store: ReadStore, view_builder: ClaimViewBuilder, mapper: DTOMapper) -> None:
        self._store = store
        self._view_builder = view_builder
        self._mapper = mapper

    def execute_point_lookup(
        self, request: ClaimRequest, plan: PhysicalPlan, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        t0 = time.monotonic()

        record = self._store.lookup(request.claim_id)
        if record is None:
            raise ClaimNotFoundError(
                f"Claim '{request.claim_id}' not found in run '{request.run_id}'"
            )

        rel_record = self._store.fetch_relationship(request.claim_id)
        # RECTIFIED (P0-5): view_builder constructs the view, mapper only maps
        view = self._view_builder.build(record, rel_record)
        dto = self._mapper.claim_to_dto(view, request.projection.level)

        import dataclasses
        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=1,
        )
        return KnowledgeResponse(data=dto, meta=make_response_meta(ctx), total_count=1)

    def execute_filter(
        self, request: SearchRequest, plan: PhysicalPlan, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        t0 = time.monotonic()

        records, total = self._store.scan(
            predicates=list(request.predicates),
            sort=request.sort,
            pagination=request.pagination,
            text_contains=request.text_contains,
        )

        dtos = []
        for record in records:
            rel_record = self._store.fetch_relationship(record["claim_id"])
            view = self._view_builder.build(record, rel_record)
            dto = self._mapper.claim_to_dto(view, request.projection.level)
            dtos.append(dto)

        import dataclasses
        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=len(dtos),
        )
        return KnowledgeResponse(data=dtos, meta=make_response_meta(ctx), total_count=total)

    # ── RECTIFIED: Routing execute method ──────────────────────────────────
    def execute(self, request, plan: PhysicalPlan, ctx: ExecutionContext) -> KnowledgeResponse:
        """
        Route the request to the specific execution method.

        Args:
            request: A KnowledgeRequest subclass (ClaimRequest or SearchRequest).
            plan:    The PhysicalPlan for this request.
            ctx:     ExecutionContext.

        Returns:
            KnowledgeResponse.

        Raises:
            ValueError: If the request type is not supported.
        """
        if isinstance(request, ClaimRequest):
            return self.execute_point_lookup(request, plan, ctx)
        elif isinstance(request, SearchRequest):
            return self.execute_filter(request, plan, ctx)
        raise ValueError(f"QueryService cannot handle request type: {type(request)}")