"""statistics_view.py — StatisticsView: distribution charts and summary metrics."""
from __future__ import annotations
from typing import Optional
import streamlit as st
from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.models.presentation import StatisticsPresentationModel
from smriti.dashboard.components.statistics_panel import render_statistics_panel_from_pm


class StatisticsView(BaseView):
    """Renders global statistics from StatisticsPresentationModel."""

    def __init__(self, stats: Optional[StatisticsPresentationModel] = None) -> None:
        self._stats = stats

    def refresh(self, stats: Optional[StatisticsPresentationModel] = None) -> None:
        self._stats = stats

    def supports(self, context) -> bool:
        return self._stats is not None

    def render(self) -> None:
        if not self._stats:
            st.error("Statistics unavailable. Ensure Phase 9 is initialized.")
            return
        render_statistics_panel_from_pm(self._stats)