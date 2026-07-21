"""result_list_view.py — ResultListView: renders a paginated claim list."""
from __future__ import annotations
from typing import List
import streamlit as st
from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.models.presentation import ClaimPresentationModel
from smriti.dashboard.state.epistemic_state import EpistemicStateManager


class ResultListView(BaseView):
    """Renders a scrollable, paginated list of ClaimPresentationModels."""

    def __init__(
        self,
        state_manager: EpistemicStateManager,
        claims: List[ClaimPresentationModel] = None,
        total: int = 0,
    ) -> None:
        self._sm = state_manager
        self._claims = claims or []
        self._total = total

    def refresh(self, claims: List[ClaimPresentationModel] = None, total: int = 0) -> None:
        self._claims = claims or []
        self._total = total

    def render(self) -> None:
        state = self._sm.state
        st.caption(f"**{self._total}** claims found")

        if not self._claims:
            st.info("No claims to display.")
            return

        for pm in self._claims:
            is_selected = pm.claim_id == state.selected_claim_id
            label = f"{pm.label_icon} {pm.text[:55]}..." if len(pm.text) > 55 else f"{pm.label_icon} {pm.text}"
            if is_selected:
                label = f"▶ {label}"
            if st.button(label, key=f"claim_{pm.claim_id}", use_container_width=True):
                self._sm.select_claim(pm.claim_id)
                st.rerun()

        # Pagination
        if self._total > state.page_size:
            max_page = max(0, (self._total - 1) // state.page_size)
            cols = st.columns(3)
            with cols[0]:
                if st.button("← Previous", disabled=state.page == 0):
                    self._sm.set_page(state.page - 1)
                    st.rerun()
            with cols[1]:
                st.caption(f"Page {state.page + 1} / {max_page + 1}")
            with cols[2]:
                if st.button("Next →", disabled=state.page >= max_page):
                    self._sm.set_page(state.page + 1)
                    st.rerun()