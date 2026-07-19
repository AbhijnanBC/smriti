"""
retrieval/validator.py — Candidate pair validation for Phase 6.

Produces ValidatedCandidatePairs (lifecycle: VALIDATED_CANDIDATE).

Rejection reasons:
    SELF_COMPARISON:     claim_id_a == claim_id_b
    DUPLICATE_PAIR:      Same pair appeared twice
    MISSING_CLAIM:       One or both claim IDs not in claims_map
    MISSING_EMBEDDING:   One or both embeddings not in embeddings_map
    BELOW_THRESHOLD:     Cosine similarity < configured threshold
    INVALID_EMBEDDING:   EmbeddedClaim quality check failed

Rules:
    ✅ Returns (valid, rejected_with_reasons) — never raises for individual pairs
    ✅ Logs every rejection reason
    ✅ Produces VALIDATED_CANDIDATE lifecycle stage on valid pairs
    ❌ Never modifies CandidatePair objects
    ❌ Never performs NLI
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import CandidatePair, EmbeddedClaim, Claim, LifecycleStage

logger = structlog.get_logger(__name__)


class RejectionReason(str, Enum):
    SELF_COMPARISON     = "self_comparison"
    DUPLICATE_PAIR      = "duplicate_pair"
    MISSING_CLAIM       = "missing_claim"
    MISSING_EMBEDDING   = "missing_embedding"
    INVALID_EMBEDDING   = "invalid_embedding"
    BELOW_THRESHOLD     = "below_threshold"


@dataclass(frozen=True)
class CandidateValidationResult:
    """Result of validating a single candidate pair."""
    pair: CandidatePair
    is_valid: bool
    rejection_reason: RejectionReason | None = None


def validate_candidates(
    candidates: List[CandidatePair],
    claims_map: Dict[str, Claim],
    embeddings_map: Dict[str, EmbeddedClaim],
    sim_threshold: float,
) -> Tuple[List[CandidatePair], Dict[str, int]]:
    """
    Validate all candidate pairs before NLI inference.
    Valid pairs are promoted to lifecycle stage VALIDATED_CANDIDATE.

    Returns:
        (valid_pairs, rejected_reason_counts)
    """
    valid: List[CandidatePair] = []
    rejected_counts: Dict[str, int] = {}
    seen_pair_keys: Set[str] = set()

    def reject(reason: RejectionReason) -> None:
        key = reason.value
        rejected_counts[key] = rejected_counts.get(key, 0) + 1
        logger.debug("candidate rejected", reason=reason.value)

    for pair in candidates:
        if pair.claim_id_a == pair.claim_id_b:
            reject(RejectionReason.SELF_COMPARISON)
            continue

        pk = pair.pair_key()
        if pk in seen_pair_keys:
            reject(RejectionReason.DUPLICATE_PAIR)
            continue
        seen_pair_keys.add(pk)

        if pair.claim_id_a not in claims_map or pair.claim_id_b not in claims_map:
            reject(RejectionReason.MISSING_CLAIM)
            continue

        if pair.claim_id_a not in embeddings_map or pair.claim_id_b not in embeddings_map:
            reject(RejectionReason.MISSING_EMBEDDING)
            continue

        emb_a = embeddings_map[pair.claim_id_a]
        emb_b = embeddings_map[pair.claim_id_b]
        if not (emb_a.quality.finite and emb_a.quality.dimension_ok):
            reject(RejectionReason.INVALID_EMBEDDING)
            continue
        if not (emb_b.quality.finite and emb_b.quality.dimension_ok):
            reject(RejectionReason.INVALID_EMBEDDING)
            continue

        if pair.cosine_similarity < sim_threshold:
            reject(RejectionReason.BELOW_THRESHOLD)
            continue

        # Promote to VALIDATED_CANDIDATE lifecycle stage
        validated_pair = CandidatePair(
            claim_id_a=pair.claim_id_a,
            claim_id_b=pair.claim_id_b,
            cosine_similarity=pair.cosine_similarity,
            candidate_rank=pair.candidate_rank,
            retrieval_backend=pair.retrieval_backend,
            index_version=pair.index_version,
            search_parameters=pair.search_parameters,
            retrieval_quality=pair.retrieval_quality,
            lifecycle_stage=LifecycleStage.VALIDATED_CANDIDATE,
        )
        valid.append(validated_pair)

    total_rejected = sum(rejected_counts.values())
    logger.info(
        "candidate validation complete",
        total=len(candidates),
        valid=len(valid),
        rejected=total_rejected,
        reasons=rejected_counts,
    )

    return valid, rejected_counts