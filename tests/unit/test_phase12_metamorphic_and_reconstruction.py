"""
Unit tests for evaluation/scientific/metamorphic.py (RC4) and
evaluation/scientific/explainability_audit.py (RC5) -- P0-13 / P1-8.
"""

from unittest.mock import MagicMock

from smriti.evaluation.scientific.metamorphic import run_reliability_metamorphic_suite
from smriti.evaluation.scientific.explainability_audit import run_reconstruction_audit


def test_metamorphic_suite_runs_all_four_relations():
    result = run_reliability_metamorphic_suite()
    assert result["n_relations"] == 4
    assert 0.0 <= result["pass_rate"] <= 1.0
    relation_names = {r["relation"] for r in result["relations"]}
    assert "MR1_independent_support_increases_reliability" in relation_names
    assert "MR2_contradiction_does_not_increase_reliability_and_raises_conflict_and_uncertainty" in relation_names
    assert "MR3_same_document_duplicate_does_not_raise_source_diversity" in relation_names
    assert "MR4_determinism_same_input_same_output" in relation_names


def test_metamorphic_suite_currently_passes_all_relations():
    """Documents the current state of the reliability model: all four
    metamorphic relations hold as of this fix. If this regresses, it means
    a change to Phase 8's fusion/signal logic broke a basic epistemic
    property (e.g. support should never hurt, contradiction should never help)."""
    result = run_reliability_metamorphic_suite()
    assert result["pass_rate"] == 1.0, result["relations"]


def test_metamorphic_mr1_independent_support_raises_reliability_and_lowers_uncertainty():
    result = run_reliability_metamorphic_suite()
    mr1 = next(r for r in result["relations"] if r["relation"] == "MR1_independent_support_increases_reliability")
    assert mr1["after"]["reliability"] >= mr1["before"]["reliability"]
    assert mr1["after"]["uncertainty"] <= mr1["before"]["uncertainty"]


def test_metamorphic_mr3_source_diversity_is_identical_not_just_non_increasing():
    """The stronger, correct claim: a same-document duplicate contributes
    NOTHING to source diversity (not merely "does not increase it")."""
    result = run_reliability_metamorphic_suite()
    mr3 = next(r for r in result["relations"] if r["relation"] == "MR3_same_document_duplicate_does_not_raise_source_diversity")
    assert mr3["before"]["source_diversity"] == mr3["after"]["source_diversity"]


def test_reconstruction_audit_with_no_accessible_store_returns_not_evaluable_shape():
    api = MagicMock()
    api._store = MagicMock()
    api._store._reliability_records = {}
    result = run_reconstruction_audit(api)
    assert result["exact_match_rate"] == 0.0
    assert result["n_checked"] == 0


def test_reconstruction_audit_reconstructs_a_real_scored_claim():
    """Build one real ReliabilityMetadata-shaped record (the same shape
    memory_store.py produces) and confirm the audit reconstructs its final
    reliability_index from its own component_scores + constraints."""
    from smriti.evaluation.scientific.metamorphic import _make_graph, _make_node, _score

    graph = _make_graph({
        "target": _make_node("target", "doc_target", support_ids=("s1",), degree=1, in_degree=1),
        "s1": _make_node("s1", "doc_other"),
    })
    ri, uncertainty, signal_vector = _score("target", graph)

    # Reconstruct the same component_scores shape memory_store.py builds
    from smriti.scoring.policies import load_policy
    from smriti.scoring.graph_stats import compute_global_stats
    from smriti.scoring.signals import signal_registry
    from smriti.scoring.normalization import assemble_contribution_set
    from smriti.scoring.fusion import compute_reliability

    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    global_stats = compute_global_stats(graph)
    node = graph.nodes["target"]
    raw_signals = [e.extract(node, graph, global_stats, policy) for e in extractors]
    contribution_set, _, sv = assemble_contribution_set(raw_signals, extractors, policy.fusion, "target")
    final_ri, _, component_scores, _ = compute_reliability(contribution_set, policy, sv)

    record = {
        "reliability_index": final_ri,
        "evidence_completeness": sv.evidence_completeness,
        "signal_vector": {
            "evidence_strength": sv.evidence_strength,
            "evidence_independence": sv.evidence_independence,
            "source_diversity": sv.source_diversity,
            "topology_strength": sv.topology_strength,
            "conflict_pressure": sv.conflict_pressure,
            "temporal_stability": sv.temporal_stability,
        },
        "signal_statuses": dict(sv.statuses),
        "component_scores": [
            {"contribution": c.contribution} for c in component_scores
        ],
    }

    api = MagicMock()
    api._store = MagicMock()
    api._store._reliability_records = {"target": record}

    result = run_reconstruction_audit(api)
    assert result["n_checked"] == 1
    assert result["n_mismatched"] == 0
    assert result["exact_match_rate"] == 1.0
