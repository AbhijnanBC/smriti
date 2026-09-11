"""conflict_view.py — ConflictView: side-by-side contradiction panel."""

from __future__ import annotations

import streamlit as st
from smriti.dashboard.models.presentation import ClaimPresentationModel
from smriti.dashboard.views.base_view import BaseView


class ConflictView(BaseView):
    """Renders side-by-side contradiction comparison from two ClaimPresentationModels."""

    def __init__(
        self,
        claim_a: ClaimPresentationModel | None = None,
        claim_b: ClaimPresentationModel | None = None,
    ) -> None:
        self._claim_a = claim_a
        self._claim_b = claim_b

    # Narrows BaseView's generic **kwargs contract to this view's specific
    # fields; ViewCoordinator always dispatches via **kwargs (Any-typed),
    # so this is safe at every real call site.
    def refresh(  # type: ignore[override]
        self,
        claim_a: ClaimPresentationModel | None = None,
        claim_b: ClaimPresentationModel | None = None,
    ) -> None:
        self._claim_a = claim_a
        self._claim_b = claim_b

    def supports(self, context) -> bool:
        return self._claim_a is not None and self._claim_b is not None

    def render(self) -> None:
        if not self._claim_a or not self._claim_b:
            st.info("Select claims on both sides to compare.")
            return
        col_a, col_div, col_b = st.columns([5, 1, 5])
        self._render_side(col_a, self._claim_a, "Claim A")
        with col_div:
            st.markdown("<br><br><br>⚡<br>VS", unsafe_allow_html=True)
        self._render_side(col_b, self._claim_b, "Claim B")

    @staticmethod
    def _render_side(col, pm: ClaimPresentationModel, label: str) -> None:
        with col:
            st.markdown(f"**{label}** — RI: `{pm.ri_formatted}` ({pm.label_display})")
            st.markdown(f"*{pm.text}*")
            if pm.context:
                st.caption(f"Context: {pm.context}")
            st.caption(f"Evidence: {pm.evidence_strength:.3f}")
            st.caption(f"Conflict Pressure: {pm.conflict_pressure:.3f}")
            st.caption(f"Support count: {pm.support_count}")
            if pm.explanation_summary:
                st.caption(f"📝 {pm.explanation_summary}")
