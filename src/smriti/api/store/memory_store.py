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
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Iterator
import structlog

from smriti.api.domain.predicates import Predicate, SortSpec, Pagination
from smriti.api.store.read_store import ReadStore
from smriti.core.models import ScoredKnowledgeGraph, SortOrder
from smriti.exceptions import ReadStoreError

logger = structlog.get_logger(__name__)

STORE_VERSION = "1.0"


class InMemoryReadStore(ReadStore):
    """
    In-memory ReadStore: primitive retrieval only.
    Loaded once at construction. Never modified after.
    """

    def __init__(self, scored_graph: ScoredKnowledgeGraph) -> None:
        t0 = time.monotonic()
        self._run_id = scored_graph.run_id
        self._graph = scored_graph.graph

        self._claim_records: Dict[str, Dict[str, Any]] = {}
        self._reliability_records: Dict[str, Dict[str, Any]] = {}
        self._adj: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
        self._edge_records: List[Dict[str, Any]] = []

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

            self._claim_records[claim_id] = {
                "claim_id": claim_id,
                "claim_text": node.claim_text,
                "context": node.context,
                "document_id": node.document_id,
                "source_path": str(node.source_path),
                "partition_id": partition_id,
                "semantic_role": role.value if role else "unclassified",
                "reliability_index": rel_meta.reliability_index if rel_meta else 0.0,
                "uncertainty_score": rel_meta.uncertainty_score if rel_meta else 100.0,
                "evidence_completeness": rel_meta.evidence_completeness if rel_meta else 0.0,
                "calibration_label": rel_meta.calibration_label.value if rel_meta else "very_low",
                "policy_version": rel_meta.policy_version if rel_meta else "",
                "degree": topo.degree if topo else 0,
                "in_degree": topo.in_degree if topo else 0,
                "centrality": topo.centrality if topo else 0.0,
                "is_hub": topo.is_hub if topo else False,
                "is_bridge": topo.is_bridge if topo else False,
                "support_count": support.support_count if support else 0,
                "weighted_confidence": support.weighted_confidence if support else 0.0,
                "supporting_claim_ids": list(support.supporting_claim_ids) if support else [],
                "temporal_status": temporal.status.value if temporal else "unknown",
                "temporal_confidence": temporal.temporal_confidence if temporal else 0.0,
                "time_delta_days": temporal.time_delta_days if temporal else None,
            }

        for claim_id, meta in reliability.items():
            sv = meta.signal_vector
            self._reliability_records[claim_id] = {
                "claim_id": claim_id,
                "reliability_index": meta.reliability_index,
                "uncertainty_score": meta.uncertainty_score,
                "evidence_completeness": meta.evidence_completeness,
                "calibration_label": meta.calibration_label.value,
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
                        "signal_name": c.signal_name,
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

        for edge_id, edge in graph.edges.items():
            rec = {
                "edge_id": edge_id,
                "source_claim_id": edge.source_node_id,
                "target_claim_id": edge.target_node_id,
                "relationship_type": edge.relationship_type.value,
                "direction": edge.direction.value,
                "calibrated_confidence": edge.calibrated_confidence,
                "cosine_similarity": edge.cosine_similarity,
                "candidate_rank": edge.candidate_rank,
            }
            self._edge_records.append(rec)
            src, tgt = edge.source_node_id, edge.target_node_id
            rtype = edge.relationship_type.value
            self._adj[src].append((tgt, edge_id, rtype))
            if edge.direction.value == "symmetric":
                self._adj[tgt].append((src, edge_id, rtype))

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def node_count(self) -> int:
        return len(self._claim_records)

    def lookup(self, claim_id: str) -> Optional[Dict[str, Any]]:
        return self._claim_records.get(claim_id)

    def scan(
        self,
        predicates: List[Predicate],
        sort: SortSpec,
        pagination: Pagination,
        text_contains: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Linear scan with predicate filter, sort, and pagination."""
        results = []
        for claim_id, record in self._claim_records.items():
            if not all(p.matches(record.get(p.field)) for p in predicates):
                continue
            if text_contains and text_contains.lower() not in record.get("claim_text", "").lower():
                continue
            results.append(record)

        total = len(results)
        reverse = (sort.order == SortOrder.DESC)
        tb_reverse = (sort.tiebreaker_order == SortOrder.DESC)
        results.sort(
            key=lambda r: (
                -(r.get(sort.field, 0) or 0) if reverse else (r.get(sort.field, 0) or 0),
                -(r.get(sort.tiebreaker_field, "") or "") if tb_reverse
                else (r.get(sort.tiebreaker_field, "") or ""),
            )
        )
        return results[pagination.offset: pagination.offset + pagination.limit], total

    def fetch_relationship(self, claim_id: str) -> Optional[Dict[str, Any]]:
        return self._reliability_records.get(claim_id)

    def stream(self) -> Iterator[Dict[str, Any]]:
        return iter(self._claim_records.values())

    def get_edge_records(self) -> List[Dict[str, Any]]:
        return list(self._edge_records)

    def get_adjacency(self) -> Dict[str, List[Tuple[str, str, str]]]:
        return dict(self._adj)

    def all_claim_records(self) -> Dict[str, Dict[str, Any]]:
        """Expose records for IndexBuilder."""
        return dict(self._claim_records)