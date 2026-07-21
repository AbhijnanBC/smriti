"""
scoring/__init__.py — Public API for Phase 8: Reliability Evaluation.

RECTIFIED: Uses signal_registry.ordered_extractors() (never static list).
Passes ContributionSet to fusion (never SignalVector directly to fusion).
Records SignalManifests and ReliabilityDecisionRecord.

RECTIFIED (Phase 8.3): Cross‑validates policy against the active registry
immediately after discovery to enforce a strict 1:1 mapping.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import KnowledgeGraph, ReliabilityMetadata, ScoredKnowledgeGraph, SignalStatus,  RawSignal
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase8Error

from smriti.scoring.policies import load_policy, PolicyProfile
from smriti.scoring.graph_stats import compute_global_stats
from smriti.scoring.signals import signal_registry
from smriti.scoring.normalization import assemble_contribution_set
from smriti.scoring.fusion import compute_reliability
from smriti.scoring.explanation import build_explanation
from smriti.scoring.builder import build_reliability_metadata, build_scored_knowledge_graph
from smriti.scoring.statistics import Phase8StatsCollector

logger = structlog.get_logger(__name__)


def _serialize_scored_graph(scored: ScoredKnowledgeGraph) -> str:
    """Serialize ScoredKnowledgeGraph to JSON for Phase 9."""
    data = {
        "graph_id": scored.graph.graph_id,
        "run_id": scored.run_id,
        "schema_version": scored.schema_version,
        "policy_profile": scored.policy_profile,
        "total_scored": scored.total_scored,
        "avg_reliability": round(scored.avg_reliability, 2),
        "policy_snapshot": scored.policy_snapshot,
        "global_stats": {
            "max_support_count": scored.global_stats.max_support_count,
            "avg_support_count": round(scored.global_stats.avg_support_count, 2),
            "node_count": scored.global_stats.node_count,
            "contradiction_count": scored.global_stats.contradiction_count,
        },
        "reliability": {},
    }

    for claim_id, meta in sorted(scored.reliability.items()):
        data["reliability"][claim_id] = {
            "claim_id": meta.claim_id,
            "reliability_index": meta.reliability_index,
            "uncertainty_score": meta.uncertainty_score,
            "evidence_completeness": meta.evidence_completeness,
            "calibration_label": meta.calibration_label.value,
            "policy_version": meta.policy_version,
            "schema_version": meta.schema_version,
            "signal_vector": {
                "evidence_strength": meta.signal_vector.evidence_strength,
                "evidence_independence": meta.signal_vector.evidence_independence,
                "source_diversity": meta.signal_vector.source_diversity,
                "topology_strength": meta.signal_vector.topology_strength,
                "conflict_pressure": meta.signal_vector.conflict_pressure,
                "temporal_stability": meta.signal_vector.temporal_stability,
            },
            "signal_manifests": [
                {
                    "signal_id": m.signal_id,
                    "extractor_version": m.extractor_version,
                    "raw_value": m.raw_value,
                    "normalized_value": m.normalized_value,
                    "normalization_strategy": m.normalization_strategy,
                    "status": m.status.value,
                    "quality_flags": list(m.quality_flags),
                    "dependency_list": list(m.dependency_list),
                }
                for m in meta.signal_manifests
            ],
            "decision_record": {
                "policy_interactions": list(meta.decision_record.policy_interactions),
                "constraints_activated": list(meta.decision_record.constraints_activated),
                "contribution_order": list(meta.decision_record.contribution_order),
                "raw_reliability": meta.decision_record.raw_reliability,
                "constrained_reliability": meta.decision_record.constrained_reliability,
                "final_reliability": meta.decision_record.final_reliability,
                "dominant_adjustment": meta.decision_record.dominant_adjustment,
            },
            "components": [
                {
                    "signal": c.signal_id,
                    "contribution": round(c.contribution, 3),
                    "direction": c.direction,
                    "explanation": c.explanation,
                }
                for c in meta.component_scores
            ],
            "explanation": {
                "summary": meta.explanation.summary,
                "strengths": list(meta.explanation.strengths),
                "weaknesses": list(meta.explanation.weaknesses),
                "dominant_signal": meta.explanation.dominant_signal,
                "limiting_signal": meta.explanation.limiting_signal,
                "recommendations": list(meta.explanation.recommendations),
            },
        }

    return json.dumps(data, indent=2, ensure_ascii=False)


def score_knowledge_graph(
    graph: KnowledgeGraph,
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    policy_profile: PolicyProfile = PolicyProfile.BALANCED,
) -> ScoredKnowledgeGraph:
    """
    Execute the complete Phase 8 Reliability Evaluation pipeline.

    RECTIFIED:
        - Uses SignalRegistry (not static list)
        - Passes ContributionSet to generic Fusion
        - Records SignalManifests and ReliabilityDecisionRecord per claim
        - Accepts policy_profile parameter for profile selection
        - Enforces strict 1:1 mapping between policy weights and registry (Phase 8.3)

    Pipeline:
        1. Load policy (with profile)
        2. Discover registered signal extractors
        3. Cross‑validate policy against registry
        4. Compute global graph statistics (once)
        5. For each ClaimNode:
            a. Extract signals (each extractor normalizes its own output)
            b. Assemble ContributionSet + SignalManifests
            c. Fuse → RI, Uncertainty, ComponentScores, DecisionRecord
            d. Build Explanation
            e. Build ReliabilityMetadata
        6. Assemble ScoredKnowledgeGraph
        7. Write artifacts + manifest
    """
    logger.info("phase 8 starting", run_id=run_id, nodes=graph.node_count)

    start_time = manifest_manager.start_phase(phase=8)
    stats = Phase8StatsCollector()

    # ── Step 1: Load policy ───────────────────────────────────────────────────
    policy = load_policy(profile=policy_profile)
    stats.set_policy_version(policy.version, policy.profile)

    # ── Step 2: Discover registered extractors (P0-1) ─────────────────────────
    extractors = signal_registry.ordered_extractors()
    stats.set_registered_signals(len(extractors))
    logger.info(
        "signal registry discovered",
        signal_count=len(extractors),
        signals=signal_registry.registered_names,
    )

    # ── Step 2.5: Cross‑validate policy against registry ─────────────────────
    active_ids = {e.signal_id for e in extractors}
    policy.validate(active_registry_ids=active_ids)
    logger.info(
        "policy validated against registry",
        policy_version=policy.version,
        profile=policy.profile,
        registered_signals=len(active_ids),
    )

    # ── Step 3: Global statistics ─────────────────────────────────────────────
    global_stats = compute_global_stats(graph)

    # ── Step 4: Score every node ──────────────────────────────────────────────
    stats.record_signal_start()
    reliability: Dict[str, ReliabilityMetadata] = {}

    with Timer("phase8_scoring"):
        for claim_id, node in sorted(graph.nodes.items()):

            # 4a: Extract signals (each extractor owns normalization)
            raw_signals = []
            for extractor in extractors:
                try:
                    sig = extractor.extract(node, graph, global_stats, policy)
                    raw_signals.append(sig)
                except Exception as e:
                    logger.warning(
                        "signal extraction failed, using default",
                        signal=extractor.signal_id.value,
                        error=str(e),
                    )
                    raw_signals.append(
                        RawSignal(
                            name=extractor.signal_id.value,
                            raw_value=0.0,
                            normalized_value=0.0,
                            status=SignalStatus.UNAVAILABLE,
                            metadata={"error": str(e)},
                        )
                    )

            # 4b: Assemble ContributionSet + SignalManifests + SignalVector
            contribution_set, signal_manifests, signal_vector = assemble_contribution_set(
                raw_signals=raw_signals,
                extractors=extractors,
                fusion_policy=policy.fusion,
                claim_id=claim_id,
            )

            # 4c: Generic fusion (ContributionSet, not SignalVector)
            stats.record_fusion_start()
            ri, unc, component_scores, decision_record = compute_reliability(
                contribution_set=contribution_set,
                policy=policy,
                signal_vector=signal_vector,
            )
            stats.record_fusion_end()

            # 4d: Build explanation
            explanation = build_explanation(ri, component_scores)

            # 4e: Build ReliabilityMetadata (with manifests + decision record)
            meta = build_reliability_metadata(
                node=node,
                reliability_index=ri,
                uncertainty_score=unc,
                signal_vector=signal_vector,
                component_scores=component_scores,
                signal_manifests=signal_manifests,
                decision_record=decision_record,
                explanation=explanation,
                policy=policy,
                run_id=run_id,
                extractors=extractors,
                graph=graph,
            )

            reliability[claim_id] = meta
            stats.record_scored(ri, unc)

    stats.record_signal_end()

    # ── Step 5: Assemble ScoredKnowledgeGraph ─────────────────────────────────
    scored_graph = build_scored_knowledge_graph(
        graph=graph,
        reliability=reliability,
        policy=policy,
        global_stats=global_stats,
        run_id=run_id,
    )

    final_stats = stats.finalize()

    # ── Step 6: Write artifacts ───────────────────────────────────────────────
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase8"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(_serialize_scored_graph(scored_graph), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        claims_scored=scored_graph.total_scored,
        avg_reliability=f"{scored_graph.avg_reliability:.2f}",
    )

    manifest_manager.end_phase(
        phase=8,
        start_time=start_time,
        inputs={"nodes": graph.node_count},
        outputs={
            "claims_scored": scored_graph.total_scored,
            "avg_reliability": round(scored_graph.avg_reliability, 2),
            "high_reliability": final_stats.high_reliability_count,
            "low_reliability": final_stats.low_reliability_count,
            "policy_version": policy.version,
            "policy_profile": policy.profile,
            "registered_signals": final_stats.registered_signal_count,
            "dataset_path": str(dataset_path),
        },
        status="success",
    )

    state_manager.complete_phase(phase=8)

    logger.info(
        "phase 8 complete",
        claims_scored=scored_graph.total_scored,
        avg_reliability=f"{scored_graph.avg_reliability:.2f}",
        high_reliability=final_stats.high_reliability_count,
        runtime_seconds=f"{final_stats.total_runtime_seconds:.2f}",
        registered_signals=final_stats.registered_signal_count,
    )

    return scored_graph