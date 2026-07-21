"""
navigation_service.py — Graph traversal service.

RECTIFIED (P0-1): Traversal logic MOVED HERE from ReadStore.
ReadStore.get_adjacency() provides the raw adjacency data.
NavigationService owns BFS and path-finding logic.

RECTIFIED (ExecutionBudget): Uses context.budget.max_traversal_depth
instead of hardcoded MAX_TRAVERSAL_DEPTH.

RECTIFIED (Method naming): execute_traversal renamed to execute for
consistent service interface.
"""

from __future__ import annotations

import time
import dataclasses
from collections import deque
from typing import List, Optional, Dict, Set, Tuple
import structlog

from smriti.api.domain.requests import TraversalRequest
from smriti.api.domain.responses import KnowledgeResponse, make_response_meta
from smriti.api.planner.plan import PhysicalPlan
from smriti.api.store.read_store import ReadStore
from smriti.api.views.claim_view_builder import ClaimViewBuilder
from smriti.api.dtos.mapper import DTOMapper
from smriti.core.models import ExecutionContext, QueryFamily

logger = structlog.get_logger(__name__)


class NavigationService:
    """Graph traversal: local neighborhood, path finding, provenance navigation."""

    def __init__(
        self,
        store: ReadStore,
        view_builder: ClaimViewBuilder,
        mapper: DTOMapper,
    ) -> None:
        self._store = store
        self._view_builder = view_builder
        self._mapper = mapper
        # Load adjacency once from ReadStore (primitive retrieval)
        self._adj = store.get_adjacency()
        self._edge_records = {er["edge_id"]: er for er in store.get_edge_records()}

    # ── RECTIFIED: Renamed from execute_traversal to execute ──────────────
    def execute(
        self, request: TraversalRequest, plan: PhysicalPlan, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        """
        Execute a graph traversal request.

        Args:
            request: TraversalRequest with start node, depth, and filters.
            plan:    PhysicalPlan for this request.
            ctx:     ExecutionContext with budget constraints.

        Returns:
            KnowledgeResponse containing nodes and edges in the traversed neighborhood.
        """
        t0 = time.monotonic()

        # Use budget from context instead of hardcoded constant
        max_allowed_depth = ctx.budget.max_traversal_depth
        depth = min(request.max_depth, max_allowed_depth)

        rel_filter = set(request.relationship_types) if request.relationship_types else None

        # BFS traversal — NavigationService owns this logic (not ReadStore)
        node_records, edge_records = self._bfs_traverse(
            start_claim_id=request.start_claim_id,
            max_depth=depth,
            relationship_type_filter=rel_filter,
        )

        # Build views and DTOs
        node_dtos = []
        for record in node_records:
            rel_record = self._store.fetch_relationship(record["claim_id"])
            view = self._view_builder.build(record, rel_record)
            node_dtos.append(self._mapper.claim_to_dto(view, request.projection.level))

        edge_dicts = [
            {
                "edge_id": er["edge_id"],
                "source": er["source_claim_id"],
                "target": er["target_claim_id"],
                "type": er["relationship_type"],
                "confidence": round(er["calibrated_confidence"], 3),
            }
            for er in edge_records
        ]

        result = {
            "start_claim_id": request.start_claim_id,
            "navigation_mode": request.navigation_mode.value,
            "depth_reached": depth,
            "nodes": [d.to_dict() for d in node_dtos],
            "edges": edge_dicts,
        }

        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=len(node_dtos),
        )
        return KnowledgeResponse(data=result, meta=make_response_meta(ctx))

    def _bfs_traverse(
        self,
        start_claim_id: str,
        max_depth: int,
        relationship_type_filter: Optional[Set[str]],
    ) -> Tuple[List[Dict], List[Dict]]:
        """BFS traversal using adjacency list. Deterministic via sorted neighbor order."""
        if not self._adj.get(start_claim_id) and self._store.lookup(start_claim_id) is None:
            return [], []

        visited_nodes: Set[str] = {start_claim_id}
        visited_edges: Set[str] = set()
        start_record = self._store.lookup(start_claim_id)
        node_records = [start_record] if start_record else []
        edge_records = []

        queue = deque([(start_claim_id, 0)])

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            neighbors = sorted(
                self._adj.get(current_id, []), key=lambda x: x[0]
            )
            for neighbor_id, edge_id, rtype in neighbors:
                if relationship_type_filter and rtype not in relationship_type_filter:
                    continue

                if edge_id not in visited_edges:
                    visited_edges.add(edge_id)
                    er = self._edge_records.get(edge_id)
                    if er:
                        edge_records.append(er)

                if neighbor_id not in visited_nodes:
                    visited_nodes.add(neighbor_id)
                    neighbor_rec = self._store.lookup(neighbor_id)
                    if neighbor_rec:
                        node_records.append(neighbor_rec)
                        queue.append((neighbor_id, depth + 1))

        return node_records, edge_records