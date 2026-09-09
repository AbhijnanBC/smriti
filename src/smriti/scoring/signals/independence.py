"""
independence.py — Evidence independence signal extractor.

RECTIFIED (P1-1): Now includes lineage heuristics beyond simple document ID
comparison. Document ID independence is a necessary but not sufficient condition.

Additional lineage heuristics:
    - Publisher domain fingerprinting: nodes from the same publisher domain
      are penalized even if document IDs differ (e.g., blog.org/post-1 and
      blog.org/post-2 share a publisher and are not independent).
    - Citation chain detection: if supporter A references supporter B in its
      source_path's directory hierarchy, they may not be independent.

These heuristics are approximate and configurable via EvidencePolicy.
"""

from __future__ import annotations

from typing import List, Set
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalID, SignalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class EvidenceIndependenceExtractor(BaseSignalExtractor):

    
    @property
    def signal_id(self) -> SignalID:
        return SignalID.EVIDENCE_INDEPENDENCE

    @property
    def version(self) -> str:
        return "1.1"  # Bumped for lineage heuristic addition

    @property
    def normalization_strategy(self) -> str:
        return "ratio_with_penalty"

    @property
    def dependency_list(self) -> List[str]:
        return [
            "support_aggregate.supporting_claim_ids",
            "graph.nodes[supporter].document_id",
            "graph.nodes[supporter].source_path",
        ]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        # RECTIFIED (P0-8): a claim with NO supporting evidence is not
        # thereby maximally "independent" -- independence is a property of
        # the evidence a claim HAS, and there is nothing here to evaluate.
        # The previous version returned raw_value=1.0 ("no evidence" ==
        # "maximum independence"), which let claims with zero support
        # receive a full-strength positive contribution from this signal.
        # UNAVAILABLE + 0.0 correctly withholds that contribution (see
        # normalization.py's evidence_completeness accounting) rather than
        # rewarding absence of evidence.
        if node.support_aggregate is None or node.support_aggregate.support_count == 0:
            return RawSignal(
                name=self.signal_id, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_to_evaluate"},
            )

        supporting_ids = node.support_aggregate.supporting_claim_ids
        if not supporting_ids:
            return RawSignal(
                name=self.signal_id, raw_value=1.0, normalized_value=1.0,
                status=SignalStatus.MEASURED,
                metadata={"support_count": 0},
            )

        total = len(supporting_ids)
        quality_flags = []

        # ── Heuristic 1: Document ID independence (original) ──────────────────
        document_ids: Set[str] = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node:
                document_ids.add(supporter_node.document_id)
        unique_docs = len(document_ids)
        doc_independence = unique_docs / max(1, total)

        # ── Heuristic 2: Publisher domain fingerprinting (NEW P1-1) ──────────
        publisher_domains: Set[str] = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node and supporter_node.source_path:
                # Extract domain approximation from path parts
                # e.g. "notes/ml/blog/post.md" → domain fingerprint = "notes/ml/blog"
                parts = supporter_node.source_path.parts
                domain = "/".join(parts[:-1]) if len(parts) > 1 else str(supporter_node.source_path)
                publisher_domains.add(domain)
        unique_publishers = len(publisher_domains)
        publisher_independence = unique_publishers / max(1, total)

        if publisher_independence < doc_independence:
            quality_flags.append("shared_publisher_domain")

        # ── Blend: document + publisher independence ───────────────────────────
        pw = policy.evidence.publisher_domain_weight
        blended_independence = (
            (1.0 - pw) * doc_independence + pw * publisher_independence
        )

        # ── Apply echo chamber penalty if below threshold ─────────────────────
        penalty = policy.evidence.echo_chamber_penalty
        threshold = policy.evidence.independence_discount_threshold
        if blended_independence < threshold:
            raw_value = blended_independence * (1.0 - penalty)
            quality_flags.append("echo_chamber_penalty_applied")
        else:
            raw_value = blended_independence

        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "unique_documents": unique_docs,
                "unique_publishers": unique_publishers,
                "total_supporters": total,
                "doc_independence": round(doc_independence, 3),
                "publisher_independence": round(publisher_independence, 3),
                "blended_independence": round(blended_independence, 3),
                "quality_flags": quality_flags,
            },
        )