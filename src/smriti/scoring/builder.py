"""
builder.py — ScoredKnowledgeGraph assembly for Phase 8.

RECTIFIED: Now populates ReliabilityMetadata with SignalManifests and
ReliabilityDecisionRecord. Registry order captured in audit trail.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List
import structlog

from smriti.core.models import (
    KnowledgeGraph, ClaimNode, SignalVector, ComponentScore,
    SignalManifest, ReliabilityDecisionRecord, ReliabilityExplanation,
    ReliabilityAudit, ReliabilityMetadata, ScoredKnowledgeGraph,
    ScoringGlobalStats, CalibrationLabel, ContributionSet,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor

logger = structlog.get_logger(__name__)

PHASE8_SCHEMA_VERSION = "8.0"


def compute_graph_fingerprint(graph: KnowledgeGraph) -> str:
    """
    Create a deterministic SHA256 fingerprint of the graph's topology.

    This fingerprint captures the set of node IDs, edge IDs, and schema version.
    It can be used to detect changes in the graph structure between runs.
    """
    node_keys = "|".join(sorted(graph.nodes.keys()))
    edge_keys = "|".join(sorted(graph.edges.keys()))
    material = f"{node_keys}||{edge_keys}||{graph.schema_version}"
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def apply_calibration_label(ri: float, policy: ReliabilityPolicy) -> CalibrationLabel:
    """Map Reliability Index to CalibrationLabel using policy thresholds."""
    cp = policy.calibration
    if ri >= cp.very_high_threshold:
        return CalibrationLabel.VERY_HIGH
    elif ri >= cp.high_threshold:
        return CalibrationLabel.HIGH
    elif ri >= cp.moderate_threshold:
        return CalibrationLabel.MODERATE
    elif ri >= cp.low_threshold:
        return CalibrationLabel.LOW
    else:
        return CalibrationLabel.VERY_LOW


def build_reliability_metadata(
    node: ClaimNode,
    reliability_index: float,
    uncertainty_score: float,
    signal_vector: SignalVector,
    component_scores: List[ComponentScore],
    signal_manifests: List[SignalManifest],          # NEW (P0-4)
    decision_record: ReliabilityDecisionRecord,       # NEW (P0-5)
    explanation: ReliabilityExplanation,
    policy: ReliabilityPolicy,
    run_id: str,
    extractors: List[BaseSignalExtractor],
    graph: KnowledgeGraph,                            # ADDED (Phase 8.4)
) -> ReliabilityMetadata:
    """
    Construct immutable ReliabilityMetadata for one ClaimNode.

    RECTIFIED (Phase 8.4): Accepts `graph` to compute graph fingerprint
    and use graph.schema_version in audit trail.
    """
    calibration_label = apply_calibration_label(reliability_index, policy)

    registry_order = tuple(e.signal_id for e in extractors)

    audit = ReliabilityAudit(
        policy_version=policy.version,
        policy_profile=policy.profile,
        graph_schema_version=graph.schema_version,          # NOW from graph
        graph_fingerprint=compute_graph_fingerprint(graph),  # NEW field (Phase 8.4)
        fusion_algorithm="weighted_linear_v2",
        normalization_version="1.1",
        computed_at_run_id=run_id,
        signal_extractor_versions={
            e.signal_id: e.version for e in extractors
        },
        registry_order=registry_order,
    )

    return ReliabilityMetadata(
        claim_id=node.claim_id,
        reliability_index=round(reliability_index, 2),
        uncertainty_score=round(uncertainty_score, 2),
        evidence_completeness=round(signal_vector.evidence_completeness, 4),
        signal_vector=signal_vector,
        signal_manifests=tuple(signal_manifests),
        component_scores=tuple(component_scores),
        decision_record=decision_record,
        explanation=explanation,
        calibration_label=calibration_label,
        audit=audit,
        policy_version=policy.version,
        schema_version=PHASE8_SCHEMA_VERSION,
    )


def build_scored_knowledge_graph(
    graph: KnowledgeGraph,
    reliability: Dict[str, ReliabilityMetadata],
    policy: ReliabilityPolicy,
    global_stats: ScoringGlobalStats,
    run_id: str,
) -> ScoredKnowledgeGraph:
    """Assemble the final ScoredKnowledgeGraph."""
    return ScoredKnowledgeGraph(
        graph=graph,
        reliability=reliability,
        policy_snapshot=policy.to_dict(),
        policy_profile=policy.profile,
        global_stats=global_stats,
        run_id=run_id,
        schema_version=PHASE8_SCHEMA_VERSION,
    )