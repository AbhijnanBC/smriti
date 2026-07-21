"""
reliability_badge.py — Reliability visualization components.
Updated to accept StatisticsPresentationModel.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.models.presentation import (
    ClaimPresentationModel,
    StatisticsPresentationModel,
)


def render_reliability_badge(pm: ClaimPresentationModel) -> None:
    """Display a colored reliability badge from a ClaimPresentationModel."""
    st.markdown(
        f'<span style="background-color:{pm.label_color};color:white;padding:4px 8px;'
        f'border-radius:4px;font-weight:bold">{pm.label_display} ({pm.ri_formatted})</span>',
        unsafe_allow_html=True,
    )


def render_calibration_distribution_from_pm(stats: StatisticsPresentationModel) -> None:
    """Render calibration label distribution chart from StatisticsPresentationModel."""
    from smriti.dashboard.models.presentation import LABEL_COLOR

    dist = stats.calibration_distribution
    if not dist:
        return

    try:
        import plotly.graph_objects as go

        labels = [k.replace("_", " ").title() for k in dist.keys()]
        counts = list(dist.values())
        colors = [LABEL_COLOR.get(k, "#95a5a6") for k in dist.keys()]

        fig = go.Figure(go.Bar(
            x=labels, y=counts, marker_color=colors,
            text=counts, textposition="outside",
        ))
        fig.update_layout(
            title="Calibration Distribution",
            xaxis_title="Calibration Level",
            yaxis_title="Claim Count",
            height=300, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        for label, count in dist.items():
            st.write(f"{label.replace('_', ' ').title()}: {count}")