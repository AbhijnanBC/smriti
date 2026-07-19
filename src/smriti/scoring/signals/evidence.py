"""evidence.py — Evidence strength signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class EvidenceStrengthExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.EVIDENCE_STRENGTH

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale_blended_confidence"

    @property
    def dependency_list(self) -> List[str]:
        return ["support_aggregate.support_count", "support_aggregate.weighted_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
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

        max_count = max(1, global_stats.max_support_count)
        log_norm = math.log1p(support_count) / math.log1p(max_count)
        raw_value = 0.7 * log_norm + 0.3 * weighted_conf
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "support_count": support_count,
                "weighted_confidence": weighted_conf,
            },
        )