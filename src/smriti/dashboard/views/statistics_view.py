"""statistics_view.py — StatisticsView: distribution charts and summary metrics."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.components.statistics_panel import render_statistics_panel_from_pm
from smriti.dashboard.models.presentation import StatisticsPresentationModel
from smriti.dashboard.views.base_view import BaseView


class StatisticsView(BaseView):
    """Renders global statistics from StatisticsPresentationModel."""

    def __init__(self, stats: StatisticsPresentationModel | None = None) -> None:
        self._stats = stats

    # Narrows BaseView's generic **kwargs contract to this view's specific
    # fields; ViewCoordinator always dispatches via **kwargs (Any-typed),
    # so this is safe at every real call site.
    def refresh(self, stats: StatisticsPresentationModel | None = None) -> None:  # type: ignore[override]
        self._stats = stats

    def supports(self, context) -> bool:
        return self._stats is not None

    def render(self) -> None:
        if not self._stats:
            st.error("Statistics unavailable. Ensure Phase 9 is initialized.")
            return
        render_statistics_panel_from_pm(self._stats)
