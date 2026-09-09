"""temporal.py — Temporal stability signal extractor."""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalID, SignalStatus, TemporalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class TemporalStabilityExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.TEMPORAL_STABILITY

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
        # RECTIFIED (external review, item 21): a claim with NO temporal
        # information is not thereby "moderately stable" -- it is a claim
        # this signal has nothing to measure for. The previous version
        # returned raw_value=policy.temporal.default_stability (0.5) with
        # status=DEFAULT for both a missing temporal_metadata object and for
        # TemporalStatus.NO_TIMESTAMP itself (whose own enum comment already
        # says "Claim.timestamp unavailable -> disabled"), silently handing
        # every claim without a timestamp a real, unearned positive
        # contribution to the fusion sum -- the same "absence of evidence
        # treated as a measured value" defect already fixed for
        # evidence_independence (scoring/signals/independence.py). Both
        # cases now return UNAVAILABLE + 0.0, withholding the contribution
        # rather than defaulting it, consistent with that fix.
        temp = node.temporal_metadata
        tp = policy.temporal

        if temp is None:
            return RawSignal(
                name=self.signal_id,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
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
            # TemporalStatus.NO_TIMESTAMP: "Claim.timestamp unavailable -> disabled".
            return RawSignal(
                name=self.signal_id,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_timestamp", "temporal_status": temp.status.value},
            )

        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id,
            raw_value=raw_value,
            normalized_value=normalized,
            status=status,
            metadata={"temporal_status": temp.status.value if temp else "none"},
        )