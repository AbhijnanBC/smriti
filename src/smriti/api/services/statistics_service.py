"""
statistics_service.py — Statistics aggregation service.

RECTIFIED (P0-1): Aggregation logic MOVED HERE from ReadStore.
ReadStore only provides stream() of records.
StatisticsService owns aggregation logic via StatisticsViewBuilder.
"""

from __future__ import annotations

import time
import structlog

from smriti.api.domain.requests import StatisticsRequest
from smriti.api.domain.responses import KnowledgeResponse, make_response_meta
from smriti.api.planner.plan import PhysicalPlan
from smriti.api.store.read_store import ReadStore
from smriti.api.views.statistics_view_builder import StatisticsViewBuilder
from smriti.core.models import ExecutionContext, QueryFamily

logger = structlog.get_logger(__name__)


class StatisticsService:
    """Aggregates graph-wide statistics from ReadStore.stream()."""

    def __init__(self, store: ReadStore, view_builder: StatisticsViewBuilder) -> None:
        self._store = store
        self._view_builder = view_builder
        # Load graph metadata once (primitive retrieval)
        self._graph_metadata = getattr(store, "_graph", None)

    def execute_statistics(
        self, request: StatisticsRequest, plan: PhysicalPlan, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        t0 = time.monotonic()

        # Collect graph-wide metadata
        total_edges = (
            self._graph_metadata.statistics.edge_count
            if self._graph_metadata else 0
        )
        total_partitions = (
            self._graph_metadata.statistics.partition_count
            if self._graph_metadata else 0
        )
        total_contradictions = (
            self._graph_metadata.statistics.contradiction_count
            if self._graph_metadata else 0
        )
        partition_data = {}
        if self._graph_metadata and request.include_partition_stats:
            for pid, part in self._graph_metadata.partitions.items():
                partition_data[pid] = {
                    "node_count": part.node_count,
                    "supports_count": part.supports_count,
                }

        view = self._view_builder.build(
            records_iter=self._store.stream(),
            run_id=self._store.run_id,
            total_edges=total_edges,
            total_partitions=total_partitions,
            total_contradictions=total_contradictions,
            partition_data=partition_data,
            include_histogram=request.include_histogram,
            include_partition_stats=request.include_partition_stats,
        )

        # Convert StatisticsView → dict (no full DTO needed for statistics)
        stats_dict = {
            "run_id": view.run_id,
            "total_claims": view.total_claims,
            "total_edges": view.total_edges,
            "total_partitions": view.total_partitions,
            "total_contradictions": view.total_contradictions,
            "avg_reliability": view.avg_reliability,
            "median_reliability": view.median_reliability,
            "high_reliability_count": view.high_reliability_count,
            "low_reliability_count": view.low_reliability_count,
            "avg_uncertainty": view.avg_uncertainty,
            "calibration_distribution": view.calibration_distribution,
            "reliability_histogram": view.reliability_histogram,
            "partition_summaries": view.partition_summaries,
        }

        import dataclasses
        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=1,
        )
        return KnowledgeResponse(data=stats_dict, meta=make_response_meta(ctx))