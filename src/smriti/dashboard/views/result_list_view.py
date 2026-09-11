"""result_list_view.py — ResultListView: renders a paginated claim list."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.commands.commands import SelectClaimCommand, SetPageCommand
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.models.presentation import ClaimPresentationModel
from smriti.dashboard.views.base_view import BaseView


class ResultListView(BaseView):
    """Renders a scrollable, paginated list of ClaimPresentationModels.
    Dispatches SelectClaimCommand / SetPageCommand rather than mutating state directly."""

    def __init__(
        self,
        dispatcher: InteractionDispatcher | None = None,
        state_manager=None,
        claims: list[ClaimPresentationModel] = None,
        total: int = 0,
    ) -> None:
        """Accept either a dispatcher or a state_manager (builds a default dispatcher)."""
        if dispatcher is not None:
            self._dispatcher = dispatcher
        elif state_manager is not None:
            from smriti.dashboard.policies.policies import InteractionPolicy, PolicyEngine

            self._dispatcher = InteractionDispatcher(
                state_manager=state_manager,
                policy_engine=PolicyEngine(InteractionPolicy()),
            )
        else:
            raise ValueError("ResultListView requires either dispatcher or state_manager")
        self._claims = claims or []
        self._total = total

    def refresh(self, claims: list[ClaimPresentationModel] = None, total: int = 0) -> None:
        self._claims = claims or []
        self._total = total

    def render(self) -> None:
        state = self._dispatcher._sm.state
        session_id = self._dispatcher._sm._session_id
        st.caption(f"**{self._total}** claims found")

        if not self._claims:
            st.info("No claims to display.")
            return

        for pm in self._claims:
            is_selected = pm.claim_id == state.selected_claim_id
            label = (
                f"{pm.label_icon} {pm.text[:55]}..."
                if len(pm.text) > 55
                else f"{pm.label_icon} {pm.text}"
            )
            if is_selected:
                label = f"▶ {label}"
            if st.button(label, key=f"claim_{pm.claim_id}", use_container_width=True):
                self._dispatcher.dispatch(
                    SelectClaimCommand(
                        session_id=session_id,
                        claim_id=pm.claim_id,
                        source_view=self.view_name,
                    )
                )
                st.rerun()

        # Pagination
        if self._total > state.page_size:
            max_page = max(0, (self._total - 1) // state.page_size)
            cols = st.columns(3)
            with cols[0]:
                if st.button("← Previous", disabled=state.page == 0):
                    self._dispatcher.dispatch(
                        SetPageCommand(session_id=session_id, page=state.page - 1)
                    )
                    st.rerun()
            with cols[1]:
                st.caption(f"Page {state.page + 1} / {max_page + 1}")
            with cols[2]:
                if st.button("Next →", disabled=state.page >= max_page):
                    self._dispatcher.dispatch(
                        SetPageCommand(session_id=session_id, page=state.page + 1)
                    )
                    st.rerun()
