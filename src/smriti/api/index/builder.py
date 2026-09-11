"""index/builder.py — IndexBuilder for Phase 9."""

from __future__ import annotations

from typing import Any

import structlog
from smriti.api.index.registry import IndexRegistry

logger = structlog.get_logger(__name__)

# Fields to index by default (configurable)
DEFAULT_INDEXED_FIELDS = [
    "reliability_index_bucket",  # bucketed for range queries: 0-10, 10-20, etc.
    "calibration_label",
    "partition_id",
    "semantic_role",
    "document_id",
]


class IndexBuilder:
    """
    Builds indexes from claim records.
    Called once during KnowledgeAPI construction.
    """

    def build(
        self,
        claim_records: dict[str, dict[str, Any]],
        fields: list[str] | None = None,
    ) -> IndexRegistry:
        """
        Build indexes for the specified fields.

        Args:
            claim_records: {claim_id: record_dict} from InMemoryReadStore.
            fields:        Fields to index. Defaults to DEFAULT_INDEXED_FIELDS.

        Returns:
            Populated IndexRegistry.
        """
        registry = IndexRegistry()
        fields = fields or DEFAULT_INDEXED_FIELDS

        for field_name in fields:
            index: dict[Any, list[str]] = {}
            for claim_id, record in claim_records.items():
                value = self._get_index_value(field_name, record)
                if value is not None:
                    index.setdefault(value, []).append(claim_id)
            registry.register(field_name, index)

        logger.info(
            "indexes built",
            fields=fields,
            total_claims=len(claim_records),
        )
        return registry

    def _get_index_value(self, field_name: str, record: dict) -> Any:
        """Get the index key for a field. Special handling for bucketed fields."""
        if field_name == "reliability_index_bucket":
            ri = record.get("reliability_index", 0.0)
            return int(ri // 10) * 10  # Bucket: 0, 10, 20, ..., 90
        return record.get(field_name)
