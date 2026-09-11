"""
metrics.py — MetricRegistry for Phase 12 (P2-3).

RECTIFIED (P2-3): Metrics are no longer hardcoded strings.
Each metric is a registered object with definition, formula, units,
range, interpretation, direction, and dependencies.

This improves extensibility: adding a new metric = creating a MetricDefinition.

RECTIFIED (P1-C, "FINAL REVIEW" round): several entries used conventional
information-retrieval/ML names (precision, recall, f1, partition_purity,
recall_at_k, calibration) while actually measuring project-specific
structural proxies (e.g. "precision" measured structural validity of
extracted claims, not true/false positives against a gold label;
"partition_purity" was a formula with no relationship to the standard
clustering-purity metric; "calibration" checked that scores fell in
[0, 100], nothing to do with ECE/Brier/temperature calibration). Renamed
every such entry to an explicit, non-conventional name describing what it
actually measures -- the same discipline already applied to
candidate_precision -> intended_pair_coverage elsewhere in this codebase.
"precision"/"recall"/"f1"/"accuracy"/"AURC"/"ECE"/"Brier"/"NLL" are
reserved for metrics that use their conventional definitions against a
real reference label; none of the entries below qualify, so none of them
use those names anymore.
"""

from __future__ import annotations

from smriti.core.models import MetricDefinition

METRIC_REGISTRY: dict[str, MetricDefinition] = {
    "structural_validity_rate": MetricDefinition(
        metric_name="structural_validity_rate",
        definition="Fraction of extracted claims that satisfy structural validity criteria",
        formula="valid_claims / total_extracted_claims",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. 1.0 = all claims structurally valid. < 0.70 = systematic extraction issue.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "extraction_completeness_rate": MetricDefinition(
        metric_name="extraction_completeness_rate",
        definition="Fraction of expected claims that were successfully extracted",
        formula="extracted_claims / total_expected_claims",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. 1.0 = no claims missed.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "structural_validity_completeness_f1": MetricDefinition(
        metric_name="structural_validity_completeness_f1",
        definition="Harmonic mean of structural_validity_rate and extraction_completeness_rate",
        formula="2 * structural_validity_rate * extraction_completeness_rate / (structural_validity_rate + extraction_completeness_rate)",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. Balances the structural-validity/completeness trade-off. Not a substitute for a true precision/recall F1 against a gold label.",
        direction="higher_is_better",
        dependencies=("structural_validity_rate", "extraction_completeness_rate"),
    ),
    "embedding_stability": MetricDefinition(
        metric_name="embedding_stability",
        definition="Consistency of embedding output across identical inputs (determinism check)",
        formula="1.0 if deterministic system else variance_measure",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="1.0 = fully deterministic. < 0.90 = non-determinism detected.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "partition_separation_rate": MetricDefinition(
        metric_name="partition_separation_rate",
        definition="Fraction of partitions correctly separating contradictory claims",
        formula="min(1.0, partition_count / (total_claims / 5))",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. Structural proxy for partition correctness. Not the standard clustering-purity metric.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "nonzero_reliability_coverage_rate": MetricDefinition(
        metric_name="nonzero_reliability_coverage_rate",
        definition="Fraction of returned results with non-zero reliability index",
        formula="valid_results / total_returned",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. Structural proxy for retrieval correctness. Not a top-k recall against a gold label -- see paper/sections/recall_at_k.tex for the genuine retrieval recall@k evaluation.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "score_range_validity_rate": MetricDefinition(
        metric_name="score_range_validity_rate",
        definition="Fraction of reliability scores in valid range [0, 100]",
        formula="in_range_count / total_count",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="1.0 = all scores properly bounded. < 1.0 = a scoring bug produced an out-of-range value. Not a calibration metric (ECE/Brier/temperature) -- see resolver_policy.confidence_policy for that distinction.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "ranking_stability": MetricDefinition(
        metric_name="ranking_stability",
        definition="Consistency of claim ordering across identical sort operations",
        formula="order_match_count / total_sorted",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="1.0 = perfectly deterministic ranking. < 0.85 = stability concern.",
        direction="higher_is_better",
        dependencies=(),
    ),
    "artifact_completeness_rate": MetricDefinition(
        metric_name="artifact_completeness_rate",
        definition="Fraction of claims with non-empty explanation summaries",
        formula="has_summary_count / total_claims_checked",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="1.0 = every claim has a complete explanation (architectural invariant).",
        direction="higher_is_better",
        dependencies=(),
    ),
    "faithfulness": MetricDefinition(
        metric_name="faithfulness",
        definition="Fraction of explanations where component contributions approximately sum to reliability index",
        formula="sum(abs(contributions)) / (reliability_index * 1.5)",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="Higher is better. < 0.95 = explanation is not fully faithful to score.",
        direction="higher_is_better",
        dependencies=("artifact_completeness_rate",),
    ),
    "traceability": MetricDefinition(
        metric_name="traceability",
        definition="Fraction of explanations with complete audit trail",
        formula="has_audit_count / total_checked",
        units="ratio",
        range_min=0.0,
        range_max=1.0,
        interpretation="1.0 = every explanation is fully traceable (architectural invariant).",
        direction="higher_is_better",
        dependencies=(),
    ),
}


def get_metric(metric_name: str) -> MetricDefinition:
    if metric_name not in METRIC_REGISTRY:
        raise KeyError(f"Metric '{metric_name}' not in MetricRegistry")
    return METRIC_REGISTRY[metric_name]


def all_metrics() -> list[MetricDefinition]:
    return list(METRIC_REGISTRY.values())
