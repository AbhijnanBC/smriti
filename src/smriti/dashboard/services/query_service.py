"""
query_service.py — Claim retrieval and search for Phase 10.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from smriti.core.models import ExplainabilityLevel, ProjectionLevel, PredicateOperator

logger = structlog.get_logger(__name__)


class QueryService:
    """Handles all claim retrieval and search operations against Phase 9."""

    def __init__(self, api) -> None:
        self._api = api

    def get_claim(
        self,
        claim_id: str,
        explain_level: int = ExplainabilityLevel.NONE,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve one claim by ID. Returns None if not found."""
        try:
            level = ProjectionLevel.DETAILED
            if explain_level >= ExplainabilityLevel.FULL_AUDIT:
                level = ProjectionLevel.FULL_AUDIT
            elif explain_level >= ExplainabilityLevel.DETAILED:
                level = ProjectionLevel.EXPLAINABILITY
            resp = self._api.get_claim(claim_id, projection=level)
            return resp.data.to_dict() if hasattr(resp.data, "to_dict") else vars(resp.data)
        except Exception as e:
            if "not found" in str(e).lower():
                return None
            logger.warning("get_claim failed", claim_id=claim_id[:8], error=str(e))
            return None

    def search_claims(
        self,
        text_query: str = "",
        filters: Dict[str, Any] = None,
        sort_field: str = "reliability_index",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search claims with filters and pagination."""
        from smriti.core.models import SortOrder
        from smriti.api.domain.predicates import Predicate

        predicates = []
        for field_name, value in (filters or {}).items():
            if value is not None and value != "":
                op = PredicateOperator.EQ
                if isinstance(value, (int, float)) and field_name == "reliability_index":
                    op = PredicateOperator.GTE
                predicates.append(Predicate(field_name, op, value))

        try:
            resp = self._api.search(
                predicates=tuple(predicates),
                text_contains=text_query or None,
                sort_field=sort_field,
                sort_order=sort_order,
                limit=limit,
                offset=offset,
                projection=ProjectionLevel.STANDARD,
            )
            claims = [
                c.to_dict() if hasattr(c, "to_dict") else vars(c)
                for c in resp.data
            ]
            return {"claims": claims, "total": resp.total_count or 0}
        except Exception as e:
            logger.error("search_claims failed", error=str(e))
            return {"claims": [], "total": 0}

    def top_claims(self, n: int = 10) -> List[Dict]:
        """Return top N most reliable claims."""
        try:
            resp = self._api.top_claims(n=n, projection=ProjectionLevel.STANDARD)
            return [
                c.to_dict() if hasattr(c, "to_dict") else vars(c)
                for c in resp.data
            ]
        except Exception as e:
            logger.error("top_claims failed", error=str(e))
            return []