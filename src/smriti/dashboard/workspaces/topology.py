"""
topology.py — TopologyWorkspace.

Investigative objective: Understand knowledge graph structure.
Views coordinated: Hub list + GraphView
"""

from __future__ import annotations

import streamlit as st
from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.components.graph_view import render_graph_view
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext


class TopologyWorkspace(BaseWorkspace):
    """Knowledge graph topology exploration workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.TOPOLOGY,
            investigative_objective="Explore knowledge graph structure and connectivity",
            default_lens=EpistemicLens.TOPOLOGY,
            default_explainability=0,
            primary_views=("hub_list", "graph_explorer"),
            navigation_strategy="topology_aware",
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state

        result = context.client.search_claims(
            filters={"semantic_role": "foundational_claim"},
            sort_field="centrality",
            sort_order="desc",
            limit=10,
        )
        hub_pms = DTOTransformer.to_claims_list(result.get("claims", []))

        col_graph, col_inspector = st.columns([3, 1])
        with col_inspector:
            st.subheader("Hub Claims")
            for pm in hub_pms:
                if st.button(f"🔵 {pm.text[:50]}", key=f"hub_{pm.claim_id}"):
                    context.state_manager.navigate_to(pm.claim_id, pm.text[:30])
                    st.rerun()

        with col_graph:
            if state.selected_claim_id:
                traversal = context.client.traverse(state.selected_claim_id, max_depth=2)
                if traversal:
                    render_graph_view(traversal, state.selected_claim_id)
                else:
                    st.info("Select a hub claim to explore its graph neighborhood.")
            else:
                stats = context.client.get_statistics()
                if stats:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Nodes", stats.get("total_claims", 0))
                    c2.metric("Edges", stats.get("total_edges", 0))
                    c3.metric("Partitions", stats.get("total_partitions", 0))
                    c4.metric("Contradictions", stats.get("total_contradictions", 0))
                st.info("Select a hub claim to explore its topology.")
