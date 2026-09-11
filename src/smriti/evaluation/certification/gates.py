"""
gates.py — Gate-Based Certification Engine (P0-1).

RECTIFIED (P0-1): Certification is NOT a weighted average of ECI and
research evidence coverage (renamed from "SCI" in P2 -- see below).

The original:
    overall = 0.40 * ECI + 0.60 * SCI  → level

Was architecturally wrong because:
    ECI=99, SCI=99, Reproducibility FAILED → still "Research Certified"
    This is scientifically indefensible.

The correct model is a sequence of gates:
    Gate 1: Verification     → architectural invariants (≥90% pass rate)
    Gate 2: Engineering      → ECI ≥ 75.0
    Gate 3: Scientific       → all 6 experiments executed
    Gate 4: Statistical      → research evidence coverage ≥ 70.0
    Gate 5: Reproducibility  → ≥80% experiments reproducible
    Gate 6: Artifact Readiness → ArtifactReadinessLevel is COMPLETE

Every gate must pass. A failed gate blocks certification at that level.
No weighted average substitutes for a passed gate.

RECTIFIED (Configuration): All gate thresholds are now read from config,
not hardcoded. This makes certification policy configurable without code changes.

RECTIFIED (P2, external "reality check" review): "SCI" (Scientific
Confidence Index) is renamed throughout to "research evidence coverage" --
it measures how much of the system has actually been measured and by what
grade of evidence, not a validated statistical confidence that SMRITI's
claims are true. See core.models.ResearchEvidenceCoverage.
"""

from __future__ import annotations

import structlog
from smriti.core.config import get_config
from smriti.core.models import (
    ArtifactReadinessAssessment,
    ArtifactReadinessLevel,
    CertificationGateResult,
    CertificationLevel,
    EngineeringVerificationIndex,
    ExperimentResult,
    GateDecision,
    ReproducibilityAssessment,
    ResearchClaim,
    ResearchEvidenceCoverage,
    VerificationResult,
    VerificationStatus,
)

logger = structlog.get_logger(__name__)


def evaluate_certification_gates(
    verification_results: list[VerificationResult],
    experiment_results: list[ExperimentResult],
    reproducibility_assessments: list[ReproducibilityAssessment],
    research_claims: list[ResearchClaim],
    eci: EngineeringVerificationIndex,
    evidence_coverage: ResearchEvidenceCoverage,
    artifact_readiness: ArtifactReadinessAssessment,
) -> tuple[CertificationLevel, list[CertificationGateResult], str]:
    """
    RECTIFIED (P0-1): Evaluate all 6 certification gates in sequence.

    Returns:
        (CertificationLevel, gate_results, rationale)

    Certification advances only if every gate passes. The level achieved
    is determined by the highest gate that passed.
    """
    gate_results: list[CertificationGateResult] = []
    rationale_parts = ["SMRITI is implemented and produces artifacts."]
    level = CertificationLevel.PROTOTYPE

    # ── Load dynamic thresholds from configuration ───────────────────────────
    config = get_config()
    eval_cfg = config.get("evaluation", {})

    req_arch_rate = eval_cfg.get("gate_1_arch_pass_rate", 0.90)
    req_eci = eval_cfg.get("gate_2_eci_required", 75.0)
    req_experiments = eval_cfg.get("gate_3_min_experiments", 6)
    req_evidence_coverage = eval_cfg.get("gate_4_evidence_coverage_required", 70.0)
    req_repro_rate = eval_cfg.get("gate_5_reproducibility_rate", 0.80)
    # Gate 6 requires ArtifactReadinessLevel.COMPLETE (no config threshold)

    # ── Gate 1: Verification (≥ config.gate_1_arch_pass_rate) ─────────────────
    total_rules = len(verification_results)
    passed_rules = sum(1 for r in verification_results if r.status == VerificationStatus.PASSED)
    arch_pass_rate = passed_rules / max(1, total_rules)
    gate1_decision = GateDecision.PASS if arch_pass_rate >= req_arch_rate else GateDecision.BLOCK
    gate1 = CertificationGateResult(
        gate_number=1,
        gate_name="Verification",
        decision=gate1_decision,
        rationale=f"{passed_rules}/{total_rules} rules pass ({arch_pass_rate:.0%}). Required: ≥ {req_arch_rate:.0%}.",
        metric_observed=arch_pass_rate * 100,
        metric_required=req_arch_rate * 100,
        blocking_reason=(
            ""
            if gate1_decision == GateDecision.PASS
            else f"Architectural pass rate below {req_arch_rate * 100}%"
        ),
    )
    gate_results.append(gate1)
    logger.info(
        "gate_evaluated", gate=1, decision=gate1_decision.value, value=f"{arch_pass_rate:.0%}"
    )

    if gate1_decision == GateDecision.BLOCK:
        rationale_parts.append(gate1.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.ARCHITECTURALLY_VERIFIED
    rationale_parts.append(gate1.rationale)

    # ── Gate 2: Engineering (ECI ≥ config.gate_2_eci_required) ───────────────
    gate2_decision = GateDecision.PASS if eci.overall_confidence >= req_eci else GateDecision.BLOCK
    gate2 = CertificationGateResult(
        gate_number=2,
        gate_name="Engineering Validation",
        decision=gate2_decision,
        rationale=f"ECI = {eci.overall_confidence:.1f}/100. Required: ≥ {req_eci}.",
        metric_observed=eci.overall_confidence,
        metric_required=req_eci,
        blocking_reason=(
            ""
            if gate2_decision == GateDecision.PASS
            else f"ECI {eci.overall_confidence:.1f} < {req_eci}"
        ),
    )
    gate_results.append(gate2)
    logger.info("gate_evaluated", gate=2, decision=gate2_decision.value, eci=eci.overall_confidence)

    if gate2_decision == GateDecision.BLOCK:
        rationale_parts.append(gate2.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.ENGINEERING_VALIDATED
    rationale_parts.append(gate2.rationale)

    # ── Gate 3: Scientific (≥ config.gate_3_min_experiments) ──────────────────
    # RECTIFIED (P1-A, "FINAL REVIEW" round): registering an experiment is
    # not the same as it having actually run. Previously this gate only
    # counted len(experiment_results), so a NOT_EVALUABLE/SKIPPED entry
    # counted the same as a real PASSED/FAILED run -- certification could
    # advance past Gate 3 with an experiment that never actually executed.
    # The gate now also requires zero NOT_EVALUABLE/SKIPPED entries among
    # the registered experiments; there is currently no "explicitly
    # designated optional" experiment concept in EXPERIMENT_REGISTRY, so
    # every registered experiment is required until one is added.
    n_experiments = len(experiment_results)
    n_not_evaluable = sum(
        1
        for r in experiment_results
        if r.status in (VerificationStatus.NOT_EVALUABLE, VerificationStatus.SKIPPED)
    )
    gate3_decision = (
        GateDecision.PASS
        if n_experiments >= req_experiments and n_not_evaluable == 0
        else GateDecision.BLOCK
    )
    if n_experiments < req_experiments:
        gate3_blocking = f"Only {n_experiments}/{req_experiments} experiments run"
    elif n_not_evaluable > 0:
        gate3_blocking = f"{n_not_evaluable} registered experiment(s) are NOT_EVALUABLE/SKIPPED, not actually run"
    else:
        gate3_blocking = ""
    gate3 = CertificationGateResult(
        gate_number=3,
        gate_name="Scientific Evaluation",
        decision=gate3_decision,
        rationale=(
            f"{n_experiments}/{req_experiments} scientific domains evaluated, "
            f"{n_not_evaluable} not actually measured."
        ),
        metric_observed=float(n_experiments - n_not_evaluable),
        metric_required=float(req_experiments),
        blocking_reason=gate3_blocking,
    )
    gate_results.append(gate3)
    logger.info("gate_evaluated", gate=3, decision=gate3_decision.value, experiments=n_experiments)

    if gate3_decision == GateDecision.BLOCK:
        rationale_parts.append(gate3.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.SCIENTIFICALLY_EVALUATED
    rationale_parts.append(gate3.rationale)

    # ── Gate 4: Statistical (research evidence coverage ≥ config.gate_4_evidence_coverage_required) ──
    gate4_decision = (
        GateDecision.PASS
        if evidence_coverage.overall_coverage >= req_evidence_coverage
        else GateDecision.BLOCK
    )
    gate4 = CertificationGateResult(
        gate_number=4,
        gate_name="Statistical Verification",
        decision=gate4_decision,
        rationale=f"Research Evidence Coverage = {evidence_coverage.overall_coverage:.1f}/100. Evidence Grade: {evidence_coverage.evidence_grade.value}. Required: ≥ {req_evidence_coverage}.",
        metric_observed=evidence_coverage.overall_coverage,
        metric_required=req_evidence_coverage,
        blocking_reason=(
            ""
            if gate4_decision == GateDecision.PASS
            else f"Research Evidence Coverage {evidence_coverage.overall_coverage:.1f} < {req_evidence_coverage}"
        ),
    )
    gate_results.append(gate4)
    logger.info(
        "gate_evaluated",
        gate=4,
        decision=gate4_decision.value,
        evidence_coverage=evidence_coverage.overall_coverage,
    )

    if gate4_decision == GateDecision.BLOCK:
        rationale_parts.append(gate4.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.STATISTICALLY_VERIFIED
    rationale_parts.append(gate4.rationale)

    # ── Gate 5: Reproducibility (≥ config.gate_5_reproducibility_rate) ───────
    n_repro = len(reproducibility_assessments)
    n_reproducible = sum(1 for a in reproducibility_assessments if a.is_reproducible)
    repro_rate = n_reproducible / max(1, n_repro)
    gate5_decision = GateDecision.PASS if repro_rate >= req_repro_rate else GateDecision.BLOCK
    gate5 = CertificationGateResult(
        gate_number=5,
        gate_name="Reproducibility",
        decision=gate5_decision,
        rationale=f"{n_reproducible}/{n_repro} experiments pass CV threshold ({repro_rate:.0%}). Required: ≥ {req_repro_rate:.0%}.",
        metric_observed=repro_rate * 100,
        metric_required=req_repro_rate * 100,
        blocking_reason=(
            ""
            if gate5_decision == GateDecision.PASS
            else f"Only {repro_rate:.0%} of experiments reproducible; required ≥ {req_repro_rate:.0%}"
        ),
    )
    gate_results.append(gate5)
    logger.info(
        "gate_evaluated", gate=5, decision=gate5_decision.value, repro_rate=f"{repro_rate:.0%}"
    )

    if gate5_decision == GateDecision.BLOCK:
        rationale_parts.append(gate5.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.REPRODUCIBLE
    rationale_parts.append(gate5.rationale)

    # ── Gate 6: Artifact Readiness (COMPLETE readiness level) ─────────────────
    gate6_decision = (
        GateDecision.PASS
        if artifact_readiness.readiness_level == ArtifactReadinessLevel.COMPLETE
        else GateDecision.BLOCK
    )
    missing = list(artifact_readiness.criteria_missing)
    gate6 = CertificationGateResult(
        gate_number=6,
        gate_name="Artifact Readiness",
        decision=gate6_decision,
        rationale=(
            "All artifact readiness criteria satisfied."
            if gate6_decision == GateDecision.PASS
            else f"Artifact readiness: {artifact_readiness.readiness_level.value}. Missing: {', '.join(missing[:3])}."
        ),
        metric_observed=None,
        metric_required=None,
        blocking_reason=(
            ""
            if gate6_decision == GateDecision.PASS
            else f"Readiness level: {artifact_readiness.readiness_level.value}"
        ),
    )
    gate_results.append(gate6)
    logger.info(
        "gate_evaluated",
        gate=6,
        decision=gate6_decision.value,
        readiness=artifact_readiness.readiness_level.value,
    )

    if gate6_decision == GateDecision.BLOCK:
        rationale_parts.append(gate6.blocking_reason)
        return level, gate_results, " | ".join(rationale_parts)

    level = CertificationLevel.PUBLICATION_READY
    rationale_parts.append(gate6.rationale)

    # ── Research Certified (all claims supported) ─────────────────────────────
    all_claims_supported = all(c.is_supported for c in research_claims)
    if all_claims_supported:
        level = CertificationLevel.RESEARCH_CERTIFIED
        rationale_parts.append(
            f"All {len(research_claims)} research claims supported by empirical evidence. "
            "SMRITI is a Living Research System."
        )
    else:
        unsupported = sum(1 for c in research_claims if not c.is_supported)
        rationale_parts.append(
            f"Research certification pending: {unsupported}/{len(research_claims)} claims lack support."
        )

    return level, gate_results, " | ".join(rationale_parts)
