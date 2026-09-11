"""
report.py — CertificationReport builder (rectified).

RECTIFIED (P0-1): overall_confidence_index is kept for backward compatibility
but is NO LONGER used to determine certification level.
Certification is determined by gate results (gates.py).
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from smriti.core.models import CertificationReport, VerificationStatus


def build_certification_report(
    run_id: str,
    verification_results: list,
    verification_coverage: list,
    engineering_confidence,
    experiment_results: list,
    science_evidence: list,
    research_claims: list,
    statistical_analyses: list,
    reproducibility_assessments: list,
    threats_to_validity: list,
    research_evidence_coverage,
    artifact_readiness,
    certification_level,
    certification_rationale: str,
    gate_results: list | None = None,  # RECTIFIED (P0-1): gate decisions
) -> CertificationReport:
    total_passed = sum(1 for r in verification_results if r.status == VerificationStatus.PASSED)
    total_failed = sum(1 for r in verification_results if r.status == VerificationStatus.FAILED)

    eci_score = engineering_confidence.overall_confidence
    evidence_coverage_score = research_evidence_coverage.overall_coverage
    # Kept for backward compat only — NOT used for gating
    overall = round(0.40 * eci_score + 0.60 * evidence_coverage_score, 2)

    report_id = hashlib.sha256(f"{run_id}:{datetime.now(tz=UTC).isoformat()}".encode()).hexdigest()[
        :16
    ]

    return CertificationReport(
        report_id=report_id,
        run_id=run_id,
        timestamp_iso=datetime.now(tz=UTC).isoformat(),
        verification_results=tuple(verification_results),
        verification_coverage=tuple(verification_coverage),
        engineering_confidence=engineering_confidence,
        experiment_results=tuple(experiment_results),
        science_evidence=tuple(science_evidence),
        research_claims=tuple(research_claims),
        statistical_analyses=tuple(statistical_analyses),
        reproducibility_assessments=tuple(reproducibility_assessments),
        threats_to_validity=tuple(threats_to_validity),
        research_evidence_coverage=research_evidence_coverage,
        artifact_readiness=artifact_readiness,
        gate_results=tuple(gate_results or []),
        certification_level=certification_level,
        certification_rationale=certification_rationale,
        total_rules_passed=total_passed,
        total_rules_failed=total_failed,
        engineering_confidence_index=eci_score,
        research_evidence_coverage_index=evidence_coverage_score,
        overall_confidence_index=overall,
        schema_version="12.1",
    )


def serialize_certification_report(report: CertificationReport) -> str:
    import json

    data = {
        "report_id": report.report_id,
        "run_id": report.run_id,
        "timestamp_iso": report.timestamp_iso,
        "schema_version": report.schema_version,
        "certification": {
            "level": report.certification_level.value,
            "level_name": report.certification_level.name,
            "rationale": report.certification_rationale,
        },
        "gate_results": [
            {
                "gate_number": g.gate_number,
                "gate_name": g.gate_name,
                "decision": g.decision.value,
                "rationale": g.rationale,
                "metric_observed": g.metric_observed,
                "metric_required": g.metric_required,
                "blocking_reason": g.blocking_reason,
            }
            for g in report.gate_results
        ],
        "confidence_indices": {
            "engineering_confidence_index": report.engineering_confidence_index,
            "research_evidence_coverage_index": report.research_evidence_coverage_index,
            "overall_confidence_index": report.overall_confidence_index,
            "note": "overall_confidence_index is informational only; certification determined by gates",
        },
        "engineering_confidence": {
            "architecture": report.engineering_confidence.architecture_confidence,
            "runtime": report.engineering_confidence.runtime_confidence,
            "infrastructure": report.engineering_confidence.infrastructure_confidence,
            "observability": report.engineering_confidence.observability_confidence,
            "governance": report.engineering_confidence.governance_confidence,
            "integration": report.engineering_confidence.integration_confidence,
            "compliance": report.engineering_confidence.compliance_confidence,
            "overall": report.engineering_confidence.overall_confidence,
            "readiness_level": report.engineering_confidence.engineering_readiness_level,
        },
        "research_evidence_coverage": {
            "experiment_pass_rate": report.research_evidence_coverage.experiment_pass_rate,
            "consistency": report.research_evidence_coverage.consistency_confidence,
            "robustness": report.research_evidence_coverage.robustness_confidence,
            "generalization": report.research_evidence_coverage.generalization_confidence,
            "interpretability": report.research_evidence_coverage.interpretability_confidence,
            "measurement_coverage": report.research_evidence_coverage.measurement_coverage,
            "overall": report.research_evidence_coverage.overall_coverage,
            "evidence_grade": report.research_evidence_coverage.evidence_grade.value,
        },
        "verification_summary": {
            "total_rules": report.total_rules_passed + report.total_rules_failed,
            "rules_passed": report.total_rules_passed,
            "rules_failed": report.total_rules_failed,
            "pass_rate": round(
                report.total_rules_passed
                / max(1, report.total_rules_passed + report.total_rules_failed),
                4,
            ),
        },
        "coverage": [
            {
                "category": c.category,
                "total": c.total_rules,
                "passed": c.rules_passed,
                "failed": c.rules_failed,
                "coverage_pct": c.coverage_percentage,
            }
            for c in report.verification_coverage
        ],
        "experiments": [
            {
                "experiment_id": r.experiment_id,
                "status": r.status.value,
                "metrics": r.metrics,
                "execution_seconds": r.execution_time_seconds,
            }
            for r in report.experiment_results
        ],
        "research_claims": [
            {
                "claim_id": c.claim_id,
                "statement": c.statement,
                "domain": c.scientific_domain.value,
                "is_supported": c.is_supported,
                "confidence": c.confidence_score,
                "evidence_grade": c.evidence_grade.value,
                "research_question": c.research_question,
                "null_hypothesis": c.null_hypothesis,
                "assumptions": list(c.assumptions),
                "applicability": c.applicability,
            }
            for c in report.research_claims
        ],
        "artifact_readiness": {
            "readiness_level": report.artifact_readiness.readiness_level.value,
            "criteria_met": list(report.artifact_readiness.criteria_met),
            "criteria_missing": list(report.artifact_readiness.criteria_missing),
            "criteria_partial": list(report.artifact_readiness.criteria_partial),
            "revision_notes": report.artifact_readiness.revision_notes,
        },
        "threats_to_validity": [
            {
                "threat_id": t.threat_id,
                "category": t.category,
                "description": t.description,
                "mitigation": t.mitigation,
                "residual_risk": t.residual_risk,
            }
            for t in report.threats_to_validity
        ],
        "statistical_analyses": [
            {
                "metric": sa.metric_name,
                "n": sa.n_samples,
                "mean": sa.mean,
                "std_dev": sa.std_dev,
                "ci_95": [sa.ci_lower, sa.ci_upper],
                "cv": sa.coefficient_of_variation,
            }
            for sa in report.statistical_analyses
        ],
        "reproducibility_assessments": [
            {
                "experiment_id": ra.experiment_id,
                "n_runs": ra.n_runs,
                "cv": ra.coefficient_of_variation,
                "level": ra.reproducibility_level,
                "is_reproducible": ra.is_reproducible,
            }
            for ra in report.reproducibility_assessments
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
