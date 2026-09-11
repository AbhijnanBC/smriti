"""Unit tests for evaluation/statistical/bootstrap.py (P1-11)."""

from smriti.evaluation.statistical.bootstrap import (
    bootstrap_mean_ci,
    bootstrap_proportion_ci,
    bootstrap_proportion_ci_clustered,
)


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
    large = bootstrap_proportion_ci(
        [True, True, True, False] * 20, n_resamples=1000, seed=1
    )  # n=80
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


def test_clustered_ci_point_estimate_matches_raw_proportion():
    outcomes = [True] * 7 + [False] * 3
    cluster_ids = ["doc_a"] * 5 + ["doc_b"] * 5
    result = bootstrap_proportion_ci_clustered(outcomes, cluster_ids, n_resamples=500)
    assert result.point_estimate == 0.7


def test_clustered_ci_bounds_are_ordered_and_within_range():
    outcomes = [True, True, True, False, False, True, True, False, True, True]
    cluster_ids = ["doc_a"] * 3 + ["doc_b"] * 3 + ["doc_c"] * 4
    result = bootstrap_proportion_ci_clustered(outcomes, cluster_ids, n_resamples=500)
    assert 0.0 <= result.ci_lower <= result.point_estimate <= result.ci_upper <= 1.0


def test_clustered_ci_is_wider_than_naive_when_outcomes_correlate_with_cluster():
    """The whole point of clustering: when an item's outcome is entirely
    determined by which document it came from (perfect within-cluster
    correlation), the cluster bootstrap must report more uncertainty than
    treating each item as an independent draw."""
    # 2 clusters of 10 items each; every item in doc_a is True, every item
    # in doc_b is False -- so the real amount of independent evidence is
    # "2 documents", not "20 items".
    outcomes = [True] * 10 + [False] * 10
    cluster_ids = ["doc_a"] * 10 + ["doc_b"] * 10
    naive = bootstrap_proportion_ci(outcomes, n_resamples=1000, seed=3)
    clustered = bootstrap_proportion_ci_clustered(outcomes, cluster_ids, n_resamples=1000, seed=3)
    naive_width = naive.ci_upper - naive.ci_lower
    clustered_width = clustered.ci_upper - clustered.ci_lower
    assert clustered_width > naive_width


def test_clustered_ci_single_cluster_returns_point_estimate_as_interval():
    outcomes = [True, True, False, True]
    cluster_ids = ["doc_a"] * 4
    result = bootstrap_proportion_ci_clustered(outcomes, cluster_ids, n_resamples=500)
    assert result.ci_lower == result.ci_upper == result.point_estimate


def test_clustered_ci_empty_outcomes_returns_zero_without_crashing():
    result = bootstrap_proportion_ci_clustered([], [], n_resamples=100)
    assert result.point_estimate == 0.0
    assert result.n_items == 0
