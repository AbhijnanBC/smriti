"""reliability_view.py — ReliabilityView: reliability metrics and calibration chart."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.components.claim_card import render_claim_card
from smriti.dashboard.components.reliability_badge import render_calibration_distribution_from_pm
from smriti.dashboard.models.presentation import ClaimPresentationModel, StatisticsPresentationModel
from smriti.dashboard.views.base_view import BaseView


class ReliabilityView(BaseView):
    """Renders reliability metrics and calibration distribution."""

    def __init__(
        self,
        claims: list[ClaimPresentationModel] | None = None,
        stats: StatisticsPresentationModel | None = None,
        selected_claim: ClaimPresentationModel | None = None,
    ) -> None:
        self._claims = claims or []
        self._stats = stats
        self._selected_claim = selected_claim

    # Narrows BaseView's generic **kwargs contract to this view's specific
    # fields; ViewCoordinator always dispatches via **kwargs (Any-typed),
    # so this is safe at every real call site.
    def refresh(  # type: ignore[override]
        self,
        claims: list[ClaimPresentationModel] | None = None,
        stats: StatisticsPresentationModel | None = None,
        selected_claim: ClaimPresentationModel | None = None,
    ) -> None:
        self._claims = claims or []
        self._stats = stats
        self._selected_claim = selected_claim

    def render(self) -> None:
        if self._claims:
            avg_ri = sum(c.reliability_index for c in self._claims) / len(self._claims)
            m1, m2, m3 = st.columns(3)
            m1.metric("Claims Shown", len(self._claims))
            m2.metric("Avg Reliability", f"{avg_ri:.1f}")
            m3.metric("Displayed", str(len(self._claims)))

        if self._selected_claim:
            st.divider()
            render_claim_card(self._selected_claim)
        elif self._stats:
            render_calibration_distribution_from_pm(self._stats)
