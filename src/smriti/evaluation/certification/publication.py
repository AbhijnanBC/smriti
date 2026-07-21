"""
publication.py — Publication Readiness Assessment (rectified P1-6).

RECTIFIED (P1-6): Publication readiness is NOT binary.
It uses PublicationReadinessLevel:
    COMPLETE        — all criteria met, ready to submit
    MINOR_REVISION  — small gaps, easily addressed
    MAJOR_REVISION  — significant work required
    NOT_READY       — fundamental gaps remain

This mirrors standard journal reviewer language and provides
actionable guidance rather than a pass/fail verdict.
"""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    PublicationReadinessAssessment, PublicationReadinessLevel,
    ResearchClaim, ReproducibilityAssessment, EngineeringConfidenceIndex,
)


def assess_publication_readiness(
    research_claims: List[ResearchClaim],
    reproducibility_assessments: List[ReproducibilityAssessment],
    eci: EngineeringConfidenceIndex,
) -> PublicationReadinessAssessment:
    """
    RECTIFIED (P1-6): Assess using ordinal PublicationReadinessLevel.

    Criteria assessed:
        clarity                 — ≥ 4 formally stated research claims
        supporting_evidence     — all claims supported by experiment
        statistical_justification — at least one experiment "good" or "excellent" reproducibility
        reproducibility         — at least one reproducible experiment
        novelty_documented      — novel architecture documented in ADRs (assumed)
        limitations_documented  — limitation registry populated (assumed)
        ethical_compliance      — local-first, no PII (assumed)
        artifact_availability   — ECI ≥ 60 (artifacts producible)
    """
    criteria_met = []
    criteria_missing = []
    criteria_partial = []

    # 1. Clarity (≥4 research claims)
    if len(research_claims) >= 6:
        criteria_met.append("clarity")
    elif len(research_claims) >= 4:
        criteria_partial.append("clarity")
    else:
        criteria_missing.append("clarity")

    # 2. Supporting evidence (all claims supported)
    if all(c.is_supported for c in research_claims):
        criteria_met.append("supporting_evidence")
    elif any(c.is_supported for c in research_claims):
        criteria_partial.append("supporting_evidence")
    else:
        criteria_missing.append("supporting_evidence")

    # 3. Statistical justification
    if any(a.reproducibility_level in ("excellent", "good") for a in reproducibility_assessments) if reproducibility_assessments else False:
        criteria_met.append("statistical_justification")
    elif any(a.reproducibility_level == "moderate" for a in reproducibility_assessments) if reproducibility_assessments else False:
        criteria_partial.append("statistical_justification")
    else:
        criteria_missing.append("statistical_justification")

    # 4. Reproducibility
    if any(a.is_reproducible for a in reproducibility_assessments) if reproducibility_assessments else False:
        criteria_met.append("reproducibility")
    else:
        criteria_missing.append("reproducibility")

    # 5. Novelty documented (ADRs document architectural novelty — assumed True)
    criteria_met.append("novelty_documented")

    # 6. Limitations documented (LimitationRegistry populated — assumed True)
    criteria_met.append("limitations_documented")

    # 7. Ethical compliance (local-first, no PII — assumed True)
    criteria_met.append("ethical_compliance")

    # 8. Artifact availability (ECI ≥ 60)
    if eci.overall_confidence >= 60.0:
        criteria_met.append("artifact_availability")
    elif eci.overall_confidence >= 40.0:
        criteria_partial.append("artifact_availability")
    else:
        criteria_missing.append("artifact_availability")

    # Determine readiness level (RECTIFIED P1-6)
    if len(criteria_missing) == 0 and len(criteria_partial) == 0:
        readiness = PublicationReadinessLevel.COMPLETE
        notes = "All criteria satisfied. Ready for submission."
    elif len(criteria_missing) == 0 and len(criteria_partial) <= 2:
        readiness = PublicationReadinessLevel.MINOR_REVISION
        notes = f"Minor gaps in: {', '.join(criteria_partial)}. Address before submission."
    elif len(criteria_missing) <= 2:
        readiness = PublicationReadinessLevel.MAJOR_REVISION
        notes = f"Significant gaps: {', '.join(criteria_missing)}. Substantial work required."
    else:
        readiness = PublicationReadinessLevel.NOT_READY
        notes = f"Fundamental gaps: {', '.join(criteria_missing)}. Major rework needed."

    return PublicationReadinessAssessment(
        readiness_level=readiness,
        criteria_met=tuple(criteria_met),
        criteria_missing=tuple(criteria_missing),
        criteria_partial=tuple(criteria_partial),
        revision_notes=notes,
    )