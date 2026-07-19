"""
evolution/__init__.py — Public API for Phase 7: Knowledge Graph Construction.

External callers import ONLY from here:
    from smriti.evolution import build_knowledge_graph, KnowledgeGraph

RECTIFIED: Passes hub_degree_multiplier and AnnotationPolicy from config
to topology and annotation stages respectively.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import Claim, KnowledgeGraph, RelationshipSet, TemporalStatus
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase7Error, GraphConstructionError

from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.construction import run_construction
from smriti.evolution.validation import validate_graph_structure
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.partitioning import run_partitioning
from smriti.evolution.topology import run_topology_analysis
from smriti.evolution.annotation import run_semantic_annotation, AnnotationPolicy
from smriti.evolution.aggregation import run_evidence_aggregation
from smriti.evolution.temporal import run_temporal_resolution
from smriti.evolution.builder import build_knowledge_graph as _assemble_graph
from smriti.evolution.statistics import Phase7StatsCollector

logger = structlog.get_logger(__name__)

PHASE7_VERSION = "1.0"


def _compute_config_hash(config: dict) -> str:
    relevant = {
        "include_neutral": config.get("knowledge_graph", {}).get("include_neutral", False),
        "min_reliable_delta_days": config.get("knowledge_graph", {}).get("min_reliable_delta_days", 1.0),
        "hub_degree_multiplier": config.get("knowledge_graph", {}).get("hub_degree_multiplier", 2.0),
        "annotation": config.get("knowledge_graph", {}).get("annotation", {}),
    }
    material = json.dumps(relevant, sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def _serialize_knowledge_graph(graph: KnowledgeGraph) -> str:
    """Serialize KnowledgeGraph to JSON for Phase 8."""
    data = {
        "graph_id": graph.graph_id,
        "run_id": graph.run_id,
        "schema_version": graph.schema_version,
        "config_hash": graph.config_hash,
        "statistics": {
            "node_count": graph.statistics.node_count,
            "edge_count": graph.statistics.edge_count,
            "partition_count": graph.statistics.partition_count,
            "contradiction_count": graph.statistics.contradiction_count,
            "supports_count": graph.statistics.supports_count,
            "refines_count": graph.statistics.refines_count,
            "bridge_nodes": graph.statistics.bridge_nodes,
            "hub_nodes": graph.statistics.hub_nodes,
            "evolution_chains": graph.statistics.evolution_chains,
            "unresolved_conflicts": graph.statistics.unresolved_conflicts,
        },
        "validation": {
            "is_valid": graph.validation_report.is_valid,
            "total_violations": graph.validation_report.total_violations,
            "semantic_warnings": len(graph.validation_report.semantic_warnings),
        },
        "nodes": {},
        "edges": {},
        "partitions": {},
    }

    for claim_id, node in sorted(graph.nodes.items()):
        node_data = {
            "claim_id": node.claim_id,
            "claim_text": node.claim_text,
            "context": node.context,
            "source_path": str(node.source_path),
            "document_id": node.document_id,
            "partition_id": node.partition_id,
            "semantic_role": node.semantic_role.value,
            "schema_version": node.schema_version,
        }
        if node.topology:
            node_data["topology"] = {
                "degree": node.topology.degree,
                "in_degree": node.topology.in_degree,
                "out_degree": node.topology.out_degree,
                "centrality": node.topology.centrality,
                "is_bridge": node.topology.is_bridge,
                "is_hub": node.topology.is_hub,
            }
        if node.support_aggregate:
            node_data["support"] = {
                "count": node.support_aggregate.support_count,
                "weighted_confidence": node.support_aggregate.weighted_confidence,
                "supporting_claims": list(node.support_aggregate.supporting_claim_ids),
            }
        if node.temporal_metadata:
            node_data["temporal"] = {
                "status": node.temporal_metadata.status.value,
                "earlier_claim_id": node.temporal_metadata.earlier_claim_id,
                "later_claim_id": node.temporal_metadata.later_claim_id,
                "time_delta_days": node.temporal_metadata.time_delta_days,
                "temporal_confidence": node.temporal_metadata.temporal_confidence,
            }
        data["nodes"][claim_id] = node_data

    for edge_id, edge in sorted(graph.edges.items()):
        data["edges"][edge_id] = {
            "source": edge.source_node_id,
            "target": edge.target_node_id,
            "relationship_type": edge.relationship_type.value,
            "direction": edge.direction.value,
            "calibrated_confidence": edge.calibrated_confidence,
            "cosine_similarity": edge.cosine_similarity,
            "candidate_rank": edge.candidate_rank,
        }

    for partition_id, partition in sorted(graph.partitions.items()):
        data["partitions"][partition_id] = {
            "node_ids": sorted(partition.node_ids),
            "stable_partition_label": partition.stable_partition_label,   # <-- fixed
            "node_count": partition.node_count,
            "edge_count": partition.edge_count,
            "supports_count": partition.supports_count,
            "refines_count": partition.refines_count,
            "density": partition.density,
            "longest_support_chain": partition.longest_support_chain,
        }

    return json.dumps(data, indent=2, ensure_ascii=False)


def build_knowledge_graph(
    relationship_set: RelationshipSet,
    claims_map: Dict[str, Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> KnowledgeGraph:
    """
    Execute the complete Phase 7 Knowledge Graph Construction pipeline.

    Sub-Pipeline A (Construction):
        1. Ingestion + Filtering
        2. Node Registry
        3. Edge Registry
        4. Backend Population
        5. Structural + Semantic Validation

    Sub-Pipeline B (Semantic Enrichment):
        1. Constraint-Based Partitioning (signed-graph coloring + Union-Find)
        2. Topology Analysis (true articulation-point bridge detection)
        3. Semantic Annotation (config-driven AnnotationPolicy)
        4. Evidence Aggregation (unique provenance roots)
        5. Temporal Resolution (Claim.timestamp, never filesystem)

    Returns:
        Immutable KnowledgeGraph (Phase 8's canonical input).
    """
    config = get_config()
    kg_cfg = config.get("knowledge_graph", {})
    include_neutral = kg_cfg.get("include_neutral", False)
    hub_degree_multiplier = kg_cfg.get("hub_degree_multiplier", 2.0)
    config_hash = _compute_config_hash(config)

    logger.info(
        "phase 7 starting",
        run_id=run_id,
        input_relationships=relationship_set.total_relationships,
        include_neutral=include_neutral,
        partitioning="constraint_based_signed_graph",
        bridge_detection="articulation_points",
        temporal_source="claim.timestamp",
    )

    start_time = manifest_manager.start_phase(phase=7)
    stats = Phase7StatsCollector()

    # ── Sub-Pipeline A: Construction ──────────────────────────────────────────
    stats.record_construction_start()
    construction_timer_start = time.monotonic()

    with Timer("phase7_construction"):
        backend = NetworkXBackend()
        construction_result = run_construction(
            relationship_set=relationship_set,
            claims_map=claims_map,
            backend=backend,
            include_neutral=include_neutral,
        )

    stats.record_input(
        total=relationship_set.total_relationships,
        filtered=construction_result.relationships_filtered,
    )

    validation_report = validate_graph_structure(
        nodes=construction_result.nodes,
        edges=construction_result.edges,
        backend=construction_result.backend,
    )
    stats.record_validation_passed()
    stats.record_construction_end(
        nodes=len(construction_result.nodes),
        edges=len(construction_result.edges),
    )

    construction_time = time.monotonic() - construction_timer_start

    # ── Sub-Pipeline B: Semantic Enrichment ───────────────────────────────────
    stats.record_enrichment_start()
    enrichment_timer_start = time.monotonic()

    annotation_policy = AnnotationPolicy.from_config()

    ctx = SemanticReasoningContext(
        nodes=construction_result.nodes,
        edges=construction_result.edges,
        backend=construction_result.backend,
        run_id=run_id,
        config_hash=config_hash,
    )

    with Timer("phase7_partitioning"):
        run_partitioning(ctx)  # Constraint-based (P0-1 fix)

    with Timer("phase7_topology"):
        run_topology_analysis(ctx, hub_degree_multiplier=hub_degree_multiplier)  # Articulation points (P0-3 fix)

    with Timer("phase7_annotation"):
        run_semantic_annotation(ctx, policy=annotation_policy)  # Config-driven (P1-4 fix)

    with Timer("phase7_aggregation"):
        run_evidence_aggregation(ctx)  # Unique provenance roots (P0-2 fix)

    with Timer("phase7_temporal"):
        run_temporal_resolution(ctx, claims_map)  # Claim.timestamp (P0-4 fix)

    enrichment_time = time.monotonic() - enrichment_timer_start

    evolution_chains = sum(
        1 for t in ctx.temporal_metadata.values()
        if t and t.status == TemporalStatus.EVOLUTION_CHAIN
    ) // 2
    unresolved = sum(
        1 for t in ctx.temporal_metadata.values()
        if t and t.status == TemporalStatus.UNRESOLVED_CONFLICT
    ) // 2
    contradiction_boundaries = sum(
        1 for e in ctx.edges.values()
        if e.relationship_type.value == "contradicts"
    )

    stats.record_enrichment_end(
        partitions=len(ctx.partitions),
        contradiction_boundaries=contradiction_boundaries,
        evolution_chains=evolution_chains,
        unresolved=unresolved,
    )

    # ── Assemble final KnowledgeGraph ─────────────────────────────────────────
    knowledge_graph = _assemble_graph(
        ctx=ctx,
        validation_report=validation_report,
        construction_time=construction_time,
        enrichment_time=enrichment_time,
    )

    final_stats = stats.finalize()

    # ── Write artifacts ────────────────────────────────────────────────────────
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase7"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(
        _serialize_knowledge_graph(knowledge_graph), encoding="utf-8"
    )

    logger.info(
        "dataset written",
        path=str(dataset_path),
        nodes=knowledge_graph.node_count,
        edges=knowledge_graph.edge_count,
        partitions=knowledge_graph.partition_count,
    )

    manifest_manager.end_phase(
        phase=7,
        start_time=start_time,
        inputs={"relationships": relationship_set.total_relationships},
        outputs={
            "nodes": knowledge_graph.node_count,
            "edges": knowledge_graph.edge_count,
            "partitions": knowledge_graph.partition_count,
            "contradictions": knowledge_graph.statistics.contradiction_count,
            "evolution_chains": knowledge_graph.statistics.evolution_chains,
            "bridge_nodes": knowledge_graph.statistics.bridge_nodes,
            "partitioning_algorithm": "constraint_based_signed_graph",
            "bridge_detection": "articulation_points",
            "temporal_source": "claim.timestamp",
            "dataset_path": str(dataset_path),
            "validation_passed": validation_report.is_valid,
        },
        status="success",
    )

    state_manager.complete_phase(phase=7)

    logger.info(
        "phase 7 complete",
        graph_id=knowledge_graph.graph_id[:8],
        nodes=knowledge_graph.node_count,
        partitions=knowledge_graph.partition_count,
        contradictions=knowledge_graph.statistics.contradiction_count,
        evolution_chains=knowledge_graph.statistics.evolution_chains,
        bridge_nodes=knowledge_graph.statistics.bridge_nodes,
        total_seconds=f"{final_stats.total_time_seconds:.2f}",
    )

    return knowledge_graph