"""
views/statistics_view_builder.py — StatisticsViewBuilder.

RECTIFIED (P0-1): Statistics computation moved out of ReadStore.
StatisticsService uses this builder (which reads from ReadStore.stream())
rather than calling ReadStore.aggregate_statistics().
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Iterator
from typing import Any

from smriti.api.domain.views import StatisticsView


class StatisticsViewBuilder:
    """Computes StatisticsView from a stream of claim records."""

    def build(
        self,
        records_iter: Iterator[dict[str, Any]],
        run_id: str,
        total_edges: int,
        total_partitions: int,
        total_contradictions: int,
        partition_data: dict[str, Any] | None = None,
        include_histogram: bool = True,
        include_partition_stats: bool = True,
    ) -> StatisticsView:
        """Build a StatisticsView by streaming claim records."""
        records = list(records_iter)
        if not records:
            return self._empty_view(run_id, total_edges, total_partitions, total_contradictions)

        ri_values = [r["reliability_index"] for r in records]
        unc_values = [r["uncertainty_score"] for r in records]

        calibration_dist: dict[str, int] = defaultdict(int)
        for r in records:
            calibration_dist[r["calibration_label"]] += 1

        histogram: list[tuple[str, int]] = []
        if include_histogram:
            for bucket_start in range(0, 100, 10):
                bucket_end = bucket_start + 10
                count = sum(1 for v in ri_values if bucket_start <= v < bucket_end)
                histogram.append((f"{bucket_start}-{bucket_end}", count))
            # Fix last bucket to include 100
            histogram[-1] = ("90-100", sum(1 for v in ri_values if 90 <= v <= 100))

        partition_summaries = []
        if include_partition_stats and partition_data:
            for pid, pinfo in partition_data.items():
                partition_ri = [
                    r["reliability_index"] for r in records if r.get("partition_id") == pid
                ]
                partition_summaries.append(
                    {
                        "partition_id": pid,
                        "node_count": pinfo.get("node_count", 0),
                        "avg_reliability": (
                            round(statistics.mean(partition_ri), 2) if partition_ri else 0.0
                        ),
                        "supports_count": pinfo.get("supports_count", 0),
                    }
                )
            partition_summaries.sort(key=lambda p: p["avg_reliability"], reverse=True)

        return StatisticsView(
            run_id=run_id,
            total_claims=len(records),
            total_edges=total_edges,
            total_partitions=total_partitions,
            total_contradictions=total_contradictions,
            avg_reliability=round(statistics.mean(ri_values), 2),
            median_reliability=round(statistics.median(ri_values), 2),
            high_reliability_count=sum(1 for v in ri_values if v >= 65),
            low_reliability_count=sum(1 for v in ri_values if v < 45),
            avg_uncertainty=round(statistics.mean(unc_values), 2),
            calibration_distribution=dict(calibration_dist),
            reliability_histogram=histogram,
            partition_summaries=partition_summaries,
        )

    def _empty_view(self, run_id, edges, partitions, contradictions) -> StatisticsView:
        return StatisticsView(
            run_id=run_id,
            total_claims=0,
            total_edges=edges,
            total_partitions=partitions,
            total_contradictions=contradictions,
            avg_reliability=0.0,
            median_reliability=0.0,
            high_reliability_count=0,
            low_reliability_count=0,
            avg_uncertainty=0.0,
            calibration_distribution={},
            reliability_histogram=[],
            partition_summaries=[],
        )
