"""
Unit tests for aggregation.py provenance-root deduplication fix (P0-2).

Verifies that support aggregation counts unique supporting claim IDs,
not unique traversal paths. In a DAG like:

    A → B → D
    A → C → D

A supports D through two paths. Old code: A counted twice.
New code: A counted exactly once (unique provenance root).
"""

from pathlib import Path

from smriti.core.models import (
    ClaimNode,
    RelationshipDirection,
    RelationshipEdge,
    RelationshipType,
)
from smriti.evolution.aggregation import run_evidence_aggregation
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning


def make_supports_edge(eid, src, tgt, confidence=0.88):
    return RelationshipEdge(
        edge_id=eid,
        source_node_id=src,
        target_node_id=tgt,
        relationship_type=RelationshipType.SUPPORTS,
        direction=RelationshipDirection.A_TO_B,
        calibrated_confidence=confidence,
        cosine_similarity=0.85,
        nli_confidence=confidence,
        candidate_rank=1,
    )


def make_ctx_with_edges(node_ids, edge_specs):
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
    for eid, src, tgt, conf in edge_specs:
        edge = make_supports_edge(eid, src, tgt, conf)
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", conf)
    return SemanticReasoningContext(
        nodes=nodes,
        edges=edges,
        backend=backend,
        run_id="test",
        config_hash="test",
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


# ── EQUIVALENT is symmetric evidence (bidirectional-NLI rewrite) ───────────


def make_equivalent_edge(eid, src, tgt, confidence=0.92):
    return RelationshipEdge(
        edge_id=eid,
        source_node_id=src,
        target_node_id=tgt,
        relationship_type=RelationshipType.EQUIVALENT,
        direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=confidence,
        cosine_similarity=0.90,
        nli_confidence=confidence,
        candidate_rank=1,
    )


def make_ctx_with_equivalent(node_ids, eid, src, tgt, confidence=0.92):
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
    edge = make_equivalent_edge(eid, src, tgt, confidence)
    backend.add_edge(src, tgt, eid, "equivalent", confidence)
    backend.add_edge(tgt, src, f"{eid}_rev", "equivalent", confidence)
    return SemanticReasoningContext(
        nodes={**nodes},
        edges={eid: edge},
        backend=backend,
        run_id="test",
        config_hash="test",
    )


def test_equivalent_edge_is_mutual_support_not_one_directional():
    """EQUIVALENT is symmetric: A and B must EACH see the other as
    supporting evidence, unlike SUPPORTS (where only the target gets
    credited). The stored edge's source/target are fixed by claim_id_a/
    claim_id_b's lexicographic order, not by any real direction."""
    ctx = make_ctx_with_equivalent(["A", "B"], "e1", "A", "B")
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_a = ctx.nodes["A"].support_aggregate
    agg_b = ctx.nodes["B"].support_aggregate
    assert agg_a.support_count == 1
    assert "B" in agg_a.supporting_claim_ids
    assert agg_b.support_count == 1
    assert "A" in agg_b.supporting_claim_ids


def test_equivalent_support_does_not_double_count_via_mirrored_edge():
    """The mirrored (reverse) edge used to give the source node credit
    must not cause a node to see itself, or count the same partner twice."""
    ctx = make_ctx_with_equivalent(["A", "B"], "e1", "A", "B")
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_a = ctx.nodes["A"].support_aggregate
    assert agg_a.support_count == 1
    assert list(agg_a.supporting_claim_ids) == ["B"]


def make_ctx_mixed_equivalent_and_independent():
    """D is supported by A, B, and C via SUPPORTS; A and B are additionally
    EQUIVALENT (paraphrases of each other). D's raw supporting_claim_ids
    should still list all three (A, B, C), but independent_evidence_group_ids
    should collapse A and B into one representative -- they are the same
    restated fact, not two independent corroborations."""
    backend = NetworkXBackend()
    node_ids = ["A", "B", "C", "D"]
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
    for eid, src, tgt, conf in [
        ("e1", "A", "D", 0.90),
        ("e2", "B", "D", 0.90),
        ("e3", "C", "D", 0.90),
    ]:
        edge = make_supports_edge(eid, src, tgt, conf)
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", conf)
    equiv_edge = make_equivalent_edge("e4", "A", "B", 0.92)
    edges["e4"] = equiv_edge
    backend.add_edge("A", "B", "e4", "equivalent", 0.92)
    backend.add_edge("B", "A", "e4_rev", "equivalent", 0.92)
    return SemanticReasoningContext(
        nodes=nodes,
        edges=edges,
        backend=backend,
        run_id="test",
        config_hash="test",
    )


def test_equivalent_pair_collapses_to_one_independent_evidence_group():
    """RECTIFIED (provenance/reliability redesign): D has 3 raw supporters
    (A, B, C), but A and B are EQUIVALENT paraphrases of each other, so
    they must collapse into ONE independent evidence group. D's
    independent_evidence_group_count must be 2 (the {A,B} group plus C),
    not 3 -- supporting_claim_ids itself is unaffected (still all 3)."""
    ctx = make_ctx_mixed_equivalent_and_independent()
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_d = ctx.nodes["D"].support_aggregate
    assert agg_d.support_count == 3
    assert set(agg_d.supporting_claim_ids) == {"A", "B", "C"}
    assert agg_d.independent_evidence_group_count == 2
    # The {A, B} equivalence class is represented by its lexicographically
    # smallest member ("A"); C is its own singleton group.
    assert set(agg_d.independent_evidence_group_ids) == {"A", "C"}


# ── P1-2: hop-distance discounting (external "reality check" review) ──


def test_direct_derived_and_multi_hop_evidence_are_classified_by_shortest_hop():
    """A -> D directly (hop 1). E -> A -> D (E is hop 2, "one-hop derived").
    F -> E -> A -> D (F is hop 3, "multi-hop"). D's evidence groups must
    classify A as direct, E as derived, F as multi-hop."""
    ctx = make_ctx_with_edges(
        ["A", "D", "E", "F"],
        [
            ("e1", "A", "D", 0.90),
            ("e2", "E", "A", 0.90),
            ("e3", "F", "E", 0.90),
        ],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_d = ctx.nodes["D"].support_aggregate
    assert set(agg_d.supporting_claim_ids) == {"A", "E", "F"}
    assert agg_d.direct_evidence_group_ids == ("A",)
    assert agg_d.derived_evidence_group_ids == ("E",)
    assert agg_d.multi_hop_evidence_group_ids == ("F",)


def test_shortest_path_wins_when_a_claim_is_reachable_both_directly_and_transitively():
    """A supports D directly (hop 1) AND A also supports B which supports D
    (hop 2 via that path). A must be classified DIRECT (shortest path),
    not derived, even though a longer path to it also exists."""
    ctx = make_ctx_with_edges(
        ["A", "B", "D"],
        [
            ("e1", "A", "D", 0.90),  # direct: A -> D
            ("e2", "A", "B", 0.90),  # A -> B
            ("e3", "B", "D", 0.90),  # B -> D (a second, longer path back to A via B)
        ],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_d = ctx.nodes["D"].support_aggregate
    assert "A" in agg_d.direct_evidence_group_ids
    assert "A" not in agg_d.derived_evidence_group_ids


def test_discounted_evidence_strength_is_less_than_raw_support_count_when_evidence_is_derived():
    """With one direct and one multi-hop supporter, discounted_evidence_strength
    (default weights 1.0 direct / 0.3 multi-hop) must be strictly less
    than the raw support_count of 2 -- discounting is actually applied,
    not a no-op that just relabels the same number."""
    ctx = make_ctx_with_edges(
        ["A", "D", "E", "F"],
        [
            ("e1", "A", "D", 0.90),
            ("e2", "E", "A", 0.90),
            ("e3", "F", "E", 0.90),
        ],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_d = ctx.nodes["D"].support_aggregate
    assert agg_d.support_count == 3
    assert agg_d.discounted_evidence_strength is not None
    assert agg_d.discounted_evidence_strength < agg_d.support_count
    # Default weights: 1.0 (A, direct) + 0.6 (E, derived) + 0.3 (F, multi-hop) = 1.9
    assert abs(agg_d.discounted_evidence_strength - 1.9) < 1e-6
