"""
graph_stats.py — Global graph statistics for Phase 8.

Computed ONCE per scoring run and shared by all signal extractors.
This avoids repeated graph traversals and ensures consistent normalization.

Why compute globally?
    Each signal extractor must normalize against the SAME baseline.
    If EvidenceStrength uses "local maximum" and Topology uses "global maximum",
    the normalization becomes inconsistent and comparisons break.
"""

from __future__ import annotations

import structlog

from smriti.core.models import KnowledgeGraph, RelationshipType, ScoringGlobalStats
from smriti.scoring.signals.provenance import source_identity

logger = structlog.get_logger(__name__)


def compute_global_stats(graph: KnowledgeGraph) -> ScoringGlobalStats:
    """Compute graph-wide statistics for normalization baselines."""
    if graph.node_count == 0:
        return ScoringGlobalStats(
            max_support_count=1,
            avg_support_count=0.0,
            max_in_degree=1,
            avg_degree=0.0,
            max_contradiction_partners=1,
            avg_contradiction_partners=0.0,
            max_source_diversity=1,
            max_temporal_confidence=1.0,
            node_count=0,
            partition_count=0,
            contradiction_count=0,
            supports_count=0,
        )

    support_counts = []
    source_diversity_counts = []
    in_degrees = []
    all_degrees = []
    contradiction_partners = []
    temporal_confidences = []

    for claim_id, node in graph.nodes.items():
        support_count = 0
        if node.support_aggregate:
            support_count = node.support_aggregate.support_count
        support_counts.append(support_count)

        # RECTIFIED (external "reality check" review round 3, P1
        # "max_source_diversity still needs correction"): this used to
        # reuse support_counts (raw supporter COUNT) as the normalization
        # denominator for source-diversity scoring -- a different
        # quantity entirely. A claim with 10 supporters that are all
        # republications of the same source has source diversity 1, not
        # 10; using raw support count as the ceiling systematically
        # understated every claim's normalized source diversity. Computed
        # here the same way signals/provenance.py's SourceDiversityExtractor
        # computes it per-claim (independent_evidence_group_ids, resolved
        # through source_identity() so republications of the same
        # declared source collapse), so numerator and denominator are
        # finally the same quantity.
        n_unique_sources = 0
        if node.support_aggregate:
            evidence_ids = (
                node.support_aggregate.independent_evidence_group_ids
                or node.support_aggregate.supporting_claim_ids
            )
            unique_sources = set()
            for cid in evidence_ids:
                supporter_node = graph.nodes.get(cid)
                if supporter_node:
                    unique_sources.add(source_identity(supporter_node.document_id, graph))
            n_unique_sources = len(unique_sources)
        source_diversity_counts.append(n_unique_sources)

        if node.topology:
            in_degrees.append(node.topology.in_degree)
            all_degrees.append(node.topology.degree)

        n_contradicts = sum(
            1
            for e in graph.edges.values()
            if e.relationship_type == RelationshipType.CONTRADICTS
            and (e.source_node_id == claim_id or e.target_node_id == claim_id)
        )
        contradiction_partners.append(n_contradicts)

        if node.temporal_metadata and node.temporal_metadata.temporal_confidence > 0:
            temporal_confidences.append(node.temporal_metadata.temporal_confidence)

    n = max(1, graph.node_count)

    return ScoringGlobalStats(
        max_support_count=max(support_counts) if support_counts else 1,
        avg_support_count=sum(support_counts) / n,
        max_in_degree=max(in_degrees) if in_degrees else 1,
        avg_degree=sum(all_degrees) / max(1, len(all_degrees)),
        max_contradiction_partners=max(contradiction_partners) if contradiction_partners else 1,
        avg_contradiction_partners=sum(contradiction_partners) / n,
        max_source_diversity=max(source_diversity_counts) if source_diversity_counts else 1,
        max_temporal_confidence=max(temporal_confidences) if temporal_confidences else 1.0,
        node_count=graph.node_count,
        partition_count=graph.partition_count,
        contradiction_count=graph.statistics.contradiction_count,
        supports_count=graph.statistics.supports_count,
    )
