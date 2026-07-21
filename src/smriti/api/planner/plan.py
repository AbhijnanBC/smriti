"""
plan.py — Logical and Physical plan objects.

RECTIFIED (P0-2): Two-phase planning:
    LogicalPlan  = what to do (intent, strategy)
    PhysicalPlan = how to do it (optimized steps, index handles, cost)

The planner produces LogicalPlans.
The optimizer converts LogicalPlan → PhysicalPlan.
The ReadStore executes PhysicalPlans.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ExecutionStrategy(str, Enum):
    POINT_LOOKUP    = "point_lookup"
    INDEXED_FILTER  = "indexed_filter"
    FULL_SCAN       = "full_scan"
    GRAPH_TRAVERSAL = "graph_traversal"
    AGGREGATION     = "aggregation"


@dataclass(frozen=True)
class QueryCost:
    """Estimated cost of executing a PhysicalPlan."""
    strategy: ExecutionStrategy
    estimated_rows: int
    estimated_ms: float
    cacheable: bool
    traversal_depth: Optional[int] = None
    index_selectivity: float = 1.0   # Lower = more selective index


@dataclass(frozen=True)
class ExecutionStep:
    """One step in the physical execution plan."""
    step_id: int
    description: str
    strategy: ExecutionStrategy
    index_name: Optional[str] = None    # Which index to use (from IndexSelector)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LogicalPlan:
    """
    What to do — intent-level plan produced by LogicalPlanner.
    No optimization has been applied yet.
    """
    plan_id: str
    run_id: str
    query_family: str
    query_repr: str               # Normalized canonical query string
    strategy: ExecutionStrategy   # High-level strategy
    cacheable: bool
    projection_level: str
    estimated_rows: int = -1


@dataclass(frozen=True)
class PhysicalPlan:
    """
    How to do it — optimized plan produced by QueryOptimizer.
    Contains concrete execution steps, index handles, and cost estimates.
    """
    plan_id: str                  # Same as LogicalPlan.plan_id
    run_id: str
    query_family: str
    steps: tuple                  # Tuple[ExecutionStep, ...]
    cost: QueryCost
    cacheable: bool
    projection_level: str

    @classmethod
    def compute_plan_id(cls, run_id: str, query_repr: str) -> str:
        """Compute deterministic plan_id from run + normalized query."""
        material = f"{run_id}:{query_repr}"
        return hashlib.sha256(material.encode()).hexdigest()[:16]

    # Backward-compat alias
    @property
    def plan_id_short(self) -> str:
        return self.plan_id[:8]