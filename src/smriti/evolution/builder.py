"""
builder.py — Immutable KnowledgeGraph assembly for Phase 7.

RECTIFIED (P2-1): Statistics computation extracted into StatisticsBuilder.
The main build_knowledge_graph() function only assembles; it delegates
all graph-wide metric computation to StatisticsBuilder.

This respects single-responsibility and allows statistics computation to
reuse precomputed metadata from context rather than re-traversing.
"""

from __future__ import annotations

import hashlib

import structlog

from smriti.core.models import (
    GraphStatistics,
    KnowledgeGraph,
    RelationshipType,
    TemporalStatus,
)
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)

PHASE7_SCHEMA_VERSION = "7.0"


class StatisticsBuilder:
    """
    Computes graph-wide statistics from the enriched SemanticReasoningContext.

    RECTIFIED (P2-1): Extracted from build_knowledge_graph() to respect
    single-responsibility. Reuses precomputed data from topology and temporal
    stages — no double-traversal.
    """

    @staticmethod
    def build(
        ctx: SemanticReasoningContext,
        construction_time: float,
        enrichment_time: float,
    ) -> GraphStatistics:
        """Build GraphStatistics from precomputed context data."""
        nodes = ctx.nodes
        edges = ctx.edges
        partitions = ctx.partitions

        contradiction_count = sum(
            1 for e in edges.values() if e.relationship_type == RelationshipType.CONTRADICTS
        )
        supports_count = sum(
            1 for e in edges.values() if e.relationship_type == RelationshipType.SUPPORTS
        )
        refines_count = sum(
            1 for e in edges.values() if e.relationship_type == RelationshipType.REFINES
        )
        equivalent_count = sum(
            1 for e in edges.values() if e.relationship_type == RelationshipType.EQUIVALENT
        )

        # Reuse precomputed topology metrics (no re-traversal)
        isolated = sum(
            1
            for nid in nodes
            if ctx.topology_metrics.get(nid) and ctx.topology_metrics[nid].degree == 0
        )
        bridges = sum(1 for m in ctx.topology_metrics.values() if m.is_bridge)
        hubs = sum(1 for m in ctx.topology_metrics.values() if m.is_hub)

        # Reuse precomputed temporal metadata (no re-traversal)
        evolution_chains = (
            sum(
                1  # type: ignore[misc]  # mypy sum()/Iterable[bool] overload quirk; see evolution/__init__.py
                for t in ctx.temporal_metadata.values()
                if t and t.status == TemporalStatus.EVOLUTION_CHAIN
            )
            // 2
        )
        unresolved = (
            sum(
                1  # type: ignore[misc]
                for t in ctx.temporal_metadata.values()
                if t and t.status == TemporalStatus.UNRESOLVED_CONFLICT
            )
            // 2
        )

        return GraphStatistics(
            node_count=len(nodes),
            edge_count=len(edges),
            partition_count=len(partitions),
            contradiction_count=contradiction_count,
            supports_count=supports_count,
            refines_count=refines_count,
            isolated_nodes=isolated,
            bridge_nodes=bridges,
            hub_nodes=hubs,
            evolution_chains=evolution_chains,
            unresolved_conflicts=unresolved,
            construction_time_seconds=round(construction_time, 4),
            enrichment_time_seconds=round(enrichment_time, 4),
            equivalent_count=equivalent_count,
        )


def build_knowledge_graph(
    ctx: SemanticReasoningContext,
    validation_report,
    construction_time: float,
    enrichment_time: float,
    document_provenance: dict | None = None,
) -> KnowledgeGraph:
    """
    Assemble the final KnowledgeGraph from a fully enriched context.

    Delegates statistics computation to StatisticsBuilder (P2-1).
    Pure construction — no reasoning, no validation, no inference.

    document_provenance (external review, P1-1): document_id -> keyed
    disclosed source identity, threaded in by the pipeline runner from
    Phase 2's own output (never fabricated here). Defaults to {} so every
    existing caller that predates this parameter keeps working unchanged.
    """
    stats = StatisticsBuilder.build(ctx, construction_time, enrichment_time)
    graph_id = _compute_graph_id(ctx.run_id, ctx.config_hash)

    graph = KnowledgeGraph(
        graph_id=graph_id,
        nodes=dict(ctx.nodes),
        edges=dict(ctx.edges),
        partitions=dict(ctx.partitions),
        statistics=stats,
        validation_report=validation_report,
        run_id=ctx.run_id,
        config_hash=ctx.config_hash,
        schema_version=PHASE7_SCHEMA_VERSION,
        document_provenance=document_provenance or {},
    )

    logger.info(
        "knowledge graph assembled",
        graph_id=graph_id[:8],
        nodes=len(ctx.nodes),
        edges=len(ctx.edges),
        partitions=len(ctx.partitions),
        contradictions=stats.contradiction_count,
        bridge_nodes=stats.bridge_nodes,
    )

    return graph


def _compute_graph_id(run_id: str, config_hash: str) -> str:
    """Deterministic 16-char graph ID."""
    material = f"{run_id}:{config_hash}"
    return hashlib.sha256(material.encode()).hexdigest()[:16]
