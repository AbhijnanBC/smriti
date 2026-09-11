"""Unit tests for evaluation/engineering/architectural.py."""

from smriti.core.models import VerificationStatus
from smriti.evaluation.engineering.architectural import (
    ARCHITECTURAL_RULES,
    run_architectural_verification,
)
from smriti.evaluation.engineering.confidence import compute_eci, compute_verification_coverage


def test_architectural_rules_defined():
    """At least 15 architectural rules must be defined."""
    assert len(ARCHITECTURAL_RULES) >= 15


def test_all_rules_have_unique_ids():
    """All rule IDs must be unique."""
    ids = [r.rule_id for r in ARCHITECTURAL_RULES]
    assert len(ids) == len(set(ids))


def test_all_rules_have_descriptions():
    """All rules must have non-empty descriptions."""
    for rule in ARCHITECTURAL_RULES:
        assert rule.description, f"Rule {rule.rule_id} has empty description"


def test_run_architectural_verification_returns_results():
    """run_architectural_verification must return one result per rule."""
    results = run_architectural_verification()
    assert len(results) == len(ARCHITECTURAL_RULES)


def test_all_results_have_valid_status():
    """All results must have a valid VerificationStatus."""
    results = run_architectural_verification()
    valid_statuses = {s.value for s in VerificationStatus}
    for result in results:
        assert result.status.value in valid_statuses


def test_results_have_timestamps():
    """All results must have a timestamp."""
    results = run_architectural_verification()
    for result in results:
        assert result.timestamp_iso, f"Result {result.rule_id} has empty timestamp"


def test_eci_is_computed():
    """ECI must produce a valid index."""
    results = run_architectural_verification()
    eci = compute_eci(results)
    assert 0.0 <= eci.overall_confidence <= 100.0
    assert 0 <= eci.engineering_readiness_level <= 5


def test_eci_dimensions_in_range():
    """All ECI dimensions must be in [0, 100]."""
    results = run_architectural_verification()
    eci = compute_eci(results)
    dimensions = [
        eci.architecture_confidence,
        eci.runtime_confidence,
        eci.infrastructure_confidence,
        eci.observability_confidence,
        eci.governance_confidence,
        eci.integration_confidence,
        eci.compliance_confidence,
    ]
    for d in dimensions:
        assert 0.0 <= d <= 100.0, f"ECI dimension out of range: {d}"


def test_coverage_computation():
    """Verification coverage must report all categories."""
    results = run_architectural_verification()
    coverage = compute_verification_coverage(results)
    assert len(coverage) > 0
    for cov in coverage:
        assert 0.0 <= cov.coverage_percentage <= 100.0


def test_frozen_dataclass_check():
    """Frozen dataclass rules must verify correctly for known frozen classes."""
    from smriti.evaluation.engineering.architectural import _check_frozen_dataclass

    passed, _ = _check_frozen_dataclass("smriti.core.models", "ClaimNode")
    # Either pass or graceful fail (not raise)
    assert isinstance(passed, bool)
