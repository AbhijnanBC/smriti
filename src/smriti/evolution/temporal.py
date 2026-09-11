"""
temporal.py — Temporal evolution resolution for Phase 7.

RECTIFIED (P0-4): The original implementation read filesystem st_mtime
via stat().st_mtime. This is semantically catastrophic:

    git checkout old_branch
    → timestamps change
    → graph evolution changes
    → KnowledgeGraph changes for the same semantic content

Fixed: TemporalResolver consumes Claim.timestamp (a semantic datetime field
set during document parsing). If Claim.timestamp is None (not yet populated
by Phase 2/3), the status is NO_TIMESTAMP and temporal reasoning is disabled
for that pair. The filesystem is NEVER consulted.

Claim.timestamp must be populated by Phase 2 (document parsing) from:
    1. YAML front matter `date:` field (ISO 8601)
    2. Explicit metadata embedded in the document
    NOT from filesystem modification time.

If Claim.timestamp is not yet a field in the current Claim model,
add Optional[datetime] = None to Claim in models.py.

CRITICAL RULE: Historical information is NEVER discarded.
Temporal reasoning adds metadata. It does not remove claims or relationships.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Claim,
    NodeAnnotations,
    RelationshipType,
    TemporalMetadata,
    TemporalStatus,
)
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


# Orchestrates the full Phase 7 temporal-resolution pipeline as one linear,
# order-sensitive sequence; splitting it up would scatter that sequence
# across helpers with no natural seams.
def run_temporal_resolution(  # noqa: C901
    ctx: SemanticReasoningContext,
    claims_map: dict[str, Claim],
) -> None:
    """
    Resolve temporal evolution for contradiction boundaries.

    Uses Claim.timestamp (semantic datetime), never filesystem st_mtime.

    For each pair of nodes connected by CONTRADICTS edges:
        1. Look up Claim.timestamp for each node
        2. If either timestamp is None → NO_TIMESTAMP
        3. Compute time delta in days
        4. Apply min_reliable_delta_days threshold from config
        5. Assign TemporalMetadata to both nodes

    CRITICAL: Never reads filesystem metadata. Never modifies claims.
    """
    config = get_config()
    min_reliable_delta = config.get("knowledge_graph", {}).get("min_reliable_delta_days", 1.0)

    temporal: dict[str, TemporalMetadata] = {}

    # Collect CONTRADICTS pairs
    contradicts_pairs: list[tuple[str, str, str]] = []
    for edge in ctx.edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            contradicts_pairs.append((edge.edge_id, edge.source_node_id, edge.target_node_id))

    # Process each contradiction boundary
    for _edge_id, node_a_id, node_b_id in contradicts_pairs:
        if node_a_id in temporal and node_b_id in temporal:
            continue  # Already processed this pair

        claim_a = claims_map.get(node_a_id)
        claim_b = claims_map.get(node_b_id)

        if not claim_a or not claim_b:
            _assign_static(temporal, node_a_id, node_b_id, temporal_confidence=0.0)
            continue

        # RECTIFIED: Use Claim.timestamp (semantic), never filesystem stat()
        ts_a = _get_semantic_timestamp(claim_a)
        ts_b = _get_semantic_timestamp(claim_b)

        if ts_a is None or ts_b is None:
            # Timestamp unavailable → NO_TIMESTAMP status
            _assign_no_timestamp(temporal, node_a_id, node_b_id)
            continue

        # Compute time delta in days
        delta = abs((ts_b - ts_a).total_seconds()) / 86400.0

        if delta < min_reliable_delta:
            _assign_unresolved(temporal, node_a_id, node_b_id, delta)
        elif ts_a < ts_b:
            _assign_evolution(temporal, node_a_id, node_b_id, delta, min_reliable_delta)
        else:
            _assign_evolution(temporal, node_b_id, node_a_id, delta, min_reliable_delta)

    # Nodes not involved in any contradiction get STATIC_PARTITION
    for node_id in ctx.nodes:
        if node_id not in temporal:
            temporal[node_id] = TemporalMetadata(
                status=TemporalStatus.STATIC_PARTITION,
                earlier_claim_id=None,
                later_claim_id=None,
                time_delta_days=None,
                temporal_confidence=0.0,
            )

    ctx.temporal_metadata = temporal

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        temp = temporal.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, temporal_metadata=temp)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    evolution_count = (
        sum(1 for t in temporal.values() if t.status == TemporalStatus.EVOLUTION_CHAIN) // 2
    )
    no_ts_count = sum(1 for t in temporal.values() if t.status == TemporalStatus.NO_TIMESTAMP) // 2
    unresolved_count = (
        sum(1 for t in temporal.values() if t.status == TemporalStatus.UNRESOLVED_CONFLICT) // 2
    )

    logger.info(
        "temporal resolution complete",
        evolution_chains=evolution_count,
        unresolved=unresolved_count,
        no_timestamp=no_ts_count,
        source="claim.timestamp (semantic — never filesystem)",
    )


def _get_semantic_timestamp(claim: Claim) -> datetime | None:
    """
    Return the semantic timestamp from Claim.timestamp.

    RECTIFIED (P0-4): This function NEVER reads the filesystem.
    If Claim.timestamp is not set, returns None.
    The caller assigns NO_TIMESTAMP status.

    To populate Claim.timestamp, Phase 2 must extract it from:
        - YAML front matter: `date: 2024-01-15`
        - Document metadata fields
    """
    ts = getattr(claim, "timestamp", None)
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    # Handle string timestamps from Phase 2/3 if needed
    try:

        if isinstance(ts, str):
            return datetime.fromisoformat(ts).replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return None
    return None


def _assign_static(
    temporal: dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
    temporal_confidence: float,
) -> None:
    meta = TemporalMetadata(
        status=TemporalStatus.STATIC_PARTITION,
        earlier_claim_id=None,
        later_claim_id=None,
        time_delta_days=None,
        temporal_confidence=temporal_confidence,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_no_timestamp(
    temporal: dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
) -> None:
    """Assign NO_TIMESTAMP when Claim.timestamp is unavailable."""
    meta = TemporalMetadata(
        status=TemporalStatus.NO_TIMESTAMP,
        earlier_claim_id=None,
        later_claim_id=None,
        time_delta_days=None,
        temporal_confidence=0.0,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_unresolved(
    temporal: dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
    delta: float,
) -> None:
    meta = TemporalMetadata(
        status=TemporalStatus.UNRESOLVED_CONFLICT,
        earlier_claim_id=None,
        later_claim_id=None,
        time_delta_days=round(delta, 2),
        temporal_confidence=0.0,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_evolution(
    temporal: dict[str, TemporalMetadata],
    earlier: str,
    later: str,
    delta: float,
    min_reliable_delta: float,
) -> None:
    """Confidence scales with delta up to 30 days (configurable)."""
    reference_days = max(min_reliable_delta * 30.0, 30.0)
    confidence = min(1.0, delta / reference_days)
    meta = TemporalMetadata(
        status=TemporalStatus.EVOLUTION_CHAIN,
        earlier_claim_id=earlier,
        later_claim_id=later,
        time_delta_days=round(delta, 2),
        temporal_confidence=round(confidence, 3),
    )
    temporal[earlier] = meta
    temporal[later] = meta
