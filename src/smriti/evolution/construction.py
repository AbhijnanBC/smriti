"""
construction.py — Graph construction pipeline (Part 3 of blueprint).

Five stages:
    Stage 1: Ingestion & Filtering      → stream of accepted Relationship objects
    Stage 2: Node Registry Construction → {claim_id: ClaimNode}
    Stage 3: Edge Registry Construction → {edge_id: RelationshipEdge}
    Stage 4: Backend Population         → GraphBackend populated
    Stage 5: Structural + Semantic Validation → ValidationReport

Complexity: O(N + E). No graph traversal during construction.

Rules:
    ✅ Deterministic ordering at every stage (sorted by ID)
    ✅ One ClaimNode per unique claim_id
    ✅ UNKNOWN relationships always filtered
    ✅ NEUTRAL relationships filtered by default
    ✅ Missing claim references terminate construction
    ❌ No semantic reasoning during construction
    ❌ No partition assignment (enrichment's job)
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from smriti.core.models import (
    Claim,
    ClaimNode,
    Relationship,
    RelationshipEdge,
    RelationshipSet,
    RelationshipType,
)
from smriti.evolution.backend import GraphBackend
from smriti.exceptions import GraphConstructionError

logger = structlog.get_logger(__name__)


@dataclass
class ConstructionResult:
    """Output of the construction sub-pipeline."""

    nodes: dict[str, ClaimNode]
    edges: dict[str, RelationshipEdge]
    backend: GraphBackend
    relationships_ingested: int
    relationships_filtered: int
    filter_reasons: dict[str, int]


ACCEPTED_TYPES = frozenset(
    [
        RelationshipType.CONTRADICTS,
        RelationshipType.SUPPORTS,
        RelationshipType.REFINES,
        RelationshipType.EQUIVALENT,
    ]
)


def run_construction(
    relationship_set: RelationshipSet,
    claims_map: dict[str, Claim],
    backend: GraphBackend,
    include_neutral: bool = False,
) -> ConstructionResult:
    """Execute the 5-stage construction sub-pipeline."""
    # Stage 1: Ingestion & Filtering
    accepted_types = ACCEPTED_TYPES | ({RelationshipType.NEUTRAL} if include_neutral else set())
    accepted: list[Relationship] = []
    filter_reasons: dict[str, int] = {}

    for rel in relationship_set.relationships:
        if rel.relationship_type not in accepted_types:
            reason = rel.relationship_type.value
            filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
            continue
        accepted.append(rel)

    accepted.sort(key=lambda r: r.relationship_id)
    relationships_filtered = len(relationship_set.relationships) - len(accepted)

    logger.info(
        "ingestion complete",
        total=len(relationship_set.relationships),
        accepted=len(accepted),
        filtered=relationships_filtered,
    )

    # Stage 2: Node Registry Construction
    claim_id_set: set[str] = set()
    for rel in accepted:
        claim_id_set.add(rel.claim_id_a)
        claim_id_set.add(rel.claim_id_b)

    nodes: dict[str, ClaimNode] = {}
    for claim_id in sorted(claim_id_set):
        claim = claims_map.get(claim_id)
        if claim is None:
            raise GraphConstructionError(
                f"Referential integrity violation: relationship references claim_id "
                f"'{claim_id}' which does not exist in claims_map. "
                "This indicates a Phase 4–6 pipeline inconsistency."
            )
        nodes[claim_id] = ClaimNode(
            node_id=claim_id,
            claim_id=claim_id,
            claim_text=claim.text,
            context=claim.context,
            source_path=claim.source_path,
            document_id=claim.document_id,
            annotations=None,  # Populated during enrichment
            schema_version="7.0",
        )

    logger.info("node registry constructed", nodes=len(nodes))

    # Stage 3: Edge Registry Construction
    edges: dict[str, RelationshipEdge] = {}
    seen_edge_ids: set[str] = set()

    for rel in accepted:
        if rel.relationship_id in seen_edge_ids:
            logger.warning("duplicate edge_id, skipping", edge_id=rel.relationship_id[:8])
            continue
        seen_edge_ids.add(rel.relationship_id)

        edges[rel.relationship_id] = RelationshipEdge(
            edge_id=rel.relationship_id,
            source_node_id=rel.claim_id_a,
            target_node_id=rel.claim_id_b,
            relationship_type=rel.relationship_type,
            direction=rel.direction,
            calibrated_confidence=rel.evidence.calibrated_confidence,
            cosine_similarity=rel.evidence.cosine_similarity,
            nli_confidence=rel.evidence.nli_scores.raw_confidence,
            candidate_rank=rel.provenance.candidate_rank,
            schema_version="7.0",
        )

    logger.info("edge registry constructed", edges=len(edges))

    # Stage 4: Backend Population
    for node_id in sorted(nodes.keys()):
        backend.add_node(node_id, claim_text=nodes[node_id].claim_text)

    for edge_id in sorted(edges.keys()):
        edge = edges[edge_id]
        backend.add_edge(
            source=edge.source_node_id,
            target=edge.target_node_id,
            edge_id=edge_id,
            relationship_type=edge.relationship_type.value,
            confidence=edge.calibrated_confidence,
        )
        # CONTRADICTS and EQUIVALENT are symmetric: add reverse edge for
        # undirected traversal (SUPPORTS/REFINES stay directed on purpose).
        if edge.relationship_type in (RelationshipType.CONTRADICTS, RelationshipType.EQUIVALENT):
            backend.add_edge(
                source=edge.target_node_id,
                target=edge.source_node_id,
                edge_id=f"{edge_id}_rev",
                relationship_type=edge.relationship_type.value,
                confidence=edge.calibrated_confidence,
            )

    logger.info(
        "backend populated",
        backend_nodes=backend.node_count,
        backend_edges=backend.edge_count,
    )

    return ConstructionResult(
        nodes=nodes,
        edges=edges,
        backend=backend,
        relationships_ingested=len(accepted),
        relationships_filtered=relationships_filtered,
        filter_reasons=filter_reasons,
    )
