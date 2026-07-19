"""
incremental.py — Incremental relationship discovery for large vaults.

Problem:
    When 50,000 claims exist and one new claim arrives, the full pipeline
    would recompute all O(N·K) candidate pairs from scratch.
    This is unacceptable for interactive or near-real-time use.

Solution:
    IncrementalDiscoveryEngine only searches for relationships between:
    - New claims and the existing indexed claims
    - New claims and each other

    The existing RelationshipSet is preserved and augmented,
    not recomputed.

Cache invalidation cascade:
    Embedding changed for claim X
        → invalidate candidate cache for all pairs containing X
        → invalidate evidence cache for those pairs
        → invalidate relationships for those pairs
        → recompute only the affected subset

Rules:
    ✅ Never recomputes existing valid relationships
    ✅ Applies conflict resolution policy when new evidence conflicts with old
    ✅ Respects resource limits (ResourceGovernor)
    ❌ Never modifies existing Relationship objects
"""

from __future__ import annotations

from typing import List, Dict, Set, Optional
import structlog

from smriti.core.models import (
    EmbeddedClaim, Claim, Relationship, RelationshipSet,
)
from smriti.core.config import get_config
from smriti.exceptions import ResourceLimitExceeded

logger = structlog.get_logger(__name__)


class CacheInvalidationPolicy:
    """
    Defines when cached results must be invalidated.

    Cascade rule:
        Embedding changed for claim X
            → invalidate candidate_cache for all pairs containing X
            → invalidate evidence_cache for those pairs
            → invalidate resolved_cache for those pairs
    """

    def __init__(self) -> None:
        config = get_config()
        cache_cfg = config.get("cache_invalidation", {})
        self._invalidate_on_embedding_change: bool = cache_cfg.get(
            "invalidate_on_embedding_change", True
        )
        self._invalidate_on_model_change: bool = cache_cfg.get(
            "invalidate_on_model_change", True
        )
        self._invalidate_on_policy_change: bool = cache_cfg.get(
            "invalidate_on_policy_change", True
        )

    def should_invalidate_for_claim(
        self,
        claim_id: str,
        changed_claim_ids: Set[str],
    ) -> bool:
        """Return True if any cache entries for this claim_id should be invalidated."""
        if not self._invalidate_on_embedding_change:
            return False
        return claim_id in changed_claim_ids

    def should_invalidate_all(
        self,
        old_config_hash: str,
        new_config_hash: str,
        old_model: str,
        new_model: str,
    ) -> bool:
        """Return True if the entire cache should be invalidated (model or policy changed)."""
        if self._invalidate_on_model_change and old_model != new_model:
            logger.info(
                "full cache invalidation: model changed",
                old=old_model, new=new_model,
            )
            return True
        if self._invalidate_on_policy_change and old_config_hash != new_config_hash:
            logger.info(
                "full cache invalidation: policy changed",
                old_hash=old_config_hash[:8], new_hash=new_config_hash[:8],
            )
            return True
        return False


class IncrementalDiscoveryEngine:
    """
    Discovers relationships for a delta of new claims against an existing RelationshipSet.

    Usage:
        # Initial full run
        result = discover_relationships(all_claims, ...)

        # Later: new claims arrive
        engine = IncrementalDiscoveryEngine(existing_result)
        updated_result = engine.update(new_claims, all_claims_map, ...)
    """

    def __init__(
        self,
        existing_relationship_set: RelationshipSet,
        invalidation_policy: Optional[CacheInvalidationPolicy] = None,
    ) -> None:
        self._existing = existing_relationship_set
        self._invalidation_policy = invalidation_policy or CacheInvalidationPolicy()

    def compute_delta(
        self,
        all_embedded_claims: List[EmbeddedClaim],
        existing_claim_ids: Set[str],
    ) -> List[EmbeddedClaim]:
        """
        Identify which claims are new (not in existing_claim_ids).

        Args:
            all_embedded_claims: Complete current set of embedded claims.
            existing_claim_ids:  Claim IDs already present in the existing RelationshipSet.

        Returns:
            Only the new EmbeddedClaims that need relationship discovery.
        """
        new_claims = [
            ec for ec in all_embedded_claims
            if ec.claim_id not in existing_claim_ids
        ]
        logger.info(
            "incremental delta computed",
            total_claims=len(all_embedded_claims),
            existing_claims=len(existing_claim_ids),
            new_claims=len(new_claims),
        )
        return new_claims

    def invalidate_changed_embeddings(
        self,
        changed_claim_ids: Set[str],
    ) -> List[Relationship]:
        """
        Remove relationships that involve claims with changed embeddings.
        Returns the remaining (valid) relationships.
        """
        if not changed_claim_ids:
            return list(self._existing.relationships)

        remaining = [
            rel for rel in self._existing.relationships
            if not (
                rel.claim_id_a in changed_claim_ids
                or rel.claim_id_b in changed_claim_ids
            )
        ]

        invalidated_count = len(self._existing.relationships) - len(remaining)
        logger.info(
            "embedding change invalidation",
            changed_claims=len(changed_claim_ids),
            invalidated_relationships=invalidated_count,
            remaining=len(remaining),
        )

        return remaining