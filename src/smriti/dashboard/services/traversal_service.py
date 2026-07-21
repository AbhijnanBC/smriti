"""
traversal_service.py — Graph traversal for Phase 10.
"""

from __future__ import annotations

from typing import Optional, Dict
import structlog

logger = structlog.get_logger(__name__)


class TraversalService:
    """Handles graph traversal operations against Phase 9."""

    def __init__(self, api) -> None:
        self._api = api

    def traverse(self, claim_id: str, max_depth: int = 2) -> Optional[Dict]:
        """Traverse graph from a claim up to max_depth hops."""
        try:
            resp = self._api.traverse(claim_id, max_depth=max_depth)
            return resp.data
        except Exception as e:
            logger.warning("traverse failed", claim_id=claim_id[:8], error=str(e))
            return None