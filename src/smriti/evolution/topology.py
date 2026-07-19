"""
topology.py — Topology analysis for Phase 7.

RECTIFIED (P0-3): Bridge detection uses the backend's articulation_points()
method, which delegates to NetworkX nx.articulation_points() on the undirected
projection. This is the true graph-theoretic definition of a bridge node.

The original `is_bridge = (total == 1 and n > 2)` was a degree-1 leaf heuristic,
NOT bridge detection. Example failure:
    A → B → C
    B has degree 2. It IS an articulation point (bridge).
    Old code: is_bridge=False (degree != 1). WRONG.
    Fixed code: is_bridge=True (articulation_points returns B). CORRECT.

RECTIFIED (P1-4): Hub detection threshold read from AnnotationPolicy (config),
not hardcoded to 2.0. Centrality formula unchanged: in_degree / (N-1).

Complexity: O(N + E) per partition, O(N + E) for articulation points.
"""

from __future__ import annotations

from typing import Dict, Set
import dataclasses
import structlog

from smriti.core.models import TopologyMetrics, NodeAnnotations
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


def run_topology_analysis(
    ctx: SemanticReasoningContext,
    hub_degree_multiplier: float = 2.0,
) -> None:
    """
    Compute topology metrics for all nodes within their partitions.

    Args:
        ctx:                   SemanticReasoningContext.
        hub_degree_multiplier: Config-driven (knowledge_graph.hub_degree_multiplier).
                               A node is a hub if degree > multiplier * avg_partition_degree.

    Updates ctx.topology_metrics and ctx.nodes (via NodeAnnotations replacement).
    """
    topology: Dict[str, TopologyMetrics] = {}

    for partition_id, partition in ctx.partitions.items():
        partition_nodes = list(partition.node_ids)
        if not partition_nodes:
            continue

        # Get partition subgraph
        sub = ctx.backend.subgraph(partition_nodes)
        n = partition.node_count

        # Compute degrees for all nodes in partition
        node_degrees = {}
        for node_id in partition_nodes:
            total = sub.degree(node_id)
            in_deg = sub.in_degree(node_id)
            out_deg = sub.out_degree(node_id)
            node_degrees[node_id] = (total, in_deg, out_deg)

        # Average degree for hub detection (config-driven, not hardcoded)
        avg_degree = (
            sum(d[0] for d in node_degrees.values()) / n if n > 0 else 0.0
        )

        # True bridge detection via articulation_points (P0-3 fix)
        art_points: Set[str] = set(sub.articulation_points())

        for node_id in partition_nodes:
            total, in_deg, out_deg = node_degrees[node_id]

            # Directed in-degree centrality: in_degree / (N-1)
            centrality = in_deg / (n - 1) if n > 1 else 0.0

            # Hub: degree significantly above average (config-driven threshold)
            is_hub = total > max(1.0, avg_degree * hub_degree_multiplier)

            # Bridge: true articulation point (NOT degree-1 heuristic)
            is_bridge = node_id in art_points

            metrics = TopologyMetrics(
                degree=total,
                in_degree=in_deg,
                out_degree=out_deg,
                is_bridge=is_bridge,
                is_hub=is_hub,
                partition_id=partition_id,
                centrality=round(centrality, 6),
            )
            topology[node_id] = metrics

    ctx.topology_metrics = topology

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        metrics = topology.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, topology=metrics)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    logger.info("topology analysis complete", nodes_enriched=len(topology))