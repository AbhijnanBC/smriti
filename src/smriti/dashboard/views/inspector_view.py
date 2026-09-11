"""inspector_view.py — InspectorView: renders a full claim detail panel."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.components.claim_card import render_claim_card
from smriti.dashboard.components.signal_chart import render_signal_chart_from_pm
from smriti.dashboard.models.presentation import ClaimPresentationModel
from smriti.dashboard.views.base_view import BaseView


class InspectorView(BaseView):
    """Renders detailed claim information from a ClaimPresentationModel."""

    def __init__(self, claim: ClaimPresentationModel | None = None) -> None:
        self._claim = claim

    # Narrows BaseView's generic **kwargs contract to this view's specific
    # fields; ViewCoordinator always dispatches via **kwargs (Any-typed),
    # so this is safe at every real call site.
    def refresh(self, claim: ClaimPresentationModel | None = None) -> None:  # type: ignore[override]
        self._claim = claim

    def supports(self, context) -> bool:
        return self._claim is not None

    def render(self) -> None:
        if not self._claim:
            st.info("Select a claim from the list to inspect it.")
            return
        render_claim_card(self._claim)
        st.divider()
        render_signal_chart_from_pm(self._claim)
