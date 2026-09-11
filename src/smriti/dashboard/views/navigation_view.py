"""navigation_view.py — NavigationView: breadcrumb bar and back button."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.commands.commands import NavigateBackCommand
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.views.base_view import BaseView


class NavigationView(BaseView):
    """Renders breadcrumbs and back navigation. Dispatches NavigateBackCommand."""

    def __init__(
        self,
        dispatcher: InteractionDispatcher | None = None,
        state_manager=None,
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
            raise ValueError("NavigationView requires either dispatcher or state_manager")

    def supports(self, context) -> bool:
        return bool(self._dispatcher._sm.state.breadcrumbs)

    def render(self) -> None:
        breadcrumbs = self._dispatcher._sm.state.breadcrumbs
        if not breadcrumbs:
            return
        crumb_parts = []
        for i, crumb in enumerate(breadcrumbs):
            label = crumb.get("label", crumb.get("claim_id", "")[:8])
            crumb_parts.append(f"**{label}**" if i == len(breadcrumbs) - 1 else label)
        st.markdown("🗺️ " + " → ".join(crumb_parts))
        if len(breadcrumbs) > 1:
            if st.button("← Back", key="breadcrumb_back"):
                self._dispatcher.dispatch(
                    NavigateBackCommand(session_id=self._dispatcher._sm._session_id)
                )
                st.rerun()
