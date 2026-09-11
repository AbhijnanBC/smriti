"""Unit tests for evolution/partitioning.py — constraint-based algorithm."""

from pathlib import Path

from smriti.core.models import (
    ClaimNode,
    RelationshipDirection,
    RelationshipEdge,
    RelationshipType,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning


def make_ctx(node_ids, edges_list):
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid,
            claim_id=nid,
            claim_text=f"Claim {nid}",
            context="",
            source_path=Path("test.md"),
            document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt, rtype in edges_list:
        edge = RelationshipEdge(
            edge_id=eid,
            source_node_id=src,
            target_node_id=tgt,
            relationship_type=rtype,
            direction=RelationshipDirection.SYMMETRIC,
            calibrated_confidence=0.88,
            cosine_similarity=0.85,
            nli_confidence=0.88,
            candidate_rank=1,
        )
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, rtype.value, 0.88)
        if rtype == RelationshipType.CONTRADICTS:
            backend.add_edge(tgt, src, f"{eid}_rev", rtype.value, 0.88)
    return SemanticReasoningContext(
        nodes=nodes,
        edges=edges,
        backend=backend,
        run_id="test",
        config_hash="test",
    )


def test_single_connected_component_is_one_partition():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    assert ctx.node_to_partition["c001"] == ctx.node_to_partition["c002"]


def test_contradiction_creates_two_partitions():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.CONTRADICTS)])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 2
    assert ctx.node_to_partition["c001"] != ctx.node_to_partition["c002"]


def test_every_node_assigned_to_partition():
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [
            ("e1", "c001", "c002", RelationshipType.CONTRADICTS),
            ("e2", "c002", "c003", RelationshipType.SUPPORTS),
        ],
    )
    run_partitioning(ctx)
    for node_id in ctx.nodes:
        assert node_id in ctx.node_to_partition
        assert ctx.node_to_partition[node_id] is not None


def test_isolated_node_gets_own_partition():
    ctx = make_ctx(["c001"], [])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    assert "c001" in ctx.node_to_partition


def test_partition_ids_are_deterministic():
    def build_ctx():
        return make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.CONTRADICTS)])

    ctx1, ctx2 = build_ctx(), build_ctx()
    run_partitioning(ctx1)
    run_partitioning(ctx2)
    assert set(ctx1.partitions.keys()) == set(ctx2.partitions.keys())


def test_partition_does_not_contain_contradicts_internal_edges():
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [
            ("e1", "c001", "c002", RelationshipType.CONTRADICTS),
            ("e2", "c001", "c003", RelationshipType.SUPPORTS),
        ],
    )
    run_partitioning(ctx)
    for partition in ctx.partitions.values():
        for eid in partition.internal_edge_ids:
            edge = ctx.edges.get(eid)
            if edge:
                assert edge.relationship_type != RelationshipType.CONTRADICTS


def test_node_objects_updated_with_partition_id():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    for node in ctx.nodes.values():
        assert node.partition_id is not None


def test_shared_support_target_does_not_merge_contradicting_nodes():
    """
    RECTIFIED (P0-1): The critical failure case for the old algorithm.

    A SUPPORTS X
    C SUPPORTS X
    A CONTRADICTS C

    Old algorithm (edge deletion + connected components):
        Remove CONTRADICTS → A, X, C all connected → SAME partition. WRONG.

    New algorithm (constraint coloring + Union-Find):
        A and C get different colors from contradiction constraint.
        Union-Find only merges same-color nodes.
        A and X merge (same color).
        C stays in its own partition (different color from A).
        X ends up with A, not with C.
        Result: A and C in DIFFERENT partitions. CORRECT.
    """
    ctx = make_ctx(
        ["A", "X", "C"],
        [
            ("e1", "A", "X", RelationshipType.SUPPORTS),
            ("e2", "C", "X", RelationshipType.SUPPORTS),
            ("e3", "A", "C", RelationshipType.CONTRADICTS),
        ],
    )
    run_partitioning(ctx)

    partition_of_a = ctx.node_to_partition["A"]
    partition_of_c = ctx.node_to_partition["C"]
    assert partition_of_a != partition_of_c, (
        "A and C contradict each other and must be in different partitions, "
        "even though they both support X."
    )


def test_stable_partition_label_present():
    """RECTIFIED (P2-5): stable_partition_label must be set on all partitions."""
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    for partition in ctx.partitions.values():
        assert partition.stable_partition_label is not None
        assert isinstance(partition.stable_partition_label, tuple)
        assert len(partition.stable_partition_label) > 0


# ── EQUIVALENT (bidirectional-NLI rewrite) ──────────────────────────────────


def test_equivalent_edge_merges_nodes_into_same_partition():
    """EQUIVALENT claims say the same thing and must be co-located, same
    as SUPPORTS/REFINES."""
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.EQUIVALENT)])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    assert ctx.node_to_partition["c001"] == ctx.node_to_partition["c002"]


def test_equivalent_edge_counted_in_partition_stats():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.EQUIVALENT)])
    run_partitioning(ctx)
    partition = next(iter(ctx.partitions.values()))
    assert partition.equivalent_count == 1
    assert partition.supports_count == 0


def test_contradiction_still_prevents_merge_even_with_equivalent_neighbor():
    """A EQUIVALENT B, A CONTRADICTS C: A and B must be co-located, but C
    must land in a different partition -- EQUIVALENT does not weaken the
    CONTRADICTS invariant."""
    ctx = make_ctx(
        ["a", "b", "c"],
        [
            ("e1", "a", "b", RelationshipType.EQUIVALENT),
            ("e2", "a", "c", RelationshipType.CONTRADICTS),
        ],
    )
    run_partitioning(ctx)
    assert ctx.node_to_partition["a"] == ctx.node_to_partition["b"]
    assert ctx.node_to_partition["a"] != ctx.node_to_partition["c"]


def test_directed_density_formula():
    """RECTIFIED (P1-5): Partition density must use directed formula: edges / (n*(n-1))."""
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [
            ("e1", "c001", "c002", RelationshipType.SUPPORTS),
            ("e2", "c002", "c003", RelationshipType.SUPPORTS),
        ],
    )
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    partition = next(iter(ctx.partitions.values()))
    n = partition.node_count  # 3
    e = partition.edge_count  # 2
    expected_density = e / (n * (n - 1))  # 2 / 6 = 0.333...
    assert abs(partition.density - expected_density) < 1e-6
