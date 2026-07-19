"""
Unit tests for aggregation.py provenance-root deduplication fix (P0-2).

Verifies that support aggregation counts unique supporting claim IDs,
not unique traversal paths. In a DAG like:

    A → B → D
    A → C → D

A supports D through two paths. Old code: A counted twice.
New code: A counted exactly once (unique provenance root).
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning
from smriti.evolution.aggregation import run_evidence_aggregation


def make_supports_edge(eid, src, tgt, confidence=0.88):
    return RelationshipEdge(
        edge_id=eid, source_node_id=src, target_node_id=tgt,
        relationship_type=RelationshipType.SUPPORTS,
        direction=RelationshipDirection.A_TO_B,
        calibrated_confidence=confidence, cosine_similarity=0.85,
        nli_confidence=confidence, candidate_rank=1,
    )


def make_ctx_with_edges(node_ids, edge_specs):
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
            context="", source_path=Path("test.md"), document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt, conf in edge_specs:
        edge = make_supports_edge(eid, src, tgt, conf)
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", conf)
    return SemanticReasoningContext(
        nodes=nodes, edges=edges, backend=backend, run_id="test", config_hash="test",
    )


def test_dag_diamond_does_not_double_count():
    """
    RECTIFIED (P0-2): Diamond DAG test.

    A → B → D
    A → C → D

    D's support_count must be 3 (A, B, C), not 4 (A counted twice in old code).
    A is the unique provenance root that supports D through two paths.
    """
    ctx = make_ctx_with_edges(
        ["A", "B", "C", "D"],
        [
            ("e1", "A", "B", 0.90),
            ("e2", "A", "C", 0.85),
            ("e3", "B", "D", 0.88),
            ("e4", "C", "D", 0.88),
        ],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_D = ctx.nodes["D"].support_aggregate
    assert agg_D is not None
    supporting = set(agg_D.supporting_claim_ids)
    # A, B, and C all transitively support D
    assert "A" in supporting
    assert "B" in supporting
    assert "C" in supporting
    # A must appear exactly once
    assert agg_D.support_count == len(supporting), (
        f"support_count ({agg_D.support_count}) must equal len(unique claim IDs) "
        f"({len(supporting)}). Each claim must be counted at most once."
    )


def test_direct_support_count():
    """Single direct SUPPORTS: count = 1."""
    ctx = make_ctx_with_edges(
        ["A", "B"],
        [("e1", "A", "B", 0.88)],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_B = ctx.nodes["B"].support_aggregate
    assert agg_B.support_count == 1
    assert "A" in agg_B.supporting_claim_ids


def test_no_support_count_zero():
    """Node with no incoming SUPPORTS: count = 0."""
    ctx = make_ctx_with_edges(["A"], [])
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_A = ctx.nodes["A"].support_aggregate
    assert agg_A.support_count == 0