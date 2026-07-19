"""
context.py — SemanticReasoningContext for Phase 7 enrichment pipeline.

Flows through all 5 semantic enrichment stages without polluting the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import structlog

from smriti.core.models import (
    ClaimNode, RelationshipEdge, KnowledgePartition,
    TopologyMetrics, SupportAggregate, TemporalMetadata, SemanticRole, Phase7Stats,
)
from smriti.evolution.backend import GraphBackend

logger = structlog.get_logger(__name__)


@dataclass
class SemanticReasoningContext:
    """
    Transient execution context flowing through the 5-stage enrichment pipeline.
    Mutated by each stage. Never exposed to callers of __init__.py.
    """
    nodes: Dict[str, ClaimNode]
    edges: Dict[str, RelationshipEdge]
    backend: GraphBackend
    run_id: str
    config_hash: str

    partitions: Dict[str, KnowledgePartition] = field(default_factory=dict)
    node_to_partition: Dict[str, str] = field(default_factory=dict)

    topology_metrics: Dict[str, TopologyMetrics] = field(default_factory=dict)
    semantic_roles: Dict[str, SemanticRole] = field(default_factory=dict)
    support_aggregates: Dict[str, SupportAggregate] = field(default_factory=dict)
    temporal_metadata: Dict[str, TemporalMetadata] = field(default_factory=dict)

    stats_collector: Optional[object] = None

    def get_partition_nodes(self, partition_id: str) -> List[str]:
        partition = self.partitions.get(partition_id)
        if not partition:
            return []
        return sorted(partition.node_ids)

    def get_partition_for_node(self, claim_id: str) -> Optional[str]:
        return self.node_to_partition.get(claim_id)