"""navigation_view.py — NavigationView: breadcrumb bar and back button."""
from __future__ import annotations
import streamlit as st
from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.state.epistemic_state import EpistemicStateManager


class NavigationView(BaseView):
    """Renders breadcrumbs and back navigation."""

    def __init__(self, state_manager: EpistemicStateManager) -> None:
        self._sm = state_manager

    def supports(self, context) -> bool:
        return bool(self._sm.state.breadcrumbs)

    def render(self) -> None:
        breadcrumbs = self._sm.state.breadcrumbs
        if not breadcrumbs:
            return
        crumb_parts = []
        for i, crumb in enumerate(breadcrumbs):
            label = crumb.get("label", crumb.get("claim_id", "")[:8])
            crumb_parts.append(f"**{label}**" if i == len(breadcrumbs) - 1 else label)
        st.markdown("🗺️ " + " → ".join(crumb_parts))
        if len(breadcrumbs) > 1:
            if st.button("← Back", key="breadcrumb_back"):
                self._sm.navigate_back()
                st.rerun()