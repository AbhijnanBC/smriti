"""
metamorphic.py — RC4 metamorphic reliability-perturbation suite (P1-8).

Metamorphic testing needs no external ground truth: instead of asking
"is this exact number correct", it asks "does the score change in the
DIRECTION the model's own design requires when we apply a controlled
transformation". This is exactly the strategy the review recommended as
the strongest available evidence given no human-annotation budget.

Each test scores a small synthetic claim graph through the REAL Phase 8
production pipeline (signal_registry's actual extractors, the actual
assemble_contribution_set + compute_reliability functions — nothing here
re-implements fusion logic) before and after one controlled perturbation,
then checks the expected relation between the two reliability/uncertainty
outcomes.

Relations tested:
    MR1  Add an independent supporting claim (different document)
         -> reliability must not decrease.
    MR2  Add a CONTRADICTS edge to a previously-uncontested claim
         -> reliability must not increase, conflict pressure must increase.
    MR3  Add a supporting claim from the SAME document as an existing
         supporter (not a new independent source)
         -> source_diversity signal must not increase.
    MR4  Re-score the identical graph twice
         -> result must be byte-identical (determinism).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from smriti.core.models import (
    ClaimNode, KnowledgeGraph, GraphStatistics, ValidationReport,
    NodeAnnotations, SemanticRole, TopologyMetrics, SupportAggregate,
    RelationshipEdge, RelationshipType, RelationshipDirection,
)
from smriti.scoring.policies import load_policy
from smriti.scoring.graph_stats import compute_global_stats
from smriti.scoring.signals import signal_registry
from smriti.scoring.normalization import assemble_contribution_set
from smriti.scoring.fusion import compute_reliability


def _make_node(claim_id: str, document_id: str, support_ids: Tuple[str, ...] = (),
                degree: int = 0, in_degree: int = 0) -> ClaimNode:
    support = None
    if support_ids:
        support = SupportAggregate(
            support_count=len(support_ids), weighted_confidence=0.85,
            supporting_claim_ids=support_ids,
            evidence_summary=f"{len(support_ids)} supporters",
        )
    topo = TopologyMetrics(
        degree=degree, in_degree=in_degree, out_degree=max(0, degree - in_degree),
        is_bridge=False, is_hub=False, partition_id="p0", centrality=0.3,
    )
    annotations = NodeAnnotations(
        semantic_role=SemanticRole.UNCLASSIFIED, topology=topo,
        support_aggregate=support, temporal_metadata=None, partition_id="p0",
    )
    return ClaimNode(
        node_id=claim_id, claim_id=claim_id, claim_text=f"Claim {claim_id}.",
        context="", source_path=Path("synthetic.md"), document_id=document_id,
        annotations=annotations,
    )


def _make_graph(nodes: Dict[str, ClaimNode], edges: Dict[str, RelationshipEdge] = None) -> KnowledgeGraph:
    edges = edges or {}
    stats = GraphStatistics(
        node_count=len(nodes), edge_count=len(edges), partition_count=1,
        contradiction_count=sum(1 for e in edges.values() if e.relationship_type == RelationshipType.CONTRADICTS),
        supports_count=sum(1 for e in edges.values() if e.relationship_type == RelationshipType.SUPPORTS),
        refines_count=0, isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
        evolution_chains=0, unresolved_conflicts=0,
        construction_time_seconds=0.0, enrichment_time_seconds=0.0,
    )
    vr = ValidationReport(
        is_valid=True, node_violations=(), edge_violations=(),
        graph_violations=(), semantic_warnings=(), validation_time_seconds=0.0,
    )
    return KnowledgeGraph(
        graph_id="metamorphic", nodes=nodes, edges=edges, partitions={},
        statistics=stats, validation_report=vr, run_id="metamorphic", config_hash="metamorphic",
    )


def _make_edge(edge_id, source, target, rel_type, confidence=0.9) -> RelationshipEdge:
    return RelationshipEdge(
        edge_id=edge_id, source_node_id=source, target_node_id=target,
        relationship_type=rel_type, direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=confidence, cosine_similarity=0.85,
        nli_confidence=confidence, candidate_rank=1,
    )


def _score(claim_id: str, graph: KnowledgeGraph):
    """Score one node through the real Phase 8 pipeline (no artifacts written)."""
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    global_stats = compute_global_stats(graph)
    node = graph.nodes[claim_id]

    raw_signals = [extractor.extract(node, graph, global_stats, policy) for extractor in extractors]
    contribution_set, _, signal_vector = assemble_contribution_set(raw_signals, extractors, policy.fusion, claim_id)
    ri, uncertainty, _, _ = compute_reliability(contribution_set, policy, signal_vector)
    return ri, uncertainty, signal_vector


def run_reliability_metamorphic_suite(api=None) -> Dict:
    """Run all metamorphic relations. `api` is accepted for interface
    consistency with the other EXP-* runners but unused — every scenario
    here is a self-contained synthetic construction, not a read of the
    live pipeline's graph."""
    results: List[Dict] = []

    # ── MR1: independent support increases (or does not decrease) reliability ──
    base_nodes = {
        "target": _make_node("target", "doc_target", support_ids=(), degree=0, in_degree=0),
    }
    base_graph = _make_graph(base_nodes)
    ri_base, unc_base, _ = _score("target", base_graph)

    perturbed_nodes = {
        "target": _make_node("target", "doc_target", support_ids=("supporter_1",), degree=1, in_degree=1),
        "supporter_1": _make_node("supporter_1", "doc_other_1"),
    }
    perturbed_graph = _make_graph(perturbed_nodes)
    ri_mr1, unc_mr1, _ = _score("target", perturbed_graph)
    results.append({
        "relation": "MR1_independent_support_increases_reliability",
        "passed": ri_mr1 >= ri_base,
        "before": {"reliability": round(ri_base, 3), "uncertainty": round(unc_base, 3)},
        "after": {"reliability": round(ri_mr1, 3), "uncertainty": round(unc_mr1, 3)},
    })

    # ── MR2: a contradiction must not increase reliability, must raise conflict ──
    contested_nodes = {
        "target": _make_node("target", "doc_target", support_ids=("supporter_1",), degree=2, in_degree=1),
        "supporter_1": _make_node("supporter_1", "doc_other_1"),
        "opponent_1": _make_node("opponent_1", "doc_other_2"),
    }
    contested_edges = {
        "e1": _make_edge("e1", "target", "opponent_1", RelationshipType.CONTRADICTS, confidence=0.9),
    }
    contested_graph = _make_graph(contested_nodes, contested_edges)
    ri_mr2, unc_mr2, sv_mr2 = _score("target", contested_graph)
    results.append({
        "relation": "MR2_contradiction_does_not_increase_reliability_and_raises_conflict_and_uncertainty",
        "passed": (ri_mr2 <= ri_mr1) and (sv_mr2.conflict_pressure > 0.0) and (unc_mr2 > unc_mr1),
        "before": {"reliability": round(ri_mr1, 3), "conflict_pressure": 0.0, "uncertainty": round(unc_mr1, 3)},
        "after": {"reliability": round(ri_mr2, 3), "conflict_pressure": round(sv_mr2.conflict_pressure, 3), "uncertainty": round(unc_mr2, 3)},
    })

    # ── MR3: a same-document duplicate supporter must not raise source diversity ──
    # compute_global_stats derives max_source_diversity from the MAX
    # support_count across all nodes in the graph -- so a bare comparison
    # between a 1-supporter and a 2-supporter scenario would normalize
    # "target" against two different denominators (1 vs 2), confounding the
    # comparison with graph-level normalization rather than isolating the
    # one intended perturbation. Both scenarios include an identical filler
    # node with a fixed, higher support_count (5 dummy supporter ids -- they
    # need not resolve to real nodes; only their COUNT feeds
    # max_source_diversity) so both graphs share the same normalization
    # baseline and "target"'s own source_diversity is genuinely comparable.
    _filler_supporters = tuple(f"filler_supporter_{i}" for i in range(5))

    single_source_nodes = {
        "target": _make_node("target", "doc_target", support_ids=("supporter_1",), degree=1, in_degree=1),
        "supporter_1": _make_node("supporter_1", "doc_other_1"),
        "filler": _make_node("filler", "doc_filler", support_ids=_filler_supporters),
    }
    single_source_graph = _make_graph(single_source_nodes)
    _, _, sv_single = _score("target", single_source_graph)

    duplicate_source_nodes = {
        "target": _make_node("target", "doc_target", support_ids=("supporter_1", "supporter_2"), degree=2, in_degree=2),
        "supporter_1": _make_node("supporter_1", "doc_other_1"),
        "supporter_2": _make_node("supporter_2", "doc_other_1"),  # SAME document as supporter_1
        "filler": _make_node("filler", "doc_filler", support_ids=_filler_supporters),
    }
    duplicate_source_graph = _make_graph(duplicate_source_nodes)
    _, _, sv_dup = _score("target", duplicate_source_graph)
    results.append({
        "relation": "MR3_same_document_duplicate_does_not_raise_source_diversity",
        "passed": sv_dup.source_diversity <= sv_single.source_diversity + 1e-6,
        "before": {"source_diversity": round(sv_single.source_diversity, 3)},
        "after": {"source_diversity": round(sv_dup.source_diversity, 3)},
    })

    # ── MR4: determinism — identical input scored twice gives identical output ──
    ri_a, unc_a, _ = _score("target", perturbed_graph)
    ri_b, unc_b, _ = _score("target", perturbed_graph)
    results.append({
        "relation": "MR4_determinism_same_input_same_output",
        "passed": (ri_a == ri_b) and (unc_a == unc_b),
        "before": {"reliability": round(ri_a, 6)},
        "after": {"reliability": round(ri_b, 6)},
    })

    n_passed = sum(1 for r in results if r["passed"])
    return {
        "pass_rate": round(n_passed / len(results), 4) if results else 0.0,
        "n_relations": len(results),
        "n_passed": n_passed,
        "relations": results,
    }
