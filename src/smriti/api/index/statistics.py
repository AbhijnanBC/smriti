"""index/statistics.py — IndexStatistics for Phase 9."""

from __future__ import annotations

from dataclasses import dataclass

from smriti.api.index.registry import IndexRegistry


@dataclass(frozen=True)
class IndexStats:
    """Statistics for one index."""

    field_name: str
    unique_values: int
    total_entries: int
    avg_entries_per_value: float


class IndexStatistics:
    """Computes and caches statistics about built indexes."""

    def compute(self, registry: IndexRegistry) -> dict[str, IndexStats]:
        stats = {}
        for field in registry.indexed_fields:
            idx = registry._indexes.get(field, {})
            n_values = len(idx)
            n_entries = sum(len(v) for v in idx.values())
            stats[field] = IndexStats(
                field_name=field,
                unique_values=n_values,
                total_entries=n_entries,
                avg_entries_per_value=n_entries / max(1, n_values),
            )
        return stats
