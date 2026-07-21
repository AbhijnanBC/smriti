"""
index/selector.py — IndexSelector for Phase 9.

RECTIFIED (P0-3, Cost-Based): The planner asks IndexSelector — never hardcodes field names.
select_best() evaluates IndexStatistics to pick the most selective (lowest-cost) index.
"""

from __future__ import annotations

from typing import Optional, List
import structlog

from smriti.api.index.registry import IndexRegistry
from smriti.api.index.statistics import IndexStatistics, IndexStats
from smriti.api.domain.predicates import Predicate

logger = structlog.get_logger(__name__)


class IndexSelector:
    """
    Provides index selection and cost estimation for the planner.

    RECTIFIED (P0-3): The planner asks IndexSelector — never hardcodes field names.
    RECTIFIED (Cost-Based): select_best() uses IndexStatistics to pick the most selective index.
    """

    def __init__(self, registry: IndexRegistry, statistics: IndexStatistics) -> None:
        self._registry = registry
        self._statistics = statistics

    def has_index(self, field_name: str) -> bool:
        """Return True if there is an index for this field."""
        return self._registry.has_index(field_name)

    def get_index_name(self, field_name: str) -> Optional[str]:
        """Return the index name for a field, or None."""
        if self._registry.has_index(field_name):
            return f"idx_{field_name}"
        return None

    def select_best(self, predicates: List[Predicate]) -> Optional[str]:
        """
        Returns the field name with the most selective (cheapest) index.

        Selectivity = avg_entries_per_value (lower = better).
        If no indexed field is present, returns None.
        """
        best_field = None
        lowest_estimated_rows = float('inf')

        for pred in predicates:
            if self._registry.has_index(pred.field):
                stats = self._statistics.get(pred.field)
                if stats:
                    # avg_entries_per_value estimates how many rows a value matches
                    if stats.avg_entries_per_value < lowest_estimated_rows:
                        lowest_estimated_rows = stats.avg_entries_per_value
                        best_field = pred.field

        if best_field:
            logger.debug(
                "index selected",
                field=best_field,
                estimated_rows=lowest_estimated_rows,
            )
        return best_field

    @property
    def all_indexed_fields(self) -> List[str]:
        return self._registry.indexed_fields