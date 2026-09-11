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

import structlog
from smriti.core.models import (
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipType,
)
from smriti.retrieval.classification.resolver import compute_decision_confidence

logger = structlog.get_logger(__name__)


class RelRejectionReason(str, Enum):
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    UNKNOWN_RELATIONSHIP = "unknown_relationship"
    NEUTRAL_RELATIONSHIP = "neutral_relationship"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    DIRECTION_INVARIANT = "direction_invariant_violated"


@dataclass(frozen=True)
class RelationshipValidationResult:
    is_valid: bool
    rejection_reason: RelRejectionReason | None = None


# Ontology invariants: required direction per type
_REQUIRED_DIRECTION = {
    RelationshipType.CONTRADICTS: {RelationshipDirection.SYMMETRIC},
    RelationshipType.EQUIVALENT: {RelationshipDirection.SYMMETRIC},
    RelationshipType.NEUTRAL: {RelationshipDirection.SYMMETRIC},
    RelationshipType.SUPPORTS: {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.REFINES: {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.UNKNOWN: {RelationshipDirection.SYMMETRIC},  # rejected anyway
}


def validate_relationship(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
    skip_neutral: bool = False,
) -> RelationshipValidationResult:
    """
    Validate one resolved relationship.

    RECTIFIED (external "reality check" review, P0-7-class defect found
    while re-running SMRITI-Reference): `relationship_discovery.
    skip_neutral_relationships` was documented in config/default.yaml
    ("NEUTRAL adds no Phase 7 signal; omit by default") but no code path
    ever read it -- NEUTRAL relationships were persisted to every Phase 6
    output regardless of the flag's value, in every environment, since
    this project began tracking it. skip_neutral is now a real parameter,
    threaded through exactly like skip_unknown.

    RECTIFIED (external "reality check" review round 3, P0-5/P0-6): this
    function previously checked ONLY the A->B calibrated confidence and
    ONLY the A->B entailment/contradiction scores, even for relationships
    the resolver decided from the B->A direction (or symmetrically from
    both). Both checks below now reason over the direction(s) the
    resolution actually depends on.
    """
    # Check 1: Minimum confidence -- the ACTUAL decision confidence for
    # this relation_type/direction (P0-5), not always the A->B reading.
    decision_confidence = compute_decision_confidence(evidence, relationship_type, direction)
    if decision_confidence < min_confidence:
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

    # Check 2b: Neutral relationship (RECTIFIED: previously a no-op flag)
    if skip_neutral and relationship_type == RelationshipType.NEUTRAL:
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.NEUTRAL_RELATIONSHIP,
        )

    # Check 3: Contradictory evidence (both E and C above threshold) --
    # RECTIFIED (P0-6): checked in BOTH directions when bidirectional
    # evidence exists. An NLI reading that is internally inconsistent
    # (high entailment AND high contradiction simultaneously) is a sign
    # of an unreliable model output regardless of which direction the
    # resolver's decision happened to depend on -- e.g. a resolver
    # decision of B_TO_A must not skip checking self-consistency of the
    # A->B reading just because the decision didn't use it directly.
    ab_inconsistent = (
        evidence.nli_scores.entailment_score >= nli_threshold
        and evidence.nli_scores.contradiction_score >= nli_threshold
    )
    ba_inconsistent = False
    if evidence.nli_scores_b_to_a is not None:
        ba = evidence.nli_scores_b_to_a
        ba_inconsistent = (
            ba.entailment_score >= nli_threshold and ba.contradiction_score >= nli_threshold
        )
    if ab_inconsistent or ba_inconsistent:
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
    evidence_with_types: list[tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]],
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
    skip_neutral: bool = False,
) -> tuple[
    list[tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]], dict[str, int]
]:
    """
    Validate a batch of resolved relationships.
    Valid items are tagged with lifecycle VALIDATED_RELATIONSHIP.

    Returns:
        (valid_triples, rejection_counts)
        valid_triples: (evidence, type, direction) tuples that passed.
    """
    valid = []
    rejection_counts: dict[str, int] = {}

    for evidence, rel_type, direction in evidence_with_types:
        result = validate_relationship(
            evidence,
            rel_type,
            direction,
            min_confidence,
            nli_threshold,
            skip_unknown,
            skip_neutral=skip_neutral,
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
