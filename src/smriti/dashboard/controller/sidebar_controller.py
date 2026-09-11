"""
sidebar_controller.py — SidebarController for Phase 10.

Owns sidebar rendering exclusively.
Extracted from app.py to keep it focused on one concern.

Responsibilities:
    ✅ Render workspace selector
    ✅ Render explainability depth selector
    ✅ Render sort controls
    ✅ Render export panel
    ✅ Dispatch state transitions via EpistemicStateManager
    ❌ Never renders workspace content
    ❌ Never accesses Phase 9 directly
"""

from __future__ import annotations

import streamlit as st
from smriti.core.models import ExplainabilityLevel, WorkspaceType
from smriti.dashboard.policies.policies import PolicyEngine
from smriti.dashboard.state.epistemic_state import EpistemicStateManager

WORKSPACE_DISPLAY = {
    WorkspaceType.RESEARCH: "🔍 Research",
    WorkspaceType.RELIABILITY: "📊 Reliability",
    WorkspaceType.CONFLICT: "⚡ Conflict",
    WorkspaceType.AUDIT: "🔎 Audit",
    WorkspaceType.PROVENANCE: "📜 Provenance",
    WorkspaceType.STATISTICS: "📈 Statistics",
    WorkspaceType.TOPOLOGY: "🕸️ Topology",
}

EXPLAINABILITY_LABELS = {
    ExplainabilityLevel.NONE: "None (fastest)",
    ExplainabilityLevel.SUMMARY: "Summary",
    ExplainabilityLevel.DETAILED: "Detailed",
    ExplainabilityLevel.FULL_AUDIT: "Full Audit",
}

SORT_OPTIONS = {
    "reliability_index": "Reliability (highest first)",
    "uncertainty_score": "Uncertainty (highest first)",
    "support_count": "Evidence Count",
    "conflict_pressure": "Conflict Pressure",
}


class SidebarController:
    """Renders and owns the Streamlit sidebar."""

    def render(
        self,
        state_manager: EpistemicStateManager,
        policy_engine: PolicyEngine,
        export_pipeline,
    ) -> None:
        state = state_manager.state

        st.sidebar.title("🧠 SMRITI")
        st.sidebar.caption(f"Run: `{state.run_id[:12]}...`")
        st.sidebar.divider()

        # ── Workspace selector ────────────────────────────────────────────────
        st.sidebar.subheader("Workspace")
        workspace_labels = list(WORKSPACE_DISPLAY.values())
        workspace_types = list(WORKSPACE_DISPLAY.keys())
        current_idx = workspace_types.index(state.workspace_type)
        selected_idx = st.sidebar.radio(
            "Select workspace",
            options=range(len(workspace_labels)),
            format_func=lambda i: workspace_labels[i],
            index=current_idx,
            label_visibility="collapsed",
        )
        if selected_idx != current_idx:
            state_manager.activate_workspace(workspace_types[selected_idx])
            st.rerun()

        st.sidebar.divider()

        # ── Explainability ────────────────────────────────────────────────────
        st.sidebar.subheader("Explainability")
        current_level = state.explainability_level
        selected_level = st.sidebar.selectbox(
            "Explainability depth",
            options=list(EXPLAINABILITY_LABELS.keys()),
            format_func=lambda l: EXPLAINABILITY_LABELS[l],
            index=current_level,
            label_visibility="collapsed",
        )
        if selected_level != current_level:
            state_manager.set_explainability(selected_level)
            st.rerun()

        st.sidebar.divider()

        # ── Sort ──────────────────────────────────────────────────────────────
        st.sidebar.subheader("Sort Claims By")
        current_sort = state.sort_field
        selected_sort = st.sidebar.selectbox(
            "Sort field",
            options=list(SORT_OPTIONS.keys()),
            format_func=lambda k: SORT_OPTIONS[k],
            index=(
                list(SORT_OPTIONS.keys()).index(current_sort) if current_sort in SORT_OPTIONS else 0
            ),
            label_visibility="collapsed",
        )
        if selected_sort != current_sort:
            state_manager.set_sort(selected_sort, "desc")
            st.rerun()

        st.sidebar.divider()

        # ── Export ────────────────────────────────────────────────────────────
        st.sidebar.subheader("Export")
        self._render_export(policy_engine, export_pipeline)

        # ── Session info ──────────────────────────────────────────────────────
        st.sidebar.divider()
        st.sidebar.caption(f"Events recorded: {len(state_manager.event_log)}")
        st.sidebar.caption(f"Workspace: {state.workspace_status.value}")
        if st.sidebar.button("Clear Selection"):
            state_manager.deselect_claim()
            state_manager.clear_filters()
            st.rerun()

    @staticmethod
    def _render_export(policy_engine: PolicyEngine, export_pipeline) -> None:
        """Render export download buttons in sidebar."""
        from smriti.exceptions import ExportPipelineError

        col_json, col_csv = st.sidebar.columns(2)
        with col_json:
            allowed, _ = policy_engine.validate_export("json")
            if allowed and st.button("JSON", use_container_width=True, key="sb_export_json"):
                with st.spinner("Exporting JSON…"):
                    try:
                        result = export_pipeline.export("json")
                        st.download_button(
                            "⬇️ JSON",
                            data=result.content,
                            file_name=result.filename,
                            mime=result.mime_type,
                            key="dl_json",
                        )
                    except ExportPipelineError as e:
                        st.sidebar.error(str(e))
        with col_csv:
            allowed, _ = policy_engine.validate_export("csv")
            if allowed and st.button("CSV", use_container_width=True, key="sb_export_csv"):
                with st.spinner("Exporting CSV…"):
                    try:
                        result = export_pipeline.export("csv")
                        st.download_button(
                            "⬇️ CSV",
                            data=result.content,
                            file_name=result.filename,
                            mime=result.mime_type,
                            key="dl_csv",
                        )
                    except ExportPipelineError as e:
                        st.sidebar.error(str(e))
