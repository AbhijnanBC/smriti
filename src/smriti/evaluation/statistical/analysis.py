"""
analysis.py — Statistical Analysis Framework (Part 4, Section 12.38).

Part 4 answers: "Why should anyone believe the evidence?"

Statistical Framework:
    - Descriptive statistics (mean, std, median, min, max)
    - 95% confidence intervals (bootstrap or analytical)
    - Coefficient of Variation (reproducibility proxy)
    - Effect sizes (Cohen's d for comparisons)
    - Reproducibility assessment (multi-run CV)
    - Threats to validity catalogue

Philosophy:
    Evidence possesses little value unless its statistical validity
    can be objectively demonstrated.
"""

from __future__ import annotations

import math
import statistics

from smriti.core.models import (
    EffectSize,
    ReproducibilityAssessment,
    StatisticalAnalysis,
    ThreatToValidity,
)


def compute_statistical_analysis(
    metric_name: str,
    values: list[float],
    confidence_level: float = 0.95,
) -> StatisticalAnalysis:
    """
    Compute descriptive statistics and confidence interval for a metric.

    Args:
        metric_name:      The metric being analysed.
        values:           Observed values from multiple runs/samples.
        confidence_level: Desired CI level (default 0.95).

    Returns:
        StatisticalAnalysis with full statistical description.
    """
    if not values:
        return StatisticalAnalysis(
            metric_name=metric_name,
            values=(),
            mean=0.0,
            std_dev=0.0,
            median=0.0,
            min_value=0.0,
            max_value=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            coefficient_of_variation=0.0,
            n_samples=0,
        )

    n = len(values)
    mean = statistics.mean(values)
    std_dev = statistics.stdev(values) if n > 1 else 0.0
    median = statistics.median(values)
    min_val = min(values)
    max_val = max(values)
    cv = std_dev / max(abs(mean), 1e-10)  # Coefficient of variation

    # 95% CI using t-distribution approximation
    # t_critical for 95% CI: varies by df
    # We use a conservative t=2.0 for n >= 5, else 1.96 for large n
    if n <= 1:
        ci_lower, ci_upper = mean, mean
    elif n < 5:
        t_crit = 2.571  # t at 95%, df=4
        margin = t_crit * std_dev / math.sqrt(n)
        ci_lower = mean - margin
        ci_upper = mean + margin
    elif n < 30:
        t_crit = 2.045  # t at 95%, df=28
        margin = t_crit * std_dev / math.sqrt(n)
        ci_lower = mean - margin
        ci_upper = mean + margin
    else:
        # z-based for large samples
        z_crit = 1.96
        margin = z_crit * std_dev / math.sqrt(n)
        ci_lower = mean - margin
        ci_upper = mean + margin

    return StatisticalAnalysis(
        metric_name=metric_name,
        values=tuple(values),
        mean=round(mean, 6),
        std_dev=round(std_dev, 6),
        median=round(median, 6),
        min_value=round(min_val, 6),
        max_value=round(max_val, 6),
        ci_lower=round(ci_lower, 6),
        ci_upper=round(ci_upper, 6),
        coefficient_of_variation=round(cv, 4),
        n_samples=n,
    )


def compute_effect_size(
    metric_name: str,
    condition_a: str,
    values_a: list[float],
    condition_b: str,
    values_b: list[float],
) -> EffectSize:
    """
    Compute Cohen's d effect size between two conditions.

    Magnitude interpretation (Cohen, 1988):
        |d| < 0.2:  negligible
        |d| < 0.5:  small
        |d| < 0.8:  medium
        |d| >= 0.8: large
    """
    if not values_a or not values_b:
        return EffectSize(
            metric_name=metric_name,
            condition_a=condition_a,
            condition_b=condition_b,
            cohens_d=0.0,
            magnitude="negligible",
        )

    mean_a = statistics.mean(values_a)
    mean_b = statistics.mean(values_b)

    std_a = statistics.stdev(values_a) if len(values_a) > 1 else 0.0
    std_b = statistics.stdev(values_b) if len(values_b) > 1 else 0.0

    # Pooled standard deviation
    n_a, n_b = len(values_a), len(values_b)
    pooled_std = math.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / max(1, n_a + n_b - 2))

    cohens_d = (mean_a - mean_b) / max(pooled_std, 1e-10)
    abs_d = abs(cohens_d)

    if abs_d < 0.2:
        magnitude = "negligible"
    elif abs_d < 0.5:
        magnitude = "small"
    elif abs_d < 0.8:
        magnitude = "medium"
    else:
        magnitude = "large"

    return EffectSize(
        metric_name=metric_name,
        condition_a=condition_a,
        condition_b=condition_b,
        cohens_d=round(cohens_d, 4),
        magnitude=magnitude,
    )


def assess_reproducibility(
    experiment_id: str,
    metric_name: str,
    values: list[float],
    cv_threshold: float = 0.10,
) -> ReproducibilityAssessment:
    """
    Assess reproducibility via Coefficient of Variation.

    Classification:
        CV < 5%:   excellent
        CV < 10%:  good
        CV < 20%:  moderate
        CV >= 20%: poor

    Args:
        experiment_id:  Which experiment these runs came from.
        metric_name:    Which metric is being assessed.
        values:         Metric values from independent runs.
        cv_threshold:   CV threshold for is_reproducible (default 10%).
    """
    if not values:
        return ReproducibilityAssessment(
            experiment_id=experiment_id,
            n_runs=0,
            mean_metric=0.0,
            std_dev_metric=0.0,
            coefficient_of_variation=0.0,
            reproducibility_level="insufficient_data",
            is_reproducible=False,
        )

    mean = statistics.mean(values)
    std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
    cv = std_dev / max(abs(mean), 1e-10)

    if cv < 0.05:
        level = "excellent"
    elif cv < 0.10:
        level = "good"
    elif cv < 0.20:
        level = "moderate"
    else:
        level = "poor"

    return ReproducibilityAssessment(
        experiment_id=experiment_id,
        n_runs=len(values),
        mean_metric=round(mean, 6),
        std_dev_metric=round(std_dev, 6),
        coefficient_of_variation=round(cv, 4),
        reproducibility_level=level,
        is_reproducible=cv < cv_threshold,
    )


# ── Threats to validity catalogue (Section 12.4) ─────────────────────────────

STANDARD_THREATS: list[ThreatToValidity] = [
    ThreatToValidity(
        threat_id="THR-001",
        category="internal",
        description=(
            "Synthetic ground truth may not represent real-world note quality. "
            "Structural validation alone cannot confirm semantic accuracy."
        ),
        mitigation=(
            "All structural invariants verified deterministically. "
            "Semantic accuracy requires human-annotated ground truth for full evaluation."
        ),
        residual_risk="medium",
    ),
    ThreatToValidity(
        threat_id="THR-002",
        category="external",
        description=(
            "Results evaluated on a single personal Obsidian vault may not "
            "generalize to different writing styles or note-taking conventions."
        ),
        mitigation=(
            "Architecture designed for domain-agnostic processing. "
            "Generalization experiments include multiple document types."
        ),
        residual_risk="medium",
    ),
    ThreatToValidity(
        threat_id="THR-003",
        category="construct",
        description=(
            "Reliability Index is a policy-driven composite measure, not "
            "an objective ground truth. Different policy weights produce different scores."
        ),
        mitigation=(
            "Policy transparency: all weights documented and configurable. "
            "Sensitivity analysis varies weights across ± 20% range."
        ),
        residual_risk="low",
    ),
    ThreatToValidity(
        threat_id="THR-004",
        category="statistical",
        description=(
            "Single-run experiments provide no statistical power. "
            "Point estimates without confidence intervals cannot justify claims."
        ),
        mitigation=(
            "Reproducibility framework requires minimum 3 runs per experiment. "
            "95% confidence intervals reported for all primary metrics."
        ),
        residual_risk="low",
    ),
    ThreatToValidity(
        threat_id="THR-005",
        category="internal",
        description=(
            "spaCy en_core_web_sm dependency for claim extraction introduces "
            "non-determinism across spaCy version updates."
        ),
        mitigation=(
            "spaCy version pinned in pyproject.toml. "
            "Model revision recorded in EmbeddingModelDescriptor for reproducibility."
        ),
        residual_risk="low",
    ),
    ThreatToValidity(
        threat_id="THR-006",
        category="external",
        description=(
            "NLI cross-encoder performance depends on the specific model version. "
            "Results may not generalize to future model releases."
        ),
        mitigation=(
            "Model name and revision recorded in RelationshipProvenance. "
            "Architecture enables model substitution without pipeline changes."
        ),
        residual_risk="low",
    ),
]
