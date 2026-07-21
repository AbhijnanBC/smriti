"""provenance.py — Source diversity signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalID, SignalStatus
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class SourceDiversityExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.SOURCE_DIVERSITY

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale"

    @property
    def dependency_list(self) -> List[str]:
        return ["support_aggregate.supporting_claim_ids", "graph.nodes[supporter].document_id"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.support_aggregate is None:
            return RawSignal(
                name=self.signal_id, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_aggregate"},
            )

        supporting_ids = node.support_aggregate.supporting_claim_ids
        if not supporting_ids:
            return RawSignal(
                name=self.signal_id, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"unique_documents": 0},
            )

        unique_docs = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node:
                unique_docs.add(supporter_node.document_id)

        n_unique = len(unique_docs)
        max_possible = max(1, global_stats.max_source_diversity)
        raw_value = math.log1p(n_unique) / math.log1p(max_possible)
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={"unique_documents": n_unique},
        )