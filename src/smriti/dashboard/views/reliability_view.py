"""reliability_view.py — ReliabilityView: reliability metrics and calibration chart."""
from __future__ import annotations
from typing import List, Optional
import streamlit as st
from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.models.presentation import ClaimPresentationModel, StatisticsPresentationModel
from smriti.dashboard.components.reliability_badge import render_calibration_distribution_from_pm
from smriti.dashboard.components.claim_card import render_claim_card


class ReliabilityView(BaseView):
    """Renders reliability metrics and calibration distribution."""

    def __init__(
        self,
        claims: List[ClaimPresentationModel] = None,
        stats: Optional[StatisticsPresentationModel] = None,
        selected_claim: Optional[ClaimPresentationModel] = None,
    ) -> None:
        self._claims = claims or []
        self._stats = stats
        self._selected_claim = selected_claim

    def refresh(
        self,
        claims: List[ClaimPresentationModel] = None,
        stats: Optional[StatisticsPresentationModel] = None,
        selected_claim: Optional[ClaimPresentationModel] = None,
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