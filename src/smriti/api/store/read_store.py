"""
read_store.py — Pure ReadStore abstract interface.

RECTIFIED (P0-1): ReadStore now exposes ONLY primitive retrieval:
    lookup(claim_id)          → raw record dict
    scan(predicates, sort, pag) → (records, total)
    fetch_relationship(claim_id) → raw reliability record
    stream()                  → all records (iterator)

MOVED OUT of ReadStore:
    traverse_graph    → NavigationService
    aggregate_statistics → StatisticsService
    connected component logic → NavigationService

This means replacing InMemoryReadStore with DuckDBReadStore or
ElasticsearchReadStore ONLY requires reimplementing lookup/scan/fetch/stream.
All traversal, aggregation, and statistics logic stays in services.

Rules:
    ✅ Deterministic ordering in scan()
    ✅ Immutable after construction
    ✅ Only primitive operations
    ❌ No traversal
    ❌ No aggregation
    ❌ No statistics computation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Iterator

from smriti.api.domain.predicates import Predicate, SortSpec, Pagination


class ReadStore(ABC):
    """Pure primitive retrieval abstract interface."""

    @property
    @abstractmethod
    def run_id(self) -> str: ...

    @property
    @abstractmethod
    def node_count(self) -> int: ...

    @abstractmethod
    def lookup(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """O(1) point lookup by claim_id. Returns raw record or None."""
        ...

    @abstractmethod
    def scan(
        self,
        predicates: List[Predicate],
        sort: SortSpec,
        pagination: Pagination,
        text_contains: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Linear scan with predicate filter, sort, and pagination.
        Returns (page_records, total_matching_count).
        Deterministically ordered.
        """
        ...

    @abstractmethod
    def fetch_relationship(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """O(1) point lookup of reliability record. Returns raw dict or None."""
        ...

    @abstractmethod
    def stream(self) -> Iterator[Dict[str, Any]]:
        """Return all claim records as an iterator (for export/full-scan)."""
        ...

    @abstractmethod
    def get_edge_records(self) -> List[Dict[str, Any]]:
        """Return all edge records as raw dicts (for graph traversal by NavigationService)."""
        ...

    @abstractmethod
    def get_adjacency(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Return adjacency list: {claim_id: [(neighbor_id, edge_id, rel_type)]}"""
        ...