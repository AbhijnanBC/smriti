"""
audit.py — AuditWorkspace.

Investigative objective: Audit why a claim has its reliability score.
Views coordinated: ResultListView + AuditView
"""

from __future__ import annotations

import streamlit as st

from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType, ExplainabilityLevel
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.result_list_view import ResultListView
from smriti.dashboard.views.audit_view import AuditView


class AuditWorkspace(BaseWorkspace):
    """Full auditability workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.AUDIT,
            investigative_objective="Audit and verify reasoning behind reliability scores",
            default_lens=EpistemicLens.AUDIT,
            default_explainability=ExplainabilityLevel.FULL_AUDIT,
            primary_views=("result_list", "audit"),
            navigation_strategy="audit_trail",
            max_results_per_page=15,
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        state = context.state
        st.info(
            "The Audit Workspace provides complete transparency into how every "
            "reliability score was produced — signals, policy weights, and decision records."
        )

        result = context.client.search_claims(
            sort_field="reliability_index", limit=state.page_size,
        )
        claim_pms = DTOTransformer.to_claims_list(result.get("claims", [])) or []

        audit_pm = None
        if state.selected_claim_id:
            explanation = context.client.get_explanation(
                state.selected_claim_id, level=ExplainabilityLevel.FULL_AUDIT,
            )
            if explanation:
                audit_pm = DTOTransformer.to_audit_pm(explanation)

        col_list, col_audit = st.columns([1, 2])
        with col_list:
            st.subheader("Select Claim to Audit")
            ResultListView(
                state_manager=context.state_manager,
                claims=claim_pms,
                total=result.get("total", 0),
            ).render()
        with col_audit:
            AuditView(audit=audit_pm).render()
            if not state.selected_claim_id:
                st.subheader("Active Scoring Policy")
                stats = context.client.get_statistics()
                if stats:
                    st.caption(f"Run: {stats.get('run_id', 'unknown')}")
                    st.caption(f"Total claims: {stats.get('total_claims', 0)}")