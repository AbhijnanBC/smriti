"""Unit tests for evaluation/certification/ (rectified)."""

import pytest
from smriti.core.models import (
    VerificationStatus, CertificationLevel, ScientificDomain, EvidenceGrade,
    ExperimentResult, VerificationResult, ReproducibilityAssessment,
    GateDecision, PublicationReadinessLevel,
)
from smriti.evaluation.certification.claims import assess_research_claims
from smriti.evaluation.certification.gates import evaluate_certification_gates
from smriti.evaluation.certification.publication import assess_publication_readiness
from smriti.evaluation.certification.levels import compute_scientific_confidence_index
from smriti.evaluation.engineering.confidence import compute_eci


def make_experiment_results(passed: bool = True):
    from smriti.evaluation.scientific.experiment import EXPERIMENT_REGISTRY
    results = []
    for exp in EXPERIMENT_REGISTRY:
        metrics = {}
        for metric, threshold in exp.acceptance_criteria.items():
            metrics[metric] = threshold + 0.05 if passed else threshold - 0.05
        results.append(ExperimentResult(
            experiment_id=exp.experiment_id, run_id="test_run",
            metrics=metrics, raw_outputs={},
            execution_time_seconds=0.1, manifest_path=None,
            status=VerificationStatus.PASSED if passed else VerificationStatus.FAILED,
        ))
    return results


def make_verification_results(pass_rate: float = 1.0):
    from smriti.evaluation.engineering.architectural import ARCHITECTURAL_RULES
    results = []
    for i, rule in enumerate(ARCHITECTURAL_RULES):
        status = VerificationStatus.PASSED if (i / len(ARCHITECTURAL_RULES)) < pass_rate else VerificationStatus.FAILED
        results.append(VerificationResult(
            rule_id=rule.rule_id, status=status,
            observed_value="compliant", expected_value=rule.acceptance_criterion,
            evidence="test", timestamp_iso="2024-01-01T00:00:00Z", duration_ms=1.0,
        ))
    return results


# ── Original 8 tests (all preserved) ─────────────────────────────────────────

def test_assess_research_claims_all_supported():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    assert len(claims) == 6
    supported = sum(1 for c in claims if c.is_supported)
    assert supported >= 3


def test_assess_research_claims_returns_six():
    claims = assess_research_claims(make_experiment_results())
    assert len(claims) == 6


def test_claims_have_evidence_grades():
    claims = assess_research_claims(make_experiment_results())
    valid_grades = {g.value for g in EvidenceGrade}
    for claim in claims:
        assert claim.evidence_grade.value in valid_grades


def test_claims_are_frozen():
    claims = assess_research_claims(make_experiment_results())
    with pytest.raises(Exception):
        claims[0].statement = "modified"


def test_sci_computation():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    ra = ReproducibilityAssessment(
        "EXP-001", 2, 0.85, 0.0, 0.0, "excellent", True,
    )
    sci = compute_scientific_confidence_index(exp_results, claims, [ra])
    assert 0.0 <= sci.overall_confidence <= 100.0


def test_publication_readiness():
    exp_results = make_experiment_results(passed=True)
    claims = assess_research_claims(exp_results)
    ra = ReproducibilityAssessment("EXP-001", 3, 0.85, 0.01, 0.01, "excellent", True)
    eci = compute_eci(make_verification_results(pass_rate=1.0))
    readiness = assess_publication_readiness(claims, [ra], eci)
    assert isinstance(readiness.readiness_level, PublicationReadinessLevel)
    assert isinstance(readiness.criteria_missing, tuple)


def test_certification_level_is_progressive():
    ver_low = make_verification_results(pass_rate=0.5)
    eci_low = compute_eci(ver_low)
    exp_low = make_experiment_results(passed=False)
    claims_low = assess_research_claims(exp_low)
    sci_low = compute_scientific_confidence_index(exp_low, claims_low, [])
    pr_low = assess_publication_readiness(claims_low, [], eci_low)
    level_low, _, _ = evaluate_certification_gates(ver_low, exp_low, [], claims_low, eci_low, sci_low, pr_low)

    ver_high = make_verification_results(pass_rate=1.0)
    eci_high = compute_eci(ver_high)
    exp_high = make_experiment_results(passed=True)
    claims_high = assess_research_claims(exp_high)
    ra = ReproducibilityAssessment("EXP-001", 3, 0.85, 0.01, 0.01, "excellent", True)
    sci_high = compute_scientific_confidence_index(exp_high, claims_high, [ra])
    pr_high = assess_publication_readiness(claims_high, [ra], eci_high)
    level_high, _, _ = evaluate_certification_gates(ver_high, exp_high, [ra], claims_high, eci_high, sci_high, pr_high)

    assert level_high.value >= level_low.value


def test_certification_report_is_frozen():
    from smriti.evaluation.certification.report import build_certification_report
    from smriti.evaluation.statistical.analysis import compute_statistical_analysis, STANDARD_THREATS
    from smriti.evaluation.engineering.confidence import compute_verification_coverage

    ver = make_verification_results()
    eci = compute_eci(ver)
    exp = make_experiment_results()
    claims = assess_research_claims(exp)
    ra = ReproducibilityAssessment("EXP-001", 2, 0.85, 0.0, 0.0, "excellent", True)
    sci = compute_scientific_confidence_index(exp, claims, [ra])
    pr = assess_publication_readiness(claims, [ra], eci)
    level, gates, rationale = evaluate_certification_gates(ver, exp, [ra], claims, eci, sci, pr)
    sa = compute_statistical_analysis("test", [0.8])
    coverage = compute_verification_coverage(ver)
    report = build_certification_report(
        run_id="test", verification_results=ver, verification_coverage=coverage,
        engineering_confidence=eci, experiment_results=exp, science_evidence=[],
        research_claims=claims, statistical_analyses=[sa], reproducibility_assessments=[ra],
        threats_to_validity=list(STANDARD_THREATS), scientific_confidence=sci,
        publication_readiness=pr, certification_level=level, certification_rationale=rationale,
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
    sci = compute_scientific_confidence_index(exp, claims, [ra])
    pr = assess_publication_readiness(claims, [ra], eci)
    level, gate_results, rationale = evaluate_certification_gates(ver, exp, [ra], claims, eci, sci, pr)
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
    sci = compute_scientific_confidence_index(exp, claims, [ra])
    pr = assess_publication_readiness(claims, [ra], eci)
    level, gate_results, rationale = evaluate_certification_gates(ver, exp, [ra], claims, eci, sci, pr)
    # Level must be ≤ ENGINEERING_VALIDATED since gate 2 (ECI) fails
    assert level.value <= CertificationLevel.ENGINEERING_VALIDATED.value, (
        f"If gate 2 (ECI < 75) blocks, level must not exceed ENGINEERING_VALIDATED. Got {level.name}"
    )


def test_enriched_research_claim_has_scientific_fields():
    """RECTIFIED (P0-3): ResearchClaim must have research_question and null_hypothesis."""
    exp = make_experiment_results(passed=True)
    claims = assess_research_claims(exp)
    for claim in claims:
        assert claim.research_question, f"{claim.claim_id} missing research_question"
        assert claim.null_hypothesis, f"{claim.claim_id} missing null_hypothesis"
        assert claim.applicability, f"{claim.claim_id} missing applicability"


def test_publication_readiness_is_ordinal():
    """RECTIFIED (P1-6): Publication readiness must be ordinal, not binary."""
    exp = make_experiment_results(passed=False)  # Low quality → not complete
    claims = assess_research_claims(exp)
    eci = compute_eci(make_verification_results(pass_rate=0.5))
    readiness = assess_publication_readiness(claims, [], eci)
    # Must be an ordinal level, not True/False
    assert isinstance(readiness.readiness_level, PublicationReadinessLevel)
    assert readiness.readiness_level != PublicationReadinessLevel.COMPLETE, (
        "Low-quality inputs must not produce COMPLETE publication readiness"
    )


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