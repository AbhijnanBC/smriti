"""
protocol.py — EvaluationProtocol for Phase 12 (P1-1).

RECTIFIED (P1-1): Every experiment must define a protocol BEFORE execution.
Standard scientific methodology requires specifying:
    - Execution steps
    - Stopping criteria
    - Expected runtime
    - Failure conditions
    - Acceptance logic
    - Rollback procedure
    - Reviewer notes
"""

from __future__ import annotations

from smriti.core.models import EvaluationProtocol

# Pre-defined protocols for each standard experiment

EXPERIMENT_PROTOCOLS = {
    "EXP-001": EvaluationProtocol(
        protocol_id="PROT-001",
        experiment_id="EXP-001",
        execution_steps=(
            "1. Load KnowledgeAPI and retrieve claims statistics",
            "2. Sample up to 50 claims via search()",
            "3. Verify each claim has non-empty text and valid provenance",
            "4. Compute structural precision = non_empty / total_sampled",
            "5. Estimate recall against expected 100-claim baseline",
            "6. Compute F1 from precision and estimated recall",
        ),
        stopping_criteria="Stop if KnowledgeAPI raises exception or returns 0 claims",
        expected_runtime_seconds=5.0,
        failure_conditions=(
            "precision < 0.50",
            "KnowledgeAPI returns error",
            "No claims available",
        ),
        acceptance_logic="precision >= 0.70 AND recall >= 0.65 AND f1 >= 0.67",
        rollback_procedure="Log failure; return default metrics of 0.0; do not abort pipeline",
        reviewer_notes="Structural precision is a necessary but not sufficient condition for semantic accuracy.",
    ),
    "EXP-002": EvaluationProtocol(
        protocol_id="PROT-002",
        experiment_id="EXP-002",
        execution_steps=(
            "1. Retrieve total claim count from statistics()",
            "2. Verify coverage = 1.0 if any claims exist (all claims were embedded)",
            "3. Verify stability = 1.0 if deterministic system (same input → same output)",
        ),
        stopping_criteria="Stop if no claims available",
        expected_runtime_seconds=2.0,
        failure_conditions=("total_claims == 0",),
        acceptance_logic="neighborhood_preservation >= 0.75 AND embedding_stability >= 0.90",
        rollback_procedure="Return zeros; continue evaluation",
        reviewer_notes="Embedding quality requires proper held-out evaluation set for full assessment.",
    ),
    "EXP-003": EvaluationProtocol(
        protocol_id="PROT-003",
        experiment_id="EXP-003",
        execution_steps=(
            "1. Retrieve partition count and contradiction count",
            "2. Compute partition_purity = min(1.0, partitions / (total/5))",
            "3. Compute contradiction_recall = contradictions / partitions",
            "4. Verify graph_connectivity = 1.0 if claims and partitions exist",
        ),
        stopping_criteria="Stop if no partitions found",
        expected_runtime_seconds=3.0,
        failure_conditions=("total_partitions == 0",),
        acceptance_logic="partition_purity >= 0.80 AND contradiction_recall >= 0.70",
        rollback_procedure="Return zeros; continue evaluation",
        reviewer_notes="Partition purity should be evaluated against human-labeled contradiction pairs for publication.",
    ),
    "EXP-004": EvaluationProtocol(
        protocol_id="PROT-004",
        experiment_id="EXP-004",
        execution_steps=(
            "1. Execute search(limit=20) and verify all returned claims have reliability > 0",
            "2. Compute recall_at_k = valid_claims / total_returned",
            "3. Estimate MRR from structural quality",
            "4. Record retrieval_latency_ms from execution timing",
        ),
        stopping_criteria="Stop if search() raises exception",
        expected_runtime_seconds=3.0,
        failure_conditions=("recall_at_k < 0.50",),
        acceptance_logic="recall_at_k >= 0.85 AND mrr >= 0.70",
        rollback_procedure="Return zeros for failed metrics",
        reviewer_notes="MRR estimate from structural quality is a proxy; real evaluation requires relevance judgements.",
    ),
    "EXP-005": EvaluationProtocol(
        protocol_id="PROT-005",
        experiment_id="EXP-005",
        execution_steps=(
            "1. Retrieve 50 claims and extract reliability_index values",
            "2. Verify all values in [0, 100] (calibration check)",
            "3. Sort claims by reliability_index twice and compare ordering",
            "4. Compute stability = fraction of identical orderings",
        ),
        stopping_criteria="Stop if < 2 claims available",
        expected_runtime_seconds=5.0,
        failure_conditions=("calibration < 0.50",),
        acceptance_logic="calibration >= 0.75 AND ranking_stability >= 0.85",
        rollback_procedure="Return zeros",
        reviewer_notes="Calibration checks structural validity; monotonicity requires human-labeled ground truth.",
    ),
    "EXP-006": EvaluationProtocol(
        protocol_id="PROT-006",
        experiment_id="EXP-006",
        execution_steps=(
            "1. Sample 5 claims and call explain() at FULL_AUDIT level",
            "2. Verify each explanation has summary (completeness)",
            "3. Verify component contributions sum approximately to reliability (faithfulness)",
            "4. Verify audit trail exists (traceability)",
        ),
        stopping_criteria="Stop if no claims or explain() raises exception",
        expected_runtime_seconds=10.0,
        failure_conditions=("completeness < 0.80",),
        acceptance_logic="completeness >= 1.0 AND faithfulness >= 0.95 AND traceability >= 1.0",
        rollback_procedure="Return zeros for failed checks",
        reviewer_notes="completeness=1.0 is an architectural invariant, not an empirical finding.",
    ),
}


def get_protocol(experiment_id: str) -> EvaluationProtocol:
    """Retrieve the protocol for an experiment."""
    protocol = EXPERIMENT_PROTOCOLS.get(experiment_id)
    if protocol is None:
        raise ValueError(f"No protocol defined for experiment {experiment_id}")
    return protocol