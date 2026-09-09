"""
levels.py — Research Evidence Coverage computation (FROZEN v2).

FROZEN (post-review rectification): the previous version of this function
computed a "Scientific Confidence Index" from a mix of real signals and
outright fabrications — a hardcoded `generalization_confidence = 50.0`
("conservative — single vault evaluation", never actually measured), and
`statistical_support = min(100, n_experiments * 15)` (a formula with no
statistical meaning whatsoever, since it rewards simply registering more
experiments regardless of whether any of them found anything). Both are
deleted, not patched.

What replaces it: every sub-score below is either a direct count/ratio of
real ExperimentResult/ResearchClaim data, or explicitly reported as 0.0
with the reason it cannot yet be measured (never left at an arbitrary
non-zero "placeholder" value). The dataclass name (ScientificConfidenceIndex)
and its overall_confidence field are kept for backward-compatible wiring
into gates.py/report.py, but every number it now reports is honest:

    accuracy_confidence:        % of registered experiments that PASSED
                                 (excludes NOT_EVALUABLE/SKIPPED from the
                                 denominator — an unmeasured experiment is
                                 neither a pass nor a fail)
    consistency_confidence:     mean confidence_score across claims that
                                 have real (non-NOT_EVALUABLE) evidence
    robustness_confidence:      reproducibility rate across REAL multi-run
                                 reproducibility assessments only (0.0, not
                                 50.0, if no real multi-run data exists yet
                                 — see evaluation/__init__.py, which no
                                 longer fabricates a fake 2-sample repeat)
    generalization_confidence:  0.0, always, until SMRITI is evaluated on
                                 more than one corpus/domain — there is no
                                 honest non-zero number to report here yet
    interpretability_confidence: EXP-005's reconstruction_exact_match_rate
                                 if measured, else 0.0
    statistical_support:        % of registered experiments that returned
                                 a REAL (non-NOT_EVALUABLE) result at all
                                 -- literally "how much of this system did
                                 we actually manage to measure", not a
                                 reward for registering more experiments
"""

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
    """Compute Research Evidence Coverage (field name kept as SCI for
    backward compatibility with gates.py/report.py's schema)."""
    if not experiment_results:
        return ScientificConfidenceIndex(
            accuracy_confidence=0.0, consistency_confidence=0.0,
            robustness_confidence=0.0, generalization_confidence=0.0,
            interpretability_confidence=0.0, statistical_support=0.0,
            overall_confidence=0.0, evidence_grade=EvidenceGrade.E,
        )

    measured = [r for r in experiment_results
                if r.status not in (VerificationStatus.NOT_EVALUABLE, VerificationStatus.SKIPPED)]
    n_measured = len(measured)
    n_total = len(experiment_results)

    n_passed = sum(1 for r in measured if r.status == VerificationStatus.PASSED)
    accuracy = (n_passed / n_measured) * 100.0 if n_measured else 0.0

    evaluated_claims = [c for c in research_claims if c.evidence_grade != EvidenceGrade.E or c.confidence_score > 0]
    consistency = (
        (sum(c.confidence_score for c in evaluated_claims) / len(evaluated_claims)) * 100.0
        if evaluated_claims else 0.0
    )

    if reproducibility_assessments:
        n_reproducible = sum(1 for a in reproducibility_assessments if a.is_reproducible)
        robustness = (n_reproducible / len(reproducibility_assessments)) * 100.0
    else:
        robustness = 0.0  # No real multi-run data exists — not "conservatively 50", just unmeasured.

    generalization = 0.0  # Single-corpus evaluation. No claim of generalization is made.

    exp005 = next((r for r in experiment_results if r.experiment_id == "EXP-005"), None)
    interp = (
        exp005.metrics.get("reconstruction_exact_match_rate", 0.0) * 100.0
        if exp005 and exp005.status not in (VerificationStatus.NOT_EVALUABLE, VerificationStatus.SKIPPED)
        else 0.0
    )

    statistical_support = (n_measured / n_total) * 100.0 if n_total else 0.0

    overall = round(
        0.30 * accuracy + 0.25 * consistency + 0.20 * robustness
        + 0.10 * generalization + 0.10 * interp + 0.05 * statistical_support,
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
        robustness_confidence=round(robustness, 2),
        generalization_confidence=round(generalization, 2),
        interpretability_confidence=round(interp, 2),
        statistical_support=round(statistical_support, 2),
        overall_confidence=overall,
        evidence_grade=grade,
    )
