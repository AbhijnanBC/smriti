"""
search_view.py — SearchView: renders search panel and dispatches SubmitSearchCommand.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.commands.commands import (
    ApplyFilterCommand,
    ClearFiltersCommand,
    SubmitSearchCommand,
)
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.policies.policies import InteractionPolicy, PolicyEngine
from smriti.dashboard.views.base_view import BaseView


class SearchView(BaseView):
    """
    Renders search box and filter controls.
    Dispatches commands via InteractionDispatcher.
    """

    def __init__(
        self,
        dispatcher: InteractionDispatcher | None = None,
        state_manager=None,
    ) -> None:
        """
        Accept either a dispatcher or a state_manager.
        If state_manager is given, we build a default dispatcher.
        """
        if dispatcher is not None:
            self._dispatcher = dispatcher
        elif state_manager is not None:
            policy_engine = PolicyEngine(InteractionPolicy())
            self._dispatcher = InteractionDispatcher(
                state_manager=state_manager,
                policy_engine=policy_engine,
            )
        else:
            raise ValueError("SearchView requires either dispatcher or state_manager")

    def render(self) -> None:
        # ── Search form ──────────────────────────────────────────────────────────
        with st.form(key="search_form"):
            current_query = self._dispatcher._sm.state.search_query

            query = st.text_input(
                "Search claims",
                value=current_query,
                placeholder="Enter keywords...",
            )
            submitted = st.form_submit_button("Search")
            if submitted:
                self._dispatcher.dispatch(
                    SubmitSearchCommand(
                        session_id=self._dispatcher._sm._session_id,
                        query=query,
                    )
                )

        # ── Filters expander ─────────────────────────────────────────────────────
        with st.expander("Filters"):
            col_a, col_b = st.columns(2)
            with col_a:
                label_filter = st.selectbox(
                    "Calibration Label",
                    options=["", "very_high", "high", "moderate", "low", "very_low"],
                    index=0,
                    format_func=lambda x: "All" if x == "" else x.replace("_", " ").title(),
                )
            with col_b:
                role_filter = st.selectbox(
                    "Semantic Role",
                    options=[
                        "",
                        "foundational_claim",
                        "bridge_claim",
                        "evidence_hub",
                        "peripheral_claim",
                        "leaf_claim",
                    ],
                    index=0,
                    format_func=lambda x: "All" if x == "" else x.replace("_", " ").title(),
                )

            apply_col, clear_col = st.columns(2)
            with apply_col:
                if st.button("Apply Filters", use_container_width=True):
                    session_id = self._dispatcher._sm._session_id
                    if label_filter:
                        self._dispatcher.dispatch(
                            ApplyFilterCommand(
                                session_id=session_id,
                                field="calibration_label",
                                value=label_filter,
                            )
                        )
                    if role_filter:
                        self._dispatcher.dispatch(
                            ApplyFilterCommand(
                                session_id=session_id,
                                field="semantic_role",
                                value=role_filter,
                            )
                        )

            with clear_col:
                if st.button("Clear Filters", use_container_width=True):
                    self._dispatcher.dispatch(
                        ClearFiltersCommand(session_id=self._dispatcher._sm._session_id)
                    )
