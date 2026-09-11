"""
signal_chart.py — Signal vector visualization.
Receives ClaimPresentationModel — never a raw dict.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.models.presentation import ClaimPresentationModel


def render_signal_chart_from_pm(pm: ClaimPresentationModel) -> None:
    """
    Render the signal vector as a horizontal Plotly bar chart.

    Args:
        pm: ClaimPresentationModel with signals pre-populated.
    """
    if not pm.signals:
        st.info("No signal data available at current explainability level.")
        return

    try:
        import plotly.graph_objects as go

        labels = [s.label for s in pm.signals]
        values = [s.value for s in pm.signals]
        colors = [s.color for s in pm.signals]
        texts = [s.formatted for s in pm.signals]

        fig = go.Figure(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color=colors,
                text=texts,
                textposition="outside",
            )
        )
        fig.update_layout(
            title="Reliability Signal Vector",
            xaxis={"range": [0, 1.1], "title": "Signal Value (0–1)"},
            height=300,
            showlegend=False,
            margin={"l": 200, "r": 60, "t": 40, "b": 40},
        )
        st.plotly_chart(fig, use_container_width=True)

        if pm.component_scores:
            st.subheader("Component Contributions")
            for comp in pm.component_scores:
                st.markdown(
                    f"{comp.icon} **{comp.display_name}:** "
                    f"`{comp.formatted_contribution}` — {comp.explanation}"
                )

    except ImportError:
        st.warning("Plotly not available. Install: `poetry add plotly`")
        for sig in pm.signals:
            st.write(f"**{sig.label}:** {sig.formatted}")
