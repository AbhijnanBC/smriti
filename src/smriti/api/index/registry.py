"""
index/registry.py — IndexRegistry for Phase 9.

RECTIFIED (P0-3): The planner NEVER hardcodes indexed field names.
Instead it calls IndexSelector.has_index(field) and
IndexSelector.get_index_name(field).

IndexRegistry holds all built indexes.
IndexBuilder constructs them from the ReadStore.
IndexSelector answers "can this field be indexed?" at planning time.
IndexStatistics tracks index health.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class IndexRegistry:
    """
    Holds all built indexes for Phase 9.
    Instantiate once per KnowledgeAPI instance.
    """

    def __init__(self) -> None:
        # Each index: field_name → {value → [claim_id, ...]}
        self._indexes: dict[str, dict[Any, list[str]]] = {}
        self._indexed_fields: set = set()

    def register(self, field_name: str, index: dict[Any, list[str]]) -> None:
        """Register a pre-built index for a field."""
        self._indexes[field_name] = index
        self._indexed_fields.add(field_name)
        logger.debug("index registered", field=field_name, unique_values=len(index))

    def lookup(self, field_name: str, value: Any) -> list[str] | None:
        """Return claim_ids matching value in field_name index, or None."""
        idx = self._indexes.get(field_name)
        if idx is None:
            return None
        return idx.get(value)

    def has_index(self, field_name: str) -> bool:
        return field_name in self._indexed_fields

    @property
    def indexed_fields(self) -> list[str]:
        return sorted(self._indexed_fields)
