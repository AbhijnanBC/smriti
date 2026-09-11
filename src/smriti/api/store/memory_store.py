"""
memory_store.py — InMemoryReadStore: pure primitive retrieval only.

RECTIFIED (P0-1): All traversal, aggregation, and statistics logic has been
REMOVED from this class. It now does exactly:
    lookup()            → dict lookup
    scan()              → linear scan + sort + slice
    fetch_relationship()→ dict lookup
    stream()            → dict iteration
    get_edge_records()  → edge list
    get_adjacency()     → pre-built adj list

NavigationService owns traversal.
StatisticsService owns aggregation.

RECTIFIED (Phase 9 compatibility): Safely extracts all enum-like fields,
handling both enum objects and strings from deserialized JSON.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Iterator
from typing import Any

import structlog
from smriti.api.domain.predicates import Pagination, Predicate, SortSpec
from smriti.api.store.read_store import ReadStore
from smriti.core.models import ScoredKnowledgeGraph, SortOrder

logger = structlog.get_logger(__name__)

STORE_VERSION = "1.0"


def _safe_str(value) -> str:
    """
    Safely convert a value to a string.
    If it's an enum with a `value` attribute, return that.
    If it's already a string, return it as-is.
    If None, return an empty string.
    """
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _safe_int(value) -> int:
    """Safely convert a value to an int."""
    if value is None:
        return 0
    return int(value)


def _safe_float(value) -> float:
    """Safely convert a value to a float."""
    if value is None:
        return 0.0
    return float(value)


class InMemoryReadStore(ReadStore):
    """
    In-memory ReadStore: primitive retrieval only.
    Loaded once at construction. Never modified after.
    """

    def __init__(self, scored_graph: ScoredKnowledgeGraph) -> None:
        t0 = time.monotonic()
        self._run_id = scored_graph.run_id
        self._graph = scored_graph.graph

        self._claim_records: dict[str, dict[str, Any]] = {}
        self._reliability_records: dict[str, dict[str, Any]] = {}
        self._adj: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        self._edge_records: list[dict[str, Any]] = []

        self._build_records(scored_graph)

        elapsed = (time.monotonic() - t0) * 1000
        logger.info(
            "read store initialized",
            claims=len(self._claim_records),
            edges=len(self._edge_records),
            build_ms=f"{elapsed:.1f}",
        )

    def _build_records(self, scored_graph: ScoredKnowledgeGraph) -> None:
        """Build flat records for O(1)/O(N) retrieval. No logic here."""
        graph = scored_graph.graph
        reliability = scored_graph.reliability

        for claim_id, node in graph.nodes.items():
            ann = getattr(node, "annotations", None)
            topo = ann.topology if ann else None
            support = ann.support_aggregate if ann else None
            temporal = ann.temporal_metadata if ann else None
            role = ann.semantic_role if ann else None
            partition_id = ann.partition_id if ann else None

            rel_meta = reliability.get(claim_id)

            # ── SAFE ENUM ACCESS: use _safe_str for all enum fields ─────────────
            self._claim_records[claim_id] = {
                "claim_id": claim_id,
                "claim_text": node.claim_text,
                "context": node.context,
                "document_id": node.document_id,
                "source_path": str(node.source_path),
                "partition_id": partition_id,
                "semantic_role": _safe_str(role) if role else "unclassified",
                "reliability_index": _safe_float(rel_meta.reliability_index if rel_meta else 0.0),
                "uncertainty_score": _safe_float(rel_meta.uncertainty_score if rel_meta else 100.0),
                "evidence_completeness": _safe_float(
                    rel_meta.evidence_completeness if rel_meta else 0.0
                ),
                "calibration_label": _safe_str(
                    rel_meta.calibration_label if rel_meta else "very_low"
                ),
                "policy_version": _safe_str(rel_meta.policy_version if rel_meta else ""),
                "degree": _safe_int(topo.degree if topo else 0),
                "in_degree": _safe_int(topo.in_degree if topo else 0),
                "centrality": _safe_float(topo.centrality if topo else 0.0),
                "is_hub": bool(topo.is_hub if topo else False),
                "is_bridge": bool(topo.is_bridge if topo else False),
                "support_count": _safe_int(support.support_count if support else 0),
                "weighted_confidence": _safe_float(support.weighted_confidence if support else 0.0),
                "supporting_claim_ids": list(support.supporting_claim_ids) if support else [],
                "temporal_status": _safe_str(temporal.status if temporal else "unknown"),
                "temporal_confidence": _safe_float(
                    temporal.temporal_confidence if temporal else 0.0
                ),
                "time_delta_days": temporal.time_delta_days if temporal else None,
            }

        for claim_id, meta in reliability.items():
            sv = meta.signal_vector
            self._reliability_records[claim_id] = {
                "claim_id": claim_id,
                "reliability_index": meta.reliability_index,
                "uncertainty_score": meta.uncertainty_score,
                "evidence_completeness": meta.evidence_completeness,
                "calibration_label": _safe_str(meta.calibration_label),
                "policy_version": meta.policy_version,
                "schema_version": meta.schema_version,
                "signal_vector": {
                    "evidence_strength": sv.evidence_strength,
                    "evidence_independence": sv.evidence_independence,
                    "source_diversity": sv.source_diversity,
                    "topology_strength": sv.topology_strength,
                    "conflict_pressure": sv.conflict_pressure,
                    "temporal_stability": sv.temporal_stability,
                    "evidence_completeness": sv.evidence_completeness,
                },
                "signal_statuses": dict(sv.statuses),
                "component_scores": [
                    {
                        "signal_name": (
                            _safe_str(c.signal_id)
                            if hasattr(c, "signal_id")
                            else _safe_str(c.get("signal_name", ""))
                        ),
                        "contribution": c.contribution,
                        "direction": c.direction,
                        "normalized_value": c.normalized_value,
                        "policy_weight": c.policy_weight,
                        "explanation": c.explanation,
                    }
                    for c in meta.component_scores
                ],
                "explanation": {
                    "summary": meta.explanation.summary,
                    "dominant_signal": meta.explanation.dominant_signal,
                    "limiting_signal": meta.explanation.limiting_signal,
                    "strengths": list(meta.explanation.strengths),
                    "weaknesses": list(meta.explanation.weaknesses),
                    "recommendations": list(meta.explanation.recommendations),
                },
                "audit": {
                    "policy_version": meta.audit.policy_version,
                    "fusion_algorithm": meta.audit.fusion_algorithm,
                    "normalization_version": meta.audit.normalization_version,
                    "computed_at_run_id": meta.audit.computed_at_run_id,
                    "signal_extractor_versions": dict(meta.audit.signal_extractor_versions),
                },
                "policy_snapshot": scored_graph.policy_snapshot,
            }

        # ── RECTIFIED: Safe edge record building ──────────────────────────────
        for edge_id, edge in graph.edges.items():
            rel_type = _safe_str(edge.relationship_type)
            direction = _safe_str(edge.direction)

            rec = {
                "edge_id": edge_id,
                "source_claim_id": edge.source_node_id,
                "target_claim_id": edge.target_node_id,
                "relationship_type": rel_type,
                "direction": direction,
                "calibrated_confidence": edge.calibrated_confidence,
                "cosine_similarity": edge.cosine_similarity,
                "candidate_rank": edge.candidate_rank,
            }
            self._edge_records.append(rec)

            src, tgt = edge.source_node_id, edge.target_node_id
            self._adj[src].append((tgt, edge_id, rel_type))
            if direction == "symmetric":
                self._adj[tgt].append((src, edge_id, rel_type))

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def node_count(self) -> int:
        return len(self._claim_records)

    def lookup(self, claim_id: str) -> dict[str, Any] | None:
        return self._claim_records.get(claim_id)

    def scan(
        self,
        predicates: list[Predicate],
        sort: SortSpec,
        pagination: Pagination,
        text_contains: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Linear scan with predicate filter, sort, and pagination."""
        results = []
        for _claim_id, record in self._claim_records.items():
            if not all(p.matches(record.get(p.field)) for p in predicates):
                continue
            if text_contains and text_contains.lower() not in record.get("claim_text", "").lower():
                continue
            results.append(record)

        total = len(results)

        # Stable sort: tiebreaker first (ascending), then primary with desired order
        if sort.tiebreaker_field:
            results.sort(key=lambda r: r.get(sort.tiebreaker_field, "") or "")
        results.sort(
            key=lambda r: r.get(sort.field, 0) or 0, reverse=(sort.order == SortOrder.DESC)
        )

        return results[pagination.offset : pagination.offset + pagination.limit], total

    def fetch_relationship(self, claim_id: str) -> dict[str, Any] | None:
        return self._reliability_records.get(claim_id)

    def stream(self) -> Iterator[dict[str, Any]]:
        return iter(self._claim_records.values())

    def get_edge_records(self) -> list[dict[str, Any]]:
        return list(self._edge_records)

    def get_adjacency(self) -> dict[str, list[tuple[str, str, str]]]:
        return dict(self._adj)

    def all_claim_records(self) -> dict[str, dict[str, Any]]:
        """Expose records for IndexBuilder."""
        return dict(self._claim_records)
