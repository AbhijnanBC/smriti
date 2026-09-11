"""
bootstrap.py — Bootstrap confidence intervals (P1-11).

The existing StatisticalAnalysis machinery (analysis.py) computes a
t/z-based CI from a handful of REPEATED-RUN values (e.g. [0.85, 0.86] from
2-3 runs of the same experiment) -- that is the right tool for
run-to-run variance, but it is the wrong tool for reporting uncertainty
on a metric like "precision over N sampled items", where the real
source of uncertainty is SAMPLING (which N items happened to be drawn),
not run-to-run noise. For that, a nonparametric bootstrap over the
per-item outcomes is the standard approach and does not assume normality.

This module is deliberately dependency-free (no scipy/numpy required)
so it can be used anywhere in the codebase without adding a dependency.
"""

from __future__ import annotations

import random
import statistics
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class BootstrapResult:
    point_estimate: float
    ci_lower: float
    ci_upper: float
    n_items: int
    n_resamples: int
    confidence_level: float


def bootstrap_proportion_ci(
    outcomes: Sequence[bool],
    confidence_level: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 42,
) -> BootstrapResult:
    """
    Percentile bootstrap CI for a proportion (e.g. precision, recall,
    accuracy) computed from a sequence of per-item boolean outcomes
    (True = correct/positive).

    Args:
        outcomes:         One bool per scored item.
        confidence_level: e.g. 0.95 for a 95% CI.
        n_resamples:      Number of bootstrap resamples.
        seed:             Fixed seed for reproducibility.
    """
    n = len(outcomes)
    if n == 0:
        return BootstrapResult(0.0, 0.0, 0.0, 0, n_resamples, confidence_level)

    point_estimate = sum(outcomes) / n
    if n == 1:
        return BootstrapResult(
            point_estimate, point_estimate, point_estimate, n, n_resamples, confidence_level
        )

    rng = random.Random(seed)
    outcomes_list = list(outcomes)
    resample_means: list[float] = []
    for _ in range(n_resamples):
        resample = [outcomes_list[rng.randrange(n)] for _ in range(n)]
        resample_means.append(sum(resample) / n)

    resample_means.sort()
    alpha = 1.0 - confidence_level
    lower_idx = int((alpha / 2) * n_resamples)
    upper_idx = int((1 - alpha / 2) * n_resamples) - 1
    lower_idx = max(0, min(lower_idx, n_resamples - 1))
    upper_idx = max(0, min(upper_idx, n_resamples - 1))

    return BootstrapResult(
        point_estimate=round(point_estimate, 4),
        ci_lower=round(resample_means[lower_idx], 4),
        ci_upper=round(resample_means[upper_idx], 4),
        n_items=n,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
    )


def bootstrap_proportion_ci_clustered(
    outcomes: Sequence[bool],
    cluster_ids: Sequence,
    confidence_level: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 42,
) -> BootstrapResult:
    """
    Cluster (block) bootstrap CI for a proportion, resampling whole
    CLUSTERS with replacement rather than individual items.

    RECTIFIED (external review item 40): bootstrap_proportion_ci() treats
    every item as an independent draw, but several claims from the same
    source document, or several relationship pairs anchored on the same
    adversarial document, are not independent observations -- they share
    whatever made that one document unusual. Resampling items directly
    understates the true sampling uncertainty whenever items cluster this
    way. The cluster bootstrap instead resamples at the cluster level (here,
    typically source document): each resample draws len(unique clusters)
    clusters with replacement, keeping every item that belongs to a drawn
    cluster (so a cluster's item count carries into the resample, standard
    for a block/cluster bootstrap), and computes the proportion over the
    resulting pooled items.

    Args:
        outcomes:    One bool per scored item (True = correct/positive).
        cluster_ids: One cluster identifier per item, same length and
                     order as `outcomes` (e.g. the source document ID).
        confidence_level, n_resamples, seed: as in bootstrap_proportion_ci.
    """
    n = len(outcomes)
    if n == 0 or len(cluster_ids) != n:
        return BootstrapResult(0.0, 0.0, 0.0, 0, n_resamples, confidence_level)

    point_estimate = sum(outcomes) / n

    by_cluster: dict = {}
    for outcome, cid in zip(outcomes, cluster_ids, strict=False):
        by_cluster.setdefault(cid, []).append(outcome)
    clusters = list(by_cluster.values())
    n_clusters = len(clusters)

    if n_clusters <= 1:
        return BootstrapResult(
            point_estimate, point_estimate, point_estimate, n, n_resamples, confidence_level
        )

    rng = random.Random(seed)
    resample_means: list[float] = []
    for _ in range(n_resamples):
        drawn = [clusters[rng.randrange(n_clusters)] for _ in range(n_clusters)]
        pooled = [item for cluster in drawn for item in cluster]
        resample_means.append(sum(pooled) / len(pooled))

    resample_means.sort()
    alpha = 1.0 - confidence_level
    lower_idx = int((alpha / 2) * n_resamples)
    upper_idx = int((1 - alpha / 2) * n_resamples) - 1
    lower_idx = max(0, min(lower_idx, n_resamples - 1))
    upper_idx = max(0, min(upper_idx, n_resamples - 1))

    return BootstrapResult(
        point_estimate=round(point_estimate, 4),
        ci_lower=round(resample_means[lower_idx], 4),
        ci_upper=round(resample_means[upper_idx], 4),
        n_items=n,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
    )


def bootstrap_mean_ci(
    values: Sequence[float],
    confidence_level: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 42,
) -> BootstrapResult:
    """Percentile bootstrap CI for the mean of a continuous metric."""
    n = len(values)
    if n == 0:
        return BootstrapResult(0.0, 0.0, 0.0, 0, n_resamples, confidence_level)

    point_estimate = statistics.mean(values)
    if n == 1:
        return BootstrapResult(
            point_estimate, point_estimate, point_estimate, n, n_resamples, confidence_level
        )

    rng = random.Random(seed)
    values_list = list(values)
    resample_means: list[float] = []
    for _ in range(n_resamples):
        resample = [values_list[rng.randrange(n)] for _ in range(n)]
        resample_means.append(sum(resample) / n)

    resample_means.sort()
    alpha = 1.0 - confidence_level
    lower_idx = int((alpha / 2) * n_resamples)
    upper_idx = int((1 - alpha / 2) * n_resamples) - 1
    lower_idx = max(0, min(lower_idx, n_resamples - 1))
    upper_idx = max(0, min(upper_idx, n_resamples - 1))

    return BootstrapResult(
        point_estimate=round(point_estimate, 4),
        ci_lower=round(resample_means[lower_idx], 4),
        ci_upper=round(resample_means[upper_idx], 4),
        n_items=n,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
    )
