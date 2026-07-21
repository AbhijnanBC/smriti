"""Unit tests for scoring/explanation.py."""

import pytest
from smriti.core.models import ComponentScore
from smriti.scoring.explanation import build_explanation


def make_component(name: str, contribution: float, direction: str = "positive") -> ComponentScore:
    return ComponentScore(
        signal_id=name, normalized_value=0.8, policy_weight=0.25,
        adjusted_value=0.8, contribution=contribution, direction=direction,
        explanation="Test explanation",
    )


def test_explanation_has_summary():
    comps = [make_component("evidence_strength", 18.0), make_component("conflict_pressure", -8.0, "negative")]
    explanation = build_explanation(75.0, comps)
    assert explanation.summary and len(explanation.summary) > 0


def test_dominant_and_limiting_signals():
    comps = [
        make_component("evidence_strength", 22.0),
        make_component("topology_strength", 12.0),
        make_component("conflict_pressure", -15.0, "negative"),
        make_component("temporal_stability", -5.0, "negative"),
    ]
    explanation = build_explanation(65.0, comps)
    assert explanation.dominant_signal == "evidence_strength"
    assert explanation.limiting_signal == "conflict_pressure"


def test_strengths_and_weaknesses():
    comps = [
        make_component("evidence_strength", 20.0),
        make_component("source_diversity", 15.0),
        make_component("conflict_pressure", -10.0, "negative"),
    ]
    explanation = build_explanation(80.0, comps)
    assert len(explanation.strengths) >= 1 and len(explanation.weaknesses) >= 1


def test_empty_components():
    explanation = build_explanation(50.0, [])
    assert explanation.summary
    assert explanation.dominant_signal == "none"
    assert explanation.limiting_signal == "none"


def test_high_reliability_label():
    comps = [make_component("evidence_strength", 30.0)]
    exp = build_explanation(90.0, comps)
    assert "reliable" in exp.summary.lower() or "high" in exp.summary.lower()