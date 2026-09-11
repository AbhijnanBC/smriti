"""
context.py — SemanticReasoningContext for Phase 7 enrichment pipeline.

Flows through all 5 semantic enrichment stages without polluting the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from smriti.core.models import (
    ClaimNode,
    KnowledgePartition,
    RelationshipEdge,
    SemanticRole,
    SupportAggregate,
    TemporalMetadata,
    TopologyMetrics,
)
from smriti.evolution.backend import GraphBackend

logger = structlog.get_logger(__name__)


@dataclass
class SemanticReasoningContext:
    """
    Transient execution context flowing through the 5-stage enrichment pipeline.
    Mutated by each stage. Never exposed to callers of __init__.py.
    """

    nodes: dict[str, ClaimNode]
    edges: dict[str, RelationshipEdge]
    backend: GraphBackend
    run_id: str
    config_hash: str

    partitions: dict[str, KnowledgePartition] = field(default_factory=dict)
    node_to_partition: dict[str, str] = field(default_factory=dict)

    topology_metrics: dict[str, TopologyMetrics] = field(default_factory=dict)
    semantic_roles: dict[str, SemanticRole] = field(default_factory=dict)
    support_aggregates: dict[str, SupportAggregate] = field(default_factory=dict)
    temporal_metadata: dict[str, TemporalMetadata] = field(default_factory=dict)

    stats_collector: object | None = None

    def get_partition_nodes(self, partition_id: str) -> list[str]:
        partition = self.partitions.get(partition_id)
        if not partition:
            return []
        return sorted(partition.node_ids)

    def get_partition_for_node(self, claim_id: str) -> str | None:
        return self.node_to_partition.get(claim_id)
