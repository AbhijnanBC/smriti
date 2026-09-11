"""audit_view.py — AuditView: renders 4-level explainability from AuditPresentationModel."""

from __future__ import annotations

import streamlit as st
from smriti.core.models import ExplainabilityLevel
from smriti.dashboard.models.presentation import AuditPresentationModel
from smriti.dashboard.views.base_view import BaseView


class AuditView(BaseView):
    """Renders audit trail at any explainability level."""

    def __init__(self, audit: AuditPresentationModel | None = None) -> None:
        self._audit = audit

    def refresh(self, audit: AuditPresentationModel | None = None) -> None:
        self._audit = audit

    def supports(self, context) -> bool:
        return self._audit is not None

    def render(self) -> None:
        if not self._audit:
            st.info("Select a claim to view its complete audit trail.")
            return

        pm = self._audit

        # ── Summary metrics ──────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Reliability Index", pm.reliability_index)
        c2.metric("Calibration", pm.calibration_label.replace("_", " ").title())
        c3.metric("Uncertainty", pm.uncertainty_score)

        # ── Explainability levels ──────────────────────────────────────────────
        level = pm.explainability_level

        if level >= ExplainabilityLevel.SUMMARY:
            if pm.summary:
                st.markdown(f"> **Summary:** {pm.summary}")
            if pm.dominant_signal:
                st.markdown(f"✅ **Primary strength:** `{pm.dominant_signal.replace('_', ' ')}`")
            if pm.limiting_signal:
                st.markdown(f"⚠️ **Main limitation:** `{pm.limiting_signal.replace('_', ' ')}`")

        if level >= ExplainabilityLevel.DETAILED:
            st.divider()
            st.subheader("Signal Measurements")
            # Guard against None signals
            for sig in pm.signals or []:
                st.progress(float(sig.value), text=f"{sig.label}: {sig.formatted}")

            st.subheader("Component Contributions")
            # Guard against None component_scores
            for comp in pm.component_scores or []:
                st.markdown(
                    f"{comp.icon} **{comp.display_name}:** `{comp.formatted_contribution}` — {comp.explanation}"
                )

        if level >= ExplainabilityLevel.FULL_AUDIT:
            st.divider()
            st.subheader("Audit Trail")
            if pm.audit_trail:
                st.json(pm.audit_trail)

            if pm.recommendations:
                st.subheader("Recommendations")
                # Guard against None recommendations (though it should be a list)
                for rec in pm.recommendations or []:
                    st.markdown(f"💡 {rec}")

            if pm.policy_snapshot:
                with st.expander("Scoring Policy (active at time of computation)"):
                    st.json(pm.policy_snapshot)
