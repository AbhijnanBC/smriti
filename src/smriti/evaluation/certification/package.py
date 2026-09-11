"""
package.py — ResearchAssurancePackage for Phase 12 (P0-big).

RECTIFIED (P0-big): ResearchAssurancePackage is the top-level object.
CertificationReport is one artifact inside this package.

This scales to:
    - Multiple publications (each gets its own CertificationReport inside the same package)
    - Repeated evaluation cycles (package accumulates evidence over time)
    - Multi-domain research (different EvidenceLedger slices per domain)
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import structlog
from smriti.core.models import (
    AssumptionRecord,
    CertificationReport,
    EvaluationManifest,
    EvidenceConflict,
    ExperimentDesign,
    LimitationRecord,
    ResearchAssurancePackage,
    ScienceEvidence,
)

logger = structlog.get_logger(__name__)


def build_research_assurance_package(
    run_id: str,
    certification_report: CertificationReport,
    experiments: list[ExperimentDesign],
    science_evidence: list[ScienceEvidence],
    evaluation_manifest: EvaluationManifest,
    assumption_registry: list[AssumptionRecord],
    limitation_registry: list[LimitationRecord],
    evidence_conflicts: list[EvidenceConflict],
) -> ResearchAssurancePackage:
    """
    Assemble the complete Research Assurance Package.

    The package is the archival artifact. CertificationReport is one component.
    """
    package_id = hashlib.sha256(
        f"{run_id}:{datetime.now(tz=UTC).isoformat()}".encode()
    ).hexdigest()[:12]

    # Compute integrity checksums for all artifacts
    integrity_checksums: dict = {
        "certification_report": hashlib.sha256(certification_report.report_id.encode()).hexdigest()[
            :16
        ],
        "evaluation_manifest": hashlib.sha256(evaluation_manifest.manifest_id.encode()).hexdigest()[
            :16
        ],
        "package": hashlib.sha256(package_id.encode()).hexdigest()[:16],
    }

    package = ResearchAssurancePackage(
        package_id=package_id,
        run_id=run_id,
        created_at=datetime.now(tz=UTC).isoformat(),
        certification_report=certification_report,
        experiment_registry=tuple(experiments),
        evidence_ledger=tuple(science_evidence),
        evaluation_manifest=evaluation_manifest,
        assumption_registry=tuple(assumption_registry),
        limitation_registry=tuple(limitation_registry),
        evidence_conflicts=tuple(evidence_conflicts),
        integrity_checksums=integrity_checksums,
    )

    logger.info(
        "research_assurance_package_assembled",
        package_id=package_id,
        certification_level=certification_report.certification_level.name,
        experiments=len(experiments),
        assumptions=len(assumption_registry),
        limitations=len(limitation_registry),
        conflicts=len(evidence_conflicts),
    )
    return package
