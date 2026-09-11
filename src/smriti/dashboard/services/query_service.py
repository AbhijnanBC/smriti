"""
query_service.py — Claim retrieval and search for Phase 10.
"""

from __future__ import annotations

from typing import Any

import structlog
from smriti.core.models import ExplainabilityLevel, PredicateOperator, ProjectionLevel

logger = structlog.get_logger(__name__)


class QueryService:
    """Handles all claim retrieval and search operations against Phase 9."""

    def __init__(self, api) -> None:
        self._api = api

    def get_claim(
        self,
        claim_id: str,
        explain_level: int = ExplainabilityLevel.NONE,
    ) -> dict[str, Any] | None:
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
        filters: dict[str, Any] = None,
        sort_field: str = "reliability_index",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search claims with filters and pagination."""
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
            claims = [c.to_dict() if hasattr(c, "to_dict") else vars(c) for c in resp.data]
            return {"claims": claims, "total": resp.total_count or 0}
        except Exception as e:
            logger.error("search_claims failed", error=str(e))
            return {"claims": [], "total": 0}

    def top_claims(self, n: int = 10) -> list[dict]:
        """Return top N most reliable claims."""
        try:
            resp = self._api.search(
                predicates=(),
                sort_field="reliability_index",
                sort_order="desc",
                limit=n,
                offset=0,
                projection=ProjectionLevel.STANDARD,
            )
            return [c.to_dict() if hasattr(c, "to_dict") else vars(c) for c in resp.data]
        except Exception as e:
            logger.error("top_claims failed", error=str(e))
            return []

    # ── NEW: Compatibility execute method ──────────────────────────────────
    def execute(self, request) -> dict[str, Any]:
        """
        Compatibility method for the Phase 10 architecture.
        If called with a SearchRequest-like object, delegate to search_claims.
        Otherwise return an empty result.
        """
        # If it's a dict, try to extract fields
        if isinstance(request, dict):
            return self.search_claims(
                text_query=request.get("text_contains", ""),
                filters=request.get("predicates", {}),
                sort_field=request.get("sort_field", "reliability_index"),
                sort_order=request.get("sort_order", "desc"),
                limit=request.get("limit", 20),
                offset=request.get("offset", 0),
            )
        # If it's an object, try attribute access
        try:
            text_query = getattr(request, "text_contains", "")
            filters = getattr(request, "predicates", {})
            sort_field = getattr(request, "sort_field", "reliability_index")
            sort_order = getattr(request, "sort_order", "desc")
            limit = getattr(request, "limit", 20)
            offset = getattr(request, "offset", 0)
            return self.search_claims(
                text_query=text_query,
                filters=filters,
                sort_field=sort_field,
                sort_order=sort_order,
                limit=limit,
                offset=offset,
            )
        except Exception:
            return {"claims": [], "total": 0}
