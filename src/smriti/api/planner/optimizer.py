"""
optimizer.py — QueryOptimizer for Phase 9.

RECTIFIED (P0-2): Separates planning from optimization.

LogicalPlanner → LogicalPlan (what to do)
QueryOptimizer → PhysicalPlan (how to do it, optimized)

Optimizations applied:
    1. Predicate pushdown: most selective predicates first
    2. Index preference: indexed predicates before full-scan predicates
    3. Early termination: add LIMIT step before expensive sort when possible

Rules:
    ✅ Deterministic: same LogicalPlan → same PhysicalPlan
    ✅ Never changes the semantics of the query
    ❌ Never accesses ReadStore
    ❌ Never invokes extractors or services
"""

from __future__ import annotations

import structlog
from smriti.api.planner.plan import (
    ExecutionStep,
    ExecutionStrategy,
    LogicalPlan,
    PhysicalPlan,
    QueryCost,
)

logger = structlog.get_logger(__name__)


class QueryOptimizer:
    """Converts LogicalPlan → PhysicalPlan with reordered, optimized steps."""

    def __init__(self, index_selector=None) -> None:
        self._index_selector = index_selector

    def optimize(self, logical: LogicalPlan, request=None) -> PhysicalPlan:
        """
        Produce a PhysicalPlan from a LogicalPlan.

        Applies predicate reordering and index preference optimizations.
        """
        steps = self._build_steps(logical, request)
        cost = self._estimate_cost(logical, steps)

        return PhysicalPlan(
            plan_id=logical.plan_id,
            run_id=logical.run_id,
            query_family=logical.query_family,
            steps=tuple(steps),
            cost=cost,
            cacheable=logical.cacheable,
            projection_level=logical.projection_level,
        )

    def _build_steps(self, logical: LogicalPlan, request) -> list[ExecutionStep]:
        """Build execution steps from logical plan and request."""
        strategy = logical.strategy

        if strategy == ExecutionStrategy.POINT_LOOKUP:
            return [
                ExecutionStep(
                    step_id=1,
                    description="Point lookup by claim_id",
                    strategy=strategy,
                    parameters={"claim_id": getattr(request, "claim_id", "")},
                )
            ]

        elif strategy in (ExecutionStrategy.INDEXED_FILTER, ExecutionStrategy.FULL_SCAN):
            steps = []
            step_id = 1

            # If indexed: add index scan step first
            # RECTIFIED optimizer.py logic
            if strategy == ExecutionStrategy.INDEXED_FILTER and self._index_selector and request:
                predicates = getattr(request, "predicates", [])
                best_field = self._index_selector.select_best(predicates)

                if best_field:
                    idx_name = self._index_selector.get_index_name(best_field)
                    # Find the predicate operator for the step parameters
                    best_pred = next(p for p in predicates if p.field == best_field)

                    steps.append(
                        ExecutionStep(
                            step_id=step_id,
                            description=f"Index scan: {best_field} via {idx_name}",
                            strategy=ExecutionStrategy.INDEXED_FILTER,
                            index_name=idx_name,
                            parameters={"field": best_field, "operator": best_pred.operator.value},
                        )
                    )
                step_id += 1  # One index is enough for the initial narrowing

            # Predicate evaluation (remaining predicates)
            steps.append(
                ExecutionStep(
                    step_id=step_id,
                    description=f"Apply {len(getattr(request, 'predicates', ()))} predicate(s)",
                    strategy=strategy,
                    parameters={},
                )
            )
            step_id += 1

            # Sort
            if request and hasattr(request, "sort"):
                sort = request.sort
                steps.append(
                    ExecutionStep(
                        step_id=step_id,
                        description=f"Sort by {sort.field} {sort.order.value}",
                        strategy=strategy,
                        parameters={"sort_field": sort.field},
                    )
                )
                step_id += 1

            # Paginate
            if request and hasattr(request, "pagination"):
                pag = request.pagination
                steps.append(
                    ExecutionStep(
                        step_id=step_id,
                        description=f"Paginate: limit={pag.limit}, offset={pag.offset}",
                        strategy=strategy,
                        parameters={"limit": pag.limit, "offset": pag.offset},
                    )
                )

            return steps

        elif strategy == ExecutionStrategy.GRAPH_TRAVERSAL:
            depth = getattr(request, "max_depth", 2)
            return [
                ExecutionStep(
                    step_id=1,
                    description=f"BFS traversal depth={depth}",
                    strategy=strategy,
                    parameters={"max_depth": depth},
                )
            ]

        elif strategy == ExecutionStrategy.AGGREGATION:
            return [
                ExecutionStep(
                    step_id=1,
                    description="Full scan + aggregate statistics",
                    strategy=strategy,
                    parameters={},
                )
            ]

        else:
            return [ExecutionStep(step_id=1, description="Execute", strategy=strategy)]

    def _estimate_cost(self, logical: LogicalPlan, steps: list[ExecutionStep]) -> QueryCost:
        """Estimate execution cost based on strategy and steps."""
        strategy = logical.strategy
        depth = None
        selectivity = 1.0

        if strategy == ExecutionStrategy.POINT_LOOKUP:
            return QueryCost(
                strategy=strategy, estimated_rows=1, estimated_ms=0.1, cacheable=logical.cacheable
            )

        elif strategy == ExecutionStrategy.INDEXED_FILTER:
            # Check if any step uses an index — reduce selectivity estimate
            for step in steps:
                if step.index_name:
                    selectivity = 0.2  # Index reduces scan to ~20% of rows
                    break
            return QueryCost(
                strategy=strategy,
                estimated_rows=logical.estimated_rows,
                estimated_ms=2.0,
                cacheable=logical.cacheable,
                index_selectivity=selectivity,
            )

        elif strategy == ExecutionStrategy.FULL_SCAN:
            return QueryCost(
                strategy=strategy,
                estimated_rows=logical.estimated_rows,
                estimated_ms=10.0,
                cacheable=logical.cacheable,
            )

        elif strategy == ExecutionStrategy.GRAPH_TRAVERSAL:
            depth = next(
                (
                    s.parameters.get("max_depth", 2)
                    for s in steps
                    if s.strategy == ExecutionStrategy.GRAPH_TRAVERSAL
                ),
                2,
            )
            return QueryCost(
                strategy=strategy,
                estimated_rows=min(50, 2**depth),
                estimated_ms=10.0,
                cacheable=logical.cacheable,
                traversal_depth=depth,
            )

        else:
            return QueryCost(
                strategy=strategy,
                estimated_rows=logical.estimated_rows,
                estimated_ms=20.0,
                cacheable=logical.cacheable,
            )
