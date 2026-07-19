"""
classification/validator.py — Relationship structural validation.

Enforces the Relationship Ontology invariants:
    1. CONTRADICTS must have SYMMETRIC direction.
    2. SUPPORTS must have A_TO_B or B_TO_A direction.
    3. REFINES must have A_TO_B or B_TO_A direction.
    4. NEUTRAL must have SYMMETRIC direction.
    5. UNKNOWN must never pass (unless skip_unknown=False, debugging only).
    6. confidence >= min_confidence floor.
    7. Not both entailment AND contradiction above threshold simultaneously.

Valid relationships are promoted to lifecycle stage VALIDATED_RELATIONSHIP.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict
import structlog

from smriti.core.models import (
    RelationshipEvidence, RelationshipType, RelationshipDirection, LifecycleStage,
)

logger = structlog.get_logger(__name__)


class RelRejectionReason(str, Enum):
    CONFIDENCE_TOO_LOW      = "confidence_too_low"
    UNKNOWN_RELATIONSHIP    = "unknown_relationship"
    CONTRADICTORY_EVIDENCE  = "contradictory_evidence"
    DIRECTION_INVARIANT     = "direction_invariant_violated"


@dataclass(frozen=True)
class RelationshipValidationResult:
    is_valid: bool
    rejection_reason: RelRejectionReason | None = None


# Ontology invariants: required direction per type
_REQUIRED_DIRECTION = {
    RelationshipType.CONTRADICTS: {RelationshipDirection.SYMMETRIC},
    RelationshipType.NEUTRAL:     {RelationshipDirection.SYMMETRIC},
    RelationshipType.SUPPORTS:    {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.REFINES:     {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.UNKNOWN:     {RelationshipDirection.SYMMETRIC},   # rejected anyway
}


def validate_relationship(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
) -> RelationshipValidationResult:
    """Validate one resolved relationship."""
    # Check 1: Minimum confidence
    if evidence.calibrated_confidence < min_confidence:
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.CONFIDENCE_TOO_LOW,
        )

    # Check 2: Unknown relationship
    if skip_unknown and relationship_type == RelationshipType.UNKNOWN:
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.UNKNOWN_RELATIONSHIP,
        )

    # Check 3: Contradictory evidence (both E and C above threshold)
    if (evidence.nli_scores.entailment_score >= nli_threshold and
            evidence.nli_scores.contradiction_score >= nli_threshold):
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.CONTRADICTORY_EVIDENCE,
        )

    # Check 4: Direction invariant (ontology specification)
    required_dirs = _REQUIRED_DIRECTION.get(relationship_type, set())
    if required_dirs and direction not in required_dirs:
        logger.warning(
            "direction invariant violated",
            type=relationship_type.value,
            direction=direction.value,
            required=[d.value for d in required_dirs],
        )
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.DIRECTION_INVARIANT,
        )

    return RelationshipValidationResult(is_valid=True)


def validate_all_relationships(
    evidence_with_types: List[Tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]],
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
) -> Tuple[List[Tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]], Dict[str, int]]:
    """
    Validate a batch of resolved relationships.
    Valid items are tagged with lifecycle VALIDATED_RELATIONSHIP.

    Returns:
        (valid_triples, rejection_counts)
        valid_triples: (evidence, type, direction) tuples that passed.
    """
    valid = []
    rejection_counts: Dict[str, int] = {}

    for evidence, rel_type, direction in evidence_with_types:
        result = validate_relationship(
            evidence, rel_type, direction, min_confidence, nli_threshold, skip_unknown
        )
        if result.is_valid:
            valid.append((evidence, rel_type, direction))
        else:
            reason = result.rejection_reason.value
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

    logger.info(
        "relationship validation complete",
        total=len(evidence_with_types),
        valid=len(valid),
        rejected=sum(rejection_counts.values()),
        reasons=rejection_counts,
    )

    return valid, rejection_counts