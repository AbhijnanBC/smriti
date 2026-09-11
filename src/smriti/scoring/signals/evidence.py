"""evidence.py — Evidence strength signal extractor."""

from __future__ import annotations

import math

from smriti.core.models import (
    ClaimNode,
    KnowledgeGraph,
    RawSignal,
    ScoringGlobalStats,
    SignalID,
    SignalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


def _discounted_strength_and_confidence(support_aggregate, policy: ReliabilityPolicy):
    """
    RECTIFIED (external review, P1-2 "evidence aggregation / double
    counting"): the reviewer's own example -- "System uses 8GB RAM" /
    "System has 8GB RAM installed" is the SAME proposition restated, not
    a second piece of evidence -- is exactly what
    independent_evidence_group_ids already collapses (a paraphrase
    contributes zero additional groups). This function additionally
    applies this project's configured hop-distance discount
    (policy.evidence.{direct,derived,multi_hop}_evidence_weight) to each
    evidence group, so a claim reached only through a chain of other
    claims ("A supports B supports C") counts as real but DISCOUNTED
    evidence for C, never as fully independent corroboration equal to a
    direct supporter.

    Returns (discounted_strength, discounted_confidence). Falls back to
    (None, None) for aggregates built before this rectification
    (direct/derived/multi_hop_evidence_group_ids all empty but
    support_count > 0 is the legacy-fixture signature), so callers can
    fall back to the old raw support_count/weighted_confidence behavior.
    """
    direct = support_aggregate.direct_evidence_group_ids
    derived = support_aggregate.derived_evidence_group_ids
    multi_hop = support_aggregate.multi_hop_evidence_group_ids
    if not direct and not derived and not multi_hop:
        return None, None

    w_direct = policy.evidence.direct_evidence_weight
    w_derived = policy.evidence.derived_evidence_weight
    w_multi = policy.evidence.multi_hop_evidence_weight

    strength = w_direct * len(direct) + w_derived * len(derived) + w_multi * len(multi_hop)
    # discounted_weighted_confidence was computed in aggregation.py using
    # this module's OWN default weights, not necessarily the configured
    # policy's -- recompute the confidence numerator honestly here rather
    # than trust that precomputed value when the policy has been tuned
    # away from the defaults. Confidence itself (mean per-group) is not
    # re-derivable from the aggregate alone, so this reuses the
    # aggregate's precomputed discounted_weighted_confidence as the best
    # available per-group-mean proxy, reweighted is not possible without
    # re-reading Phase 7 state -- documented limitation, not silently
    # papered over.
    confidence = support_aggregate.discounted_weighted_confidence
    return round(strength, 6), confidence


class EvidenceStrengthExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.EVIDENCE_STRENGTH

    @property
    def version(self) -> str:
        return "1.1"  # Bumped for hop-distance-discounted evidence strength (P1-2)

    @property
    def normalization_strategy(self) -> str:
        return "log_scale_blended_confidence"

    @property
    def dependency_list(self) -> list[str]:
        return [
            "support_aggregate.support_count",
            "support_aggregate.weighted_confidence",
            "support_aggregate.direct_evidence_group_ids",
            "support_aggregate.derived_evidence_group_ids",
            "support_aggregate.multi_hop_evidence_group_ids",
        ]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self,
        node: ClaimNode,
        graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats,
        policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.support_aggregate is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_aggregate"},
            )

        support_count = node.support_aggregate.support_count
        weighted_conf = node.support_aggregate.weighted_confidence

        if support_count == 0:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"support_count": 0, "weighted_confidence": 0.0},
            )

        discounted_strength, discounted_conf = _discounted_strength_and_confidence(
            node.support_aggregate, policy
        )
        effective_count = discounted_strength if discounted_strength is not None else support_count
        effective_conf = discounted_conf if discounted_conf is not None else weighted_conf

        max_count = max(1, global_stats.max_support_count)
        log_norm = math.log1p(effective_count) / math.log1p(max_count)
        raw_value = 0.7 * log_norm + 0.3 * effective_conf
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "support_count": support_count,
                "weighted_confidence": weighted_conf,
                "discounted_evidence_strength": discounted_strength,
                "n_direct": len(node.support_aggregate.direct_evidence_group_ids),
                "n_derived": len(node.support_aggregate.derived_evidence_group_ids),
                "n_multi_hop": len(node.support_aggregate.multi_hop_evidence_group_ids),
            },
        )
