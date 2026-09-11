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

RECTIFIED (P2, external "reality check" review): the dataclass itself is
now named ResearchEvidenceCoverage (was ScientificConfidenceIndex) and its
headline field overall_coverage (was overall_confidence) -- completing the
rename this module's own docstring had already described conceptually but
deferred at the Python-identifier level for backward compatibility. That
compatibility concern no longer applies now that gates.py/report.py are
updated in the same pass.

RECTIFIED (P1-A, "FINAL REVIEW" round): the previous accuracy_confidence
field computed n_passed / n_measured, i.e. it EXCLUDED NOT_EVALUABLE/
SKIPPED experiments from its own denominator. That let a missing
experiment disappear rather than count against the score: 4 PASSED + 1
NOT_EVALUABLE reported 100% "accuracy" even though only 4/5 of the
registered experiments actually ran. The fix, per the review: report
experiment_pass_rate = n_passed / n_TOTAL (so a NOT_EVALUABLE experiment
is neither silently excluded nor silently counted as passing -- it
correctly drags the pass rate down) alongside measurement_coverage =
n_measured / n_total (renamed from statistical_support, same formula, so
readers can tell "ran and failed" apart from "never ran" even though both
now lower experiment_pass_rate the same way).

What replaces the original fabricated version: every sub-score below is
either a direct count/ratio of real ExperimentResult/ResearchClaim data,
or explicitly reported as 0.0 with the reason it cannot yet be measured
(never left at an arbitrary non-zero "placeholder" value). Every number
it now reports is honest:

    experiment_pass_rate:       % of ALL registered experiments that
                                 PASSED (denominator is every registered
                                 experiment, including NOT_EVALUABLE/
                                 SKIPPED ones -- a missing experiment
                                 lowers this number, it cannot hide from it)
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
    measurement_coverage:       % of registered experiments that returned
                                 a REAL (non-NOT_EVALUABLE) result at all
                                 -- literally "how much of this system did
                                 we actually manage to measure", not a
                                 reward for registering more experiments
"""

from __future__ import annotations

from smriti.core.models import (
    EvidenceGrade,
    ExperimentResult,
    ReproducibilityAssessment,
    ResearchClaim,
    ResearchEvidenceCoverage,
    VerificationStatus,
)


def compute_research_evidence_coverage(
    experiment_results: list[ExperimentResult],
    research_claims: list[ResearchClaim],
    reproducibility_assessments: list[ReproducibilityAssessment],
) -> ResearchEvidenceCoverage:
    """Compute Research Evidence Coverage."""
    if not experiment_results:
        return ResearchEvidenceCoverage(
            experiment_pass_rate=0.0,
            consistency_confidence=0.0,
            robustness_confidence=0.0,
            generalization_confidence=0.0,
            interpretability_confidence=0.0,
            measurement_coverage=0.0,
            overall_coverage=0.0,
            evidence_grade=EvidenceGrade.E,
        )

    measured = [
        r
        for r in experiment_results
        if r.status not in (VerificationStatus.NOT_EVALUABLE, VerificationStatus.SKIPPED)
    ]
    n_measured = len(measured)
    n_total = len(experiment_results)

    # RECTIFIED (P1-A): denominator is n_total, not n_measured -- a
    # NOT_EVALUABLE/SKIPPED experiment must lower this rate, not vanish
    # from it (see module docstring).
    n_passed = sum(1 for r in experiment_results if r.status == VerificationStatus.PASSED)
    accuracy = (n_passed / n_total) * 100.0 if n_total else 0.0

    evaluated_claims = [
        c for c in research_claims if c.evidence_grade != EvidenceGrade.E or c.confidence_score > 0
    ]
    consistency = (
        (sum(c.confidence_score for c in evaluated_claims) / len(evaluated_claims)) * 100.0
        if evaluated_claims
        else 0.0
    )

    if reproducibility_assessments:
        n_reproducible = sum(1 for a in reproducibility_assessments if a.is_reproducible)
        robustness = (n_reproducible / len(reproducibility_assessments)) * 100.0
    else:
        robustness = (
            0.0  # No real multi-run data exists — not "conservatively 50", just unmeasured.
        )

    generalization = 0.0  # Single-corpus evaluation. No claim of generalization is made.

    exp005 = next((r for r in experiment_results if r.experiment_id == "EXP-005"), None)
    interp = (
        exp005.metrics.get("reconstruction_exact_match_rate", 0.0) * 100.0
        if exp005
        and exp005.status not in (VerificationStatus.NOT_EVALUABLE, VerificationStatus.SKIPPED)
        else 0.0
    )

    measurement_coverage = (n_measured / n_total) * 100.0 if n_total else 0.0

    overall = round(
        0.30 * accuracy
        + 0.25 * consistency
        + 0.20 * robustness
        + 0.10 * generalization
        + 0.10 * interp
        + 0.05 * measurement_coverage,
        2,
    )

    # RECTIFIED (P1-B, "FINAL REVIEW" round): the overall evidence grade is
    # no longer a function of HOW MANY claims are supported (5+ -> B, 3+ ->
    # C, 1+ -> D) -- that rule rewarded registering more claims regardless
    # of what backed them. claims.py now assigns each claim's own grade
    # from its evidence PROVENANCE (see EVIDENCE_PROVENANCE_GRADE there).
    # The overall grade here is the worst (lowest-quality) grade among the
    # SUPPORTED claims: certification cannot be stronger than its weakest
    # supporting evidence, and coverage still matters implicitly (a claim
    # with no evidence is not "supported" and cannot pull the overall
    # grade up by being ignored).
    grade_order = [
        EvidenceGrade.A,
        EvidenceGrade.B,
        EvidenceGrade.C,
        EvidenceGrade.D,
        EvidenceGrade.E,
    ]
    supported_grades = [c.evidence_grade for c in research_claims if c.is_supported]
    if supported_grades:
        grade = max(supported_grades, key=grade_order.index)
    else:
        grade = EvidenceGrade.E

    return ResearchEvidenceCoverage(
        experiment_pass_rate=round(accuracy, 2),
        consistency_confidence=round(consistency, 2),
        robustness_confidence=round(robustness, 2),
        generalization_confidence=round(generalization, 2),
        interpretability_confidence=round(interp, 2),
        measurement_coverage=round(measurement_coverage, 2),
        overall_coverage=overall,
        evidence_grade=grade,
    )
