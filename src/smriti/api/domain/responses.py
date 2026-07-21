"""responses.py — Response contracts for Phase 9."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import dataclasses

from smriti.core.models import ResponseMeta, ExecutionContext, ExecutionBudget


@dataclass
class KnowledgeResponse:
    """Generic response wrapper. Always includes ResponseMeta."""
    data: Any
    meta: ResponseMeta
    total_count: Optional[int] = None


def make_response_meta(ctx: ExecutionContext) -> ResponseMeta:
    """Build ResponseMeta from a completed ExecutionContext."""
    return ResponseMeta(
        request_id=ctx.request_id,
        run_id=ctx.run_id,
        api_version=ctx.api_version,
        query_family=ctx.query_family,
        execution_plan_id=ctx.plan_id,
        cache_hit=ctx.cache_hit,
        planner_ms=round(ctx.planner_ms, 2),
        execution_ms=round(ctx.execution_ms, 2),
        total_ms=round(ctx.total_ms, 2),
        rows_returned=ctx.rows_returned,
        projection_used=ctx.projection_level,
    )


def make_execution_context(
    run_id: str,
    query_family: str,
    projection_level: str,
    explain_level: int,
    api_version: str = "1.0",
    budget: Optional[ExecutionBudget] = None,
) -> ExecutionContext:
    """Build a fresh ExecutionContext for a new request."""
    if budget is None:
        budget = ExecutionBudget.from_config()
    return ExecutionContext(
        request_id=str(uuid.uuid4()),
        run_id=run_id,
        api_version=api_version,
        query_family=query_family,
        projection_level=projection_level,
        explain_level=explain_level,
        budget=budget,
    )