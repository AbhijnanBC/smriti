"""
statistics_panel.py — Statistics visualization from StatisticsPresentationModel.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.models.presentation import StatisticsPresentationModel


def render_statistics_panel_from_pm(stats: StatisticsPresentationModel) -> None:
    """Render global statistics from a StatisticsPresentationModel."""
    st.subheader("Knowledge Base Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Claims",        stats.total_claims)
    c2.metric("Total Edges",         stats.total_edges)
    c3.metric("Partitions",          stats.total_partitions)
    c4.metric("Contradictions",      stats.total_contradictions)

    col_ri, col_unc = st.columns(2)
    with col_ri:
        st.metric("Avg Reliability Index", f"{stats.avg_reliability:.1f}",
                  delta=f"Median: {stats.median_reliability:.1f}")
    with col_unc:
        st.metric("Avg Uncertainty Score", f"{stats.avg_uncertainty:.1f}")

    st.divider()

    # Reliability histogram
    if stats.reliability_histogram:
        st.subheader("Reliability Distribution")
        try:
            import plotly.graph_objects as go

            buckets = [h[0] for h in stats.reliability_histogram]
            counts  = [h[1] for h in stats.reliability_histogram]
            colors  = [
                "#c0392b" if i < 3 else "#f39c12" if i < 5
                else "#2980b9" if i < 7 else "#27ae60"
                for i in range(len(buckets))
            ]
            fig = go.Figure(go.Bar(x=buckets, y=counts, marker_color=colors))
            fig.update_layout(
                title="Reliability Index Distribution",
                xaxis_title="RI Bucket", yaxis_title="Claim Count", height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            for bucket, count in stats.reliability_histogram:
                st.write(f"{bucket}: {count}")

    # Partition summaries
    if stats.partition_summaries:
        st.subheader("Partition Summary")
        try:
            import pandas as pd
            rows = [
                {
                    "Partition":       ps.get("partition_id", "")[:8] + "...",
                    "Claims":          ps.get("node_count", 0),
                    "Avg Reliability": round(ps.get("avg_reliability", 0.0), 1),
                    "Supports":        ps.get("supports_count", 0),
                }
                for ps in stats.partition_summaries[:10]
            ]
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
        except ImportError:
            for ps in stats.partition_summaries[:5]:
                st.write(ps)