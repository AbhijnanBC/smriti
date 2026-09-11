"""provenance.py — Source diversity signal extractor."""

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


def source_identity(document_id: str, graph: KnowledgeGraph) -> str:
    """
    RECTIFIED (external review, P1-1 "provenance/source lineage"): the
    identity two documents should be compared on for diversity/
    independence purposes is the declared source_id when the document
    discloses one, NOT the document_id -- two document_ids that declare
    the SAME source_id are copies/republications of one underlying
    source (e.g. the same article saved as two files), not two
    independent sources. Falls back to document_id itself when no
    provenance was disclosed (graph.document_provenance has no entry, or
    the entry has no source_id), which is the honest default for the
    overwhelming majority of documents in any corpus today -- this
    function narrows, never widens, what counts as "the same source"
    relative to the old document_id-only behavior.
    """
    prov = graph.document_provenance.get(document_id)
    if prov is not None and prov.source_id:
        return prov.source_id
    return document_id


class SourceDiversityExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.SOURCE_DIVERSITY

    @property
    def version(self) -> str:
        return "1.2"  # Bumped for declared-source-identity (P1-1) grouping

    @property
    def normalization_strategy(self) -> str:
        return "log_scale"

    @property
    def dependency_list(self) -> list[str]:
        return [
            "support_aggregate.supporting_claim_ids",
            "support_aggregate.independent_evidence_group_ids",
            "graph.nodes[supporter].document_id",
            "graph.document_provenance[document_id].source_id",
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
                name=self.signal_id,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_aggregate"},
            )

        # RECTIFIED (provenance/reliability redesign): count documents over
        # independent_evidence_group_ids, not raw supporting_claim_ids --
        # two claims linked by an EQUIVALENT edge are the same restated
        # evidence, and previously each contributed its own document_id to
        # this count even when they were paraphrases of one another, one
        # from each of two documents, inflating apparent source diversity
        # for what is actually one piece of evidence appearing twice. Falls
        # back to supporting_claim_ids for aggregates built before this
        # rectification (independent_evidence_group_ids empty but
        # supporting_claim_ids non-empty is the legacy-fixture signature).
        evidence_ids = (
            node.support_aggregate.independent_evidence_group_ids
            or node.support_aggregate.supporting_claim_ids
        )
        if not evidence_ids:
            return RawSignal(
                name=self.signal_id,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"unique_documents": 0},
            )

        unique_docs = set()
        for cid in evidence_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node:
                unique_docs.add(source_identity(supporter_node.document_id, graph))

        n_unique = len(unique_docs)
        max_possible = max(1, global_stats.max_source_diversity)
        raw_value = math.log1p(n_unique) / math.log1p(max_possible)
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "unique_documents": n_unique,
                "evidence_group_count": len(evidence_ids),
                "raw_supporter_count": len(node.support_aggregate.supporting_claim_ids),
            },
        )
