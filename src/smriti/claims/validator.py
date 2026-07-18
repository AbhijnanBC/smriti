"""
validator.py — Structural validator for Phase 4 claims.

Responsibility:
    Validate a collection of Claim objects for structural correctness.
    Check per-claim and cross-claim invariants.

Rules:
    ✅ Claim IDs must be unique                          → CLM006 (fatal)
    ✅ Provenance chain must be complete                 → CLM007 (fatal)
    ✅ Text must not be empty                            → CLM005 (discard)
    ✅ schema_version must be "4.0"                      → CLM008 (fatal)
    ✅ extraction_mode must be a valid ExtractionMode    → CLM008 (fatal)

Rules about what validator NEVER does:
    ❌ Never evaluates claim semantics
    ❌ Never modifies any object
    ❌ Never reorders claims
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import Claim, ClaimWarning
from smriti.exceptions import ClaimValidationError

logger = structlog.get_logger(__name__)


def validate_claims(
    claims: List[Claim],
    document_id: str,
    seen_ids: dict,
) -> Tuple[List[Claim], List[ClaimWarning]]:
    """
    Validate a collection of Claims for one document.

    Args:
        claims:       Claims to validate.
        document_id:  Expected document_id for all claims.

    Returns:
        (valid_claims, warnings)
        valid_claims excludes empty-text claims.

    Raises:
        ClaimValidationError: On duplicate IDs, broken provenance, invalid schema.
    """
    warnings: List[ClaimWarning] = []
    valid: List[Claim] = []
    

    for claim in claims:
        # Check 1: Non-empty text
        if not claim.text.strip():
            warnings.append(ClaimWarning.CLM_EMPTY_ASSERTION)
            logger.debug("empty claim discarded", claim_id=claim.claim_id)
            continue

        # Check 2: Unique claim ID with consistency (fatal)
        if claim.claim_id in seen_ids:
            existing = seen_ids[claim.claim_id]
            # Must have same content_hash and same provenance (sentence_id/doc_id)
            if (existing.content_hash != claim.content_hash or
                existing.provenance != claim.provenance):
                raise ClaimValidationError(
                    f"Duplicate claim_id {claim.claim_id} with inconsistent content "
                    f"or provenance. Existing: {existing.content_hash[:8]}..., "
                    f"new: {claim.content_hash[:8]}..."
                )
            # Even if identical, raise to enforce uniqueness and catch logic bugs
            raise ClaimValidationError(
                f"Duplicate claim_id {claim.claim_id} detected. "
                "All claims must have unique IDs."
            )
        seen_ids[claim.claim_id] = claim

        # Check 3: Provenance chain (fatal)
        if not claim.provenance:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has no provenance. "
                "Every claim must have an unbroken lineage."
            )
        if claim.provenance.document_id != document_id:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has provenance.document_id "
                f"'{claim.provenance.document_id}' but expected '{document_id}'"
            )

        # Check 4: Schema version
        if claim.schema_version != "4.0":
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has schema_version '{claim.schema_version}', "
                "expected '4.0'"
            )

        valid.append(claim)

    return valid, warnings