"""
protocol.py — EvaluationProtocol for Phase 12 (FROZEN v2, matches EXP-001..EXP-005).

RECTIFIED (P1-1): Every experiment must define a protocol BEFORE execution.
Standard scientific methodology requires specifying:
    - Execution steps
    - Stopping criteria
    - Expected runtime
    - Failure conditions
    - Acceptance logic
    - Rollback procedure
    - Reviewer notes

FROZEN (post-review rectification): rewritten to describe what
evaluation/scientific/experiment.py ACTUALLY does after the scientific
cleanup — real reference-annotation lookups and a direct graph
re-verification, not the old structural-proxy formulas these protocols
used to document.
"""

from __future__ import annotations

from smriti.core.models import EvaluationProtocol

EXPERIMENT_PROTOCOLS = {
    "EXP-001": EvaluationProtocol(
        protocol_id="PROT-001",
        experiment_id="EXP-001",
        execution_steps=(
            "1. Load evaluation/annotation/results_summary.json (produced by "
            "evaluation/annotation/score.py from two independent LLM-derived "
            "reference annotation passes)",
            "2. Read claim_annotation.extraction_precision_on_agreed_subset "
            "(fraction of the 298 annotator-agreed claims judged structurally valid)",
            "3. If the file or field is missing, return NOT_EVALUABLE — do not "
            "compute a substitute metric",
        ),
        stopping_criteria="N/A — this is a lookup against a pre-computed reference file, not a live pipeline run",
        expected_runtime_seconds=0.1,
        failure_conditions=("precision < 0.70",),
        acceptance_logic="precision >= 0.70",
        rollback_procedure="Return NOT_EVALUABLE if reference data absent; never default to a passing value",
        reviewer_notes="Recall is explicitly NOT_EVALUABLE under this protocol — it would require an annotator "
                       "to enumerate every assertable claim in each source document, which this sampling "
                       "protocol does not do. See paper Limitations.",
    ),
    "EXP-002": EvaluationProtocol(
        protocol_id="PROT-002",
        experiment_id="EXP-002",
        execution_steps=(
            "1. Load evaluation/annotation/results_summary.json",
            "2. Read relationship_annotation.smriti_per_class_prf1 "
            "(SUPPORTS/CONTRADICTS/REFINES/NEUTRAL precision/recall/F1 against "
            "the 269 annotator-agreed relationship pairs)",
            "3. Compute macro_f1 as the unweighted mean of the four per-class F1 scores",
            "4. Also surface contradiction_recall_on_known_pairs (recall on the "
            "deliberately-planted hard-contradiction target pairs)",
        ),
        stopping_criteria="N/A — reference-file lookup",
        expected_runtime_seconds=0.1,
        failure_conditions=("macro_f1 < 0.60",),
        acceptance_logic="macro_f1 >= 0.60",
        rollback_procedure="Return NOT_EVALUABLE if reference data absent",
        reviewer_notes="Known result as of the last reference-annotation run: macro-F1 is low, driven almost "
                       "entirely by CONTRADICTS precision of ~3%. This experiment is expected to FAIL until "
                       "the Phase 6 relatedness-gate + calibration + abstention redesign lands — a failing "
                       "result here is the correct, honest outcome, not a bug in the experiment.",
    ),
    "EXP-003": EvaluationProtocol(
        protocol_id="PROT-003",
        experiment_id="EXP-003",
        execution_steps=(
            "1. Read the live KnowledgeGraph served by Phase 9's KnowledgeAccessService "
            "(api._store._graph) directly — do not trust Phase 7's own success/failure alone",
            "2. For every edge with relationship_type == CONTRADICTS, check whether "
            "its two endpoint nodes share a partition_id",
            "3. contradiction_violation_rate = violating_edges / total_contradiction_edges",
            "4. Separately record singleton_rate and partition_count as descriptive "
            "statistics (NOT part of the pass/fail criterion)",
        ),
        stopping_criteria="Stop if the graph has no accessible nodes/edges",
        expected_runtime_seconds=1.0,
        failure_conditions=("contradiction_violation_rate > 0.0",),
        acceptance_logic="contradiction_violation_rate <= 0.0",
        rollback_procedure="Return NOT_EVALUABLE if the graph object is unreachable",
        reviewer_notes="This claim is about the STRUCTURAL invariant only — it says nothing about whether "
                       "individual CONTRADICTS predictions are semantically correct (that is RC2's concern). "
                       "A high singleton_rate is a real, separately-reported finding about over-fragmentation, "
                       "not a failure of this experiment.",
    ),
    "EXP-004": EvaluationProtocol(
        protocol_id="PROT-004",
        experiment_id="EXP-004",
        execution_steps=(
            "1. Run the metamorphic reliability-perturbation suite "
            "(evaluation/scientific/metamorphic.py): for a set of seed claims, apply "
            "controlled transformations (add independent support, add contradiction, "
            "add duplicate-source claim, reformat only) and record reliability/uncertainty before and after",
            "2. Check each transformation against its expected DIRECTION of change "
            "(e.g. independent support must not decrease reliability)",
            "3. monotonicity_pass_rate = transformations satisfying their expected relation / total transformations",
        ),
        stopping_criteria="Stop if the metamorphic suite module is not implemented yet",
        expected_runtime_seconds=30.0,
        failure_conditions=("monotonicity_pass_rate < 0.90",),
        acceptance_logic="monotonicity_pass_rate >= 0.90",
        rollback_procedure="Return NOT_EVALUABLE if evaluation/scientific/metamorphic.py does not exist yet",
        reviewer_notes="Requires zero external ground truth — the expected relation (direction of change) is "
                       "known from the reliability model's own design, so this is a legitimate no-human-"
                       "annotation evaluation strategy.",
    ),
    "EXP-005": EvaluationProtocol(
        protocol_id="PROT-005",
        experiment_id="EXP-005",
        execution_steps=(
            "1. Run the explainability reconstruction audit "
            "(evaluation/scientific/explainability_audit.py) over every scored claim",
            "2. For each claim, recompute raw_reliability from its recorded "
            "component_scores contributions and compare to the audited raw_reliability",
            "3. Recompute constrained/final reliability by re-applying the recorded "
            "constraints_activated and compare to the audited constrained/final values",
            "4. reconstruction_exact_match_rate = claims matching within numerical "
            "tolerance / total scored claims",
        ),
        stopping_criteria="Stop if the reconstruction module is not implemented yet",
        expected_runtime_seconds=10.0,
        failure_conditions=("reconstruction_exact_match_rate < 1.0",),
        acceptance_logic="reconstruction_exact_match_rate >= 1.0",
        rollback_procedure="Return NOT_EVALUABLE if evaluation/scientific/explainability_audit.py does not exist yet",
        reviewer_notes="This is a self-consistency check on SMRITI's own audit trail (does the math the "
                       "system claims to have done actually match the math it recorded?), not an external "
                       "validity claim about whether the reliability MODEL itself is correct.",
    ),
}


def get_protocol(experiment_id: str) -> EvaluationProtocol:
    """Retrieve the protocol for an experiment."""
    protocol = EXPERIMENT_PROTOCOLS.get(experiment_id)
    if protocol is None:
        raise ValueError(f"No protocol defined for experiment {experiment_id}")
    return protocol
