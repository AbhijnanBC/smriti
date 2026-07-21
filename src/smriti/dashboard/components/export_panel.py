"""
export_panel.py — Export controls using ExportPipeline.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.export.pipeline import ExportPipeline
from smriti.dashboard.policies.policies import PolicyEngine
from smriti.exceptions import ExportPipelineError


def render_export_panel(export_pipeline: ExportPipeline, policy_engine: PolicyEngine) -> None:
    """Render export options as download buttons."""
    st.subheader("Export Knowledge Base")
    col_json, col_csv = st.columns(2)

    with col_json:
        allowed, reason = policy_engine.validate_export("json")
        if allowed:
            if st.button("Prepare JSON Export", key="ep_json"):
                with st.spinner("Exporting…"):
                    try:
                        result = export_pipeline.export("json")
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=result.content,
                            file_name=result.filename,
                            mime=result.mime_type,
                        )
                    except ExportPipelineError as e:
                        st.error(str(e))
        else:
            st.caption(f"JSON export disabled: {reason}")

    with col_csv:
        allowed, reason = policy_engine.validate_export("csv")
        if allowed:
            if st.button("Prepare CSV Export", key="ep_csv"):
                with st.spinner("Exporting…"):
                    try:
                        result = export_pipeline.export("csv")
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=result.content,
                            file_name=result.filename,
                            mime=result.mime_type,
                        )
                    except ExportPipelineError as e:
                        st.error(str(e))
        else:
            st.caption(f"CSV export disabled: {reason}")