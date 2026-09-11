"""
Unit tests for evaluation/partitioning/run_partitioning_comparison.py (P1-5,
external "reality check" review -- partitioning-method comparison).

Uses the EXACT counter-example documented in evolution/partitioning.py's own
module docstring:

    A SUPPORTS X
    C SUPPORTS X
    A CONTRADICTS C

to concretely prove, on a synthetic but well-understood graph, which of the
four compared methods actually uphold the "no two contradicting claims in
the same partition" invariant and which do not -- rather than trusting the
docstring's prose claim alone.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "partitioning"))

from run_partitioning_comparison import (
    compute_metrics,
    constraint_based_signed_coloring,
    contradiction_edge_deletion,
    naive_connected_components,
    weighted_constraint_variant,
)
from smriti.core.models import RelationshipDirection, RelationshipEdge, RelationshipType


def _edge(eid, src, tgt, rel_type, confidence=0.90):
    direction = (
        RelationshipDirection.SYMMETRIC
        if rel_type in (RelationshipType.CONTRADICTS, RelationshipType.EQUIVALENT)
        else RelationshipDirection.A_TO_B
    )
    return RelationshipEdge(
        edge_id=eid,
        source_node_id=src,
        target_node_id=tgt,
        relationship_type=rel_type,
        direction=direction,
        calibrated_confidence=confidence,
        cosine_similarity=0.85,
        nli_confidence=confidence,
        candidate_rank=1,
    )


def make_shared_neighbor_counterexample():
    """A supports X, C supports X, A contradicts C -- the documented
    counter-example that breaks naive connected components AND the
    pre-P0-1-fix contradiction-edge-deletion algorithm."""
    node_ids = {"A", "C", "X"}
    edges = {
        "e1": _edge("e1", "A", "X", RelationshipType.SUPPORTS),
        "e2": _edge("e2", "C", "X", RelationshipType.SUPPORTS),
        "e3": _edge("e3", "A", "C", RelationshipType.CONTRADICTS, confidence=0.95),
    }
    return node_ids, edges


def test_naive_connected_components_violates_the_invariant():
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = naive_connected_components(node_ids, edges)
    assert (
        pm["A"] == pm["C"]
    ), "naive method must merge A and C via the shared neighbor X (that is the bug being demonstrated)"


def test_contradiction_edge_deletion_still_violates_the_invariant():
    """This is the documented pre-P0-1-fix bug: deleting the DIRECT
    A-C edge does nothing about the transitive path through X."""
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = contradiction_edge_deletion(node_ids, edges)
    assert (
        pm["A"] == pm["C"]
    ), "contradiction-edge-deletion must still merge A and C transitively through X"


def test_constraint_based_signed_coloring_upholds_the_invariant():
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = constraint_based_signed_coloring(node_ids, edges)
    assert pm["A"] != pm["C"], "current production algorithm must never merge contradicting A and C"


def test_weighted_constraint_variant_upholds_the_invariant_on_a_simple_cycle():
    """No odd cycle exists in this 3-node example (the contradiction graph
    A-C is just a single edge, trivially 2-colorable) -- the weighted
    variant must behave identically to method 3 here, with zero drops."""
    node_ids, edges = make_shared_neighbor_counterexample()
    pm, dropped = weighted_constraint_variant(node_ids, edges)
    assert pm["A"] != pm["C"]
    assert dropped == []


def make_odd_contradiction_cycle():
    """A contradicts B contradicts C contradicts A -- an odd cycle, not
    2-colorable. The current production algorithm shatters ALL THREE into
    singletons. The weighted variant should instead drop the lowest-
    confidence edge in the cycle and keep the other two constrained."""
    node_ids = {"A", "B", "C"}
    edges = {
        "e1": _edge("e1", "A", "B", RelationshipType.CONTRADICTS, confidence=0.95),
        "e2": _edge("e2", "B", "C", RelationshipType.CONTRADICTS, confidence=0.60),  # weakest
        "e3": _edge("e3", "C", "A", RelationshipType.CONTRADICTS, confidence=0.90),
    }
    return node_ids, edges


def test_current_production_shatters_odd_cycle_into_singletons():
    node_ids, edges = make_odd_contradiction_cycle()
    pm = constraint_based_signed_coloring(node_ids, edges)
    # All three must be in DIFFERENT partitions (singleton-ized).
    assert len({pm["A"], pm["B"], pm["C"]}) == 3


def test_weighted_variant_drops_the_weakest_edge_in_an_odd_cycle():
    node_ids, edges = make_odd_contradiction_cycle()
    pm, dropped = weighted_constraint_variant(node_ids, edges)
    assert len(dropped) == 1
    dropped_pair = frozenset(dropped[0][:2])
    assert dropped_pair == frozenset(
        {"B", "C"}
    ), "must drop the lowest-confidence edge (B-C, conf=0.60), not A-B or C-A"
    assert dropped[0][2] == 0.60


def test_metrics_report_zero_violations_for_current_production():
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = constraint_based_signed_coloring(node_ids, edges)
    metrics = compute_metrics(node_ids, edges, pm)
    assert metrics["contradiction_violations"] == 0


def test_metrics_report_nonzero_violations_for_naive_baseline():
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = naive_connected_components(node_ids, edges)
    metrics = compute_metrics(node_ids, edges, pm)
    assert metrics["contradiction_violations"] == 1


def test_metrics_structural_edges_retained_vs_cut_partition_correctly():
    node_ids, edges = make_shared_neighbor_counterexample()
    pm = constraint_based_signed_coloring(node_ids, edges)
    metrics = compute_metrics(node_ids, edges, pm)
    total = (
        metrics["structural_edges_retained"]["supports"]
        + metrics["structural_edges_cut"]["supports"]
    )
    assert (
        total == 2
    ), "both SUPPORTS edges (A->X, C->X) must be accounted for as either retained or cut"
