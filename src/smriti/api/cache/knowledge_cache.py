"""
knowledge_cache.py — KnowledgeViewCache for Phase 9.

RECTIFIED (P0-4): Cache now stores KnowledgeView objects, NOT DTOs.

Reason:
    If cache stored DTOs, changing the DTO schema would require
    invalidating the entire cache even when the underlying knowledge is unchanged.
    Storing Views (domain objects) means:
        - Same View can be used to produce any DTO version
        - Cache is schema-independent
        - Only the DTOMapper needs to change on schema updates

Cache key = SHA256(run_id + plan_id + projection_level)[:24]

Cache is run-scoped:
    - Entries from different run_ids never collide
    - Cache is invalidated when a new ScoredKnowledgeGraph is loaded
"""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class KnowledgeViewCache:
    """
    LRU in-memory cache for KnowledgeView objects (NOT DTOs).
    Scoped to one run_id.
    """

    def __init__(self, max_size: int = 256, run_id: str = "") -> None:
        self._max_size = max_size
        self._run_id = run_id
        self._store: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _make_key(self, plan_id: str, projection_level: str) -> str:
        material = f"{self._run_id}:{plan_id}:{projection_level}"
        return hashlib.sha256(material.encode()).hexdigest()[:24]

    def get_view(self, plan_id: str, projection_level: str) -> Any | None:
        """Return cached KnowledgeView or None on miss."""
        key = self._make_key(plan_id, projection_level)
        if key in self._store:
            self._store.move_to_end(key)
            self._hits += 1
            logger.debug("view cache hit", key=key[:8])
            return self._store[key]
        self._misses += 1
        return None

    def set_view(self, plan_id: str, projection_level: str, view: Any) -> None:
        """Store a KnowledgeView in cache."""
        key = self._make_key(plan_id, projection_level)
        if key in self._store:
            self._store.move_to_end(key)
        else:
            if len(self._store) >= self._max_size:
                self._store.popitem(last=False)
        self._store[key] = view

    def clear(self) -> None:
        self._store.clear()
        logger.info("knowledge view cache cleared")

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._store)
