"""search_view.py — SearchView: renders search panel and dispatches SubmitSearchCommand."""
from __future__ import annotations

import streamlit as st

from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.commands.commands import (
    SubmitSearchCommand,
    ApplyFilterCommand,
    ClearFiltersCommand,
)
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher


class SearchView(BaseView):
    """
    Renders search box and filter controls.
    Dispatches commands via InteractionDispatcher instead of mutating state directly.
    st.rerun() is removed – the EventBus handles reruns via StreamlitLifecycleSubscriber.
    """

    def __init__(self, dispatcher: InteractionDispatcher) -> None:
        self._dispatcher = dispatcher

    def render(self) -> None:
        # ── Search form ──────────────────────────────────────────────────────────
        with st.form(key="search_form"):
            # The current search query value is read from state, but we don't mutate it.
            # We'll get the current value from the dispatcher's state_manager.
            # For simplicity, we assume we can access state via dispatcher's internal state manager.
            current_query = self._dispatcher._sm.state.search_query

            query = st.text_input(
                "Search claims",
                value=current_query,
                placeholder="Enter keywords...",
            )
            submitted = st.form_submit_button("Search")
            if submitted:
                self._dispatcher.dispatch(SubmitSearchCommand(query))
                # No st.rerun() – EventBus will trigger rerun via subscriber

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
                    options=["", "foundational_claim", "bridge_claim", "evidence_hub",
                             "peripheral_claim", "leaf_claim"],
                    index=0,
                    format_func=lambda x: "All" if x == "" else x.replace("_", " ").title(),
                )

            apply_col, clear_col = st.columns(2)
            with apply_col:
                if st.button("Apply Filters", use_container_width=True):
                    if label_filter:
                        self._dispatcher.dispatch(ApplyFilterCommand("calibration_label", label_filter))
                    if role_filter:
                        self._dispatcher.dispatch(ApplyFilterCommand("semantic_role", role_filter))
                    # No st.rerun()

            with clear_col:
                if st.button("Clear Filters", use_container_width=True):
                    self._dispatcher.dispatch(ClearFiltersCommand())
                    # No st.rerun()