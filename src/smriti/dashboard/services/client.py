"""
client.py — ServiceClient for Phase 10.

THE exclusive communication channel between Phase 10 and Phase 9.
Delegates to specialised service modules — no Phase 9 logic lives here.

Rules:
    ✅ One instance per session (stored in st.session_state)
    ✅ Delegates to QueryService, TraversalService, etc.
    ✅ Every method returns Python-native types (dict/list/str)
    ❌ No business logic — pure delegation
    ❌ No caching beyond Streamlit's built-in caching
    ❌ No presentation component accesses Phase 9 directly
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from smriti.dashboard.services.query_service import QueryService
from smriti.dashboard.services.traversal_service import TraversalService
from smriti.dashboard.services.statistics_service import StatisticsService
from smriti.dashboard.services.export_service import ExportService
from smriti.dashboard.services.explainability_service import ExplainabilityService


class ServiceClient:
    """
    Thin delegator — the only Phase 10 ↔ Phase 9 façade.
    Split into five service modules to keep each bounded and testable.
    """

    def __init__(self, api) -> None:
        self._api = api
        self._query        = QueryService(api)
        self._traversal    = TraversalService(api)
        self._statistics   = StatisticsService(api)
        self._export       = ExportService(api)
        self._explainability = ExplainabilityService(api)

    @property
    def run_id(self) -> str:
        return self._api.run_id

    @property
    def node_count(self) -> int:
        return self._api.node_count

    # ── Delegation to QueryService ─────────────────────────────────────────────

    def get_claim(self, claim_id: str, explain_level: int = 0) -> Optional[Dict[str, Any]]:
        return self._query.get_claim(claim_id, explain_level=explain_level)

    def search_claims(
        self,
        text_query: str = "",
        filters: Dict[str, Any] = None,
        sort_field: str = "reliability_index",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        return self._query.search_claims(
            text_query=text_query,
            filters=filters,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def top_claims(self, n: int = 10) -> List[Dict]:
        return self._query.top_claims(n=n)

    # ── Delegation to TraversalService ────────────────────────────────────────

    def traverse(self, claim_id: str, max_depth: int = 2) -> Optional[Dict]:
        return self._traversal.traverse(claim_id, max_depth=max_depth)

    # ── Delegation to StatisticsService ──────────────────────────────────────

    def get_statistics(self) -> Dict[str, Any]:
        return self._statistics.get_statistics()

    # ── Delegation to ExplainabilityService ───────────────────────────────────

    def get_explanation(self, claim_id: str, level: int = 3) -> Optional[Dict]:
        return self._explainability.get_explanation(claim_id, level=level)

    # ── Delegation to ExportService ───────────────────────────────────────────

    def export_data(self, fmt: str = "json") -> Optional[str]:
        return self._export.get_raw_export(fmt=fmt)

    # ── Convenience ───────────────────────────────────────────────────────────

    def get_contradictions(self, min_reliability: float = 0.0) -> Dict[str, Any]:
        """Return claims most involved in contradictions."""
        return self.search_claims(
            sort_field="conflict_pressure",
            sort_order="desc",
            limit=50,
        )