"""
artifact_readiness.py — Artifact Readiness Assessment (rectified P1-6, renamed P2).

RECTIFIED (P1-6): Readiness is NOT binary.
It uses ArtifactReadinessLevel:
    COMPLETE        — all criteria met, ready to submit
    MINOR_REVISION  — small gaps, easily addressed
    MAJOR_REVISION  — significant work required
    NOT_READY       — fundamental gaps remain

This mirrors standard journal reviewer language and provides
actionable guidance rather than a pass/fail verdict.

RECTIFIED (P2, external "reality check" review): completed the rename
this module's own docstring had already argued for -- see below.
PublicationReadiness(Assessment/Level) are now ArtifactReadiness(Assessment/Level)
throughout, and assess_publication_readiness is assess_artifact_readiness.

RECTIFIED (P2, "FINAL REVIEW" round): the FILE itself was still named
publication.py even though every symbol inside it had already been
renamed away from "publication" in the pass above -- the one remaining
stale name was the module's own filename. Renamed to artifact_readiness.py
to match; import as smriti.evaluation.certification.artifact_readiness.
"""

from __future__ import annotations

from smriti.core.models import (
    ArtifactReadinessAssessment,
    ArtifactReadinessLevel,
    EngineeringVerificationIndex,
    ReproducibilityAssessment,
    ResearchClaim,
)


# Evaluates several independent publication-readiness criteria (claim
# support, reproducibility, engineering confidence, etc.) as a flat set of
# checks; each check is simple, but there are enough of them to trip
# mccabe's threshold.
def assess_artifact_readiness(  # noqa: C901
    research_claims: list[ResearchClaim],
    reproducibility_assessments: list[ReproducibilityAssessment],
    eci: EngineeringVerificationIndex,
) -> ArtifactReadinessAssessment:
    """
    RECTIFIED (P1-6, and again per external review): Assess using ordinal
    ArtifactReadinessLevel, over ONLY criteria this function can actually
    verify from the artifacts it receives.

    RECTIFIED (external review, "PublicationReadiness pseudo-science"): this
    function previously appended "novelty_documented", "limitations_documented",
    and "ethical_compliance" to criteria_met unconditionally, with comments
    literally reading "(assumed True)" — fabricating three "met" criteria with
    no evidence behind them, exactly the defect category the rest of Phase 12
    was rebuilt to eliminate. Those three are removed rather than patched:
    whether a paper documents its novelty/limitations/ethics honestly is an
    editorial and human-reviewer judgment, not something this function can
    measure from a ResearchClaim/ReproducibilityAssessment/ECI triple. This
    function's output describes ARTIFACT readiness (does the evidence and
    tooling exist), not publication readiness in the human-reviewer sense --
    which is now also reflected in the function and dataclass names
    themselves (P2), not just this comment.

    Also fixed: "clarity" previously required >= 6 research claims to ever
    reach "met", when the frozen registry has always had exactly 5 (RC1-RC5)
    since the P0 cleanup — a threshold this system could never satisfy by its
    own intentional design. It now checks that all five canonical claim IDs
    are actually present in the registry (a real integrity check), not an
    arbitrary count threshold.

    Criteria assessed:
        clarity                    — all 5 canonical claims (RC1-RC5) present
        supporting_evidence        — all claims supported by experiment
        statistical_justification  — at least one experiment "good"/"excellent" reproducibility
        reproducibility            — at least one reproducible experiment
        artifact_availability      — ECI ≥ 60 (artifacts producible)
    """
    criteria_met = []
    criteria_missing = []
    criteria_partial = []

    # 1. Clarity: are all five frozen canonical claims present?
    canonical_ids = {"RC1", "RC2", "RC3", "RC4", "RC5"}
    present_ids = {c.claim_id for c in research_claims}
    if canonical_ids.issubset(present_ids):
        criteria_met.append("clarity")
    elif present_ids & canonical_ids:
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
    if (
        any(a.reproducibility_level in ("excellent", "good") for a in reproducibility_assessments)
        if reproducibility_assessments
        else False
    ):
        criteria_met.append("statistical_justification")
    elif (
        any(a.reproducibility_level == "moderate" for a in reproducibility_assessments)
        if reproducibility_assessments
        else False
    ):
        criteria_partial.append("statistical_justification")
    else:
        criteria_missing.append("statistical_justification")

    # 4. Reproducibility
    if (
        any(a.is_reproducible for a in reproducibility_assessments)
        if reproducibility_assessments
        else False
    ):
        criteria_met.append("reproducibility")
    else:
        criteria_missing.append("reproducibility")

    # 5. Artifact availability (ECI ≥ 60)
    if eci.overall_confidence >= 60.0:
        criteria_met.append("artifact_availability")
    elif eci.overall_confidence >= 40.0:
        criteria_partial.append("artifact_availability")
    else:
        criteria_missing.append("artifact_availability")

    # Determine readiness level (RECTIFIED P1-6)
    if len(criteria_missing) == 0 and len(criteria_partial) == 0:
        readiness = ArtifactReadinessLevel.COMPLETE
        notes = "All criteria satisfied. Ready for submission."
    elif len(criteria_missing) == 0 and len(criteria_partial) <= 2:
        readiness = ArtifactReadinessLevel.MINOR_REVISION
        notes = f"Minor gaps in: {', '.join(criteria_partial)}. Address before submission."
    elif len(criteria_missing) <= 2:
        readiness = ArtifactReadinessLevel.MAJOR_REVISION
        notes = f"Significant gaps: {', '.join(criteria_missing)}. Substantial work required."
    else:
        readiness = ArtifactReadinessLevel.NOT_READY
        notes = f"Fundamental gaps: {', '.join(criteria_missing)}. Major rework needed."

    return ArtifactReadinessAssessment(
        readiness_level=readiness,
        criteria_met=tuple(criteria_met),
        criteria_missing=tuple(criteria_missing),
        criteria_partial=tuple(criteria_partial),
        revision_notes=notes,
    )
