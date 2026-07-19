"""conflict.py — Conflict pressure signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus, RelationshipType,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class ConflictPressureExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "conflict_pressure"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale_saturating"

    @property
    def dependency_list(self) -> List[str]:
        return ["graph.edges[CONTRADICTS]", "edge.calibrated_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        claim_id = node.claim_id
        contradiction_edges = [
            e for e in graph.edges.values()
            if e.relationship_type == RelationshipType.CONTRADICTS
            and (e.source_node_id == claim_id or e.target_node_id == claim_id)
        ]
        n_contradictions = len(contradiction_edges)

        if n_contradictions == 0:
            return RawSignal(
                name=self.signal_name, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"contradiction_count": 0},
            )

        max_c = max(1, global_stats.max_contradiction_partners)
        normalized_count = math.log1p(n_contradictions) / math.log1p(max_c)
        saturation = policy.conflict.conflict_saturation
        raw_sat = normalized_count / saturation if normalized_count < saturation else 1.0

        avg_confidence = (
            sum(e.calibrated_confidence for e in contradiction_edges) / n_contradictions
        )
        raw_value = raw_sat * (0.7 + 0.3 * avg_confidence)
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "contradiction_count": n_contradictions,
                "avg_contradiction_confidence": round(avg_confidence, 3),
            },
        )