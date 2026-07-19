"""temporal.py — Temporal stability signal extractor."""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus, TemporalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class TemporalStabilityExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "temporal_stability"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "step_function_temporal_status"

    @property
    def dependency_list(self) -> List[str]:
        return ["temporal_metadata.status", "temporal_metadata.temporal_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        temp = node.temporal_metadata
        tp = policy.temporal

        if temp is None:
            return RawSignal(
                name=self.signal_name,
                raw_value=tp.default_stability,
                normalized_value=tp.default_stability,
                status=SignalStatus.DEFAULT,
                metadata={"reason": "no_temporal_metadata"},
            )

        if temp.status == TemporalStatus.EVOLUTION_CHAIN:
            temporal_conf = temp.temporal_confidence or 0.5
            raw_value = min(1.0, tp.default_stability + tp.evolution_bonus + 0.10 * temporal_conf)
            status = SignalStatus.MEASURED
        elif temp.status == TemporalStatus.STATIC_PARTITION:
            raw_value = tp.default_stability
            status = SignalStatus.MEASURED
        elif temp.status == TemporalStatus.UNRESOLVED_CONFLICT:
            raw_value = max(0.0, tp.default_stability - tp.conflict_penalty)
            status = SignalStatus.ESTIMATED
        else:
            raw_value = tp.default_stability
            status = SignalStatus.DEFAULT

        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=status,
            metadata={"temporal_status": temp.status.value if temp else "none"},
        )