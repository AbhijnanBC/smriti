"""
explainability_service.py — Explainability retrieval for Phase 10.
"""

from __future__ import annotations

import structlog
from smriti.core.models import ExplainabilityLevel

logger = structlog.get_logger(__name__)


class ExplainabilityService:
    """Handles explainability record retrieval from Phase 9."""

    def __init__(self, api) -> None:
        self._api = api

    def get_explanation(
        self,
        claim_id: str,
        level: int = ExplainabilityLevel.FULL_AUDIT,
    ) -> dict | None:
        """Retrieve full explainability record for one claim."""
        try:
            from smriti.core.models import ExplainabilityLevel as EL

            resp = self._api.explain(claim_id, level=EL(level))
            return resp.data
        except Exception as e:
            logger.warning("get_explanation failed", claim_id=claim_id[:8], error=str(e))
            return None
