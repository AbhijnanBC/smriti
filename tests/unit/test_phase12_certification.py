"""Unit tests for evaluation/certification/ (rectified)."""

import pytest
from smriti.core.models import (
    ArtifactReadinessLevel,
    CertificationLevel,
    EvidenceGrade,
    ExperimentResult,
    GateDecision,
    ReproducibilityAssessment,
    VerificationResult,
    VerificationStatus,
)
from smriti.evaluation.certification.artifact_readiness import assess_artifact_readiness
from smriti.evaluation.certification.claims import assess_research_claims
from smriti.evaluation.certification.gates import evaluate_certification_gates
from smriti.evaluation.certification.levels import compute_research_evidence_coverage
from smriti.evaluation.engineering.confidence import compute_eci


def make_experiment_results(passed: bool = True):
    from smriti.evaluation.scientific.experiment import EXPERIMENT_REGISTRY

    # Metrics where a LOWER value is better (threshold is a maximum, not a
    # minimum) -- e.g. EXP-003's contradiction_violation_rate, whose
    # threshold of 0.0 is already the floor, so "threshold - 0.05" would be
    # a nonsensical negative rate. See claims.py's `inverted` handling.
    inverted_metrics = {"contradiction_violation_rate"}
    results = []
    for exp in EXPERIMENT_REGISTRY:
        metrics = {}
        for metric, threshold in exp.acceptance_criteria.items():
            if metric in inverted_metrics:
                metrics[metric] = 0.0 if passed else threshold + 0.05
            else:
                metrics[metric] = threshold + 0.05 if passed else threshold - 0.05
        results.append(
            ExperimentResult(
                experiment_id=exp.experiment_id,
                run_id="test_run",
                metrics=metrics,
                raw_outputs={},
                execution_time_seconds=0.1,
                manifest_path=None,
                status=VerificationStatus.PASSED if passed else VerificationStatus.FAILED,
            )
        )
    return results


def make_verification_results(pass_rate: float = 1.0):
    from smriti.evaluation.engineering.architectural import ARCHITECTURAL_RULES

    results = []
    for i, rule in enumerate(ARCHITECTURAL_RULES):
        status = (
            VerificationStatus.PASSED
            if (i / len(ARCHITECTURAL_RULES)) < pass_rate
            else VerificationStatus.FAILED
        )
        results.append(
            VerificationResult(
                rule_id=rule.rule_id,
                status=status,
                observed_value="compliant",
                expected_value=rule.acceptance_criterion,
                evidence="test",
                timestamp_iso="2024-01-01T00:00:00Z",
                duration_ms=1.0,
            )
        )
    return results


# ── Original 8 tests (all preserved) ─────────────────────────────────────────


def test_assess_research_claims_all_supported():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    assert len(claims) == 5
    supported = sum(1 for c in claims if c.is_supported)
    assert supported >= 3


def test_assess_research_claims_returns_six():
    claims = assess_research_claims(make_experiment_results())
    assert len(claims) == 5


def test_claims_have_evidence_grades():
    claims = assess_research_claims(make_experiment_results())
    valid_grades = {g.value for g in EvidenceGrade}
    for claim in claims:
        assert claim.evidence_grade.value in valid_grades


def test_claims_are_frozen():
    claims = assess_research_claims(make_experiment_results())
    with pytest.raises(Exception):
        claims[0].statement = "modified"


def test_evidence_coverage_computation():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    ra = ReproducibilityAssessment(
        "EXP-001",
        2,
        0.85,
        0.0,
        0.0,
        "excellent",
        True,
    )
    coverage = compute_research_evidence_coverage(exp_results, claims, [ra])
    assert 0.0 <= coverage.overall_coverage <= 100.0


def test_artifact_readiness():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    ra = ReproducibilityAssessment("EXP-001", 3, 0.85, 0.01, 0.01, "excellent", True)
    eci = compute_eci(make_verification_results(pass_rate=1.0))
    readiness = assess_artifact_readiness(claims, [ra], eci)
    assert isinstance(readiness.readiness_level, ArtifactReadinessLevel)
    assert isinstance(readiness.criteria_missing, tuple)


def test_certification_level_is_progressive():
    ver_low = make_verification_results(pass_rate=0.5)
    eci_low = compute_eci(ver_low)
    exp_low = make_experiment_results(passed=False)
    claims_low = assess_research_claims(exp_low)
    coverage_low = compute_research_evidence_coverage(exp_low, claims_low, [])
    pr_low = assess_artifact_readiness(claims_low, [], eci_low)
    level_low, _, _ = evaluate_certification_gates(
        ver_low, exp_low, [], claims_low, eci_low, coverage_low, pr_low
    )

    ver_high = make_verification_results(pass_rate=1.0)
    eci_high = compute_eci(ver_high)
    exp_high = make_experiment_results(passed=True)
    claims_high = assess_research_claims(exp_high)
    ra = ReproducibilityAssessment("EXP-001", 3, 0.85, 0.01, 0.01, "excellent", True)
    coverage_high = compute_research_evidence_coverage(exp_high, claims_high, [ra])
    pr_high = assess_artifact_readiness(claims_high, [ra], eci_high)
    level_high, _, _ = evaluate_certification_gates(
        ver_high, exp_high, [ra], claims_high, eci_high, coverage_high, pr_high
    )

    assert level_high.value >= level_low.value


def test_certification_report_is_frozen():
    from smriti.evaluation.certification.report import build_certification_report
    from smriti.evaluation.engineering.confidence import compute_verification_coverage
    from smriti.evaluation.statistical.analysis import (
        STANDARD_THREATS,
        compute_statistical_analysis,
    )

    ver = make_verification_results()
    eci = compute_eci(ver)
    exp = make_experiment_results()
    claims = assess_research_claims(exp)
    ra = ReproducibilityAssessment("EXP-001", 2, 0.85, 0.0, 0.0, "excellent", True)
    evidence_coverage = compute_research_evidence_coverage(exp, claims, [ra])
    pr = assess_artifact_readiness(claims, [ra], eci)
    level, gates, rationale = evaluate_certification_gates(
        ver, exp, [ra], claims, eci, evidence_coverage, pr
    )
    sa = compute_statistical_analysis("test", [0.8])
    verification_cov = compute_verification_coverage(ver)
    report = build_certification_report(
        run_id="test",
        verification_results=ver,
        verification_coverage=verification_cov,
        engineering_confidence=eci,
        experiment_results=exp,
        science_evidence=[],
        research_claims=claims,
        statistical_analyses=[sa],
        reproducibility_assessments=[ra],
        threats_to_validity=list(STANDARD_THREATS),
        research_evidence_coverage=evidence_coverage,
        artifact_readiness=pr,
        certification_level=level,
        certification_rationale=rationale,
        gate_results=gates,
    )
    with pytest.raises(Exception):
        report.run_id = "modified"


# ── 6 new rectified tests ─────────────────────────────────────────────────────


def test_gate_based_certification_not_score_based():
    """RECTIFIED (P0-1): Gate-based certification produces CertificationGateResult objects."""
    ver = make_verification_results(pass_rate=1.0)
    eci = compute_eci(ver)
    exp = make_experiment_results(passed=True)
    claims = assess_research_claims(exp)
    ra = ReproducibilityAssessment("EXP-001", 2, 0.85, 0.0, 0.0, "excellent", True)
    coverage = compute_research_evidence_coverage(exp, claims, [ra])
    pr = assess_artifact_readiness(claims, [ra], eci)
    level, gate_results, rationale = evaluate_certification_gates(
        ver, exp, [ra], claims, eci, coverage, pr
    )
    assert len(gate_results) >= 1, "Gate-based certification must produce gate results"
    for g in gate_results:
        assert g.decision in (GateDecision.PASS, GateDecision.BLOCK)


def test_failed_gate_blocks_higher_levels():
    """RECTIFIED (P0-1): A failed gate must prevent advancement to higher levels."""
    # Pass gate 1 (arch) but fail gate 2 (ECI too low via low pass rate)
    ver = make_verification_results(pass_rate=0.91)  # Passes gate 1
    eci = compute_eci(make_verification_results(pass_rate=0.5))  # Fails gate 2 (ECI < 75)
    exp = make_experiment_results(passed=True)
    claims = assess_research_claims(exp)
    ra = ReproducibilityAssessment("EXP-001", 2, 0.85, 0.0, 0.0, "excellent", True)
    coverage = compute_research_evidence_coverage(exp, claims, [ra])
    pr = assess_artifact_readiness(claims, [ra], eci)
    level, gate_results, rationale = evaluate_certification_gates(
        ver, exp, [ra], claims, eci, coverage, pr
    )
    # Level must be ≤ ENGINEERING_VALIDATED since gate 2 (ECI) fails
    assert (
        level.value <= CertificationLevel.ENGINEERING_VALIDATED.value
    ), f"If gate 2 (ECI < 75) blocks, level must not exceed ENGINEERING_VALIDATED. Got {level.name}"


def test_enriched_research_claim_has_scientific_fields():
    """RECTIFIED (P0-3): ResearchClaim must have research_question and null_hypothesis."""
    exp = make_experiment_results(passed=True)
    claims = assess_research_claims(exp)
    for claim in claims:
        assert claim.research_question, f"{claim.claim_id} missing research_question"
        assert claim.null_hypothesis, f"{claim.claim_id} missing null_hypothesis"
        assert claim.applicability, f"{claim.claim_id} missing applicability"


def test_artifact_readiness_is_ordinal():
    """RECTIFIED (P1-6): Publication readiness must be ordinal, not binary."""
    exp = make_experiment_results(passed=False)  # Low quality → not complete
    claims = assess_research_claims(exp)
    eci = compute_eci(make_verification_results(pass_rate=0.5))
    readiness = assess_artifact_readiness(claims, [], eci)
    # Must be an ordinal level, not True/False
    assert isinstance(readiness.readiness_level, ArtifactReadinessLevel)
    assert (
        readiness.readiness_level != ArtifactReadinessLevel.COMPLETE
    ), "Low-quality inputs must not produce COMPLETE publication readiness"


def test_assumption_registry_has_entries():
    """RECTIFIED (P1-3): AssumptionRegistry must have registered assumptions."""
    from smriti.evaluation.statistical.assumptions import ASSUMPTION_REGISTRY

    assert len(ASSUMPTION_REGISTRY) >= 5
    for a in ASSUMPTION_REGISTRY:
        assert a.assumption_id
        assert a.description
        assert a.risk_if_violated in ("low", "medium", "high")


def test_limitation_registry_has_entries():
    """RECTIFIED (P1-4): LimitationRegistry must have registered limitations."""
    from smriti.evaluation.statistical.limitations import LIMITATION_REGISTRY

    assert len(LIMITATION_REGISTRY) >= 4
    for lim in LIMITATION_REGISTRY:
        assert lim.limitation_id
        assert lim.description
        assert lim.possible_future_work


# ── P1-A/P1-B regression tests ("FINAL REVIEW" round) ─────────────────────────


def test_evidence_coverage_does_not_mask_not_evaluable():
    """RECTIFIED (P1-A): a NOT_EVALUABLE experiment must lower
    experiment_pass_rate, not silently disappear from its denominator.
    4 PASSED + 1 NOT_EVALUABLE must report 80%, never 100%."""
    exp_results = make_experiment_results(passed=True)
    assert len(exp_results) == 5
    exp_results[-1] = ExperimentResult(
        experiment_id=exp_results[-1].experiment_id,
        run_id="test_run",
        metrics={},
        raw_outputs={},
        execution_time_seconds=0.1,
        manifest_path=None,
        status=VerificationStatus.NOT_EVALUABLE,
    )
    claims = assess_research_claims(exp_results)
    coverage = compute_research_evidence_coverage(exp_results, claims, [])
    assert coverage.experiment_pass_rate == pytest.approx(80.0)
    assert coverage.measurement_coverage == pytest.approx(80.0)


def test_gate_3_blocks_on_not_evaluable_experiment():
    """RECTIFIED (P1-A): Gate 3 must BLOCK if any registered experiment is
    NOT_EVALUABLE/SKIPPED, even if enough experiments are registered."""
    ver = make_verification_results(pass_rate=1.0)
    eci = compute_eci(ver)
    exp = make_experiment_results(passed=True)
    exp[-1] = ExperimentResult(
        experiment_id=exp[-1].experiment_id,
        run_id="test_run",
        metrics={},
        raw_outputs={},
        execution_time_seconds=0.1,
        manifest_path=None,
        status=VerificationStatus.NOT_EVALUABLE,
    )
    claims = assess_research_claims(exp)
    coverage = compute_research_evidence_coverage(exp, claims, [])
    pr = assess_artifact_readiness(claims, [], eci)
    level, gate_results, _ = evaluate_certification_gates(ver, exp, [], claims, eci, coverage, pr)
    gate3 = next(g for g in gate_results if g.gate_number == 3)
    assert gate3.decision == GateDecision.BLOCK
    assert level.value <= CertificationLevel.ENGINEERING_VALIDATED.value


def test_evidence_grade_reflects_provenance_not_claim_count():
    """RECTIFIED (P1-B): evidence grade must come from each claim's
    evidence provenance, not simply how many claims are supported. RC1/RC2
    (LLM reference annotation) must grade C; RC3 (structural invariant)
    and RC4/RC5 (self-consistency/reconstruction) must grade D -- none of
    them should be inflated to A/B just because 5 claims are supported."""
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    by_id = {c.claim_id: c for c in claims}
    assert by_id["RC1"].evidence_grade == EvidenceGrade.C
    assert by_id["RC2"].evidence_grade == EvidenceGrade.C
    assert by_id["RC3"].evidence_grade == EvidenceGrade.D
    assert by_id["RC4"].evidence_grade == EvidenceGrade.D
    assert by_id["RC5"].evidence_grade == EvidenceGrade.D

    coverage = compute_research_evidence_coverage(exp_results, claims, [])
    # Overall grade is the worst grade among supported claims (D here),
    # never the old count-based B for "5 claims supported".
    assert coverage.evidence_grade == EvidenceGrade.D
