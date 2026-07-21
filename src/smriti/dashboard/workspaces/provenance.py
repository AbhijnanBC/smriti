"""
provenance.py — ProvenanceWorkspace.

Investigative objective: Trace knowledge lineage from claims to sources.
Views coordinated: ResultListView + custom provenance panel
"""

from __future__ import annotations

import streamlit as st

from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.result_list_view import ResultListView


class ProvenanceWorkspace(BaseWorkspace):
    """Knowledge lineage tracing workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.PROVENANCE,
            investigative_objective="Trace knowledge origin and lineage",
            default_lens=EpistemicLens.PROVENANCE,
            default_explainability=1,
            primary_views=("result_list", "provenance_trail", "evidence_chain"),
            navigation_strategy="provenance_trace",
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state

        result = context.client.search_claims(
            sort_field="support_count", sort_order="desc", limit=state.page_size,
        )
        claim_pms = DTOTransformer.to_claims_list(result.get("claims", []))

        col_list, col_prov = st.columns([1, 2])
        with col_list:
            st.subheader("Select Claim")
            ResultListView(
                state_manager=context.state_manager,
                claims=claim_pms,
                total=result.get("total", 0),
            ).render()

        with col_prov:
            if state.selected_claim_id:
                dto = context.client.get_claim(state.selected_claim_id, explain_level=1)
                if dto:
                    pm = DTOTransformer.to_claim_pm(dto)
                    from smriti.dashboard.components.claim_card import render_claim_card
                    render_claim_card(pm)
                    st.divider()
                    st.subheader("Provenance Trail")
                    st.markdown(f"**Source file:** `{pm.source_path}`")
                    if pm.context:
                        st.markdown(f"**Context:** {pm.context}")
                    st.markdown(f"**Supporting claims:** {pm.support_count}")
                    if st.button("Traverse Evidence Graph", key="prov_traverse"):
                        traversal = context.client.traverse(state.selected_claim_id, max_depth=2)
                        if traversal:
                            nodes = traversal.get("nodes", [])
                            st.markdown(f"**Reachable in 2 hops:** {len(nodes)} claims")
                            for n in nodes[:5]:
                                if n.get("claim_id") != state.selected_claim_id:
                                    st.markdown(
                                        f"- `{n.get('claim_id','')[:8]}` — {n.get('claim_text','')[:60]}..."
                                    )