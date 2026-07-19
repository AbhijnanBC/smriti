"""
aggregation.py — Evidence aggregation for Phase 7.

RECTIFIED (P0-2): The original BFS deduplication used visited_edges (unique edges),
not unique supporting CLAIM IDs. In a DAG like:

    A → B → D
    A → C → D

BFS visiting D's incoming edges reaches A via two paths. Original code tracked
visited_edges, meaning it would add A's confidence once per path — double-counting.

Fix: Track supporting_claim_ids as a set. Add a claim's contribution only the
first time it appears, regardless of how many paths lead from it to the target.
This is "aggregate over unique provenance roots, not unique traversal paths."

Rules:
    - Follows only SUPPORTS edges within the same partition
    - Counts each unique supporting claim_id exactly ONCE
    - CONTRADICTS edges never contribute support
    - Aggregation never modifies edge confidence values
    - Never crosses partition boundaries
"""

from __future__ import annotations

import dataclasses
from collections import deque
from typing import Dict, Set
import structlog

from smriti.core.models import SupportAggregate, RelationshipType, NodeAnnotations
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


def run_evidence_aggregation(ctx: SemanticReasoningContext) -> None:
    """
    Aggregate SUPPORTS evidence for every node within its partition.
    Counts unique provenance root claim IDs, not traversal paths.
    """
    aggregates: Dict[str, SupportAggregate] = {}

    for partition_id, partition in ctx.partitions.items():
        partition_node_ids = partition.node_ids

        # Precompute: for each node, which SUPPORTS edges point TO it (same partition)
        incoming_supports: Dict[str, list] = {nid: [] for nid in partition_node_ids}
        # Also track: for each supporting claim, its edge confidence
        claim_confidence: Dict[str, float] = {}  # claim_id → confidence of its direct support edge

        for edge in ctx.edges.values():
            if (edge.relationship_type == RelationshipType.SUPPORTS
                    and edge.target_node_id in partition_node_ids
                    and edge.source_node_id in partition_node_ids):
                incoming_supports[edge.target_node_id].append(edge)
                # Store per-claim confidence for the first direct edge encountered
                if edge.source_node_id not in claim_confidence:
                    claim_confidence[edge.source_node_id] = edge.calibrated_confidence

        for node_id in partition_node_ids:
            # BFS: collect all transitive UNIQUE CLAIM IDs (not unique paths)
            # RECTIFIED (P0-2): supporting_ids tracks claim IDs seen,
            # ensuring each supporting claim is counted at most once regardless
            # of how many paths lead from it to node_id.
            supporting_ids: Set[str] = set()
            total_confidence = 0.0

            queue = deque(incoming_supports.get(node_id, []))
            visited_edge_ids: Set[str] = set()

            while queue:
                edge = queue.popleft()
                if edge.edge_id in visited_edge_ids:
                    continue
                visited_edge_ids.add(edge.edge_id)

                source_id = edge.source_node_id
                if source_id not in supporting_ids:
                    # First time we reach this claim — count its contribution
                    supporting_ids.add(source_id)
                    total_confidence += claim_confidence.get(source_id, edge.calibrated_confidence)
                # Always BFS further upstream (even if we've seen source_id before,
                # there may be new unique supporters upstream)
                for upstream_edge in incoming_supports.get(source_id, []):
                    if upstream_edge.edge_id not in visited_edge_ids:
                        queue.append(upstream_edge)

            # Weighted confidence = mean over unique supporting claims
            weighted_confidence = (
                total_confidence / len(supporting_ids) if supporting_ids else 0.0
            )
            summary = (
                f"{len(supporting_ids)} unique supporting claim(s), "
                f"avg confidence {weighted_confidence:.2f}"
                if supporting_ids else "No supporting evidence"
            )

            aggregates[node_id] = SupportAggregate(
                support_count=len(supporting_ids),
                weighted_confidence=round(weighted_confidence, 6),
                supporting_claim_ids=tuple(sorted(supporting_ids)),
                evidence_summary=summary,
            )

    ctx.support_aggregates = aggregates

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        agg = aggregates.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, support_aggregate=agg)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    logger.info(
        "evidence aggregation complete (unique provenance roots)",
        nodes_with_support=sum(1 for a in aggregates.values() if a.support_count > 0),
        total_nodes=len(aggregates),
    )