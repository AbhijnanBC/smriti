"""Unit tests for evaluation/statistical/analysis.py."""

import pytest
from smriti.evaluation.statistical.analysis import (
    STANDARD_THREATS,
    assess_reproducibility,
    compute_effect_size,
    compute_statistical_analysis,
)


def test_statistical_analysis_single_value():
    """Single value produces valid stats."""
    sa = compute_statistical_analysis("metric", [0.85])
    assert sa.mean == 0.85
    assert sa.n_samples == 1
    assert sa.std_dev == 0.0


def test_statistical_analysis_multiple_values():
    """Multiple values compute correct mean and CI."""
    values = [0.80, 0.85, 0.82, 0.83, 0.81]
    sa = compute_statistical_analysis("metric", values)
    assert abs(sa.mean - 0.822) < 0.01
    assert sa.n_samples == 5
    assert sa.ci_lower < sa.mean < sa.ci_upper


def test_statistical_analysis_empty():
    """Empty values produce zero stats."""
    sa = compute_statistical_analysis("metric", [])
    assert sa.n_samples == 0
    assert sa.mean == 0.0


def test_effect_size_no_effect():
    """Equal conditions produce near-zero effect size."""
    es = compute_effect_size("m", "A", [0.8, 0.8, 0.8], "B", [0.8, 0.8, 0.8])
    assert abs(es.cohens_d) < 0.01
    assert es.magnitude == "negligible"


def test_effect_size_large():
    """Large difference produces large effect size."""
    es = compute_effect_size("m", "A", [0.9, 0.9, 0.9], "B", [0.1, 0.1, 0.1])
    assert abs(es.cohens_d) > 0.8
    assert es.magnitude == "large"


def test_reproducibility_excellent():
    """Identical values produce excellent reproducibility."""
    ra = assess_reproducibility("EXP-001", "metric", [0.85, 0.85, 0.85], cv_threshold=0.05)
    assert ra.coefficient_of_variation == 0.0
    assert ra.reproducibility_level == "excellent"
    assert ra.is_reproducible is True


def test_reproducibility_poor():
    """High variance produces poor reproducibility."""
    ra = assess_reproducibility("EXP-001", "metric", [0.2, 0.8, 0.4, 0.9], cv_threshold=0.05)
    assert ra.reproducibility_level == "poor"
    assert ra.is_reproducible is False


def test_standard_threats_defined():
    """Standard threats catalogue must have at least 6 entries."""
    assert len(STANDARD_THREATS) >= 6


def test_threats_are_frozen():
    """ThreatToValidity must be immutable."""
    threat = STANDARD_THREATS[0]
    with pytest.raises(Exception):
        threat.description = "modified"
