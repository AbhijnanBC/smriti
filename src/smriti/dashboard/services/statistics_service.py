"""
statistics_service.py — Global statistics for Phase 10.
"""

from __future__ import annotations

from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class StatisticsService:
    """Handles graph-wide statistics retrieval from Phase 9."""

    def __init__(self, api) -> None:
        self._api = api

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve graph-wide statistics."""
        try:
            resp = self._api.statistics()
            return resp.data
        except Exception as e:
            logger.error("get_statistics failed", error=str(e))
            return {}