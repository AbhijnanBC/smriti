"""
evaluation/__init__.py — Phase 12 CertificationEngine.

RECTIFIED:
    - Uses gate-based certification (not weighted average)
    - Produces ResearchAssurancePackage (CertificationReport is one artifact inside it)
    - Builds enriched ResearchClaim objects with scientific fields
    - Manages EvaluationManifest, AssumptionRegistry, LimitationRegistry
    - Detects and resolves evidence conflicts
    - Reports ArtifactReadinessLevel (ordinal, not binary)

Public API:
    from smriti.evaluation import CertificationEngine, run_evaluation
"""

from __future__ import annotations

import time

import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    CertificationReport,
    ResearchAssurancePackage,
    ScienceEvidence,
)
from smriti.evaluation.certification.artifact_readiness import assess_artifact_readiness
from smriti.evaluation.certification.claims import assess_research_claims
from smriti.evaluation.certification.gates import evaluate_certification_gates
from smriti.evaluation.certification.levels import compute_research_evidence_coverage
from smriti.evaluation.certification.manifest import build_evaluation_manifest
from smriti.evaluation.certification.package import build_research_assurance_package
from smriti.evaluation.certification.report import (
    build_certification_report,
    serialize_certification_report,
)
from smriti.evaluation.engineering.architectural import run_architectural_verification
from smriti.evaluation.engineering.confidence import compute_eci, compute_verification_coverage
from smriti.evaluation.scientific.conflict import (
    apply_conflict_adjustments,
    detect_evidence_conflicts,
)
from smriti.evaluation.scientific.experiment import EXPERIMENT_REGISTRY, run_experiment
from smriti.evaluation.statistical.analysis import (
    STANDARD_THREATS,
    compute_statistical_analysis,
)
from smriti.evaluation.statistical.assumptions import ASSUMPTION_REGISTRY
from smriti.evaluation.statistical.limitations import LIMITATION_REGISTRY

logger = structlog.get_logger(__name__)
PHASE12_VERSION = "1.0"


class CertificationEngine:
    """
    Phase 12 Research Assurance Architecture.

    RECTIFIED:
        - Certification determined by 6 sequential gates (not weighted average)
        - Returns ResearchAssurancePackage containing CertificationReport
        - Supports backward-compatible .run() returning CertificationReport
        - .run_full() returns ResearchAssurancePackage
    """

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        logger.info("CertificationEngine initialized", run_id=run_id, version=PHASE12_VERSION)

    def run(self, knowledge_api) -> CertificationReport:
        """Backward-compatible API: returns CertificationReport."""
        pkg = self.run_full(knowledge_api)
        return pkg.certification_report

    def run_full(self, knowledge_api) -> ResearchAssurancePackage:
        """Full API: returns ResearchAssurancePackage (top-level container)."""
        logger.info("phase 12 starting (gate-based certification)", run_id=self._run_id)
        t0 = time.monotonic()

        # ── Part 2: Engineering Verification ─────────────────────────────────
        logger.info("part 2: engineering verification")
        verification_results = run_architectural_verification()
        verification_coverage = compute_verification_coverage(verification_results)
        eci = compute_eci(verification_results)
        logger.info(
            "engineering verification complete",
            passed=sum(1 for r in verification_results if r.status.value == "passed"),
            total=len(verification_results),
            eci=f"{eci.overall_confidence:.1f}",
        )

        # ── Part 3: Scientific Evaluation ─────────────────────────────────────
        logger.info("part 3: scientific evaluation")
        experiment_results = []
        for experiment in EXPERIMENT_REGISTRY:
            result = run_experiment(experiment, knowledge_api, self._run_id)
            experiment_results.append(result)
        logger.info(
            "scientific evaluation complete",
            experiments=len(experiment_results),
            passed=sum(1 for r in experiment_results if r.status.value == "passed"),
        )

        # ── Part 4: Statistical Analysis ──────────────────────────────────────
        logger.info("part 4: statistical analysis")
        statistical_analyses = []
        # RECTIFIED (scientific cleanup): reproducibility assessments require
        # REAL independent repeated runs of an experiment. The previous
        # version fabricated one by duplicating a single measurement
        # (`values=[primary_metric, primary_metric]`), which has zero
        # variance by construction and therefore ALWAYS reports "excellent"
        # reproducibility regardless of whether the experiment is remotely
        # stable. Since a single pipeline invocation runs each experiment
        # exactly once, there is no real multi-run data to assess here —
        # reproducibility_assessments is honestly empty. Gate 5 in gates.py
        # correctly treats an empty list as 0% reproducible and blocks
        # advancement past STATISTICALLY_VERIFIED, which is the accurate
        # state of affairs until a genuine multi-run study is performed
        # (see paper Limitations: "single-run experiments").
        reproducibility_assessments: list = []

        for result in experiment_results:
            for metric, value in result.metrics.items():
                if isinstance(value, int | float):
                    sa = compute_statistical_analysis(
                        metric_name=f"{result.experiment_id}:{metric}",
                        values=[value],
                    )
                    statistical_analyses.append(sa)

        research_claims = assess_research_claims(experiment_results)

        # RECTIFIED (P1-5): Detect and resolve evidence conflicts
        science_evidence: list[ScienceEvidence] = []  # Populated when full evidence model is built
        conflicts = detect_evidence_conflicts(science_evidence)
        if conflicts:
            research_claims = apply_conflict_adjustments(research_claims, conflicts)
            logger.info("evidence_conflicts_resolved", count=len(conflicts))

        evidence_coverage = compute_research_evidence_coverage(
            experiment_results=experiment_results,
            research_claims=research_claims,
            reproducibility_assessments=reproducibility_assessments,
        )
        logger.info(
            "statistical analysis complete",
            evidence_coverage=f"{evidence_coverage.overall_coverage:.1f}",
            claims_supported=sum(1 for c in research_claims if c.is_supported),
        )

        # ── Part 5: Certification ─────────────────────────────────────────────
        logger.info("part 5: gate-based certification")

        # RECTIFIED (P1-6): Ordinal publication readiness
        artifact_readiness = assess_artifact_readiness(
            research_claims=research_claims,
            reproducibility_assessments=reproducibility_assessments,
            eci=eci,
        )

        # RECTIFIED (P0-1): Gate-based certification (not weighted average)
        certification_level, gate_results, rationale = evaluate_certification_gates(
            verification_results=verification_results,
            experiment_results=experiment_results,
            reproducibility_assessments=reproducibility_assessments,
            research_claims=research_claims,
            eci=eci,
            evidence_coverage=evidence_coverage,
            artifact_readiness=artifact_readiness,
        )

        gates_passed = sum(1 for g in gate_results if g.decision.value == "pass")
        logger.info(
            "certification complete",
            level=certification_level.value,
            level_name=certification_level.name,
            gates_passed=f"{gates_passed}/{len(gate_results)}",
            artifact_readiness_level=artifact_readiness.readiness_level.value,
        )

        # ── Assemble CertificationReport ──────────────────────────────────────
        report = build_certification_report(
            run_id=self._run_id,
            verification_results=verification_results,
            verification_coverage=verification_coverage,
            engineering_confidence=eci,
            experiment_results=experiment_results,
            science_evidence=science_evidence,
            research_claims=research_claims,
            statistical_analyses=statistical_analyses,
            reproducibility_assessments=reproducibility_assessments,
            threats_to_validity=list(STANDARD_THREATS),
            research_evidence_coverage=evidence_coverage,
            artifact_readiness=artifact_readiness,
            certification_level=certification_level,
            certification_rationale=rationale,
            gate_results=gate_results,
        )

        # RECTIFIED (P0-big): Build ResearchAssurancePackage
        evaluation_manifest = build_evaluation_manifest(
            run_id=self._run_id,
            experiments=list(EXPERIMENT_REGISTRY),
            policy_version=get_config().get("scoring_policy", {}).get("version", "1.0"),
        )

        package = build_research_assurance_package(
            run_id=self._run_id,
            certification_report=report,
            experiments=list(EXPERIMENT_REGISTRY),
            science_evidence=science_evidence,
            evaluation_manifest=evaluation_manifest,
            assumption_registry=list(ASSUMPTION_REGISTRY),
            limitation_registry=list(LIMITATION_REGISTRY),
            evidence_conflicts=conflicts,
        )

        total_time = time.monotonic() - t0
        logger.info(
            "phase 12 complete",
            run_id=self._run_id,
            certification_level=certification_level.name,
            eci=f"{eci.overall_confidence:.1f}",
            evidence_coverage=f"{evidence_coverage.overall_coverage:.1f}",
            gates_passed=gates_passed,
            artifact_readiness_level=artifact_readiness.readiness_level.value,
            runtime_seconds=f"{total_time:.2f}",
        )

        return package


def run_evaluation(
    knowledge_api, run_id: str, manifest_manager, state_manager
) -> CertificationReport:
    """Execute Phase 12 as part of the pipeline. Writes artifacts, returns CertificationReport."""
    start_time = manifest_manager.start_phase(phase=12)

    engine = CertificationEngine(run_id=run_id)
    package = engine.run_full(knowledge_api)
    report = package.certification_report

    # Write artifacts
    phase_dir = (
        manifest_manager.run_dir / "phase12"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)

    report_json = serialize_certification_report(report)
    (phase_dir / "certification_report.json").write_text(report_json, encoding="utf-8")

    # Write evaluation manifest
    import json as _json

    manifest_data = {
        "manifest_id": package.evaluation_manifest.manifest_id,
        "run_id": run_id,
        "experiment_ids": list(package.evaluation_manifest.experiment_ids),
        "policy_version": package.evaluation_manifest.policy_version,
        "random_seeds": package.evaluation_manifest.random_seeds,
        "software_versions": package.evaluation_manifest.software_versions,
        "hardware_description": package.evaluation_manifest.hardware_description,
        "created_at": package.evaluation_manifest.created_at,
    }
    (phase_dir / "evaluation_manifest.json").write_text(
        _json.dumps(manifest_data, indent=2), encoding="utf-8"
    )

    logger.info("certification artifacts written", path=str(phase_dir))

    manifest_manager.end_phase(
        phase=12,
        start_time=start_time,
        inputs={"run_id": run_id},
        outputs={
            "certification_level": report.certification_level.value,
            "certification_name": report.certification_level.name,
            "eci": report.engineering_confidence_index,
            "evidence_coverage": report.research_evidence_coverage_index,
            "gates_passed": sum(1 for g in report.gate_results if g.decision.value == "pass"),
            "artifact_readiness_level": report.artifact_readiness.readiness_level.value,
            "report_path": str(phase_dir / "certification_report.json"),
            "schema_version": report.schema_version,
        },
        status="success",
    )

    state_manager.complete_phase(phase=12)
    return report
