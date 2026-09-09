"""Unit tests for evaluation/statistical/bootstrap.py (P1-11)."""

from smriti.evaluation.statistical.bootstrap import bootstrap_proportion_ci, bootstrap_mean_ci


def test_proportion_ci_point_estimate_matches_raw_proportion():
    outcomes = [True] * 7 + [False] * 3
    result = bootstrap_proportion_ci(outcomes, n_resamples=500)
    assert result.point_estimate == 0.7


def test_proportion_ci_bounds_are_ordered_and_within_range():
    outcomes = [True] * 7 + [False] * 3
    result = bootstrap_proportion_ci(outcomes, n_resamples=500)
    assert 0.0 <= result.ci_lower <= result.point_estimate <= result.ci_upper <= 1.0


def test_proportion_ci_all_true_gives_tight_interval_near_one():
    outcomes = [True] * 20
    result = bootstrap_proportion_ci(outcomes, n_resamples=500)
    assert result.point_estimate == 1.0
    assert result.ci_lower == 1.0
    assert result.ci_upper == 1.0


def test_proportion_ci_wider_for_smaller_samples():
    """A smaller sample should generally produce a wider (or equal) CI
    than a larger sample with the same underlying proportion."""
    small = bootstrap_proportion_ci([True, True, True, False] * 2, n_resamples=1000, seed=1)  # n=8
    large = bootstrap_proportion_ci([True, True, True, False] * 20, n_resamples=1000, seed=1)  # n=80
    small_width = small.ci_upper - small.ci_lower
    large_width = large.ci_upper - large.ci_lower
    assert small_width >= large_width


def test_empty_outcomes_returns_zero_without_crashing():
    result = bootstrap_proportion_ci([], n_resamples=100)
    assert result.point_estimate == 0.0
    assert result.n_items == 0


def test_mean_ci_point_estimate_matches_raw_mean():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = bootstrap_mean_ci(values, n_resamples=500)
    assert result.point_estimate == 3.0


def test_bootstrap_is_deterministic_given_seed():
    outcomes = [True, False, True, True, False, True, True, True, False, True]
    r1 = bootstrap_proportion_ci(outcomes, n_resamples=500, seed=7)
    r2 = bootstrap_proportion_ci(outcomes, n_resamples=500, seed=7)
    assert r1 == r2
