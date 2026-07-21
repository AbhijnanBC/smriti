"""
conflict.py — ConflictWorkspace.

Investigative objective: Investigate and understand contradictions.
Views coordinated: Two ResultListViews (side A / side B) + ConflictView
"""

from __future__ import annotations

import streamlit as st

from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.conflict_view import ConflictView


class ConflictWorkspace(BaseWorkspace):
    """Contradiction investigation workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.CONFLICT,
            investigative_objective="Investigate contradictions and competing knowledge",
            default_lens=EpistemicLens.CONFLICT,
            default_explainability=2,
            primary_views=("side_a_list", "side_b_list", "conflict"),
            navigation_strategy="contradiction_aware",
            max_results_per_page=15,
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state
        st.info(
            "This workspace focuses on claims in semantic contradictions. "
            "Claims in different partitions contain competing knowledge."
        )

        result = context.client.search_claims(
            sort_field="conflict_pressure", sort_order="desc", limit=state.page_size,
        )
        claims = result.get("claims", [])
        if not claims:
            st.warning("No contradictions detected in this knowledge base.")
            return

        partitions: dict = {}
        for c in claims:
            pid = c.get("partition_id", "unknown")
            partitions.setdefault(pid, []).append(c)

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Competing Claims — Side A")
            for claim in list(partitions.values())[0][:5] if partitions else []:
                cid = claim.get("claim_id", "")
                if st.button(f"📌 {claim.get('claim_text','')[:60]}...", key=f"conflict_a_{cid}"):
                    current = state.comparison_claim_ids
                    context.state_manager.set_comparison_claims(
                        (cid, current[1] if len(current) > 1 else "")
                    )
                    st.rerun()

        with col_right:
            st.subheader("Competing Claims — Side B")
            for claim in list(partitions.values())[1][:5] if len(partitions) >= 2 else []:
                cid = claim.get("claim_id", "")
                if st.button(f"📌 {claim.get('claim_text','')[:60]}...", key=f"conflict_b_{cid}"):
                    current = state.comparison_claim_ids
                    context.state_manager.set_comparison_claims(
                        (current[0] if len(current) > 0 else "", cid)
                    )
                    st.rerun()

        if len(state.comparison_claim_ids) >= 2 and all(state.comparison_claim_ids):
            st.divider()
            st.subheader("Side-by-Side Comparison")
            dto_a = context.client.get_claim(state.comparison_claim_ids[0], explain_level=2)
            dto_b = context.client.get_claim(state.comparison_claim_ids[1], explain_level=2)
            pm_a = DTOTransformer.to_claim_pm(dto_a) if dto_a else None
            pm_b = DTOTransformer.to_claim_pm(dto_b) if dto_b else None
            ConflictView(claim_a=pm_a, claim_b=pm_b).render()