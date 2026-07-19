"""
classification/conflict.py — Cross-run relationship conflict resolution.

Problem:
    When the pipeline is run multiple times (incremental updates, re-indexing),
    the same claim pair may receive different RelationshipType assignments.

    Example:
        Run 1: (claim_a, claim_b) → SUPPORTS
        Run 2: (claim_a, claim_b) → CONTRADICTS

    Which one wins? This module answers that question deterministically
    according to the configured ConflictResolutionPolicy.

Policies (see models.py ConflictResolutionPolicy):
    LATEST_WINS:         Most recent run's classification wins.
    HIGHEST_CONFIDENCE:  Classification with highest calibrated_confidence wins.
    MOST_SPECIFIC:       Priority: CONTRADICTS > REFINES > SUPPORTS > NEUTRAL > UNKNOWN.
    CONSERVATIVE:        Only keep if all runs agree on the type.

Rules:
    ✅ Deterministic: same inputs → same output
    ✅ Never modifies Relationship objects (returns winner or None)
    ❌ Never calls ML models
    ❌ Never modifies existing relationships
"""

from __future__ import annotations

from typing import List, Optional, Dict, Tuple
import structlog

from smriti.core.models import Relationship, RelationshipType, ConflictResolutionPolicy
from smriti.exceptions import ConflictResolutionError

logger = structlog.get_logger(__name__)

# Priority order for MOST_SPECIFIC policy (higher index = lower priority)
_SPECIFICITY_ORDER = {
    RelationshipType.CONTRADICTS: 0,
    RelationshipType.REFINES:     1,
    RelationshipType.SUPPORTS:    2,
    RelationshipType.NEUTRAL:     3,
    RelationshipType.UNKNOWN:     4,
}


class ConflictResolver:
    """
    Resolves type conflicts between relationships for the same claim pair.
    Instantiate once per pipeline run.
    """

    def __init__(self, policy: ConflictResolutionPolicy) -> None:
        self._policy = policy
        logger.info("conflict resolver initialized", policy=policy.value)

    def resolve_conflicts(
        self,
        relationships: List[Relationship],
    ) -> List[Relationship]:
        """
        Given a list of relationships (potentially with conflicts for the same pair),
        return a deduplicated list according to the conflict policy.

        Args:
            relationships: All relationships from the current run and any loaded
                           prior-run relationships.

        Returns:
            Deduplicated list with at most one Relationship per pair_key.
        """
        # Group by pair_key
        by_pair: Dict[str, List[Relationship]] = {}
        for rel in relationships:
            key = rel.evidence.pair.pair_key()
            by_pair.setdefault(key, []).append(rel)

        resolved: List[Relationship] = []
        for pair_key, candidates in by_pair.items():
            if len(candidates) == 1:
                resolved.append(candidates[0])
            else:
                winner = self._apply_policy(pair_key, candidates)
                if winner is not None:
                    resolved.append(winner)

        logger.info(
            "conflict resolution complete",
            input_count=len(relationships),
            output_count=len(resolved),
            pairs_with_conflicts=sum(
                1 for c in by_pair.values() if len(c) > 1
            ),
        )

        return resolved

    def _apply_policy(
        self,
        pair_key: str,
        candidates: List[Relationship],
    ) -> Optional[Relationship]:
        """Apply the conflict policy to select one winner from conflicting relationships."""
        if self._policy == ConflictResolutionPolicy.LATEST_WINS:
            return max(candidates, key=lambda r: r.provenance.run_id)

        elif self._policy == ConflictResolutionPolicy.HIGHEST_CONFIDENCE:
            return max(candidates, key=lambda r: r.evidence.calibrated_confidence)

        elif self._policy == ConflictResolutionPolicy.MOST_SPECIFIC:
            return min(
                candidates,
                key=lambda r: _SPECIFICITY_ORDER.get(r.relationship_type, 999)
            )

        elif self._policy == ConflictResolutionPolicy.CONSERVATIVE:
            types = {r.relationship_type for r in candidates}
            if len(types) == 1:
                return candidates[0]   # All agree
            else:
                logger.debug(
                    "conservative policy: conflicting types, dropping pair",
                    pair_key=pair_key,
                    types=[t.value for t in types],
                )
                return None   # Disagreement — drop the pair

        else:
            raise ConflictResolutionError(
                f"Unknown conflict resolution policy: {self._policy}"
            )