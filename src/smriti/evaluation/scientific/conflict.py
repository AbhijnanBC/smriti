"""
conflict.py — Evidence Conflict Framework (P1-5).

RECTIFIED (P1-5): When two experiments produce conflicting evidence
on the same claim, this framework detects, classifies, and resolves
the conflict and updates the claim's confidence accordingly.

Pipeline:
    Evidence → Conflict Detection → Conflict Resolution → Confidence Update → Reviewer Note
"""

from __future__ import annotations

import uuid

import structlog
from smriti.core.models import (
    EvidenceConflict,
    ResearchClaim,
    ScienceEvidence,
)

logger = structlog.get_logger(__name__)


def detect_evidence_conflicts(
    science_evidence: list[ScienceEvidence],
) -> list[EvidenceConflict]:
    """
    Detect conflicts between evidence items targeting the same claim.

    A conflict exists when:
        - Two evidence items target the same claim (supports_claim)
        - One item's observed_value >= its threshold (supporting)
        - The other item's observed_value < its threshold (contradicting)
    """
    by_claim: dict[str, list[ScienceEvidence]] = {}
    for ev in science_evidence:
        by_claim.setdefault(ev.supports_claim, []).append(ev)

    conflicts: list[EvidenceConflict] = []
    for claim_id, evidences in by_claim.items():
        if len(evidences) < 2:
            continue
        supporting = [e for e in evidences if e.observed_value >= e.threshold]
        contradicting = [e for e in evidences if e.observed_value < e.threshold]
        if supporting and contradicting:
            for sup in supporting:
                for con in contradicting:
                    conflict = EvidenceConflict(
                        conflict_id=str(uuid.uuid4())[:8],
                        claim_id=claim_id,
                        evidence_a_id=sup.evidence_id,
                        evidence_b_id=con.evidence_id,
                        conflict_type="contradicts",
                        resolution="higher_quality_evidence_preferred",
                        confidence_impact=-0.10,  # Reduce confidence by 10%
                        reviewer_note=(
                            f"EXP {sup.experiment_id} supports claim "
                            f"({sup.observed_value:.3f} >= {sup.threshold:.3f}) but "
                            f"EXP {con.experiment_id} contradicts it "
                            f"({con.observed_value:.3f} < {con.threshold:.3f}). "
                            "Reviewer should inspect experimental conditions."
                        ),
                    )
                    conflicts.append(conflict)
                    logger.warning(
                        "evidence_conflict_detected",
                        claim_id=claim_id,
                        conflict_id=conflict.conflict_id,
                    )

    return conflicts


def apply_conflict_adjustments(
    claims: list[ResearchClaim],
    conflicts: list[EvidenceConflict],
) -> list[ResearchClaim]:
    """
    Update claim confidence scores based on resolved conflicts.
    Returns new ResearchClaim list (immutable originals unchanged).
    """
    import dataclasses

    conflict_map: dict[str, float] = {}
    for conflict in conflicts:
        conflict_map[conflict.claim_id] = (
            conflict_map.get(conflict.claim_id, 0.0) + conflict.confidence_impact
        )

    updated = []
    for claim in claims:
        impact = conflict_map.get(claim.claim_id, 0.0)
        if abs(impact) > 1e-6:
            new_confidence = max(0.0, min(1.0, claim.confidence_score + impact))
            updated.append(dataclasses.replace(claim, confidence_score=round(new_confidence, 4)))
            logger.info(
                "claim_confidence_adjusted_for_conflict",
                claim_id=claim.claim_id,
                original=claim.confidence_score,
                adjusted=new_confidence,
            )
        else:
            updated.append(claim)
    return updated
