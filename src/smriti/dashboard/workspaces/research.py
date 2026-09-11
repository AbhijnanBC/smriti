"""
research.py — ResearchWorkspace.

Investigative objective: General-purpose knowledge exploration.
Views coordinated: NavigationView + SearchView + ResultListView + InspectorView
"""

from __future__ import annotations

import streamlit as st
from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.inspector_view import InspectorView
from smriti.dashboard.views.navigation_view import NavigationView
from smriti.dashboard.views.result_list_view import ResultListView
from smriti.dashboard.views.search_view import SearchView
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext


class ResearchWorkspace(BaseWorkspace):
    """General-purpose exploratory research workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.RESEARCH,
            investigative_objective="Explore and discover knowledge relationships",
            default_lens=EpistemicLens.EXPLORATION,
            default_explainability=1,
            primary_views=("navigation", "search", "result_list", "inspector"),
            navigation_strategy="semantic",
            max_results_per_page=20,
        )

    def on_create(self) -> None:
        """Build views — no data yet, just structure."""

        # Views created here are placeholders; data injected via refresh_all()
        # Actual state_manager injected at first render via _fetch_and_refresh
        pass

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state

        # Fetch data from ServiceClient
        result = context.client.search_claims(
            text_query=state.search_query,
            filters=state.active_filters,
            sort_field=state.sort_field,
            sort_order=state.sort_order,
            limit=state.page_size,
            offset=state.page * state.page_size,
        )
        claims_dtos = result.get("claims", [])
        total = result.get("total", 0)
        claim_pms = DTOTransformer.to_claims_list(claims_dtos) or []

        selected_pm = None
        if state.selected_claim_id:
            dto = context.client.get_claim(
                state.selected_claim_id,
                explain_level=state.explainability_level,
            )
            if dto:
                selected_pm = DTOTransformer.to_claim_pm(dto)

        # Two-column layout: list | inspector
        col_list, col_inspector = st.columns([2, 3])

        with col_list:
            nav_view = NavigationView(state_manager=context.state_manager)
            nav_view.render()

            search_view = SearchView(state_manager=context.state_manager)
            search_view.render()

            list_view = ResultListView(
                state_manager=context.state_manager,
                claims=claim_pms,
                total=total,
            )
            list_view.render()

        with col_inspector:
            inspector_view = InspectorView(claim=selected_pm)
            inspector_view.render()
