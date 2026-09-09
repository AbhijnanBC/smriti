"""
experiment.py — Experiment Design + Registry with Lifecycle (FROZEN v2).

FROZEN (post-review rectification): exactly five experiments, EXP-001
through EXP-005, one per canonical research claim (RC1-RC5, see
evaluation/certification/claims.py). Each either measures its claim
against a real, independently-produced reference dataset, or returns
VerificationStatus.NOT_EVALUABLE with an explicit reason — never a
fabricated number standing in for missing evidence. The previous version
of this file computed things like `precision = non_empty_claims /
total_sampled` and called it extraction precision, invented recall from
`min(1.0, total/100)`, and hard-coded retrieval latency; none of that
measured anything real, and all of it has been deleted, not patched.

Lifecycle enforces the pre-registration principle:
    DRAFT -> REGISTERED (acceptance criteria locked)
    -> APPROVED -> EXECUTED -> VALIDATED -> ARCHIVED

Nothing in Phase 12 may execute an experiment that is not REGISTERED or APPROVED.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from smriti.core.models import (
    ExperimentDesign, ExperimentResult, ExperimentLifecycleState,
    VerificationStatus, ScientificDomain, RelationshipType,
)

# Where evaluation/annotation/score.py writes the LLM-derived reference
# annotation results. If this does not exist, RC1/RC2 are NOT_EVALUABLE —
# Phase 12 never regenerates or fabricates this data itself.
_REFERENCE_RESULTS_PATH = Path("evaluation/annotation/results_summary.json")


EXPERIMENT_REGISTRY: List[ExperimentDesign] = [
    ExperimentDesign(
        experiment_id="EXP-001",
        scientific_domain=ScientificDomain.KNOWLEDGE_EXTRACTION,
        hypothesis="Claim extraction achieves >= 0.70 precision against an independent reference annotation",
        independent_variables=("segmentation_strategy", "spacy_model", "assertion_classifier"),
        dependent_variables=("precision",),
        controlled_variables=("dataset", "random_seed", "config"),
        confounding_variables=("writing_style", "document_length", "noise_level"),
        ground_truth_version="llm_reference_annotation_v1",
        acceptance_criteria={"precision": 0.70},
        random_seed=42,
        lifecycle_state=ExperimentLifecycleState.REGISTERED,
    ),
    ExperimentDesign(
        experiment_id="EXP-002",
        scientific_domain=ScientificDomain.RELATIONSHIP_RESOLUTION,
        hypothesis="Relationship classification achieves >= 0.60 macro-F1 against an independent reference annotation",
        independent_variables=("nli_model", "candidate_threshold", "decision_margin"),
        dependent_variables=("macro_f1", "contradiction_precision", "contradiction_recall_on_known_pairs"),
        controlled_variables=("dataset", "random_seed", "nli_model"),
        confounding_variables=("claim_length", "semantic_ambiguity", "cross_domain_pair_rate"),
        ground_truth_version="llm_reference_annotation_v1",
        acceptance_criteria={"macro_f1": 0.60},
        random_seed=42,
        lifecycle_state=ExperimentLifecycleState.REGISTERED,
    ),
    ExperimentDesign(
        experiment_id="EXP-003",
        scientific_domain=ScientificDomain.KNOWLEDGE_GRAPH,
        hypothesis="No CONTRADICTS edge ever connects two nodes assigned to the same partition",
        independent_variables=("contradiction_threshold", "sim_threshold"),
        dependent_variables=("contradiction_violation_rate", "singleton_rate", "partition_count"),
        controlled_variables=("dataset", "random_seed", "nli_model"),
        confounding_variables=("claim_length", "semantic_ambiguity"),
        ground_truth_version="structural_invariant_direct_verification",
        acceptance_criteria={"contradiction_violation_rate": 0.0},
        random_seed=42,
        lifecycle_state=ExperimentLifecycleState.REGISTERED,
    ),
    ExperimentDesign(
        experiment_id="EXP-004",
        scientific_domain=ScientificDomain.RELIABILITY_SCORING,
        hypothesis="Reliability responds monotonically and predictably to controlled evidence perturbations (metamorphic testing)",
        independent_variables=("policy_weights", "signal_configuration"),
        dependent_variables=("monotonicity_pass_rate",),
        controlled_variables=("dataset", "random_seed", "policy_version"),
        confounding_variables=("evidence_overlap",),
        ground_truth_version="metamorphic_relations_v1",
        acceptance_criteria={"monotonicity_pass_rate": 0.90},
        random_seed=42,
        lifecycle_state=ExperimentLifecycleState.REGISTERED,
    ),
    ExperimentDesign(
        experiment_id="EXP-005",
        scientific_domain=ScientificDomain.EXPLAINABILITY,
        hypothesis="Every claim's final reliability score is exactly reconstructible from its recorded signal contributions and constraint adjustments",
        independent_variables=("explainability_level",),
        dependent_variables=("reconstruction_exact_match_rate",),
        controlled_variables=("dataset", "policy_version"),
        confounding_variables=("signal_count",),
        ground_truth_version="self_consistency_direct_verification",
        acceptance_criteria={"reconstruction_exact_match_rate": 1.0},
        random_seed=42,
        lifecycle_state=ExperimentLifecycleState.REGISTERED,
    ),
]


def get_experiment(experiment_id: str) -> Optional[ExperimentDesign]:
    return next((e for e in EXPERIMENT_REGISTRY if e.experiment_id == experiment_id), None)


def _load_reference_results() -> Optional[Dict]:
    """Load the LLM-derived reference annotation scoring results, if present."""
    if not _REFERENCE_RESULTS_PATH.exists():
        return None
    try:
        return json.loads(_REFERENCE_RESULTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def run_experiment(
    experiment: ExperimentDesign,
    knowledge_api,
    run_id: str,
) -> ExperimentResult:
    """Execute a pre-specified experiment. Protocol is retrieved and logged."""
    if experiment.lifecycle_state not in (
        ExperimentLifecycleState.REGISTERED,
        ExperimentLifecycleState.APPROVED,
    ):
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            run_id=run_id,
            metrics={},
            raw_outputs={"reason": f"lifecycle_state={experiment.lifecycle_state.value}"},
            execution_time_seconds=0.0,
            manifest_path=None,
            status=VerificationStatus.SKIPPED,
        )

    t0 = time.monotonic()
    try:
        metrics, raw_outputs, status = _execute_domain(experiment, knowledge_api)
        if status is None:
            status = _evaluate_acceptance(metrics, experiment.acceptance_criteria)
    except Exception as e:
        metrics, raw_outputs = {}, {"error": str(e)}
        status = VerificationStatus.FAILED

    return ExperimentResult(
        experiment_id=experiment.experiment_id,
        run_id=run_id,
        metrics=metrics,
        raw_outputs=raw_outputs,
        execution_time_seconds=time.monotonic() - t0,
        manifest_path=None,
        status=status,
    )


def _execute_domain(experiment: ExperimentDesign, knowledge_api):
    domain = experiment.scientific_domain
    if domain == ScientificDomain.KNOWLEDGE_EXTRACTION:
        return _run_extraction()
    elif domain == ScientificDomain.RELATIONSHIP_RESOLUTION:
        return _run_relationship_resolution()
    elif domain == ScientificDomain.KNOWLEDGE_GRAPH:
        return _run_graph_partitioning(knowledge_api)
    elif domain == ScientificDomain.RELIABILITY_SCORING:
        return _run_reliability_metamorphic(knowledge_api)
    elif domain == ScientificDomain.EXPLAINABILITY:
        return _run_explainability_reconstruction(knowledge_api)
    return {}, {}, VerificationStatus.NOT_EVALUABLE


def _not_evaluable(reason: str):
    return {}, {"reason": reason}, VerificationStatus.NOT_EVALUABLE


def _evaluate_acceptance(metrics: Dict, criteria: Dict) -> VerificationStatus:
    for metric, threshold in criteria.items():
        if metric not in metrics:
            return VerificationStatus.WARNING
        if metrics[metric] < threshold:
            return VerificationStatus.FAILED
    return VerificationStatus.PASSED


# ── EXP-001 (RC1): Claim extraction precision against reference annotation ──

def _run_extraction():
    ref = _load_reference_results()
    if ref is None or "claim_annotation" not in ref:
        return _not_evaluable(
            "No LLM/human reference annotation found at "
            f"{_REFERENCE_RESULTS_PATH}. Run evaluation/annotation/score.py "
            "against a reference-annotated claim sample first; this "
            "experiment does not generate or approximate its own ground truth."
        )
    ca = ref["claim_annotation"]
    precision = ca.get("extraction_precision_on_agreed_subset")
    if precision is None:
        return _not_evaluable("Reference results file exists but has no extraction_precision_on_agreed_subset field.")
    metrics = {"precision": float(precision)}
    raw_outputs = {
        "n_sampled": ca.get("n_sampled"),
        "n_agreed": ca.get("n_agreed"),
        "n_disputed_validity": ca.get("n_disputed_validity"),
        "inter_pass_kappa_validity": ca.get("inter_pass_kappa_validity"),
        "recall": "NOT_EVALUABLE -- measuring recall requires an annotator to "
                  "enumerate every assertable claim in each source document "
                  "independent of what SMRITI extracted; this sample-based "
                  "annotation protocol does not do that (see paper Limitations).",
    }
    return metrics, raw_outputs, None


# ── EXP-002 (RC2): Relationship classification macro-F1 ─────────────────────

def _run_relationship_resolution():
    ref = _load_reference_results()
    if ref is None or "relationship_annotation" not in ref:
        return _not_evaluable(
            "No LLM/human reference annotation found at "
            f"{_REFERENCE_RESULTS_PATH}. Run evaluation/annotation/score.py first."
        )
    ra = ref["relationship_annotation"]
    per_class = ra.get("smriti_per_class_prf1", {})
    if not per_class:
        return _not_evaluable("Reference results file exists but has no smriti_per_class_prf1 field.")
    f1s = [v["f1"] for v in per_class.values() if "f1" in v]
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    metrics = {
        "macro_f1": round(macro_f1, 4),
        "contradiction_precision": per_class.get("CONTRADICTS", {}).get("precision", 0.0),
        "contradiction_recall_on_known_pairs": ra.get("smriti_recall_on_known_hard_contradiction_pairs") or 0.0,
    }
    raw_outputs = {
        "per_class_prf1": per_class,
        "inter_pass_kappa": ra.get("inter_pass_kappa"),
        "n_agreed_excl_unsure": ra.get("n_agreed_excl_unsure"),
        "n_known_hard_contradiction_pairs_in_agreed_gold": ra.get("n_known_hard_contradiction_pairs_in_agreed_gold"),
    }
    return metrics, raw_outputs, None


# ── EXP-003 (RC3): Direct, independent re-verification of the partition invariant ──

def _run_graph_partitioning(api):
    """
    Independently re-walks the knowledge graph and checks, edge by edge,
    that no CONTRADICTS edge connects two nodes in the same partition.

    This is deliberately redundant with Phase 7's own enforcement (which
    raises PartitioningError on violation) -- Phase 12 does not TRUST that
    Phase 7 ran correctly, it re-derives the check from the graph Phase 9
    is actually serving, so a future regression that broke the invariant
    without crashing would still be caught here.
    """
    store = getattr(api, "_store", None)
    graph = getattr(store, "_graph", None) if store else None
    nodes = getattr(graph, "nodes", None) if graph is not None else None
    edges = getattr(graph, "edges", None) if graph is not None else None
    if not isinstance(nodes, dict) or not isinstance(edges, dict):
        return _not_evaluable(
            "KnowledgeAccessService has no accessible real graph to verify "
            "(nodes/edges are not the expected dict structures — e.g. this "
            "API instance is a test double rather than a live Phase 9 service)."
        )

    violations = []
    for edge_id, edge in edges.items():
        if edge.relationship_type != RelationshipType.CONTRADICTS:
            continue
        src = nodes.get(edge.source_node_id)
        tgt = nodes.get(edge.target_node_id)
        if src is None or tgt is None:
            continue
        src_pid = src.annotations.partition_id if src.annotations else None
        tgt_pid = tgt.annotations.partition_id if tgt.annotations else None
        if src_pid is not None and src_pid == tgt_pid:
            violations.append(edge_id)

    n_contradiction_edges = sum(1 for e in edges.values() if e.relationship_type == RelationshipType.CONTRADICTS)
    violation_rate = len(violations) / max(1, n_contradiction_edges)

    partition_sizes: Dict[str, int] = {}
    for n in nodes.values():
        pid = n.annotations.partition_id if n.annotations else None
        if pid:
            partition_sizes[pid] = partition_sizes.get(pid, 0) + 1
    n_singleton = sum(1 for size in partition_sizes.values() if size == 1)
    singleton_rate = n_singleton / max(1, len(partition_sizes))

    metrics = {
        "contradiction_violation_rate": round(violation_rate, 6),
        "singleton_rate": round(singleton_rate, 4),
        "partition_count": float(len(partition_sizes)),
    }
    raw_outputs = {
        "n_contradiction_edges_checked": n_contradiction_edges,
        "n_violations": len(violations),
        "violating_edge_ids": violations[:10],
        "n_nodes": len(nodes),
        "n_partitions": len(partition_sizes),
        "n_singleton_partitions": n_singleton,
        "note": "singleton_rate and partition_count are DESCRIPTIVE statistics "
                "about graph fragmentation, not pass/fail criteria on their own "
                "-- high fragmentation is a real finding reported in the paper's "
                "error analysis, not a violation of this claim.",
    }
    return metrics, raw_outputs, None


# ── EXP-004 (RC4): Reliability metamorphic tests ─────────────────────────────

def _run_reliability_metamorphic(api):
    try:
        from smriti.evaluation.scientific.metamorphic import run_reliability_metamorphic_suite
    except ImportError:
        return _not_evaluable(
            "Metamorphic reliability perturbation suite not yet implemented "
            "(evaluation/scientific/metamorphic.py). See paper roadmap."
        )
    result = run_reliability_metamorphic_suite(api)
    metrics = {"monotonicity_pass_rate": result["pass_rate"]}
    return metrics, result, None


# ── EXP-005 (RC5): Explainability reconstruction test ────────────────────────

def _run_explainability_reconstruction(api):
    try:
        from smriti.evaluation.scientific.explainability_audit import run_reconstruction_audit
    except ImportError:
        return _not_evaluable(
            "Explainability reconstruction audit not yet implemented "
            "(evaluation/scientific/explainability_audit.py)."
        )
    result = run_reconstruction_audit(api)
    metrics = {"reconstruction_exact_match_rate": result["exact_match_rate"]}
    return metrics, result, None
