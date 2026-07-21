"""levels.py — SCI computation + publication assessment helpers."""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ScientificConfidenceIndex, EvidenceGrade, ExperimentResult,
    ResearchClaim, ReproducibilityAssessment, VerificationStatus,
)


def compute_scientific_confidence_index(
    experiment_results: List[ExperimentResult],
    research_claims: List[ResearchClaim],
    reproducibility_assessments: List[ReproducibilityAssessment],
) -> ScientificConfidenceIndex:
    """Compute the Scientific Confidence Index (continuous 0–100)."""
    if not experiment_results:
        return ScientificConfidenceIndex(
            accuracy_confidence=0.0, consistency_confidence=0.0,
            robustness_confidence=50.0, generalization_confidence=50.0,
            interpretability_confidence=0.0, statistical_support=0.0,
            overall_confidence=0.0, evidence_grade=EvidenceGrade.E,
        )

    n_passed = sum(1 for r in experiment_results if r.status == VerificationStatus.PASSED)
    n_total = max(1, len(experiment_results))
    accuracy = (n_passed / n_total) * 100.0
    consistency = (sum(c.confidence_score for c in research_claims) / max(1, len(research_claims))) * 100.0
    repro_rate = (
        sum(1 for a in reproducibility_assessments if a.is_reproducible)
        / max(1, len(reproducibility_assessments))
    ) * 100.0 if reproducibility_assessments else 50.0
    generalization = 50.0  # Conservative — single vault evaluation
    interp = (
        next((r.metrics.get("completeness", 0.0) for r in experiment_results if r.experiment_id == "EXP-006"), 0.0) * 100.0
    )
    stat_support = min(100.0, n_total * 15.0)  # Up to 100 with 6+ experiments

    overall = round(
        0.30 * accuracy + 0.25 * consistency + 0.20 * repro_rate
        + 0.10 * generalization + 0.10 * interp + 0.05 * stat_support,
        2,
    )

    n_supported = sum(1 for c in research_claims if c.is_supported)
    if n_supported >= 5:   grade = EvidenceGrade.B
    elif n_supported >= 3: grade = EvidenceGrade.C
    elif n_supported >= 1: grade = EvidenceGrade.D
    else:                  grade = EvidenceGrade.E

    return ScientificConfidenceIndex(
        accuracy_confidence=round(accuracy, 2),
        consistency_confidence=round(consistency, 2),
        robustness_confidence=round(repro_rate, 2),
        generalization_confidence=round(generalization, 2),
        interpretability_confidence=round(interp, 2),
        statistical_support=round(stat_support, 2),
        overall_confidence=overall,
        evidence_grade=grade,
    )