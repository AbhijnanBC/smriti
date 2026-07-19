"""
Unit tests for topology.py bridge detection fix (P0-3).

Verifies that bridge detection uses articulation_points (NetworkX),
NOT the degree-1 heuristic from the original implementation.
"""

import pytest
from pathlib import Path
from smriti.core.models import ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection, KnowledgePartition
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.topology import run_topology_analysis
from smriti.evolution.partitioning import run_partitioning


def make_ctx_chain(node_ids, edges_list):
    """Build a chain context for bridge testing."""
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
            context="", source_path=Path("test.md"), document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt in edges_list:
        edge = RelationshipEdge(
            edge_id=eid, source_node_id=src, target_node_id=tgt,
            relationship_type=RelationshipType.SUPPORTS,
            direction=RelationshipDirection.A_TO_B,
            calibrated_confidence=0.88, cosine_similarity=0.85,
            nli_confidence=0.88, candidate_rank=1,
        )
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", 0.88)
    return SemanticReasoningContext(
        nodes=nodes, edges=edges, backend=backend, run_id="test", config_hash="test",
    )


def test_middle_node_in_chain_is_bridge():
    """
    RECTIFIED (P0-3): A → B → C
    B is the articulation point (bridge). Removing B disconnects A and C.
    Old code: is_bridge=False (B has degree 2, not 1). WRONG.
    New code: is_bridge=True (nx.articulation_points returns B). CORRECT.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    assert ctx.topology_metrics["B"].is_bridge is True, (
        "B is the only path between A and C; removing B disconnects the graph. "
        "B must be detected as a bridge (articulation point)."
    )


def test_leaf_node_is_not_bridge():
    """
    A → B → C: C is a leaf (degree 1 in undirected). It is NOT an articulation point.
    Old code incorrectly flagged leaf nodes as bridges.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    # C has degree 1 in undirected, but removing it doesn't disconnect the rest
    assert ctx.topology_metrics["C"].is_bridge is False, (
        "C is a leaf node. Removing C doesn't disconnect A and B. "
        "C must NOT be a bridge."
    )


def test_cycle_has_no_bridges():
    """
    A → B → C → A (cycle): No bridges.
    In a cycle, no single node removal disconnects the graph.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C"), ("e3", "C", "A")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    for node_id, metrics in ctx.topology_metrics.items():
        assert metrics.is_bridge is False, (
            f"No node in a cycle should be a bridge. Node {node_id} incorrectly flagged."
        )