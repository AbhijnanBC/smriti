"""
graph_view.py — Graph topology visualization using Plotly.
Operates on traversal dict directly (graph structure, not claim presentation).
"""

from __future__ import annotations

from typing import Any, Dict
import streamlit as st


def render_graph_view(traversal: Dict[str, Any], center_id: str) -> None:
    """
    Render a graph neighborhood using Plotly scatter-with-lines.

    Args:
        traversal:  Traversal result dict from ServiceClient.
        center_id:  The starting claim_id (rendered at center).
    """
    try:
        import plotly.graph_objects as go
        import math

        nodes = traversal.get("nodes", [])
        edges = traversal.get("edges", [])

        if not nodes:
            st.info("No graph data to display.")
            return

        positions = {}
        n = len(nodes)
        for i, node in enumerate(nodes):
            nid = node.get("claim_id", "")
            if nid == center_id:
                positions[nid] = (0, 0)
            else:
                angle = 2 * math.pi * i / max(1, n - 1)
                positions[nid] = (math.cos(angle) * 2, math.sin(angle) * 2)

        edge_x, edge_y = [], []
        for edge in edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            if src in positions and tgt in positions:
                x0, y0 = positions[src]
                x1, y1 = positions[tgt]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color="#888"),
            hoverinfo="none", mode="lines",
        )

        node_x = [positions[n.get("claim_id", "")][0] for n in nodes if n.get("claim_id") in positions]
        node_y = [positions[n.get("claim_id", "")][1] for n in nodes if n.get("claim_id") in positions]
        node_text = [
            f"{n.get('claim_text', '')[:40]}... (RI: {n.get('reliability_index', 0):.1f})"
            for n in nodes if n.get("claim_id") in positions
        ]
        node_colors = [
            "red" if n.get("claim_id") == center_id else "blue"
            for n in nodes if n.get("claim_id") in positions
        ]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=node_text,
            textposition="top center",
            marker=dict(size=12, color=node_colors),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f"Graph Neighborhood (depth=2 from {center_id[:8]})",
                showlegend=False, hovermode="closest", height=450,
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.warning("Plotly not installed. Install: `poetry add plotly`")
        nodes = traversal.get("nodes", [])
        st.write(f"Graph has {len(nodes)} nodes in this neighborhood.")