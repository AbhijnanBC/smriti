"""
claim_card.py — ClaimCard presentation component.

ALWAYS receives ClaimPresentationModel — never a raw dict.
"""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.models.presentation import ClaimPresentationModel


def render_claim_card(pm: ClaimPresentationModel, detailed: bool = True) -> None:
    """
    Render a single claim as an interactive detail card.

    Args:
        pm:       ClaimPresentationModel from DTOTransformer.
        detailed: If True, show support metrics and temporal status.
    """
    with st.container():
        st.markdown(
            f"**{pm.label_icon} {pm.label_display}** "
            f"— RI: `{pm.ri_formatted}` | Uncertainty: `{pm.uncertainty_formatted}`"
        )
        st.markdown(f"*{pm.text}*")

        if pm.context:
            st.caption(f"🏷️ Context: {pm.context}")
        if pm.role_display:
            st.caption(f"📍 Role: {pm.role_display}")
        if pm.document_id:
            st.caption(f"📄 Source: {pm.document_id}")

        if detailed:
            d1, d2, d3 = st.columns(3)
            d1.metric("Support", pm.support_count)
            d2.metric("Degree", pm.degree)
            d3.metric("Centrality", f"{pm.centrality:.3f}")

            if pm.temporal_status:
                st.caption(f"⏱️ Temporal: {pm.temporal_status.replace('_', ' ').title()}")

        st.divider()