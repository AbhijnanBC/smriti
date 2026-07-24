"""
reliability.py — ReliabilityWorkspace.

Investigative objective: Evaluate the trustworthiness of claims.
Views coordinated: ResultListView + ReliabilityView (detail + calibration)
"""

from __future__ import annotations

import streamlit as st

from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.result_list_view import ResultListView
from smriti.dashboard.views.reliability_view import ReliabilityView


class ReliabilityWorkspace(BaseWorkspace):
    """Reliability evaluation workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.RELIABILITY,
            investigative_objective="Evaluate the trustworthiness of claims",
            default_lens=EpistemicLens.RELIABILITY,
            default_explainability=2,
            primary_views=("result_list", "reliability"),
            navigation_strategy="reliability_ordered",
            max_results_per_page=25,
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state

        col_filter, col_sort = st.columns(2)
        with col_filter:
            min_ri = st.slider("Minimum Reliability Index", 0, 100, 0, step=5)
        with col_sort:
            sort_field = st.selectbox(
                "Sort by",
                ["reliability_index", "uncertainty_score", "support_count"],
                index=0,
            )

        filters = {"reliability_index": min_ri} if min_ri > 0 else {}
        result = context.client.search_claims(
            filters=filters,
            sort_field=sort_field,
            sort_order="desc",
            limit=state.page_size,
            offset=state.page * state.page_size,
        )
        claim_pms = DTOTransformer.to_claims_list(result.get("claims", [])) or []
        total = result.get("total", 0)

        stats_pm = None
        selected_pm = None

        if state.selected_claim_id:
            dto = context.client.get_claim(
                state.selected_claim_id,
                explain_level=max(state.explainability_level, 2),
            )
            if dto:
                selected_pm = DTOTransformer.to_claim_pm(dto)
        else:
            stats_dto = context.client.get_statistics()
            if stats_dto:
                stats_pm = DTOTransformer.to_statistics_pm(stats_dto)

        col_list, col_detail = st.columns([2, 3])
        with col_list:
            ResultListView(
                state_manager=context.state_manager,
                claims=claim_pms,
                total=total,
            ).render()
        with col_detail:
            ReliabilityView(
                claims=claim_pms,
                stats=stats_pm,
                selected_claim=selected_pm,
            ).render()