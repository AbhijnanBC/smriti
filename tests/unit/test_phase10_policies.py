"""Unit tests for dashboard/policies/policies.py."""

import pytest
from smriti.dashboard.policies.policies import (
    InteractionPolicy, PolicyEngine, VisualizationPolicy,
    ComparisonPolicy, ExportPolicy,
)


@pytest.fixture
def engine():
    return PolicyEngine(InteractionPolicy())


def test_graph_size_within_limit(engine):
    allowed, reason = engine.validate_graph_size(30)
    assert allowed is True


def test_graph_size_exceeds_limit(engine):
    allowed, reason = engine.validate_graph_size(200)
    assert allowed is False
    assert "large" in reason.lower() or "max" in reason.lower()


def test_comparison_within_limit(engine):
    allowed, reason = engine.validate_comparison(2)
    assert allowed is True


def test_comparison_exceeds_limit(engine):
    allowed, reason = engine.validate_comparison(5)
    assert allowed is False


def test_json_export_allowed(engine):
    allowed, reason = engine.validate_export("json")
    assert allowed is True


def test_csv_export_allowed(engine):
    allowed, reason = engine.validate_export("csv")
    assert allowed is True


def test_graphml_export_disallowed_by_default():
    policy = InteractionPolicy(export=ExportPolicy(allow_graphml_export=False))
    engine = PolicyEngine(policy)
    allowed, reason = engine.validate_export("graphml")
    assert allowed is False


def test_policy_is_immutable():
    policy = InteractionPolicy()
    with pytest.raises(Exception):
        policy.visualization = VisualizationPolicy(max_nodes_in_graph=999)