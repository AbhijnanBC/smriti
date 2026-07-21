"""explanation.py — Structured explanation builder for Phase 8."""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.models import ComponentScore, ReliabilityExplanation

logger = structlog.get_logger(__name__)

MAX_EXPLANATION_SIGNALS = 3


def build_explanation(
    reliability_index: float,
    component_scores: List[ComponentScore],
) -> ReliabilityExplanation:
    """Build a structured explanation from ComponentScores."""
    positive = sorted(
        [c for c in component_scores if c.contribution > 0],
        key=lambda c: c.contribution, reverse=True,
    )
    negative = sorted(
        [c for c in component_scores if c.contribution < 0],
        key=lambda c: c.contribution,
    )

    strengths = tuple(
        (c.signal_id, round(c.contribution, 2))
        for c in positive[:MAX_EXPLANATION_SIGNALS]
    )
    weaknesses = tuple(
        (c.signal_id, round(c.contribution, 2))
        for c in negative[:MAX_EXPLANATION_SIGNALS]
    )

    dominant = positive[0].signal_id if positive else "none"
    limiting = negative[0].signal_id if negative else "none"

    summary = _build_summary(reliability_index, positive, negative)
    recommendations = _build_recommendations(component_scores)

    return ReliabilityExplanation(
        summary=summary,
        strengths=strengths,
        weaknesses=weaknesses,
        dominant_signal=dominant,
        limiting_signal=limiting,
        recommendations=recommendations,
    )


def _build_summary(ri: float, positive: list, negative: list) -> str:
    if ri >= 80:
        base = "Highly reliable."
    elif ri >= 65:
        base = "Reliable."
    elif ri >= 45:
        base = "Moderately reliable."
    elif ri >= 25:
        base = "Limited reliability."
    else:
        base = "Very low reliability."

    if positive:
        top = positive[0].signal_id.replace("_", " ").capitalize()
        base += f" Primary strength: {top}."

    if negative:
        top_neg = negative[0].signal_id.replace("_", " ").capitalize()
        base += f" Main concern: {top_neg}."

    return base


def _build_recommendations(component_scores: List[ComponentScore]) -> tuple:
    recs = []
    score_map = {c.signal_id: c.contribution for c in component_scores}

    if score_map.get("conflict_pressure", 0) < -10:
        recs.append("Review contradicting claims in other partitions.")
    if score_map.get("evidence_independence", 1.0) < 0:
        recs.append("Seek supporting evidence from additional independent sources.")
    if score_map.get("source_diversity", 1.0) < 0.05:
        recs.append("Diversify evidence across more document sources.")
    if score_map.get("temporal_stability", 1.0) < 0.05:
        recs.append("Monitor for temporal evolution of this claim.")
    if not recs:
        recs.append("Maintain current evidence quality.")

    return tuple(recs)