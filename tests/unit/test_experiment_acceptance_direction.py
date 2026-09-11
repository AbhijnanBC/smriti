"""
Regression tests for _evaluate_acceptance()'s acceptance-direction fix
(P0-A, "FINAL REVIEW" round).

Before this fix, every metric was assumed higher-is-better
(`metrics[metric] < threshold` -> FAILED). EXP-003's
contradiction_violation_rate is lower-is-better (threshold 0.0 is a
MAXIMUM): a violation rate of 0.10 evaluated `0.10 < 0.0` -> False ->
PASSED, exactly backwards -- a real violation was reported as a pass.
These tests cover all four quadrants the review explicitly asked for,
plus the specific 0.0/0.01 case that was concretely wrong.
"""

from smriti.core.models import VerificationStatus
from smriti.evaluation.scientific.experiment import _evaluate_acceptance


def test_higher_is_better_above_threshold_passes():
    status = _evaluate_acceptance(
        {"precision": 0.80},
        {"precision": 0.70},
        {"precision": "higher_is_better"},
    )
    assert status == VerificationStatus.PASSED


def test_higher_is_better_below_threshold_fails():
    status = _evaluate_acceptance(
        {"precision": 0.50},
        {"precision": 0.70},
        {"precision": "higher_is_better"},
    )
    assert status == VerificationStatus.FAILED


def test_lower_is_better_below_threshold_passes():
    status = _evaluate_acceptance(
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": "lower_is_better"},
    )
    assert status == VerificationStatus.PASSED


def test_lower_is_better_above_threshold_fails():
    """The concrete bug: a real 10% violation rate must FAIL, not PASS."""
    status = _evaluate_acceptance(
        {"contradiction_violation_rate": 0.10},
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": "lower_is_better"},
    )
    assert status == VerificationStatus.FAILED


def test_exactly_the_reviews_named_case_0_0_le_0_0_passes():
    status = _evaluate_acceptance(
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": "lower_is_better"},
    )
    assert status == VerificationStatus.PASSED


def test_exactly_the_reviews_named_case_0_01_le_0_0_fails():
    status = _evaluate_acceptance(
        {"contradiction_violation_rate": 0.01},
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": "lower_is_better"},
    )
    assert status == VerificationStatus.FAILED


def test_missing_direction_defaults_to_higher_is_better():
    """No entry in `directions` for a metric -> higher_is_better, the
    correct default for every experiment except EXP-003 today."""
    status = _evaluate_acceptance({"macro_f1": 0.50}, {"macro_f1": 0.60}, {})
    assert status == VerificationStatus.FAILED
    status = _evaluate_acceptance({"macro_f1": 0.70}, {"macro_f1": 0.60}, {})
    assert status == VerificationStatus.PASSED


def test_missing_metric_from_results_warns_regardless_of_direction():
    status = _evaluate_acceptance(
        {},
        {"contradiction_violation_rate": 0.0},
        {"contradiction_violation_rate": "lower_is_better"},
    )
    assert status == VerificationStatus.WARNING


def test_exp003_registry_entry_actually_declares_lower_is_better():
    """Guards against the direction annotation silently disappearing
    from the live experiment registry, not just the helper function."""
    from smriti.evaluation.scientific.experiment import EXPERIMENT_REGISTRY

    exp003 = next(e for e in EXPERIMENT_REGISTRY if e.experiment_id == "EXP-003")
    assert exp003.acceptance_directions.get("contradiction_violation_rate") == "lower_is_better"
