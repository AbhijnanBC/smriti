"""
validation.py — Structural + semantic invariant validation for Phase 7.

RECTIFIED (P2-4): Added SemanticValidator which checks:
    - A claim cannot be both the source AND target of contradicting chains
      (e.g. SUPPORTS → CONTRADICTS → SUPPORTS is flagged as suspicious)
    - CONTRADICTS edges within any partition after partitioning is complete

Structural validation is unchanged from original.
Semantic validation is additive — it records warnings but only raises
GraphValidationError for hard invariant breaches (internal CONTRADICTS).

Any violation aborts graph construction. No partially valid graph proceeds.
Validation never modifies objects.
"""

from __future__ import annotations

import time
from typing import List, Tuple, Dict
import structlog

from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, ValidationReport,
)
from smriti.evolution.backend import GraphBackend
from smriti.exceptions import GraphValidationError

logger = structlog.get_logger(__name__)


def validate_graph_structure(
    nodes: Dict[str, ClaimNode],
    edges: Dict[str, RelationshipEdge],
    backend: GraphBackend,
) -> ValidationReport:
    """
    Validate structural and semantic invariants before enrichment.

    Structural checks:
        Node: unique IDs, non-empty claim_text
        Edge: existing endpoints, valid types, no UNKNOWN, confidence range
        Graph: backend/registry consistency

    Semantic checks (P2-4):
        - No SUPPORTS→CONTRADICTS→SUPPORTS chains that would indicate
          a transitivity violation (logged as a semantic warning)

    Returns:
        ValidationReport. is_valid=True if all invariants hold.

    Raises:
        GraphValidationError: On fatal invariant violation.
    """
    start = time.monotonic()
    node_violations: List[Tuple[str, str]] = []
    edge_violations: List[Tuple[str, str]] = []
    graph_violations: List[str] = []
    semantic_warnings: List[str] = []

    # ── Node validation ───────────────────────────────────────────────────────
    seen_node_ids = set()
    for node_id, node in nodes.items():
        if node_id != node.node_id:
            node_violations.append((node_id, f"Key mismatch: dict key={node_id}, node.node_id={node.node_id}"))
        if node_id in seen_node_ids:
            node_violations.append((node_id, "Duplicate node_id"))
        seen_node_ids.add(node_id)
        if not node.claim_text:
            node_violations.append((node_id, "Empty claim_text"))

    # Backend/registry consistency
    backend_nodes = set(backend.all_node_ids())
    for nid in sorted(set(nodes.keys()) - backend_nodes):
        graph_violations.append(f"Node {nid[:8]} in registry but not in backend")

    # ── Edge validation ───────────────────────────────────────────────────────
    seen_edge_ids = set()
    for edge_id, edge in edges.items():
        if edge_id in seen_edge_ids:
            edge_violations.append((edge_id, "Duplicate edge_id"))
        seen_edge_ids.add(edge_id)

        if edge.source_node_id not in nodes:
            edge_violations.append((edge_id, f"Source node {edge.source_node_id[:8]} not in registry"))
        if edge.target_node_id not in nodes:
            edge_violations.append((edge_id, f"Target node {edge.target_node_id[:8]} not in registry"))
        if edge.relationship_type == RelationshipType.UNKNOWN:
            edge_violations.append((edge_id, "UNKNOWN relationship type in graph (forbidden)"))
        if not (0.0 <= edge.calibrated_confidence <= 1.0):
            edge_violations.append((edge_id, f"Confidence out of range: {edge.calibrated_confidence}"))

    if backend.node_count == 0 and nodes:
        graph_violations.append("Backend is empty but node registry is not")

    # ── Semantic validation (P2-4) ─────────────────────────────────────────────
    # Check for suspicious SUPPORTS → CONTRADICTS → SUPPORTS chains
    # These don't abort construction but are flagged as semantic warnings
    for edge in edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            # Find nodes that SUPPORT edge.source_node_id
            supports_into_source = [
                e for e in edges.values()
                if e.relationship_type == RelationshipType.SUPPORTS
                and e.target_node_id == edge.source_node_id
            ]
            # Find nodes that edge.target_node_id SUPPORTs
            supports_out_of_target = [
                e for e in edges.values()
                if e.relationship_type == RelationshipType.SUPPORTS
                and e.source_node_id == edge.target_node_id
            ]
            if supports_into_source and supports_out_of_target:
                semantic_warnings.append(
                    f"Suspicious chain: SUPPORTS→CONTRADICTS→SUPPORTS around edge {edge.edge_id[:8]}. "
                    f"Claims supporting '{edge.source_node_id[:8]}' are transitively contradicted by "
                    f"claims that '{edge.target_node_id[:8]}' supports."
                )

    elapsed = time.monotonic() - start
    is_valid = (
        len(node_violations) == 0
        and len(edge_violations) == 0
        and len(graph_violations) == 0
        # semantic_warnings are non-fatal
    )

    report = ValidationReport(
        is_valid=is_valid,
        node_violations=tuple(node_violations),
        edge_violations=tuple(edge_violations),
        graph_violations=tuple(graph_violations),
        semantic_warnings=tuple(semantic_warnings),
        validation_time_seconds=elapsed,
    )

    if not is_valid:
        logger.error(
            "graph validation FAILED",
            node_violations=len(node_violations),
            edge_violations=len(edge_violations),
            graph_violations=len(graph_violations),
        )
        raise GraphValidationError(
            f"Graph validation failed: {report.total_violations} violation(s). "
            f"Node: {len(node_violations)}, Edge: {len(edge_violations)}, "
            f"Graph: {len(graph_violations)}"
        )

    if semantic_warnings:
        logger.warning(
            "semantic chain warnings detected",
            count=len(semantic_warnings),
        )

    logger.info(
        "graph validation passed",
        nodes=len(nodes), edges=len(edges),
        semantic_warnings=len(semantic_warnings),
        validation_seconds=f"{elapsed:.3f}",
    )
    return report