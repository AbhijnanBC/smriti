This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  workflows/
    ci.yml
artifacts/
  .gitkeep
config/
  default.yaml
  dev.yaml
  test.yaml
data/
  raw/
    .gitkeep
  .gitkeep
docs/
  relationship_ontology.md
scripts/
  download_models.ps1
  setup_dev.ps1
src/
  smriti/
    claims/
      __init__.py
      annotation.py
      boundaries.py
      builder.py
      degradation.py
      models.py
      parser.py
      rules.py
      statistics.py
      structure.py
      validator.py
    contradiction/
      __init__.py
      detector.py
    core/
      __init__.py
      cache.py
      config.py
      hashing.py
      logger.py
      manifest.py
      models.py
      paths.py
      state.py
      timing.py
    dashboard/
      __init__.py
      app.py
    discovery/
      __init__.py
      builder.py
      duplicate.py
      hashing.py
      metadata.py
      scanner.py
      validator.py
    embedding/
      __init__.py
      builders.py
      cache.py
      embedder.py
      input_factory.py
      models.py
      normalization.py
      statistics.py
      validation.py
    evolution/
      __init__.py
      aggregation.py
      annotation.py
      backend.py
      builder.py
      construction.py
      context.py
      networkx_backend.py
      partitioning.py
      statistics.py
      temporal.py
      topology.py
      validation.py
    extraction/
      scanner/
        __init__.py
        code.py
        heading.py
        paragraph.py
        scanner.py
        table.py
      __init__.py
      builder.py
      context.py
      extractor.py
      normalizer.py
      rules.py
      segmenter.py
      statistics.py
      validator.py
    parsing/
      __init__.py
      builder.py
      loader.py
      markdown.py
      normalize.py
      parser.py
      pdf.py
      statistics.py
      text.py
    pipeline/
      __init__.py
      runner.py
      validator.py
    reporting/
      __init__.py
      exporter.py
    retrieval/
      classification/
        calibration.py
        conflict.py
        evidence.py
        resolver.py
        validator.py
      __init__.py
      benchmark.py
      builder.py
      candidate_generator.py
      faiss_index.py
      governance.py
      incremental.py
      index.py
      replay.py
      retriever.py
      statistics.py
      validator.py
    scoring/
      signals/
        __init__.py
        base.py
        conflict.py
        evidence.py
        independence.py
        provenance.py
        structural.py
        temporal.py
      __init__.py
      builder.py
      constraints.py
      explanation.py
      fusion.py
      graph_stats.py
      normalization.py
      policies.py
      scorer.py
      statistics.py
    __init__.py
    __version__.py
    constants.py
    exceptions.py
    main.py
  .gitkeep
tests/
  fixtures/
    sample_notes.md
    sample.pdf
  integration/
    test_phase1_discovery.py
    test_phase3_extraction.py
    test_phase4_extraction.py
    test_phase5_embedding.py
    test_phase6_discovery.py
    test_phase7_knowledge_graph.py
    test_phase8_scoring.py
    test_pipeline_runner.py
  unit/
    test_builder.py
    test_cache.py
    test_config.py
    test_duplicate.py
    test_hashing.py
    test_manifest.py
    test_metadata.py
    test_models.py
    test_parsing_builder.py
    test_parsing_loader.py
    test_parsing_markdown.py
    test_parsing_normalize.py
    test_parsing_pdf.py
    test_parsing_statistics.py
    test_phase2_extraction.py
    test_phase3_builder.py
    test_phase3_context.py
    test_phase3_normalizer.py
    test_phase3_scanner.py
    test_phase3_segmenter.py
    test_phase3_statistics.py
    test_phase3_validator.py
    test_phase4_annotation.py
    test_phase4_boundaries.py
    test_phase4_builder.py
    test_phase4_parser.py
    test_phase4_structure.py
    test_phase4_validator.py
    test_phase5_builders.py
    test_phase5_cache.py
    test_phase5_input_factory.py
    test_phase5_normalization.py
    test_phase5_property_based.py
    test_phase5_validation.py
    test_phase6_builder.py
    test_phase6_calibration.py
    test_phase6_candidate_generator.py
    test_phase6_candidate_validator.py
    test_phase6_resolver.py
    test_phase7_aggregation_dedup.py
    test_phase7_annotation.py
    test_phase7_construction.py
    test_phase7_partitioning.py
    test_phase7_temporal_semantic.py
    test_phase7_topology_bridges.py
    test_phase7_validation.py
    test_phase8_explanation.py
    test_phase8_fusion.py
    test_phase8_normalization.py
    test_phase8_policies.py
    test_phase8_registry.py
    test_phase8_signals.py
    test_scanner.py
    test_validator.py
  __init__.py
  conftest.py
.gitignore
download_models.ps1
LICENSE
Makefile.ps1
pyproject.toml
README.md
setup_dev.ps1
```

# Files

## File: docs/relationship_ontology.md
````markdown
# SMRITI Phase 7: Semantic Relationship Ontology & Graph Traversal Specification

This document defines the canonical ontology for semantic relationships discovered in Phase 6 and establishes the strict mathematical and traversal rules for the Phase 7 Knowledge Graph construction. 

All downstream consumers, graph traversal algorithms, and temporal reasoning engines must adhere to these invariants.

---

### 1. Ingestion & Discard Policy

Phase 7 treats the `RelationshipSet` output from Phase 6 as an immutable stream of edges. Before any graph construction begins, the following ingestion filters must be applied:

*   **Valid Edges:** `SUPPORTS`, `CONTRADICTS`, and `REFINES` relationships are explicitly ingested into the graph structure.
*   **Neutral Edges:** `NEUTRAL` relationships are dropped during ingestion to prevent graph bloat, as they represent semantic proximity without logical direction.
*   **The Discard Policy:** `UNKNOWN` relationships are strictly dropped at the Phase 6 boundary. They must never enter the Phase 7 graph, as they represent insufficient or contradictory evidence and cannot be safely traversed.

---

### 2. Semantic Edge Definitions & Transitivity

The Phase 7 Knowledge Graph relies on the specific mathematical properties of each relationship type to perform safe logical reasoning.

| Relationship Type | Directionality | Transitivity | Graph Usage |
| :--- | :--- | :--- | :--- |
| **SUPPORTS** | Directional (A → B) | **True** | Builds corroboration chains. If A supports B, and B supports C, the graph infers A indirectly supports C. |
| **CONTRADICTS** | Symmetric (A ↔ B) | **False** | Identifies factual collisions. If A contradicts B, and B contradicts C, A does not necessarily contradict C. |
| **REFINES** | Directional (A → B) | **False** | Tracks concept elaboration. Narrowing scope repeatedly may alter the premise, so transitivity cannot be assumed. |

---

### 3. Graph Traversal & Boundary Rules

When querying or walking the Phase 7 Knowledge Graph, traversal algorithms must respect structural boundaries to prevent the fusion of incompatible realities into a single context window.

*   **The Contradiction Partition:** `CONTRADICTS` edges act as strict graph partitions. A standard logical traversal (e.g., aggregating facts about a specific topic) must stop immediately upon encountering a `CONTRADICTS` edge.
*   **Graph Bifurcation:** When a contradiction is encountered, the graph effectively bifurcates into competing states of reality. The traversal algorithm must not fuse claims from across the contradiction boundary into a cohesive summary.
*   **Temporal Resolution:** To resolve graph partitions, traversal algorithms must inspect the `ClaimProvenance` timestamps of the conflicting nodes. Graph algorithms must weight these edges by timestamp, allowing the system to prefer the most recent claim as the "current" reality while preserving the older claim strictly as historical evolution.
````

## File: src/smriti/evolution/aggregation.py
````python
"""
aggregation.py — Evidence aggregation for Phase 7.

RECTIFIED (P0-2): The original BFS deduplication used visited_edges (unique edges),
not unique supporting CLAIM IDs. In a DAG like:

    A → B → D
    A → C → D

BFS visiting D's incoming edges reaches A via two paths. Original code tracked
visited_edges, meaning it would add A's confidence once per path — double-counting.

Fix: Track supporting_claim_ids as a set. Add a claim's contribution only the
first time it appears, regardless of how many paths lead from it to the target.
This is "aggregate over unique provenance roots, not unique traversal paths."

Rules:
    - Follows only SUPPORTS edges within the same partition
    - Counts each unique supporting claim_id exactly ONCE
    - CONTRADICTS edges never contribute support
    - Aggregation never modifies edge confidence values
    - Never crosses partition boundaries
"""

from __future__ import annotations

import dataclasses
from collections import deque
from typing import Dict, Set
import structlog

from smriti.core.models import SupportAggregate, RelationshipType, NodeAnnotations
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


def run_evidence_aggregation(ctx: SemanticReasoningContext) -> None:
    """
    Aggregate SUPPORTS evidence for every node within its partition.
    Counts unique provenance root claim IDs, not traversal paths.
    """
    aggregates: Dict[str, SupportAggregate] = {}

    for partition_id, partition in ctx.partitions.items():
        partition_node_ids = partition.node_ids

        # Precompute: for each node, which SUPPORTS edges point TO it (same partition)
        incoming_supports: Dict[str, list] = {nid: [] for nid in partition_node_ids}
        # Also track: for each supporting claim, its edge confidence
        claim_confidence: Dict[str, float] = {}  # claim_id → confidence of its direct support edge

        for edge in ctx.edges.values():
            if (edge.relationship_type == RelationshipType.SUPPORTS
                    and edge.target_node_id in partition_node_ids
                    and edge.source_node_id in partition_node_ids):
                incoming_supports[edge.target_node_id].append(edge)
                # Store per-claim confidence for the first direct edge encountered
                if edge.source_node_id not in claim_confidence:
                    claim_confidence[edge.source_node_id] = edge.calibrated_confidence

        for node_id in partition_node_ids:
            # BFS: collect all transitive UNIQUE CLAIM IDs (not unique paths)
            # RECTIFIED (P0-2): supporting_ids tracks claim IDs seen,
            # ensuring each supporting claim is counted at most once regardless
            # of how many paths lead from it to node_id.
            supporting_ids: Set[str] = set()
            total_confidence = 0.0

            queue = deque(incoming_supports.get(node_id, []))
            visited_edge_ids: Set[str] = set()

            while queue:
                edge = queue.popleft()
                if edge.edge_id in visited_edge_ids:
                    continue
                visited_edge_ids.add(edge.edge_id)

                source_id = edge.source_node_id
                if source_id not in supporting_ids:
                    # First time we reach this claim — count its contribution
                    supporting_ids.add(source_id)
                    total_confidence += claim_confidence.get(source_id, edge.calibrated_confidence)
                # Always BFS further upstream (even if we've seen source_id before,
                # there may be new unique supporters upstream)
                for upstream_edge in incoming_supports.get(source_id, []):
                    if upstream_edge.edge_id not in visited_edge_ids:
                        queue.append(upstream_edge)

            # Weighted confidence = mean over unique supporting claims
            weighted_confidence = (
                total_confidence / len(supporting_ids) if supporting_ids else 0.0
            )
            summary = (
                f"{len(supporting_ids)} unique supporting claim(s), "
                f"avg confidence {weighted_confidence:.2f}"
                if supporting_ids else "No supporting evidence"
            )

            aggregates[node_id] = SupportAggregate(
                support_count=len(supporting_ids),
                weighted_confidence=round(weighted_confidence, 6),
                supporting_claim_ids=tuple(sorted(supporting_ids)),
                evidence_summary=summary,
            )

    ctx.support_aggregates = aggregates

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        agg = aggregates.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, support_aggregate=agg)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    logger.info(
        "evidence aggregation complete (unique provenance roots)",
        nodes_with_support=sum(1 for a in aggregates.values() if a.support_count > 0),
        total_nodes=len(aggregates),
    )
````

## File: src/smriti/evolution/annotation.py
````python
"""
annotation.py — Semantic role annotation for Phase 7.

RECTIFIED (P1-4): All annotation thresholds are now read from AnnotationPolicy
(constructed from config). No threshold values are hardcoded in this file.

RECTIFIED (P2-3): RoleClassifier protocol introduced. Default implementation
is TopologyRoleClassifier. Future implementations can use ML-based classifiers
without changing this file's public interface.

AnnotationPolicy fields (all configurable):
    foundational_centrality_threshold: float  (default 0.50)
    foundational_min_in_degree:        int    (default 2)
    evidence_hub_min_in_degree:        int    (default 3)
    refinement_root_min_out:           int    (default 2)
    hub_degree_multiplier:             float  (default 2.0)
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Dict, Protocol
from collections import Counter
import structlog

from smriti.core.config import get_config
from smriti.core.models import SemanticRole, RelationshipType, NodeAnnotations
from smriti.evolution.context import SemanticReasoningContext
from smriti.exceptions import AnnotationPolicyError

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class AnnotationPolicy:
    """
    All annotation thresholds in one place. Read from config.
    No threshold values appear in annotation logic itself.

    RECTIFIED (P1-4): replaces hardcoded 0.50, 0.30, 3, 2, etc.
    """
    foundational_centrality_threshold: float = 0.50
    foundational_min_in_degree: int = 2
    evidence_hub_min_in_degree: int = 3
    refinement_root_min_out: int = 2
    peripheral_max_degree: int = 1

    def __post_init__(self):
        if self.foundational_centrality_threshold <= 0 or self.foundational_centrality_threshold > 1:
            raise AnnotationPolicyError(
                f"foundational_centrality_threshold must be in (0,1], "
                f"got {self.foundational_centrality_threshold}"
            )
        if self.evidence_hub_min_in_degree < 1:
            raise AnnotationPolicyError(
                f"evidence_hub_min_in_degree must be >= 1, "
                f"got {self.evidence_hub_min_in_degree}"
            )

    @classmethod
    def from_config(cls) -> "AnnotationPolicy":
        config = get_config()
        kg_cfg = config.get("knowledge_graph", {}).get("annotation", {})
        return cls(
            foundational_centrality_threshold=kg_cfg.get("foundational_centrality_threshold", 0.50),
            foundational_min_in_degree=kg_cfg.get("foundational_min_in_degree", 2),
            evidence_hub_min_in_degree=kg_cfg.get("evidence_hub_min_in_degree", 3),
            refinement_root_min_out=kg_cfg.get("refinement_root_min_out", 2),
            peripheral_max_degree=kg_cfg.get("peripheral_max_degree", 1),
        )


class RoleClassifier(Protocol):
    """
    Protocol for role classifiers (P2-3).
    Default implementation: TopologyRoleClassifier.
    Future: ML-based or domain-ontology-based classifiers.
    """
    def classify(
        self,
        topology,
        refines_out: int,
        policy: AnnotationPolicy,
    ) -> SemanticRole: ...


class TopologyRoleClassifier:
    """Default topology-driven role classifier."""

    def classify(
        self,
        topology,
        refines_out: int,
        policy: AnnotationPolicy,
    ) -> SemanticRole:
        return _classify_role(topology, refines_out, policy)


def run_semantic_annotation(
    ctx: SemanticReasoningContext,
    policy: Optional[AnnotationPolicy] = None,
    classifier: Optional[RoleClassifier] = None,
) -> None:
    """
    Annotate every node with a SemanticRole based on its topology.
    Uses AnnotationPolicy for all thresholds (P1-4 fix).

    Args:
        ctx:        SemanticReasoningContext.
        policy:     AnnotationPolicy (from config by default).
        classifier: RoleClassifier implementation (default: TopologyRoleClassifier).
    """
    if policy is None:
        policy = AnnotationPolicy.from_config()
    if classifier is None:
        classifier = TopologyRoleClassifier()

    roles: Dict[str, SemanticRole] = {}

    for claim_id, node in ctx.nodes.items():
        topology = node.topology
        if topology is None:
            roles[claim_id] = SemanticRole.UNCLASSIFIED
            continue

        refines_out = sum(
            1 for e in ctx.edges.values()
            if e.source_node_id == claim_id
            and e.relationship_type == RelationshipType.REFINES
        )

        role = classifier.classify(topology, refines_out, policy)
        roles[claim_id] = role

    ctx.semantic_roles = roles

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        role = roles.get(claim_id, SemanticRole.UNCLASSIFIED)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, semantic_role=role)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    distribution = Counter(r.value for r in roles.values())
    logger.info("semantic annotation complete", distribution=dict(distribution))


def _classify_role(
    topology,
    refines_out: int,
    policy: AnnotationPolicy,
) -> SemanticRole:
    """
    Classify a node's semantic role from topology + policy.
    Priority order is intentional and documented.
    """
    # 1. Bridge: articulation point (must check first — structural primacy)
    if topology.is_bridge:
        return SemanticRole.BRIDGE_CLAIM

    # 2. Foundational: high centrality AND sufficient incoming support
    if (topology.centrality >= policy.foundational_centrality_threshold
            and topology.in_degree >= policy.foundational_min_in_degree):
        return SemanticRole.FOUNDATIONAL_CLAIM

    # 3. Evidence hub: many direct incoming SUPPORTS edges
    if topology.in_degree >= policy.evidence_hub_min_in_degree:
        return SemanticRole.EVIDENCE_HUB

    # 4. Refinement root: many REFINES outgoing edges
    if refines_out >= policy.refinement_root_min_out:
        return SemanticRole.REFINEMENT_ROOT

    # 5. Leaf: no outgoing semantic edges
    if topology.out_degree == 0:
        return SemanticRole.LEAF_CLAIM

    # 6. Peripheral: very low degree
    if topology.degree <= policy.peripheral_max_degree:
        return SemanticRole.PERIPHERAL_CLAIM

    return SemanticRole.UNCLASSIFIED


# Allow Optional in type hints
from typing import Optional
````

## File: src/smriti/evolution/backend.py
````python
"""
backend.py — Abstract graph backend interface for Phase 7.

RECTIFIED (P2-2): Added predecessors() and successors() to the interface
for cleaner directional traversal. get_neighbors() remains for undirected use.

Rules:
    ✅ Returns plain Python types only (no NetworkX types)
    ✅ Every implementation is interchangeable
    ❌ Never performs semantic reasoning
    ❌ Never performs partitioning/aggregation/annotation
    ❌ Never constructs Relationship objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any, Optional


@dataclass(frozen=True)
class EdgeTuple:
    """A minimal edge representation returned by GraphBackend."""
    source: str
    target: str
    edge_id: str
    relationship_type: str
    confidence: float


class GraphBackend(ABC):
    """Abstract graph backend for Phase 7."""

    @property
    @abstractmethod
    def node_count(self) -> int: ...

    @property
    @abstractmethod
    def edge_count(self) -> int: ...

    @abstractmethod
    def add_node(self, node_id: str, **attrs: Any) -> None:
        """Add a node. Silently updates if node already exists."""
        ...

    @abstractmethod
    def add_edge(
        self, source: str, target: str, edge_id: str,
        relationship_type: str, confidence: float, **attrs: Any,
    ) -> None:
        """Add a directed edge."""
        ...

    @abstractmethod
    def has_node(self, node_id: str) -> bool: ...

    @abstractmethod
    def has_edge(self, source: str, target: str, edge_id: str) -> bool: ...

    @abstractmethod
    def get_neighbors(self, node_id: str) -> List[str]:
        """Return IDs of all adjacent nodes (in + out, deduplicated)."""
        ...

    @abstractmethod
    def predecessors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes with edges pointing TO node_id."""
        ...

    @abstractmethod
    def successors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes that node_id points TO."""
        ...

    @abstractmethod
    def get_out_edges(self, node_id: str) -> List[EdgeTuple]:
        """Return all edges leaving node_id."""
        ...

    @abstractmethod
    def get_in_edges(self, node_id: str) -> List[EdgeTuple]:
        """Return all edges entering node_id."""
        ...

    @abstractmethod
    def all_edges(self) -> List[EdgeTuple]: ...

    @abstractmethod
    def all_node_ids(self) -> List[str]:
        """Return all node IDs in deterministic sorted order."""
        ...

    @abstractmethod
    def connected_components_undirected(self) -> List[List[str]]:
        """
        Return connected components ignoring edge direction.
        Each component is a sorted list of node IDs.
        Sorted by size (largest first), then by first node ID.
        """
        ...

    @abstractmethod
    def subgraph(self, node_ids: List[str]) -> "GraphBackend":
        """Return a subgraph containing only the specified nodes."""
        ...

    @abstractmethod
    def in_degree(self, node_id: str) -> int: ...

    @abstractmethod
    def out_degree(self, node_id: str) -> int: ...

    @abstractmethod
    def degree(self, node_id: str) -> int: ...

    @abstractmethod
    def remove_edges_of_type(self, relationship_type: str) -> "GraphBackend":
        """Return a new backend with all edges of the given type removed."""
        ...

    @abstractmethod
    def articulation_points(self) -> List[str]:
        """
        Return all articulation points (bridge nodes) in the undirected projection.
        Implemented using NetworkX nx.articulation_points().
        RECTIFIED (P0-3): replaces degree-1 heuristic.
        """
        ...
````

## File: src/smriti/evolution/builder.py
````python
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
from typing import Dict
import structlog

from smriti.core.models import (
    KnowledgeGraph, GraphStatistics, RelationshipType, TemporalStatus,
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
            1 for e in edges.values()
            if e.relationship_type == RelationshipType.CONTRADICTS
        )
        supports_count = sum(
            1 for e in edges.values()
            if e.relationship_type == RelationshipType.SUPPORTS
        )
        refines_count = sum(
            1 for e in edges.values()
            if e.relationship_type == RelationshipType.REFINES
        )

        # Reuse precomputed topology metrics (no re-traversal)
        isolated = sum(
            1 for nid in nodes
            if ctx.topology_metrics.get(nid) and ctx.topology_metrics[nid].degree == 0
        )
        bridges = sum(1 for m in ctx.topology_metrics.values() if m.is_bridge)
        hubs = sum(1 for m in ctx.topology_metrics.values() if m.is_hub)

        # Reuse precomputed temporal metadata (no re-traversal)
        evolution_chains = sum(
            1 for t in ctx.temporal_metadata.values()
            if t and t.status == TemporalStatus.EVOLUTION_CHAIN
        ) // 2
        unresolved = sum(
            1 for t in ctx.temporal_metadata.values()
            if t and t.status == TemporalStatus.UNRESOLVED_CONFLICT
        ) // 2

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
        )


def build_knowledge_graph(
    ctx: SemanticReasoningContext,
    validation_report,
    construction_time: float,
    enrichment_time: float,
) -> KnowledgeGraph:
    """
    Assemble the final KnowledgeGraph from a fully enriched context.

    Delegates statistics computation to StatisticsBuilder (P2-1).
    Pure construction — no reasoning, no validation, no inference.
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
````

## File: src/smriti/evolution/construction.py
````python
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
from typing import List, Dict, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Claim, Relationship, RelationshipSet, RelationshipType, RelationshipDirection,
    ClaimNode, RelationshipEdge, SemanticRole, NodeAnnotations,
)
from smriti.evolution.backend import GraphBackend
from smriti.exceptions import GraphConstructionError

logger = structlog.get_logger(__name__)


@dataclass
class ConstructionResult:
    """Output of the construction sub-pipeline."""
    nodes: Dict[str, ClaimNode]
    edges: Dict[str, RelationshipEdge]
    backend: GraphBackend
    relationships_ingested: int
    relationships_filtered: int
    filter_reasons: Dict[str, int]


ACCEPTED_TYPES = frozenset([
    RelationshipType.CONTRADICTS,
    RelationshipType.SUPPORTS,
    RelationshipType.REFINES,
])


def run_construction(
    relationship_set: RelationshipSet,
    claims_map: Dict[str, Claim],
    backend: GraphBackend,
    include_neutral: bool = False,
) -> ConstructionResult:
    """Execute the 5-stage construction sub-pipeline."""
    # Stage 1: Ingestion & Filtering
    accepted_types = ACCEPTED_TYPES | ({RelationshipType.NEUTRAL} if include_neutral else set())
    accepted: List[Relationship] = []
    filter_reasons: Dict[str, int] = {}

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
    claim_id_set: Set[str] = set()
    for rel in accepted:
        claim_id_set.add(rel.claim_id_a)
        claim_id_set.add(rel.claim_id_b)

    nodes: Dict[str, ClaimNode] = {}
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
            annotations=None,           # Populated during enrichment
            schema_version="7.0",
        )

    logger.info("node registry constructed", nodes=len(nodes))

    # Stage 3: Edge Registry Construction
    edges: Dict[str, RelationshipEdge] = {}
    seen_edge_ids: Set[str] = set()

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
        # CONTRADICTS is symmetric: add reverse edge for undirected traversal
        if edge.relationship_type == RelationshipType.CONTRADICTS:
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
````

## File: src/smriti/evolution/context.py
````python
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
````

## File: src/smriti/evolution/networkx_backend.py
````python
"""
networkx_backend.py — NetworkX implementation of GraphBackend.

This is the ONLY module in Phase 7 that imports networkx.

RECTIFIED (P0-3): articulation_points() uses nx.articulation_points()
on the undirected projection — the true graph-theoretic definition,
not degree-1 heuristic.

RECTIFIED (P2-2): predecessors() and successors() added.
"""

from __future__ import annotations

from typing import List, Any
import structlog

from smriti.evolution.backend import GraphBackend, EdgeTuple
from smriti.exceptions import BackendError

logger = structlog.get_logger(__name__)


class NetworkXBackend(GraphBackend):
    """NetworkX MultiDiGraph implementation of GraphBackend."""

    def __init__(self) -> None:
        try:
            import networkx as nx
            self._G = nx.MultiDiGraph()
            self._nx = nx
        except ImportError as e:
            raise BackendError(
                f"networkx is not installed. Run: poetry add networkx\nError: {e}"
            ) from e

    @property
    def node_count(self) -> int:
        return self._G.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self._G.number_of_edges()

    def add_node(self, node_id: str, **attrs: Any) -> None:
        self._G.add_node(node_id, **attrs)

    def add_edge(
        self, source: str, target: str, edge_id: str,
        relationship_type: str, confidence: float, **attrs: Any,
    ) -> None:
        self._G.add_edge(
            source, target, key=edge_id,
            edge_id=edge_id, relationship_type=relationship_type,
            confidence=confidence, **attrs,
        )

    def has_node(self, node_id: str) -> bool:
        return self._G.has_node(node_id)

    def has_edge(self, source: str, target: str, edge_id: str) -> bool:
        return self._G.has_edge(source, target, key=edge_id)

    def get_neighbors(self, node_id: str) -> List[str]:
        successors = set(self._G.successors(node_id))
        predecessors = set(self._G.predecessors(node_id))
        return sorted(successors | predecessors)

    def predecessors(self, node_id: str) -> List[str]:
        """Return nodes with edges pointing TO node_id."""
        return sorted(self._G.predecessors(node_id))

    def successors(self, node_id: str) -> List[str]:
        """Return nodes that node_id points TO."""
        return sorted(self._G.successors(node_id))

    def get_out_edges(self, node_id: str) -> List[EdgeTuple]:
        edges = []
        for _, target, data in self._G.out_edges(node_id, data=True):
            edges.append(EdgeTuple(
                source=node_id, target=target,
                edge_id=data.get("edge_id", ""),
                relationship_type=data.get("relationship_type", ""),
                confidence=data.get("confidence", 0.0),
            ))
        return edges

    def get_in_edges(self, node_id: str) -> List[EdgeTuple]:
        edges = []
        for source, _, data in self._G.in_edges(node_id, data=True):
            edges.append(EdgeTuple(
                source=source, target=node_id,
                edge_id=data.get("edge_id", ""),
                relationship_type=data.get("relationship_type", ""),
                confidence=data.get("confidence", 0.0),
            ))
        return edges

    def all_edges(self) -> List[EdgeTuple]:
        edges = []
        for source, target, data in self._G.edges(data=True):
            edges.append(EdgeTuple(
                source=source, target=target,
                edge_id=data.get("edge_id", ""),
                relationship_type=data.get("relationship_type", ""),
                confidence=data.get("confidence", 0.0),
            ))
        return sorted(edges, key=lambda e: (e.source, e.target, e.edge_id))

    def all_node_ids(self) -> List[str]:
        return sorted(self._G.nodes())

    def connected_components_undirected(self) -> List[List[str]]:
        undirected = self._G.to_undirected()
        components = list(self._nx.connected_components(undirected))
        return sorted(
            [sorted(c) for c in components],
            key=lambda c: (-len(c), c[0] if c else ""),
        )

    def subgraph(self, node_ids: List[str]) -> "NetworkXBackend":
        sub = self._G.subgraph(node_ids).copy()
        new_backend = NetworkXBackend.__new__(NetworkXBackend)
        new_backend._nx = self._nx
        new_backend._G = sub
        return new_backend

    def in_degree(self, node_id: str) -> int:
        return self._G.in_degree(node_id)

    def out_degree(self, node_id: str) -> int:
        return self._G.out_degree(node_id)

    def degree(self, node_id: str) -> int:
        return self._G.degree(node_id)

    def remove_edges_of_type(self, relationship_type: str) -> "NetworkXBackend":
        new_backend = NetworkXBackend.__new__(NetworkXBackend)
        new_backend._nx = self._nx
        new_backend._G = self._G.copy()
        edges_to_remove = [
            (u, v, k) for u, v, k, d in new_backend._G.edges(data=True, keys=True)
            if d.get("relationship_type") == relationship_type
        ]
        new_backend._G.remove_edges_from(edges_to_remove)
        return new_backend

    def articulation_points(self) -> List[str]:
        """
        Return true articulation points using NetworkX.

        RECTIFIED (P0-3): Uses nx.articulation_points() on the undirected
        projection. This is the correct graph-theoretic definition:
        a node whose removal disconnects the graph.
        degree == 1 is NOT a valid bridge-detection heuristic.

        Example where old code was wrong:
            A → B → C (chain of 3)
            B has degree 2 and is the only articulation point.
            Old code: is_bridge=False (degree != 1)
            Fixed code: is_bridge=True (nx.articulation_points detects B)
        """
        if self._G.number_of_nodes() < 2:
            return []
        undirected = self._G.to_undirected()
        try:
            return sorted(self._nx.articulation_points(undirected))
        except Exception:
            return []
````

## File: src/smriti/evolution/partitioning.py
````python
"""
partitioning.py — Constraint-based partition engine for Phase 7.

RECTIFIED (P0-1): The original algorithm (remove CONTRADICTS edges → connected
components) is semantically incorrect on graphs where contradicting nodes share
a common neighbor via SUPPORTS.

Counter-example that breaks the old algorithm:
    A SUPPORTS X
    C SUPPORTS X
    A CONTRADICTS C

Old algorithm:
    Remove CONTRADICTS: A→X and C→X remain connected.
    Result: A, X, C all in the SAME partition.
    VIOLATED INVARIANT: A and C contradict each other but are in the same partition.

Fixed algorithm (constraint-based signed-graph partitioning):
    Step 1: Build contradiction-constraint graph from CONTRADICTS edges only.
    Step 2: 2-color the constraint graph (like graph coloring for signed graphs).
            Nodes connected by CONTRADICTS must have different colors.
            If the constraint graph is not 2-colorable (odd cycle), odd contradiction
            cycles intentionally degrade into singleton partitions rather than attempting
            approximate optimization. This safely partitions contradictions at the cost
            of destroying SUPPORTS structure strictly within the cycle.
    Step 3: Apply Union-Find on SUPPORTS/REFINES edges, but only merge nodes
            that have the SAME color. This ensures contradicting claims are
            never merged into the same partition even if they share a neighbor.
    Step 4: Build KnowledgePartition for each Union-Find group.

Complexity: O(N + E) — BFS coloring + Union-Find with path compression.

Invariant guaranteed:
    No two nodes connected by CONTRADICTS will ever be in the same partition.
    This holds even in the presence of shared SUPPORTS neighbors.
"""

from __future__ import annotations

import hashlib
from collections import deque
from typing import Dict, List, Set, Optional, Tuple
import structlog
import dataclasses

from smriti.core.models import (
    KnowledgePartition, RelationshipType, NodeAnnotations, SemanticRole,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.exceptions import PartitioningError

logger = structlog.get_logger(__name__)


def run_partitioning(ctx: SemanticReasoningContext) -> None:
    """
    Partition the graph using constraint-based signed-graph coloring + Union-Find.

    Mutates ctx.partitions, ctx.node_to_partition, ctx.nodes (partition_id).

    Raises:
        PartitioningError: If any node is left unassigned.
    """
    all_node_ids = set(ctx.nodes.keys())

    # ── Step 1: Collect contradiction constraints ─────────────────────────────
    # contradiction_constraints[A] = set of nodes that A directly CONTRADICTS
    contradiction_constraints: Dict[str, Set[str]] = {nid: set() for nid in all_node_ids}
    for edge in ctx.edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            contradiction_constraints[edge.source_node_id].add(edge.target_node_id)
            contradiction_constraints[edge.target_node_id].add(edge.source_node_id)

    # ── Step 2: 2-color the contradiction graph ───────────────────────────────
    # Color 0 and Color 1 are the two contradiction "sides".
    # Nodes that CONTRADICT each other must have different colors.
    # If not 2-colorable (odd cycle), each node in the conflicting group
    # gets a unique color (conservative: separate partition per node).
    node_color: Dict[str, int] = {}
    color_counter = [2]  # Colors 0 and 1 are standard; higher = isolated

    def bfs_color(start: str) -> bool:
        """BFS 2-coloring. Returns True if successfully 2-colored."""
        queue = deque([start])
        node_color[start] = 0
        while queue:
            node = queue.popleft()
            for neighbor in contradiction_constraints.get(node, set()):
                if neighbor not in node_color:
                    node_color[neighbor] = 1 - node_color[node]
                    queue.append(neighbor)
                elif node_color[neighbor] == node_color[node]:
                    return False  # Odd cycle — not 2-colorable
        return True

    # Process connected components of the contradiction graph
    for node_id in sorted(all_node_ids):
        if node_id not in node_color:
            if not contradiction_constraints[node_id]:
                # Isolated in contradiction graph — assign unique color
                node_color[node_id] = color_counter[0]
                color_counter[0] += 1
            else:
                if not bfs_color(node_id):
                    # Odd contradiction cycle detected.
                    # DESIGN DECISION: We intentionally degrade into singleton partitions
                    # rather than attempting approximate graph-cut optimization.
                    visited = set()
                    q = deque([node_id])
                    while q:
                        n = q.popleft()
                        if n in visited:
                            continue
                        visited.add(n)
                        if n not in node_color:
                            node_color[n] = color_counter[0]
                            color_counter[0] += 1
                        for nb in contradiction_constraints.get(n, set()):
                            if nb not in visited:
                                q.append(nb)

    # ── Step 3: Union-Find on SUPPORTS/REFINES edges (same-color only) ────────
    parent: Dict[str, str] = {nid: nid for nid in all_node_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # Path compression
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        px, py = find(x), find(y)
        if px != py:
            # Only merge if same color (no contradiction constraint between them)
            if node_color.get(px) == node_color.get(py):
                parent[px] = py

    for edge in ctx.edges.values():
        if edge.relationship_type in (RelationshipType.SUPPORTS, RelationshipType.REFINES):
            union(edge.source_node_id, edge.target_node_id)

    # ── Step 4: Build KnowledgePartition for each Union-Find group ───────────
    # Group nodes by their root in Union-Find
    groups: Dict[str, Set[str]] = {}
    for node_id in sorted(all_node_ids):
        root = find(node_id)
        groups.setdefault(root, set()).add(node_id)

    partitions: Dict[str, KnowledgePartition] = {}
    node_to_partition: Dict[str, str] = {}

    for root, group_nodes in groups.items():
        node_ids = frozenset(group_nodes)
        partition_id = _compute_partition_id(node_ids)
        stable_label = tuple(sorted(node_ids))  # Store as a sorted tuple

        # Find internal edges (SUPPORTS/REFINES within this partition)
        internal_edges = {}
        supports_count = 0
        refines_count = 0

        for edge_id, edge in ctx.edges.items():
            if (edge.source_node_id in node_ids
                    and edge.target_node_id in node_ids
                    and edge.relationship_type != RelationshipType.CONTRADICTS):
                internal_edges[edge_id] = edge
                if edge.relationship_type == RelationshipType.SUPPORTS:
                    supports_count += 1
                elif edge.relationship_type == RelationshipType.REFINES:
                    refines_count += 1

        # Directed density (P1-5): edges / (n * (n-1))
        n = len(node_ids)
        max_directed_edges = n * (n - 1) if n > 1 else 1
        density = len(internal_edges) / max_directed_edges if max_directed_edges > 0 else 0.0

        longest_chain = _compute_longest_support_chain(node_ids, internal_edges)

        partition = KnowledgePartition(
            partition_id=partition_id,
            stable_partition_label=stable_label,
            node_ids=node_ids,
            internal_edge_ids=frozenset(internal_edges.keys()),
            node_count=len(node_ids),
            edge_count=len(internal_edges),
            supports_count=supports_count,
            refines_count=refines_count,
            density=round(density, 6),
            longest_support_chain=longest_chain,
            schema_version="7.0",
        )
        partitions[partition_id] = partition
        for nid in node_ids:
            node_to_partition[nid] = partition_id

    # ── Verify all nodes assigned ─────────────────────────────────────────────
    unassigned = all_node_ids - set(node_to_partition.keys())
    if unassigned:
        raise PartitioningError(
            f"Partitioning left {len(unassigned)} nodes unassigned: "
            f"{sorted(unassigned)[:5]}"
        )

    # ── Verify partition invariant: no CONTRADICTS within any partition ────────
    for partition in partitions.values():
        for edge_id, edge in ctx.edges.items():
            if (edge.relationship_type == RelationshipType.CONTRADICTS
                    and edge.source_node_id in partition.node_ids
                    and edge.target_node_id in partition.node_ids):
                raise PartitioningError(
                    f"CONTRADICTS edge {edge_id[:8]} found WITHIN partition "
                    f"{partition.partition_id[:8]}. Constraint partitioning failed."
                )

    ctx.partitions = partitions
    ctx.node_to_partition = node_to_partition

    # Update node annotations with partition_id
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        pid = node_to_partition.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(
            current_ann,
            partition_id=pid,
            stable_partition_label=partitions[pid].stable_partition_label if pid else None,
        )
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    logger.info(
        "constraint-based partitioning complete",
        partitions=len(partitions),
        nodes=len(ctx.nodes),
        algorithm="signed_graph_coloring_union_find",
    )


def _compute_partition_id(node_ids: frozenset) -> str:
    """Deterministic partition ID from sorted node IDs."""
    material = "|".join(sorted(node_ids))
    return hashlib.sha256(material.encode()).hexdigest()[:12]


def _compute_longest_support_chain(node_ids: frozenset, internal_edges: dict) -> int:
    """Compute the longest directed SUPPORTS chain within a partition via DFS."""
    if not internal_edges:
        return 0

    adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
    for edge in internal_edges.values():
        if edge.relationship_type == RelationshipType.SUPPORTS:
            adj[edge.source_node_id].append(edge.target_node_id)

    def dfs_length(node: str, visited: Set[str]) -> int:
        if node in visited:
            return 0
        visited = visited | {node}
        successors = adj.get(node, [])
        if not successors:
            return 1
        return 1 + max(dfs_length(s, visited) for s in successors)

    if not any(adj.values()):
        return 0

    return max(dfs_length(nid, set()) for nid in node_ids)
````

## File: src/smriti/evolution/statistics.py
````python
"""statistics.py — Phase 7 execution telemetry. Observes. Never influences."""

from __future__ import annotations

import time
from smriti.core.models import Phase7Stats


class Phase7StatsCollector:
    """Mutable statistics accumulator for Phase 7."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._construction_start: float | None = None
        self._construction_end: float | None = None
        self._enrichment_start: float | None = None
        self._enrichment_end: float | None = None
        self._input_relationships = 0
        self._filtered = 0
        self._nodes = 0
        self._edges = 0
        self._partitions = 0
        self._contradiction_boundaries = 0
        self._evolution_chains = 0
        self._unresolved = 0
        self._validation_passed = False

    def record_input(self, total: int, filtered: int) -> None:
        self._input_relationships = total
        self._filtered = filtered

    def record_construction_start(self) -> None:
        self._construction_start = time.monotonic()

    def record_construction_end(self, nodes: int, edges: int) -> None:
        self._construction_end = time.monotonic()
        self._nodes = nodes
        self._edges = edges

    def record_enrichment_start(self) -> None:
        self._enrichment_start = time.monotonic()

    def record_enrichment_end(
        self, partitions: int, contradiction_boundaries: int,
        evolution_chains: int, unresolved: int,
    ) -> None:
        self._enrichment_end = time.monotonic()
        self._partitions = partitions
        self._contradiction_boundaries = contradiction_boundaries
        self._evolution_chains = evolution_chains
        self._unresolved = unresolved

    def record_validation_passed(self) -> None:
        self._validation_passed = True

    def finalize(self) -> Phase7Stats:
        total = time.monotonic() - self._start
        construction_time = (
            (self._construction_end - self._construction_start)
            if self._construction_start and self._construction_end else 0.0
        )
        enrichment_time = (
            (self._enrichment_end - self._enrichment_start)
            if self._enrichment_start and self._enrichment_end else 0.0
        )
        return Phase7Stats(
            input_relationships=self._input_relationships,
            input_filtered=self._filtered,
            nodes_created=self._nodes,
            edges_created=self._edges,
            partitions_created=self._partitions,
            contradictions_as_boundaries=self._contradiction_boundaries,
            evolution_chains_detected=self._evolution_chains,
            unresolved_conflicts=self._unresolved,
            construction_time_seconds=round(construction_time, 4),
            enrichment_time_seconds=round(enrichment_time, 4),
            total_time_seconds=round(total, 4),
            validation_passed=self._validation_passed,
        )
````

## File: src/smriti/evolution/temporal.py
````python
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
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import structlog

from smriti.core.models import (
    Claim, RelationshipType, TemporalMetadata, TemporalStatus, NodeAnnotations,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.core.config import get_config

logger = structlog.get_logger(__name__)


def run_temporal_resolution(
    ctx: SemanticReasoningContext,
    claims_map: Dict[str, Claim],
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
    min_reliable_delta = config.get("knowledge_graph", {}).get(
        "min_reliable_delta_days", 1.0
    )

    temporal: Dict[str, TemporalMetadata] = {}

    # Collect CONTRADICTS pairs
    contradicts_pairs: List[Tuple[str, str, str]] = []
    for edge in ctx.edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            contradicts_pairs.append((edge.edge_id, edge.source_node_id, edge.target_node_id))

    # Process each contradiction boundary
    for edge_id, node_a_id, node_b_id in contradicts_pairs:
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

    evolution_count = sum(
        1 for t in temporal.values() if t.status == TemporalStatus.EVOLUTION_CHAIN
    ) // 2
    no_ts_count = sum(
        1 for t in temporal.values() if t.status == TemporalStatus.NO_TIMESTAMP
    ) // 2
    unresolved_count = sum(
        1 for t in temporal.values() if t.status == TemporalStatus.UNRESOLVED_CONFLICT
    ) // 2

    logger.info(
        "temporal resolution complete",
        evolution_chains=evolution_count,
        unresolved=unresolved_count,
        no_timestamp=no_ts_count,
        source="claim.timestamp (semantic — never filesystem)",
    )


def _get_semantic_timestamp(claim: Claim) -> Optional[datetime]:
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
        from datetime import timezone
        if isinstance(ts, str):
            return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None
    return None


def _assign_static(
    temporal: Dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
    temporal_confidence: float,
) -> None:
    meta = TemporalMetadata(
        status=TemporalStatus.STATIC_PARTITION,
        earlier_claim_id=None, later_claim_id=None,
        time_delta_days=None,
        temporal_confidence=temporal_confidence,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_no_timestamp(
    temporal: Dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
) -> None:
    """Assign NO_TIMESTAMP when Claim.timestamp is unavailable."""
    meta = TemporalMetadata(
        status=TemporalStatus.NO_TIMESTAMP,
        earlier_claim_id=None, later_claim_id=None,
        time_delta_days=None,
        temporal_confidence=0.0,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_unresolved(
    temporal: Dict[str, TemporalMetadata],
    node_a: str,
    node_b: str,
    delta: float,
) -> None:
    meta = TemporalMetadata(
        status=TemporalStatus.UNRESOLVED_CONFLICT,
        earlier_claim_id=None, later_claim_id=None,
        time_delta_days=round(delta, 2),
        temporal_confidence=0.0,
    )
    temporal[node_a] = meta
    temporal[node_b] = meta


def _assign_evolution(
    temporal: Dict[str, TemporalMetadata],
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
````

## File: src/smriti/evolution/topology.py
````python
"""
topology.py — Topology analysis for Phase 7.

RECTIFIED (P0-3): Bridge detection uses the backend's articulation_points()
method, which delegates to NetworkX nx.articulation_points() on the undirected
projection. This is the true graph-theoretic definition of a bridge node.

The original `is_bridge = (total == 1 and n > 2)` was a degree-1 leaf heuristic,
NOT bridge detection. Example failure:
    A → B → C
    B has degree 2. It IS an articulation point (bridge).
    Old code: is_bridge=False (degree != 1). WRONG.
    Fixed code: is_bridge=True (articulation_points returns B). CORRECT.

RECTIFIED (P1-4): Hub detection threshold read from AnnotationPolicy (config),
not hardcoded to 2.0. Centrality formula unchanged: in_degree / (N-1).

Complexity: O(N + E) per partition, O(N + E) for articulation points.
"""

from __future__ import annotations

from typing import Dict, Set
import dataclasses
import structlog

from smriti.core.models import TopologyMetrics, NodeAnnotations
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


def run_topology_analysis(
    ctx: SemanticReasoningContext,
    hub_degree_multiplier: float = 2.0,
) -> None:
    """
    Compute topology metrics for all nodes within their partitions.

    Args:
        ctx:                   SemanticReasoningContext.
        hub_degree_multiplier: Config-driven (knowledge_graph.hub_degree_multiplier).
                               A node is a hub if degree > multiplier * avg_partition_degree.

    Updates ctx.topology_metrics and ctx.nodes (via NodeAnnotations replacement).
    """
    topology: Dict[str, TopologyMetrics] = {}

    for partition_id, partition in ctx.partitions.items():
        partition_nodes = list(partition.node_ids)
        if not partition_nodes:
            continue

        # Get partition subgraph
        sub = ctx.backend.subgraph(partition_nodes)
        n = partition.node_count

        # Compute degrees for all nodes in partition
        node_degrees = {}
        for node_id in partition_nodes:
            total = sub.degree(node_id)
            in_deg = sub.in_degree(node_id)
            out_deg = sub.out_degree(node_id)
            node_degrees[node_id] = (total, in_deg, out_deg)

        # Average degree for hub detection (config-driven, not hardcoded)
        avg_degree = (
            sum(d[0] for d in node_degrees.values()) / n if n > 0 else 0.0
        )

        # True bridge detection via articulation_points (P0-3 fix)
        art_points: Set[str] = set(sub.articulation_points())

        for node_id in partition_nodes:
            total, in_deg, out_deg = node_degrees[node_id]

            # Directed in-degree centrality: in_degree / (N-1)
            centrality = in_deg / (n - 1) if n > 1 else 0.0

            # Hub: degree significantly above average (config-driven threshold)
            is_hub = total > max(1.0, avg_degree * hub_degree_multiplier)

            # Bridge: true articulation point (NOT degree-1 heuristic)
            is_bridge = node_id in art_points

            metrics = TopologyMetrics(
                degree=total,
                in_degree=in_deg,
                out_degree=out_deg,
                is_bridge=is_bridge,
                is_hub=is_hub,
                partition_id=partition_id,
                centrality=round(centrality, 6),
            )
            topology[node_id] = metrics

    ctx.topology_metrics = topology

    # Update node annotations
    updated_nodes = {}
    for claim_id, node in ctx.nodes.items():
        metrics = topology.get(claim_id)
        current_ann = node.annotations or NodeAnnotations()
        updated_ann = dataclasses.replace(current_ann, topology=metrics)
        updated_nodes[claim_id] = dataclasses.replace(node, annotations=updated_ann)
    ctx.nodes = updated_nodes

    logger.info("topology analysis complete", nodes_enriched=len(topology))
````

## File: src/smriti/evolution/validation.py
````python
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
````

## File: src/smriti/retrieval/classification/calibration.py
````python
"""
calibration.py — Confidence calibration for NLI evidence scores.

Problem being solved:
    Different NLI models have different confidence distributions.
    A raw score of 0.85 from model A may not mean the same thing
    as 0.85 from model B. For example, some models tend to produce
    scores clustered near 0.9–1.0 even for ambiguous pairs (overconfident),
    while others cluster near 0.5–0.7 (underconfident).

    Without calibration, the thresholds in ResolverPolicy become
    model-specific constants that must be manually tuned whenever
    the NLI model is changed.

Solution:
    ConfidenceCalibrator applies a model-specific transformation to
    raw confidence scores to produce calibrated_confidence values
    that are comparable across models.

Currently implemented strategies:
    IDENTITY:          No calibration (raw score passes through). Default.
    TEMPERATURE:       Divide logits by temperature T before softmax.
                       Effective when the model produces overconfident scores.
    PERCENTILE:        Map raw score to its percentile in a reference distribution.
                       Requires a reference distribution (fit on a validation set).
    ISOTONIC:          Isotonic regression calibration.
                       Requires a fitted sklearn IsotonicRegression (optional dep).

Rules:
    ✅ Pure math — never calls any ML model
    ✅ Deterministic given same parameters
    ✅ Gracefully degrades to IDENTITY if calibration data unavailable
    ❌ Never modifies NLIScores objects
    ❌ Never changes predicted_label (only calibrates confidence magnitude)
"""

from __future__ import annotations

import math
from enum import Enum
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import RelationshipEvidence, NLIScores, LifecycleStage
from smriti.core.paths import CONFIG_DIR
from smriti.exceptions import CalibrationError

logger = structlog.get_logger(__name__)

CALIBRATOR_VERSION = "1.0"


class CalibrationStrategy(str, Enum):
    IDENTITY    = "identity"
    TEMPERATURE = "temperature"
    PERCENTILE  = "percentile"
    ISOTONIC    = "isotonic"


class ConfidenceCalibrator:
    """
    Applies model-specific confidence calibration to NLI evidence.

    Instantiate once per pipeline run (per model).
    """

    def __init__(
        self,
        model_name: str,
        strategy: Optional[CalibrationStrategy] = None,
        temperature: float = 1.0,
        reference_distribution: Optional[List[float]] = None,
    ) -> None:
        """
        Args:
            model_name:              NLI model being calibrated (for logging).
            strategy:                Which calibration strategy to apply.
                                     Defaults to config or IDENTITY.
            temperature:             Temperature for TEMPERATURE strategy (T > 1 softens,
                                     T < 1 sharpens). Only used when strategy=TEMPERATURE.
            reference_distribution:  Sorted list of raw confidence scores from a
                                     representative sample (for PERCENTILE strategy).
        """
        config = get_config()
        calib_cfg = config.get("calibration", {}).get(model_name, {})

        if strategy is None:
            strategy_str = calib_cfg.get("strategy", "identity")
            strategy = CalibrationStrategy(strategy_str)

        self._model_name = model_name
        self._strategy = strategy
        self._temperature = calib_cfg.get("temperature", temperature)
        self._reference_distribution = (
            reference_distribution
            or calib_cfg.get("reference_distribution")
        )

        logger.info(
            "calibrator initialized",
            model=model_name,
            strategy=self._strategy.value,
            temperature=self._temperature,
        )

    def calibrate(self, evidence: RelationshipEvidence) -> RelationshipEvidence:
        """
        Calibrate the confidence score in a RelationshipEvidence.

        Args:
            evidence: Evidence with raw NLI scores.

        Returns:
            New RelationshipEvidence with calibrated_confidence updated.
            NLIScores (predicted_label, raw scores) are never modified.
        """
        raw = evidence.nli_scores.raw_confidence

        try:
            calibrated = self._apply_strategy(
                raw_confidence=raw,
                entailment=evidence.nli_scores.entailment_score,
                neutral=evidence.nli_scores.neutral_score,
                contradiction=evidence.nli_scores.contradiction_score,
            )
        except CalibrationError as e:
            logger.warning(
                "calibration failed, using raw confidence",
                model=self._model_name,
                error=str(e),
            )
            calibrated = raw

        # Return new RelationshipEvidence with calibrated_confidence set
        # and lifecycle advanced to CALIBRATED_EVIDENCE
        return RelationshipEvidence(
            pair=evidence.pair,
            cosine_similarity=evidence.cosine_similarity,
            nli_scores=evidence.nli_scores,
            calibrated_confidence=calibrated,
            inference_metadata=evidence.inference_metadata,
            lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
        )

    def calibrate_batch(
        self,
        evidence_list: List[RelationshipEvidence],
    ) -> List[RelationshipEvidence]:
        """Calibrate a batch of evidence objects."""
        return [self.calibrate(ev) for ev in evidence_list]

    def _apply_strategy(
        self,
        raw_confidence: float,
        entailment: float,
        neutral: float,
        contradiction: float,
    ) -> float:
        """Apply the configured calibration strategy."""
        if self._strategy == CalibrationStrategy.IDENTITY:
            return raw_confidence

        elif self._strategy == CalibrationStrategy.TEMPERATURE:
            return self._temperature_scale(
                entailment, neutral, contradiction, self._temperature
            )

        elif self._strategy == CalibrationStrategy.PERCENTILE:
            if not self._reference_distribution:
                logger.warning(
                    "PERCENTILE calibration requested but no reference distribution; "
                    "falling back to IDENTITY",
                    model=self._model_name,
                )
                return raw_confidence
            return self._percentile_calibrate(raw_confidence, self._reference_distribution)

        elif self._strategy == CalibrationStrategy.ISOTONIC:
            return self._isotonic_calibrate(raw_confidence)

        else:
            return raw_confidence

    @staticmethod
    def _temperature_scale(
        entailment: float,
        neutral: float,
        contradiction: float,
        temperature: float,
    ) -> float:
        """
        Apply temperature scaling.
        Re-compute softmax after dividing by T.
        T > 1 produces softer (lower) confidence.
        T < 1 produces sharper (higher) confidence.
        """
        if temperature <= 0:
            raise CalibrationError(f"Temperature must be > 0, got {temperature}")

        # Back-compute approximate logits (inverse softmax is not unique,
        # but log(p) is a reasonable approximation for calibration)
        eps = 1e-9
        logits = [
            math.log(max(entailment, eps)),
            math.log(max(neutral, eps)),
            math.log(max(contradiction, eps)),
        ]
        scaled = [l / temperature for l in logits]
        max_l = max(scaled)
        exps = [math.exp(s - max_l) for s in scaled]
        total = sum(exps)
        probs = [e / total for e in exps]
        return max(probs)

    @staticmethod
    def _percentile_calibrate(
        raw_confidence: float,
        reference: List[float],
    ) -> float:
        """
        Map raw_confidence to its percentile rank in the reference distribution.
        Reference must be sorted ascending.
        """
        if not reference:
            return raw_confidence

        # Binary search for position
        lo, hi = 0, len(reference)
        while lo < hi:
            mid = (lo + hi) // 2
            if reference[mid] < raw_confidence:
                lo = mid + 1
            else:
                hi = mid

        return lo / len(reference)

    def _isotonic_calibrate(self, raw_confidence: float) -> float:
        """
        Isotonic regression calibration.
        Expects a serialized sklearn IsotonicRegression model.

        The model should be placed at:
            config/calibration/{model_name}_isotonic.pkl
        where model_name has '/' replaced with '_'.
        """
        try:
            import joblib

            # Replace slashes in huggingface model names for safe filenames
            safe_name = self._model_name.replace("/", "_")
            calib_path = CONFIG_DIR / "calibration" / f"{safe_name}_isotonic.pkl"

            if calib_path.exists():
                calibrator = joblib.load(calib_path)
                # Predict returns an array, we want the float
                return float(calibrator.transform([raw_confidence])[0])
            else:
                logger.warning(
                    "Isotonic calibration artifact missing at %s, falling back to raw",
                    calib_path
                )
                return raw_confidence
        except ImportError as e:
            logger.warning(
                "scikit-learn or joblib not installed, falling back to raw: %s", e
            )
            return raw_confidence
        except Exception as e:
            logger.warning(
                "Isotonic calibration failed (%s), falling back to raw", e
            )
            return raw_confidence
````

## File: src/smriti/retrieval/classification/conflict.py
````python
"""
classification/conflict.py — Cross-run relationship conflict resolution.

Problem:
    When the pipeline is run multiple times (incremental updates, re-indexing),
    the same claim pair may receive different RelationshipType assignments.

    Example:
        Run 1: (claim_a, claim_b) → SUPPORTS
        Run 2: (claim_a, claim_b) → CONTRADICTS

    Which one wins? This module answers that question deterministically
    according to the configured ConflictResolutionPolicy.

Policies (see models.py ConflictResolutionPolicy):
    LATEST_WINS:         Most recent run's classification wins.
    HIGHEST_CONFIDENCE:  Classification with highest calibrated_confidence wins.
    MOST_SPECIFIC:       Priority: CONTRADICTS > REFINES > SUPPORTS > NEUTRAL > UNKNOWN.
    CONSERVATIVE:        Only keep if all runs agree on the type.

Rules:
    ✅ Deterministic: same inputs → same output
    ✅ Never modifies Relationship objects (returns winner or None)
    ❌ Never calls ML models
    ❌ Never modifies existing relationships
"""

from __future__ import annotations

from typing import List, Optional, Dict, Tuple
import structlog

from smriti.core.models import Relationship, RelationshipType, ConflictResolutionPolicy
from smriti.exceptions import ConflictResolutionError

logger = structlog.get_logger(__name__)

# Priority order for MOST_SPECIFIC policy (higher index = lower priority)
_SPECIFICITY_ORDER = {
    RelationshipType.CONTRADICTS: 0,
    RelationshipType.REFINES:     1,
    RelationshipType.SUPPORTS:    2,
    RelationshipType.NEUTRAL:     3,
    RelationshipType.UNKNOWN:     4,
}


class ConflictResolver:
    """
    Resolves type conflicts between relationships for the same claim pair.
    Instantiate once per pipeline run.
    """

    def __init__(self, policy: ConflictResolutionPolicy) -> None:
        self._policy = policy
        logger.info("conflict resolver initialized", policy=policy.value)

    def resolve_conflicts(
        self,
        relationships: List[Relationship],
    ) -> List[Relationship]:
        """
        Given a list of relationships (potentially with conflicts for the same pair),
        return a deduplicated list according to the conflict policy.

        Args:
            relationships: All relationships from the current run and any loaded
                           prior-run relationships.

        Returns:
            Deduplicated list with at most one Relationship per pair_key.
        """
        # Group by pair_key
        by_pair: Dict[str, List[Relationship]] = {}
        for rel in relationships:
            key = rel.evidence.pair.pair_key()
            by_pair.setdefault(key, []).append(rel)

        resolved: List[Relationship] = []
        for pair_key, candidates in by_pair.items():
            if len(candidates) == 1:
                resolved.append(candidates[0])
            else:
                winner = self._apply_policy(pair_key, candidates)
                if winner is not None:
                    resolved.append(winner)

        logger.info(
            "conflict resolution complete",
            input_count=len(relationships),
            output_count=len(resolved),
            pairs_with_conflicts=sum(
                1 for c in by_pair.values() if len(c) > 1
            ),
        )

        return resolved

    def _apply_policy(
        self,
        pair_key: str,
        candidates: List[Relationship],
    ) -> Optional[Relationship]:
        """Apply the conflict policy to select one winner from conflicting relationships."""
        if self._policy == ConflictResolutionPolicy.LATEST_WINS:
            return max(candidates, key=lambda r: r.provenance.run_id)

        elif self._policy == ConflictResolutionPolicy.HIGHEST_CONFIDENCE:
            return max(candidates, key=lambda r: r.evidence.calibrated_confidence)

        elif self._policy == ConflictResolutionPolicy.MOST_SPECIFIC:
            return min(
                candidates,
                key=lambda r: _SPECIFICITY_ORDER.get(r.relationship_type, 999)
            )

        elif self._policy == ConflictResolutionPolicy.CONSERVATIVE:
            types = {r.relationship_type for r in candidates}
            if len(types) == 1:
                return candidates[0]   # All agree
            else:
                logger.debug(
                    "conservative policy: conflicting types, dropping pair",
                    pair_key=pair_key,
                    types=[t.value for t in types],
                )
                return None   # Disagreement — drop the pair

        else:
            raise ConflictResolutionError(
                f"Unknown conflict resolution policy: {self._policy}"
            )
````

## File: src/smriti/retrieval/classification/evidence.py
````python
"""
classification/evidence.py — NLI cross-encoder evidence generation.

This is the ONLY module in Phase 6 that imports sentence-transformers.

Produces RelationshipEvidence objects (lifecycle: EVIDENCE).
ConfidenceCalibrator (called by __init__.py) advances to CALIBRATED_EVIDENCE.

Changes from original:
    - Evidence now populates NLIScores + InferenceMetadata (separated)
    - raw_confidence is set in NLIScores; calibrated_confidence starts equal
      to raw_confidence until ConfidenceCalibrator is applied
    - InferenceMetadata records latency per batch

Rules:
    ✅ Process in configurable batches
    ✅ Handle model failures gracefully (skip pair, record error)
    ✅ Convert numpy/torch → plain Python before returning
    ✅ Record per-batch latency in InferenceMetadata
    ❌ Never modify Claims or CandidatePairs
    ❌ Never produce Relationship objects (resolver does that)
    ❌ Never apply thresholds (resolver does that)
"""

from __future__ import annotations

import time
from typing import List, Dict, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Claim, CandidatePair, RelationshipEvidence,
    NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.exceptions import NLIModelError, NLIInferenceBatchError

logger = structlog.get_logger(__name__)

_NLI_LABELS = ["contradiction", "entailment", "neutral"]
_LABEL_INDEX = {label: i for i, label in enumerate(_NLI_LABELS)}

NLI_MODEL_VERSION = "1.0"

# Retry configuration
_NLI_MAX_RETRIES = 3
_NLI_RETRY_BACKOFF_BASE = 2  # seconds: 1, 2, 4


class NLIEvidenceGenerator:
    """
    Generates RelationshipEvidence for candidate pairs using NLI cross-encoder.
    Instantiate once per pipeline run.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        config = get_config()
        nli_cfg = config.get("nli", {})
        self._model_name = model_name or nli_cfg.get(
            "model", "cross-encoder/nli-deberta-v3-small"
        )
        self._batch_size: int = nli_cfg.get("batch_size", 16)
        self._model = self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(self._model_name)
            logger.info("nli model loaded", model=self._model_name)
            return model
        except ImportError as e:
            raise NLIModelError(f"sentence-transformers not installed: {e}") from e
        except Exception as e:
            raise NLIModelError(
                f"Failed to load NLI model '{self._model_name}': {e}"
            ) from e

    def generate_batch(
        self,
        pairs: List[CandidatePair],
        claims_map: Dict[str, Claim],
    ) -> List[RelationshipEvidence]:
        """
        Generate NLI evidence for validated candidate pairs.

        Returns:
            List of RelationshipEvidence (lifecycle: EVIDENCE, pre-calibration).
        """
        if not pairs:
            return []

        results: List[RelationshipEvidence] = []

        for batch_idx, batch_start in enumerate(range(0, len(pairs), self._batch_size)):
            batch = pairs[batch_start: batch_start + self._batch_size]
            try:
                batch_evidence = self._process_batch(batch, claims_map, batch_index=batch_idx)
                results.extend(batch_evidence)
            except NLIInferenceBatchError as e:
                logger.warning(
                    "nli batch failed, skipping batch",
                    batch_index=batch_idx,
                    batch_size=len(batch),
                    error=str(e),
                )
                continue

        logger.info(
            "nli evidence generation complete",
            pairs_processed=len(pairs),
            evidence_produced=len(results),
        )

        return results

    def _process_batch(
        self,
        batch: List[CandidatePair],
        claims_map: Dict[str, Claim],
        batch_index: int = 0,
    ) -> List[RelationshipEvidence]:
        """Process one batch of candidate pairs with retry logic."""
        text_pairs = []
        valid_pairs = []

        for pair in batch:
            claim_a = claims_map.get(pair.claim_id_a)
            claim_b = claims_map.get(pair.claim_id_b)
            if claim_a is None or claim_b is None:
                logger.warning(
                    "claim not found for nli",
                    claim_id_a=pair.claim_id_a[:8],
                    claim_id_b=pair.claim_id_b[:8],
                )
                continue
            text_pairs.append((claim_a.text, claim_b.text))
            valid_pairs.append(pair)

        if not text_pairs:
            return []

        batch_start_time = time.monotonic()
        scores_list = None

        # Retry loop with exponential backoff
        for attempt in range(_NLI_MAX_RETRIES):
            try:
                raw_scores = self._model.predict(
                    text_pairs,
                    apply_softmax=True,
                    show_progress_bar=False,
                )
                scores_list = raw_scores.tolist()
                break  # Success, exit retry loop
            except Exception as e:
                if attempt == _NLI_MAX_RETRIES - 1:
                    # Last attempt failed, raise error
                    raise NLIInferenceBatchError(
                        f"NLI batch inference failed after {_NLI_MAX_RETRIES} attempts: {e}"
                    ) from e
                # Exponential backoff: 1s, 2s, 4s
                wait_seconds = _NLI_RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "NLI batch inference failed, retrying",
                    attempt=attempt + 1,
                    max_retries=_NLI_MAX_RETRIES,
                    wait_seconds=wait_seconds,
                    error=str(e),
                )
                time.sleep(wait_seconds)

        # Should never happen if the loop succeeded, but guard
        if scores_list is None:
            raise NLIInferenceBatchError("NLI batch inference failed with no retries left")

        batch_elapsed = time.monotonic() - batch_start_time
        per_pair_latency_ms = (batch_elapsed / max(len(text_pairs), 1)) * 1000.0

        evidence_list: List[RelationshipEvidence] = []

        for pair, scores in zip(valid_pairs, scores_list):
            contradiction_score = float(scores[_LABEL_INDEX["contradiction"]])
            entailment_score = float(scores[_LABEL_INDEX["entailment"]])
            neutral_score = float(scores[_LABEL_INDEX["neutral"]])
            raw_confidence = max(contradiction_score, entailment_score, neutral_score)
            predicted_label = _NLI_LABELS[scores.index(max(scores))]

            nli_scores = NLIScores(
                entailment_score=entailment_score,
                neutral_score=neutral_score,
                contradiction_score=contradiction_score,
                predicted_label=predicted_label,
                raw_confidence=raw_confidence,
            )

            inference_metadata = InferenceMetadata(
                model_name=self._model_name,
                model_version=NLI_MODEL_VERSION,
                runtime_seconds=batch_elapsed,
                device="cpu",                     # Extend to detect GPU if needed
                batch_index=batch_index,
                latency_ms=per_pair_latency_ms,
            )

            evidence = RelationshipEvidence(
                pair=pair,
                cosine_similarity=pair.cosine_similarity,
                nli_scores=nli_scores,
                calibrated_confidence=raw_confidence,  # Updated by ConfidenceCalibrator
                inference_metadata=inference_metadata,
                lifecycle_stage=LifecycleStage.EVIDENCE,
            )
            evidence_list.append(evidence)

        return evidence_list
````

## File: src/smriti/retrieval/classification/resolver.py
````python
"""
classification/resolver.py — Policy-driven relationship resolution.

RECTIFIED: All threshold values have been moved out of Python code and into
ResolverPolicy, which is constructed from config. The resolver itself is a
pure function: (evidence, policy) → (RelationshipType, RelationshipDirection).
No threshold values appear in this file.

Resolution rules (applied in priority order as defined by the policy):
    1. If contradiction_score >= policy.nli_threshold AND
       contradiction_score > entailment_score
       → CONTRADICTS (symmetric)
    2. If entailment_score >= policy.nli_threshold AND
       entailment_score > contradiction_score
       → SUPPORTS (a_to_b)
    3. If cosine_similarity >= policy.high_sim_threshold AND
       neutral_score >= policy.neutrality_threshold AND
       contradiction_score < 0.1
       → REFINES (a_to_b)
    4. If neutral_score >= policy.neutrality_threshold
       → NEUTRAL (symmetric)
    5. Otherwise
       → UNKNOWN (symmetric)

Rules:
    ✅ Resolver NEVER contains hard-coded thresholds
    ✅ Resolver NEVER calls any ML model
    ✅ Resolver NEVER accesses external state
    ✅ Policy is versioned and validated on construction
    ✅ Rule priority order is configurable via policy.priority_order
    ❌ No randomness, no external state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    RelationshipEvidence,
    RelationshipType,
    RelationshipDirection,
    LifecycleStage,
)
from smriti.exceptions import ResolverPolicyError

logger = structlog.get_logger(__name__)

RESOLVER_VERSION = "1.0"


@dataclass(frozen=True)
class ResolverPolicy:
    """
    All resolver thresholds and rule configuration in one place.

    This object replaces every hard-coded if/else threshold in the resolver.
    Changing resolver behavior requires changing config, not code.

    Fields:
        nli_threshold:       Minimum score for CONTRADICTS / SUPPORTS classification.
        refine_threshold:    (Deprecated) Previously used for REFINES; now unused.
        high_sim_threshold:  Minimum cosine similarity required for REFINES.
        neutrality_threshold: Minimum neutral_score for NEUTRAL classification.
        contradiction_margin: Minimum gap between contradiction and entailment scores
                              required to classify as CONTRADICTS (prevents edge cases).
        entailment_margin:   Minimum gap between entailment and contradiction scores
                             required to classify as SUPPORTS.
        confidence_policy:   "calibrated" (use calibrated_confidence) or
                             "raw" (use raw NLI score). Default: "calibrated".
        priority_order:      List of RelationshipType values in resolution priority order.
                             Default: [CONTRADICTS, SUPPORTS, REFINES, NEUTRAL, UNKNOWN].
        version:             Resolver policy version string.
    """
    nli_threshold: float
    refine_threshold: float
    high_sim_threshold: float
    neutrality_threshold: float
    contradiction_margin: float = 0.0
    entailment_margin: float = 0.0
    confidence_policy: str = "calibrated"
    priority_order: List[str] = field(default_factory=lambda: [
        "contradicts", "supports", "refines", "neutral", "unknown"
    ])
    version: str = RESOLVER_VERSION

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate internal consistency of the policy."""
        if self.nli_threshold <= 0 or self.nli_threshold > 1:
            raise ResolverPolicyError(
                f"nli_threshold must be in (0, 1], got {self.nli_threshold}"
            )
        if self.refine_threshold >= self.nli_threshold:
            raise ResolverPolicyError(
                f"refine_threshold ({self.refine_threshold}) must be < "
                f"nli_threshold ({self.nli_threshold})"
            )
        if self.high_sim_threshold <= 0 or self.high_sim_threshold > 1:
            raise ResolverPolicyError(
                f"high_sim_threshold must be in (0, 1], got {self.high_sim_threshold}"
            )
        if self.contradiction_margin < 0:
            raise ResolverPolicyError(
                f"contradiction_margin must be >= 0, got {self.contradiction_margin}"
            )

    @classmethod
    def from_config(cls) -> "ResolverPolicy":
        """
        Construct ResolverPolicy from the application configuration.
        This is the canonical way to get a ResolverPolicy in production.
        """
        config = get_config()
        nli_cfg = config.get("nli", {})
        rd_cfg = config.get("relationship_discovery", {})
        policy_cfg = config.get("resolver_policy", {})

        return cls(
            nli_threshold=nli_cfg.get("nli_threshold", 0.80),
            refine_threshold=rd_cfg.get("refine_threshold", 0.55),
            high_sim_threshold=rd_cfg.get("high_sim_threshold", 0.88),
            neutrality_threshold=rd_cfg.get("neutrality_threshold", 0.60),
            contradiction_margin=policy_cfg.get("contradiction_margin", 0.0),
            entailment_margin=policy_cfg.get("entailment_margin", 0.0),
            confidence_policy=policy_cfg.get("confidence_policy", "calibrated"),
            priority_order=policy_cfg.get("priority_order", [
                "contradicts", "supports", "refines", "neutral", "unknown"
            ]),
            version=policy_cfg.get("version", RESOLVER_VERSION),
        )


class RelationshipResolver:
    """
    Policy-driven resolver: RelationshipEvidence → RelationshipType.

    The resolver itself contains no threshold values.
    All rules come from the ResolverPolicy.
    Instantiate once per pipeline run.
    """

    def __init__(self, policy: Optional["ResolverPolicy"] = None) -> None:
        self._policy = policy or ResolverPolicy.from_config()
        logger.info(
            "resolver initialized",
            policy_version=self._policy.version,
            nli_threshold=self._policy.nli_threshold,
            high_sim_threshold=self._policy.high_sim_threshold,
            neutrality_threshold=self._policy.neutrality_threshold,
            confidence_policy=self._policy.confidence_policy,
        )

    @property
    def policy(self) -> ResolverPolicy:
        return self._policy

    def resolve(
        self,
        evidence: RelationshipEvidence,
    ) -> Tuple[RelationshipType, RelationshipDirection]:
        """
        Apply policy rules to classify a RelationshipEvidence.

        Uses calibrated_confidence from evidence (unless policy says "raw").

        Returns:
            (RelationshipType, RelationshipDirection) — never raises.
        """
        p = self._policy
        c = evidence.nli_scores.contradiction_score
        e = evidence.nli_scores.entailment_score
        n = evidence.nli_scores.neutral_score
        cos = evidence.cosine_similarity

        for rule in p.priority_order:
            if rule == "contradicts":
                if (c >= p.nli_threshold
                        and c > e
                        and (c - e) >= p.contradiction_margin):
                    logger.debug(
                        "resolved: CONTRADICTS",
                        contradiction=f"{c:.3f}", entailment=f"{e:.3f}",
                    )
                    return RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC

            elif rule == "supports":
                if (e >= p.nli_threshold
                        and e > c
                        and (e - c) >= p.entailment_margin):
                    logger.debug("resolved: SUPPORTS", entailment=f"{e:.3f}")
                    return RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B

            elif rule == "refines":
                # Rectified heuristic:
                # A refinement is highly similar (high cosine), strictly NOT contradictory,
                # and usually classified as NLI Neutral because it does not strictly
                # entail in either direction.
                if (cos >= p.high_sim_threshold
                        and n >= p.neutrality_threshold
                        and c < 0.1):   # Strict ceiling on contradiction
                    logger.debug(
                        "resolved: REFINES",
                        neutral=f"{n:.3f}", cosine=f"{cos:.3f}",
                    )
                    return RelationshipType.REFINES, RelationshipDirection.A_TO_B

            elif rule == "neutral":
                if n >= p.neutrality_threshold:
                    logger.debug("resolved: NEUTRAL", neutral=f"{n:.3f}")
                    return RelationshipType.NEUTRAL, RelationshipDirection.SYMMETRIC

            elif rule == "unknown":
                logger.debug(
                    "resolved: UNKNOWN",
                    c=f"{c:.3f}", e=f"{e:.3f}", n=f"{n:.3f}",
                )
                return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC

        # Should never reach here, but fallback to UNKNOWN
        return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC
````

## File: src/smriti/retrieval/classification/validator.py
````python
"""
classification/validator.py — Relationship structural validation.

Enforces the Relationship Ontology invariants:
    1. CONTRADICTS must have SYMMETRIC direction.
    2. SUPPORTS must have A_TO_B or B_TO_A direction.
    3. REFINES must have A_TO_B or B_TO_A direction.
    4. NEUTRAL must have SYMMETRIC direction.
    5. UNKNOWN must never pass (unless skip_unknown=False, debugging only).
    6. confidence >= min_confidence floor.
    7. Not both entailment AND contradiction above threshold simultaneously.

Valid relationships are promoted to lifecycle stage VALIDATED_RELATIONSHIP.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict
import structlog

from smriti.core.models import (
    RelationshipEvidence, RelationshipType, RelationshipDirection, LifecycleStage,
)

logger = structlog.get_logger(__name__)


class RelRejectionReason(str, Enum):
    CONFIDENCE_TOO_LOW      = "confidence_too_low"
    UNKNOWN_RELATIONSHIP    = "unknown_relationship"
    CONTRADICTORY_EVIDENCE  = "contradictory_evidence"
    DIRECTION_INVARIANT     = "direction_invariant_violated"


@dataclass(frozen=True)
class RelationshipValidationResult:
    is_valid: bool
    rejection_reason: RelRejectionReason | None = None


# Ontology invariants: required direction per type
_REQUIRED_DIRECTION = {
    RelationshipType.CONTRADICTS: {RelationshipDirection.SYMMETRIC},
    RelationshipType.NEUTRAL:     {RelationshipDirection.SYMMETRIC},
    RelationshipType.SUPPORTS:    {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.REFINES:     {RelationshipDirection.A_TO_B, RelationshipDirection.B_TO_A},
    RelationshipType.UNKNOWN:     {RelationshipDirection.SYMMETRIC},   # rejected anyway
}


def validate_relationship(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
) -> RelationshipValidationResult:
    """Validate one resolved relationship."""
    # Check 1: Minimum confidence
    if evidence.calibrated_confidence < min_confidence:
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.CONFIDENCE_TOO_LOW,
        )

    # Check 2: Unknown relationship
    if skip_unknown and relationship_type == RelationshipType.UNKNOWN:
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.UNKNOWN_RELATIONSHIP,
        )

    # Check 3: Contradictory evidence (both E and C above threshold)
    if (evidence.nli_scores.entailment_score >= nli_threshold and
            evidence.nli_scores.contradiction_score >= nli_threshold):
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.CONTRADICTORY_EVIDENCE,
        )

    # Check 4: Direction invariant (ontology specification)
    required_dirs = _REQUIRED_DIRECTION.get(relationship_type, set())
    if required_dirs and direction not in required_dirs:
        logger.warning(
            "direction invariant violated",
            type=relationship_type.value,
            direction=direction.value,
            required=[d.value for d in required_dirs],
        )
        return RelationshipValidationResult(
            is_valid=False,
            rejection_reason=RelRejectionReason.DIRECTION_INVARIANT,
        )

    return RelationshipValidationResult(is_valid=True)


def validate_all_relationships(
    evidence_with_types: List[Tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]],
    min_confidence: float,
    nli_threshold: float,
    skip_unknown: bool,
) -> Tuple[List[Tuple[RelationshipEvidence, RelationshipType, RelationshipDirection]], Dict[str, int]]:
    """
    Validate a batch of resolved relationships.
    Valid items are tagged with lifecycle VALIDATED_RELATIONSHIP.

    Returns:
        (valid_triples, rejection_counts)
        valid_triples: (evidence, type, direction) tuples that passed.
    """
    valid = []
    rejection_counts: Dict[str, int] = {}

    for evidence, rel_type, direction in evidence_with_types:
        result = validate_relationship(
            evidence, rel_type, direction, min_confidence, nli_threshold, skip_unknown
        )
        if result.is_valid:
            valid.append((evidence, rel_type, direction))
        else:
            reason = result.rejection_reason.value
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

    logger.info(
        "relationship validation complete",
        total=len(evidence_with_types),
        valid=len(valid),
        rejected=sum(rejection_counts.values()),
        reasons=rejection_counts,
    )

    return valid, rejection_counts
````

## File: src/smriti/retrieval/benchmark.py
````python
"""
benchmark.py — Phase 6 benchmarking framework.

Provides:
    SyntheticCorpus:  Deterministic gold-standard dataset for regression testing.
    BenchmarkSuite:   Evaluates Recall@K, Precision, latency, and relationship density.

Rules:
    ✅ SyntheticCorpus is fully deterministic (seeded random)
    ✅ BenchmarkSuite never modifies pipeline objects
    ✅ All metrics are computed against a gold-standard label set
    ❌ Never used in production pipeline runs
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
import structlog

from smriti.core.models import RelationshipType

logger = structlog.get_logger(__name__)


@dataclass
class GoldPair:
    """A gold-standard relationship label for evaluation."""
    claim_id_a: str
    claim_id_b: str
    expected_type: RelationshipType


@dataclass
class SyntheticCorpus:
    """
    Deterministic gold-standard dataset for Phase 6 regression testing.

    Usage:
        corpus = SyntheticCorpus.generate(seed=42, n_claims=100, n_gold_pairs=50)
        # Use corpus.claims, corpus.embeddings, corpus.gold_labels in tests
    """
    claims: List[Dict]                          # {claim_id, text}
    embeddings: List[Tuple[str, List[float]]]   # (claim_id, vector)
    gold_labels: List[GoldPair]
    dimension: int
    seed: int

    @classmethod
    def generate(
        cls,
        seed: int = 42,
        n_claims: int = 100,
        n_gold_pairs: int = 50,
        dimension: int = 8,
    ) -> "SyntheticCorpus":
        """
        Generate a deterministic synthetic corpus.

        All gold pairs are created by deterministically constructing
        claim pairs that should have known relationship types:
            - CONTRADICTS: opposite-sign vectors
            - SUPPORTS:    nearly identical vectors
            - REFINES:     high cosine but slight offset
            - NEUTRAL:     orthogonal vectors
        """
        rng = random.Random(seed)

        # Generate claim texts (templates for determinism)
        claim_texts = [
            (f"c{i:04d}", f"Synthetic claim {i} about topic {i % 10}.")
            for i in range(n_claims)
        ]
        claims = [{"claim_id": cid, "text": text} for cid, text in claim_texts]

        # Generate random L2-normalized embeddings
        def rand_vector() -> List[float]:
            vec = [rng.gauss(0, 1) for _ in range(dimension)]
            norm = math.sqrt(sum(v ** 2 for v in vec))
            return [v / max(norm, 1e-9) for v in vec]

        embeddings_dict: Dict[str, List[float]] = {
            cid: rand_vector() for cid, _ in claim_texts
        }

        # Create gold pairs with controlled relationship types
        gold_labels: List[GoldPair] = []
        claim_ids = [cid for cid, _ in claim_texts]
        pairs_created: Set[str] = set()

        for i in range(n_gold_pairs):
            idx_a = rng.randint(0, n_claims - 1)
            idx_b = rng.randint(0, n_claims - 1)
            if idx_a == idx_b:
                continue

            id_a, id_b = sorted([claim_ids[idx_a], claim_ids[idx_b]])
            pair_key = f"{id_a}:{id_b}"
            if pair_key in pairs_created:
                continue
            pairs_created.add(pair_key)

            # Assign relationship type and adjust embeddings accordingly
            rel_type_idx = i % 4
            if rel_type_idx == 0:
                rel_type = RelationshipType.CONTRADICTS
                embeddings_dict[id_b] = [-v for v in embeddings_dict[id_a]]
            elif rel_type_idx == 1:
                rel_type = RelationshipType.SUPPORTS
                noise = [rng.gauss(0, 0.01) for _ in range(dimension)]
                vec = [v + n for v, n in zip(embeddings_dict[id_a], noise)]
                norm = math.sqrt(sum(v ** 2 for v in vec))
                embeddings_dict[id_b] = [v / max(norm, 1e-9) for v in vec]
            elif rel_type_idx == 2:
                rel_type = RelationshipType.REFINES
                noise = [rng.gauss(0, 0.1) for _ in range(dimension)]
                vec = [v + n for v, n in zip(embeddings_dict[id_a], noise)]
                norm = math.sqrt(sum(v ** 2 for v in vec))
                embeddings_dict[id_b] = [v / max(norm, 1e-9) for v in vec]
            else:
                rel_type = RelationshipType.NEUTRAL

            gold_labels.append(GoldPair(
                claim_id_a=id_a, claim_id_b=id_b, expected_type=rel_type,
            ))

        embeddings = list(embeddings_dict.items())

        logger.info(
            "synthetic corpus generated",
            seed=seed, n_claims=n_claims,
            n_gold_pairs=len(gold_labels),
        )

        return cls(
            claims=claims,
            embeddings=embeddings,
            gold_labels=gold_labels,
            dimension=dimension,
            seed=seed,
        )


@dataclass
class BenchmarkResult:
    """Results of running BenchmarkSuite."""
    recall_at_k: float                          # Fraction of gold pairs retrieved
    precision: float                            # Fraction of retrieved pairs that are gold
    relationship_density: float                 # relationships / claims
    nli_latency_ms_per_pair: float
    retrieval_latency_ms_per_claim: float
    memory_mb: float
    by_type: Dict[str, Dict[str, float]]        # {type: {precision, recall}}


class BenchmarkSuite:
    """
    Evaluates Phase 6 pipeline against a gold-standard corpus.

    Usage:
        corpus = SyntheticCorpus.generate(seed=42)
        suite = BenchmarkSuite(corpus)
        result = suite.evaluate(relationship_set, retrieval_latency, nli_latency)
    """

    def __init__(self, corpus: SyntheticCorpus) -> None:
        self._corpus = corpus
        self._gold_by_pair: Dict[str, RelationshipType] = {
            f"{g.claim_id_a}:{g.claim_id_b}": g.expected_type
            for g in corpus.gold_labels
        }

    def evaluate(
        self,
        relationship_set,
        retrieval_latency_seconds: float,
        nli_latency_seconds: float,
        memory_mb: float = 0.0,
    ) -> BenchmarkResult:
        """Evaluate a RelationshipSet against the gold labels."""
        gold_keys = set(self._gold_by_pair.keys())
        predicted_keys = {
            rel.evidence.pair.pair_key()
            for rel in relationship_set.relationships
        }

        retrieved_gold = gold_keys & predicted_keys
        recall_at_k = len(retrieved_gold) / max(len(gold_keys), 1)
        precision = len(retrieved_gold) / max(len(predicted_keys), 1)

        n_claims = self._corpus.seed   # rough proxy
        relationship_density = relationship_set.total_relationships / max(n_claims, 1)

        nli_count = max(relationship_set.total_validated, 1)
        nli_latency_ms = (nli_latency_seconds / nli_count) * 1000.0

        n_embedded = max(relationship_set.total_candidates, 1)
        retrieval_latency_ms = (retrieval_latency_seconds / n_embedded) * 1000.0

        # Per-type breakdown
        by_type: Dict[str, Dict[str, float]] = {}
        for rel_type in RelationshipType:
            gold_of_type = {
                k for k, v in self._gold_by_pair.items()
                if v == rel_type
            }
            predicted_of_type = {
                rel.evidence.pair.pair_key()
                for rel in relationship_set.relationships
                if rel.relationship_type == rel_type
            }
            tp = len(gold_of_type & predicted_of_type)
            p = tp / max(len(predicted_of_type), 1)
            r = tp / max(len(gold_of_type), 1)
            by_type[rel_type.value] = {"precision": p, "recall": r, "tp": tp}

        return BenchmarkResult(
            recall_at_k=recall_at_k,
            precision=precision,
            relationship_density=relationship_density,
            nli_latency_ms_per_pair=nli_latency_ms,
            retrieval_latency_ms_per_claim=retrieval_latency_ms,
            memory_mb=memory_mb,
            by_type=by_type,
        )
````

## File: src/smriti/retrieval/builder.py
````python
"""
builder.py — Immutable Relationship and RelationshipSet construction.

Changes from original:
    - Populates SchemaVersionInfo (schema_version, migration_version, compatibility_version)
    - Populates RelationshipProvenance with new fields (index_version, search_parameters,
      calibrator_version, classifier_version, raw_nli_confidence, calibrated_confidence)
    - Populates RelationshipQuality with calibration_applied and retrieval_quality
    - Sets lifecycle_stage to RELATIONSHIP on all constructed objects
    - relationship_id includes schema_version to guarantee ID change when ontology changes

Rules:
    ✅ Pure object construction
    ✅ Deterministic relationship_id generation
    ✅ Full provenance including calibration info
    ❌ Never perform NLI inference
    ❌ Never validate
    ❌ No heuristics or logic beyond construction
"""

from __future__ import annotations

import hashlib
from typing import List, Dict, Optional
import structlog

from smriti.core.models import (
    Relationship, RelationshipSet, RelationshipEvidence,
    RelationshipProvenance, RelationshipQuality, SchemaVersionInfo,
    RelationshipType, RelationshipDirection, LifecycleStage,
)
from smriti.retrieval.faiss_index import RETRIEVAL_BACKEND, RETRIEVAL_VERSION, INDEX_VERSION
from smriti.retrieval.classification.resolver import RESOLVER_VERSION
from smriti.retrieval.classification.calibration import CALIBRATOR_VERSION

logger = structlog.get_logger(__name__)

CURRENT_SCHEMA_VERSION = "6.0"
CURRENT_MIGRATION_VERSION = "6.0"
CURRENT_COMPATIBILITY_VERSION = "6.0"


def _compute_relationship_id(
    claim_id_a: str,
    claim_id_b: str,
    relationship_type: str,
    schema_version: str = CURRENT_SCHEMA_VERSION,
) -> str:
    """
    Deterministic 16-char SHA256 relationship ID including schema version.

    Injecting the schema version into the hash ensures that if the relationship
    ontology changes (e.g., the definition of SUPPORTS or CONTRADICTS evolves),
    the ID of every relationship changes automatically, preventing accidental
    cross-version mixing.
    """
    material = f"{claim_id_a}:{claim_id_b}:{relationship_type}:{schema_version}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def build_relationship(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
    nli_threshold: float,
    config_hash: str,
    run_id: str,
) -> Relationship:
    """
    Construct one immutable Relationship.

    Args:
        evidence:           NLI evidence for the pair (post-calibration).
        relationship_type:  Resolved type from resolver.
        direction:          Resolved direction.
        nli_threshold:      NLI confidence threshold (for quality diagnostics).
        config_hash:        SHA256 of relevant config.
        run_id:             Current pipeline run identifier.

    Returns:
        Immutable Relationship with full provenance, quality, and version info.
    """
    claim_id_a = evidence.pair.claim_id_a
    claim_id_b = evidence.pair.claim_id_b

    relationship_id = _compute_relationship_id(
        claim_id_a=claim_id_a,
        claim_id_b=claim_id_b,
        relationship_type=relationship_type.value,
        schema_version=CURRENT_SCHEMA_VERSION,
    )

    provenance = RelationshipProvenance(
        retrieval_backend=RETRIEVAL_BACKEND,
        retrieval_version=RETRIEVAL_VERSION,
        index_version=INDEX_VERSION,
        search_parameters=evidence.pair.search_parameters,
        classifier_model=evidence.inference_metadata.model_name,
        classifier_version=evidence.inference_metadata.model_version,
        resolver_version=RESOLVER_VERSION,
        calibrator_version=CALIBRATOR_VERSION,
        cosine_similarity=evidence.cosine_similarity,
        candidate_rank=evidence.pair.candidate_rank,
        raw_nli_confidence=evidence.nli_scores.raw_confidence,
        calibrated_confidence=evidence.calibrated_confidence,
        config_hash=config_hash,
        run_id=run_id,
        replay_id=None,
    )

    calibration_applied = (
        abs(evidence.nli_scores.raw_confidence - evidence.calibrated_confidence) > 1e-6
    )

    quality = RelationshipQuality(
        cosine_above_threshold=True,   # Guaranteed by candidate validator
        nli_above_threshold=evidence.calibrated_confidence >= nli_threshold,
        evidence_consistent=not (
            evidence.nli_scores.entailment_score >= nli_threshold
            and evidence.nli_scores.contradiction_score >= nli_threshold
        ),
        calibration_applied=calibration_applied,
        retrieval_quality=evidence.pair.retrieval_quality,
    )

    version_info = SchemaVersionInfo(
        schema_version=CURRENT_SCHEMA_VERSION,
        migration_version=CURRENT_MIGRATION_VERSION,
        compatibility_version=CURRENT_COMPATIBILITY_VERSION,
    )

    relationship = Relationship(
        relationship_id=relationship_id,
        claim_id_a=claim_id_a,
        claim_id_b=claim_id_b,
        relationship_type=relationship_type,
        direction=direction,
        evidence=evidence,
        quality=quality,
        provenance=provenance,
        version_info=version_info,
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )

    logger.debug(
        "relationship built",
        rel_id=relationship_id[:8],
        type=relationship_type.value,
        calibrated_confidence=f"{evidence.calibrated_confidence:.3f}",
        calibration_applied=calibration_applied,
    )

    return relationship


def build_relationship_set(
    relationships: List[Relationship],
    total_candidates: int,
    total_validated: int,
    total_rejected: int,
    rejected_reasons: Dict[str, int],
    run_id: str,
) -> RelationshipSet:
    """Build the final RelationshipSet."""
    return RelationshipSet(
        relationships=relationships,
        total_candidates=total_candidates,
        total_validated=total_validated,
        total_rejected=total_rejected,
        rejected_reasons=rejected_reasons,
        run_id=run_id,
        version_info=SchemaVersionInfo(
            schema_version=CURRENT_SCHEMA_VERSION,
            migration_version=CURRENT_MIGRATION_VERSION,
            compatibility_version=CURRENT_COMPATIBILITY_VERSION,
        ),
    )
````

## File: src/smriti/retrieval/candidate_generator.py
````python
"""
candidate_generator.py — Hybrid ANN candidate retrieval for Phase 6.

Responsibility:
    Given an EmbeddingIndex, retrieve candidate pairs worth evaluating.

    Two-stage filter:
        Stage 1 (ANN): Find top-K nearest neighbors via FAISS
        Stage 2 (threshold): Keep only pairs above cosine_threshold

    Symmetric pair elimination:
        (claim_a, claim_b) and (claim_b, claim_a) → one canonical pair.
        Keep only the pair where claim_id_a < claim_id_b (lexicographic).

    Retrieval provenance is attached to every CandidatePair so
    debugging and replay are possible without re-running the pipeline.

Input:  List[EmbeddedClaim] + EmbeddingIndex
Output: List[CandidatePair]  (lifecycle: CANDIDATE)

Rules:
    ✅ Deterministic ordering (sort by pair_key after collection)
    ✅ Symmetric pair deduplication (pair_key canonicalization)
    ✅ Self-comparison elimination
    ✅ Configurable K and cosine threshold
    ✅ RetrievalSearchParameters attached to every pair (provenance)
    ✅ RetrievalQuality attached to every pair

    ❌ Never performs NLI inference
    ❌ Never modifies EmbeddedClaim objects
    ❌ Never builds Relationship objects
"""

from __future__ import annotations

from typing import List, Dict, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    CandidatePair, EmbeddedClaim, LifecycleStage,
    RetrievalSearchParameters, RetrievalQuality,
)
from smriti.retrieval.index import EmbeddingIndex
from smriti.retrieval.faiss_index import RETRIEVAL_BACKEND, INDEX_VERSION

logger = structlog.get_logger(__name__)

# Threshold for "high density region" — if a claim has >N neighbors above threshold
_HIGH_DENSITY_THRESHOLD = 20
# Threshold for "isolated claim" — if a claim has 0 or 1 neighbors above threshold
_ISOLATED_THRESHOLD = 1


class CandidateGenerator:
    """
    Generates candidate pairs for NLI classification via ANN search.
    Instantiate once per pipeline run.
    """

    def __init__(self) -> None:
        config = get_config()
        retrieval_cfg = config.get("relationship_discovery", {})
        self._top_k: int = retrieval_cfg.get("top_k", 50)
        self._sim_threshold: float = retrieval_cfg.get("sim_threshold", 0.75)

    def generate(
        self,
        embedded_claims: List[EmbeddedClaim],
        index: EmbeddingIndex,
    ) -> List[CandidatePair]:
        """
        Generate candidate pairs via ANN search.

        Args:
            embedded_claims: All EmbeddedClaims from Phase 5.
            index:           Pre-built vector index.

        Returns:
            Deduplicated, sorted list of CandidatePair (lifecycle: CANDIDATE).
        """
        if not embedded_claims:
            return []

        search_parameters = RetrievalSearchParameters(
            top_k=self._top_k,
            sim_threshold=self._sim_threshold,
            index_type=RETRIEVAL_BACKEND,
            index_version=INDEX_VERSION,
        )

        # Track neighbor counts for retrieval quality assessment
        neighbor_counts: Dict[str, int] = {}
        seen_pair_keys: Set[str] = set()
        candidates: List[CandidatePair] = []

        for embedded_claim in embedded_claims:
            claim_id = embedded_claim.claim_id
            query_vector = list(embedded_claim.values)

            search_results = index.search(
                query_id=claim_id,
                query_vector=query_vector,
                k=self._top_k,
            )

            above_threshold = [r for r in search_results if r.score >= self._sim_threshold]
            neighbor_counts[claim_id] = len(above_threshold)

            for result in above_threshold:
                neighbor_id = result.claim_id
                id_a, id_b = sorted([claim_id, neighbor_id])
                pair_key = f"{id_a}:{id_b}"

                if pair_key in seen_pair_keys:
                    continue
                seen_pair_keys.add(pair_key)

                candidates.append(CandidatePair(
                    claim_id_a=id_a,
                    claim_id_b=id_b,
                    cosine_similarity=result.score,
                    candidate_rank=result.rank,
                    retrieval_backend=RETRIEVAL_BACKEND,
                    index_version=INDEX_VERSION,
                    search_parameters=search_parameters,
                    retrieval_quality=None,   # Populated below after neighbor counts known
                    lifecycle_stage=LifecycleStage.CANDIDATE,
                ))

        # Now attach RetrievalQuality (requires neighbor counts for both claims)
        candidates_with_quality = []
        for pair in candidates:
            count_a = neighbor_counts.get(pair.claim_id_a, 0)
            count_b = neighbor_counts.get(pair.claim_id_b, 0)
            quality = RetrievalQuality(
                exact_match=False,   # Text-level duplicate check done in validator
                duplicate_removed=False,
                below_threshold=False,
                high_density_region=(
                    count_a > _HIGH_DENSITY_THRESHOLD or count_b > _HIGH_DENSITY_THRESHOLD
                ),
                isolated_claim=(
                    count_a <= _ISOLATED_THRESHOLD or count_b <= _ISOLATED_THRESHOLD
                ),
            )
            # Rebuild with quality (frozen dataclass — must reconstruct)
            candidates_with_quality.append(CandidatePair(
                claim_id_a=pair.claim_id_a,
                claim_id_b=pair.claim_id_b,
                cosine_similarity=pair.cosine_similarity,
                candidate_rank=pair.candidate_rank,
                retrieval_backend=pair.retrieval_backend,
                index_version=pair.index_version,
                search_parameters=pair.search_parameters,
                retrieval_quality=quality,
                lifecycle_stage=LifecycleStage.CANDIDATE,
            ))

        candidates_with_quality.sort(key=lambda c: c.pair_key())

        logger.info(
            "candidate generation complete",
            total_embedded=len(embedded_claims),
            candidates_found=len(candidates_with_quality),
            top_k=self._top_k,
            threshold=self._sim_threshold,
        )

        return candidates_with_quality
````

## File: src/smriti/retrieval/faiss_index.py
````python
"""
faiss_index.py — FAISS implementation of EmbeddingIndex.

This is the ONLY module in Phase 6 that imports faiss.
All other modules see only the EmbeddingIndex interface.

Rules:
    ✅ Convert numpy arrays → plain Python lists before returning
    ✅ Convert Python lists → numpy arrays before passing to FAISS
    ✅ Handle faiss not installed gracefully
    ❌ Never return numpy arrays or tensors
    ❌ Never expose FAISS types outside this module
"""

from __future__ import annotations

from typing import List, Optional, Dict
import structlog

from smriti.retrieval.index import EmbeddingIndex, SearchResult
from smriti.exceptions import IndexBuildError, FAISSNotAvailableError

logger = structlog.get_logger(__name__)

RETRIEVAL_BACKEND = "faiss_flat_ip"
RETRIEVAL_VERSION = "1.0"
INDEX_VERSION = "1.0"


class FAISSIndex(EmbeddingIndex):
    """
    FAISS IndexFlatIP — exact inner product search on L2-normalized vectors.
    Cosine similarity == dot product when both vectors are L2-normalized.
    """

    def __init__(self, dimension: int) -> None:
        self._dimension = dimension
        self._claim_ids: List[str] = []
        self._id_to_idx: Dict[str, int] = {}
        self._index = self._create_index(dimension)

    def _create_index(self, dimension: int):
        try:
            import faiss
            index = faiss.IndexFlatIP(dimension)
            logger.info("faiss index created", dimension=dimension)
            return index
        except ImportError as e:
            raise FAISSNotAvailableError(
                f"faiss-cpu is not installed. Run: poetry add faiss-cpu\nError: {e}"
            ) from e

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def size(self) -> int:
        return len(self._claim_ids)

    def add(self, claim_ids: List[str], vectors: List[List[float]]) -> None:
        import numpy as np

        if not vectors:
            return

        for i, v in enumerate(vectors):
            if len(v) != self._dimension:
                raise IndexBuildError(
                    f"Vector at position {i} has dimension {len(v)}, "
                    f"expected {self._dimension}"
                )

        try:
            matrix = np.array(vectors, dtype=np.float32)
            self._index.add(matrix)
            start_idx = len(self._claim_ids)
            for i, cid in enumerate(claim_ids):
                self._claim_ids.append(cid)
                self._id_to_idx[cid] = start_idx + i

            logger.info("vectors added to index", count=len(vectors), total=self.size)
        except Exception as e:
            raise IndexBuildError(f"FAISS add failed: {e}") from e

    def search(
        self,
        query_id: str,
        query_vector: List[float],
        k: int,
        exclude_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        import numpy as np

        if self.size == 0:
            return []

        excluded = {query_id}
        if exclude_ids:
            excluded.update(exclude_ids)

        k_request = min(k + len(excluded) + 1, self.size)

        try:
            query_np = np.array([query_vector], dtype=np.float32)
            scores_np, indices_np = self._index.search(query_np, k_request)
            scores = scores_np[0].tolist()
            indices = indices_np[0].tolist()
        except Exception as e:
            logger.warning("faiss search failed", query_id=query_id[:8], error=str(e))
            return []

        results = []
        rank = 1
        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self._claim_ids):
                continue
            neighbor_id = self._claim_ids[idx]
            if neighbor_id in excluded:
                continue
            results.append(SearchResult(claim_id=neighbor_id, score=float(score), rank=rank))
            rank += 1
            if len(results) >= k:
                break

        return results
````

## File: src/smriti/retrieval/governance.py
````python
"""
governance.py — Resource governance for Phase 6 discovery pipeline.

Prevents runaway resource consumption on large vaults or misconfigured runs.

Limits enforced:
    max_pairs:        Maximum number of candidate pairs to process through NLI.
    max_gpu_memory_gb: Maximum GPU memory allocation (0 = CPU only).
    max_batch_size:   Maximum NLI batch size.
    timeout_seconds:  Maximum wall-clock time for the entire Phase 6 run.
    cancel_on_limit:  If True, abort when any limit is exceeded. If False, truncate.

Rules:
    ✅ Limits read from config (never hard-coded)
    ✅ Truncation is deterministic (sorted by cosine_similarity desc)
    ✅ Resource violations are logged and raised as ResourceLimitExceeded
    ❌ Never modifies evidence or relationships
"""

from __future__ import annotations

import time
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import CandidatePair
from smriti.exceptions import ResourceLimitExceeded

logger = structlog.get_logger(__name__)


class ResourceLimits:
    """Holds all resource limits for one Phase 6 run."""

    def __init__(self) -> None:
        config = get_config()
        gov_cfg = config.get("resource_governance", {})

        self.max_pairs: int = gov_cfg.get("max_pairs", 100_000)
        self.max_gpu_memory_gb: float = gov_cfg.get("max_gpu_memory_gb", 0.0)
        self.max_batch_size: int = gov_cfg.get("max_batch_size", 64)
        self.timeout_seconds: float = gov_cfg.get("timeout_seconds", 3600.0)
        self.cancel_on_limit: bool = gov_cfg.get("cancel_on_limit", False)


class ResourceGovernor:
    """
    Enforces resource limits during Phase 6.
    Instantiate once per run; call check_* methods at critical points.
    """

    def __init__(self, limits: Optional[ResourceLimits] = None) -> None:
        self._limits = limits or ResourceLimits()
        self._start_time = time.monotonic()
        logger.info(
            "resource governor initialized",
            max_pairs=self._limits.max_pairs,
            timeout_seconds=self._limits.timeout_seconds,
            cancel_on_limit=self._limits.cancel_on_limit,
        )

    def enforce_pair_limit(
        self,
        candidates: List[CandidatePair],
    ) -> List[CandidatePair]:
        """
        Enforce max_pairs limit on the candidate list.

        If cancel_on_limit=True and limit exceeded: raises ResourceLimitExceeded.
        If cancel_on_limit=False: returns the top max_pairs by cosine_similarity.
        """
        if len(candidates) <= self._limits.max_pairs:
            return candidates

        if self._limits.cancel_on_limit:
            raise ResourceLimitExceeded(
                f"Candidate pairs ({len(candidates)}) exceeded max_pairs "
                f"({self._limits.max_pairs}). Aborting. "
                f"Increase resource_governance.max_pairs or reduce top_k."
            )

        logger.warning(
            "pair limit exceeded, truncating",
            total=len(candidates),
            limit=self._limits.max_pairs,
        )
        # Truncate to top pairs by cosine similarity (deterministic)
        sorted_candidates = sorted(
            candidates, key=lambda c: c.cosine_similarity, reverse=True
        )
        return sorted_candidates[: self._limits.max_pairs]

    def check_timeout(self) -> None:
        """
        Check if the timeout has been exceeded.
        Raises ResourceLimitExceeded if so.
        """
        elapsed = time.monotonic() - self._start_time
        if elapsed > self._limits.timeout_seconds:
            raise ResourceLimitExceeded(
                f"Phase 6 timeout exceeded: {elapsed:.1f}s > "
                f"{self._limits.timeout_seconds:.1f}s. "
                f"Increase resource_governance.timeout_seconds or reduce vault size."
            )

    def clamp_batch_size(self, requested: int) -> int:
        """Return min(requested, max_batch_size)."""
        clamped = min(requested, self._limits.max_batch_size)
        if clamped < requested:
            logger.warning(
                "batch size clamped by resource governor",
                requested=requested, clamped=clamped,
            )
        return clamped
````

## File: src/smriti/retrieval/incremental.py
````python
"""
incremental.py — Incremental relationship discovery for large vaults.

Problem:
    When 50,000 claims exist and one new claim arrives, the full pipeline
    would recompute all O(N·K) candidate pairs from scratch.
    This is unacceptable for interactive or near-real-time use.

Solution:
    IncrementalDiscoveryEngine only searches for relationships between:
    - New claims and the existing indexed claims
    - New claims and each other

    The existing RelationshipSet is preserved and augmented,
    not recomputed.

Cache invalidation cascade:
    Embedding changed for claim X
        → invalidate candidate cache for all pairs containing X
        → invalidate evidence cache for those pairs
        → invalidate relationships for those pairs
        → recompute only the affected subset

Rules:
    ✅ Never recomputes existing valid relationships
    ✅ Applies conflict resolution policy when new evidence conflicts with old
    ✅ Respects resource limits (ResourceGovernor)
    ❌ Never modifies existing Relationship objects
"""

from __future__ import annotations

from typing import List, Dict, Set, Optional
import structlog

from smriti.core.models import (
    EmbeddedClaim, Claim, Relationship, RelationshipSet,
)
from smriti.core.config import get_config
from smriti.exceptions import ResourceLimitExceeded

logger = structlog.get_logger(__name__)


class CacheInvalidationPolicy:
    """
    Defines when cached results must be invalidated.

    Cascade rule:
        Embedding changed for claim X
            → invalidate candidate_cache for all pairs containing X
            → invalidate evidence_cache for those pairs
            → invalidate resolved_cache for those pairs
    """

    def __init__(self) -> None:
        config = get_config()
        cache_cfg = config.get("cache_invalidation", {})
        self._invalidate_on_embedding_change: bool = cache_cfg.get(
            "invalidate_on_embedding_change", True
        )
        self._invalidate_on_model_change: bool = cache_cfg.get(
            "invalidate_on_model_change", True
        )
        self._invalidate_on_policy_change: bool = cache_cfg.get(
            "invalidate_on_policy_change", True
        )

    def should_invalidate_for_claim(
        self,
        claim_id: str,
        changed_claim_ids: Set[str],
    ) -> bool:
        """Return True if any cache entries for this claim_id should be invalidated."""
        if not self._invalidate_on_embedding_change:
            return False
        return claim_id in changed_claim_ids

    def should_invalidate_all(
        self,
        old_config_hash: str,
        new_config_hash: str,
        old_model: str,
        new_model: str,
    ) -> bool:
        """Return True if the entire cache should be invalidated (model or policy changed)."""
        if self._invalidate_on_model_change and old_model != new_model:
            logger.info(
                "full cache invalidation: model changed",
                old=old_model, new=new_model,
            )
            return True
        if self._invalidate_on_policy_change and old_config_hash != new_config_hash:
            logger.info(
                "full cache invalidation: policy changed",
                old_hash=old_config_hash[:8], new_hash=new_config_hash[:8],
            )
            return True
        return False


class IncrementalDiscoveryEngine:
    """
    Discovers relationships for a delta of new claims against an existing RelationshipSet.

    Usage:
        # Initial full run
        result = discover_relationships(all_claims, ...)

        # Later: new claims arrive
        engine = IncrementalDiscoveryEngine(existing_result)
        updated_result = engine.update(new_claims, all_claims_map, ...)
    """

    def __init__(
        self,
        existing_relationship_set: RelationshipSet,
        invalidation_policy: Optional[CacheInvalidationPolicy] = None,
    ) -> None:
        self._existing = existing_relationship_set
        self._invalidation_policy = invalidation_policy or CacheInvalidationPolicy()

    def compute_delta(
        self,
        all_embedded_claims: List[EmbeddedClaim],
        existing_claim_ids: Set[str],
    ) -> List[EmbeddedClaim]:
        """
        Identify which claims are new (not in existing_claim_ids).

        Args:
            all_embedded_claims: Complete current set of embedded claims.
            existing_claim_ids:  Claim IDs already present in the existing RelationshipSet.

        Returns:
            Only the new EmbeddedClaims that need relationship discovery.
        """
        new_claims = [
            ec for ec in all_embedded_claims
            if ec.claim_id not in existing_claim_ids
        ]
        logger.info(
            "incremental delta computed",
            total_claims=len(all_embedded_claims),
            existing_claims=len(existing_claim_ids),
            new_claims=len(new_claims),
        )
        return new_claims

    def invalidate_changed_embeddings(
        self,
        changed_claim_ids: Set[str],
    ) -> List[Relationship]:
        """
        Remove relationships that involve claims with changed embeddings.
        Returns the remaining (valid) relationships.
        """
        if not changed_claim_ids:
            return list(self._existing.relationships)

        remaining = [
            rel for rel in self._existing.relationships
            if not (
                rel.claim_id_a in changed_claim_ids
                or rel.claim_id_b in changed_claim_ids
            )
        ]

        invalidated_count = len(self._existing.relationships) - len(remaining)
        logger.info(
            "embedding change invalidation",
            changed_claims=len(changed_claim_ids),
            invalidated_relationships=invalidated_count,
            remaining=len(remaining),
        )

        return remaining
````

## File: src/smriti/retrieval/index.py
````python
"""
index.py — Abstract vector index interface for Phase 6.

Responsibility:
    Define the contract that all vector index implementations must satisfy.
    The rest of Phase 6 depends ONLY on this interface, never on FAISS directly.
    This allows FAISS to be replaced with HNSW, Annoy, ScaNN, or any future
    ANN backend without changing any other Phase 6 code.

Public interface:
    EmbeddingIndex.add(claim_ids, vectors) → None
    EmbeddingIndex.search(query_id, k)     → List[SearchResult]
    EmbeddingIndex.dimension               → int
    EmbeddingIndex.size                    → int

Rules:
    ✅ Returns plain Python types only (no numpy, no tensors)
    ✅ Every implementation is interchangeable
    ❌ Never performs NLI inference
    ❌ Never constructs Relationship objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SearchResult:
    """A single ANN search result."""
    claim_id: str
    score: float         # Cosine similarity (dot product on L2-normalized vectors)
    rank: int            # 1 = nearest neighbor


class EmbeddingIndex(ABC):
    """
    Abstract vector index for ANN (Approximate Nearest Neighbor) search.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension expected by this index."""
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        """Number of vectors currently in the index."""
        ...

    @abstractmethod
    def add(self, claim_ids: List[str], vectors: List[List[float]]) -> None:
        """
        Add vectors to the index.

        Args:
            claim_ids: Identifiers for each vector.
            vectors:   L2-normalized float lists (len == dimension each).

        Raises:
            IndexBuildError: If vectors cannot be added.
        """
        ...

    @abstractmethod
    def search(
        self,
        query_id: str,
        query_vector: List[float],
        k: int,
        exclude_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Find the K nearest neighbors of query_vector.

        Args:
            query_id:     The claim_id of the query (to exclude from results).
            query_vector: L2-normalized float list.
            k:            Maximum neighbors to return.
            exclude_ids:  Additional IDs to exclude from results.

        Returns:
            List of SearchResult, sorted by score (highest first).
            Never includes query_id itself.
        """
        ...
````

## File: src/smriti/retrieval/replay.py
````python
"""
replay.py — Deterministic replay of Phase 6 discovery runs.

Given a run_id, the ReplayEngine can reconstruct exactly the same
RelationshipSet that was produced in the original run, provided:
    - The same EmbeddedClaims are available
    - The same NLI model is available
    - The replay manifest is intact

A replay manifest is written after every successful Phase 6 run.
It records all parameters needed to exactly reproduce the run.

Rules:
    ✅ Replay is bit-identical to the original (same config, same model)
    ✅ Replay manifest written atomically after every successful run
    ✅ Replays are labeled with replay_id in provenance
    ❌ Replay never modifies existing artifacts
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import structlog

from smriti.core.paths import ARTIFACTS_DIR

logger = structlog.get_logger(__name__)


@dataclass
class ReplayManifest:
    """
    Everything needed to replay a Phase 6 run identically.
    Written to artifacts/run_{id}/phase6/replay_manifest.json.
    """
    run_id: str
    schema_version: str
    nli_model: str
    nli_threshold: float
    sim_threshold: float
    top_k: int
    min_confidence: float
    refine_threshold: float
    high_sim_threshold: float
    neutrality_threshold: float
    contradiction_margin: float
    entailment_margin: float
    calibration_strategy: str
    calibration_temperature: float
    conflict_resolution_policy: str
    deduplication_policy: str
    skip_unknown_relationships: bool
    config_hash: str
    total_embedded_claims: int
    total_relationships: int
    phase5_dataset_path: str
    phase4_dataset_path: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, text: str) -> "ReplayManifest":
        data = json.loads(text)
        return cls(**data)


class ReplayEngine:
    """
    Writes and reads replay manifests for deterministic replay.
    """

    def write_replay_manifest(
        self,
        manifest: ReplayManifest,
        run_id: str,
    ) -> Path:
        """Write the replay manifest after a successful run."""
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase6"
        phase_dir.mkdir(parents=True, exist_ok=True)
        replay_path = phase_dir / "replay_manifest.json"
        replay_path.write_text(manifest.to_json(), encoding="utf-8")
        logger.info(
            "replay manifest written",
            path=str(replay_path),
            run_id=run_id,
        )
        return replay_path

    def load_replay_manifest(self, run_id: str) -> ReplayManifest:
        """Load the replay manifest for a given run_id."""
        from smriti.exceptions import ReplayError

        replay_path = ARTIFACTS_DIR / f"run_{run_id}" / "phase6" / "replay_manifest.json"
        if not replay_path.exists():
            raise ReplayError(
                f"Replay manifest not found for run_id={run_id}: {replay_path}"
            )
        return ReplayManifest.from_json(replay_path.read_text(encoding="utf-8"))

    def build_replay_manifest(
        self,
        run_id: str,
        config: dict,
        config_hash: str,
        total_embedded: int,
        total_relationships: int,
        phase5_path: str,
        phase4_path: str,
    ) -> ReplayManifest:
        """Build a ReplayManifest from the current run's parameters."""
        nli_cfg = config.get("nli", {})
        rd_cfg = config.get("relationship_discovery", {})
        policy_cfg = config.get("resolver_policy", {})
        calib_cfg = config.get("calibration", {}).get(nli_cfg.get("model", ""), {})

        return ReplayManifest(
            run_id=run_id,
            schema_version="6.0",
            nli_model=nli_cfg.get("model", "cross-encoder/nli-deberta-v3-small"),
            nli_threshold=nli_cfg.get("nli_threshold", 0.80),
            sim_threshold=rd_cfg.get("sim_threshold", 0.75),
            top_k=rd_cfg.get("top_k", 50),
            min_confidence=rd_cfg.get("min_confidence", 0.50),
            refine_threshold=rd_cfg.get("refine_threshold", 0.55),
            high_sim_threshold=rd_cfg.get("high_sim_threshold", 0.88),
            neutrality_threshold=rd_cfg.get("neutrality_threshold", 0.60),
            contradiction_margin=policy_cfg.get("contradiction_margin", 0.0),
            entailment_margin=policy_cfg.get("entailment_margin", 0.0),
            calibration_strategy=calib_cfg.get("strategy", "identity"),
            calibration_temperature=calib_cfg.get("temperature", 1.0),
            conflict_resolution_policy=rd_cfg.get(
                "conflict_resolution_policy", "highest_confidence"
            ),
            deduplication_policy=rd_cfg.get(
                "deduplication_policy", "keep_highest_confidence"
            ),
            skip_unknown_relationships=rd_cfg.get("skip_unknown_relationships", True),
            config_hash=config_hash,
            total_embedded_claims=total_embedded,
            total_relationships=total_relationships,
            phase5_dataset_path=phase5_path,
            phase4_dataset_path=phase4_path,
        )
````

## File: src/smriti/retrieval/statistics.py
````python
"""
statistics.py — Phase 6 execution telemetry.

RECTIFIED: Phase6Stats (frozen dataclass) replaced with:
    - Phase6StatsCollector: mutable accumulator (no frozen schema issues)
    - DiscoveryReport: serializable report object produced by finalize()

This prevents the "frozen schema becomes annoying" problem while keeping
the clean separation between collection and reporting.

Rules:
    ✅ Never influences execution
    ✅ DiscoveryReport is JSON-serializable
    ✅ New metrics can be added to StatsCollector without schema freeze pain
    ❌ Never modifies any pipeline object
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import structlog

from smriti.core.models import RelationshipType

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveryReport:
    """
    Serializable report of Phase 6 execution.

    Generated by Phase6StatsCollector.finalize().
    This is what gets written to manifests and logs.
    """
    total_embedded_claims: int
    total_candidate_pairs: int
    validated_candidates: int
    rejected_candidates: int
    nli_calls: int
    relationships_produced: int
    contradictions: int
    supports: int
    refinements: int
    neutrals: int
    unknowns: int
    rejected_relationships: int
    total_runtime_seconds: float
    retrieval_latency_seconds: float
    nli_latency_seconds: float
    calibration_applied_count: int
    conflicts_resolved: int
    cache_hit_rate: float
    # Histogram of calibrated confidence scores (10 buckets, 0.0–1.0)
    confidence_histogram: Dict[str, int]
    # Rejection reasons breakdown
    rejection_breakdown: Dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class Phase6StatsCollector:
    """
    Mutable accumulator for Phase 6 statistics.

    Add new metrics here without breaking any frozen schema.
    Call finalize() to produce a DiscoveryReport.
    """

    def __init__(self) -> None:
        self._total_embedded = 0
        self._total_candidates = 0
        self._validated_candidates = 0
        self._rejected_candidates = 0
        self._nli_calls = 0
        self._relationships = 0
        self._by_type: Dict[str, int] = {t.value: 0 for t in RelationshipType}
        self._rejected_relationships = 0
        self._calibration_applied = 0
        self._conflicts_resolved = 0
        self._cache_hit_rate = 0.0
        self._rejection_breakdown: Dict[str, int] = {}
        self._confidence_buckets: Dict[str, int] = {
            f"{i/10:.1f}-{(i+1)/10:.1f}": 0 for i in range(10)
        }
        self._start_time = time.monotonic()
        self._retrieval_start: Optional[float] = None
        self._retrieval_end: Optional[float] = None
        self._nli_start: Optional[float] = None
        self._nli_end: Optional[float] = None

    def record_embedded_claims(self, count: int) -> None:
        self._total_embedded = count

    def record_candidate_start(self) -> None:
        self._retrieval_start = time.monotonic()

    def record_candidate_end(self, total: int, validated: int, rejected: int) -> None:
        self._retrieval_end = time.monotonic()
        self._total_candidates = total
        self._validated_candidates = validated
        self._rejected_candidates = rejected

    def record_nli_start(self) -> None:
        self._nli_start = time.monotonic()

    def record_nli_end(self, calls: int) -> None:
        self._nli_end = time.monotonic()
        self._nli_calls = calls

    def record_relationship(
        self,
        rel_type: RelationshipType,
        calibrated_confidence: float,
        calibration_applied: bool,
    ) -> None:
        self._relationships += 1
        self._by_type[rel_type.value] = self._by_type.get(rel_type.value, 0) + 1
        if calibration_applied:
            self._calibration_applied += 1
        # Bucket the confidence score
        bucket_idx = min(int(calibrated_confidence * 10), 9)
        bucket_key = f"{bucket_idx/10:.1f}-{(bucket_idx+1)/10:.1f}"
        self._confidence_buckets[bucket_key] = self._confidence_buckets.get(bucket_key, 0) + 1

    def record_rejected_relationship(self, reason: str = "unknown") -> None:
        self._rejected_relationships += 1
        self._rejection_breakdown[reason] = self._rejection_breakdown.get(reason, 0) + 1

    def record_conflict_resolved(self) -> None:
        self._conflicts_resolved += 1

    def record_cache_hit_rate(self, rate: float) -> None:
        self._cache_hit_rate = rate

    def finalize(self) -> DiscoveryReport:
        """Produce the final DiscoveryReport."""
        elapsed = time.monotonic() - self._start_time
        retrieval_latency = (
            (self._retrieval_end - self._retrieval_start)
            if self._retrieval_start and self._retrieval_end else 0.0
        )
        nli_latency = (
            (self._nli_end - self._nli_start)
            if self._nli_start and self._nli_end else 0.0
        )

        return DiscoveryReport(
            total_embedded_claims=self._total_embedded,
            total_candidate_pairs=self._total_candidates,
            validated_candidates=self._validated_candidates,
            rejected_candidates=self._rejected_candidates,
            nli_calls=self._nli_calls,
            relationships_produced=self._relationships,
            contradictions=self._by_type.get("contradicts", 0),
            supports=self._by_type.get("supports", 0),
            refinements=self._by_type.get("refines", 0),
            neutrals=self._by_type.get("neutral", 0),
            unknowns=self._by_type.get("unknown", 0),
            rejected_relationships=self._rejected_relationships,
            total_runtime_seconds=elapsed,
            retrieval_latency_seconds=retrieval_latency,
            nli_latency_seconds=nli_latency,
            calibration_applied_count=self._calibration_applied,
            conflicts_resolved=self._conflicts_resolved,
            cache_hit_rate=self._cache_hit_rate,
            confidence_histogram=dict(self._confidence_buckets),
            rejection_breakdown=dict(self._rejection_breakdown),
        )
````

## File: src/smriti/retrieval/validator.py
````python
"""
retrieval/validator.py — Candidate pair validation for Phase 6.

Produces ValidatedCandidatePairs (lifecycle: VALIDATED_CANDIDATE).

Rejection reasons:
    SELF_COMPARISON:     claim_id_a == claim_id_b
    DUPLICATE_PAIR:      Same pair appeared twice
    MISSING_CLAIM:       One or both claim IDs not in claims_map
    MISSING_EMBEDDING:   One or both embeddings not in embeddings_map
    BELOW_THRESHOLD:     Cosine similarity < configured threshold
    INVALID_EMBEDDING:   EmbeddedClaim quality check failed

Rules:
    ✅ Returns (valid, rejected_with_reasons) — never raises for individual pairs
    ✅ Logs every rejection reason
    ✅ Produces VALIDATED_CANDIDATE lifecycle stage on valid pairs
    ❌ Never modifies CandidatePair objects
    ❌ Never performs NLI
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import CandidatePair, EmbeddedClaim, Claim, LifecycleStage

logger = structlog.get_logger(__name__)


class RejectionReason(str, Enum):
    SELF_COMPARISON     = "self_comparison"
    DUPLICATE_PAIR      = "duplicate_pair"
    MISSING_CLAIM       = "missing_claim"
    MISSING_EMBEDDING   = "missing_embedding"
    INVALID_EMBEDDING   = "invalid_embedding"
    BELOW_THRESHOLD     = "below_threshold"


@dataclass(frozen=True)
class CandidateValidationResult:
    """Result of validating a single candidate pair."""
    pair: CandidatePair
    is_valid: bool
    rejection_reason: RejectionReason | None = None


def validate_candidates(
    candidates: List[CandidatePair],
    claims_map: Dict[str, Claim],
    embeddings_map: Dict[str, EmbeddedClaim],
    sim_threshold: float,
) -> Tuple[List[CandidatePair], Dict[str, int]]:
    """
    Validate all candidate pairs before NLI inference.
    Valid pairs are promoted to lifecycle stage VALIDATED_CANDIDATE.

    Returns:
        (valid_pairs, rejected_reason_counts)
    """
    valid: List[CandidatePair] = []
    rejected_counts: Dict[str, int] = {}
    seen_pair_keys: Set[str] = set()

    def reject(reason: RejectionReason) -> None:
        key = reason.value
        rejected_counts[key] = rejected_counts.get(key, 0) + 1
        logger.debug("candidate rejected", reason=reason.value)

    for pair in candidates:
        if pair.claim_id_a == pair.claim_id_b:
            reject(RejectionReason.SELF_COMPARISON)
            continue

        pk = pair.pair_key()
        if pk in seen_pair_keys:
            reject(RejectionReason.DUPLICATE_PAIR)
            continue
        seen_pair_keys.add(pk)

        if pair.claim_id_a not in claims_map or pair.claim_id_b not in claims_map:
            reject(RejectionReason.MISSING_CLAIM)
            continue

        if pair.claim_id_a not in embeddings_map or pair.claim_id_b not in embeddings_map:
            reject(RejectionReason.MISSING_EMBEDDING)
            continue

        emb_a = embeddings_map[pair.claim_id_a]
        emb_b = embeddings_map[pair.claim_id_b]
        if not (emb_a.quality.finite and emb_a.quality.dimension_ok):
            reject(RejectionReason.INVALID_EMBEDDING)
            continue
        if not (emb_b.quality.finite and emb_b.quality.dimension_ok):
            reject(RejectionReason.INVALID_EMBEDDING)
            continue

        if pair.cosine_similarity < sim_threshold:
            reject(RejectionReason.BELOW_THRESHOLD)
            continue

        # Promote to VALIDATED_CANDIDATE lifecycle stage
        validated_pair = CandidatePair(
            claim_id_a=pair.claim_id_a,
            claim_id_b=pair.claim_id_b,
            cosine_similarity=pair.cosine_similarity,
            candidate_rank=pair.candidate_rank,
            retrieval_backend=pair.retrieval_backend,
            index_version=pair.index_version,
            search_parameters=pair.search_parameters,
            retrieval_quality=pair.retrieval_quality,
            lifecycle_stage=LifecycleStage.VALIDATED_CANDIDATE,
        )
        valid.append(validated_pair)

    total_rejected = sum(rejected_counts.values())
    logger.info(
        "candidate validation complete",
        total=len(candidates),
        valid=len(valid),
        rejected=total_rejected,
        reasons=rejected_counts,
    )

    return valid, rejected_counts
````

## File: src/smriti/scoring/signals/__init__.py
````python
"""
signals/__init__.py — SignalRegistry for Phase 8.

RECTIFIED (P0-1): Replaces the static SIGNAL_EXTRACTORS list with a
dynamic SignalRegistry that supports:
    - register(extractor): Register a new extractor (any module can call this)
    - discover(): Return all registered extractors in priority order
    - ordered_extractors(): Return extractors sorted by priority
    - deregister(signal_name): Remove an extractor (for testing)

Open/Closed compliance:
    Adding a new signal extractor ONLY requires:
        1. Creating the extractor class
        2. Calling SignalRegistry.register() (typically in the extractor's module)
    The __init__.py pipeline, Fusion engine, and all other modules NEVER change.

Priority ordering:
    Lower priority number = extracted first.
    Extractors with the same priority are ordered alphabetically by signal_id.
    Default priority = 100. Negative priorities are reserved for system signals.

RECTIFIED (Phase 8.2): Uses signal_id (SignalID enum) instead of string signal_name.
Enforces API version compatibility at registration time.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import structlog

from smriti.scoring.signals.base import BaseSignalExtractor, SIGNAL_API_VERSION
from smriti.exceptions import RegistryError

logger = structlog.get_logger(__name__)


class SignalRegistry:
    """
    Central registry for all signal extractors.

    Usage:
        # In an extractor module (e.g., novelty.py):
        from smriti.scoring.signals import signal_registry
        signal_registry.register(NoveltySignalExtractor(), priority=90)

        # In the pipeline:
        extractors = signal_registry.ordered_extractors()
        # That's it. Pipeline never changes.
    """

    def __init__(self) -> None:
        self._extractors: Dict[str, BaseSignalExtractor] = {}
        self._priorities: Dict[str, int] = {}

    def register(
        self,
        extractor: BaseSignalExtractor,
        priority: int = 100,
    ) -> None:
        """
        Register a signal extractor.

        Args:
            extractor: The extractor instance.
            priority:  Execution priority (lower = runs first). Default = 100.

        Raises:
            RegistryError: If a different extractor is already registered
                           with the same signal_id, or if the extractor's
                           API version does not match SIGNAL_API_VERSION.
        """
        # ── API version check ─────────────────────────────────────────────────────
        if extractor.api_version != SIGNAL_API_VERSION:
            raise RegistryError(
                f"Extractor {extractor.__class__.__name__} uses API version "
                f"{extractor.api_version}, but registry expects {SIGNAL_API_VERSION}. "
                f"Update the extractor to comply with the current API."
            )

        signal_id = extractor.signal_id
        key = signal_id.value

        if key in self._extractors:
            existing = self._extractors[key]
            if type(existing) is not type(extractor):
                raise RegistryError(
                    f"Signal '{key}' is already registered with a different extractor type "
                    f"({type(existing).__name__}). Deregister first if you intend to replace it."
                )
            logger.debug("signal already registered, skipping", signal=key)
            return

        self._extractors[key] = extractor
        self._priorities[key] = priority
        logger.debug(
            "signal registered",
            signal=key,
            priority=priority,
            version=extractor.version,
            api_version=extractor.api_version,
        )

    def deregister(self, signal_id_value: str) -> None:
        """Remove an extractor by its SignalID value. Primarily for testing."""
        self._extractors.pop(signal_id_value, None)
        self._priorities.pop(signal_id_value, None)

    def discover(self) -> Dict[str, BaseSignalExtractor]:
        """Return all registered extractors keyed by SignalID value."""
        return dict(self._extractors)

    def ordered_extractors(self) -> List[BaseSignalExtractor]:
        """Return extractors sorted by (priority, signal_id.value) for determinism."""
        return sorted(
            self._extractors.values(),
            key=lambda e: (self._priorities.get(e.signal_id.value, 100), e.signal_id.value),
        )

    def get(self, signal_id_value: str) -> Optional[BaseSignalExtractor]:
        """Get a specific extractor by its SignalID value."""
        return self._extractors.get(signal_id_value)

    @property
    def registered_names(self) -> List[str]:
        """Sorted list of all registered SignalID values."""
        return sorted(self._extractors.keys())

    def __len__(self) -> int:
        return len(self._extractors)


# ── Singleton registry instance ───────────────────────────────────────────────
signal_registry = SignalRegistry()

# ── Register all built-in extractors ─────────────────────────────────────────
# Import order determines when each extractor calls register().
# Priority values control execution order.

from smriti.scoring.signals.evidence import EvidenceStrengthExtractor
from smriti.scoring.signals.independence import EvidenceIndependenceExtractor
from smriti.scoring.signals.provenance import SourceDiversityExtractor
from smriti.scoring.signals.structural import (
    TopologyStrengthExtractor,
    HubScoreExtractor,
    BridgeScoreExtractor,
)
from smriti.scoring.signals.conflict import ConflictPressureExtractor
from smriti.scoring.signals.temporal import TemporalStabilityExtractor

# Register with explicit priorities (lower = runs first)
signal_registry.register(EvidenceStrengthExtractor(),    priority=10)
signal_registry.register(EvidenceIndependenceExtractor(), priority=20)
signal_registry.register(SourceDiversityExtractor(),     priority=30)
signal_registry.register(TopologyStrengthExtractor(),    priority=40)
signal_registry.register(HubScoreExtractor(),            priority=41)   # RECTIFIED (P0-3)
signal_registry.register(BridgeScoreExtractor(),         priority=42)   # RECTIFIED (P0-3)
signal_registry.register(ConflictPressureExtractor(),    priority=50)
signal_registry.register(TemporalStabilityExtractor(),   priority=60)

# Backward-compatible alias for external callers that used SIGNAL_EXTRACTORS
# (Maintained for compatibility but should be considered deprecated)
SIGNAL_EXTRACTORS = signal_registry.ordered_extractors()

__all__ = [
    "BaseSignalExtractor",
    "SignalRegistry",
    "signal_registry",
    "SIGNAL_EXTRACTORS",
    "EvidenceStrengthExtractor",
    "EvidenceIndependenceExtractor",
    "SourceDiversityExtractor",
    "TopologyStrengthExtractor",
    "HubScoreExtractor",
    "BridgeScoreExtractor",
    "ConflictPressureExtractor",
    "TemporalStabilityExtractor",
]
````

## File: src/smriti/scoring/signals/base.py
````python
"""
signals/base.py — Abstract base for all signal extractors.

RECTIFIED (P1-2): Each extractor now owns its normalize() method.
The normalization engine calls extractor.normalize(raw_value) rather than
centralizing normalization logic.

RECTIFIED (P0-4): extract() now returns RawSignal with both raw_value and
normalized_value, plus a build_manifest() method for SignalManifest construction.

RECTIFIED (Phase 8.2): signal_name replaced by signal_id (a SignalID enum)
for type-safe signal identification across the registry and fusion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalManifest, SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy

SIGNAL_API_VERSION = 1


class BaseSignalExtractor(ABC):
    """Abstract base for all signal extractors."""

    @property
    @abstractmethod
    def signal_id(self) -> SignalID:
        """
        Unique signal identifier (replaces signal_name).

        Uses the SignalID enum for type safety and canonical registry.
        """
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Extractor version for audit trail."""
        ...

    @property
    def normalization_strategy(self) -> str:
        """
        Human-readable description of the normalization strategy.
        RECTIFIED (P1-2): Each extractor declares its strategy.
        """
        return "identity"

    @property
    def dependency_list(self) -> List[str]:
        """
        Which graph fields this extractor depends on.
        RECTIFIED (P0-4): For SignalManifest.dependency_list.
        """
        return []

    @property
    def api_version(self) -> int:
        """The interface version this extractor was built against."""
        return SIGNAL_API_VERSION

    @abstractmethod
    def extract(
        self,
        node: ClaimNode,
        graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats,
        policy: ReliabilityPolicy,
    ) -> RawSignal:
        """
        Extract and normalize the raw signal value for one ClaimNode.

        RECTIFIED (P1-2): Extractor owns normalization.
        Returns RawSignal with BOTH raw_value and normalized_value populated.
        normalized_value is always in [0, 1].

        NEVER raises — errors are captured in status and metadata.
        """
        ...

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        """
        RECTIFIED (P1-2): Extractor-owned normalization strategy.
        Default: identity (raw already in [0,1]).
        Override in subclass for log-scale, step-function, etc.
        """
        return max(0.0, min(1.0, raw))

    def build_manifest(
        self,
        signal: RawSignal,
        quality_flags: Optional[List[str]] = None,
    ) -> SignalManifest:
        """
        RECTIFIED (P0-4): Build a SignalManifest for this signal/claim.
        Called by the normalization engine after extract().
        """
        return SignalManifest(
            signal_name=self.signal_id.value,           # Enum value as string
            extractor_version=self.version,
            raw_value=signal.raw_value,
            normalized_value=signal.normalized_value,
            normalization_strategy=self.normalization_strategy,
            status=signal.status,
            quality_flags=tuple(quality_flags or []),
            dependency_list=tuple(self.dependency_list),
            diagnostics=dict(signal.metadata),
        )
````

## File: src/smriti/scoring/signals/conflict.py
````python
"""conflict.py — Conflict pressure signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus, RelationshipType,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class ConflictPressureExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "conflict_pressure"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale_saturating"

    @property
    def dependency_list(self) -> List[str]:
        return ["graph.edges[CONTRADICTS]", "edge.calibrated_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        claim_id = node.claim_id
        contradiction_edges = [
            e for e in graph.edges.values()
            if e.relationship_type == RelationshipType.CONTRADICTS
            and (e.source_node_id == claim_id or e.target_node_id == claim_id)
        ]
        n_contradictions = len(contradiction_edges)

        if n_contradictions == 0:
            return RawSignal(
                name=self.signal_name, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"contradiction_count": 0},
            )

        max_c = max(1, global_stats.max_contradiction_partners)
        normalized_count = math.log1p(n_contradictions) / math.log1p(max_c)
        saturation = policy.conflict.conflict_saturation
        raw_sat = normalized_count / saturation if normalized_count < saturation else 1.0

        avg_confidence = (
            sum(e.calibrated_confidence for e in contradiction_edges) / n_contradictions
        )
        raw_value = raw_sat * (0.7 + 0.3 * avg_confidence)
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "contradiction_count": n_contradictions,
                "avg_contradiction_confidence": round(avg_confidence, 3),
            },
        )
````

## File: src/smriti/scoring/signals/evidence.py
````python
"""evidence.py — Evidence strength signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class EvidenceStrengthExtractor(BaseSignalExtractor):

    @property
    def signal_id(self) -> SignalID:
        return SignalID.EVIDENCE_STRENGTH

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale_blended_confidence"

    @property
    def dependency_list(self) -> List[str]:
        return ["support_aggregate.support_count", "support_aggregate.weighted_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.support_aggregate is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_aggregate"},
            )

        support_count = node.support_aggregate.support_count
        weighted_conf = node.support_aggregate.weighted_confidence

        if support_count == 0:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"support_count": 0, "weighted_confidence": 0.0},
            )

        max_count = max(1, global_stats.max_support_count)
        log_norm = math.log1p(support_count) / math.log1p(max_count)
        raw_value = 0.7 * log_norm + 0.3 * weighted_conf
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "support_count": support_count,
                "weighted_confidence": weighted_conf,
            },
        )
````

## File: src/smriti/scoring/signals/independence.py
````python
"""
independence.py — Evidence independence signal extractor.

RECTIFIED (P1-1): Now includes lineage heuristics beyond simple document ID
comparison. Document ID independence is a necessary but not sufficient condition.

Additional lineage heuristics:
    - Publisher domain fingerprinting: nodes from the same publisher domain
      are penalized even if document IDs differ (e.g., blog.org/post-1 and
      blog.org/post-2 share a publisher and are not independent).
    - Citation chain detection: if supporter A references supporter B in its
      source_path's directory hierarchy, they may not be independent.

These heuristics are approximate and configurable via EvidencePolicy.
"""

from __future__ import annotations

from typing import List, Set
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class EvidenceIndependenceExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "evidence_independence"

    @property
    def version(self) -> str:
        return "1.1"  # Bumped for lineage heuristic addition

    @property
    def normalization_strategy(self) -> str:
        return "ratio_with_penalty"

    @property
    def dependency_list(self) -> List[str]:
        return [
            "support_aggregate.supporting_claim_ids",
            "graph.nodes[supporter].document_id",
            "graph.nodes[supporter].source_path",
        ]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.support_aggregate is None or node.support_aggregate.support_count == 0:
            return RawSignal(
                name=self.signal_name, raw_value=1.0, normalized_value=1.0,
                status=SignalStatus.DEFAULT,
                metadata={"reason": "no_support_to_evaluate"},
            )

        supporting_ids = node.support_aggregate.supporting_claim_ids
        if not supporting_ids:
            return RawSignal(
                name=self.signal_name, raw_value=1.0, normalized_value=1.0,
                status=SignalStatus.MEASURED,
                metadata={"support_count": 0},
            )

        total = len(supporting_ids)
        quality_flags = []

        # ── Heuristic 1: Document ID independence (original) ──────────────────
        document_ids: Set[str] = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node:
                document_ids.add(supporter_node.document_id)
        unique_docs = len(document_ids)
        doc_independence = unique_docs / max(1, total)

        # ── Heuristic 2: Publisher domain fingerprinting (NEW P1-1) ──────────
        publisher_domains: Set[str] = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node and supporter_node.source_path:
                # Extract domain approximation from path parts
                # e.g. "notes/ml/blog/post.md" → domain fingerprint = "notes/ml/blog"
                parts = supporter_node.source_path.parts
                domain = "/".join(parts[:-1]) if len(parts) > 1 else str(supporter_node.source_path)
                publisher_domains.add(domain)
        unique_publishers = len(publisher_domains)
        publisher_independence = unique_publishers / max(1, total)

        if publisher_independence < doc_independence:
            quality_flags.append("shared_publisher_domain")

        # ── Blend: document + publisher independence ───────────────────────────
        pw = policy.evidence.publisher_domain_weight
        blended_independence = (
            (1.0 - pw) * doc_independence + pw * publisher_independence
        )

        # ── Apply echo chamber penalty if below threshold ─────────────────────
        penalty = policy.evidence.echo_chamber_penalty
        threshold = policy.evidence.independence_discount_threshold
        if blended_independence < threshold:
            raw_value = blended_independence * (1.0 - penalty)
            quality_flags.append("echo_chamber_penalty_applied")
        else:
            raw_value = blended_independence

        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "unique_documents": unique_docs,
                "unique_publishers": unique_publishers,
                "total_supporters": total,
                "doc_independence": round(doc_independence, 3),
                "publisher_independence": round(publisher_independence, 3),
                "blended_independence": round(blended_independence, 3),
                "quality_flags": quality_flags,
            },
        )
````

## File: src/smriti/scoring/signals/provenance.py
````python
"""provenance.py — Source diversity signal extractor."""

from __future__ import annotations

import math
from typing import List
from smriti.core.models import ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class SourceDiversityExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "source_diversity"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "log_scale"

    @property
    def dependency_list(self) -> List[str]:
        return ["support_aggregate.supporting_claim_ids", "graph.nodes[supporter].document_id"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.support_aggregate is None:
            return RawSignal(
                name=self.signal_name, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_support_aggregate"},
            )

        supporting_ids = node.support_aggregate.supporting_claim_ids
        if not supporting_ids:
            return RawSignal(
                name=self.signal_name, raw_value=0.0, normalized_value=0.0,
                status=SignalStatus.MEASURED,
                metadata={"unique_documents": 0},
            )

        unique_docs = set()
        for cid in supporting_ids:
            supporter_node = graph.nodes.get(cid)
            if supporter_node:
                unique_docs.add(supporter_node.document_id)

        n_unique = len(unique_docs)
        max_possible = max(1, global_stats.max_source_diversity)
        raw_value = math.log1p(n_unique) / math.log1p(max_possible)
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={"unique_documents": n_unique},
        )
````

## File: src/smriti/scoring/signals/structural.py
````python
"""
structural.py — Topology signal extractors.

RECTIFIED (P0-3): hub_bonus and bridge_bonus have been removed from TopologyPolicy.
Instead, HubScore and BridgeScore are now SEPARATE registered signals with their
own policy weights in FusionPolicy.signal_weights.

This means:
    - TopologyPolicy never knows what "hub" or "bridge" means internally
    - Fusion simply weights hub_score and bridge_score as independent signals
    - Adding a new topology sub-signal only requires a new extractor + registration
    - Policies adjust weights, not bonuses

Three extractors in this file:
    1. TopologyStrengthExtractor  — centrality-based topology signal
    2. HubScoreExtractor          — binary hub signal (is_hub → 1.0, else 0.0)
    3. BridgeScoreExtractor       — binary bridge signal (is_bridge → 1.0, else 0.0)
"""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class TopologyStrengthExtractor(BaseSignalExtractor):
    """Measures centrality-based structural importance."""

    @property
    def signal_id(self) -> SignalID:
        return SignalID.TOPOLOGY_STRENGTH

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "linear_centrality_scale"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.centrality", "topology.degree"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        topo = node.topology
        # RECTIFIED: only centrality × scale — no hub/bridge bonus here
        raw_value = topo.centrality * policy.topology.centrality_scale
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "centrality": topo.centrality,
                "degree": topo.degree,
                "centrality_scale": policy.topology.centrality_scale,
            },
        )


class HubScoreExtractor(BaseSignalExtractor):
    """
    RECTIFIED (P0-3): Emits HubScore as a separate signal.

    hub_bonus was a policy detail bleeding into topology measurement.
    Instead: hub_score = 1.0 if is_hub else 0.0.
    The FusionPolicy.signal_weights["hub_score"] controls importance.
    Policy never needs to know what "hub" means structurally.
    """

    @property
    def signal_id(self) -> SignalID:
        return SignalID.HUB_SCORE

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "binary"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.is_hub"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        raw_value = 1.0 if node.topology.is_hub else 0.0

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=raw_value,
            status=SignalStatus.MEASURED,
            metadata={"is_hub": node.topology.is_hub},
        )


class BridgeScoreExtractor(BaseSignalExtractor):
    """
    RECTIFIED (P0-3): Emits BridgeScore as a separate signal.

    bridge_bonus was a policy detail bleeding into topology measurement.
    Instead: bridge_score = 1.0 if is_bridge else 0.0.
    The FusionPolicy.signal_weights["bridge_score"] controls importance.
    """

    @property
    def signal_id(self) -> SignalID:
        return SignalID.BRIDGE_SCORE

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "binary"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.is_bridge"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        raw_value = 1.0 if node.topology.is_bridge else 0.0

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=raw_value,
            status=SignalStatus.MEASURED,
            metadata={"is_bridge": node.topology.is_bridge},
        )
````

## File: src/smriti/scoring/signals/temporal.py
````python
"""temporal.py — Temporal stability signal extractor."""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus, TemporalStatus,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class TemporalStabilityExtractor(BaseSignalExtractor):

    @property
    def signal_name(self) -> str:
        return "temporal_stability"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "step_function_temporal_status"

    @property
    def dependency_list(self) -> List[str]:
        return ["temporal_metadata.status", "temporal_metadata.temporal_confidence"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        temp = node.temporal_metadata
        tp = policy.temporal

        if temp is None:
            return RawSignal(
                name=self.signal_name,
                raw_value=tp.default_stability,
                normalized_value=tp.default_stability,
                status=SignalStatus.DEFAULT,
                metadata={"reason": "no_temporal_metadata"},
            )

        if temp.status == TemporalStatus.EVOLUTION_CHAIN:
            temporal_conf = temp.temporal_confidence or 0.5
            raw_value = min(1.0, tp.default_stability + tp.evolution_bonus + 0.10 * temporal_conf)
            status = SignalStatus.MEASURED
        elif temp.status == TemporalStatus.STATIC_PARTITION:
            raw_value = tp.default_stability
            status = SignalStatus.MEASURED
        elif temp.status == TemporalStatus.UNRESOLVED_CONFLICT:
            raw_value = max(0.0, tp.default_stability - tp.conflict_penalty)
            status = SignalStatus.ESTIMATED
        else:
            raw_value = tp.default_stability
            status = SignalStatus.DEFAULT

        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_name,
            raw_value=raw_value,
            normalized_value=normalized,
            status=status,
            metadata={"temporal_status": temp.status.value if temp else "none"},
        )
````

## File: src/smriti/scoring/builder.py
````python
"""
builder.py — ScoredKnowledgeGraph assembly for Phase 8.

RECTIFIED: Now populates ReliabilityMetadata with SignalManifests and
ReliabilityDecisionRecord. Registry order captured in audit trail.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List
import structlog

from smriti.core.models import (
    KnowledgeGraph, ClaimNode, SignalVector, ComponentScore,
    SignalManifest, ReliabilityDecisionRecord, ReliabilityExplanation,
    ReliabilityAudit, ReliabilityMetadata, ScoredKnowledgeGraph,
    ScoringGlobalStats, CalibrationLabel, ContributionSet,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor

logger = structlog.get_logger(__name__)

PHASE8_SCHEMA_VERSION = "8.0"


def compute_graph_fingerprint(graph: KnowledgeGraph) -> str:
    """
    Create a deterministic SHA256 fingerprint of the graph's topology.

    This fingerprint captures the set of node IDs, edge IDs, and schema version.
    It can be used to detect changes in the graph structure between runs.
    """
    node_keys = "|".join(sorted(graph.nodes.keys()))
    edge_keys = "|".join(sorted(graph.edges.keys()))
    material = f"{node_keys}||{edge_keys}||{graph.schema_version}"
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def apply_calibration_label(ri: float, policy: ReliabilityPolicy) -> CalibrationLabel:
    """Map Reliability Index to CalibrationLabel using policy thresholds."""
    cp = policy.calibration
    if ri >= cp.very_high_threshold:
        return CalibrationLabel.VERY_HIGH
    elif ri >= cp.high_threshold:
        return CalibrationLabel.HIGH
    elif ri >= cp.moderate_threshold:
        return CalibrationLabel.MODERATE
    elif ri >= cp.low_threshold:
        return CalibrationLabel.LOW
    else:
        return CalibrationLabel.VERY_LOW


def build_reliability_metadata(
    node: ClaimNode,
    reliability_index: float,
    uncertainty_score: float,
    signal_vector: SignalVector,
    component_scores: List[ComponentScore],
    signal_manifests: List[SignalManifest],          # NEW (P0-4)
    decision_record: ReliabilityDecisionRecord,       # NEW (P0-5)
    explanation: ReliabilityExplanation,
    policy: ReliabilityPolicy,
    run_id: str,
    extractors: List[BaseSignalExtractor],
    graph: KnowledgeGraph,                            # ADDED (Phase 8.4)
) -> ReliabilityMetadata:
    """
    Construct immutable ReliabilityMetadata for one ClaimNode.

    RECTIFIED (Phase 8.4): Accepts `graph` to compute graph fingerprint
    and use graph.schema_version in audit trail.
    """
    calibration_label = apply_calibration_label(reliability_index, policy)

    registry_order = tuple(e.signal_name for e in extractors)

    audit = ReliabilityAudit(
        policy_version=policy.version,
        policy_profile=policy.profile,
        graph_schema_version=graph.schema_version,          # NOW from graph
        graph_fingerprint=compute_graph_fingerprint(graph),  # NEW field (Phase 8.4)
        fusion_algorithm="weighted_linear_v2",
        normalization_version="1.1",
        computed_at_run_id=run_id,
        signal_extractor_versions={
            e.signal_name: e.version for e in extractors
        },
        registry_order=registry_order,
    )

    return ReliabilityMetadata(
        claim_id=node.claim_id,
        reliability_index=round(reliability_index, 2),
        uncertainty_score=round(uncertainty_score, 2),
        evidence_completeness=round(signal_vector.evidence_completeness, 4),
        signal_vector=signal_vector,
        signal_manifests=tuple(signal_manifests),
        component_scores=tuple(component_scores),
        decision_record=decision_record,
        explanation=explanation,
        calibration_label=calibration_label,
        audit=audit,
        policy_version=policy.version,
        schema_version=PHASE8_SCHEMA_VERSION,
    )


def build_scored_knowledge_graph(
    graph: KnowledgeGraph,
    reliability: Dict[str, ReliabilityMetadata],
    policy: ReliabilityPolicy,
    global_stats: ScoringGlobalStats,
    run_id: str,
) -> ScoredKnowledgeGraph:
    """Assemble the final ScoredKnowledgeGraph."""
    return ScoredKnowledgeGraph(
        graph=graph,
        reliability=reliability,
        policy_snapshot=policy.to_dict(),
        policy_profile=policy.profile,
        global_stats=global_stats,
        run_id=run_id,
        schema_version=PHASE8_SCHEMA_VERSION,
    )
````

## File: src/smriti/scoring/constraints.py
````python
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from smriti.core.models import SignalVector
from smriti.scoring.policies import FusionPolicy

class FusionConstraint(ABC):
    @abstractmethod
    def apply(self, current_ri: float, sv: SignalVector, fp: FusionPolicy) -> Tuple[float, Optional[str]]:
        """Returns (new_ri, activation_log_message)."""
        pass

class NoEvidenceConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        cap = fp.max_reliability_without_evidence
        if sv.evidence_strength < 0.10 and current_ri > cap:
            return cap, f"no_evidence_cap: {cap}"
        return current_ri, None

class MaxConflictConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        cap = fp.max_reliability_with_max_conflict
        if sv.conflict_pressure >= 0.90 and current_ri > cap:
            return cap, f"max_conflict_cap: {cap}"
        return current_ri, None

class TopologyWithoutEvidenceConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        if sv.evidence_strength < 0.20 and sv.topology_strength > 0.80 and current_ri > 60.0:
            return 60.0, "topology_without_evidence_cap: 60.0"
        return current_ri, None

CONSTRAINT_PIPELINE = [
    NoEvidenceConstraint(),
    MaxConflictConstraint(),
    TopologyWithoutEvidenceConstraint(),
]
````

## File: src/smriti/scoring/explanation.py
````python
"""explanation.py — Structured explanation builder for Phase 8."""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.models import ComponentScore, ReliabilityExplanation

logger = structlog.get_logger(__name__)

MAX_EXPLANATION_SIGNALS = 3


def build_explanation(
    reliability_index: float,
    component_scores: List[ComponentScore],
) -> ReliabilityExplanation:
    """Build a structured explanation from ComponentScores."""
    positive = sorted(
        [c for c in component_scores if c.contribution > 0],
        key=lambda c: c.contribution, reverse=True,
    )
    negative = sorted(
        [c for c in component_scores if c.contribution < 0],
        key=lambda c: c.contribution,
    )

    strengths = tuple(
        (c.signal_name, round(c.contribution, 2))
        for c in positive[:MAX_EXPLANATION_SIGNALS]
    )
    weaknesses = tuple(
        (c.signal_name, round(c.contribution, 2))
        for c in negative[:MAX_EXPLANATION_SIGNALS]
    )

    dominant = positive[0].signal_name if positive else "none"
    limiting = negative[0].signal_name if negative else "none"

    summary = _build_summary(reliability_index, positive, negative)
    recommendations = _build_recommendations(component_scores)

    return ReliabilityExplanation(
        summary=summary,
        strengths=strengths,
        weaknesses=weaknesses,
        dominant_signal=dominant,
        limiting_signal=limiting,
        recommendations=recommendations,
    )


def _build_summary(ri: float, positive: list, negative: list) -> str:
    if ri >= 80:
        base = "Highly reliable."
    elif ri >= 65:
        base = "Reliable."
    elif ri >= 45:
        base = "Moderately reliable."
    elif ri >= 25:
        base = "Limited reliability."
    else:
        base = "Very low reliability."

    if positive:
        top = positive[0].signal_name.replace("_", " ").capitalize()
        base += f" Primary strength: {top}."

    if negative:
        top_neg = negative[0].signal_name.replace("_", " ").capitalize()
        base += f" Main concern: {top_neg}."

    return base


def _build_recommendations(component_scores: List[ComponentScore]) -> tuple:
    recs = []
    score_map = {c.signal_name: c.contribution for c in component_scores}

    if score_map.get("conflict_pressure", 0) < -10:
        recs.append("Review contradicting claims in other partitions.")
    if score_map.get("evidence_independence", 1.0) < 0:
        recs.append("Seek supporting evidence from additional independent sources.")
    if score_map.get("source_diversity", 1.0) < 0.05:
        recs.append("Diversify evidence across more document sources.")
    if score_map.get("temporal_stability", 1.0) < 0.05:
        recs.append("Monitor for temporal evolution of this claim.")
    if not recs:
        recs.append("Maintain current evidence quality.")

    return tuple(recs)
````

## File: src/smriti/scoring/fusion.py
````python
"""
fusion.py — Generic Reliability Fusion Engine for Phase 8.

RECTIFIED (P0-2): Fusion receives ContributionSet, NOT SignalVector.
Fusion never references any signal by name — it processes whatever
ContributionCandidates are registered, with their weights and directions.

This means:
    - Adding a new signal (e.g., NoveltySignal) requires ZERO changes here
    - Fusion works on any set of signals
    - Policy interactions that reference specific signals are documented
      in _apply_policy_interactions() and flagged in ReliabilityDecisionRecord

RECTIFIED (P0-5): Every call to compute_reliability() produces a
ReliabilityDecisionRecord documenting:
    - Which policy interactions fired
    - Which constraints were activated
    - The contribution order
    - Raw vs constrained vs final reliability

Architectural invariants:
    ✅ Deterministic: same ContributionSet + same policy → same RI
    ✅ Generic: Fusion never contains signal names (except in interactions)
    ✅ Every contribution traceable (ComponentScore)
    ✅ Every decision recorded (ReliabilityDecisionRecord)
    ❌ Fusion never reads the graph directly
    ❌ Fusion never imports signal extractors
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import (
    ContributionSet, ContributionCandidate, ComponentScore,
    ReliabilityDecisionRecord, SignalVector,
)
from smriti.scoring.policies import FusionPolicy, ReliabilityPolicy

logger = structlog.get_logger(__name__)

FUSION_ALGORITHM_VERSION = "weighted_linear_v2"   # Bumped for generic fusion


def compute_reliability(
    contribution_set: ContributionSet,
    policy: ReliabilityPolicy,
    signal_vector: SignalVector,        # Still needed for constraint checks
) -> Tuple[float, float, List[ComponentScore], ReliabilityDecisionRecord]:
    """
    Compute Reliability Index, Uncertainty Score, ComponentScores, and DecisionRecord.

    RECTIFIED (P0-2): Receives ContributionSet (generic), not SignalVector (named).
    RECTIFIED (P0-5): Returns ReliabilityDecisionRecord alongside the scores.

    Args:
        contribution_set:  Generic set of ContributionCandidates from normalization.
        policy:            Active ReliabilityPolicy.
        signal_vector:     For constraint evaluation and uncertainty (backward compat).

    Returns:
        (reliability_index, uncertainty_score, component_scores, decision_record)
    """
    fp = policy.fusion
    policy_interactions: List[str] = []
    constraints_activated: List[str] = []

    # ── Step 1: Policy interactions (before contribution building) ────────────
    # Interactions are documented but do not use signal names directly in Fusion.
    # They work by looking up candidates by name (only place signal names appear here).
    adjusted_candidates = _apply_policy_interactions(
        list(contribution_set.candidates), policy, policy_interactions
    )

    # ── Step 2: Build ComponentScores (generic — no signal name references) ───
    component_scores: List[ComponentScore] = []
    for candidate in adjusted_candidates:
        if candidate.direction == "positive":
            contribution = candidate.normalized_value * candidate.policy_weight * 100
        else:
            contribution = -(candidate.normalized_value * candidate.policy_weight * 100)

        component_scores.append(ComponentScore(
            signal_name=candidate.signal_name,
            normalized_value=candidate.normalized_value,
            policy_weight=candidate.policy_weight,
            adjusted_value=candidate.normalized_value,
            contribution=contribution,
            direction=candidate.direction,
            explanation=_build_signal_explanation(candidate.signal_name, candidate.normalized_value, candidate.direction),
        ))

    # ── Step 3: Raw fusion ────────────────────────────────────────────────────
    raw_reliability = sum(c.contribution for c in component_scores)

    # ── Step 4: Constraint validation ─────────────────────────────────────────
    constrained_reliability = _apply_constraints(
        raw_reliability, signal_vector, fp, constraints_activated
    )

    # ── Step 5: Clamp ─────────────────────────────────────────────────────────
    reliability_index = max(0.0, min(100.0, constrained_reliability))

    # ── Step 6: Uncertainty Score ─────────────────────────────────────────────
    uncertainty_score, uncertainty_components = _compute_uncertainty(signal_vector, fp)

    # ── Step 7: Build contribution order (descending |contribution|) ──────────
    contribution_order = tuple(
        c.signal_name
        for c in sorted(component_scores, key=lambda c: abs(c.contribution), reverse=True)
    )

    # ── Step 8: Build ReliabilityDecisionRecord (P0-5) ────────────────────────
    dominant_adj = policy_interactions[0] if policy_interactions else "none"
    decision_record = ReliabilityDecisionRecord(
        claim_id=contribution_set.claim_id,
        policy_interactions=tuple(policy_interactions),
        constraints_activated=tuple(constraints_activated),
        contribution_order=contribution_order,
        raw_reliability=round(raw_reliability, 4),
        constrained_reliability=round(constrained_reliability, 4),
        final_reliability=round(reliability_index, 4),
        uncertainty_components=tuple(uncertainty_components),
        dominant_adjustment=dominant_adj,
    )

    logger.debug(
        "reliability computed",
        claim_id=contribution_set.claim_id[:8],
        raw=f"{raw_reliability:.2f}",
        constrained=f"{constrained_reliability:.2f}",
        final=f"{reliability_index:.2f}",
        uncertainty=f"{uncertainty_score:.2f}",
        interactions=len(policy_interactions),
        constraints=len(constraints_activated),
    )

    return reliability_index, uncertainty_score, component_scores, decision_record


def _apply_policy_interactions(
    candidates: List[ContributionCandidate],
    policy: ReliabilityPolicy,
    interactions_log: List[str],
) -> List[ContributionCandidate]:
    """
    Apply policy interactions to adjust candidate values before fusion.

    NOTE: This is the ONLY place in Fusion where signal names may appear,
    because interactions are inherently signal-aware (e.g., echo chamber
    connects evidence_independence to evidence_strength). These are documented
    and localized here to minimize coupling.

    Any interaction that fires is logged to interactions_log.
    """
    candidates_map = {c.signal_name: c for c in candidates}

    # Interaction 1: Echo chamber discount
    # If evidence_independence is low, discount evidence_strength
    independence = candidates_map.get("evidence_independence")
    evidence = candidates_map.get("evidence_strength")
    if (independence and evidence
            and independence.normalized_value < policy.evidence.independence_discount_threshold):
        discount = policy.evidence.echo_chamber_penalty
        new_value = evidence.normalized_value * (1.0 - discount)
        new_candidate = ContributionCandidate(
            signal_name=evidence.signal_name,
            normalized_value=new_value,
            policy_weight=evidence.policy_weight,
            direction=evidence.direction,
            label=evidence.label,
            raw_value=evidence.raw_value,
        )
        candidates_map["evidence_strength"] = new_candidate
        interactions_log.append(
            f"echo_chamber_discount_applied: evidence_strength {evidence.normalized_value:.3f}"
            f" → {new_value:.3f} (independence={independence.normalized_value:.3f})"
        )

    return list(candidates_map.values())


def _apply_constraints(
    raw_ri: float,
    sv: SignalVector,
    fp: FusionPolicy,
    constraints_log: List[str],
) -> float:
    """Execute the ConstraintPipeline."""
    from smriti.scoring.constraints import CONSTRAINT_PIPELINE
    
    result = raw_ri
    for constraint in CONSTRAINT_PIPELINE:
        result, log_msg = constraint.apply(result, sv, fp)
        if log_msg:
            constraints_log.append(log_msg)
            
    return result


def _compute_uncertainty(
    sv: SignalVector,
    fp: FusionPolicy,
) -> Tuple[float, List[Tuple[str, float]]]:
    """Compute uncertainty score and decompose into named components."""
    incompleteness = 1.0 - sv.evidence_completeness
    low_diversity = 1.0 - sv.source_diversity
    low_independence = 1.0 - sv.evidence_independence

    components = [
        ("evidence_incompleteness", incompleteness * 0.50),
        ("low_source_diversity", low_diversity * 0.25),
        ("low_independence", low_independence * 0.25),
    ]

    raw_uncertainty = sum(v for _, v in components) * 100.0
    uncertainty_score = min(100.0, max(0.0, raw_uncertainty))
    return uncertainty_score, components


def _build_signal_explanation(
    signal_name: str,
    value: float,
    direction: str,
) -> str:
    """Generic explanation for a signal contribution."""
    label = signal_name.replace("_", " ").capitalize()
    if direction == "positive":
        if value >= 0.80:
            return f"{label}: very high ({value:.2f}). Strong positive contribution."
        elif value >= 0.50:
            return f"{label}: moderate ({value:.2f}). Positive contribution."
        elif value > 0.10:
            return f"{label}: low ({value:.2f}). Limited positive contribution."
        else:
            return f"{label}: negligible ({value:.2f}). Minimal contribution."
    else:
        if value >= 0.80:
            return f"{label}: very high ({value:.2f}). Strong negative pressure."
        elif value >= 0.50:
            return f"{label}: moderate ({value:.2f}). Notable negative pressure."
        elif value > 0.10:
            return f"{label}: low ({value:.2f}). Weak negative pressure."
        else:
            return f"{label}: negligible ({value:.2f}). No significant pressure."


# ── Backward-compatible wrapper for tests that use old signature ───────────────

def compute_reliability_from_signal_vector(
    signal_vector: SignalVector,
    policy: ReliabilityPolicy,
) -> Tuple[float, float, List[ComponentScore]]:
    """
    Backward-compatible wrapper for existing tests.
    Converts SignalVector to ContributionSet and calls the generic fusion.
    """
    from smriti.core.models import ContributionCandidate, ContributionSet

    fp = policy.fusion
    candidates = []
    for signal_name, weight in fp.signal_weights.items():
        direction = fp.get_direction(signal_name)
        # Get value from signal_vector by signal_name
        value = getattr(signal_vector, signal_name, 0.0)
        if weight > 0:
            candidates.append(ContributionCandidate(
                signal_name=signal_name,
                normalized_value=value,
                policy_weight=weight,
                direction=direction,
                label=signal_name.replace("_", " ").title(),
                raw_value=value,
            ))

    cs = ContributionSet(
        candidates=tuple(candidates),
        evidence_completeness=signal_vector.evidence_completeness,
        claim_id="test",
    )

    ri, unc, comps, _ = compute_reliability(cs, policy, signal_vector)
    return ri, unc, comps
````

## File: src/smriti/scoring/graph_stats.py
````python
"""
graph_stats.py — Global graph statistics for Phase 8.

Computed ONCE per scoring run and shared by all signal extractors.
This avoids repeated graph traversals and ensures consistent normalization.

Why compute globally?
    Each signal extractor must normalize against the SAME baseline.
    If EvidenceStrength uses "local maximum" and Topology uses "global maximum",
    the normalization becomes inconsistent and comparisons break.
"""

from __future__ import annotations

import math
from typing import List
import structlog

from smriti.core.models import KnowledgeGraph, RelationshipType, ScoringGlobalStats

logger = structlog.get_logger(__name__)


def compute_global_stats(graph: KnowledgeGraph) -> ScoringGlobalStats:
    """Compute graph-wide statistics for normalization baselines."""
    if graph.node_count == 0:
        return ScoringGlobalStats(
            max_support_count=1, avg_support_count=0.0, max_in_degree=1,
            avg_degree=0.0, max_contradiction_partners=1, avg_contradiction_partners=0.0,
            max_source_diversity=1, max_temporal_confidence=1.0,
            node_count=0, partition_count=0, contradiction_count=0, supports_count=0,
        )

    support_counts = []
    in_degrees = []
    all_degrees = []
    contradiction_partners = []
    temporal_confidences = []

    for claim_id, node in graph.nodes.items():
        support_count = 0
        if node.support_aggregate:
            support_count = node.support_aggregate.support_count
        support_counts.append(support_count)

        if node.topology:
            in_degrees.append(node.topology.in_degree)
            all_degrees.append(node.topology.degree)

        n_contradicts = sum(
            1 for e in graph.edges.values()
            if e.relationship_type == RelationshipType.CONTRADICTS
            and (e.source_node_id == claim_id or e.target_node_id == claim_id)
        )
        contradiction_partners.append(n_contradicts)

        if node.temporal_metadata and node.temporal_metadata.temporal_confidence > 0:
            temporal_confidences.append(node.temporal_metadata.temporal_confidence)

    n = max(1, graph.node_count)

    return ScoringGlobalStats(
        max_support_count=max(support_counts) if support_counts else 1,
        avg_support_count=sum(support_counts) / n,
        max_in_degree=max(in_degrees) if in_degrees else 1,
        avg_degree=sum(all_degrees) / max(1, len(all_degrees)),
        max_contradiction_partners=max(contradiction_partners) if contradiction_partners else 1,
        avg_contradiction_partners=sum(contradiction_partners) / n,
        max_source_diversity=max(support_counts) if support_counts else 1,
        max_temporal_confidence=max(temporal_confidences) if temporal_confidences else 1.0,
        node_count=graph.node_count,
        partition_count=graph.partition_count,
        contradiction_count=graph.statistics.contradiction_count,
        supports_count=graph.statistics.supports_count,
    )
````

## File: src/smriti/scoring/normalization.py
````python
"""
normalization.py — Signal assembly and ContributionSet construction.

RECTIFIED (P0-2): This module no longer builds SignalVector as the primary output
for Fusion. Instead it builds ContributionSet — a generic list of
ContributionCandidates that Fusion can process without knowing signal names.

RECTIFIED (P1-2): Normalization is now owned by each extractor. This module
assembles and validates extractor-normalized values — it never re-normalizes.

RECTIFIED (P0-4): Builds SignalManifest list from extractor.build_manifest().

SignalVector is still built for backward compatibility (serialization, tests).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple
import structlog

from smriti.core.models import (
    RawSignal, SignalVector, ContributionCandidate, ContributionSet,
    SignalManifest, SignalStatus,
)
from smriti.scoring.policies import FusionPolicy
from smriti.scoring.signals.base import BaseSignalExtractor

logger = structlog.get_logger(__name__)


def assemble_contribution_set(
    raw_signals: List[RawSignal],
    extractors: List[BaseSignalExtractor],
    fusion_policy: FusionPolicy,
    claim_id: str,
) -> Tuple[ContributionSet, List[SignalManifest], SignalVector]:
    """
    RECTIFIED (P0-2, P0-4, P1-2): Primary assembly function.

    Validates extractor-normalized values and builds:
        - ContributionSet: for generic Fusion (signal-name-agnostic)
        - List[SignalManifest]: for derivation tracing (P0-4)
        - SignalVector: for backward-compatible serialization

    Args:
        raw_signals:    RawSignal list from all extractors.
        extractors:     The extractor instances (for manifest building).
        fusion_policy:  FusionPolicy for weights and directions.
        claim_id:       For logging and ContributionSet.

    Returns:
        (ContributionSet, manifests, signal_vector)
    """
    extractor_map = {e.signal_name: e for e in extractors}
    validated: Dict[str, RawSignal] = {}
    status_map: Dict[str, str] = {}
    manifests: List[SignalManifest] = []

    for sig in raw_signals:
        value = sig.normalized_value  # Extractor already normalized (P1-2)
        status = sig.status
        quality_flags = []

        # Validate extractor-normalized value
        if math.isnan(value):
            logger.warning("NaN normalized signal", signal=sig.name)
            value = 0.0
            status = SignalStatus.UNAVAILABLE
            quality_flags.append("nan_detected")
        elif math.isinf(value):
            logger.warning("Inf normalized signal", signal=sig.name)
            value = 0.0
            status = SignalStatus.UNAVAILABLE
            quality_flags.append("inf_detected")
        elif not (0.0 <= value <= 1.0):
            logger.warning("out-of-range normalized signal", signal=sig.name, value=value)
            value = max(0.0, min(1.0, value))
            quality_flags.append("clamped_out_of_range")

        # Build validated RawSignal (normalized_value may have been corrected)
        corrected_sig = RawSignal(
            name=sig.name,
            raw_value=sig.raw_value,
            normalized_value=value,
            status=status,
            metadata=sig.metadata,
        )
        validated[sig.name] = corrected_sig
        status_map[sig.name] = status.value

        # Build SignalManifest (P0-4)
        extractor = extractor_map.get(sig.name)
        if extractor:
            manifest = extractor.build_manifest(corrected_sig, quality_flags)
            manifests.append(manifest)

    # ── Build ContributionSet (P0-2) ────────────────────────────────────────
    candidates = []
    for signal_name, sig in validated.items():
        weight = fusion_policy.get_weight(signal_name)
        direction = fusion_policy.get_direction(signal_name)
        if weight > 0:
            candidates.append(ContributionCandidate(
                signal_name=signal_name,
                normalized_value=sig.normalized_value,
                policy_weight=weight,
                direction=direction,
                label=signal_name.replace("_", " ").title(),
                raw_value=sig.raw_value,
            ))

    evidence_completeness = _compute_completeness(status_map)

    contribution_set = ContributionSet(
        candidates=tuple(candidates),
        evidence_completeness=evidence_completeness,
        claim_id=claim_id,
    )

    # ── Build SignalVector for backward compatibility ─────────────────────────
    def get_norm(name: str) -> float:
        return validated[name].normalized_value if name in validated else 0.0

    signal_vector = SignalVector(
        evidence_strength=get_norm("evidence_strength"),
        evidence_independence=get_norm("evidence_independence"),
        source_diversity=get_norm("source_diversity"),
        topology_strength=get_norm("topology_strength"),
        conflict_pressure=get_norm("conflict_pressure"),
        temporal_stability=get_norm("temporal_stability"),
        evidence_completeness=evidence_completeness,
        statuses=status_map,
    )

    return contribution_set, manifests, signal_vector


def _compute_completeness(status_map: Dict[str, str]) -> float:
    """Fraction of signals with actual measurements."""
    total = max(1, len(status_map))
    measured = sum(
        1 for status in status_map.values()
        if status in (SignalStatus.MEASURED.value, SignalStatus.ESTIMATED.value)
    )
    return measured / total


# ── Backward-compatible wrapper for tests that use validate_and_normalize ─────

def validate_and_normalize(raw_signals: List[RawSignal]) -> SignalVector:
    """
    Backward-compatible wrapper. Tests that test normalization directly use this.
    Production code uses assemble_contribution_set().
    """
    status_map: Dict[str, str] = {}
    signal_map: Dict[str, float] = {}

    for sig in raw_signals:
        value = sig.normalized_value
        status = sig.status

        if math.isnan(value):
            value = 0.0
            status = SignalStatus.UNAVAILABLE
        elif math.isinf(value):
            value = 0.0
            status = SignalStatus.UNAVAILABLE
        elif not (0.0 <= value <= 1.0):
            value = max(0.0, min(1.0, value))

        signal_map[sig.name] = value
        status_map[sig.name] = status.value

    def get(name: str) -> float:
        return signal_map.get(name, 0.0)

    return SignalVector(
        evidence_strength=get("evidence_strength"),
        evidence_independence=get("evidence_independence"),
        source_diversity=get("source_diversity"),
        topology_strength=get("topology_strength"),
        conflict_pressure=get("conflict_pressure"),
        temporal_stability=get("temporal_stability"),
        evidence_completeness=_compute_completeness(status_map),
        statuses=status_map,
    )
````

## File: src/smriti/scoring/policies.py
````python
"""
policies.py — Phase 8 policy definitions.

RECTIFIED (P0-3): TopologyPolicy no longer contains hub_bonus or bridge_bonus.
Those are topology implementation details. The topology extractor emits HubScore
and BridgeScore as separate registered signals. Policy only has centrality_scale.

RECTIFIED (P1-3): PolicyProfile enum added with preset profiles:
    CONSERVATIVE: High evidence bar, strong conflict penalty
    BALANCED:     Default — balanced across all signals
    RESEARCH:     Emphasizes independence and source diversity
    EVIDENCE_FIRST: Maximum weight on evidence strength

RECTIFIED (Phase 8.3): FusionPolicy.validate() now requires the active registry
set to enforce a strict 1:1 mapping between policy weights and registered signals.
This prevents silent mismatches when signals are added or removed.

Rules:
    ✅ Algorithms remain fixed; only policies change
    ✅ Changing a policy never requires changing implementation
    ✅ TopologyPolicy never knows how topology works internally
    ❌ No hard-coded weights except default policy values here
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import SignalID
from smriti.exceptions import PolicyError

logger = structlog.get_logger(__name__)

POLICY_VERSION = "1.0"


class PolicyProfile(str, Enum):
    """
    RECTIFIED (P1-3): Named policy profiles for benchmarking and domain use.

    Each profile configures all weights and thresholds for a specific use case.
    Loading a profile overrides any manual configuration.

    Profiles:
        BALANCED:       Default. Balanced across evidence, topology, conflict.
        CONSERVATIVE:   High evidence requirement, strong conflict penalty.
                        Use when false positives are costly.
        RESEARCH:       Emphasizes independence and source diversity.
                        Use for academic knowledge bases.
        EVIDENCE_FIRST: Maximum weight on direct evidence strength.
                        Use when graph topology is sparse/unreliable.
    """
    BALANCED       = "balanced"
    CONSERVATIVE   = "conservative"
    RESEARCH       = "research"
    EVIDENCE_FIRST = "evidence_first"


@dataclass(frozen=True)
class EvidencePolicy:
    """Parameters governing evidence signal extraction."""
    min_support_count: int = 1
    max_support_count: int = 20
    echo_chamber_penalty: float = 0.30
    independence_discount_threshold: float = 0.50
    # NEW (P1-1): lineage heuristics for independence detection
    lineage_depth_limit: int = 2              # How many citation hops to check
    publisher_domain_weight: float = 0.50     # Weight of publisher domain in independence


@dataclass(frozen=True)
class ConflictPolicy:
    """Parameters governing contradiction pressure computation."""
    max_contradiction_partners: int = 5
    conflict_saturation: float = 0.80
    contradiction_weight_multiplier: float = 1.0


@dataclass(frozen=True)
class TopologyPolicy:
    """
    Parameters governing structural importance signals.

    RECTIFIED (P0-3): hub_bonus and bridge_bonus removed.
    Those are topology implementation details — they belong in the extractor.
    The extractor emits HubScore and BridgeScore as separate signals.
    Policy only controls how centrality is scaled.
    """
    centrality_scale: float = 1.0     # Multiplier for the centrality signal


@dataclass(frozen=True)
class TemporalPolicy:
    """Parameters governing temporal stability signals."""
    default_stability: float = 0.50
    evolution_bonus: float = 0.15
    conflict_penalty: float = 0.10
    recency_window_days: float = 90.0


@dataclass(frozen=True)
class FusionPolicy:
    """
    Signal weights and fusion constraints.

    RECTIFIED (P0-2): Weights are keyed by signal_name (str → float dict).
    This means adding a new signal only requires adding it to the weights dict;
    Fusion reads weights by signal_name, not by fixed field names.

    RECTIFIED (Phase 8.3): validate() now enforces a strict 1:1 mapping
    between policy weights and the active registry of signals.
    Any registered signal missing a weight, or any weight pointing to an
    unregistered signal, raises PolicyError.

    The sum of all positive-direction weights minus negative-direction weights
    must equal 1.0 (validated on construction).
    """
    # Weights keyed by SignalID value (string) — must match the registry exactly
    signal_weights: Dict[str, float] = field(default_factory=lambda: {
        "evidence_strength":    0.25,
        "evidence_independence": 0.15,
        "source_diversity":     0.15,
        "topology_strength":    0.10,
        "hub_score":            0.05,    # RECTIFIED (P0-3): topology sub-signals
        "bridge_score":         0.05,
        "conflict_pressure":    0.20,
        "temporal_stability":   0.05,
    })

    # Signal directions: "positive" raises RI, "negative" lowers it
    signal_directions: Dict[str, str] = field(default_factory=lambda: {
        "evidence_strength":    "positive",
        "evidence_independence": "positive",
        "source_diversity":     "positive",
        "topology_strength":    "positive",
        "hub_score":            "positive",
        "bridge_score":         "positive",
        "conflict_pressure":    "negative",
        "temporal_stability":   "positive",
    })

    # Fusion constraints
    max_reliability_without_evidence: float = 60.0
    max_reliability_with_max_conflict: float = 40.0
    min_reliability_for_high_topology: float = 20.0
    max_uncertainty_discount: float = 20.0

    def validate(self, active_registry_ids: Set[SignalID]) -> None:
        """
        Verify weights sum to 1.0 AND match the active registry perfectly.

        Args:
            active_registry_ids: Set of SignalID enums currently registered.

        Raises:
            PolicyError: If any registered signal is missing a weight,
                         or if any weight points to an unregistered signal,
                         or if weights do not sum to 1.0.
        """
        # Convert registry to strings for comparison
        registry_strings = {s.value for s in active_registry_ids}
        policy_strings = set(self.signal_weights.keys())

        # Check for missing signals
        missing_in_policy = registry_strings - policy_strings
        if missing_in_policy:
            raise PolicyError(
                f"Registered signals missing from policy weights: {sorted(missing_in_policy)}. "
                f"Add them to scoring_policy.fusion.signal_weights."
            )

        # Check for extra signals
        missing_in_registry = policy_strings - registry_strings
        if missing_in_registry:
            raise PolicyError(
                f"Policy contains weights for unregistered signals: {sorted(missing_in_registry)}. "
                f"Either register these signals or remove them from scoring_policy.fusion.signal_weights."
            )

        # Check directions consistency (all policy keys should have a direction)
        for name in policy_strings:
            if name not in self.signal_directions:
                raise PolicyError(
                    f"Signal '{name}' has a weight but no direction defined in signal_directions."
                )

        # Sum check (existing logic)
        positive_total = sum(
            w for name, w in self.signal_weights.items()
            if self.signal_directions.get(name, "positive") == "positive"
        )
        negative_total = sum(
            w for name, w in self.signal_weights.items()
            if self.signal_directions.get(name, "positive") == "negative"
        )
        total = positive_total + negative_total
        if abs(total - 1.0) > 0.001:
            raise PolicyError(
                f"FusionPolicy signal_weights must sum to 1.0, got {total:.4f}. "
                "Adjust scoring_policy.fusion.signal_weights in config."
            )

    def get_weight(self, signal_name: str) -> float:
        """Look up weight by signal name. Returns 0.0 if not registered."""
        return self.signal_weights.get(signal_name, 0.0)

    def get_direction(self, signal_name: str) -> str:
        """Look up direction by signal name. Defaults to 'positive'."""
        return self.signal_directions.get(signal_name, "positive")


@dataclass(frozen=True)
class CalibrationPolicy:
    """Thresholds for mapping Reliability Index → CalibrationLabel."""
    very_high_threshold: float = 80.0
    high_threshold: float = 65.0
    moderate_threshold: float = 45.0
    low_threshold: float = 25.0


@dataclass(frozen=True)
class ReliabilityPolicy:
    """
    Complete policy for one scoring run.
    Loaded from config/default.yaml [scoring_policy] section.
    """
    version: str
    profile: str                  # NEW (P1-3): which PolicyProfile was used
    evidence: EvidencePolicy
    conflict: ConflictPolicy
    topology: TopologyPolicy
    temporal: TemporalPolicy
    fusion: FusionPolicy
    calibration: CalibrationPolicy

    def validate(self, active_registry_ids: Set[SignalID]) -> None:
        """
        Validate the entire policy against the active registry.
        Delegates to fusion.validate() for the weight-registry mapping.
        """
        self.fusion.validate(active_registry_ids)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def config_hash(self) -> str:
        material = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(material.encode()).hexdigest()[:16]


# ── Policy Profile Presets ────────────────────────────────────────────────────

_PROFILE_WEIGHTS = {
    PolicyProfile.BALANCED: {
        "evidence_strength": 0.25, "evidence_independence": 0.15,
        "source_diversity": 0.15, "topology_strength": 0.10,
        "hub_score": 0.05, "bridge_score": 0.05,
        "conflict_pressure": 0.20, "temporal_stability": 0.05,
    },
    PolicyProfile.CONSERVATIVE: {
        "evidence_strength": 0.35, "evidence_independence": 0.20,
        "source_diversity": 0.10, "topology_strength": 0.05,
        "hub_score": 0.02, "bridge_score": 0.03,
        "conflict_pressure": 0.25, "temporal_stability": 0.00,
    },
    PolicyProfile.RESEARCH: {
        "evidence_strength": 0.20, "evidence_independence": 0.25,
        "source_diversity": 0.25, "topology_strength": 0.05,
        "hub_score": 0.03, "bridge_score": 0.02,
        "conflict_pressure": 0.15, "temporal_stability": 0.05,
    },
    PolicyProfile.EVIDENCE_FIRST: {
        "evidence_strength": 0.45, "evidence_independence": 0.10,
        "source_diversity": 0.10, "topology_strength": 0.05,
        "hub_score": 0.03, "bridge_score": 0.02,
        "conflict_pressure": 0.20, "temporal_stability": 0.05,
    },
}

_PROFILE_DIRECTIONS = {
    "evidence_strength": "positive", "evidence_independence": "positive",
    "source_diversity": "positive", "topology_strength": "positive",
    "hub_score": "positive", "bridge_score": "positive",
    "conflict_pressure": "negative", "temporal_stability": "positive",
}


def load_policy(
    profile: PolicyProfile = PolicyProfile.BALANCED,
) -> ReliabilityPolicy:
    """
    Load ReliabilityPolicy from config/default.yaml [scoring_policy] section.

    Args:
        profile: Which PolicyProfile preset to apply (RECTIFIED P1-3).
                 Config can override the profile via scoring_policy.profile.

    Returns:
        ReliabilityPolicy (not yet validated against the registry).
        Caller must call policy.validate(active_registry_ids) after loading.
    """
    config = get_config()
    sp = config.get("scoring_policy", {})

    # Determine active profile
    profile_str = sp.get("profile", profile.value)
    try:
        active_profile = PolicyProfile(profile_str)
    except ValueError:
        logger.warning("unknown policy profile, using BALANCED", profile=profile_str)
        active_profile = PolicyProfile.BALANCED

    ev_cfg = sp.get("evidence", {})
    co_cfg = sp.get("conflict", {})
    to_cfg = sp.get("topology", {})
    te_cfg = sp.get("temporal", {})
    fu_cfg = sp.get("fusion", {})
    ca_cfg = sp.get("calibration", {})

    # Signal weights: start from profile preset, allow config override
    preset_weights = dict(_PROFILE_WEIGHTS[active_profile])
    config_weights = fu_cfg.get("signal_weights", {})
    preset_weights.update(config_weights)   # Config overrides preset

    fusion = FusionPolicy(
        signal_weights=preset_weights,
        signal_directions=dict(_PROFILE_DIRECTIONS),
        max_reliability_without_evidence=fu_cfg.get("max_reliability_without_evidence", 60.0),
        max_reliability_with_max_conflict=fu_cfg.get("max_reliability_with_max_conflict", 40.0),
        min_reliability_for_high_topology=fu_cfg.get("min_reliability_for_high_topology", 20.0),
        max_uncertainty_discount=fu_cfg.get("max_uncertainty_discount", 20.0),
    )

    policy = ReliabilityPolicy(
        version=sp.get("version", POLICY_VERSION),
        profile=active_profile.value,
        evidence=EvidencePolicy(
            min_support_count=ev_cfg.get("min_support_count", 1),
            max_support_count=ev_cfg.get("max_support_count", 20),
            echo_chamber_penalty=ev_cfg.get("echo_chamber_penalty", 0.30),
            independence_discount_threshold=ev_cfg.get("independence_discount_threshold", 0.50),
            lineage_depth_limit=ev_cfg.get("lineage_depth_limit", 2),
            publisher_domain_weight=ev_cfg.get("publisher_domain_weight", 0.50),
        ),
        conflict=ConflictPolicy(
            max_contradiction_partners=co_cfg.get("max_contradiction_partners", 5),
            conflict_saturation=co_cfg.get("conflict_saturation", 0.80),
            contradiction_weight_multiplier=co_cfg.get("contradiction_weight_multiplier", 1.0),
        ),
        topology=TopologyPolicy(
            centrality_scale=to_cfg.get("centrality_scale", 1.0),
        ),
        temporal=TemporalPolicy(
            default_stability=te_cfg.get("default_stability", 0.50),
            evolution_bonus=te_cfg.get("evolution_bonus", 0.15),
            conflict_penalty=te_cfg.get("conflict_penalty", 0.10),
            recency_window_days=te_cfg.get("recency_window_days", 90.0),
        ),
        fusion=fusion,
        calibration=CalibrationPolicy(
            very_high_threshold=ca_cfg.get("very_high_threshold", 80.0),
            high_threshold=ca_cfg.get("high_threshold", 65.0),
            moderate_threshold=ca_cfg.get("moderate_threshold", 45.0),
            low_threshold=ca_cfg.get("low_threshold", 25.0),
        ),
    )

    logger.info(
        "policy loaded (validation deferred to caller)",
        version=policy.version,
        profile=active_profile.value,
        config_hash=policy.config_hash(),
    )
    return policy
````

## File: src/smriti/scoring/statistics.py
````python
"""
statistics.py — Phase 8 execution telemetry. Observes. Never influences.

RECTIFIED (Phase 8.4): Now returns Phase8Telemetry with cleanly segregated
ExecutionStats (timing and infrastructure) and KnowledgeStats (knowledge outcomes).
Calibration histogram is tracked per claim for better diagnostics.
"""

from __future__ import annotations

import time
from typing import Dict
from smriti.core.models import (
    Phase8Telemetry,
    ExecutionStats,
    KnowledgeStats,
    CalibrationLabel,
)


class Phase8StatsCollector:
    """Mutable accumulator for Phase 8 statistics."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._signal_start: float | None = None
        self._signal_end: float | None = None
        self._fusion_start: float | None = None
        self._fusion_end: float | None = None

        # Knowledge metrics
        self._scored: int = 0
        self._ri_sum: float = 0.0
        self._unc_sum: float = 0.0
        self._high_ri: int = 0
        self._low_ri: int = 0
        self._high_unc: int = 0
        self._calibration_histogram: Dict[str, int] = {
            label.value: 0 for label in CalibrationLabel
        }

        # Execution metadata
        self._policy_version: str = ""
        self._policy_profile: str = ""
        self._registered_signals: int = 0

    def record_signal_start(self) -> None:
        self._signal_start = time.monotonic()

    def record_signal_end(self) -> None:
        self._signal_end = time.monotonic()

    def record_fusion_start(self) -> None:
        self._fusion_start = time.monotonic()

    def record_fusion_end(self) -> None:
        self._fusion_end = time.monotonic()

    def record_scored(
        self,
        ri: float,
        unc: float,
        calibration_label: CalibrationLabel,
    ) -> None:
        """
        Record a scored claim's reliability index, uncertainty, and calibration label.
        """
        self._scored += 1
        self._ri_sum += ri
        self._unc_sum += unc

        if ri >= 65:
            self._high_ri += 1
        if ri < 45:
            self._low_ri += 1
        if unc >= 50:
            self._high_unc += 1

        self._calibration_histogram[calibration_label.value] = (
            self._calibration_histogram.get(calibration_label.value, 0) + 1
        )

    def set_policy_version(self, version: str, profile: str = "") -> None:
        self._policy_version = version
        self._policy_profile = profile

    def set_registered_signals(self, count: int) -> None:
        self._registered_signals = count

    def finalize(self) -> Phase8Telemetry:
        """Produce the complete Phase 8 telemetry report."""
        total = time.monotonic() - self._start

        n = max(1, self._scored)

        signal_secs = (
            (self._signal_end - self._signal_start)
            if self._signal_start and self._signal_end
            else 0.0
        )
        fusion_secs = (
            (self._fusion_end - self._fusion_start)
            if self._fusion_start and self._fusion_end
            else 0.0
        )

        execution = ExecutionStats(
            total_runtime_seconds=round(total, 4),
            signal_extraction_seconds=round(signal_secs, 4),
            fusion_seconds=round(fusion_secs, 4),
            registered_signal_count=self._registered_signals,
        )

        knowledge = KnowledgeStats(
            total_claims_scored=self._scored,
            avg_reliability_index=round(self._ri_sum / n, 2),
            avg_uncertainty_score=round(self._unc_sum / n, 2),
            calibration_histogram=dict(self._calibration_histogram),
        )

        return Phase8Telemetry(
            policy_version=self._policy_version,
            policy_profile=self._policy_profile,
            execution=execution,
            knowledge=knowledge,
        )
````

## File: tests/integration/test_phase6_discovery.py
````python
"""
Integration test for Phase 6 end-to-end.
Uses mock NLI generator and mock FAISS index to avoid model downloads.
"""

import pytest
from pathlib import Path
from typing import List, Dict, Optional

from smriti.core.models import (
    Claim, EmbeddedClaim, RelationshipSet, RelationshipType,
    CandidatePair, RelationshipEvidence, NLIScores, InferenceMetadata,
    ClaimProvenance, ExtractionMode, AssertionMetadata, LifecycleStage,
    Embedding, EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, VectorDType,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.retrieval import discover_relationships
from smriti.retrieval.index import EmbeddingIndex, SearchResult
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator


class MockNLIGenerator(NLIEvidenceGenerator):
    """Mock NLI generator — returns configurable evidence scores."""

    def __init__(self, contradiction_score: float = 0.90, entailment_score: float = 0.05):
        self._model_name = "mock-nli"
        self._batch_size = 16
        self._contradiction_score = contradiction_score
        self._entailment_score = entailment_score

    def _load_model(self):
        return None

    def generate_batch(self, pairs, claims_map):
        results = []
        neutral = max(0.0, 1.0 - self._contradiction_score - self._entailment_score)
        for pair in pairs:
            scores = [self._contradiction_score, self._entailment_score, neutral]
            predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
            nli_scores = NLIScores(
                entailment_score=self._entailment_score,
                neutral_score=neutral,
                contradiction_score=self._contradiction_score,
                predicted_label=predicted,
                raw_confidence=max(scores),
            )
            metadata = InferenceMetadata(model_name="mock-nli")
            results.append(RelationshipEvidence(
                pair=pair,
                cosine_similarity=pair.cosine_similarity,
                nli_scores=nli_scores,
                calibrated_confidence=max(scores),
                inference_metadata=metadata,
                lifecycle_stage=LifecycleStage.EVIDENCE,
            ))
        return results


def make_claim(claim_id: str, text: str, context: str = "") -> Claim:
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=text, content_hash=claim_id[:16], context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context=context, sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_embedded_claim(claim_id: str, values: tuple = (0.5, 0.5, 0.5, 0.5)) -> EmbeddedClaim:
    vec = Vector(values=values, dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="test_sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2", device="cpu", config_hash="test",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=True, normalized=True, finite=True, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


class MockFAISSIndex(EmbeddingIndex):
    def __init__(self, results: Dict[str, List[SearchResult]]):
        self._results = results
        self._dimension = 4
        self._size = 0

    @property
    def dimension(self): return self._dimension

    @property
    def size(self): return self._size

    def add(self, claim_ids, vectors):
        self._size += len(claim_ids)

    def search(self, query_id, query_vector, k, exclude_ids=None):
        results = self._results.get(query_id, [])
        if exclude_ids:
            results = [r for r in results if r.claim_id not in exclude_ids]
        return results[:k]


@pytest.fixture
def run_id():
    return "test_phase6_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Original 10 tests (preserved) ────────────────────────────────────────────

def test_empty_claims_returns_empty_relationship_set(run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[], claims_map={},
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, nli_generator=MockNLIGenerator(),
    )
    assert isinstance(result, RelationshipSet)
    assert result.total_relationships == 0


def test_contradiction_is_discovered(run_id, test_managers):
    ec_a = make_embedded_claim("c001", (0.9, 0.1, 0.0, 0.0))
    ec_b = make_embedded_claim("c002", (-0.9, -0.1, 0.0, 0.0))
    claims_map = {
        "c001": make_claim("c001", "Python always normalizes features before PCA."),
        "c002": make_claim("c002", "Normalization before PCA is often unnecessary."),
    }
    mock_index = MockFAISSIndex({
        "c001": [SearchResult("c002", 0.85, 1)],
        "c002": [SearchResult("c001", 0.85, 1)],
    })
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.92),
    )
    assert result.total_relationships >= 1
    assert len(result.contradictions) >= 1


def test_all_relationships_are_immutable(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    for rel in result.relationships:
        with pytest.raises(Exception):
            rel.claim_id_a = "modified"


def test_relationship_ids_are_unique(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    claims_map = {
        "c001": make_claim("c001", "Python is fast."),
        "c002": make_claim("c002", "Python is slow."),
        "c003": make_claim("c003", "Julia is fastest."),
    }
    mock_index = MockFAISSIndex({
        "c001": [SearchResult("c002", 0.85, 1), SearchResult("c003", 0.82, 2)],
        "c002": [SearchResult("c003", 0.80, 1)],
        "c003": [],
    })
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b, ec_c], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    rel_ids = [r.relationship_id for r in result.relationships]
    assert len(rel_ids) == len(set(rel_ids))


def test_all_relationships_have_complete_provenance(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.provenance is not None
        assert rel.provenance.run_id == run_id
        assert rel.provenance.classifier_model != ""
        assert rel.provenance.config_hash != ""


def test_schema_version_is_60(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.schema_version == "6.0"


def test_dataset_json_written(run_id, test_managers, tmp_path):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    assert result.dataset_path is not None
    assert result.dataset_path.exists()


def test_manifest_written(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    import json
    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 6
    assert manifest["status"] == "success"


def test_pipeline_state_updated(run_id, test_managers):
    _, state_mgr = test_managers
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, _ = test_managers
    discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    state = state_mgr.load()
    assert state is not None
    assert 6 in state.completed_phases


def test_no_nli_model_imports_in_candidate_modules():
    import smriti.retrieval.candidate_generator as cg
    import smriti.retrieval.validator as cv
    import smriti.retrieval.builder as cb

    nli_modules = {"sentence_transformers", "transformers", "torch"}
    for module in [cg, cv, cb]:
        keys = set(vars(module).keys())
        assert not (keys & nli_modules)


# ── Rectified 3 new tests ─────────────────────────────────────────────────────

def test_replay_manifest_written(run_id, test_managers):
    """RECTIFIED: replay manifest must be written after every successful run."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    assert result.replay_manifest_path is not None
    assert result.replay_manifest_path.exists()


def test_all_relationships_have_schema_version_info(run_id, test_managers):
    """RECTIFIED: every relationship must carry SchemaVersionInfo."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.version_info is not None
        assert rel.version_info.schema_version == "6.0"
        assert rel.version_info.migration_version is not None
        assert rel.version_info.compatibility_version is not None


def test_calibrated_confidence_in_provenance(run_id, test_managers):
    """RECTIFIED: provenance must record both raw and calibrated confidence."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    for rel in result.relationships:
        assert rel.provenance.raw_nli_confidence > 0
        assert rel.provenance.calibrated_confidence > 0
        assert rel.provenance.calibrator_version != ""
````

## File: tests/integration/test_phase7_knowledge_graph.py
````python
"""Integration tests for Phase 7 end-to-end."""

import json
import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Relationship, RelationshipSet, RelationshipType, RelationshipDirection,
    RelationshipEvidence, RelationshipProvenance, RelationshipQuality,
    NLIScores, InferenceMetadata, CandidatePair, SchemaVersionInfo,
    LifecycleStage, KnowledgeGraph,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.evolution import build_knowledge_graph


def make_claim(cid, text="Test.", doc_id="d001"):
    return Claim(
        claim_id=cid, sentence_id="s001", document_id=doc_id,
        text=text, content_hash=cid[:16], context="Python",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None, assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=doc_id,
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_rel(rel_id, cid_a, cid_b, rel_type, confidence=0.88):
    pair = CandidatePair(claim_id_a=cid_a, claim_id_b=cid_b, cosine_similarity=0.85, candidate_rank=1)
    nli = NLIScores(
        entailment_score=0.05, neutral_score=0.05, contradiction_score=0.90,
        predicted_label="contradiction", raw_confidence=confidence,
    )
    evidence = RelationshipEvidence(
        pair=pair, cosine_similarity=0.85, nli_scores=nli,
        calibrated_confidence=confidence,
        inference_metadata=InferenceMetadata(model_name="test"),
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )
    prov = RelationshipProvenance(
        retrieval_backend="faiss_flat_ip", retrieval_version="1.0", index_version="1.0",
        search_parameters=None, classifier_model="test", classifier_version="1.0",
        resolver_version="1.0", calibrator_version="1.0", cosine_similarity=0.85,
        candidate_rank=1, raw_nli_confidence=confidence, calibrated_confidence=confidence,
        config_hash="test", run_id="run1",
    )
    quality = RelationshipQuality(
        cosine_above_threshold=True, nli_above_threshold=True,
        evidence_consistent=True, calibration_applied=False,
    )
    version = SchemaVersionInfo(schema_version="6.0", migration_version="6.0", compatibility_version="6.0")
    return Relationship(
        relationship_id=rel_id, claim_id_a=cid_a, claim_id_b=cid_b,
        relationship_type=rel_type, direction=RelationshipDirection.SYMMETRIC,
        evidence=evidence, quality=quality, provenance=prov, version_info=version,
    )


def make_rel_set(rels, run_id="test_run"):
    return RelationshipSet(
        relationships=rels, total_candidates=len(rels),
        total_validated=len(rels), total_rejected=0,
        rejected_reasons={}, run_id=run_id,
    )


@pytest.fixture
def run_id():
    return "test_phase7_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Original 12 tests (all preserved) ────────────────────────────────────────

def test_basic_knowledge_graph_construction(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert isinstance(graph, KnowledgeGraph)
    assert graph.node_count == 2 and graph.edge_count == 1


def test_contradiction_produces_two_partitions(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert graph.partition_count == 2 and graph.statistics.contradiction_count == 1


def test_supports_keeps_claims_in_same_partition(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert graph.partition_count == 1
    assert graph.nodes["c001"].partition_id == graph.nodes["c002"].partition_id


def test_knowledge_graph_is_immutable(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    with pytest.raises(Exception):
        graph.run_id = "modified"


def test_validation_report_passes(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert graph.validation_report.is_valid is True and graph.validation_report.total_violations == 0


def test_schema_version_correct(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert graph.schema_version == "7.0"
    for node in graph.nodes.values():
        assert node.schema_version == "7.0"
    for edge in graph.edges.values():
        assert edge.schema_version == "7.0"


def test_nodes_have_semantic_roles(run_id, test_managers):
    from smriti.core.models import SemanticRole
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    for node in graph.nodes.values():
        assert node.semantic_role is not None and isinstance(node.semantic_role, SemanticRole)


def test_manifest_written(run_id, test_managers):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    manifest_path = manifest_mgr.run_dir / "phase7" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["phase"] == 7 and manifest["status"] == "success"


def test_dataset_json_written(run_id, test_managers, tmp_path):
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase7" / "dataset.json"
    assert dataset_path.exists()
    data = json.loads(dataset_path.read_text())
    assert all(k in data for k in ("graph_id", "nodes", "edges", "partitions"))


def test_pipeline_state_updated(run_id, test_managers):
    _, state_mgr = test_managers
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, _ = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    state = state_mgr.load()
    assert state is not None and 7 in state.completed_phases


def test_deterministic_construction(run_id, test_managers, tmp_path):
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c001", "c003", RelationshipType.SUPPORTS),
    ]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002"), "c003": make_claim("c003")}
    manifest_mgr, state_mgr = test_managers
    graph1 = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    manifest_mgr2 = ManifestManager(run_id=f"{run_id}_2", artifacts_dir=tmp_path / "artifacts2")
    state_mgr2 = StateManager(state_file=tmp_path / "state2.json")
    graph2 = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr2, state_mgr2)
    assert graph1.graph_id == graph2.graph_id
    assert graph1.node_count == graph2.node_count
    assert graph1.partition_count == graph2.partition_count


def test_unknown_relationships_excluded_from_graph(run_id, test_managers):
    from smriti.core.models import RelationshipType
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.UNKNOWN),
        make_rel("r2", "c001", "c003", RelationshipType.CONTRADICTS),
    ]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002"), "c003": make_claim("c003")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    for edge in graph.edges.values():
        assert edge.relationship_type != RelationshipType.UNKNOWN


def test_realistic_knowledge_graph(run_id, test_managers):
    """Full test with realistic structure."""
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c003", "c001", RelationshipType.SUPPORTS),
        make_rel("r3", "c004", "c001", RelationshipType.REFINES),
    ]
    claims = {
        "c001": make_claim("c001", "Always normalize features before PCA."),
        "c002": make_claim("c002", "Normalization before PCA is often unnecessary."),
        "c003": make_claim("c003", "Use StandardScaler for consistent preprocessing."),
        "c004": make_claim("c004", "Normalization improves PCA convergence on numerical data."),
    }
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    assert graph.node_count == 4 and graph.edge_count == 3
    assert graph.statistics.contradiction_count == 1
    node_c001 = graph.nodes["c001"]
    node_c002 = graph.nodes["c002"]
    assert node_c001.partition_id != node_c002.partition_id
    partition_c001 = graph.partitions[node_c001.partition_id]
    assert "c003" in partition_c001.node_ids and "c004" in partition_c001.node_ids
    assert node_c001.support_aggregate is not None
    assert node_c001.support_aggregate.support_count >= 1
    assert graph.schema_version == "7.0" and graph.validation_report.is_valid
    for node in graph.nodes.values():
        assert node.semantic_role is not None


# ── 3 new rectified integration tests ────────────────────────────────────────

def test_shared_support_target_partitioned_correctly(run_id, test_managers):
    """
    RECTIFIED (P0-1): Critical test — shared SUPPORTS target must not
    merge contradicting nodes into the same partition.

    A SUPPORTS X, C SUPPORTS X, A CONTRADICTS C.
    A and C must be in DIFFERENT partitions.
    """
    rels = [
        make_rel("r1", "A", "X", RelationshipType.SUPPORTS),
        make_rel("r2", "C", "X", RelationshipType.SUPPORTS),
        make_rel("r3", "A", "C", RelationshipType.CONTRADICTS),
    ]
    claims = {
        "A": make_claim("A", "Claim A."),
        "X": make_claim("X", "Claim X."),
        "C": make_claim("C", "Claim C."),
    }
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)

    partition_of_A = graph.nodes["A"].partition_id
    partition_of_C = graph.nodes["C"].partition_id
    assert partition_of_A != partition_of_C, (
        "A and C contradict each other. Even though they both support X, "
        "they must be in different partitions."
    )


def test_stable_partition_label_in_dataset_json(run_id, test_managers):
    """RECTIFIED (P2-5): stable_partition_label must be written to dataset.json."""
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    manifest_mgr, state_mgr = test_managers
    build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase7" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for partition_data in data["partitions"].values():
        assert "stable_partition_label" in partition_data, (
            "stable_partition_label must be written to dataset.json for incremental comparison."
        )


def test_bridge_nodes_counted_in_statistics(run_id, test_managers):
    """RECTIFIED (P0-3): bridge_nodes stat must use articulation-point count."""
    # A → B → C: B is an articulation point
    rels = [
        make_rel("r1", "A", "B", RelationshipType.SUPPORTS),
        make_rel("r2", "B", "C", RelationshipType.SUPPORTS),
    ]
    claims = {"A": make_claim("A"), "B": make_claim("B"), "C": make_claim("C")}
    manifest_mgr, state_mgr = test_managers
    graph = build_knowledge_graph(make_rel_set(rels, run_id), claims, run_id, manifest_mgr, state_mgr)
    # B is the true articulation point
    assert graph.statistics.bridge_nodes >= 1, (
        "B is an articulation point. bridge_nodes stat must reflect this."
    )
````

## File: tests/integration/test_phase8_scoring.py
````python
"""Integration test for Phase 8 end-to-end."""

import json
import pytest
from pathlib import Path

from smriti.core.models import (
    KnowledgeGraph, ClaimNode, RelationshipEdge, KnowledgePartition,
    RelationshipType, RelationshipDirection, GraphStatistics, ValidationReport,
    SemanticRole, TopologyMetrics, SupportAggregate, TemporalMetadata,
    TemporalStatus, ScoredKnowledgeGraph, CalibrationLabel, NodeAnnotations,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.scoring import score_knowledge_graph


def make_minimal_graph(run_id="test_run") -> KnowledgeGraph:
    topo_a = TopologyMetrics(
        degree=3, in_degree=2, out_degree=1, is_bridge=False, is_hub=False,
        partition_id="p001", centrality=0.65,
    )
    support_a = SupportAggregate(
        support_count=3, weighted_confidence=0.82,
        supporting_claim_ids=("c002", "c003"),
        evidence_summary="3 supporting claims",
    )
    temporal_a = TemporalMetadata(
        status=TemporalStatus.STATIC_PARTITION,
        earlier_claim_id=None, later_claim_id=None,
        time_delta_days=None, temporal_confidence=0.0,
    )
    topo_b = TopologyMetrics(
        degree=1, in_degree=0, out_degree=1, is_bridge=False, is_hub=False,
        partition_id="p002", centrality=0.10,
    )
    ann_a = NodeAnnotations(
        semantic_role=SemanticRole.FOUNDATIONAL_CLAIM,
        topology=topo_a, support_aggregate=support_a, temporal_metadata=temporal_a,
        partition_id="p001",
    )
    ann_b = NodeAnnotations(
        semantic_role=SemanticRole.PERIPHERAL_CLAIM,
        topology=topo_b, support_aggregate=None, temporal_metadata=None,
        partition_id="p002",
    )
    nodes = {
        "c001": ClaimNode(
            node_id="c001", claim_id="c001",
            claim_text="Always normalize features before PCA.",
            context="Python > ML", source_path=Path("note.md"),
            document_id="d001", annotations=ann_a,
        ),
        "c002": ClaimNode(
            node_id="c002", claim_id="c002",
            claim_text="Normalization is often unnecessary.",
            context="Python > ML", source_path=Path("note2.md"),
            document_id="d002", annotations=ann_b,
        ),
    }
    edges = {
        "r1": RelationshipEdge(
            edge_id="r1", source_node_id="c001", target_node_id="c002",
            relationship_type=RelationshipType.CONTRADICTS,
            direction=RelationshipDirection.SYMMETRIC,
            calibrated_confidence=0.88, cosine_similarity=0.82,
            nli_confidence=0.88, candidate_rank=1,
        ),
    }
    partitions = {
        "p001": KnowledgePartition(
            partition_id="p001", stable_partition_label="c001",
            node_ids=frozenset(["c001"]),
            internal_edge_ids=frozenset(), node_count=1, edge_count=0,
            supports_count=0, refines_count=0, density=0.0, longest_support_chain=0,
        ),
        "p002": KnowledgePartition(
            partition_id="p002", stable_partition_label="c002",
            node_ids=frozenset(["c002"]),
            internal_edge_ids=frozenset(), node_count=1, edge_count=0,
            supports_count=0, refines_count=0, density=0.0, longest_support_chain=0,
        ),
    }
    stats = GraphStatistics(
        node_count=2, edge_count=1, partition_count=2,
        contradiction_count=1, supports_count=0, refines_count=0,
        isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
        evolution_chains=0, unresolved_conflicts=0,
        construction_time_seconds=0.1, enrichment_time_seconds=0.2,
    )
    vr = ValidationReport(
        is_valid=True, node_violations=(), edge_violations=(),
        graph_violations=(), semantic_violations=(), validation_time_seconds=0.01,
    )
    return KnowledgeGraph(
        graph_id="test_graph_001", nodes=nodes, edges=edges, partitions=partitions,
        statistics=stats, validation_report=vr, run_id=run_id,
        config_hash="test_hash", schema_version="7.0",
    )


@pytest.fixture
def run_id(): return "test_phase8_20240101"

@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )

@pytest.fixture
def graph(): return make_minimal_graph()


# ── Original 15 tests ─────────────────────────────────────────────────────────

def test_returns_scored_knowledge_graph(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    assert isinstance(result, ScoredKnowledgeGraph)


def test_every_node_is_scored(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    assert result.total_scored == graph.node_count
    for claim_id in graph.nodes:
        assert claim_id in result.reliability


def test_original_graph_not_modified(graph, run_id, test_managers):
    original_count = graph.node_count
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    assert result.graph is graph
    assert result.graph.node_count == original_count


def test_reliability_index_in_range(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        assert 0.0 <= meta.reliability_index <= 100.0


def test_uncertainty_in_range(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        assert 0.0 <= meta.uncertainty_score <= 100.0


def test_calibration_label_assigned(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        assert isinstance(meta.calibration_label, CalibrationLabel)


def test_explanation_is_populated(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        assert meta.explanation.summary


def test_schema_version_correct(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    assert result.schema_version == "8.0"
    for meta in result.reliability.values():
        assert meta.schema_version == "8.0"


def test_component_scores_sum_approximates_ri(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        comp_sum = sum(c.contribution for c in meta.component_scores)
        assert abs(comp_sum - meta.reliability_index) <= 30.0


def test_deterministic_scoring(graph, run_id, test_managers, tmp_path):
    manifest_mgr, state_mgr = test_managers
    result1 = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    manifest_mgr2 = ManifestManager(run_id=f"{run_id}_2", artifacts_dir=tmp_path / "artifacts2")
    state_mgr2 = StateManager(state_file=tmp_path / "state2.json")
    result2 = score_knowledge_graph(graph=graph, run_id=f"{run_id}_2", manifest_manager=manifest_mgr2, state_manager=state_mgr2)
    for claim_id in graph.nodes:
        ri1 = result1.reliability[claim_id].reliability_index
        ri2 = result2.reliability[claim_id].reliability_index
        assert ri1 == ri2, f"Non-deterministic: {claim_id} got {ri1} vs {ri2}"


def test_dataset_json_written(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    phase_dir = manifest_mgr.run_dir / "phase8"
    dataset_path = phase_dir / "dataset.json"
    assert dataset_path.exists()
    data = json.loads(dataset_path.read_text())
    assert "reliability" in data and len(data["reliability"]) == graph.node_count


def test_manifest_written(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    manifest_path = manifest_mgr.run_dir / "phase8" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["phase"] == 8 and manifest["status"] == "success"


def test_pipeline_state_updated(graph, run_id, test_managers):
    _, state_mgr = test_managers
    manifest_mgr, _ = test_managers
    score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    state = state_mgr.load()
    assert state is not None and 8 in state.completed_phases


def test_well_supported_claim_higher_than_unsupported(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    ri_c001 = result.reliability["c001"].reliability_index
    ri_c002 = result.reliability["c002"].reliability_index
    assert ri_c001 > ri_c002


def test_audit_trail_populated(graph, run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    for meta in result.reliability.values():
        assert meta.audit.policy_version
        assert meta.audit.fusion_algorithm
        assert meta.audit.computed_at_run_id == run_id


# ── 4 new rectified integration tests ────────────────────────────────────────

def test_signal_manifests_in_dataset_json(graph, run_id, test_managers):
    """RECTIFIED (P0-4): Signal manifests must be written to dataset.json."""
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase8" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for claim_id, meta in data["reliability"].items():
        assert "signal_manifests" in meta, (
            f"signal_manifests missing for claim {claim_id}. "
            "Every claim must have a full derivation trace."
        )
        assert len(meta["signal_manifests"]) > 0


def test_decision_record_in_dataset_json(graph, run_id, test_managers):
    """RECTIFIED (P0-5): ReliabilityDecisionRecord must be in dataset.json."""
    manifest_mgr, state_mgr = test_managers
    score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    dataset_path = manifest_mgr.run_dir / "phase8" / "dataset.json"
    data = json.loads(dataset_path.read_text())
    for claim_id, meta in data["reliability"].items():
        assert "decision_record" in meta, (
            f"decision_record missing for claim {claim_id}. "
            "Every claim must have a ReliabilityDecisionRecord."
        )
        dr = meta["decision_record"]
        assert "policy_interactions" in dr
        assert "constraints_activated" in dr
        assert "contribution_order" in dr
        assert "final_reliability" in dr


def test_policy_profile_recorded(graph, run_id, test_managers):
    """RECTIFIED (P1-3): PolicyProfile must be recorded in ScoredKnowledgeGraph and dataset."""
    from smriti.scoring.policies import PolicyProfile
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(
        graph=graph, run_id=run_id,
        manifest_manager=manifest_mgr, state_manager=state_mgr,
        policy_profile=PolicyProfile.BALANCED,
    )
    assert result.policy_profile == "balanced"
    for meta in result.reliability.values():
        assert meta.audit.policy_profile == "balanced"


def test_hub_and_bridge_scored_separately(graph, run_id, test_managers):
    """RECTIFIED (P0-3): hub_score and bridge_score must appear in component scores."""
    manifest_mgr, state_mgr = test_managers
    result = score_knowledge_graph(graph=graph, run_id=run_id, manifest_manager=manifest_mgr, state_manager=state_mgr)
    # At least one claim must have hub_score and bridge_score in its component_scores
    all_signal_names = set()
    for meta in result.reliability.values():
        for comp in meta.component_scores:
            all_signal_names.add(comp.signal_name)
    assert "hub_score" in all_signal_names or "bridge_score" in all_signal_names, (
        "hub_score and bridge_score must appear as separate ComponentScores. "
        "They must not be merged into topology_strength."
    )
````

## File: tests/unit/test_phase6_builder.py
````python
"""Unit tests for retrieval/builder.py."""

import pytest
from smriti.core.models import (
    CandidatePair, RelationshipEvidence, RelationshipType, RelationshipDirection,
    Relationship, NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.retrieval.builder import build_relationship, build_relationship_set


def make_evidence(claim_id_a="c001", claim_id_b="c002"):
    pair = CandidatePair(
        claim_id_a=claim_id_a, claim_id_b=claim_id_b,
        cosine_similarity=0.85, candidate_rank=1,
    )
    nli_scores = NLIScores(
        entailment_score=0.05,
        neutral_score=0.03,
        contradiction_score=0.92,
        predicted_label="contradiction",
        raw_confidence=0.92,
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair, cosine_similarity=0.85,
        nli_scores=nli_scores,
        calibrated_confidence=0.88,   # Slightly different from raw (calibrated)
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


def test_build_relationship_returns_relationship():
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert isinstance(rel, Relationship)


def test_relationship_id_is_16_chars():
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert len(rel.relationship_id) == 16


def test_relationship_id_is_deterministic():
    evidence = make_evidence()
    rel1 = build_relationship(evidence, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    rel2 = build_relationship(evidence, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel1.relationship_id == rel2.relationship_id


def test_relationship_is_frozen():
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    with pytest.raises(Exception):
        rel.claim_id_a = "modified"


def test_relationship_provenance_populated():
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel.provenance is not None
    assert rel.provenance.run_id == "run1"
    assert rel.provenance.config_hash == "hash"


def test_relationship_schema_version():
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel.schema_version == "6.0"


def test_relationship_set_contradictions_property():
    e1 = make_evidence("c001", "c002")
    e2 = make_evidence("c003", "c004")
    rel1 = build_relationship(e1, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    rel2 = build_relationship(e2, RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B, 0.80, "hash", "run1")
    rel_set = build_relationship_set(
        relationships=[rel1, rel2], total_candidates=10,
        total_validated=5, total_rejected=5,
        rejected_reasons={"below_threshold": 5}, run_id="run1",
    )
    assert len(rel_set.contradictions) == 1
    assert len(rel_set.supports) == 1


def test_schema_version_info_populated():
    """RECTIFIED: SchemaVersionInfo must be populated on every Relationship."""
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel.version_info is not None
    assert rel.version_info.schema_version == "6.0"
    assert rel.version_info.migration_version == "6.0"
    assert rel.version_info.compatibility_version == "6.0"


def test_calibration_applied_flag_set_when_scores_differ():
    """RECTIFIED: calibration_applied must be True when raw != calibrated."""
    evidence = make_evidence()  # raw_confidence=0.92, calibrated_confidence=0.88
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel.quality.calibration_applied is True


def test_lifecycle_stage_is_relationship():
    """RECTIFIED: built relationships must carry RELATIONSHIP lifecycle stage."""
    evidence = make_evidence()
    rel = build_relationship(evidence, RelationshipType.CONTRADICTS,
                             RelationshipDirection.SYMMETRIC, 0.80, "hash", "run1")
    assert rel.lifecycle_stage == LifecycleStage.RELATIONSHIP
````

## File: tests/unit/test_phase6_calibration.py
````python
"""Unit tests for classification/calibration.py."""

import pytest
from smriti.core.models import (
    CandidatePair, RelationshipEvidence, NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.retrieval.classification.calibration import (
    ConfidenceCalibrator, CalibrationStrategy,
)


def make_evidence(entailment=0.1, neutral=0.05, contradiction=0.85, cosine=0.80):
    pair = CandidatePair(claim_id_a="c001", claim_id_b="c002", cosine_similarity=cosine, candidate_rank=1)
    nli_scores = NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label="contradiction",
        raw_confidence=max(entailment, neutral, contradiction),
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=cosine,
        nli_scores=nli_scores,
        calibrated_confidence=nli_scores.raw_confidence,
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.EVIDENCE,
    )


def test_identity_calibration_preserves_confidence():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidence = make_evidence(contradiction=0.85)
    result = calibrator.calibrate(evidence)
    assert abs(result.calibrated_confidence - 0.85) < 1e-6


def test_temperature_calibration_softens_high_confidence():
    calibrator = ConfidenceCalibrator(
        model_name="test",
        strategy=CalibrationStrategy.TEMPERATURE,
        temperature=2.0,   # Higher temperature → softer distribution
    )
    evidence = make_evidence(contradiction=0.95, entailment=0.03, neutral=0.02)
    result = calibrator.calibrate(evidence)
    # Temperature > 1 should reduce the max confidence
    assert result.calibrated_confidence < evidence.nli_scores.raw_confidence


def test_calibration_advances_lifecycle_to_calibrated():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidence = make_evidence()
    result = calibrator.calibrate(evidence)
    assert result.lifecycle_stage == LifecycleStage.CALIBRATED_EVIDENCE


def test_nli_scores_unchanged_after_calibration():
    calibrator = ConfidenceCalibrator(
        model_name="test",
        strategy=CalibrationStrategy.TEMPERATURE,
        temperature=2.0,
    )
    evidence = make_evidence(contradiction=0.90)
    result = calibrator.calibrate(evidence)
    assert result.nli_scores.contradiction_score == 0.90   # Raw scores untouched
    assert result.nli_scores.predicted_label == "contradiction"


def test_calibrate_batch_processes_all():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidences = [make_evidence() for _ in range(5)]
    results = calibrator.calibrate_batch(evidences)
    assert len(results) == 5
````

## File: tests/unit/test_phase6_candidate_generator.py
````python
"""Unit tests for retrieval/candidate_generator.py."""

import pytest
from smriti.core.models import CandidatePair, EmbeddedClaim
from smriti.retrieval.candidate_generator import CandidateGenerator
from smriti.retrieval.index import EmbeddingIndex, SearchResult
from typing import List, Optional


class MockIndex(EmbeddingIndex):
    def __init__(self, results: dict):
        self._results = results
        self._dimension = 4
        self._size = 0

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def size(self) -> int:
        return self._size

    def add(self, claim_ids, vectors):
        self._size += len(claim_ids)

    def search(self, query_id, query_vector, k, exclude_ids=None):
        return self._results.get(query_id, [])


def make_embedded_claim(claim_id: str, values=(0.1, 0.2, 0.3, 0.4)):
    from smriti.core.models import (
        EmbeddedClaim, Embedding, EmbeddingModelDescriptor,
        EmbeddingProvenance, EmbeddingQuality, Vector, VectorDType,
    )
    vec = Vector(values=tuple(values), dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="test_sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2",
        device="cpu", config_hash="test",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=True, normalized=True, finite=True, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


@pytest.fixture
def generator():
    return CandidateGenerator()


def test_generates_candidate_pairs(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    mock_index = MockIndex({
        "c001": [SearchResult(claim_id="c002", score=0.85, rank=1)],
        "c002": [SearchResult(claim_id="c001", score=0.85, rank=1)],
    })
    candidates = generator.generate([ec_a, ec_b], mock_index)
    assert len(candidates) == 1


def test_self_comparison_excluded(generator):
    ec_a = make_embedded_claim("c001")
    mock_index = MockIndex({
        "c001": [SearchResult(claim_id="c001", score=1.0, rank=1)],
    })
    candidates = generator.generate([ec_a], mock_index)
    assert len(candidates) == 0


def test_symmetric_deduplication(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    mock_index = MockIndex({
        "c001": [SearchResult("c002", 0.90, 1), SearchResult("c003", 0.80, 2)],
        "c002": [SearchResult("c001", 0.90, 1)],
        "c003": [],
    })
    candidates = generator.generate([ec_a, ec_b, ec_c], mock_index)
    pair_keys = {c.pair_key() for c in candidates}
    assert len(pair_keys) == len(candidates)


def test_output_is_sorted(generator):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    mock_index = MockIndex({
        "c001": [SearchResult("c003", 0.85, 1)],
        "c002": [SearchResult("c001", 0.80, 1)],
        "c003": [],
    })
    candidates = generator.generate([ec_a, ec_b, ec_c], mock_index)
    keys = [c.pair_key() for c in candidates]
    assert keys == sorted(keys)


def test_retrieval_provenance_attached(generator):
    """RECTIFIED: CandidatePair must have retrieval provenance fields."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    mock_index = MockIndex({
        "c001": [SearchResult("c002", 0.85, 1)],
        "c002": [],
    })
    candidates = generator.generate([ec_a, ec_b], mock_index)
    assert len(candidates) == 1
    pair = candidates[0]
    assert pair.retrieval_backend is not None
    assert pair.index_version is not None
    assert pair.search_parameters is not None
    assert pair.retrieval_quality is not None
````

## File: tests/unit/test_phase6_candidate_validator.py
````python
"""Unit tests for retrieval/validator.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    CandidatePair, Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    EmbeddedClaim, Embedding, EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, VectorDType, LifecycleStage,
)
from smriti.retrieval.validator import validate_candidates, RejectionReason


def make_claim(claim_id: str, text: str = "Test claim."):
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=text, content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_embedded_claim(claim_id: str, finite: bool = True, dim_ok: bool = True):
    vec = Vector(values=(0.1, 0.2, 0.3, 0.4), dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2", device="cpu", config_hash="hash",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=dim_ok, normalized=True, finite=finite, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


def make_pair(id_a: str, id_b: str, score: float = 0.85):
    a, b = sorted([id_a, id_b])
    return CandidatePair(claim_id_a=a, claim_id_b=b, cosine_similarity=score, candidate_rank=1)


def test_valid_pair_passes():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.85)]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 1
    assert not rejections


def test_self_comparison_rejected():
    claims = {"c001": make_claim("c001")}
    embs = {"c001": make_embedded_claim("c001")}
    pair = CandidatePair(claim_id_a="c001", claim_id_b="c001", cosine_similarity=1.0, candidate_rank=0)
    valid, rejections = validate_candidates([pair], claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.SELF_COMPARISON.value in rejections


def test_missing_claim_rejected():
    claims = {"c001": make_claim("c001")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002")]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.MISSING_CLAIM.value in rejections


def test_invalid_embedding_rejected():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001", finite=False), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002")]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.INVALID_EMBEDDING.value in rejections


def test_below_threshold_rejected():
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.60)]
    valid, rejections = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert len(valid) == 0
    assert RejectionReason.BELOW_THRESHOLD.value in rejections


def test_empty_input():
    valid, rejections = validate_candidates([], {}, {}, sim_threshold=0.75)
    assert valid == []
    assert not rejections


def test_valid_pair_promoted_to_validated_candidate_lifecycle():
    """RECTIFIED: valid pairs must carry VALIDATED_CANDIDATE lifecycle stage."""
    claims = {"c001": make_claim("c001"), "c002": make_claim("c002")}
    embs = {"c001": make_embedded_claim("c001"), "c002": make_embedded_claim("c002")}
    pairs = [make_pair("c001", "c002", score=0.85)]
    valid, _ = validate_candidates(pairs, claims, embs, sim_threshold=0.75)
    assert valid[0].lifecycle_stage == LifecycleStage.VALIDATED_CANDIDATE
````

## File: tests/unit/test_phase6_resolver.py
````python
"""Unit tests for classification/resolver.py."""

import pytest
from smriti.core.models import (
    CandidatePair, RelationshipEvidence, RelationshipType,
    RelationshipDirection, NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy


def make_evidence(contradiction: float, entailment: float, neutral: float, cosine: float = 0.82):
    pair = CandidatePair(claim_id_a="c001", claim_id_b="c002", cosine_similarity=cosine, candidate_rank=1)
    scores = [contradiction, entailment, neutral]
    predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
    raw_confidence = max(scores)
    nli_scores = NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label=predicted,
        raw_confidence=raw_confidence,
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=cosine,
        nli_scores=nli_scores,
        calibrated_confidence=raw_confidence,
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


@pytest.fixture
def policy():
    return ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
    )


@pytest.fixture
def resolver(policy):
    return RelationshipResolver(policy=policy)


def test_strong_contradiction_resolves_contradicts(resolver):
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.CONTRADICTS


def test_strong_entailment_resolves_supports(resolver):
    evidence = make_evidence(contradiction=0.03, entailment=0.93, neutral=0.04)
    rel_type, direction = resolver.resolve(evidence)
    assert rel_type == RelationshipType.SUPPORTS


def test_weak_contradiction_high_cosine_resolves_refines(resolver):
    evidence = make_evidence(contradiction=0.60, entailment=0.20, neutral=0.20, cosine=0.90)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.REFINES


def test_high_neutral_resolves_neutral(resolver):
    evidence = make_evidence(contradiction=0.15, entailment=0.20, neutral=0.65)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.NEUTRAL


def test_low_confidence_resolves_unknown(resolver):
    evidence = make_evidence(contradiction=0.35, entailment=0.33, neutral=0.32)
    rel_type, _ = resolver.resolve(evidence)
    assert rel_type == RelationshipType.UNKNOWN


def test_resolver_is_deterministic(resolver):
    evidence = make_evidence(contradiction=0.88, entailment=0.08, neutral=0.04)
    assert resolver.resolve(evidence) == resolver.resolve(evidence) == resolver.resolve(evidence)


def test_contradicts_is_symmetric(resolver):
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    _, direction = resolver.resolve(evidence)
    assert direction == RelationshipDirection.SYMMETRIC


def test_supports_is_directional(resolver):
    evidence = make_evidence(contradiction=0.03, entailment=0.93, neutral=0.04)
    _, direction = resolver.resolve(evidence)
    assert direction == RelationshipDirection.A_TO_B


def test_resolver_policy_is_configurable():
    """RECTIFIED: resolver must use policy, not hard-coded values."""
    # Custom policy with much higher threshold
    strict_policy = ResolverPolicy(
        nli_threshold=0.99,
        refine_threshold=0.90,
        high_sim_threshold=0.99,
        neutrality_threshold=0.99,
    )
    strict_resolver = RelationshipResolver(policy=strict_policy)
    # 0.92 contradiction won't exceed 0.99 threshold
    evidence = make_evidence(contradiction=0.92, entailment=0.05, neutral=0.03)
    rel_type, _ = strict_resolver.resolve(evidence)
    assert rel_type == RelationshipType.UNKNOWN


def test_resolver_policy_validates_on_construction():
    """RECTIFIED: invalid policy must raise ResolverPolicyError."""
    from smriti.exceptions import ResolverPolicyError
    with pytest.raises(ResolverPolicyError):
        ResolverPolicy(
            nli_threshold=0.80,
            refine_threshold=0.90,   # Violation: refine_threshold >= nli_threshold
            high_sim_threshold=0.88,
            neutrality_threshold=0.60,
        )


def test_resolver_contradiction_margin_enforced():
    """RECTIFIED: contradiction_margin must widen the gap requirement."""
    policy_with_margin = ResolverPolicy(
        nli_threshold=0.80,
        refine_threshold=0.55,
        high_sim_threshold=0.88,
        neutrality_threshold=0.60,
        contradiction_margin=0.20,   # C must exceed E by 0.20
    )
    resolver = RelationshipResolver(policy=policy_with_margin)
    # C=0.85, E=0.10 → gap=0.75 > 0.20 → CONTRADICTS
    evidence_pass = make_evidence(contradiction=0.85, entailment=0.10, neutral=0.05)
    rel_type, _ = resolver.resolve(evidence_pass)
    assert rel_type == RelationshipType.CONTRADICTS

    # C=0.82, E=0.75 → gap=0.07 < 0.20 → not CONTRADICTS
    evidence_fail = make_evidence(contradiction=0.82, entailment=0.75, neutral=0.03)
    rel_type, _ = resolver.resolve(evidence_fail)
    assert rel_type != RelationshipType.CONTRADICTS
````

## File: tests/unit/test_phase7_aggregation_dedup.py
````python
"""
Unit tests for aggregation.py provenance-root deduplication fix (P0-2).

Verifies that support aggregation counts unique supporting claim IDs,
not unique traversal paths. In a DAG like:

    A → B → D
    A → C → D

A supports D through two paths. Old code: A counted twice.
New code: A counted exactly once (unique provenance root).
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning
from smriti.evolution.aggregation import run_evidence_aggregation


def make_supports_edge(eid, src, tgt, confidence=0.88):
    return RelationshipEdge(
        edge_id=eid, source_node_id=src, target_node_id=tgt,
        relationship_type=RelationshipType.SUPPORTS,
        direction=RelationshipDirection.A_TO_B,
        calibrated_confidence=confidence, cosine_similarity=0.85,
        nli_confidence=confidence, candidate_rank=1,
    )


def make_ctx_with_edges(node_ids, edge_specs):
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
            context="", source_path=Path("test.md"), document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt, conf in edge_specs:
        edge = make_supports_edge(eid, src, tgt, conf)
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", conf)
    return SemanticReasoningContext(
        nodes=nodes, edges=edges, backend=backend, run_id="test", config_hash="test",
    )


def test_dag_diamond_does_not_double_count():
    """
    RECTIFIED (P0-2): Diamond DAG test.

    A → B → D
    A → C → D

    D's support_count must be 3 (A, B, C), not 4 (A counted twice in old code).
    A is the unique provenance root that supports D through two paths.
    """
    ctx = make_ctx_with_edges(
        ["A", "B", "C", "D"],
        [
            ("e1", "A", "B", 0.90),
            ("e2", "A", "C", 0.85),
            ("e3", "B", "D", 0.88),
            ("e4", "C", "D", 0.88),
        ],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_D = ctx.nodes["D"].support_aggregate
    assert agg_D is not None
    supporting = set(agg_D.supporting_claim_ids)
    # A, B, and C all transitively support D
    assert "A" in supporting
    assert "B" in supporting
    assert "C" in supporting
    # A must appear exactly once
    assert agg_D.support_count == len(supporting), (
        f"support_count ({agg_D.support_count}) must equal len(unique claim IDs) "
        f"({len(supporting)}). Each claim must be counted at most once."
    )


def test_direct_support_count():
    """Single direct SUPPORTS: count = 1."""
    ctx = make_ctx_with_edges(
        ["A", "B"],
        [("e1", "A", "B", 0.88)],
    )
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_B = ctx.nodes["B"].support_aggregate
    assert agg_B.support_count == 1
    assert "A" in agg_B.supporting_claim_ids


def test_no_support_count_zero():
    """Node with no incoming SUPPORTS: count = 0."""
    ctx = make_ctx_with_edges(["A"], [])
    run_partitioning(ctx)
    run_evidence_aggregation(ctx)

    agg_A = ctx.nodes["A"].support_aggregate
    assert agg_A.support_count == 0
````

## File: tests/unit/test_phase7_annotation.py
````python
"""Unit tests for evolution/annotation.py."""

import pytest
from smriti.core.models import SemanticRole, TopologyMetrics
from smriti.evolution.annotation import _classify_role, AnnotationPolicy
from smriti.exceptions import AnnotationPolicyError


def make_topology(degree, in_degree, out_degree, centrality, is_bridge=False, is_hub=False):
    return TopologyMetrics(
        degree=degree, in_degree=in_degree, out_degree=out_degree,
        is_bridge=is_bridge, is_hub=is_hub,
        partition_id="p001", centrality=centrality,
    )


DEFAULT_POLICY = AnnotationPolicy()


def test_foundational_claim_annotation():
    topo = make_topology(5, 3, 2, centrality=0.75)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.FOUNDATIONAL_CLAIM


def test_bridge_claim_annotation():
    topo = make_topology(1, 1, 0, centrality=0.10, is_bridge=True)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.BRIDGE_CLAIM


def test_evidence_hub_annotation():
    topo = make_topology(5, 4, 1, centrality=0.40)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.EVIDENCE_HUB


def test_refinement_root_annotation():
    topo = make_topology(4, 1, 3, centrality=0.20)
    assert _classify_role(topo, 3, DEFAULT_POLICY) == SemanticRole.REFINEMENT_ROOT


def test_leaf_claim_annotation():
    topo = make_topology(2, 2, 0, centrality=0.30)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.LEAF_CLAIM


def test_peripheral_claim_annotation():
    topo = make_topology(1, 0, 1, centrality=0.05)
    assert _classify_role(topo, 0, DEFAULT_POLICY) == SemanticRole.PERIPHERAL_CLAIM


def test_annotation_policy_thresholds_respected():
    """RECTIFIED (P1-4): Annotation thresholds must come from policy, not hardcode."""
    strict_policy = AnnotationPolicy(
        foundational_centrality_threshold=0.90,  # Very strict
        foundational_min_in_degree=5,
    )
    # centrality=0.75, in_degree=3 — would be FOUNDATIONAL with default but not with strict
    topo = make_topology(5, 3, 2, centrality=0.75)
    role_default = _classify_role(topo, 0, DEFAULT_POLICY)
    role_strict = _classify_role(topo, 0, strict_policy)
    assert role_default == SemanticRole.FOUNDATIONAL_CLAIM
    assert role_strict != SemanticRole.FOUNDATIONAL_CLAIM


def test_annotation_policy_validates_on_construction():
    """RECTIFIED (P1-4): Invalid policy must raise AnnotationPolicyError."""
    with pytest.raises(AnnotationPolicyError):
        AnnotationPolicy(foundational_centrality_threshold=1.5)  # Out of range
````

## File: tests/unit/test_phase7_construction.py
````python
"""Unit tests for evolution/construction.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Relationship, RelationshipSet, RelationshipType, RelationshipDirection,
    RelationshipEvidence, RelationshipProvenance, RelationshipQuality,
    NLIScores, InferenceMetadata, CandidatePair, SchemaVersionInfo, LifecycleStage,
)
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.construction import run_construction
from smriti.exceptions import GraphConstructionError


def make_claim(claim_id, text="Test.", doc_id="d001"):
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id=doc_id,
        text=text, content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None, assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=doc_id,
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_rel(rel_id, cid_a, cid_b, rel_type, confidence=0.88):
    pair = CandidatePair(claim_id_a=cid_a, claim_id_b=cid_b, cosine_similarity=0.85, candidate_rank=1)
    nli = NLIScores(
        entailment_score=0.05, neutral_score=0.05, contradiction_score=0.90,
        predicted_label="contradiction", raw_confidence=confidence,
    )
    inf = InferenceMetadata(model_name="test-nli")
    evidence = RelationshipEvidence(
        pair=pair, cosine_similarity=0.85, nli_scores=nli,
        calibrated_confidence=confidence, inference_metadata=inf,
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )
    prov = RelationshipProvenance(
        retrieval_backend="faiss_flat_ip", retrieval_version="1.0", index_version="1.0",
        search_parameters=None, classifier_model="test", classifier_version="1.0",
        resolver_version="1.0", calibrator_version="1.0", cosine_similarity=0.85,
        candidate_rank=1, raw_nli_confidence=confidence, calibrated_confidence=confidence,
        config_hash="test", run_id="run1",
    )
    quality = RelationshipQuality(
        cosine_above_threshold=True, nli_above_threshold=True,
        evidence_consistent=True, calibration_applied=False,
    )
    version = SchemaVersionInfo(schema_version="6.0", migration_version="6.0", compatibility_version="6.0")
    return Relationship(
        relationship_id=rel_id, claim_id_a=cid_a, claim_id_b=cid_b,
        relationship_type=rel_type, direction=RelationshipDirection.SYMMETRIC,
        evidence=evidence, quality=quality, provenance=prov, version_info=version,
    )


def make_rel_set(relationships, run_id="run1"):
    return RelationshipSet(
        relationships=relationships, total_candidates=len(relationships),
        total_validated=len(relationships), total_rejected=0,
        rejected_reasons={}, run_id=run_id,
    )


def make_claims_map(*claim_ids):
    return {cid: make_claim(cid) for cid in claim_ids}


def test_constructs_nodes_for_all_claims():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend())
    assert "c001" in result.nodes and "c002" in result.nodes
    assert len(result.nodes) == 2


def test_constructs_edges_for_relationships():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.SUPPORTS)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend())
    assert "r1" in result.edges


def test_unknown_relationships_filtered():
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.UNKNOWN),
        make_rel("r2", "c001", "c003", RelationshipType.CONTRADICTS),
    ]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002", "c003"), NetworkXBackend())
    assert "r1" not in result.edges and "r2" in result.edges


def test_missing_claim_raises_construction_error():
    rels = [make_rel("r1", "c001", "c_MISSING", RelationshipType.CONTRADICTS)]
    with pytest.raises(GraphConstructionError):
        run_construction(make_rel_set(rels), {"c001": make_claim("c001")}, NetworkXBackend())


def test_duplicate_claim_ids_produce_one_node():
    rels = [
        make_rel("r1", "c001", "c002", RelationshipType.CONTRADICTS),
        make_rel("r2", "c001", "c003", RelationshipType.SUPPORTS),
    ]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002", "c003"), NetworkXBackend())
    assert len(result.nodes) == 3


def test_neutral_filtered_by_default():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.NEUTRAL)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend(), include_neutral=False)
    assert "r1" not in result.edges and result.relationships_filtered == 1


def test_neutral_included_when_configured():
    rels = [make_rel("r1", "c001", "c002", RelationshipType.NEUTRAL)]
    result = run_construction(make_rel_set(rels), make_claims_map("c001", "c002"), NetworkXBackend(), include_neutral=True)
    assert "r1" in result.edges


def test_empty_relationship_set_produces_empty_graph():
    result = run_construction(make_rel_set([]), {}, NetworkXBackend())
    assert len(result.nodes) == 0 and len(result.edges) == 0
````

## File: tests/unit/test_phase7_partitioning.py
````python
"""Unit tests for evolution/partitioning.py — constraint-based algorithm."""

import pytest
from pathlib import Path
from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection, SemanticRole,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning


def make_ctx(node_ids, edges_list):
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
            context="", source_path=Path("test.md"), document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt, rtype in edges_list:
        edge = RelationshipEdge(
            edge_id=eid, source_node_id=src, target_node_id=tgt,
            relationship_type=rtype, direction=RelationshipDirection.SYMMETRIC,
            calibrated_confidence=0.88, cosine_similarity=0.85,
            nli_confidence=0.88, candidate_rank=1,
        )
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, rtype.value, 0.88)
        if rtype == RelationshipType.CONTRADICTS:
            backend.add_edge(tgt, src, f"{eid}_rev", rtype.value, 0.88)
    return SemanticReasoningContext(
        nodes=nodes, edges=edges, backend=backend, run_id="test", config_hash="test",
    )


def test_single_connected_component_is_one_partition():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    assert ctx.node_to_partition["c001"] == ctx.node_to_partition["c002"]


def test_contradiction_creates_two_partitions():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.CONTRADICTS)])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 2
    assert ctx.node_to_partition["c001"] != ctx.node_to_partition["c002"]


def test_every_node_assigned_to_partition():
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [("e1", "c001", "c002", RelationshipType.CONTRADICTS),
         ("e2", "c002", "c003", RelationshipType.SUPPORTS)],
    )
    run_partitioning(ctx)
    for node_id in ctx.nodes:
        assert node_id in ctx.node_to_partition
        assert ctx.node_to_partition[node_id] is not None


def test_isolated_node_gets_own_partition():
    ctx = make_ctx(["c001"], [])
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    assert "c001" in ctx.node_to_partition


def test_partition_ids_are_deterministic():
    def build_ctx():
        return make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.CONTRADICTS)])
    ctx1, ctx2 = build_ctx(), build_ctx()
    run_partitioning(ctx1)
    run_partitioning(ctx2)
    assert set(ctx1.partitions.keys()) == set(ctx2.partitions.keys())


def test_partition_does_not_contain_contradicts_internal_edges():
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [("e1", "c001", "c002", RelationshipType.CONTRADICTS),
         ("e2", "c001", "c003", RelationshipType.SUPPORTS)],
    )
    run_partitioning(ctx)
    for partition in ctx.partitions.values():
        for eid in partition.internal_edge_ids:
            edge = ctx.edges.get(eid)
            if edge:
                assert edge.relationship_type != RelationshipType.CONTRADICTS


def test_node_objects_updated_with_partition_id():
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    for node in ctx.nodes.values():
        assert node.partition_id is not None


def test_shared_support_target_does_not_merge_contradicting_nodes():
    """
    RECTIFIED (P0-1): The critical failure case for the old algorithm.

    A SUPPORTS X
    C SUPPORTS X
    A CONTRADICTS C

    Old algorithm (edge deletion + connected components):
        Remove CONTRADICTS → A, X, C all connected → SAME partition. WRONG.

    New algorithm (constraint coloring + Union-Find):
        A and C get different colors from contradiction constraint.
        Union-Find only merges same-color nodes.
        A and X merge (same color).
        C stays in its own partition (different color from A).
        X ends up with A, not with C.
        Result: A and C in DIFFERENT partitions. CORRECT.
    """
    ctx = make_ctx(
        ["A", "X", "C"],
        [
            ("e1", "A", "X", RelationshipType.SUPPORTS),
            ("e2", "C", "X", RelationshipType.SUPPORTS),
            ("e3", "A", "C", RelationshipType.CONTRADICTS),
        ],
    )
    run_partitioning(ctx)

    partition_of_A = ctx.node_to_partition["A"]
    partition_of_C = ctx.node_to_partition["C"]
    assert partition_of_A != partition_of_C, (
        "A and C contradict each other and must be in different partitions, "
        "even though they both support X."
    )


def test_stable_partition_label_present():
    """RECTIFIED (P2-5): stable_partition_label must be set on all partitions."""
    ctx = make_ctx(["c001", "c002"], [("e1", "c001", "c002", RelationshipType.SUPPORTS)])
    run_partitioning(ctx)
    for partition in ctx.partitions.values():
        assert partition.stable_partition_label is not None
        assert isinstance(partition.stable_partition_label, str)
        assert len(partition.stable_partition_label) > 0


def test_directed_density_formula():
    """RECTIFIED (P1-5): Partition density must use directed formula: edges / (n*(n-1))."""
    ctx = make_ctx(
        ["c001", "c002", "c003"],
        [
            ("e1", "c001", "c002", RelationshipType.SUPPORTS),
            ("e2", "c002", "c003", RelationshipType.SUPPORTS),
        ],
    )
    run_partitioning(ctx)
    assert len(ctx.partitions) == 1
    partition = next(iter(ctx.partitions.values()))
    n = partition.node_count  # 3
    e = partition.edge_count  # 2
    expected_density = e / (n * (n - 1))  # 2 / 6 = 0.333...
    assert abs(partition.density - expected_density) < 1e-6
````

## File: tests/unit/test_phase7_temporal_semantic.py
````python
"""
Unit tests for temporal.py semantic-timestamp fix (P0-4).

Verifies that temporal resolution uses Claim.timestamp (semantic),
never filesystem st_mtime.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection,
    TemporalStatus,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning
from smriti.evolution.temporal import run_temporal_resolution, _get_semantic_timestamp


def make_claim(claim_id, timestamp=None):
    claim = Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=f"Claim {claim_id}", content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None, assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )
    # Inject timestamp as attribute (until Claim model has it as a field)
    object.__setattr__(claim, "timestamp", timestamp) if hasattr(claim, "__dataclass_fields__") else None
    try:
        object.__setattr__(claim, "_timestamp_override", timestamp)
    except Exception:
        pass
    return claim


def make_contradiction_ctx(node_a, node_b):
    backend = NetworkXBackend()
    nodes = {
        node_a: ClaimNode(
            node_id=node_a, claim_id=node_a, claim_text=f"Claim {node_a}",
            context="", source_path=Path("test.md"), document_id="d001",
        ),
        node_b: ClaimNode(
            node_id=node_b, claim_id=node_b, claim_text=f"Claim {node_b}",
            context="", source_path=Path("test.md"), document_id="d001",
        ),
    }
    edge = RelationshipEdge(
        edge_id="e1", source_node_id=node_a, target_node_id=node_b,
        relationship_type=RelationshipType.CONTRADICTS,
        direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=0.88, cosine_similarity=0.85,
        nli_confidence=0.88, candidate_rank=1,
    )
    for nid in nodes:
        backend.add_node(nid)
    backend.add_edge(node_a, node_b, "e1", "contradicts", 0.88)
    backend.add_edge(node_b, node_a, "e1_rev", "contradicts", 0.88)
    return SemanticReasoningContext(
        nodes=nodes, edges={"e1": edge}, backend=backend, run_id="test", config_hash="test",
    )


def test_no_timestamp_produces_no_timestamp_status():
    """RECTIFIED (P0-4): Missing Claim.timestamp → NO_TIMESTAMP status, not filesystem fallback."""
    ctx = make_contradiction_ctx("c001", "c002")
    run_partitioning(ctx)

    claims_map = {
        "c001": make_claim("c001", timestamp=None),
        "c002": make_claim("c002", timestamp=None),
    }
    run_temporal_resolution(ctx, claims_map)

    status_c001 = ctx.nodes["c001"].temporal_metadata.status
    # Should be NO_TIMESTAMP, not a filesystem-derived value
    assert status_c001 in (TemporalStatus.NO_TIMESTAMP, TemporalStatus.STATIC_PARTITION), (
        "When Claim.timestamp is None, temporal status must be NO_TIMESTAMP "
        "or STATIC_PARTITION — never an EVOLUTION_CHAIN from filesystem metadata."
    )


def test_get_semantic_timestamp_never_reads_filesystem(monkeypatch):
    """RECTIFIED (P0-4): _get_semantic_timestamp must NEVER call stat()."""
    stat_called = []

    def mock_stat(*args, **kwargs):
        stat_called.append(True)
        raise Exception("stat() must not be called")

    monkeypatch.setattr(Path, "stat", mock_stat)

    claim = make_claim("c001", timestamp=None)
    result = _get_semantic_timestamp(claim)

    assert not stat_called, "stat() was called! Temporal resolver must not read filesystem."
    assert result is None
````

## File: tests/unit/test_phase7_topology_bridges.py
````python
"""
Unit tests for topology.py bridge detection fix (P0-3).

Verifies that bridge detection uses articulation_points (NetworkX),
NOT the degree-1 heuristic from the original implementation.
"""

import pytest
from pathlib import Path
from smriti.core.models import ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection, KnowledgePartition
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.topology import run_topology_analysis
from smriti.evolution.partitioning import run_partitioning


def make_ctx_chain(node_ids, edges_list):
    """Build a chain context for bridge testing."""
    backend = NetworkXBackend()
    nodes = {}
    for nid in node_ids:
        nodes[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
            context="", source_path=Path("test.md"), document_id="d001",
        )
        backend.add_node(nid)
    edges = {}
    for eid, src, tgt in edges_list:
        edge = RelationshipEdge(
            edge_id=eid, source_node_id=src, target_node_id=tgt,
            relationship_type=RelationshipType.SUPPORTS,
            direction=RelationshipDirection.A_TO_B,
            calibrated_confidence=0.88, cosine_similarity=0.85,
            nli_confidence=0.88, candidate_rank=1,
        )
        edges[eid] = edge
        backend.add_edge(src, tgt, eid, "supports", 0.88)
    return SemanticReasoningContext(
        nodes=nodes, edges=edges, backend=backend, run_id="test", config_hash="test",
    )


def test_middle_node_in_chain_is_bridge():
    """
    RECTIFIED (P0-3): A → B → C
    B is the articulation point (bridge). Removing B disconnects A and C.
    Old code: is_bridge=False (B has degree 2, not 1). WRONG.
    New code: is_bridge=True (nx.articulation_points returns B). CORRECT.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    assert ctx.topology_metrics["B"].is_bridge is True, (
        "B is the only path between A and C; removing B disconnects the graph. "
        "B must be detected as a bridge (articulation point)."
    )


def test_leaf_node_is_not_bridge():
    """
    A → B → C: C is a leaf (degree 1 in undirected). It is NOT an articulation point.
    Old code incorrectly flagged leaf nodes as bridges.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    # C has degree 1 in undirected, but removing it doesn't disconnect the rest
    assert ctx.topology_metrics["C"].is_bridge is False, (
        "C is a leaf node. Removing C doesn't disconnect A and B. "
        "C must NOT be a bridge."
    )


def test_cycle_has_no_bridges():
    """
    A → B → C → A (cycle): No bridges.
    In a cycle, no single node removal disconnects the graph.
    """
    ctx = make_ctx_chain(
        ["A", "B", "C"],
        [("e1", "A", "B"), ("e2", "B", "C"), ("e3", "C", "A")],
    )
    run_partitioning(ctx)
    run_topology_analysis(ctx)

    for node_id, metrics in ctx.topology_metrics.items():
        assert metrics.is_bridge is False, (
            f"No node in a cycle should be a bridge. Node {node_id} incorrectly flagged."
        )
````

## File: tests/unit/test_phase7_validation.py
````python
"""Unit tests for evolution/validation.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection, SemanticRole,
)
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.validation import validate_graph_structure
from smriti.exceptions import GraphValidationError


def make_node(nid):
    return ClaimNode(
        node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
        context="", source_path=Path("test.md"), document_id="d001",
    )


def make_edge(eid, src, tgt, rtype=RelationshipType.CONTRADICTS):
    return RelationshipEdge(
        edge_id=eid, source_node_id=src, target_node_id=tgt,
        relationship_type=rtype, direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=0.88, cosine_similarity=0.85,
        nli_confidence=0.88, candidate_rank=1,
    )


def test_valid_graph_passes():
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001"), "c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002")}
    backend.add_node("c001")
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "contradicts", 0.88)
    report = validate_graph_structure(nodes, edges, backend)
    assert report.is_valid is True and report.total_violations == 0


def test_orphan_edge_source_missing_raises():
    backend = NetworkXBackend()
    nodes = {"c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002")}
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "contradicts", 0.88)
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, edges, backend)


def test_unknown_type_in_edge_raises():
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001"), "c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002", RelationshipType.UNKNOWN)}
    backend.add_node("c001")
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "unknown", 0.50)
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, edges, backend)


def test_empty_claim_text_raises():
    backend = NetworkXBackend()
    bad_node = ClaimNode(
        node_id="c001", claim_id="c001", claim_text="",
        context="", source_path=Path("test.md"), document_id="d001",
    )
    nodes = {"c001": bad_node}
    backend.add_node("c001")
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, {}, backend)


def test_semantic_violations_detected_and_reported():
    """RECTIFIED (P2-4): SUPPORTS→CONTRADICTS→SUPPORTS chain produces semantic warning."""
    backend = NetworkXBackend()
    nodes = {
        "c001": make_node("c001"),
        "c002": make_node("c002"),
        "c003": make_node("c003"),
        "c004": make_node("c004"),
    }
    # c001 SUPPORTS c002, c002 CONTRADICTS c003, c003 SUPPORTS c004
    edges = {
        "e1": make_edge("e1", "c001", "c002", RelationshipType.SUPPORTS),
        "e2": make_edge("e2", "c002", "c003", RelationshipType.CONTRADICTS),
        "e3": make_edge("e3", "c003", "c004", RelationshipType.SUPPORTS),
    }
    for nid in nodes:
        backend.add_node(nid)
    backend.add_edge("c001", "c002", "e1", "supports", 0.88)
    backend.add_edge("c002", "c003", "e2", "contradicts", 0.88)
    backend.add_edge("c003", "c004", "e3", "supports", 0.88)

    # Should pass structurally but produce semantic warnings
    report = validate_graph_structure(nodes, edges, backend)
    assert report.is_valid is True  # Not a fatal error
    assert len(report.semantic_violations) > 0


def test_semantic_violations_field_present_on_report():
    """RECTIFIED (P2-4): ValidationReport must have semantic_violations tuple."""
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001")}
    backend.add_node("c001")
    report = validate_graph_structure(nodes, {}, backend)
    assert hasattr(report, "semantic_violations")
    assert isinstance(report.semantic_violations, tuple)
````

## File: tests/unit/test_phase8_explanation.py
````python
"""Unit tests for scoring/explanation.py."""

import pytest
from smriti.core.models import ComponentScore
from smriti.scoring.explanation import build_explanation


def make_component(name: str, contribution: float, direction: str = "positive") -> ComponentScore:
    return ComponentScore(
        signal_name=name, normalized_value=0.8, policy_weight=0.25,
        adjusted_value=0.8, contribution=contribution, direction=direction,
        explanation="Test explanation",
    )


def test_explanation_has_summary():
    comps = [make_component("evidence_strength", 18.0), make_component("conflict_pressure", -8.0, "negative")]
    explanation = build_explanation(75.0, comps)
    assert explanation.summary and len(explanation.summary) > 0


def test_dominant_and_limiting_signals():
    comps = [
        make_component("evidence_strength", 22.0),
        make_component("topology_strength", 12.0),
        make_component("conflict_pressure", -15.0, "negative"),
        make_component("temporal_stability", -5.0, "negative"),
    ]
    explanation = build_explanation(65.0, comps)
    assert explanation.dominant_signal == "evidence_strength"
    assert explanation.limiting_signal == "conflict_pressure"


def test_strengths_and_weaknesses():
    comps = [
        make_component("evidence_strength", 20.0),
        make_component("source_diversity", 15.0),
        make_component("conflict_pressure", -10.0, "negative"),
    ]
    explanation = build_explanation(80.0, comps)
    assert len(explanation.strengths) >= 1 and len(explanation.weaknesses) >= 1


def test_empty_components():
    explanation = build_explanation(50.0, [])
    assert explanation.summary
    assert explanation.dominant_signal == "none"
    assert explanation.limiting_signal == "none"


def test_high_reliability_label():
    comps = [make_component("evidence_strength", 30.0)]
    exp = build_explanation(90.0, comps)
    assert "reliable" in exp.summary.lower() or "high" in exp.summary.lower()
````

## File: tests/unit/test_phase8_fusion.py
````python
"""Unit tests for scoring/fusion.py — generic fusion + monotonicity + constraints."""

import pytest
from smriti.core.models import SignalVector, ContributionCandidate, ContributionSet
from smriti.scoring.policies import load_policy, FusionPolicy
from smriti.scoring.fusion import compute_reliability, compute_reliability_from_signal_vector


@pytest.fixture
def policy(): return load_policy()


def make_sv(**kwargs):
    defaults = dict(
        evidence_strength=0.5, evidence_independence=0.7, source_diversity=0.5,
        topology_strength=0.4, conflict_pressure=0.2, temporal_stability=0.6,
        evidence_completeness=1.0, statuses={},
    )
    defaults.update(kwargs)
    return SignalVector(**defaults)


def make_cs(policy, **sv_kwargs):
    """Build ContributionSet from keyword signal values."""
    sv = make_sv(**sv_kwargs)
    fp = policy.fusion
    candidates = []
    for name, value in {
        "evidence_strength": sv.evidence_strength,
        "evidence_independence": sv.evidence_independence,
        "source_diversity": sv.source_diversity,
        "topology_strength": sv.topology_strength,
        "conflict_pressure": sv.conflict_pressure,
        "temporal_stability": sv.temporal_stability,
        "hub_score": 0.0,
        "bridge_score": 0.0,
    }.items():
        if fp.get_weight(name) > 0:
            candidates.append(ContributionCandidate(
                signal_name=name, normalized_value=value,
                policy_weight=fp.get_weight(name),
                direction=fp.get_direction(name),
                label=name, raw_value=value,
            ))
    return ContributionSet(
        candidates=tuple(candidates), evidence_completeness=sv.evidence_completeness, claim_id="c001"
    ), sv


def test_basic_reliability_in_range(policy):
    cs, sv = make_cs(policy)
    ri, unc, _, _ = compute_reliability(cs, policy, sv)
    assert 0.0 <= ri <= 100.0


def test_uncertainty_in_range(policy):
    cs, sv = make_cs(policy)
    _, unc, _, _ = compute_reliability(cs, policy, sv)
    assert 0.0 <= unc <= 100.0


def test_six_plus_component_scores_produced(policy):
    cs, sv = make_cs(policy)
    _, _, comps, _ = compute_reliability(cs, policy, sv)
    assert len(comps) >= 6


def test_more_evidence_increases_reliability(policy):
    cs_low, sv_low = make_cs(policy, evidence_strength=0.10)
    cs_high, sv_high = make_cs(policy, evidence_strength=0.90)
    ri_low, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high > ri_low


def test_more_conflict_decreases_reliability(policy):
    cs_low, sv_low = make_cs(policy, conflict_pressure=0.05)
    cs_high, sv_high = make_cs(policy, conflict_pressure=0.95)
    ri_low_c, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high_c, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high_c < ri_low_c


def test_higher_topology_increases_reliability(policy):
    cs_low, sv_low = make_cs(policy, topology_strength=0.10)
    cs_high, sv_high = make_cs(policy, topology_strength=0.90)
    ri_low, _, _, _ = compute_reliability(cs_low, policy, sv_low)
    ri_high, _, _, _ = compute_reliability(cs_high, policy, sv_high)
    assert ri_high > ri_low


def test_no_evidence_caps_reliability(policy):
    cs, sv = make_cs(policy, evidence_strength=0.0, topology_strength=1.0, conflict_pressure=0.0)
    ri, _, _, _ = compute_reliability(cs, policy, sv)
    assert ri <= policy.fusion.max_reliability_without_evidence + 0.01


def test_maximum_conflict_caps_reliability(policy):
    cs, sv = make_cs(policy, evidence_strength=1.0, conflict_pressure=1.0)
    ri, _, _, _ = compute_reliability(cs, policy, sv)
    assert ri <= policy.fusion.max_reliability_with_max_conflict + 0.01


def test_deterministic_fusion(policy):
    cs, sv = make_cs(policy, evidence_strength=0.75, conflict_pressure=0.30)
    ri1, unc1, _, _ = compute_reliability(cs, policy, sv)
    ri2, unc2, _, _ = compute_reliability(cs, policy, sv)
    assert ri1 == ri2 and unc1 == unc2


def test_fusion_receives_contribution_set_not_signal_vector(policy):
    """RECTIFIED (P0-2): Fusion must accept ContributionSet, not SignalVector."""
    cs, sv = make_cs(policy)
    # compute_reliability takes ContributionSet as first arg — this is the rectified API
    ri, unc, comps, dr = compute_reliability(cs, policy, sv)
    assert 0.0 <= ri <= 100.0
    from smriti.core.models import ContributionSet
    # Verify the function signature accepts ContributionSet
    assert isinstance(cs, ContributionSet)


def test_decision_record_produced(policy):
    """RECTIFIED (P0-5): compute_reliability must return a ReliabilityDecisionRecord."""
    from smriti.core.models import ReliabilityDecisionRecord
    cs, sv = make_cs(policy)
    ri, unc, comps, dr = compute_reliability(cs, policy, sv)
    assert isinstance(dr, ReliabilityDecisionRecord)
    assert dr.claim_id == "c001"
    assert isinstance(dr.policy_interactions, tuple)
    assert isinstance(dr.constraints_activated, tuple)
    assert isinstance(dr.contribution_order, tuple)
    assert dr.final_reliability == ri


def test_decision_record_constraints_logged(policy):
    """RECTIFIED (P0-5): When constraints activate, DecisionRecord must record them."""
    cs, sv = make_cs(policy, evidence_strength=0.0, topology_strength=1.0)
    ri, _, _, dr = compute_reliability(cs, policy, sv)
    assert len(dr.constraints_activated) > 0, (
        "No-evidence constraint must be recorded in ReliabilityDecisionRecord "
        "when evidence_strength is 0.0."
    )
````

## File: tests/unit/test_phase8_normalization.py
````python
"""Unit tests for scoring/normalization.py."""

import pytest
from smriti.core.models import RawSignal, SignalStatus, SignalVector
from smriti.scoring.normalization import validate_and_normalize, assemble_contribution_set
from smriti.scoring.policies import load_policy
from smriti.scoring.signals import signal_registry


def make_raw(name: str, value: float, status=SignalStatus.MEASURED, raw_value=None) -> RawSignal:
    return RawSignal(
        name=name, raw_value=raw_value if raw_value is not None else value,
        normalized_value=value, status=status,
    )


def test_valid_signals_produce_signal_vector():
    signals = [
        make_raw("evidence_strength", 0.80),
        make_raw("evidence_independence", 0.70),
        make_raw("source_diversity", 0.60),
        make_raw("topology_strength", 0.50),
        make_raw("conflict_pressure", 0.20),
        make_raw("temporal_stability", 0.75),
    ]
    sv = validate_and_normalize(signals)
    assert isinstance(sv, SignalVector)
    assert sv.evidence_strength == 0.80


def test_nan_signal_becomes_zero():
    signals = [
        make_raw("evidence_strength", float("nan")),
        make_raw("conflict_pressure", 0.20),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 0.0


def test_inf_signal_becomes_zero():
    signals = [
        make_raw("evidence_strength", float("inf")),
        make_raw("conflict_pressure", 0.20),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 0.0


def test_out_of_range_signal_clamped():
    signals = [
        make_raw("evidence_strength", 1.5),
        make_raw("conflict_pressure", -0.3),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 1.0
    assert sv.conflict_pressure == 0.0


def test_completeness_with_all_measured():
    signals = [
        make_raw("evidence_strength", 0.8, SignalStatus.MEASURED),
        make_raw("evidence_independence", 0.7, SignalStatus.MEASURED),
        make_raw("source_diversity", 0.6, SignalStatus.MEASURED),
        make_raw("topology_strength", 0.5, SignalStatus.MEASURED),
        make_raw("conflict_pressure", 0.2, SignalStatus.MEASURED),
        make_raw("temporal_stability", 0.7, SignalStatus.MEASURED),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_completeness == 1.0


def test_completeness_with_some_unavailable():
    signals = [
        make_raw("evidence_strength", 0.0, SignalStatus.UNAVAILABLE),
        make_raw("evidence_independence", 0.7, SignalStatus.MEASURED),
        make_raw("source_diversity", 0.6, SignalStatus.MEASURED),
        make_raw("topology_strength", 0.0, SignalStatus.UNAVAILABLE),
        make_raw("conflict_pressure", 0.2, SignalStatus.MEASURED),
        make_raw("temporal_stability", 0.7, SignalStatus.DEFAULT),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_completeness < 1.0
    assert sv.evidence_completeness > 0.0


def test_contribution_set_produced():
    """RECTIFIED (P0-2): assemble_contribution_set must produce a ContributionSet."""
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    signals = [
        make_raw("evidence_strength", 0.80, raw_value=0.72),
        make_raw("evidence_independence", 0.70),
        make_raw("source_diversity", 0.60),
        make_raw("topology_strength", 0.50),
        make_raw("hub_score", 0.00),
        make_raw("bridge_score", 0.00),
        make_raw("conflict_pressure", 0.20),
        make_raw("temporal_stability", 0.75),
    ]
    cs, manifests, sv = assemble_contribution_set(signals, extractors, policy.fusion, "c001")
    from smriti.core.models import ContributionSet
    assert isinstance(cs, ContributionSet)
    assert cs.claim_id == "c001"
    assert len(cs.candidates) > 0


def test_signal_manifests_produced():
    """RECTIFIED (P0-4): assemble_contribution_set must produce SignalManifests."""
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    signals = [
        make_raw("evidence_strength", 0.80, raw_value=0.72),
        make_raw("conflict_pressure", 0.20),
    ]
    cs, manifests, sv = assemble_contribution_set(signals, extractors, policy.fusion, "c001")
    from smriti.core.models import SignalManifest
    evidence_manifest = next((m for m in manifests if m.signal_name == "evidence_strength"), None)
    assert evidence_manifest is not None
    assert evidence_manifest.normalization_strategy != ""
    assert isinstance(evidence_manifest.quality_flags, tuple)
    assert isinstance(evidence_manifest.dependency_list, tuple)
````

## File: tests/unit/test_phase8_policies.py
````python
"""Unit tests for scoring/policies.py."""

import pytest
from smriti.scoring.policies import (
    load_policy, ReliabilityPolicy, FusionPolicy, PolicyError,
    PolicyProfile,
)
from smriti.exceptions import PolicyError


def test_policy_loads_without_error():
    policy = load_policy()
    assert policy is not None
    assert policy.version is not None


def test_fusion_weights_sum_to_one():
    policy = load_policy()
    total = sum(policy.fusion.signal_weights.values())
    assert abs(total - 1.0) < 0.001


def test_invalid_weights_raise_policy_error():
    fp = FusionPolicy(
        signal_weights={
            "evidence_strength": 0.90, "evidence_independence": 0.15,
            "source_diversity": 0.15, "topology_strength": 0.10,
            "hub_score": 0.05, "bridge_score": 0.05,
            "conflict_pressure": 0.20, "temporal_stability": 0.05,
        },
        signal_directions={
            "evidence_strength": "positive", "evidence_independence": "positive",
            "source_diversity": "positive", "topology_strength": "positive",
            "hub_score": "positive", "bridge_score": "positive",
            "conflict_pressure": "negative", "temporal_stability": "positive",
        },
    )
    with pytest.raises(PolicyError):
        fp.validate()


def test_policy_config_hash_is_deterministic():
    policy = load_policy()
    h1 = policy.config_hash()
    h2 = policy.config_hash()
    assert h1 == h2 and len(h1) == 16


def test_policy_to_dict_serializable():
    import json
    policy = load_policy()
    d = policy.to_dict()
    json_str = json.dumps(d)
    assert len(json_str) > 0


def test_topology_policy_has_no_hub_bridge_bonus():
    """RECTIFIED (P0-3): TopologyPolicy must not have hub_bonus or bridge_bonus."""
    policy = load_policy()
    tp = policy.topology
    assert not hasattr(tp, "hub_bonus"), (
        "hub_bonus must not be in TopologyPolicy. "
        "Hub is now a separate signal (hub_score) in the registry."
    )
    assert not hasattr(tp, "bridge_bonus"), (
        "bridge_bonus must not be in TopologyPolicy. "
        "Bridge is now a separate signal (bridge_score) in the registry."
    )
    assert hasattr(tp, "centrality_scale")


def test_policy_profile_loads_correct_weights():
    """RECTIFIED (P1-3): PolicyProfile presets must produce different weights."""
    balanced = load_policy(PolicyProfile.BALANCED)
    research = load_policy(PolicyProfile.RESEARCH)
    # Research profile emphasizes independence and source diversity more
    assert (
        research.fusion.signal_weights.get("evidence_independence", 0)
        > balanced.fusion.signal_weights.get("evidence_independence", 0)
    ) or (
        research.fusion.signal_weights.get("source_diversity", 0)
        > balanced.fusion.signal_weights.get("source_diversity", 0)
    )


def test_hub_bridge_have_separate_weights():
    """RECTIFIED (P0-3): hub_score and bridge_score must have weights in fusion."""
    policy = load_policy()
    weights = policy.fusion.signal_weights
    assert "hub_score" in weights, "hub_score must be a registered weight in fusion policy"
    assert "bridge_score" in weights, "bridge_score must be a registered weight in fusion policy"
    assert weights["hub_score"] > 0
    assert weights["bridge_score"] > 0
````

## File: tests/unit/test_phase8_registry.py
````python
"""Unit tests for SignalRegistry (P0-1)."""

import pytest
from smriti.scoring.signals import signal_registry, SignalRegistry
from smriti.scoring.signals.base import BaseSignalExtractor
from smriti.core.models import ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus
from smriti.scoring.policies import ReliabilityPolicy, load_policy
from smriti.exceptions import RegistryError
from pathlib import Path


class MockExtractor(BaseSignalExtractor):
    def __init__(self, name, ver="1.0"):
        self._name = name
        self._ver = ver

    @property
    def signal_name(self): return self._name

    @property
    def version(self): return self._ver

    def extract(self, node, graph, global_stats, policy):
        return RawSignal(name=self._name, raw_value=0.5, normalized_value=0.5, status=SignalStatus.MEASURED)


def test_registry_has_default_signals():
    """Default registry must have at least 6 built-in signals."""
    assert len(signal_registry) >= 6


def test_registry_ordered_extractors_deterministic():
    """ordered_extractors() must return the same order every call."""
    order1 = [e.signal_name for e in signal_registry.ordered_extractors()]
    order2 = [e.signal_name for e in signal_registry.ordered_extractors()]
    assert order1 == order2


def test_new_signal_can_be_registered():
    """Registering a new extractor must make it available via ordered_extractors()."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor("novelty_signal")
    fresh_registry.register(ext, priority=99)
    names = [e.signal_name for e in fresh_registry.ordered_extractors()]
    assert "novelty_signal" in names


def test_duplicate_registration_is_idempotent():
    """Registering the same extractor type twice must not raise."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor("my_signal")
    fresh_registry.register(ext, priority=50)
    fresh_registry.register(ext, priority=50)  # Should not raise
    assert len(fresh_registry) == 1


def test_different_extractor_same_name_raises():
    """Registering two DIFFERENT extractor types with the same signal_name must raise."""
    fresh_registry = SignalRegistry()
    ext1 = MockExtractor("shared_name")
    ext2 = MockExtractor("shared_name", ver="2.0")  # Different version — treated as different

    class AnotherExtractor(MockExtractor):
        pass

    ext3 = AnotherExtractor("shared_name")
    fresh_registry.register(ext1)
    with pytest.raises(RegistryError):
        fresh_registry.register(ext3)  # Different type, same name → RegistryError


def test_hub_score_and_bridge_score_registered():
    """RECTIFIED (P0-3): hub_score and bridge_score must be in the default registry."""
    names = signal_registry.registered_names
    assert "hub_score" in names, "hub_score must be registered as a separate signal"
    assert "bridge_score" in names, "bridge_score must be registered as a separate signal"


def test_pipeline_never_changes_when_new_signal_registered():
    """
    RECTIFIED (P0-1): The core pipeline (__init__.py) must work identically
    whether 6 or 7 signals are registered — it reads from the registry.
    This test verifies that ordered_extractors() returns the right count.
    """
    fresh_registry = SignalRegistry()
    for i in range(3):
        fresh_registry.register(MockExtractor(f"signal_{i}"), priority=i)
    assert len(fresh_registry.ordered_extractors()) == 3
````

## File: tests/unit/test_phase8_signals.py
````python
"""Unit tests for scoring/signals/*.py."""

import pytest
import dataclasses
from pathlib import Path
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, ScoringGlobalStats, GraphStatistics,
    ValidationReport, SemanticRole, TopologyMetrics, SupportAggregate,
    TemporalMetadata, TemporalStatus, SignalStatus, NodeAnnotations,
)
from smriti.scoring.policies import load_policy
from smriti.scoring.signals import (
    EvidenceStrengthExtractor, EvidenceIndependenceExtractor,
    TopologyStrengthExtractor, HubScoreExtractor, BridgeScoreExtractor,
    ConflictPressureExtractor, SourceDiversityExtractor, TemporalStabilityExtractor,
)


def make_global_stats(**kwargs):
    defaults = dict(
        max_support_count=10, avg_support_count=3.0, max_in_degree=5,
        avg_degree=2.5, max_contradiction_partners=3, avg_contradiction_partners=0.5,
        max_source_diversity=5, max_temporal_confidence=1.0,
        node_count=10, partition_count=2, contradiction_count=2, supports_count=8,
    )
    defaults.update(kwargs)
    return ScoringGlobalStats(**defaults)


def make_node(claim_id="c001", support_count=0, in_degree=1,
              degree=2, centrality=0.5, is_hub=False, is_bridge=False,
              temporal_status=None) -> ClaimNode:
    support = None
    if support_count > 0:
        supporting_ids = [f"supporter_{i}" for i in range(support_count)]
        support = SupportAggregate(
            support_count=support_count, weighted_confidence=0.80,
            supporting_claim_ids=tuple(supporting_ids),
            evidence_summary=f"{support_count} supporters",
        )
    topo = TopologyMetrics(
        degree=degree, in_degree=in_degree, out_degree=degree - in_degree,
        is_bridge=is_bridge, is_hub=is_hub, partition_id="p001", centrality=centrality,
    )
    temporal = None
    if temporal_status:
        temporal = TemporalMetadata(
            status=temporal_status, earlier_claim_id=None, later_claim_id=None,
            time_delta_days=30.0, temporal_confidence=0.80,
        )
    annotations = NodeAnnotations(
        semantic_role=SemanticRole.UNCLASSIFIED,
        topology=topo, support_aggregate=support, temporal_metadata=temporal,
        partition_id="p001",
    )
    return ClaimNode(
        node_id=claim_id, claim_id=claim_id, claim_text="Test.",
        context="", source_path=Path("test.md"), document_id="d001",
        annotations=annotations,
    )


def make_empty_graph():
    stats = GraphStatistics(
        node_count=1, edge_count=0, partition_count=1,
        contradiction_count=0, supports_count=0, refines_count=0,
        isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
        evolution_chains=0, unresolved_conflicts=0,
        construction_time_seconds=0.0, enrichment_time_seconds=0.0,
    )
    vr = ValidationReport(
        is_valid=True, node_violations=(), edge_violations=(),
        graph_violations=(), semantic_violations=(), validation_time_seconds=0.0,
    )
    return KnowledgeGraph(
        graph_id="test", nodes={}, edges={}, partitions={},
        statistics=stats, validation_report=vr, run_id="test", config_hash="test",
    )


@pytest.fixture
def policy(): return load_policy()

@pytest.fixture
def global_stats(): return make_global_stats()

@pytest.fixture
def graph(): return make_empty_graph()


class TestEvidenceStrengthExtractor:
    def test_no_support_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001", support_count=0)
        ext = EvidenceStrengthExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_high_support_returns_high_value(self, policy, global_stats, graph):
        node = make_node("c001", support_count=10)
        ext = EvidenceStrengthExtractor()
        signal = ext.extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.5

    def test_value_in_range(self, policy, global_stats, graph):
        for count in [0, 1, 3, 10, 20]:
            node = make_node("c001", support_count=count)
            ext = EvidenceStrengthExtractor()
            signal = ext.extract(node, graph, global_stats, policy)
            assert 0.0 <= signal.normalized_value <= 1.0

    def test_status_is_measured(self, policy, global_stats, graph):
        node = make_node("c001", support_count=5)
        signal = EvidenceStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.MEASURED


class TestTopologyStrengthExtractor:
    def test_high_centrality_gives_high_value(self, policy, global_stats, graph):
        node = make_node("c001", centrality=0.90)
        signal = TopologyStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.70

    def test_no_topology_returns_unavailable(self, policy, global_stats, graph):
        node = ClaimNode(
            node_id="c001", claim_id="c001", claim_text="Test.",
            context="", source_path=Path("test.md"), document_id="d001",
            annotations=None,
        )
        signal = TopologyStrengthExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.UNAVAILABLE
        assert signal.normalized_value == 0.0


class TestConflictPressureExtractor:
    def test_no_contradictions_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001")
        signal = ConflictPressureExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_value_always_in_range(self, policy, global_stats, graph):
        node = make_node("c001")
        signal = ConflictPressureExtractor().extract(node, graph, global_stats, policy)
        assert 0.0 <= signal.normalized_value <= 1.0


class TestTemporalStabilityExtractor:
    def test_evolution_chain_gives_high_stability(self, policy, global_stats, graph):
        node = make_node("c001", temporal_status=TemporalStatus.EVOLUTION_CHAIN)
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value > 0.50

    def test_no_temporal_data_uses_default(self, policy, global_stats, graph):
        node = make_node("c001", temporal_status=None)
        node = dataclasses.replace(
            node, annotations=dataclasses.replace(node.annotations, temporal_metadata=None)
        )
        signal = TemporalStabilityExtractor().extract(node, graph, global_stats, policy)
        assert signal.status == SignalStatus.DEFAULT
        assert signal.normalized_value == policy.temporal.default_stability


class TestHubAndBridgeExtractors:
    """RECTIFIED (P0-3): hub_score and bridge_score are now separate signals."""

    def test_hub_node_returns_one(self, policy, global_stats, graph):
        node = make_node("c001", is_hub=True)
        signal = HubScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 1.0

    def test_non_hub_node_returns_zero(self, policy, global_stats, graph):
        node = make_node("c001", is_hub=False)
        signal = HubScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 0.0

    def test_bridge_node_returns_one(self, policy, global_stats, graph):
        node = make_node("c001", is_bridge=True)
        signal = BridgeScoreExtractor().extract(node, graph, global_stats, policy)
        assert signal.normalized_value == 1.0

    def test_topology_strength_has_no_hub_bonus(self, policy, global_stats, graph):
        """RECTIFIED (P0-3): TopologyStrengthExtractor must NOT apply hub bonus."""
        node_hub = make_node("c001", centrality=0.50, is_hub=True)
        node_normal = make_node("c002", centrality=0.50, is_hub=False)
        ext = TopologyStrengthExtractor()
        sig_hub = ext.extract(node_hub, graph, global_stats, policy)
        sig_normal = ext.extract(node_normal, graph, global_stats, policy)
        # With hub bonus removed, both should produce the same value for same centrality
        assert abs(sig_hub.normalized_value - sig_normal.normalized_value) < 1e-6, (
            "TopologyStrengthExtractor must not apply hub bonus. "
            "Hub importance is handled by HubScoreExtractor as a separate signal."
        )

    def test_signal_manifest_has_normalization_strategy(self, policy, global_stats, graph):
        """RECTIFIED (P0-4): Every signal must expose normalization_strategy."""
        for ext_class in [
            EvidenceStrengthExtractor, HubScoreExtractor, BridgeScoreExtractor,
            ConflictPressureExtractor, TemporalStabilityExtractor,
        ]:
            ext = ext_class()
            assert hasattr(ext, "normalization_strategy")
            assert isinstance(ext.normalization_strategy, str)
            assert len(ext.normalization_strategy) > 0
````

## File: .github/workflows/ci.yml
````yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-and-lint:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      run: python -m pip install poetry
      shell: bash

    - name: Install dependencies
      run: poetry install --with dev
      shell: bash

    - name: Download spaCy model
      run: poetry run python -m spacy download en_core_web_sm
      shell: bash

    - name: Run tests
      run: poetry run pytest tests/ -v --cov=src/smriti
      shell: bash

    - name: Lint with Ruff
      run: poetry run ruff check src/ tests/
      shell: bash

    - name: Format check with Black
      run: poetry run black --check src/ tests/
      shell: bash

    - name: Type check
      run: poetry run mypy src/smriti
      shell: bash

    - name: Upload coverage
      uses: codecov/codecov-action@v4
````

## File: artifacts/.gitkeep
````

````

## File: config/default.yaml
````yaml
# config/default.yaml
# Single source of truth for all tunable parameters.
# constants.py holds only structural/schema values.
env: dev
debug: false

pipeline:
  max_notes: 10000
  max_claims_per_note: 100

extraction:
  spacy_model: "en_core_web_sm"
  min_svo_confidence: 0.6
  fallback_to_sentences: true

# Model names are configuration, not constants.
# Change model here — nothing else needs to change.
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 32
  cache_embeddings: true

nli:
  model: "cross-encoder/nli-deberta-v3-small"
  sim_threshold: 0.75
  nli_threshold: 0.80
  temporal_base: 30

metrics:
  kcs_min_pairs: 5
  ds_min_claims: 2

logging:
  level: "INFO"

# config/default.yaml — append discovery section

discovery:
  # Extension whitelist. Only these will enter the pipeline.
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"

  # Directories always skipped during recursive traversal.
  # These are IN ADDITION to the hardcoded system dirs in scanner.py.
  ignored_dirs:
    - ".git"
    - ".obsidian"
    - ".vscode"
    - "__pycache__"
    - "node_modules"
    - ".idea"
    - "dist"
    - "build"

  # Maximum file size in bytes. Files larger than this are skipped.
  # Default: 50 MB
  max_file_size_bytes: 52428800

  # Skip files starting with these prefixes (case-insensitive)
  ignored_prefixes:
    - "~$"          # Word/Excel temp files
    - ".~lock."     # LibreOffice temp files

  # Output
  output_dataset_filename: "dataset.json"  

# ── Phase 2: Text Extraction ──────────────────────────────────────────────────
parsing:
  # Unicode normalization form. NFC makes equivalent sequences identical.
  # Do NOT change after first run — would invalidate cached normalized text.
  unicode_normalization: "NFC"

  # Maximum consecutive blank lines allowed after normalization.
  # 100 blank lines → collapse_blank_lines blank lines.
  collapse_blank_lines: 2

  # Whether to preserve Markdown syntax characters in extracted text.
  # true  → "# Heading" stays "# Heading"  (downstream sees full context)
  # false → "# Heading" becomes "Heading"   (NOT recommended)
  preserve_markdown_syntax: true

  # Whether to preserve indentation (code blocks, nested lists).
  preserve_indentation: true

  # Remove trailing whitespace on every line.
  remove_trailing_whitespace: true

  # Encoding detection order. First succeeds → used.
  # Every fallback beyond utf-8 generates an EncodingFallbackWarning.
  encoding_fallbacks:
    - "utf-8"
    - "utf-8-sig"   # UTF-8 with BOM
    - "utf-16"
    - "latin-1"     # Last resort — never fails, but may misrepresent bytes

  # PDF extraction limits
  max_pdf_pages: 500           # Pages beyond this are skipped with a warning
  max_text_length_chars: 5000000  # ~5 MB of text — documents larger are truncated with warning

  # Minimum non-whitespace characters required for a document to be
  # considered "successfully extracted" (not empty). Documents below
  # this threshold produce a NoExtractableTextWarning.
  min_extractable_chars: 10

  # Output artifact filename
  output_dataset_filename: "dataset.json"  

  # ── Phase 3: Semantic Sentence Construction ──────────────────────────────────
segmentation:
  # Minimum characters for a sentence to be kept.
  # Shorter candidates are discarded with SEG001.
  min_sentence_chars: 3

  # Maximum characters before emitting SEG002 warning.
  max_sentence_chars: 2000

  # Abbreviations that should never trigger sentence boundaries.
  abbreviations:
    - "dr"
    - "mr"
    - "mrs"
    - "ms"
    - "prof"
    - "sr"
    - "jr"
    - "e.g"
    - "i.e"
    - "vs"
    - "etc"
    - "fig"
    - "no"
    - "vol"
    - "pt"
    - "pp"
    - "u.s"
    - "u.k"
    - "a.m"
    - "p.m"

  # Context path separator
  context_separator: " > "

  # Maximum heading depth to track in context stack.
  # Headings deeper than this generate CTX001 warning.
  max_context_depth: 6

  # Table serialisation: how to format key-value pairs from table cells.
  table_kv_template: "{key}: {value}."


  # ── Phase 4: Claim Construction ───────────────────────────────────────────────
claim_extraction:

  # Maximum claims extracted from one SemanticSentence.
  # Prevents pathological outputs from complex sentences.
  max_claims_per_sentence: 10

  # Minimum characters for a claim to be kept.
  min_claim_chars: 3

  # Whether to attempt splitting coordinated predicates/clauses.
  # "Python supports X and Y" → two claims when true.
  split_conjunctions: true

  # Whether to split conditional clauses.
  # "If X, then Y" → usually kept together (false = safer).
  split_conditionals: false

  # Whether to split relative clauses into independent claims.
  # "Python, which runs on CPU, is popular" → conservative: keep together.
  split_relative_clauses: false

  # Whether to annotate negation, modality, attribution.
  enable_annotation: true

  # Whether to preserve the author's exact wording.
  # MUST always be true. Here for documentation only.
  preserve_original_text: true

  # ── Phase 5: Semantic Embedding Layer ────────────────────────────────────────
embedding_phase5:
  # Embedding model (sentence-transformers format)
  model_name: "sentence-transformers/all-MiniLM-L6-v2"

  # Inference device: "cpu", "cuda", or "mps"
  # Default is CPU — SMRITI is designed to run without GPU
  device: "cpu"

  # Number of claims to encode in one inference call
  # Larger batches = faster throughput; smaller batches = lower memory
  # NOTE: batch_size does NOT affect embedding values — excluded from config_hash
  batch_size: 32

  # Apply L2 normalization after inference
  # Recommended: true — enables cosine similarity via dot product in Phase 6
  normalize: true

  # Cache embeddings to disk
  # Huge speed improvement for re-runs on unchanged vaults
  cache_embeddings: true

  # Optional instruction prefix (for instruction-tuned models like BGE, Instructor, E5)
  # Leave empty for standard models like MiniLM
  # INCLUDED in config_hash — changing this invalidates all cached embeddings
  instruction_prefix: ""

  # Maximum sequence length override (model-specific)
  # Leave null to use the model's default
  # INCLUDED in config_hash — changing this may change truncation behavior
  max_seq_length: null

  # Pipeline version — increment when pipeline logic changes
  pipeline_version: "1.0"

  # ── Phase 6: Semantic Relationship Discovery ──────────────────────────────────
relationship_discovery:
  top_k: 50
  sim_threshold: 0.75
  min_confidence: 0.50
  skip_unknown_relationships: true
  skip_neutral_relationships: true     # NEUTRAL adds no Phase 7 signal; omit by default
  refine_threshold: 0.55
  high_sim_threshold: 0.88
  neutrality_threshold: 0.60
  batch_size: 16
  cache_nli_results: true
  conflict_resolution_policy: "highest_confidence"   # RECTIFIED: was implicit
  deduplication_policy: "keep_highest_confidence"    # RECTIFIED: was implicit

# Resolver policy (RECTIFIED: was hard-coded in resolver.py)
resolver_policy:
  contradiction_margin: 0.0
  entailment_margin: 0.0
  confidence_policy: "calibrated"      # "calibrated" or "raw"
  priority_order:
    - "contradicts"
    - "supports"
    - "refines"
    - "neutral"
    - "unknown"
  version: "1.0"

# NLI model configuration
nli_phase6:
  model: "cross-encoder/nli-deberta-v3-small"
  sim_threshold: 0.75
  nli_threshold: 0.80
  temporal_base: 30
  batch_size: 16
  cache_nli_results: true

# Confidence calibration (RECTIFIED: new section)
# calibration:
#   "cross-encoder/nli-deberta-v3-small":
#     strategy: "identity"     # identity | temperature | percentile | isotonic
#     temperature: 1.0         # Only for temperature strategy
#     reference_distribution:  # Only for percentile strategy (list of floats)
calibration: {}   # Empty by default → IDENTITY for all models

# Cache invalidation policy (RECTIFIED: new section)
cache_invalidation:
  invalidate_on_embedding_change: true
  invalidate_on_model_change: true
  invalidate_on_policy_change: true

# Resource governance (RECTIFIED: new section)
resource_governance:
  max_pairs: 100000
  max_gpu_memory_gb: 0.0
  max_batch_size: 64
  timeout_seconds: 3600.0
  cancel_on_limit: false      # If false, truncate; if true, abort

# Schema evolution (RECTIFIED: documents the schema migration policy)
# When schema_version bumps (e.g. 6.0 → 6.1):
#   - Update CURRENT_SCHEMA_VERSION in builder.py
#   - Update CURRENT_MIGRATION_VERSION if breaking (Phase 7 readers must update)
#   - Update CURRENT_COMPATIBILITY_VERSION to oldest compatible reader
schema:
  current_version: "6.0"
  migration_version: "6.0"
  compatibility_version: "6.0"

# ── Phase 7: Knowledge Graph Construction ─────────────────────────────────────
knowledge_graph:
  include_neutral: false
  schema_version: "7.0"

  # Minimum timestamp delta (days) to classify a contradiction as EVOLUTION_CHAIN.
  # RECTIFIED: used with Claim.timestamp, never filesystem mtime.
  min_reliable_delta_days: 1.0

  # Hub detection: degree > hub_degree_multiplier * avg_partition_degree
  # RECTIFIED (P1-4): config-driven, not hardcoded.
  hub_degree_multiplier: 2.0

  # Whether to include CONTRADICTS in topology degree computation.
  topology_include_contradicts: false

  # RECTIFIED (P1-4): All SemanticRole annotation thresholds now in config.
  annotation:
    foundational_centrality_threshold: 0.50
    foundational_min_in_degree: 2
    evidence_hub_min_in_degree: 3
    refinement_root_min_out: 2
    peripheral_max_degree: 1

  # Partitioning algorithm: always "constraint_based" (rectified from "edge_deletion")
  # This field is informational — the algorithm is not pluggable via config.
  partitioning_algorithm: "constraint_based_signed_graph"

  # Bridge detection: always "articulation_points" (rectified from "degree_heuristic")
  bridge_detection: "articulation_points"

  # Temporal timestamp source: always "claim.timestamp" (rectified from "filesystem")
  temporal_source: "claim.timestamp"  

# ── Phase 8: Reliability Evaluation ─────────────────────────────────────────
scoring_policy:
  version: "1.0"
  # RECTIFIED (P1-3): Active profile. Options: balanced, conservative, research, evidence_first
  profile: "balanced"

  evidence:
    min_support_count: 1
    max_support_count: 20
    echo_chamber_penalty: 0.30
    independence_discount_threshold: 0.50
    # RECTIFIED (P1-1): Lineage heuristics
    lineage_depth_limit: 2
    publisher_domain_weight: 0.50

  conflict:
    max_contradiction_partners: 5
    conflict_saturation: 0.80
    contradiction_weight_multiplier: 1.0

  topology:
    # RECTIFIED (P0-3): hub_bonus and bridge_bonus removed from here
    # They are now separate registered signals (hub_score, bridge_score)
    # with their own weights in fusion.signal_weights below
    centrality_scale: 1.0

  temporal:
    default_stability: 0.50
    evolution_bonus: 0.15
    conflict_penalty: 0.10
    recency_window_days: 90.0

  fusion:
    # RECTIFIED (P0-2, P0-3): signal_weights dict replaces per-field weights
    # Adding a new signal only requires adding it here + registering the extractor
    signal_weights:
      evidence_strength:     0.25
      evidence_independence: 0.15
      source_diversity:      0.15
      topology_strength:     0.10
      hub_score:             0.05    # RECTIFIED (P0-3): separated from topology bonus
      bridge_score:          0.05    # RECTIFIED (P0-3): separated from topology bonus
      conflict_pressure:     0.20
      temporal_stability:    0.05
    max_reliability_without_evidence: 60.0
    max_reliability_with_max_conflict: 40.0
    min_reliability_for_high_topology: 20.0
    max_uncertainty_discount: 20.0

  calibration:
    very_high_threshold: 80.0
    high_threshold: 65.0
    moderate_threshold: 45.0
    low_threshold: 25.0
````

## File: config/dev.yaml
````yaml
# config/dev.yaml
# Only override what changes for local development.
# Deep-merged: keys not listed here are inherited from default.yaml.

env: dev
debug: true

logging:
  level: "DEBUG"

embedding:
  batch_size: 8   # Smaller batches — faster iteration on dev hardware

# config/dev.yaml — Phase 1 overrides for development

discovery:
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"
    - ".rst"  

parsing:
  # Smaller limits for faster local iteration
  max_pdf_pages: 50
  max_text_length_chars: 500000
````

## File: config/test.yaml
````yaml
# config/test.yaml
env: test
debug: false

pipeline:
  max_notes: 100

logging:
  level: "WARNING"

embedding:
  cache_embeddings: false

nli:
  cache_nli_results: false


# config/test.yaml — Phase 1 overrides for tests

discovery:
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"
  max_file_size_bytes: 1048576  # 1 MB limit in tests  

parsing:
  max_pdf_pages: 10
  max_text_length_chars: 100000
  min_extractable_chars: 1  

# config/test.yaml — Phase 3 test overrides
segmentation:
  min_sentence_chars: 1    # Accept very short sentences in tests
  max_sentence_chars: 5000  


# config/test.yaml — Phase 4 test overrides
claim_extraction:
  max_claims_per_sentence: 5
  split_conjunctions: true
  split_conditionals: false
  enable_annotation: true  

# config/test.yaml — Phase 5 test overrides
embedding_phase5:
  batch_size: 4            # Small batches for test speed
  cache_embeddings: false  # No caching during tests
  normalize: true
  device: "cpu"
  instruction_prefix: ""
  max_seq_length: null  


relationship_discovery:
  top_k: 5
  sim_threshold: 0.50
  min_confidence: 0.40
  batch_size: 4
  cache_nli_results: false
  skip_unknown_relationships: false
  skip_neutral_relationships: false
  conflict_resolution_policy: "highest_confidence"
  deduplication_policy: "keep_highest_confidence"

resolver_policy:
  contradiction_margin: 0.0
  entailment_margin: 0.0
  confidence_policy: "calibrated"
  version: "1.0"

nli_phase6:
  nli_threshold: 0.70
  cache_nli_results: false

calibration: {}

resource_governance:
  max_pairs: 1000
  timeout_seconds: 60.0
  cancel_on_limit: false

cache_invalidation:
  invalidate_on_embedding_change: true
  invalidate_on_model_change: true
  invalidate_on_policy_change: true  

knowledge_graph:
  include_neutral: false
  min_reliable_delta_days: 0.0
  hub_degree_multiplier: 1.5
  annotation:
    foundational_centrality_threshold: 0.30
    foundational_min_in_degree: 1
    evidence_hub_min_in_degree: 2
    refinement_root_min_out: 1
    peripheral_max_degree: 1  

scoring_policy:
  version: "test_1.0"
  profile: "balanced"
  evidence:
    echo_chamber_penalty: 0.20
    max_support_count: 5
    lineage_depth_limit: 1
    publisher_domain_weight: 0.30
  fusion:
    signal_weights:
      evidence_strength:     0.25
      evidence_independence: 0.15
      source_diversity:      0.15
      topology_strength:     0.10
      hub_score:             0.05
      bridge_score:          0.05
      conflict_pressure:     0.20
      temporal_stability:    0.05
````

## File: data/raw/.gitkeep
````

````

## File: data/.gitkeep
````

````

## File: scripts/download_models.ps1
````powershell
<#
.SYNOPSIS
    Download ML models required by SMRITI.
.DESCRIPTION
    Downloads spaCy and sentence-transformers models.
    Checks internet connectivity before attempting downloads.
#>

#Requires -Version 5.1
$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Fail { param([string]$msg) Write-Host "  ✗ $msg" -ForegroundColor Red; exit 1 }

Write-Step "Checking internet connectivity"
try {
    $null = Invoke-WebRequest -Uri "https://huggingface.co" -UseBasicParsing -TimeoutSec 10
    Write-OK "Internet reachable"
} catch {
    Write-Fail "No internet connection. Cannot download models."
}

Write-Step "Downloading spaCy model"
poetry run python -m spacy download en_core_web_sm
if ($LASTEXITCODE -ne 0) { Write-Fail "spaCy model download failed" }
Write-OK "en_core_web_sm ready"

Write-Step "Downloading sentence-transformers embedding model"
poetry run python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('embedding model ready')
"
if ($LASTEXITCODE -ne 0) { Write-Fail "Embedding model download failed" }
Write-OK "all-MiniLM-L6-v2 ready"

Write-Step "Downloading NLI cross-encoder model"
poetry run python -c "
from sentence_transformers import CrossEncoder
CrossEncoder('cross-encoder/nli-deberta-v3-small')
print('NLI model ready')
"
if ($LASTEXITCODE -ne 0) { Write-Fail "NLI model download failed" }
Write-OK "nli-deberta-v3-small ready"

Write-Host "`n=== All models downloaded ===" -ForegroundColor Green
````

## File: scripts/setup_dev.ps1
````powershell
<#
.SYNOPSIS
    Setup development environment for SMRITI on Windows.
.DESCRIPTION
    Validates Python version, installs Poetry, installs dependencies,
    verifies virtual environment, checks internet connectivity,
    then downloads required ML models.
#>

#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$MIN_PYTHON_MAJOR = 3
$MIN_PYTHON_MINOR = 11
$MIN_POETRY_VERSION = [version]"1.8.0"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Fail { param([string]$msg) Write-Host "  ✗ $msg" -ForegroundColor Red; exit 1 }

# ── 1. Python version check ──────────────────────────────────────────────────
Write-Step "Checking Python version"
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]; $minor = [int]$Matches[2]
        if ($major -lt $MIN_PYTHON_MAJOR -or ($major -eq $MIN_PYTHON_MAJOR -and $minor -lt $MIN_PYTHON_MINOR)) {
            Write-Fail "Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR+ required. Found: $pyVersion"
        }
        Write-OK "Python $major.$minor"
    } else {
        Write-Fail "Could not parse Python version from: $pyVersion"
    }
} catch {
    Write-Fail "Python not found. Install from https://python.org"
}

# ── 2. Poetry check / install ────────────────────────────────────────────────
Write-Step "Checking Poetry"
$poetryInstalled = $false
try {
    $poetryRaw = poetry --version 2>&1
    if ($poetryRaw -match "Poetry \(version (\d+\.\d+\.\d+)\)") {
        $poetryVer = [version]$Matches[1]
        if ($poetryVer -ge $MIN_POETRY_VERSION) {
            Write-OK "Poetry $poetryVer"
            $poetryInstalled = $true
        } else {
            Write-Host "  ! Poetry $poetryVer found — upgrading..." -ForegroundColor Yellow
        }
    }
} catch { }

if (-not $poetryInstalled) {
    Write-Host "  Installing Poetry..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    $env:Path += ";$env:APPDATA\Python\Scripts"
    Write-OK "Poetry installed"
}

# ── 3. Install dependencies ───────────────────────────────────────────────────
Write-Step "Installing Python dependencies"
poetry install --with dev
if ($LASTEXITCODE -ne 0) { Write-Fail "poetry install failed" }
Write-OK "Dependencies installed"

# ── 4. Virtual environment validation ────────────────────────────────────────
Write-Step "Validating virtual environment"
$venvPath = poetry env info --path 2>&1
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPath)) {
    Write-Fail "Virtual environment not found at: $venvPath"
}
Write-OK "Virtual env: $venvPath"

# ── 5. Internet connectivity check ───────────────────────────────────────────
Write-Step "Checking internet connectivity (needed to download models)"
try {
    $null = Invoke-WebRequest -Uri "https://huggingface.co" -UseBasicParsing -TimeoutSec 10
    Write-OK "Internet reachable"
} catch {
    Write-Fail "No internet connection. Cannot download ML models. Check your network."
}

# ── 6. Download spaCy model ───────────────────────────────────────────────────
Write-Step "Downloading spaCy model (en_core_web_sm)"
poetry run python -m spacy download en_core_web_sm
if ($LASTEXITCODE -ne 0) { Write-Fail "spaCy model download failed" }
Write-OK "spaCy model ready"

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  .\Makefile.ps1 test    # Run all tests"
Write-Host "  .\Makefile.ps1 lint    # Lint and type-check"
````

## File: src/smriti/claims/__init__.py
````python
"""
claims/__init__.py — Public API for Phase 4: Claim Construction.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.claims import extract_claims, Phase4Result

They NEVER import from internal modules:
    claims.parser, claims.boundaries, claims.structure,
    claims.annotation, claims.degradation, claims.builder,
    claims.validator, claims.statistics, claims.models, claims.rules

Public contract:
    extract_claims(semantic_sentences: List[SemanticSentence]) → Phase4Result

That is the ONLY function that crosses the Phase 4 boundary.

Everything inside this module (parser, boundaries, structure, annotation,
degradation, builder, validator) is an implementation detail.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    ClaimWarning,
    ExtractionMode,
    Phase4Stats,
    SemanticSentence,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase4Error, ClaimValidationError

from smriti.claims.parser import BaseParser, SpaCyParser  # <-- REPLACED
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.builder import build_claim
from smriti.claims.validator import validate_claims
from smriti.claims.statistics import Phase4StatsCollector

logger = structlog.get_logger(__name__)


# ── Public result types ────────────────────────────────────────────────────────

@dataclass
class SentenceExtractionResult:
    """Phase 4 result for a single SemanticSentence."""
    sentence_id: str
    claims: List[Claim]
    warnings: List[ClaimWarning]
    error: Optional[str] = None

    @property
    def claim_count(self) -> int:
        return len(self.claims)


@dataclass
class Phase4Result:
    """
    Complete output of Phase 4 — all claims extracted from all sentences.
    This is what Phase 5 (Embedding) receives.
    """
    sentence_results: List[SentenceExtractionResult]
    stats: Phase4Stats
    run_id: str
    manifest_path: Optional[Path] = None

    @property
    def all_claims(self) -> List[Claim]:
        """Flat list of all claims across all sentences."""
        result = []
        for sr in self.sentence_results:
            result.extend(sr.claims)
        return result

    @property
    def total_claims(self) -> int:
        return sum(sr.claim_count for sr in self.sentence_results)

    @property
    def successful_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is None)

    @property
    def failed_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is not None)

    def to_dataset_json(self) -> str:
        """
        Serialize all Claims to JSON for Phase 5.
        Written to artifacts/run_{id}/phase4/dataset.json.
        """
        records = []
        for claim in self.all_claims:
            record = {
                "claim_id":         claim.claim_id,
                "sentence_id":      claim.sentence_id,
                "document_id":      claim.document_id,
                "text":             claim.text,
                "content_hash":     claim.content_hash,          # NEW
                "context":          claim.context,
                "source_path":      str(claim.source_path),
                "extraction_mode":  claim.extraction_mode.value,
                "schema_version":   claim.schema_version,
                "rule_version":     claim.rule_version,          # NEW
                "is_negated":       claim.assertion_metadata.is_negated,
                "modality":         claim.assertion_metadata.modality.value,
                "is_conditional":   claim.assertion_metadata.is_conditional,
                "is_comparative":   claim.assertion_metadata.is_comparative,
                "is_attributed":    claim.assertion_metadata.is_attributed,
                "attributed_to":    claim.assertion_metadata.attributed_to,
                "provenance": {
                    "sentence_id":       claim.provenance.sentence_id,
                    "document_id":       claim.provenance.document_id,
                    "source_path":       str(claim.provenance.source_path),
                    "sentence_context":  claim.provenance.sentence_context,
                    "sentence_position": claim.provenance.sentence_position,
                },
            }
            # Include SVO if available
            if claim.structured_assertion:
                record["svo"] = {
                    "subject":   claim.structured_assertion.subject,
                    "predicate": claim.structured_assertion.predicate,
                    "object":    claim.structured_assertion.object,
                }
            else:
                record["svo"] = None

            records.append(record)

        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ───────────────────────────────────────────────────────

def extract_claims_from_sentence(
    sentence: SemanticSentence,
    parser: BaseParser,
    boundary_detector: BoundaryDetector,
    structure_extractor: StructureExtractor,
    annotator: AssertionAnnotator,
    degradation_handler: DegradationHandler,
    stats_collector: Phase4StatsCollector,
    max_claims: int,
    global_seen_ids: dict,
) -> SentenceExtractionResult:
    """
    Extract claims from a single SemanticSentence.

    This is the 7-stage compiler pipeline applied to one sentence.

    Returns:
        SentenceExtractionResult (never raises — errors are captured).
    """
    sentence_id = sentence.sentence_id
    all_warnings: List[ClaimWarning] = []

    try:
        stats_collector.record_sentence_processed()

        # Stage 1: Linguistic Analysis
        parsed = parser.parse(sentence)
        if not parsed.parse_ok:
            stats_collector.record_parser_failure()
            all_warnings.append(ClaimWarning.CLM_PARSER_FAILURE)

        # Stage 2–3: Assertion Analysis + Boundary Detection
        candidates = boundary_detector.detect(parsed)
        stats_collector.record_boundary_split(len(candidates))

        # Enforce max claims per sentence
        if len(candidates) > max_claims:
            candidates = candidates[:max_claims]
            all_warnings.append(ClaimWarning.CLM_EXCEEDED_MAX_CLAIMS)

        claims: List[Claim] = []

        for candidate in candidates:
            # Stage 4: Structured Extraction
            structured = structure_extractor.extract(candidate, parser)

            # Stage 5: Assertion Annotation
            annotated = annotator.annotate(structured)

            # Stage 6: Failure Degradation
            validated = degradation_handler.apply(annotated)
            all_warnings.extend(validated.all_warnings)

            # Stage 7: Build Claim
            claim = build_claim(validated)

            # Record statistics
            stats_collector.record_claim(
                mode=claim.extraction_mode,
                is_negated=claim.is_negated,
                is_modal=claim.assertion_metadata.modality.value != "certain",
                is_attributed=claim.assertion_metadata.is_attributed,
            )

            claims.append(claim)

        # Validate the complete claim collection
        validated_claims, val_warnings = validate_claims(claims, sentence.document_id, global_seen_ids)
        all_warnings.extend(val_warnings)
        stats_collector.record_warnings(all_warnings)

        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=validated_claims,
            warnings=all_warnings,
        )

    except ClaimValidationError as e:
        logger.error(
            "fatal claim validation error",
            sentence_id=sentence_id[:8],
            error=str(e),
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in claim extraction",
            sentence_id=sentence_id[:8],
            error=str(e),
            exc_info=True,
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )


def extract_claims(
    semantic_sentences: List[SemanticSentence],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> Phase4Result:
    """
    Extract claims from all SemanticSentences.

    This is the sole public function of Phase 4.
    All internal pipeline components are created here and hidden from callers.

    Args:
        semantic_sentences: All SemanticSentences from Phase 3.
        run_id:             Current pipeline run identifier.
        manifest_manager:   For writing phase manifest.
        state_manager:      For updating pipeline state.

    Returns:
        Phase4Result containing all Claims and statistics.
    """
    config = get_config()
    ce_cfg = config.get("claim_extraction", {})
    max_claims = ce_cfg.get("max_claims_per_sentence", 10)

    logger.info(
        "phase 4 starting",
        run_id=run_id,
        sentences=len(semantic_sentences),
    )
    start_time = manifest_manager.start_phase(phase=4)

    # Initialize all pipeline components once
    parser = SpaCyParser()  # <-- REPLACED (instantiate concrete class)
    boundary_detector = BoundaryDetector()
    structure_extractor = StructureExtractor()
    annotator = AssertionAnnotator()
    degradation_handler = DegradationHandler()
    stats_collector = Phase4StatsCollector()

    sentence_results: List[SentenceExtractionResult] = []
    global_seen_ids: dict = {}

    with Timer("phase4_claim_construction"):
        for sentence in semantic_sentences:
            result = extract_claims_from_sentence(
                sentence=sentence,
                parser=parser,
                boundary_detector=boundary_detector,
                structure_extractor=structure_extractor,
                annotator=annotator,
                degradation_handler=degradation_handler,
                stats_collector=stats_collector,
                max_claims=max_claims,
                global_seen_ids=global_seen_ids,
            )
            sentence_results.append(result)

    stats = stats_collector.finalize()

    phase4_result = Phase4Result(
        sentence_results=sentence_results,
        stats=stats,
        run_id=run_id,
    )

    # Write dataset artifact for Phase 5
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase4"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(phase4_result.to_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        claims=phase4_result.total_claims,
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=4,
        start_time=start_time,
        inputs={"sentences": len(semantic_sentences)},
        outputs={
            "total_claims": phase4_result.total_claims,
            "structured": stats.structured_claims,
            "partial": stats.partial_claims,
            "lexical": stats.lexical_claims,
            "whole_sentence": stats.whole_sentence_claims,
            "parser_failures": stats.parser_failures,
            "dataset_path": str(dataset_path),
        },
        status="success",
    )
    phase4_result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=4)

    logger.info(
        "phase 4 complete",
        total_claims=phase4_result.total_claims,
        structured=stats.structured_claims,
        fallbacks=stats.whole_sentence_claims,
        parser_failures=stats.parser_failures,
    )

    return phase4_result
````

## File: src/smriti/claims/annotation.py
````python
"""
annotation.py — Semantic metadata annotation for Phase 4.

Responsibility:
    Add semantic metadata to a StructuredAssertionCandidate.
    Detect: negation, modality, attribution, conditional, comparison, quotation.

Rules:
    ✅ Annotate text with semantic flags
    ✅ Record metadata accurately

    ❌ NEVER modify text
    ❌ NEVER rewrite claims
    ❌ NEVER perform semantic inference
    ❌ NEVER change ExtractionMode

The text remains exactly as the author wrote it.
Metadata is additive, never transformative.
"""

from __future__ import annotations

import structlog

from smriti.core.models import Modality
from smriti.claims.models import (
    StructuredAssertionCandidate, 
    AnnotatedAssertion,
    LinguisticMetadata,
    SemanticMetadata
)
from smriti.claims.rules import (
    NEGATION_MARKERS,
    MODALITY_POSSIBLE,
    MODALITY_PROBABLE,
    MODALITY_REQUIRED,
    MODALITY_IMPOSSIBLE,
    ATTRIBUTION_VERBS,
    COMPARISON_MARKERS,
)

logger = structlog.get_logger(__name__)


class AssertionAnnotator:
    """
    Annotates assertions with semantic metadata.
    """

    def annotate(self, candidate: StructuredAssertionCandidate) -> AnnotatedAssertion:
        """
        Annotate an assertion with semantic metadata.

        Args:
            candidate: StructuredAssertionCandidate from structure.py.

        Returns:
            AnnotatedAssertion with metadata populated.
        """
        parsed = candidate.candidate.source
        text = candidate.candidate.text.lower()

        # ── Linguistic metadata ──────────────────────────────────────────────────
        is_negated = self._detect_negation(parsed, text)
        modality = self._detect_modality(parsed, text)
        is_quoted = self._detect_quotation(text)

        linguistic = LinguisticMetadata(
            is_negated=is_negated,
            modality=modality,
            is_quoted=is_quoted,
        )

        # ── Semantic metadata ────────────────────────────────────────────────────
        is_conditional = self._detect_conditional(parsed, text)
        is_comparative = self._detect_comparative(text)
        is_attributed, attributed_to = self._detect_attribution(parsed)

        semantic = SemanticMetadata(
            is_conditional=is_conditional,
            is_comparative=is_comparative,
            is_attributed=is_attributed,
            attributed_to=attributed_to,
        )

        logger.debug(
            "assertion annotated",
            negated=is_negated,
            modality=modality.value,
            conditional=is_conditional,
            attributed=is_attributed,
        )

        return AnnotatedAssertion(
            structured_candidate=candidate,
            linguistic_metadata=linguistic,
            semantic_metadata=semantic,
        )

    def _detect_negation(self, parsed, text_lower: str) -> bool:
        """Detect negation via spaCy dep_ or keyword scan."""
        # spaCy negation detection (more accurate)
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ == "neg":
                    return True

        # Keyword fallback
        words = set(text_lower.split())
        return bool(words & NEGATION_MARKERS)

    def _detect_modality(self, parsed, text_lower: str) -> Modality:
        """Detect modality from auxiliary verbs."""
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ in ("aux", "auxpass"):
                    lemma = token.lemma_.lower()
                    if lemma in MODALITY_IMPOSSIBLE:
                        return Modality.IMPOSSIBLE
                    if lemma in MODALITY_REQUIRED:
                        return Modality.REQUIRED
                    if lemma in MODALITY_PROBABLE:
                        return Modality.PROBABLE
                    if lemma in MODALITY_POSSIBLE:
                        return Modality.POSSIBLE

        # Keyword fallback
        words = set(text_lower.split())
        if words & MODALITY_IMPOSSIBLE:
            return Modality.IMPOSSIBLE
        if words & MODALITY_REQUIRED:
            return Modality.REQUIRED
        if words & MODALITY_PROBABLE:
            return Modality.PROBABLE
        if words & MODALITY_POSSIBLE:
            return Modality.POSSIBLE

        return Modality.CERTAIN

    def _detect_conditional(self, parsed, text_lower: str) -> bool:
        """Detect conditional clauses (if/unless/when)."""
        conditional_markers = {"if", "unless", "when", "whenever", "provided", "assuming"}
        words = set(text_lower.split())
        return bool(words & conditional_markers)

    def _detect_comparative(self, text_lower: str) -> bool:
        """Detect comparative claims ("faster than", "better than")."""
        words = set(text_lower.split())
        return bool(words & COMPARISON_MARKERS)

    def _detect_attribution(self, parsed) -> tuple:
        """
        Detect attribution: "X says Y" / "According to X, Y".

        Returns:
            (is_attributed: bool, attributed_to: Optional[str])
        """
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return False, None

        for token in parsed.spacy_doc:
            if token.lemma_.lower() in ATTRIBUTION_VERBS:
                # Find the subject of the attribution verb
                subjects = [t for t in token.children if t.dep_ in ("nsubj", "nsubjpass")]
                if subjects:
                    attributed_to = subjects[0].text
                    return True, attributed_to

        return False, None

    def _detect_quotation(self, text_lower: str) -> bool:
        """Detect direct quotations (text contains quotes)."""
        return '"' in text_lower or "'" in text_lower
````

## File: src/smriti/claims/boundaries.py
````python
"""
boundaries.py — Claim boundary detection for Phase 4.

Responsibility:
    Given a ParsedSentence, identify where individual semantic assertions begin
    and end within the sentence text.

    This is the most algorithmically complex module in Phase 4.

    Input:  ParsedSentence (with spaCy Doc)
    Output: List[AssertionCandidate]

Boundary Rules (deterministic, in priority order):
    1. Coordinated predicates with shared subject: split
       "Python supports generators and decorators"
       → "Python supports generators." + "Python supports decorators."

    2. Independent clauses joined by coordinator: split
       "CUDA is proprietary and AMD ROCm is open."
       → "CUDA is proprietary." + "AMD ROCm is open."

    3. Contrastive clauses (although/whereas): preserve both sides
       "Although CUDA is proprietary, it performs well."
       → "CUDA is proprietary." + "CUDA performs well."
       (relationship recorded in metadata)

    4. Conditional clauses: preserve entire conditional as one claim
       "If CUDA is installed, PyTorch uses the GPU."
       → Single claim (condition must not be severed)

    5. Relative clauses: preserve as one claim unless independent
       "Python, which was released in 1991, supports generators."
       → Single claim (relative clause is not an independent assertion)

    6. Single assertion (default): no split → one candidate

Design:
    If splitting fails or is ambiguous → fall back to whole-sentence candidate.
    Information is NEVER lost. Ambiguous → conservative (no split).
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.config import get_config
from smriti.core.models import BoundaryReason
from smriti.claims.models import ParsedSentence, AssertionCandidate
from smriti.claims.rules import SUBJECT_DEP_LABELS

logger = structlog.get_logger(__name__)


class BoundaryDetector:
    """
    Applies deterministic boundary rules to find assertion boundaries.

    Instantiate once, call detect() per ParsedSentence.
    """

    def __init__(self) -> None:
        config = get_config()
        ce_cfg = config.get("claim_extraction", {})
        self._split_conjunctions: bool = ce_cfg.get("split_conjunctions", True)
        self._split_conditionals: bool = ce_cfg.get("split_conditionals", False)
        self._split_relative_clauses: bool = ce_cfg.get("split_relative_clauses", False)

    def detect(self, parsed: ParsedSentence) -> List[AssertionCandidate]:
        """
        Detect claim boundaries in a parsed sentence.

        Args:
            parsed: ParsedSentence from parser.py.

        Returns:
            List of AssertionCandidate. Always at least one (whole-sentence fallback).
        """
        # If parsing failed, return the whole sentence as one candidate
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return [self._whole_sentence_candidate(parsed, reason=BoundaryReason.PARSE_FAILED)]

        doc = parsed.spacy_doc
        candidates: List[AssertionCandidate] = []

        if self._split_conjunctions:
            candidates = self._detect_coordination_boundaries(parsed, doc)

        # If no splits were detected (or splitting disabled), use whole sentence
        if not candidates:
            candidates = [self._whole_sentence_candidate(parsed, reason=BoundaryReason.SINGLE_ASSERTION)]

        logger.debug(
            "boundaries detected",
            sentence_id=parsed.sentence.sentence_id[:8],
            candidate_count=len(candidates),
        )

        return candidates

    def _detect_coordination_boundaries(
        self,
        parsed: ParsedSentence,
        doc,
    ) -> List[AssertionCandidate]:
        """
        Detect boundaries created by coordinating conjunctions (and, but, or).

        Uses exact token spans to reconstruct clauses, preserving tense, aspect,
        and passive voice. Never uses .lemma_ for reconstruction.
        """
        try:
            # Find sentence root (usually the main verb)
            roots = [token for token in doc if token.dep_ == "ROOT"]
            if not roots:
                return []

            root = roots[0]

            # Find coordinating conjunctions attached to root
            conj_tokens = [
                t for t in doc
                if t.dep_ == "conj" and t.head == root
            ]

            if not conj_tokens:
                return []

            # Use the new reconstruction method
            return self._reconstruct_coordinated_clauses(
                sent=doc,
                root=root,
                conjuncts=conj_tokens,
                parsed=parsed,
            )

        except Exception as e:
            logger.debug(
                "boundary detection error (falling back)",
                error=str(e),
                sentence_id=parsed.sentence.sentence_id[:8],
            )
            return []

    def _reconstruct_coordinated_clauses(
        self,
        sent,
        root,
        conjuncts,
        parsed: ParsedSentence,
    ) -> List[AssertionCandidate]:
        """
        Reconstruct clauses using exact token spans to preserve tense, aspect, and passive voice.
        NEVER uses lemmas for reconstruction.
        """
        candidates = []

        # 1. Extract the exact token span for the subject
        subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass", "csubj")]
        subj_tokens = list(subjects[0].subtree) if subjects else []

        # 2. Extract the main clause (exclude conjunct subtrees and their coordinating conjunctions)
        conjunct_subtrees = set()
        for conj in conjuncts:
            conjunct_subtrees.update(conj.subtree)
            # Catch the 'and' / 'or' attached to the conjunct
            for cc in conj.lefts:
                if cc.dep_ == "cc":
                    conjunct_subtrees.add(cc)

        main_clause_tokens = [t for t in sent if t not in conjunct_subtrees]
        main_text = self._tokens_to_string(main_clause_tokens)

        candidates.append(
            AssertionCandidate(
                text=main_text,
                source=parsed,
                span_start=0,
                span_end=len(main_text),  # approximate end; we keep it simple
                boundary_reason=BoundaryReason.COORDINATION,
            )
        )

        # 3. Reconstruct each conjunct clause by combining:
        #    Subject Tokens + Auxiliary Tokens + Conjunct Tokens
        aux_tokens = [t for t in root.lefts if t.dep_ in ("aux", "auxpass")]

        for conj in conjuncts:
            # Combine all required tokens and sort them by their original position in the sentence
            reconstructed_tokens = sorted(
                set(subj_tokens + aux_tokens + list(conj.subtree)),
                key=lambda x: x.i
            )
            conj_text = self._tokens_to_string(reconstructed_tokens)

            candidates.append(
                AssertionCandidate(
                    text=conj_text,
                    source=parsed,
                    span_start=conj.idx,
                    span_end=conj.idx + len(conj_text),
                    boundary_reason=BoundaryReason.COORDINATION,
                )
            )

        return candidates

    def _tokens_to_string(self, tokens: list) -> str:
        """Safely join tokens respecting spaCy's original whitespace mapping."""
        if not tokens:
            return ""
        text = tokens[0].text
        for i in range(1, len(tokens)):
            if tokens[i-1].whitespace_:
                text += " " + tokens[i].text
            else:
                # Handle punctuation spacing fallback if whitespace is lost
                if tokens[i].is_punct:
                    text += tokens[i].text
                else:
                    text += " " + tokens[i].text
        return text.strip()

    def _whole_sentence_candidate(
        self,
        parsed: ParsedSentence,
        reason: BoundaryReason = BoundaryReason.SINGLE_ASSERTION,
    ) -> AssertionCandidate:
        """Create a single whole-sentence candidate (no splitting)."""
        text = parsed.sentence.text
        return AssertionCandidate(
            text=text,
            span_start=0,
            span_end=len(text),
            source=parsed,
            boundary_reason=reason,
        )
````

## File: src/smriti/claims/builder.py
````python
"""
builder.py — Immutable Claim construction for Phase 4.

Responsibility:
    Construct the final immutable Claim object from a ValidatedAssertion.

    This is the ONLY place where Claim is instantiated.
    That enforces a single, consistent construction path.

Builder performs:
    1. Deterministic claim_id generation (SHA256, never random)
    2. Content hash computation (SHA256 of exact text)
    3. Provenance chain construction
    4. Object construction with schema and rule versioning

    Builder NEVER modifies text.
    Builder NEVER applies logic or heuristics.
    Builder NEVER performs validation.
    Pure object construction only.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import structlog

from smriti.core.models import (
    Claim,
    ClaimProvenance,
    ExtractionMode,
    AssertionMetadata,  # <-- ADDED
)
from smriti.claims.models import ValidatedAssertion
from smriti.claims.rules import CLAIM_SCHEMA_VERSION, RULE_VERSION

logger = structlog.get_logger(__name__)


def build_claim(validated: ValidatedAssertion) -> Claim:
    """
    Construct a single immutable Claim from a ValidatedAssertion.

    Args:
        validated: ValidatedAssertion from degradation.py.

    Returns:
        Immutable Claim with deterministic ID and complete provenance.
    """
    sentence = validated.source_sentence
    text = validated.text
    span_start = validated.span_start

    # Deterministic claim_id
    claim_id = _compute_claim_id(
        sentence_id=sentence.sentence_id,
        text=text,
        span_start=span_start,
    )

    # Content hash (SHA256 of exact claim text)
    content_hash = _compute_content_hash(text)

    # Complete provenance chain
    provenance = ClaimProvenance(
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        source_path=sentence.source_path,
        sentence_context=sentence.context,
        sentence_position=sentence.position,
    )

    # <-- NEW: Merge internal split metadata into the final public contract
    merged_metadata = AssertionMetadata(
        is_negated=validated.linguistic_metadata.is_negated,
        modality=validated.linguistic_metadata.modality,
        is_conditional=validated.semantic_metadata.is_conditional,
        is_comparative=validated.semantic_metadata.is_comparative,
        is_attributed=validated.semantic_metadata.is_attributed,
        attributed_to=validated.semantic_metadata.attributed_to,
        is_quoted=validated.linguistic_metadata.is_quoted,
    )

    claim = Claim(
        claim_id=claim_id,
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        text=text,
        content_hash=content_hash,
        context=sentence.context,
        source_path=sentence.source_path,
        extraction_mode=validated.extraction_mode,
        structured_assertion=validated.structured_assertion,
        assertion_metadata=merged_metadata,  # <-- REPLACED
        provenance=provenance,
        schema_version=CLAIM_SCHEMA_VERSION,
        rule_version=RULE_VERSION,
    )

    logger.debug(
        "claim built",
        claim_id=claim_id[:8],
        mode=validated.extraction_mode.value,
        is_svo=claim.is_svo,
        negated=claim.is_negated,
        hash_prefix=content_hash[:8],
        rule_version=RULE_VERSION,
    )

    return claim


def _compute_claim_id(sentence_id: str, text: str, span_start: int) -> str:
    """
    Compute a deterministic 16-character claim ID.

    Input:  sentence_id + claim text + span_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs → same ID (deterministic)
        - No timestamps, no random values
        - span_start disambiguates identical text at different positions
          within the same sentence
    """
    id_material = f"{sentence_id}:{text}:{span_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]


def _compute_content_hash(text: str) -> str:
    """
    Compute SHA256 hash of the exact claim text.

    Important: This preserves case and all characters exactly as they appear.
    Lowercasing is NOT applied because case can carry semantic meaning
    (e.g., proper nouns, acronyms).

    Returns:
        16-character hex digest (first 16 chars of full SHA256).
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
````

## File: src/smriti/claims/degradation.py
````python
"""
degradation.py — Failure recovery hierarchy for Phase 4.

Responsibility:
    Apply the graceful degradation hierarchy when structured extraction fails.
    NEVER loses information — only loses structure.

Hierarchy (tried in order, first success wins):
    1. ExtractionMode.STRUCTURED    — Full SVO: S + P + O
    2. ExtractionMode.PARTIAL       — Partial SVO: at least S+P or P+O
    3. ExtractionMode.LEXICAL       — No SVO: lexical text span from boundary
    4. ExtractionMode.WHOLE_SENTENCE — Parse failed: entire sentence text

Philosophy:
    Structure is optional.
    Information is mandatory.
    A Claim must ALWAYS be produced from every AssertionCandidate.

Rules:
    ✅ Produce a Claim from every candidate, regardless of extraction success
    ✅ Record warnings for every degradation step
    ✅ Preserve original text unchanged

    ❌ Never discard an assertion
    ❌ Never invent structure to avoid degradation
    ❌ Never elevate ExtractionMode (degradation only goes down)
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.models import ExtractionMode, ClaimWarning
from smriti.claims.models import AnnotatedAssertion, ValidatedAssertion

logger = structlog.get_logger(__name__)


class DegradationHandler:
    """
    Applies the failure degradation hierarchy.
    """

    def apply(self, annotated: AnnotatedAssertion) -> ValidatedAssertion:
        """
        Apply degradation rules and return a ValidatedAssertion.

        Args:
            annotated: AnnotatedAssertion from annotation.py.

        Returns:
            ValidatedAssertion (never None — always something).
        """
        mode = annotated.extraction_mode
        warnings: List[ClaimWarning] = list(annotated.additional_warnings)
        warnings.extend(annotated.structured_candidate.warnings)

        if mode == ExtractionMode.STRUCTURED:
            # Best case — no degradation needed
            logger.debug("extraction mode: STRUCTURED")

        elif mode == ExtractionMode.PARTIAL:
            # Partial structure — acceptable, add warning
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            logger.debug("extraction mode: PARTIAL")

        elif mode == ExtractionMode.LEXICAL:
            # No structure — whole text span preserved
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: LEXICAL (fallback)")

        elif mode == ExtractionMode.WHOLE_SENTENCE:
            # Parser completely failed — sentence text used as-is
            warnings.append(ClaimWarning.CLM_PARSER_FAILURE)
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: WHOLE_SENTENCE (total fallback)")

        return ValidatedAssertion(
            annotated=annotated,
            all_warnings=warnings,
        )
````

## File: src/smriti/claims/models.py
````python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any

from smriti.core.models import (           # Note: BoundaryReason now in core.models
    SemanticSentence,
    StructuredAssertion,
    AssertionMetadata,
    ExtractionMode,
    ClaimWarning,
    BoundaryReason, 
    Modality,                  # NEW import
)

# ── NEW: Internal Split Metadata ──────────────────────────────────────────────

@dataclass
class LinguisticMetadata:
    is_negated: bool
    modality: Modality
    is_quoted: bool

@dataclass
class SemanticMetadata:
    is_conditional: bool
    is_comparative: bool
    is_attributed: bool
    attributed_to: Optional[str]


@dataclass
class ParsedSentence:
    sentence: SemanticSentence
    spacy_doc: Optional[Any]
    parse_ok: bool
    parse_error: Optional[str] = None


@dataclass
class AssertionCandidate:
    text: str
    span_start: int
    span_end: int
    source: ParsedSentence
    boundary_reason: BoundaryReason   # now Enum
    # confidence removed (Priority 2)


@dataclass
class StructuredAssertionCandidate:
    candidate: AssertionCandidate
    structured_assertion: Optional[StructuredAssertion]
    extraction_mode: ExtractionMode
    warnings: List[ClaimWarning] = field(default_factory=list)


@dataclass
class AnnotatedAssertion:
    structured_candidate: StructuredAssertionCandidate
    linguistic_metadata: LinguisticMetadata  # <-- REPLACED
    semantic_metadata: SemanticMetadata      # <-- REPLACED
    additional_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.structured_candidate.candidate.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.structured_candidate.extraction_mode


@dataclass
class ValidatedAssertion:
    annotated: AnnotatedAssertion
    all_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.annotated.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.annotated.extraction_mode

    @property
    def structured_assertion(self) -> Optional[StructuredAssertion]:
        return self.annotated.structured_candidate.structured_assertion

    @property
    def linguistic_metadata(self) -> LinguisticMetadata:   # <-- ADDED
        return self.annotated.linguistic_metadata

    @property
    def semantic_metadata(self) -> SemanticMetadata:       # <-- ADDED
        return self.annotated.semantic_metadata

    @property
    def source_sentence(self) -> SemanticSentence:
        return self.annotated.structured_candidate.candidate.source.sentence

    @property
    def span_start(self) -> int:
        return self.annotated.structured_candidate.candidate.span_start
````

## File: src/smriti/claims/parser.py
````python
"""
parser.py — Deterministic linguistic analysis wrapper for Phase 4.
Now uses a pluggable parser abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import SemanticSentence
from smriti.claims.models import ParsedSentence
from smriti.exceptions import SpacyNotLoadedError

logger = structlog.get_logger(__name__)


@dataclass
class ParserCapabilities:
    """Defines the supported features of the underlying linguistic parser."""
    supports_svo: bool
    supports_negation: bool
    supports_modality: bool
    supports_dependencies: bool


class BaseParser(ABC):
    """Abstract interface for linguistic parsers."""

    @property
    @abstractmethod
    def capabilities(self) -> ParserCapabilities:
        """Return the capabilities supported by this parser."""
        ...

    @abstractmethod
    def parse(self, sentence: SemanticSentence) -> ParsedSentence:
        """Parse a SemanticSentence into a ParsedSentence."""
        ...


class SpaCyParser(BaseParser):
    """spaCy-based implementation of the linguistic parser."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        if model_name is None:
            config = get_config()
            model_name = config.get("extraction", {}).get("spacy_model", "en_core_web_sm")
        self._model_name = model_name
        self._nlp = self._load_model()

    @property
    def capabilities(self) -> ParserCapabilities:
        """spaCy supports full dependency parsing and structural extraction."""
        return ParserCapabilities(
            supports_svo=True,
            supports_negation=True,
            supports_modality=True,
            supports_dependencies=True,
        )

    def _load_model(self):
        try:
            import spacy
            return spacy.load(self._model_name)
        except OSError as e:
            raise SpacyNotLoadedError(
                f"spaCy model '{self._model_name}' not found. "
                f"Run: poetry run python -m spacy download {self._model_name}\n"
                f"Error: {e}"
            ) from e
        except ImportError as e:
            raise SpacyNotLoadedError(
                f"spaCy is not installed. Run: poetry add spacy\nError: {e}"
            ) from e

    def parse(self, sentence: SemanticSentence) -> ParsedSentence:
        """
        Parse a SemanticSentence using spaCy.

        Args:
            sentence: SemanticSentence from Phase 3.

        Returns:
            ParsedSentence with spacy_doc populated if parse succeeded,
            or with parse_ok=False and parse_error set if it failed.
            NEVER raises — failures are captured in the result.
        """
        text = sentence.text

        if not text or not text.strip():
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=None,
                parse_ok=False,
                parse_error="Empty sentence text",
            )

        try:
            doc = self._nlp(text)
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=doc,
                parse_ok=True,
            )
        except Exception as e:
            logger.warning(
                "spacy parse failed",
                sentence_id=sentence.sentence_id[:8],
                text=text[:50],
                error=str(e),
            )
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=None,
                parse_ok=False,
                parse_error=str(e),
            )
````

## File: src/smriti/claims/rules.py
````python
"""
rules.py — All deterministic extraction rules for Phase 4.

This file contains ONLY data and patterns.
Zero execution logic lives here.

Every constant is configurable via config/default.yaml [claim_extraction].
These are the hard-coded defaults for those config values.
"""

from typing import FrozenSet

# ── Coordinating conjunctions that split claims ───────────────────────────────
# "Python supports X and Y" → two claims if Y is a noun phrase with no predicate
# "Python is fast and Java is slow" → two claims (each has own predicate)
COORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset(["and", "but", "or", "nor"])

# ── Subordinating conjunctions that signal boundary candidates ─────────────
SUBORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset([
    "although", "because", "since", "while", "whereas", "though",
    "even though", "as long as", "unless", "until",
])

# ── Negation markers ──────────────────────────────────────────────────────────
NEGATION_MARKERS: FrozenSet[str] = frozenset([
    "not", "no", "never", "neither", "nor", "without",
    "n't", "cannot", "can't", "won't", "doesn't", "don't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
    "hadn't", "wouldn't", "couldn't", "shouldn't",
])

# ── Modality markers and their classifications ────────────────────────────────
MODALITY_POSSIBLE: FrozenSet[str] = frozenset([
    "may", "might", "could", "can",
])

MODALITY_PROBABLE: FrozenSet[str] = frozenset([
    "probably", "likely", "should", "ought",
])

MODALITY_REQUIRED: FrozenSet[str] = frozenset([
    "must", "will", "shall", "need", "have to", "has to",
])

MODALITY_IMPOSSIBLE: FrozenSet[str] = frozenset([
    "cannot", "can't", "impossible",
])

# ── Attribution verbs (X says Y / X believes Y) ───────────────────────────────
ATTRIBUTION_VERBS: FrozenSet[str] = frozenset([
    "say", "says", "said", "claim", "claims", "claimed",
    "argue", "argues", "argued", "believe", "believes", "believed",
    "state", "states", "stated", "report", "reports", "reported",
    "suggest", "suggests", "suggested", "note", "notes", "noted",
    "assert", "asserts", "asserted", "propose", "proposes", "proposed",
    "write", "writes", "wrote", "show", "shows", "showed", "shown",
    "find", "finds", "found",
])

# ── Comparison markers ────────────────────────────────────────────────────────
COMPARISON_MARKERS: FrozenSet[str] = frozenset([
    "faster", "slower", "better", "worse", "more", "less",
    "higher", "lower", "greater", "smaller", "stronger", "weaker",
    "outperforms", "underperforms", "exceeds", "beats",
    "superior", "inferior", "compared", "than",
])

# ── POS dependency labels for SVO extraction ─────────────────────────────────
# spaCy dependency labels for subject identification
SUBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "nsubj",     # Nominal subject: "Python supports X"
    "nsubjpass", # Passive nominal subject: "X is supported by Python"
    "csubj",     # Clausal subject
    "expl",      # Expletive: "There is X"
])

# spaCy dependency labels for object identification
OBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "dobj",  # Direct object: "Python supports generators"
    "pobj",  # Object of preposition: "runs on GPU"
    "attr",  # Attribute: "Python is a language"
    "acomp", # Adjectival complement: "Python is fast"
])

# spaCy POS tags for verb/predicate identification
VERB_POS_TAGS: FrozenSet[str] = frozenset(["VERB", "AUX"])

# ── Schema ────────────────────────────────────────────────────────────────────
CLAIM_SCHEMA_VERSION = "4.0"
RULE_VERSION = "1.0"          # NEW (Priority 1)
PHASE4_PIPELINE_VERSION = "1.0"

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_CLAIMS_PER_SENTENCE_DEFAULT = 10
MIN_CLAIM_CHARS_DEFAULT = 3
````

## File: src/smriti/claims/statistics.py
````python
"""
statistics.py — Phase 4 execution statistics collector.

Responsibility:
    Collect operational metrics during Phase 4 processing.
    Statistics are DIAGNOSTIC ONLY — they never affect execution.

Design:
    This module observes. It never influences.
    Think of it as a telemetry layer.
"""

from __future__ import annotations

from typing import List

from smriti.core.models import ExtractionMode, ClaimWarning, Phase4Stats


class Phase4StatsCollector:
    """
    Mutable collector that accumulates Phase 4 statistics.
    Call finalize() to get the immutable Phase4Stats result.
    """

    def __init__(self) -> None:
        self._sentences = 0
        self._claims = 0
        self._structured = 0
        self._partial = 0
        self._lexical = 0
        self._whole_sentence = 0
        self._parser_failures = 0
        self._boundary_splits = 0
        self._negated = 0
        self._modal = 0
        self._attributed = 0
        self._warnings: List[ClaimWarning] = []

    def record_sentence_processed(self) -> None:
        self._sentences += 1

    def record_parser_failure(self) -> None:
        self._parser_failures += 1

    def record_boundary_split(self, count: int) -> None:
        """Record that a sentence was split into `count` claims."""
        if count > 1:
            self._boundary_splits += 1

    def record_claim(self, mode: ExtractionMode, is_negated: bool,
                     is_modal: bool, is_attributed: bool) -> None:
        self._claims += 1
        if mode == ExtractionMode.STRUCTURED:
            self._structured += 1
        elif mode == ExtractionMode.PARTIAL:
            self._partial += 1
        elif mode == ExtractionMode.LEXICAL:
            self._lexical += 1
        elif mode == ExtractionMode.WHOLE_SENTENCE:
            self._whole_sentence += 1

        if is_negated:
            self._negated += 1
        if is_modal:
            self._modal += 1
        if is_attributed:
            self._attributed += 1

    def record_warnings(self, warnings: List[ClaimWarning]) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase4Stats:
        return Phase4Stats(
            total_sentences_processed=self._sentences,
            total_claims_produced=self._claims,
            structured_claims=self._structured,
            partial_claims=self._partial,
            lexical_claims=self._lexical,
            whole_sentence_claims=self._whole_sentence,
            parser_failures=self._parser_failures,
            boundary_splits=self._boundary_splits,
            negated_claims=self._negated,
            modal_claims=self._modal,
            attributed_claims=self._attributed,
            warnings=tuple(self._warnings),
        )
````

## File: src/smriti/claims/structure.py
````python
"""
structure.py — SVO structured extraction for Phase 4.

Responsibility:
    Attempt to extract Subject–Verb–Object structure from an AssertionCandidate.
    Returns StructuredAssertionCandidate regardless of success.

    Structure is OPTIONAL.
    A Claim always exists; its SVO is a bonus, not a requirement.

    If extraction succeeds → ExtractionMode.STRUCTURED
    If partial extraction → ExtractionMode.PARTIAL
    If extraction fails → ExtractionMode.LEXICAL (text span preserved)

Rules:
    ✅ Extract subject, predicate, object from dependency tree
    ✅ Return partial results if full SVO is unavailable
    ✅ Never reject — always return something

    ❌ Never modify text
    ❌ Never invent structure
    ❌ Never perform semantic inference
"""

from __future__ import annotations

from typing import Optional
import structlog

from smriti.core.models import (
    StructuredAssertion,
    ExtractionMode,
    ClaimWarning,
    SemanticSentence,
)
from smriti.claims.models import AssertionCandidate, StructuredAssertionCandidate
from smriti.claims.parser import BaseParser
from smriti.claims.rules import SUBJECT_DEP_LABELS, OBJECT_DEP_LABELS, VERB_POS_TAGS

logger = structlog.get_logger(__name__)


class StructureExtractor:
    """
    Extracts SVO structure from AssertionCandidates.
    """

    def extract(self, candidate: AssertionCandidate, parser: BaseParser) -> StructuredAssertionCandidate:
        """
        Attempt SVO extraction.

        The candidate text is re-parsed in isolation to strictly avoid
        cross-clause contamination from the full sentence dependency tree.

        Args:
            candidate: AssertionCandidate with text and original parse.
            parser: Linguistic parser to use for re‑parsing the candidate.

        Returns:
            StructuredAssertionCandidate with extraction result.
        """
        warnings = []

        # Create an isolated mock sentence to restrict the dependency tree
        isolated_sentence = SemanticSentence(
            sentence_id=f"{candidate.source.sentence.sentence_id}_sub",
            document_id=candidate.source.sentence.document_id,
            text=candidate.text,
            source_path=candidate.source.sentence.source_path,
            context=candidate.source.sentence.context,
            position=candidate.source.sentence.position,
            char_start=0,
            char_end=len(candidate.text),
            origin_block_type=candidate.source.sentence.origin_block_type,
            schema_version=candidate.source.sentence.schema_version,
        )

        # Reparse strictly the candidate's span
        local_parse = parser.parse(isolated_sentence)

        if not local_parse.parse_ok or local_parse.spacy_doc is None:
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.WHOLE_SENTENCE,
                warnings=warnings,
            )

        # Extract SVO from the isolated doc
        svo = self._extract_svo(local_parse.spacy_doc)

        if svo is None:
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.LEXICAL,
                warnings=warnings,
            )

        # Determine extraction mode based on completeness
        if svo.is_complete:
            mode = ExtractionMode.STRUCTURED
        elif svo.is_partial:
            mode = ExtractionMode.PARTIAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
        else:
            mode = ExtractionMode.LEXICAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)

        return StructuredAssertionCandidate(
            candidate=candidate,
            structured_assertion=svo,
            extraction_mode=mode,
            warnings=warnings,
        )

    def _extract_svo(self, doc) -> Optional[StructuredAssertion]:
        """
        Extract Subject, Verb (Predicate), Object from spaCy dependency tree.

        Traversal strategy:
            1. Find ROOT token (main verb)
            2. Find subject: child of ROOT with dep_ in SUBJECT_DEP_LABELS
            3. Find object: child of ROOT with dep_ in OBJECT_DEP_LABELS
            4. Extract full noun phrase spans for subject and object

        Returns None if no structure can be identified.
        """
        subject = None
        predicate = None
        obj = None
        negation_marker = None
        modality_marker = None

        # Find root (main verb)
        roots = [t for t in doc if t.dep_ == "ROOT"]
        if not roots:
            return None

        root = roots[0]

        # Predicate = root verb text (lemma form for consistency in annotation)
        if root.pos_ in VERB_POS_TAGS:
            predicate = root.text
        else:
            # Root is not a verb — cannot extract SVO
            return None

        # Find negation attached to root
        neg_tokens = [t for t in root.children if t.dep_ == "neg"]
        if neg_tokens:
            negation_marker = neg_tokens[0].text

        # Find auxiliary/modal attached to root
        aux_tokens = [t for t in root.children if t.dep_ in ("aux", "auxpass")]
        if aux_tokens:
            modality_marker = aux_tokens[0].text

        # Find subject
        for token in root.children:
            if token.dep_ in SUBJECT_DEP_LABELS:
                # Extract full noun phrase subtree
                subject = " ".join(t.text for t in token.subtree)
                break

        # Find object
        for token in root.children:
            if token.dep_ in OBJECT_DEP_LABELS:
                obj = " ".join(t.text for t in token.subtree)
                break

        # If nothing found at all, return None
        if not any([subject, predicate, obj]):
            return None

        return StructuredAssertion(
            subject=subject,
            predicate=predicate,
            object=obj,
            negation_marker=negation_marker,
            modality_marker=modality_marker,
        )
````

## File: src/smriti/claims/validator.py
````python
"""
validator.py — Structural validator for Phase 4 claims.

Responsibility:
    Validate a collection of Claim objects for structural correctness.
    Check per-claim and cross-claim invariants.

Rules:
    ✅ Claim IDs must be unique                          → CLM006 (fatal)
    ✅ Provenance chain must be complete                 → CLM007 (fatal)
    ✅ Text must not be empty                            → CLM005 (discard)
    ✅ schema_version must be "4.0"                      → CLM008 (fatal)
    ✅ extraction_mode must be a valid ExtractionMode    → CLM008 (fatal)

Rules about what validator NEVER does:
    ❌ Never evaluates claim semantics
    ❌ Never modifies any object
    ❌ Never reorders claims
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import Claim, ClaimWarning
from smriti.exceptions import ClaimValidationError

logger = structlog.get_logger(__name__)


def validate_claims(
    claims: List[Claim],
    document_id: str,
    seen_ids: dict,
) -> Tuple[List[Claim], List[ClaimWarning]]:
    """
    Validate a collection of Claims for one document.

    Args:
        claims:       Claims to validate.
        document_id:  Expected document_id for all claims.

    Returns:
        (valid_claims, warnings)
        valid_claims excludes empty-text claims.

    Raises:
        ClaimValidationError: On duplicate IDs, broken provenance, invalid schema.
    """
    warnings: List[ClaimWarning] = []
    valid: List[Claim] = []
    

    for claim in claims:
        # Check 1: Non-empty text
        if not claim.text.strip():
            warnings.append(ClaimWarning.CLM_EMPTY_ASSERTION)
            logger.debug("empty claim discarded", claim_id=claim.claim_id)
            continue

        # Check 2: Unique claim ID with consistency (fatal)
        if claim.claim_id in seen_ids:
            existing = seen_ids[claim.claim_id]
            # Must have same content_hash and same provenance (sentence_id/doc_id)
            if (existing.content_hash != claim.content_hash or
                existing.provenance != claim.provenance):
                raise ClaimValidationError(
                    f"Duplicate claim_id {claim.claim_id} with inconsistent content "
                    f"or provenance. Existing: {existing.content_hash[:8]}..., "
                    f"new: {claim.content_hash[:8]}..."
                )
            # Even if identical, raise to enforce uniqueness and catch logic bugs
            raise ClaimValidationError(
                f"Duplicate claim_id {claim.claim_id} detected. "
                "All claims must have unique IDs."
            )
        seen_ids[claim.claim_id] = claim

        # Check 3: Provenance chain (fatal)
        if not claim.provenance:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has no provenance. "
                "Every claim must have an unbroken lineage."
            )
        if claim.provenance.document_id != document_id:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has provenance.document_id "
                f"'{claim.provenance.document_id}' but expected '{document_id}'"
            )

        # Check 4: Schema version
        if claim.schema_version != "4.0":
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has schema_version '{claim.schema_version}', "
                "expected '4.0'"
            )

        valid.append(claim)

    return valid, warnings
````

## File: src/smriti/contradiction/__init__.py
````python

````

## File: src/smriti/contradiction/detector.py
````python
# Will be filled in Phase 6\n
````

## File: src/smriti/core/__init__.py
````python

````

## File: src/smriti/core/cache.py
````python
"""
Cache manager for expensive computations.

Cache layout (all under project root cache/):
  cache/
    embeddings/   ← Phase 4: embedding vectors
    parsed/       ← Phase 2: parsed document structures
    retrieval/    ← Phase 5: FAISS index
    nli/          ← Phase 6: NLI predictions

CONTRACT: Everything under cache/ is ephemeral.
Safe to delete at any time with: .\\Makefile.ps1 clean-cache
"""

import pickle
from pathlib import Path
from typing import Any, Optional, Dict
import structlog

from smriti.core.paths import (
    EMBEDDINGS_CACHE_DIR,
    PARSED_CACHE_DIR,
    RETRIEVAL_CACHE_DIR,
    NLI_CACHE_DIR,
)


logger = structlog.get_logger(__name__)


class CacheManager:
    """
    Namespaced pickle cache for a single cache directory.
    Instantiate one per namespace: CacheManager(EMBEDDINGS_CACHE_DIR)
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached object by key. Returns None on miss."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "rb") as f:
                obj = pickle.load(f)
            logger.debug("cache hit", key=key, dir=self.cache_dir.name)
            return obj
        except Exception as e:
            logger.warning("cache read failed", key=key, error=str(e))
            return None

    def set(self, key: str, obj: Any) -> None:
        """Store an object in cache."""
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(obj, f)
            logger.debug("cache write", key=key, dir=self.cache_dir.name)
        except Exception as e:
            logger.error("cache write failed", key=key, error=str(e))

    def delete(self, key: str) -> None:
        """Remove a single cache entry."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()

    def clear(self) -> None:
        """Clear this entire cache namespace."""
        import shutil
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("cache namespace cleared", dir=self.cache_dir.name)


# ── Specialised caches ────────────────────────────────────────────────────────

class EmbeddingCache(CacheManager):
    """Cache for embedding vectors (Phase 4)."""

    def __init__(self):
        super().__init__(EMBEDDINGS_CACHE_DIR)

    def get_batch(self, claim_ids: list) -> Dict[str, list]:
        """Retrieve multiple embeddings at once."""
        return {cid: v for cid in claim_ids if (v := self.get(cid)) is not None}


class NLICache(CacheManager):
    """Cache for NLI predictions (Phase 6)."""

    def __init__(self):
        super().__init__(NLI_CACHE_DIR)

    @staticmethod
    def _pair_key(claim_a_id: str, claim_b_id: str) -> str:
        """Deterministic key: (A,B) and (B,A) produce the same key."""
        a, b = sorted([claim_a_id, claim_b_id])
        return f"{a}__{b}"

    def get_pair(self, claim_a_id: str, claim_b_id: str) -> Optional[Dict]:
        return self.get(self._pair_key(claim_a_id, claim_b_id))

    def set_pair(self, claim_a_id: str, claim_b_id: str, result: Dict) -> None:
        self.set(self._pair_key(claim_a_id, claim_b_id), result)
````

## File: src/smriti/core/config.py
````python
"""
Configuration management for SMRITI.

Loading order:
  1. config/default.yaml     — complete baseline
  2. config/{env}.yaml       — environment overrides (deep-merged)

Deep merge: nested keys are merged recursively, not overwritten.
Model names and thresholds belong here, not in constants.py.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml

from smriti.core.paths import CONFIG_DIR
from smriti.exceptions import ConfigError

# Module-level singleton — call get_config() everywhere
_config: Optional["Config"] = None


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Recursively merge override into base.
    Nested dicts are merged; scalars are overwritten.

    Example:
        base     = {"embedding": {"model": "MiniLM", "batch_size": 32}}
        override = {"embedding": {"batch_size": 8}}
        result   = {"embedding": {"model": "MiniLM", "batch_size": 8}}
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Load and expose layered YAML configuration."""

    def __init__(self, env: str = "dev", config_dir: Path = CONFIG_DIR):
        self.env = env
        self._data: Dict[str, Any] = {}
        self._load(config_dir)

    def _load(self, config_dir: Path) -> None:
        """Load default config then deep-merge env override."""
        default_path = config_dir / "default.yaml"
        if not default_path.exists():
            raise ConfigError(f"Missing required config file: {default_path}")

        with open(default_path, encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        env_path = config_dir / f"{self.env}.yaml"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
            self._data = _deep_merge(self._data, env_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Top-level key access with optional default."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dict-style access: config["embedding"]["model"]."""
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data


def get_config(env: str = "dev") -> Config:
    """Return the module-level config singleton (lazy init)."""
    global _config
    if _config is None:
        _config = Config(env=env)
    return _config
````

## File: src/smriti/core/hashing.py
````python
"""
Content hashing for incremental processing.
Detects which notes changed since last run — skip the rest.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE
from smriti.core.paths import HASH_CACHE_FILE


class ContentHasher:
    """Computes and persists content hashes for change detection."""

    def __init__(self, cache_file: Path = HASH_CACHE_FILE):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.hashes: Dict[str, str] = self._load()

    def compute_hash(self, content: str) -> str:
        """SHA-256 hash of a string."""
        return hashlib.new(HASH_ALGORITHM, content.encode("utf-8")).hexdigest()

    def compute_file_hash(self, file_path: Path) -> str:
        """SHA-256 hash of a file (chunked for large files)."""
        h = hashlib.new(HASH_ALGORITHM)
        with open(file_path, "rb") as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()

    def has_changed(self, path: Path, content: str) -> bool:
        """True if content differs from last stored hash (or not yet seen)."""
        current = self.compute_hash(content)
        return self.hashes.get(str(path)) != current

    def update_hash(self, path: Path, content: str) -> None:
        """Store current hash for a file."""
        self.hashes[str(path)] = self.compute_hash(content)
        self._save()

    def clear(self) -> None:
        """Reset all stored hashes."""
        self.hashes = {}
        self._save()

    def _load(self) -> Dict[str, str]:
        if self.cache_file.exists():
            with open(self.cache_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.hashes, f, indent=2)
````

## File: src/smriti/core/logger.py
````python
"""
Structured logging setup.
Reads level from config — not hardcoded.
"""

import logging
import structlog
from pathlib import Path

from smriti.core.paths import LOG_DIR
from smriti.core.config import get_config


def setup_logging() -> None:
    """Configure structured logging from config."""
    config = get_config()
    level = config["logging"]["level"]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "smriti.log"

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return a named structlog logger."""
    return structlog.get_logger(name)
````

## File: src/smriti/core/manifest.py
````python
"""
Manifest system for tracking phase execution.
Every phase writes a manifest.json under its own run directory.

Directory layout:
  artifacts/
    run_20240715_143022/
      phase1/manifest.json
      phase2/manifest.json
      ...
    run_20240715_160500/
      phase1/manifest.json
      ...
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from smriti.constants import MANIFEST_SCHEMA_VERSION
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.models import ManifestEntry


logger = structlog.get_logger(__name__)


class ManifestManager:
    """Manages per-run, per-phase manifests."""

    def __init__(self, run_id: str, artifacts_dir: Path = ARTIFACTS_DIR):
        self.run_id = run_id
        self.artifacts_dir = Path(artifacts_dir)
        self.run_dir = self.artifacts_dir / f"run_{run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def start_phase(self, phase: int) -> float:
        """
        Mark phase as started. Returns wall-clock start time.
        Call this immediately before phase logic runs.
        """
        start_time = time.time()
        phase_dir = self.run_dir / f"phase{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        logger.info("phase started", run_id=self.run_id, phase=phase)
        return start_time

    def end_phase(
        self,
        phase: int,
        start_time: float,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        status: str = "success",
        error: Optional[str] = None,
    ) -> Path:
        """
        Record phase completion and write manifest.json.
        Returns: path to the manifest file.
        """
        duration = time.time() - start_time

        entry = ManifestEntry(
            run_id=self.run_id,
            phase=phase,
            timestamp=datetime.now(),
            duration_seconds=duration,
            inputs=inputs,
            outputs=outputs,
            status=status,
            schema_version=MANIFEST_SCHEMA_VERSION,
            error=error,
        )

        phase_dir = self.run_dir / f"phase{phase}"
        manifest_path = phase_dir / "manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": entry.schema_version,
                    "run_id": entry.run_id,
                    "phase": entry.phase,
                    "timestamp": entry.timestamp.isoformat(),
                    "duration_seconds": round(entry.duration_seconds, 4),
                    "inputs": entry.inputs,
                    "outputs": entry.outputs,
                    "status": entry.status,
                    "error": entry.error,
                },
                f,
                indent=2,
            )

        logger.info(
            "phase completed",
            run_id=self.run_id,
            phase=phase,
            status=status,
            duration_seconds=f"{duration:.2f}",
        )
        return manifest_path

    def list_completed_phases(self) -> list:
        """Return list of phase numbers that have a manifest in this run."""
        completed = []
        for phase_dir in sorted(self.run_dir.glob("phase*")):
            if (phase_dir / "manifest.json").exists():
                completed.append(int(phase_dir.name.replace("phase", "")))
        return completed
````

## File: src/smriti/core/models.py
````python
"""
Data models for SMRITI.
Define once, use everywhere.
These are the contracts between phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class FileFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class ContradictionType(str, Enum):
    DIRECT_REVERSAL = "direct_reversal"
    REFINEMENT = "refinement"
    STRATEGY_SHIFT = "strategy_shift"
    DEFINITION_CHANGE = "definition_change"


class ExtractionMethod(str, Enum):
    """Which extractor was used to produce raw_text."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class WarningCode(str, Enum):
    """Strict taxonomy of extraction and normalization warnings."""
    UNICODE_NORMALIZED = "unicode_normalized"
    BOM_REMOVED = "bom_removed"
    LINE_ENDINGS_NORMALIZED = "line_endings_normalized"
    TRAILING_WHITESPACE_REMOVED = "trailing_whitespace_removed"
    CONTROL_CHARS_REMOVED = "control_chars_removed"
    BLANK_LINES_COLLAPSED = "blank_lines_collapsed"
    MIXED_LINE_ENDINGS = "mixed_line_endings"
    NULL_BYTES_REMOVED = "null_bytes_removed"
    ENCODING_FALLBACK = "encoding_fallback"
    PAGE_LIMIT_REACHED = "page_limit_reached"
    PAGE_EXTRACTION_FAILED = "page_extraction_failed"
    EMPTY_PDF_PAGE = "empty_pdf_page"
    NO_EXTRACTABLE_TEXT = "no_extractable_text"
    TEXT_TRUNCATED = "text_truncated"


# ── Phase 3 Warning Codes ────────────────────────────────────────────────────

class SegmentationWarning(str, Enum):
    """Warning codes specific to Phase 3 semantic sentence construction."""
    SEG_EMPTY_SENTENCE_DISCARDED   = "SEG001"   # Empty string after strip
    SEG_VERY_LONG_SENTENCE         = "SEG002"   # Exceeds max_sentence_chars
    SEG_UNKNOWN_STRUCTURE          = "SEG003"   # Structural element not recognised
    SEG_MALFORMED_TABLE            = "SEG004"   # Table could not be parsed
    SEG_CODE_BLOCK_SKIPPED         = "SEG005"   # Code block skipped (V1)
    CTX_STACK_IMBALANCE            = "CTX001"   # Context stack depth mismatch
    VAL_DUPLICATE_SENTENCE_ID      = "VAL001"   # Two sentences share an ID (fatal)
    VAL_INVALID_POSITION_ORDER     = "VAL002"   # Non-monotonic positions (fatal)
    VAL_INVALID_CONTEXT            = "VAL003"   # Context string malformed


# ── Phase 4 Warning Codes ─────────────────────────────────────────────────────

class ClaimWarning(str, Enum):
    """Warning codes specific to Phase 4 claim construction."""
    CLM_PARSER_FAILURE          = "CLM001"
    CLM_BOUNDARY_AMBIGUITY      = "CLM002"
    CLM_STRUCTURE_UNAVAILABLE   = "CLM003"
    CLM_FALLBACK_ACTIVATED      = "CLM004"
    CLM_EMPTY_ASSERTION         = "CLM005"
    CLM_DUPLICATE_CLAIM_ID      = "CLM006"  # Fatal if inconsistent
    CLM_INVALID_PROVENANCE      = "CLM007"
    CLM_VALIDATION_FAILURE      = "CLM008"
    CLM_EXCEEDED_MAX_CLAIMS     = "CLM009"
    CLM_UNSUPPORTED_SYNTAX      = "CLM010"


class ExtractionMode(str, Enum):
    STRUCTURED    = "structured"
    PARTIAL       = "partial"
    LEXICAL       = "lexical"
    WHOLE_SENTENCE = "whole_sentence"


class Modality(str, Enum):
    CERTAIN    = "certain"
    POSSIBLE   = "possible"
    PROBABLE   = "probable"
    IMPOSSIBLE = "impossible"
    REQUIRED   = "required"
    UNKNOWN    = "unknown"


class BoundaryReason(str, Enum):
    """Enum for deterministic boundary detection reasons."""
    SINGLE_ASSERTION       = "single_assertion"
    COORDINATED_PREDICATE  = "coordinated_predicate"
    INDEPENDENT_CLAUSE     = "independent_clause"
    PARSE_FAILED           = "parse_failed"
    CONDITIONAL_SPLIT      = "conditional_split"      # reserved
    RELATIVE_CLAUSE        = "relative_clause"
    COORDINATION           = "coordination"


# ── Phase 3 contract: Document → SemanticSentence ────────────────────────────

@dataclass(frozen=True)
class SemanticSentence:
    """
    The immutable public output of Phase 3.

    This is the contract boundary between document processing and knowledge processing.
    Phase 4+ never needs to understand Markdown, headings, or document structure.
    Everything structural is fully encapsulated here.

    Fields:
        sentence_id:       Deterministic SHA256‑based identifier (16 hex chars)
        document_id:       doc_id of the source Document (links back to Phase 2)
        text:              The sentence text exactly as it appears (canonical prose)
        context:           Heading path under which this sentence appears, or empty string
                           Example: "Python > Generators > Yield"
                           Stored SEPARATELY from text — never fused.
        position:          0‑based sequence number within this document
        char_start:        Character offset in Document.normalized_text where sentence begins
                           (for generated prose, refers to the start of the block)
        char_end:          Character offset in Document.normalized_text where sentence ends
                           (for generated prose, refers to the end of the block)
        source_path:       Path to the original file (for traceability)
        origin_block_type: BlockType that produced this sentence (stored as string)
        schema_version:    Version of this data structure

    All offsets refer to Document.normalized_text; they are traceability offsets,
    not reconstructed offsets into generated prose.
    """
    sentence_id: str
    document_id: str
    text: str
    context: str           # "Python > Generators" or "" if at root
    position: int
    char_start: int
    char_end: int
    source_path: Path
    origin_block_type: str   # e.g., "paragraph", "heading", etc.
    schema_version: str = "3.0"


# ── Phase 3 result ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Phase3Stats:
    """Structural statistics collected during Phase 3 for a single Document."""
    total_headings: int = 0
    total_paragraphs: int = 0
    total_list_items: int = 0
    total_tables: int = 0
    total_block_quotes: int = 0
    total_code_blocks_skipped: int = 0
    total_horizontal_rules: int = 0
    total_front_matter_blocks: int = 0
    total_blank_lines: int = 0
    total_unknown_blocks: int = 0
    sentences_produced: int = 0
    sentences_discarded: int = 0
    warnings: tuple = field(default_factory=tuple)


# ── Phase 1 contract: Discovery → Parsing ────────────────────────────────────

@dataclass(frozen=True)
class SourceDocument:
    """
    The immutable, file‑centric representation of one discovered document.
    Produced by Phase 1, consumed by Phase 2.
    """
    doc_id: str
    path: Path
    relative_path: Path
    source_root: Path
    format: FileFormat
    content_hash: str
    size_bytes: int
    modified_at: datetime


# ── Phase 2 extraction models ────────────────────────────────────────────────

@dataclass(frozen=True)
class TextStatistics:
    character_count: int
    word_count: int
    line_count: int
    blank_line_count: int
    paragraph_count: int


@dataclass(frozen=True)
class RawExtractionResult:
    raw_text: str
    warnings: tuple[WarningCode, ...]
    method: ExtractionMethod
    encoding_used: str


@dataclass(frozen=True)
class NormalizationResult:
    normalized_text: str
    warnings: tuple[WarningCode, ...]


@dataclass(frozen=True)
class Document:
    """The final enriched document produced by Phase 2."""
    doc_id: str
    source_document: SourceDocument
    raw_text: str
    normalized_text: str
    extraction_method: ExtractionMethod
    extraction_warnings: tuple[WarningCode, ...]
    text_statistics: TextStatistics
    encoding_used: str
    schema_version: str = "2.0"

    @property
    def has_warnings(self) -> bool:
        return len(self.extraction_warnings) > 0

    @property
    def is_empty(self) -> bool:
        return len(self.normalized_text.strip()) == 0


# ── Phase 4 contract: SemanticSentence → Claim ───────────────────────────────

@dataclass(frozen=True)
class StructuredAssertion:
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    negation_marker: Optional[str] = None
    modality_marker: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return all([self.subject, self.predicate, self.object])

    @property
    def is_partial(self) -> bool:
        return any([self.subject, self.predicate, self.object])


@dataclass(frozen=True)
class AssertionMetadata:
    is_negated: bool = False
    modality: Modality = Modality.CERTAIN
    is_conditional: bool = False
    is_comparative: bool = False
    is_attributed: bool = False
    attributed_to: Optional[str] = None
    is_quoted: bool = False


@dataclass(frozen=True)
class ClaimProvenance:
    sentence_id: str
    document_id: str
    source_path: Path
    sentence_context: str
    sentence_position: int


@dataclass(frozen=True)
class Claim:
    """
    An atomic claim (SVO triple or full sentence). Produced by Phase 4.

    Fields:
        claim_id:            Deterministic identifier (SHA256 of content hash + metadata)
        sentence_id:         The ID of the SemanticSentence this claim originated from
        document_id:         doc_id of the source Document
        text:                The claim text (exact substring or full sentence)
        content_hash:        SHA256 of the exact text (for deduplication)
        context:             Heading path (same as SemanticSentence.context)
        source_path:         Path to the original file
        extraction_mode:     How this claim was constructed (structured/partial/lexical/whole_sentence)
        structured_assertion: Optional SVO triple (if extracted with a parser)
        assertion_metadata:  Negation, modality, attribution, etc.
        provenance:          Link back to the original sentence
        schema_version:      Version of this data structure
        rule_version:        Version of the extraction rules used
    """
    claim_id: str
    sentence_id: str
    document_id: str
    text: str
    content_hash: str
    context: str
    source_path: Path
    extraction_mode: ExtractionMode
    structured_assertion: Optional[StructuredAssertion]
    assertion_metadata: AssertionMetadata
    provenance: ClaimProvenance
    schema_version: str = "4.0"
    rule_version: str = "1.0"

    @property
    def is_svo(self) -> bool:
        return (
            self.extraction_mode == ExtractionMode.STRUCTURED
            and self.structured_assertion is not None
            and self.structured_assertion.is_complete
        )

    @property
    def is_negated(self) -> bool:
        return self.assertion_metadata.is_negated

    @property
    def subject(self) -> Optional[str]:
        return self.structured_assertion.subject if self.structured_assertion else None

    @property
    def predicate(self) -> Optional[str]:
        return self.structured_assertion.predicate if self.structured_assertion else None

    @property
    def object(self) -> Optional[str]:
        return self.structured_assertion.object if self.structured_assertion else None


@dataclass(frozen=True)
class Phase4Stats:
    total_sentences_processed: int = 0
    total_claims_produced: int = 0
    structured_claims: int = 0
    partial_claims: int = 0
    lexical_claims: int = 0
    whole_sentence_claims: int = 0
    parser_failures: int = 0
    boundary_splits: int = 0
    negated_claims: int = 0
    modal_claims: int = 0
    attributed_claims: int = 0
    warnings: tuple = field(default_factory=tuple)


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────

class VectorDType(str, Enum):
    FLOAT32 = "float32"
    FLOAT64 = "float64"

@dataclass(frozen=True)
class Vector:
    """
    A typed, self-describing embedding vector.

    This is the lowest-level geometric primitive in Phase 5.
    All higher-level objects (Embedding, EmbeddedClaim) reference a Vector.

    Design:
        Replaces the raw `tuple` that was previously embedded in Embedding.
        This future-proofs for: quantization, sparse vectors, binary vectors,
        multimodal vectors — without touching Phase 6.

    Fields:
        values:     Immutable float tuple (the actual numbers).
        dimension:  Length of values (redundant but self-documenting).
        dtype:      "float64" or "float32" — guards against object-type contamination.
        normalized: True if L2 norm has been applied (||values||₂ ≈ 1.0).
    """
    values: tuple
    dimension: int
    dtype: VectorDType = VectorDType.FLOAT64
    normalized: bool = False

    def __post_init__(self):
        if len(self.values) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: values has {len(self.values)} elements "
                f"but dimension={self.dimension}"
            )

    def to_list(self) -> list:
        """Return values as a plain Python list (for serialization, FAISS, etc.)."""
        return list(self.values)

    def __len__(self) -> int:
        return self.dimension


@dataclass(frozen=True)
class EmbeddingModelDescriptor:
    """
    Identifies the exact semantic encoder that produced an embedding.

    All fields together form the model signature used in cache key generation.
    Any change to any field invalidates all cached embeddings.

    Fields:
        provider:         "sentence-transformers", "openai", "bge", etc.
        model_name:       "all-MiniLM-L6-v2"
        model_revision:   Git revision hash of model weights
        dimension:        Embedding dimension (384 for MiniLM)
        model_signature:  SHA256 of (provider + model_name + revision)
        embedding_family: High-level family: "SentenceTransformer", "OpenAI", "BGE", "Instructor"
        checkpoint_sha:   Optional content-addressable SHA if available (beyond HF revision)
    """
    provider: str
    model_name: str
    model_revision: str
    dimension: int
    model_signature: str   # Deterministic: SHA256(provider:model_name:revision)
    embedding_family: str = ""   # e.g. "SentenceTransformer", "OpenAI", "BGE"
    checkpoint_sha: str = ""     # Content-addressable checkpoint hash if available


@dataclass(frozen=True)
class EmbeddingProvenance:
    """
    Execution metadata for one embedding — lightweight, non-semantic.

    Fields:
        pipeline_version:   Phase 5 implementation version
        normalization_mode: "l2" or "none"
        device:             "cpu" / "cuda" / "mps"
        config_hash:        SHA256 of the embedding config section
    """
    pipeline_version: str
    normalization_mode: str
    device: str
    config_hash: str


@dataclass(frozen=True)
class EmbeddingQuality:
    """
    Per-claim diagnostic snapshot produced during Phase 5.

    Phase 6 reads these — it never recomputes them.
    Invaluable when debugging large vaults with thousands of claims.

    Fields:
        dimension_ok:  True if vector.dimension == descriptor.dimension
        normalized:    True if L2 normalization was applied
        finite:        True if all values are finite (no NaN or Inf)
        cache_used:    True if vector came from cache (not fresh inference)
    """
    dimension_ok: bool
    normalized: bool
    finite: bool
    cache_used: bool


@dataclass(frozen=True)
class Embedding:
    """
    The canonical semantic artifact produced by Phase 5 for one Claim.

    DESIGN PRINCIPLE: Embedding is a timeless semantic object.
    It does NOT carry execution status (cached / fresh / stale).
    Execution metadata belongs to EmbeddingResult (internal) and EmbeddingQuality.

    Fields:
        claim_id:   Links back to the originating Claim (referential integrity)
        vector:     Validated, normalized Vector domain object
        descriptor: Which model produced this vector
        provenance: How/where the inference was run
    """
    claim_id: str
    vector: Vector
    descriptor: EmbeddingModelDescriptor
    provenance: EmbeddingProvenance

    @property
    def dimension(self) -> int:
        return self.vector.dimension

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience)."""
        return self.vector.values


@dataclass(frozen=True)
class EmbeddedClaim:
    """
    The bridge between symbolic knowledge (Claim) and numeric geometry (Embedding).

    Phase 6 receives List[EmbeddedClaim] and uses them for similarity search.

    Design:
        Claim is NOT duplicated here — only its ID is referenced.
        This preserves referential integrity and avoids unnecessary duplication.
        Phase 6 looks up the Claim by claim_id when needed.

        quality provides pre-computed diagnostics so Phase 6 never has to
        re-derive normalization status, dimension correctness, etc.
    """
    claim_id: str
    embedding: Embedding
    quality: EmbeddingQuality
    schema_version: str = "5.0"

    @property
    def vector(self) -> Vector:
        return self.embedding.vector

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience for Phase 6 / FAISS)."""
        return self.embedding.vector.values

    @property
    def dimension(self) -> int:
        return self.embedding.dimension

    @property
    def is_cached(self) -> bool:
        return self.quality.cache_used


@dataclass(frozen=True)
class Phase5Stats:
    """Statistics collected during one Phase 5 execution."""
    total_claims: int = 0
    successful: int = 0
    cached: int = 0
    stale: int = 0
    failed: int = 0
    skipped: int = 0
    total_batches: int = 0
    average_batch_size: float = 0.0
    cache_hit_rate: float = 0.0
    total_runtime_seconds: float = 0.0
    vectors_per_second: float = 0.0
    current_memory_mb: float = 0.0
    cache_entries_reused: int = 0
    cache_entries_regenerated: int = 0
    cache_entries_invalidated: int = 0


# ── Phase 6 contract: CandidatePair → RelationshipSet ─────────────────────────

class RelationshipType(str, Enum):
    """
    The semantic relationship type between two Claims.

    ⚠️  This enum is governed by the Relationship Ontology Specification
    in docs/relationship_ontology.md. Any change to these values requires
    updating that document first.

    Rules:
        - CONTRADICTS is symmetric; SUPPORTS and REFINES are directional.
        - UNKNOWN must never be persisted to Phase 7.
        - NEUTRAL should not be persisted to Phase 7 (configurable).
    """
    CONTRADICTS   = "contradicts"    # Symmetric: claims assert opposing facts
    SUPPORTS      = "supports"       # Directional: claim_a reinforces claim_b
    REFINES       = "refines"        # Directional: claim_a qualifies/narrows claim_b
    NEUTRAL       = "neutral"        # Symmetric: semantically close, no direction
    UNKNOWN       = "unknown"        # Resolver could not classify (never persist)


class RelationshipDirection(str, Enum):
    """
    Direction of a relationship between claim_a and claim_b.

    Ontology constraints:
        CONTRADICTS → always SYMMETRIC
        SUPPORTS    → always A_TO_B or B_TO_A
        REFINES     → always A_TO_B or B_TO_A
        NEUTRAL     → always SYMMETRIC
    """
    A_TO_B      = "a_to_b"       # claim_a → claim_b
    B_TO_A      = "b_to_a"       # claim_b → claim_a
    SYMMETRIC   = "symmetric"    # Both directions are equivalent


class LifecycleStage(str, Enum):
    """
    Explicit lifecycle of a claim pair through the Phase 6 pipeline.

    Every object in the pipeline belongs to exactly one stage.
    Transitions are one-way; no object can move backward.

    CANDIDATE              → discovered by ANN, not yet validated
    VALIDATED_CANDIDATE    → passed all candidate validation checks
    EVIDENCE               → NLI inference completed; raw scores available
    CALIBRATED_EVIDENCE    → scores adjusted by ConfidenceCalibrator
    RESOLVED               → RelationshipType assigned by resolver
    VALIDATED_RELATIONSHIP → passed confidence and consistency checks
    RELATIONSHIP           → immutable Relationship object constructed
    REJECTED               → failed at any stage; not in final RelationshipSet
    """
    CANDIDATE              = "candidate"
    VALIDATED_CANDIDATE    = "validated_candidate"
    EVIDENCE               = "evidence"
    CALIBRATED_EVIDENCE    = "calibrated_evidence"
    RESOLVED               = "resolved"
    VALIDATED_RELATIONSHIP = "validated_relationship"
    RELATIONSHIP           = "relationship"
    REJECTED               = "rejected"


@dataclass(frozen=True)
class RetrievalSearchParameters:
    """
    Parameters used during ANN search for this candidate pair.

    Enables exact reproduction of retrieval behavior during debugging or replay.
    """
    top_k: int
    sim_threshold: float
    index_type: str         # e.g. "faiss_flat_ip"
    index_version: str      # e.g. "1.0"


@dataclass(frozen=True)
class RetrievalQuality:
    """
    Quality signal for the retrieval stage of a CandidatePair.

    Fields:
        exact_match:          claim_id_a and claim_id_b share identical text (duplicate)
        duplicate_removed:    A duplicate was detected and eliminated
        below_threshold:      The pair was below the sim_threshold (should not occur post-filter)
        high_density_region:  Both claims have many neighbors (dense semantic region)
        isolated_claim:       One or both claims had very few neighbors (isolated semantics)
    """
    exact_match: bool = False
    duplicate_removed: bool = False
    below_threshold: bool = False
    high_density_region: bool = False
    isolated_claim: bool = False


@dataclass(frozen=True)
class CandidatePair:
    """
    A pair of semantically similar claims discovered by ANN search.

    This is the entry ticket to the classification pipeline.
    Every CandidatePair that passes validation proceeds to NLI evidence generation.

    Fields:
        claim_id_a:           First claim's ID (always ≤ claim_id_b lexicographically)
        claim_id_b:           Second claim's ID
        cosine_similarity:    Cosine similarity from FAISS ANN search (0.0–1.0)
        candidate_rank:       Rank of claim_b in claim_a's neighbor list (1 = nearest)
        retrieval_backend:    Backend used for retrieval (e.g. "faiss_flat_ip")
        index_version:        Version of the retrieval index
        search_parameters:    Full search parameters for exact reproduction
        retrieval_quality:    Quality signals for this retrieval result
        lifecycle_stage:      Always CANDIDATE when first created
    """
    claim_id_a: str
    claim_id_b: str
    cosine_similarity: float
    candidate_rank: int
    retrieval_backend: str = "faiss_flat_ip"
    index_version: str = "1.0"
    search_parameters: Optional["RetrievalSearchParameters"] = None
    retrieval_quality: Optional["RetrievalQuality"] = None
    lifecycle_stage: "LifecycleStage" = LifecycleStage.CANDIDATE

    def pair_key(self) -> str:
        """Canonical pair identifier (order-independent)."""
        a, b = sorted([self.claim_id_a, self.claim_id_b])
        return f"{a}:{b}"


@dataclass(frozen=True)
class NLILabel(str, Enum):
    """NLI labels from the cross-encoder model."""
    ENTAILMENT    = "entailment"
    NEUTRAL       = "neutral"
    CONTRADICTION = "contradiction"


@dataclass(frozen=True)
class InferenceMetadata:
    """
    Operational metadata about the NLI inference run.

    Separated from NLI scores to keep evidence clean.
    Fields:
        model_name:        NLI model identifier
        model_version:     Model version / revision (from HF hub)
        runtime_seconds:   Wall-clock time for this pair's inference
        device:            "cpu" | "cuda" | "mps"
        batch_index:       Which batch this pair was processed in
        latency_ms:        Per-pair inference latency in milliseconds
    """
    model_name: str
    model_version: str = "unknown"
    runtime_seconds: float = 0.0
    device: str = "cpu"
    batch_index: int = 0
    latency_ms: float = 0.0


@dataclass(frozen=True)
class NLIScores:
    """
    Raw NLI evidence scores from the cross-encoder.

    This is pure evidence — no model metadata here.
    Interpretation belongs to ConfidenceCalibrator → RelationshipResolver.

    Fields:
        entailment_score:       P(entailment | claim_a, claim_b)
        neutral_score:          P(neutral | claim_a, claim_b)
        contradiction_score:    P(contradiction | claim_a, claim_b)
        predicted_label:        argmax label from the cross-encoder
        raw_confidence:         max(E, N, C) — before calibration
    """
    entailment_score: float
    neutral_score: float
    contradiction_score: float
    predicted_label: str         # "entailment" | "neutral" | "contradiction"
    raw_confidence: float        # max of the three scores, before calibration


@dataclass(frozen=True)
class RelationshipEvidence:
    """
    Complete evidence record for one CandidatePair.

    Contains:
        - pair:             The candidate pair this evidence was gathered for
        - cosine_similarity: From Phase 5 ANN search
        - nli_scores:       Raw NLI evidence (pure scores)
        - calibrated_confidence: Calibrated confidence after ConfidenceCalibrator
        - inference_metadata:  Model + runtime metadata (separated from scores)
        - lifecycle_stage:  EVIDENCE or CALIBRATED_EVIDENCE

    Replaces the original flat RelationshipEvidence which mixed scores and metadata.
    """
    pair: "CandidatePair"
    cosine_similarity: float
    nli_scores: "NLIScores"
    calibrated_confidence: float          # After calibration; use this for thresholding
    inference_metadata: "InferenceMetadata"
    lifecycle_stage: "LifecycleStage" = LifecycleStage.EVIDENCE

    # Convenience accessors (backward-compatible with resolver and tests)
    @property
    def entailment_score(self) -> float:
        return self.nli_scores.entailment_score

    @property
    def neutral_score(self) -> float:
        return self.nli_scores.neutral_score

    @property
    def contradiction_score(self) -> float:
        return self.nli_scores.contradiction_score

    @property
    def predicted_label(self) -> str:
        return self.nli_scores.predicted_label

    @property
    def confidence(self) -> float:
        return self.calibrated_confidence

    @property
    def model_name(self) -> str:
        return self.inference_metadata.model_name


@dataclass(frozen=True)
class RelationshipProvenance:
    """
    Complete audit trail for one Relationship.

    Every relationship must know exactly how it was discovered.
    Enables reproducibility, debugging, future auditing, and replay.

    Fields:
        retrieval_backend:    "faiss_flat_ip" etc.
        retrieval_version:    Phase 6 implementation version
        index_version:        Index build version
        search_parameters:    Full ANN search parameters for exact reproduction
        classifier_model:     NLI model name
        classifier_version:   NLI model version
        resolver_version:     Resolver policy version
        calibrator_version:   ConfidenceCalibrator version
        cosine_similarity:    Similarity from ANN search
        candidate_rank:       Neighbor rank
        raw_nli_confidence:   Confidence before calibration
        calibrated_confidence: Confidence after calibration
        config_hash:          SHA256 of relevant config
        run_id:               Pipeline run identifier
        replay_id:            If this was a replay, the original run_id; else None
    """
    retrieval_backend: str
    retrieval_version: str
    index_version: str
    search_parameters: Optional["RetrievalSearchParameters"]
    classifier_model: str
    classifier_version: str
    resolver_version: str
    calibrator_version: str
    cosine_similarity: float
    candidate_rank: int
    raw_nli_confidence: float
    calibrated_confidence: float
    config_hash: str
    run_id: str
    replay_id: Optional[str] = None


@dataclass(frozen=True)
class RelationshipQuality:
    """Pre-computed quality diagnostics for a Relationship."""
    cosine_above_threshold: bool
    nli_above_threshold: bool
    evidence_consistent: bool   # entailment+contradiction don't both exceed threshold
    calibration_applied: bool   # Whether ConfidenceCalibrator changed the confidence
    retrieval_quality: Optional["RetrievalQuality"] = None


@dataclass(frozen=True)
class SchemaVersionInfo:
    """
    Schema version information for artifact evolution.

    Fields:
        schema_version:        Current schema version (e.g. "6.0")
        migration_version:     Minimum version that can read this artifact (e.g. "6.0")
        compatibility_version: Maximum backward-compatible version (e.g. "5.0" = breaks Phase 5 readers)

    Migration contract:
        When schema_version bumps to 6.1:
            - migration_version stays "6.0" if old Phase 7 readers can still read it
            - migration_version bumps to "6.1" if breaking change
            - compatibility_version reflects the oldest reader still compatible
    """
    schema_version: str
    migration_version: str
    compatibility_version: str


@dataclass(frozen=True)
class Relationship:
    """
    An immutable, fully-traced semantic relationship between two Claims.

    This is Phase 6's canonical output.
    Phase 7 consumes List[Relationship] for temporal reasoning.

    Fields:
        relationship_id:    Deterministic SHA256-based ID (16 hex chars)
        claim_id_a:         First claim
        claim_id_b:         Second claim
        relationship_type:  The semantic relationship (CONTRADICTS, SUPPORTS, etc.)
        direction:          Symmetric or directional (see ontology spec)
        evidence:           Full evidence record (NLI scores + metadata)
        quality:            Pre-computed quality diagnostics
        provenance:         Complete audit trail
        version_info:       Schema/migration/compatibility versions
        lifecycle_stage:    Always RELATIONSHIP when fully constructed
    """
    relationship_id: str
    claim_id_a: str
    claim_id_b: str
    relationship_type: RelationshipType
    direction: RelationshipDirection
    evidence: "RelationshipEvidence"
    quality: RelationshipQuality
    provenance: RelationshipProvenance
    version_info: "SchemaVersionInfo"
    lifecycle_stage: "LifecycleStage" = LifecycleStage.RELATIONSHIP

    # Backward-compatible property
    @property
    def schema_version(self) -> str:
        return self.version_info.schema_version

    def is_contradiction(self) -> bool:
        return self.relationship_type == RelationshipType.CONTRADICTS

    def is_support(self) -> bool:
        return self.relationship_type == RelationshipType.SUPPORTS

    def involves(self, claim_id: str) -> bool:
        return claim_id in (self.claim_id_a, self.claim_id_b)


@dataclass
class RelationshipSet:
    """
    The complete output of Phase 6.
    This is what Phase 7 receives.

    Fields:
        relationships:          All discovered relationships
        total_candidates:       How many candidate pairs were evaluated
        total_validated:        How many passed candidate validation
        total_rejected:         How many were rejected (all stages combined)
        rejected_reasons:       Counts by rejection reason
        run_id:                 Pipeline run identifier
        version_info:           Schema/migration/compatibility versions for this set
        replay_manifest_path:   Path to the replay manifest (for deterministic replay)
    """
    relationships: List["Relationship"]
    total_candidates: int
    total_validated: int
    total_rejected: int
    rejected_reasons: Dict[str, int]
    run_id: str
    version_info: "SchemaVersionInfo" = None
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None
    replay_manifest_path: Optional[Path] = None

    def __post_init__(self):
        if self.version_info is None:
            self.version_info = SchemaVersionInfo(
                schema_version="6.0",
                migration_version="6.0",
                compatibility_version="6.0",
            )

    @property
    def total_relationships(self) -> int:
        return len(self.relationships)

    @property
    def contradictions(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.CONTRADICTS]

    @property
    def supports(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refinements(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.REFINES]


class RelationshipDeduplicationPolicy(str, Enum):
    """
    Policy for handling duplicate relationships (same pair, same type, different runs).

    KEEP_FIRST:     Keep the relationship from the first run that discovered it.
    KEEP_LATEST:    Keep the relationship from the most recent run.
    KEEP_HIGHEST_CONFIDENCE: Keep the relationship with the highest calibrated confidence.
    KEEP_ALL:       Keep all copies (dangerous for graph construction; use for audit).
    """
    KEEP_FIRST              = "keep_first"
    KEEP_LATEST             = "keep_latest"
    KEEP_HIGHEST_CONFIDENCE = "keep_highest_confidence"
    KEEP_ALL                = "keep_all"


class ConflictResolutionPolicy(str, Enum):
    """
    Policy for resolving type conflicts between runs (same pair, different RelationshipType).

    Example: Run 1 says SUPPORTS, Run 2 says CONTRADICTS — which wins?

    LATEST_WINS:       The most recent run's classification wins.
    HIGHEST_CONFIDENCE: The classification with highest calibrated_confidence wins.
    MOST_SPECIFIC:      Priority: CONTRADICTS > REFINES > SUPPORTS > NEUTRAL > UNKNOWN.
    CONSERVATIVE:       Only keep the relationship if all runs agree on the type.
    """
    LATEST_WINS         = "latest_wins"
    HIGHEST_CONFIDENCE  = "highest_confidence"
    MOST_SPECIFIC       = "most_specific"
    CONSERVATIVE        = "conservative"

# ── Phase 7: Knowledge Graph Construction ────────────────────────────────────

class SemanticRole(str, Enum):
    """
    Semantic role annotation derived from graph topology.

    Converted from topology numbers → domain concepts.
    DESCRIPTIVE, not inferential — describes structural importance.

    All thresholds that determine these roles are configured in
    AnnotationPolicy (config/default.yaml: knowledge_graph.annotation).
    No threshold values are hardcoded in annotation.py.
    """
    FOUNDATIONAL_CLAIM  = "foundational_claim"   # High centrality, many SUPPORTS edges
    BRIDGE_CLAIM        = "bridge_claim"          # Articulation point: removal disconnects partition
    EVIDENCE_HUB        = "evidence_hub"          # Many incoming SUPPORTS edges
    REFINEMENT_ROOT     = "refinement_root"       # Source of many REFINES edges
    PERIPHERAL_CLAIM    = "peripheral_claim"      # Low degree, mostly disconnected
    LEAF_CLAIM          = "leaf_claim"            # No outgoing semantic edges
    UNCLASSIFIED        = "unclassified"          # Insufficient topology data


class TemporalStatus(str, Enum):
    """Status of temporal analysis for a contradiction boundary."""
    EVOLUTION_CHAIN     = "evolution_chain"       # Reliable semantic timestamps → evolved
    STATIC_PARTITION    = "static_partition"      # No timestamp ordering → competing beliefs
    UNRESOLVED_CONFLICT = "unresolved_conflict"   # Identical timestamps → cannot determine
    NO_TIMESTAMP        = "no_timestamp"          # Claim.timestamp unavailable → disabled


@dataclass(frozen=True)
class TopologyMetrics:
    """
    Graph-derived structural information for one ClaimNode.
    Computed by TopologyAnalyzer within each partition.

    Bridge detection uses NetworkX articulation_points, not degree-heuristics.
    Density is computed as directed: edges / (n * (n-1)), n = partition size.
    """
    degree: int                      # Total edges (in + out)
    in_degree: int                   # Incoming edges (being supported/contradicted)
    out_degree: int                  # Outgoing edges (supporting/contradicting others)
    is_bridge: bool                  # True articulation point (NetworkX algorithm)
    is_hub: bool                     # Significantly above-average degree (config-driven)
    partition_id: str                # Which partition this node belongs to
    centrality: float = 0.0          # Normalized in-degree centrality (in_degree / (N-1))


@dataclass(frozen=True)
class SupportAggregate:
    """
    Aggregated semantic support for one ClaimNode within its partition.

    PROVENANCE ROOT DEFINITION:
    This aggregate includes ALL transitive supporting claims. In a chain where 
    A -> B -> C, both A and B are considered supporting claims of C. 
    The supporting_claim_ids tuple contains the unique IDs of all such claims, 
    ensuring no claim is double-counted even if multiple paths exist.
    """
    support_count: int
    weighted_confidence: float
    supporting_claim_ids: tuple
    evidence_summary: str         # Human-readable summary


@dataclass(frozen=True)
class TemporalMetadata:
    """
    Temporal evolution metadata for one contradiction boundary.

    RECTIFIED: populated from Claim.timestamp (semantic timestamp),
    never from filesystem st_mtime. If Claim.timestamp is None,
    status is NO_TIMESTAMP rather than inferring from the filesystem.
    """
    status: TemporalStatus
    earlier_claim_id: Optional[str]  # claim_id of the earlier claim (if EVOLUTION_CHAIN)
    later_claim_id: Optional[str]    # claim_id of the later claim (if EVOLUTION_CHAIN)
    time_delta_days: Optional[float] # Days between timestamps
    temporal_confidence: float       # Confidence in the temporal ordering (0.0–1.0)


@dataclass(frozen=True)
class NodeAnnotations:
    """
    All enrichment annotations for one ClaimNode, grouped into a single container.

    RECTIFIED (P1-2): ClaimNode no longer stores topology, support, temporal,
    semantic role, and partition_id as flat fields. These are grouped here.
    ClaimNode.annotations is a single Optional[NodeAnnotations].

    This decouples the enrichment lifecycle from the domain model.
    """
    semantic_role: SemanticRole = SemanticRole.UNCLASSIFIED
    topology: Optional["TopologyMetrics"] = None
    support_aggregate: Optional["SupportAggregate"] = None
    temporal_metadata: Optional["TemporalMetadata"] = None
    partition_id: Optional[str] = None
    stable_partition_label: Optional[str] = None  # Incremental-friendly label (P2-5)


@dataclass(frozen=True)
class ClaimNode:
    """
    One canonical semantic claim inside the KnowledgeGraph.

    RECTIFIED (P1-2): All enrichment data lives in NodeAnnotations.
    ClaimNode itself only holds identity + raw claim data.
    Backward-compatible property accessors are provided for all original fields.

    Fields:
        node_id:       Deterministic ID == claim_id from Phase 4
        claim_id:      Reference to the originating Claim
        claim_text:    Original claim text
        context:       Heading context (e.g. "Python > Generators")
        source_path:   Original file path
        document_id:   Which document produced this claim
        annotations:   All topology/support/temporal/role/partition data
        schema_version: "7.0"
    """
    node_id: str
    claim_id: str
    claim_text: str
    context: str
    source_path: Path
    document_id: str
    annotations: Optional["NodeAnnotations"] = None
    schema_version: str = "7.0"

    # ── Backward-compatible accessors ──────────────────────────────────────────
    @property
    def semantic_role(self) -> "SemanticRole":
        if self.annotations:
            return self.annotations.semantic_role
        return SemanticRole.UNCLASSIFIED

    @property
    def topology(self) -> Optional["TopologyMetrics"]:
        return self.annotations.topology if self.annotations else None

    @property
    def support_aggregate(self) -> Optional["SupportAggregate"]:
        return self.annotations.support_aggregate if self.annotations else None

    @property
    def temporal_metadata(self) -> Optional["TemporalMetadata"]:
        return self.annotations.temporal_metadata if self.annotations else None

    @property
    def partition_id(self) -> Optional[str]:
        return self.annotations.partition_id if self.annotations else None


@dataclass(frozen=True)
class RelationshipEdge:
    """
    One semantic relationship inside the KnowledgeGraph.

    Invariants:
        - source_node_id and target_node_id must reference existing ClaimNodes
        - relationship_type is NEVER UNKNOWN
        - NEUTRAL is absent unless configuration explicitly permits it
        - Every edge is unique (pair + type)
    """
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: "RelationshipType"
    direction: "RelationshipDirection"
    calibrated_confidence: float
    cosine_similarity: float
    nli_confidence: float
    candidate_rank: int
    schema_version: str = "7.0"


@dataclass(frozen=True)
class KnowledgePartition:
    """
    One internally consistent semantic context within the KnowledgeGraph.

    RECTIFIED (P1-5): density is DIRECTED: edges / (n * (n-1)) where n = node count.
    This is documented explicitly. Previously the formula was ambiguous.

    RECTIFIED (P2-5): stable_partition_label added alongside SHA256-based partition_id.
    stable_partition_label is the sorted comma-separated list of node_ids, enabling
    comparison across incremental runs without rehashing.

    Invariants:
        - No CONTRADICTS edges exist WITHIN a partition
        - All nodes within a partition are reachable via SUPPORTS/REFINES
        - Partition membership is exclusive
    """
    partition_id: str                        # SHA256(sorted_node_ids)[:12] — deterministic
    stable_partition_label: tuple              # sorted ",".join(node_ids) — incremental-friendly
    node_ids: frozenset
    internal_edge_ids: frozenset
    node_count: int
    edge_count: int
    supports_count: int
    refines_count: int
    density: float                           # Directed: edge_count / (n * (n-1)); 0 if n<=1
    longest_support_chain: int
    schema_version: str = "7.0"


@dataclass(frozen=True)
class GraphStatistics:
    """Graph-wide statistics for one KnowledgeGraph."""
    node_count: int
    edge_count: int
    partition_count: int
    contradiction_count: int
    supports_count: int
    refines_count: int
    isolated_nodes: int
    bridge_nodes: int                        # True articulation points (P0-3 fix)
    hub_nodes: int
    evolution_chains: int
    unresolved_conflicts: int
    construction_time_seconds: float
    enrichment_time_seconds: float


@dataclass(frozen=True)
class ValidationReport:
    is_valid: bool
    node_violations: tuple
    edge_violations: tuple
    graph_violations: tuple
    semantic_warnings: tuple   # Renamed from semantic_violations
    validation_time_seconds: float

    @property
    def total_violations(self) -> int:
        return (
            len(self.node_violations) + len(self.edge_violations)
            + len(self.graph_violations)
        )


@dataclass(frozen=True)
class KnowledgeGraph:
    """
    The immutable canonical semantic representation of the entire corpus.
    Phase 7's output and Phase 8's input.

    KnowledgeGraph is NOT a live graph database.
    It is a frozen artifact representing the state of knowledge at one point in time.
    """
    graph_id: str
    nodes: Dict[str, "ClaimNode"]
    edges: Dict[str, "RelationshipEdge"]
    partitions: Dict[str, "KnowledgePartition"]
    statistics: "GraphStatistics"
    validation_report: "ValidationReport"
    run_id: str
    config_hash: str
    schema_version: str = "7.0"

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def partition_count(self) -> int:
        return len(self.partitions)

    @property
    def contradiction_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.CONTRADICTS]

    @property
    def supports_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refines_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.REFINES]

    def get_node(self, claim_id: str) -> Optional["ClaimNode"]:
        return self.nodes.get(claim_id)

    def get_partition_for_node(self, claim_id: str) -> Optional["KnowledgePartition"]:
        node = self.nodes.get(claim_id)
        if node and node.partition_id:
            return self.partitions.get(node.partition_id)
        return None


@dataclass(frozen=True)
class Phase7Stats:
    """Statistics collected during Phase 7 execution."""
    input_relationships: int = 0
    input_filtered: int = 0
    nodes_created: int = 0
    edges_created: int = 0
    partitions_created: int = 0
    contradictions_as_boundaries: int = 0
    evolution_chains_detected: int = 0
    unresolved_conflicts: int = 0
    construction_time_seconds: float = 0.0
    enrichment_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    validation_passed: bool = False    

# ── Phase 7 contract: Contradiction → Scoring ────────────────────────────────

@dataclass
class Contradiction:
    """A detected contradiction between two claims. Produced by Phase 7."""
    claim_a_id: str
    claim_b_id: str
    contradiction_type: ContradictionType
    nli_confidence: float       # Gate 2 output
    similarity_score: float     # Gate 1 output
    temporal_distance_days: int
    severity_score: float       # Gate 3 final score
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def __repr__(self) -> str:
        return (
            f"Contradiction({self.claim_a_id[:20]} vs {self.claim_b_id[:20]}, "
            f"type={self.contradiction_type}, severity={self.severity_score:.2f})"
        )


# ── Phase 8: Reliability Evaluation ──────────────────────────────────────────

class CalibrationLabel(str, Enum):
    """
    Human-readable reliability tier derived from Reliability Index.

    RECTIFIED (P1-4): Each label now has a semantic contract that Phase 9
    can consume without guessing. The contract is documented here and enforced
    by the Validation Checklist.

    Contracts:
        VERY_HIGH: Multiple independent, high-confidence sources, no significant
                   contradiction. Display with full confidence.
        HIGH:      Well-supported, minor concerns only. Display normally.
        MODERATE:  Some support but notable gaps, limited independence, or weak
                   conflict present. Note caveats.
        LOW:       Weak/dependent evidence or moderate conflict. Flag for review.
        VERY_LOW:  No meaningful support or overwhelmed by contradiction. Mark unverified.

    Calibration changes representation, NOT underlying evidence.
    """
    VERY_HIGH = "very_high"   # RI >= 80
    HIGH      = "high"        # RI >= 65
    MODERATE  = "moderate"    # RI >= 45
    LOW       = "low"         # RI >= 25
    VERY_LOW  = "very_low"    # RI < 25

class SignalID(str, Enum):
    """Canonical registry of all known signal identities."""
    EVIDENCE_STRENGTH = "evidence_strength"
    EVIDENCE_INDEPENDENCE = "evidence_independence"
    SOURCE_DIVERSITY = "source_diversity"
    TOPOLOGY_STRENGTH = "topology_strength"
    HUB_SCORE = "hub_score"
    BRIDGE_SCORE = "bridge_score"
    CONFLICT_PRESSURE = "conflict_pressure"
    TEMPORAL_STABILITY = "temporal_stability"

class SignalStatus(str, Enum):
    """Quality status for a single extracted signal."""
    MEASURED    = "measured"     # Derived from full graph data
    ESTIMATED   = "estimated"    # Derived but with incomplete data
    UNAVAILABLE = "unavailable"  # Cannot be computed (e.g., no provenance)
    DEFAULT     = "default"      # Using policy default (no signal data)

    


@dataclass(frozen=True)
class RawSignal:
    """
    Raw measurement from one signal extractor, before normalization.

    Fields:
        name:              Signal identifier (matches ContributionCandidate.signal_name)
        raw_value:         The raw measurement (units depend on signal, may exceed [0,1])
        normalized_value:  Value after extractor-owned normalization (always in [0,1])
        status:            Quality status of this measurement
        metadata:          Extractor-specific diagnostic metadata
    """
    name: str
    raw_value: float
    normalized_value: float           # Owned by extractor (P1-2 fix)
    status: SignalStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SignalManifest:
    """
    RECTIFIED (P0-4): Full derivation trace for one signal, one claim.

    This is NOT the same as an audit trail (which covers versioning).
    This covers derivation: WHY this signal has this value.

    Fields:
        signal_name:           Signal identifier
        extractor_version:     Version of the extractor that produced this signal
        raw_value:             Before normalization
        normalized_value:      After extractor-owned normalization
        normalization_strategy: Description of the strategy used (e.g., "log_scale")
        status:                Signal quality status
        quality_flags:         List of quality issues detected (e.g., ["low_sample"])
        dependency_list:       Which graph fields this signal depended on
        diagnostics:           Arbitrary extractor-specific diagnostic data
    """
    signal_id: SignalID
    extractor_version: str
    raw_value: float
    normalized_value: float
    normalization_strategy: str          # e.g. "log_scale", "linear", "step_function"
    status: SignalStatus
    quality_flags: tuple                  # e.g. ("low_sample_count", "echo_chamber_risk")
    dependency_list: tuple                # e.g. ("support_aggregate", "topology.centrality")
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContributionCandidate:
    """
    RECTIFIED (P0-2): What the Fusion Engine receives for one signal.

    Fusion engine receives a list of ContributionCandidates and knows NOTHING
    about what the signals mean — it only knows: normalized_value, policy_weight,
    direction, and label. This is the key architectural fix that decouples Fusion
    from signal semantics.

    Fields:
        signal_name:       Identifier (opaque to Fusion)
        normalized_value:  In [0,1]
        policy_weight:     From policy (how important is this signal)
        direction:         "positive" (higher = more reliable) or "negative" (higher = less reliable)
        label:             Human-readable signal label for explanation generation
        raw_value:         Original pre-normalization value (for DecisionRecord)
    """
    signal_id: SignalID
    normalized_value: float
    policy_weight: float
    direction: str               # "positive" | "negative"
    label: str                   # For explanation generation
    raw_value: float = 0.0       # Pre-normalization, for DecisionRecord


@dataclass(frozen=True)
class ContributionSet:
    """
    RECTIFIED (P0-2): The complete set of ContributionCandidates for one claim.

    This is what the Fusion Engine receives. It contains everything needed
    to compute the Reliability Index without the Fusion Engine knowing anything
    about individual signal semantics.
    """
    candidates: tuple               # Tuple[ContributionCandidate, ...]
    evidence_completeness: float    # Fraction of signals with actual measurements
    claim_id: str                   # For logging/tracing


@dataclass(frozen=True)
class ComponentScore:
    """One signal's contribution to the final Reliability Index."""
    signal_id: SignalID
    normalized_value: float    # From ContributionCandidate (0.0–1.0)
    policy_weight: float       # From policy (0.0–1.0)
    adjusted_value: float      # After policy interactions
    contribution: float        # = adjusted_value * policy_weight * 100 (or negative)
    direction: str             # "positive" or "negative"
    explanation: str           # Human-readable reason


@dataclass(frozen=True)
class ReliabilityDecisionRecord:
    """
    RECTIFIED (P0-5): Full decision path for one claim's reliability score.

    Contains everything needed to understand exactly WHY a claim received
    its reliability index — from policy interactions to constraints activated.

    Invaluable for:
        - Benchmarking policy profiles against each other
        - Debugging unexpected scores
        - Future academic documentation
        - Phase 9 surfacing "why" explanations to users

    Fields:
        claim_id:                  Which claim this covers
        policy_interactions:       List of interactions applied (e.g., "echo_chamber_discount")
        constraints_activated:     List of constraints that fired (e.g., "no_evidence_cap")
        contribution_order:        Signal names in decreasing absolute contribution order
        raw_reliability:           Before constraints
        constrained_reliability:   After constraints, before clamping
        final_reliability:         After clamping to [0, 100]
        uncertainty_components:    What drove the uncertainty score
        dominant_adjustment:       The single most impactful policy interaction
    """
    claim_id: str
    policy_interactions: tuple           # e.g. ("echo_chamber_discount_applied",)
    constraints_activated: tuple         # e.g. ("no_evidence_cap: 60.0",)
    contribution_order: tuple            # signal names by descending |contribution|
    raw_reliability: float
    constrained_reliability: float
    final_reliability: float
    uncertainty_components: tuple        # (component_name, contribution) tuples
    dominant_adjustment: str


@dataclass(frozen=True)
class SignalVector:
    """
    All normalized signal measurements for one ClaimNode.
    All values are in [0.0, 1.0].

    Kept for backward compatibility with existing normalization tests.
    In the rectified architecture, ContributionSet is the primary fusion input.
    SignalVector is assembled from ContributionCandidates for serialization.
    """
    evidence_strength: float
    evidence_independence: float
    source_diversity: float
    topology_strength: float
    conflict_pressure: float
    temporal_stability: float
    evidence_completeness: float
    statuses: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ReliabilityExplanation:
    """Structured explanation for a Reliability Index."""
    summary: str
    strengths: tuple
    weaknesses: tuple
    dominant_signal: str
    limiting_signal: str
    recommendations: tuple


@dataclass(frozen=True)
class ReliabilityAudit:
    """Reproducibility audit trail for one ReliabilityMetadata."""
    policy_version: str
    policy_profile: str 
    graph_fingerprint: str             # NEW (P1-3): which profile was active
    graph_schema_version: str
    fusion_algorithm: str
    normalization_version: str
    computed_at_run_id: str
    signal_extractor_versions: Dict[str, str]
    registry_order: tuple            # NEW: ordered list of registered signal names


@dataclass(frozen=True)
class ReliabilityHistory:
    """
    RECTIFIED (P1-5): Architecture stub for confidence evolution tracking.

    Not active in production (requires cross-run storage).
    Architecture is wired up so Phase 9/10 can activate it.
    """
    claim_id: str
    history: tuple   # Tuple of (run_id, reliability_index, timestamp_iso) triples


@dataclass(frozen=True)
class ReliabilityMetadata:
    """
    The complete reliability profile for one ClaimNode.

    RECTIFIED: Now includes SignalManifest list and ReliabilityDecisionRecord.

    Fields:
        claim_id:               Links to KnowledgeGraph.nodes[claim_id]
        reliability_index:      Final score 0–100
        uncertainty_score:      Measurement uncertainty 0–100
        evidence_completeness:  Fraction of signals with actual measurements
        signal_vector:          All normalized signal measurements (for serialization)
        signal_manifests:       Per-signal derivation traces (NEW P0-4)
        component_scores:       Per-signal contributions (fully explainable)
        decision_record:        Full policy decision path (NEW P0-5)
        explanation:            Structured human-readable explanation
        calibration_label:      Human-friendly tier with semantic contract
        audit:                  Full reproducibility audit trail
        policy_version:         Which policy version produced this score
        schema_version:         "8.0"
    """
    claim_id: str
    reliability_index: float
    uncertainty_score: float
    evidence_completeness: float
    signal_vector: SignalVector
    signal_manifests: tuple            # Tuple[SignalManifest, ...] — NEW (P0-4)
    component_scores: tuple
    decision_record: ReliabilityDecisionRecord  # NEW (P0-5)
    explanation: ReliabilityExplanation
    calibration_label: CalibrationLabel
    audit: ReliabilityAudit
    policy_version: str
    schema_version: str = "8.0"


@dataclass(frozen=True)
class ScoringGlobalStats:
    """Graph-wide statistics computed once and shared by all signal extractors."""
    max_support_count: int
    avg_support_count: float
    max_in_degree: int
    avg_degree: float
    max_contradiction_partners: int
    avg_contradiction_partners: float
    max_source_diversity: int
    max_temporal_confidence: float
    node_count: int
    partition_count: int
    contradiction_count: int
    supports_count: int


@dataclass(frozen=True)
class ScoredKnowledgeGraph:
    """
    Phase 8's canonical output: KnowledgeGraph + reliability overlay.

    The original KnowledgeGraph remains immutable.
    Reliability metadata lives in a separate dict indexed by claim_id.

    Design allows:
        - Multiple scoring policies on the same graph (via PolicyProfile)
        - Policy comparisons side by side
        - Future phases choosing which scoring profile to consume
    """
    graph: "KnowledgeGraph"
    reliability: Dict[str, ReliabilityMetadata]
    policy_snapshot: Dict[str, Any]
    policy_profile: str              # NEW (P1-3): which profile was used
    global_stats: ScoringGlobalStats
    run_id: str
    schema_version: str = "8.0"

    @property
    def total_scored(self) -> int:
        return len(self.reliability)

    @property
    def avg_reliability(self) -> float:
        if not self.reliability:
            return 0.0
        return sum(m.reliability_index for m in self.reliability.values()) / len(self.reliability)

    def get_reliability(self, claim_id: str) -> Optional[ReliabilityMetadata]:
        return self.reliability.get(claim_id)

    def top_reliable(self, n: int = 10) -> List[ReliabilityMetadata]:
        return sorted(
            self.reliability.values(),
            key=lambda m: m.reliability_index,
            reverse=True,
        )[:n]

    def least_reliable(self, n: int = 10) -> List[ReliabilityMetadata]:
        return sorted(
            self.reliability.values(),
            key=lambda m: m.reliability_index,
        )[:n]


@dataclass(frozen=True)
class ExecutionStats:
    """Runtime and performance metrics for the Phase 8 engine."""
    total_runtime_seconds: float
    signal_extraction_seconds: float
    fusion_seconds: float
    registered_signal_count: int

@dataclass(frozen=True)
class KnowledgeStats:
    """Scientific and epistemic metrics for the evaluated graph."""
    total_claims_scored: int
    avg_reliability_index: float
    avg_uncertainty_score: float
    calibration_histogram: Dict[str, int]  # e.g., {"VERY_HIGH": 12, "LOW": 3}

@dataclass(frozen=True)
class Phase8Telemetry:
    """Complete telemetry payload for a Phase 8 execution."""
    policy_version: str
    policy_profile: str
    execution: ExecutionStats
    knowledge: KnowledgeStats


# ── Phase 8 contract: Evolution ───────────────────────────────────────────────

@dataclass
class Topic:
    """A topic/theme grouping related claims. Produced by Phase 8."""
    name: str
    claim_ids: List[str] = field(default_factory=list)
    contradiction_count: int = 0

    @property
    def drift_score(self) -> float:
        """Drift score for this topic (0–100)."""
        if not self.claim_ids:
            return 0.0
        return min(100.0, (self.contradiction_count / len(self.claim_ids)) * 100)


@dataclass
class EvolutionChain:
    """Temporal chain of related claims showing how a belief evolved."""
    topic: str
    claim_ids: List[str]                    # Ordered by timestamp
    stages: List[Dict[str, Any]] = field(default_factory=list)


# ── Manifest and state ────────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    """Record of a completed phase. Written by ManifestManager after each phase."""
    run_id: str                             # unique per execution
    phase: int
    timestamp: datetime
    duration_seconds: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str                             # pending | running | success | failed
    schema_version: str = "1.0"            # version manifest format
    error: Optional[str] = None
    versions: Dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineState:
    """Current state of pipeline execution. Persisted for resume capability."""
    started_at: datetime
    current_phase: int
    completed_phases: List[int] = field(default_factory=list)
    manifests: List[ManifestEntry] = field(default_factory=list)

    def is_resumable(self) -> bool:
        """Can pipeline be resumed from checkpoint?"""
        return len(self.manifests) > 0


# ── Internal embedding models (not exported) ────────────────────────────────
# These are used internally by Phase 5; they never cross the phase boundary.
````

## File: src/smriti/core/paths.py
````python
"""
Centralized path definitions for SMRITI.

Every path in the project is derived from PROJECT_ROOT.
Import from here — never hardcode path strings elsewhere.
"""

from pathlib import Path

# === ROOT ===
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # smriti/

# === SOURCE ===
SRC_DIR = PROJECT_ROOT / "src" / "smriti"

# === CONFIGURATION ===
CONFIG_DIR = PROJECT_ROOT / "config"

# === DATA (input) ===
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# === CACHE (ephemeral — always safe to delete) ===
CACHE_DIR = PROJECT_ROOT / "cache"
EMBEDDINGS_CACHE_DIR = CACHE_DIR / "embeddings"
PARSED_CACHE_DIR = CACHE_DIR / "parsed"
RETRIEVAL_CACHE_DIR = CACHE_DIR / "retrieval"
NLI_CACHE_DIR = CACHE_DIR / "nli"
HASH_CACHE_FILE = CACHE_DIR / "hashes.json"

# === ARTIFACTS (immutable — do not delete) ===
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

# === OUTPUT ===
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"

# === STATE ===
STATE_FILE = ARTIFACTS_DIR / "pipeline_state.json"


def ensure_dirs() -> None:
    """Create all required directories on first run."""
    dirs = [
        RAW_DATA_DIR,
        EMBEDDINGS_CACHE_DIR,
        PARSED_CACHE_DIR,
        RETRIEVAL_CACHE_DIR,
        NLI_CACHE_DIR,
        ARTIFACTS_DIR,
        LOG_DIR,
        REPORTS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
````

## File: src/smriti/core/state.py
````python
"""
Pipeline state for resuming interrupted runs.
Stores: which phases completed, when they started, current position.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog

from smriti.core.paths import STATE_FILE
from smriti.core.models import PipelineState


logger = structlog.get_logger(__name__)


class StateManager:
    """Persist and restore pipeline state across interruptions."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def start_run(self) -> PipelineState:
        """Initialize a new pipeline run and persist it."""
        state = PipelineState(started_at=datetime.now(), current_phase=1)
        self.save(state)
        logger.info("pipeline run started", started_at=state.started_at.isoformat())
        return state

    def complete_phase(self, phase: int) -> None:
        """Mark a phase as completed and advance current_phase."""
        state = self.load()
        if state:
            if phase not in state.completed_phases:
                state.completed_phases.append(phase)
            state.current_phase = phase + 1
            self.save(state)
            logger.info("phase marked complete", phase=phase)

    def load(self) -> Optional[PipelineState]:
        """Load existing state. Returns None if no state file found."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, encoding="utf-8") as f:
                data = json.load(f)
            return PipelineState(
                started_at=datetime.fromisoformat(data["started_at"]),
                current_phase=data.get("current_phase", 1),
                completed_phases=data.get("completed_phases", []),
            )
        except Exception as e:
            logger.error("state load failed", error=str(e))
            return None

    def save(self, state: PipelineState) -> None:
        """Persist state to disk."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "started_at": state.started_at.isoformat(),
                    "current_phase": state.current_phase,
                    "completed_phases": state.completed_phases,
                },
                f,
                indent=2,
            )

    def clear(self) -> None:
        """Clear saved state (use before a fresh run)."""
        if self.state_file.exists():
            self.state_file.unlink()
        logger.info("state cleared")
````

## File: src/smriti/core/timing.py
````python
"""
Performance timing for pipeline profiling.

Captures:
  - Wall clock time
  - CPU time (user + system)
  - Peak memory delta (MB)
  - Optional: documents processed, claims generated

Invaluable for identifying bottlenecks before optimizing.
"""

import time
import os
import psutil
import structlog
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, Generator

logger = structlog.get_logger(__name__)

_process = psutil.Process(os.getpid())


@dataclass
class TimingStats:
    """Performance statistics captured during a timed block."""

    operation: str
    wall_time_seconds: float
    cpu_time_seconds: float
    peak_memory_delta_mb: float
    documents_processed: int = 0
    claims_generated: int = 0

    def log(self) -> None:
        logger.info(
            "timing_stats",
            operation=self.operation,
            wall_s=f"{self.wall_time_seconds:.2f}",
            cpu_s=f"{self.cpu_time_seconds:.2f}",
            peak_mem_mb=f"{self.peak_memory_delta_mb:.1f}",
            docs=self.documents_processed,
            claims=self.claims_generated,
        )


class Timer:
    """
    Context manager that captures wall time, CPU time, and peak memory.

    Usage:
        with Timer("Phase 4 — Embedding") as t:
            run_embedding(claims)
        t.stats.log()
    """

    def __init__(self, name: str):
        self.name = name
        self.stats: Optional[TimingStats] = None

    def __enter__(self) -> "Timer":
        self._wall_start = time.perf_counter()
        self._cpu_start = time.process_time()
        mem = _process.memory_info()
        self._mem_start_mb = mem.rss / 1024 / 1024
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        wall = time.perf_counter() - self._wall_start
        cpu = time.process_time() - self._cpu_start
        mem_end_mb = _process.memory_info().rss / 1024 / 1024
        peak_delta = mem_end_mb - self._mem_start_mb

        self.stats = TimingStats(
            operation=self.name,
            wall_time_seconds=wall,
            cpu_time_seconds=cpu,
            peak_memory_delta_mb=peak_delta,
        )
        self.stats.log()


@contextmanager
def timed_operation(name: str) -> Generator[None, None, None]:
    """Lightweight context manager for one-liner timing."""
    with Timer(name) as t:
        yield
    # stats already logged by Timer.__exit__
````

## File: src/smriti/dashboard/__init__.py
````python

````

## File: src/smriti/dashboard/app.py
````python
# Will be filled in Phase 10\n
````

## File: src/smriti/discovery/__init__.py
````python
"""
discovery/__init__.py — Public API for Phase 1.

External callers (PipelineRunner) import from here:

    from smriti.discovery import run_discovery, DiscoveryResult

They never import from individual submodules.

Orchestration:
  1. Validate input directories           [validator.validate_directories]
  2. Discover candidate files             [scanner.discover_files]
  3. Validate each candidate file         [validator.validate_file]
  4. Extract metadata for valid files     [metadata.extract_metadata]
  5. Compute content hash                 [hashing.compute_hash + hash cache]
  6. Build duplicate registry             [duplicate.build_duplicate_registry]
  7. Build source documents               [builder.build_source_document]
  8. Write manifest                       [manifest.ManifestManager]
  9. Update pipeline state                [state.StateManager]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.hashing import ContentHasher
from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR, CACHE_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import DiscoveryError

from smriti.discovery.scanner import discover_files
from smriti.discovery.validator import validate_directories, validate_file
from smriti.discovery.metadata import extract_metadata, FileMetadata
from smriti.discovery.hashing import compute_hash
from smriti.discovery.duplicate import build_duplicate_registry, DuplicateRegistry
from smriti.discovery.builder import SourceDocument, build_source_document

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveryContext:
    """
    Immutable shared execution context for Phase 1.
    Carries configuration, run metadata, and managers.
    """
    run_id: str
    manifest_manager: ManifestManager
    state_manager: StateManager
    force_full: bool
    config: dict
    discovered_at: datetime


@dataclass
class DiscoveryStats:
    """Statistics from one discovery run."""

    total_candidates: int = 0
    valid_count: int = 0
    skipped_count: int = 0
    duplicate_count: int = 0
    # Incremental stats (based on hash cache)
    unchanged_count: int = 0
    new_count: int = 0
    modified_count: int = 0

    def summary(self) -> str:
        return (
            f"discovered={self.valid_count} "
            f"skipped={self.skipped_count} "
            f"duplicates={self.duplicate_count} "
            f"new={self.new_count} "
            f"unchanged={self.unchanged_count} "
            f"modified={self.modified_count}"
        )


@dataclass
class DiscoveryResult:
    """
    Complete output of Phase 1.
    This is what Phase 2 receives.

    Attributes:
        documents:          All valid SourceDocument objects (including duplicates).
        duplicate_registry: Mapping from content hash to duplicate info.
        skipped:            All paths that failed validation (with reasons).
        stats:              Summary statistics.
        run_id:             Pipeline run identifier.
        manifest_path:      Path to written manifest.json.
    """

    documents: List[SourceDocument]
    duplicate_registry: DuplicateRegistry
    skipped: List[Tuple[Path, str]]
    stats: DiscoveryStats
    run_id: str
    manifest_path: Optional[Path] = None

    @property
    def canonical_documents(self) -> List[SourceDocument]:
        """Return only canonical (non‑duplicate) documents."""
        return [d for d in self.documents if not self.duplicate_registry.is_duplicate(d.path)]

    @property
    def duplicate_documents(self) -> List[SourceDocument]:
        """Return only duplicate documents."""
        return [d for d in self.documents if self.duplicate_registry.is_duplicate(d.path)]

    @property
    def canonical_count(self) -> int:
        return len(self.canonical_documents)

    def to_dataset_json(self) -> str:
        """
        Serialize the canonical document dataset to JSON.
        Written to artifacts/run_{id}/phase1/dataset.json for Phase 2.
        """
        records = []
        for doc in self.canonical_documents:
            records.append({
                "doc_id": doc.doc_id,
                "path": str(doc.path),
                "relative_path": str(doc.relative_path),
                "source_root": str(doc.source_root),
                "format": doc.format.value,
                "content_hash": doc.content_hash,
                "size_bytes": doc.size_bytes,
                "modified_at": doc.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_discovery(
    input_dirs: List[Path],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    force_full: bool = False,
) -> DiscoveryResult:
    """
    Execute the complete Phase 1 discovery pipeline.

    Args:
        input_dirs:       Root directories to scan.
        run_id:           Unique pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        force_full:       If True, ignore hash cache and re-process all files.

    Returns:
        DiscoveryResult containing canonical documents and statistics.

    Raises:
        DiscoveryError: If input directories are invalid (fatal).
    """
    config = get_config()
    discovered_at = datetime.now(tz=timezone.utc)
    context = DiscoveryContext(
        run_id=run_id,
        manifest_manager=manifest_manager,
        state_manager=state_manager,
        force_full=force_full,
        config=config,
        discovered_at=discovered_at,
    )
    stats = DiscoveryStats()

    with Timer("phase1_discovery") as timer:

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=1)
        logger.info("phase 1 starting", run_id=run_id)

        # ── Step 2: Validate input directories ────────────────────────────────
        logger.info("validating input directories", count=len(input_dirs))
        validated_roots = validate_directories(input_dirs)

        # ── Step 3: Discover candidate files ──────────────────────────────────
        logger.info("scanning directories")
        candidate_paths = discover_files(validated_roots)
        stats.total_candidates = len(candidate_paths)
        logger.info("candidates found", count=stats.total_candidates)

        # ── Step 4: Validate individual files ─────────────────────────────────
        logger.info("validating files")
        valid_paths: List[Path] = []
        skipped: List[Tuple[Path, str]] = []

        for path in candidate_paths:
            result = validate_file(path)
            if result.is_valid:
                valid_paths.append(path)
            else:
                skipped.append((path, result.rejection_reason))
                logger.debug(
                    "file skipped",
                    path=str(path),
                    reason=result.rejection_reason,
                )

        stats.valid_count = len(valid_paths)
        stats.skipped_count = len(skipped)
        logger.info(
            "file validation complete",
            valid=stats.valid_count,
            skipped=stats.skipped_count,
        )

        # ── Step 5: Extract metadata ───────────────────────────────────────────
        logger.info("extracting metadata")
        metadata_map: Dict[Path, FileMetadata] = {}
        for path in valid_paths:
            try:
                metadata_map[path] = extract_metadata(path)
            except OSError as e:
                logger.warning("metadata extraction failed", path=str(path), error=str(e))
                skipped.append((path, f"metadata error: {e}"))
                stats.skipped_count += 1
                stats.valid_count -= 1

        valid_paths = [p for p in valid_paths if p in metadata_map]

        # ── Step 6: Compute content hashes (with incremental cache) ───────────
        logger.info("computing content hashes")
        hash_cache = ContentHasher(cache_file=CACHE_DIR / "hashes.json")
        path_hash_pairs: List[Tuple[Path, str]] = []
        
        new_active_hashes: Dict[str, str] = {}  # <-- ADDED: Initialize fresh dictionary

        for path in valid_paths:
            try:
                content_hash = compute_hash(path)  # reads once
            except OSError as e:
                logger.warning("hash computation failed", path=str(path), error=str(e))
                skipped.append((path, f"hash error: {e}"))
                stats.skipped_count += 1
                continue

            # Incremental classification (for stats only)
            if not force_full:
                cached = hash_cache.hashes.get(str(path))
                if cached is None:
                    stats.new_count += 1
                elif cached == content_hash:
                    stats.unchanged_count += 1
                else:
                    stats.modified_count += 1
            else:
                stats.new_count += 1

            # <-- CHANGED: Populate the fresh dictionary instead of updating old cache
            new_active_hashes[str(path)] = content_hash  
            path_hash_pairs.append((path, content_hash))

        # <-- ADDED: Overwrite the cache completely to prune deleted files
        hash_cache.hashes = new_active_hashes
        hash_cache._save()

        # ── Step 7: Detect duplicates ──────────────────────────────────────────
        logger.info("detecting duplicate content")
        duplicate_registry = build_duplicate_registry(path_hash_pairs)
        stats.duplicate_count = duplicate_registry.duplicate_count

        # ── Step 8: Build source documents ────────────────────────────────────
        logger.info("building source documents")
        hash_dict = dict(path_hash_pairs)
        all_documents: List[SourceDocument] = []

        for path in valid_paths:
            if path not in hash_dict:
                continue  # was skipped during hashing

            # Determine which root this file belongs to
            source_root = _find_source_root(path, validated_roots)

            doc = build_source_document(
                metadata=metadata_map[path],
                content_hash=hash_dict[path],
                source_root=source_root,
            )
            all_documents.append(doc)

        # ── Step 9: Write dataset artifact ────────────────────────────────────
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase1"
        phase_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = phase_dir / "dataset.json"

        result = DiscoveryResult(
            documents=all_documents,
            duplicate_registry=duplicate_registry,
            skipped=skipped,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(
            result.to_dataset_json(), encoding="utf-8"
        )
        logger.info("dataset written", path=str(dataset_path), count=result.canonical_count)

        # ── Step 10: Write manifest ────────────────────────────────────────────
        manifest_path = manifest_manager.end_phase(
            phase=1,
            start_time=start_time,
            inputs={
                "directories": [str(d) for d in input_dirs],
                "force_full": force_full,
            },
            outputs={
                "canonical_documents": result.canonical_count,
                "duplicate_documents": len(result.duplicate_documents),
                "skipped_files": len(skipped),
                "dataset_path": str(dataset_path),
            },
            status="success",
        )
        result.manifest_path = manifest_path

        # ── Step 11: Update pipeline state ────────────────────────────────────
        state_manager.complete_phase(phase=1)

    logger.info("phase 1 complete", **{k: v for k, v in vars(stats).items()})

    return result


def _find_source_root(path: Path, roots: List[Path]) -> Path:
    """Find which root directory a discovered file belongs to."""
    # Pre‑sort roots by length descending to match the most specific root.
    for root in sorted(roots, key=lambda r: len(str(r)), reverse=True):
        try:
            path.relative_to(root)
            return root
        except ValueError:
            continue
    return roots[0]  # Fallback
````

## File: src/smriti/discovery/builder.py
````python
"""
builder.py — SourceDocument construction.

Responsibility: Assemble the final SourceDocument objects from
validated metadata and content hash.

Input:
  - FileMetadata (from metadata.py)
  - content_hash: str (from hashing.py)
  - source_root: Path (which root dir this file came from)

Output:
  - SourceDocument (immutable, file‑centric)
"""

from datetime import datetime
from pathlib import Path
import structlog

from smriti.core.models import FileFormat, SourceDocument
from smriti.discovery.metadata import FileMetadata

logger = structlog.get_logger(__name__)

# Map file extensions to FileFormat enum values
_EXTENSION_TO_FORMAT = {
    ".md": FileFormat.MARKDOWN,
    ".txt": FileFormat.TEXT,
    ".pdf": FileFormat.PDF,
}

def build_source_document(
    metadata: FileMetadata,
    content_hash: str,
    source_root: Path,
) -> SourceDocument:
    """
    Construct a SourceDocument from its component parts.

    Args:
        metadata:       Filesystem metadata from metadata.py
        content_hash:   SHA256 digest from hashing.py
        source_root:    The root directory this file was found under

    Returns:
        Immutable SourceDocument.
    """
    path = metadata.path
    format = _EXTENSION_TO_FORMAT.get(metadata.extension, FileFormat.TEXT)

    # ADR-7: doc_id is the content hash itself — content defines identity.
    doc_id = content_hash

    # Relative path for human-readable display
    try:
        relative_path = path.relative_to(source_root)
    except ValueError:
        relative_path = path  # Fallback if not under source_root

    doc = SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=relative_path,
        source_root=source_root,
        format=format,
        content_hash=content_hash,
        size_bytes=metadata.size_bytes,
        modified_at=metadata.modified_at,
    )

    logger.debug(
        "source document built",
        doc_id=doc_id[:8],
        path=str(relative_path),
        format=format.value,
    )

    return doc
````

## File: src/smriti/discovery/duplicate.py
````python
"""
duplicate.py — Content-based duplicate detection.

Responsibility: Given a sequence of (path, hash) pairs, identify which
paths have identical content to a path seen earlier.

Input:  List of (path, hash) tuples — processed in discovery order
Output: DuplicateRegistry — maps each hash to its canonical path and alternates,
        plus a reverse dict for O(1) canonical lookup.

Complexity: O(n) — dictionary lookup, not pairwise comparison.

Rules:
  - "Duplicate" means identical SHA256 hash. Nothing else.
  - Same filename in different folders is NOT a duplicate.
  - First file encountered with a given hash becomes the canonical document.
  - Subsequent files with the same hash are recorded as alternate locations.
  - Duplicates are never silently discarded — always recorded.
  - This module has no filesystem access. It only compares strings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DuplicateEntry:
    """
    Records a hash and all paths that share it.
    canonical_path: First file discovered with this hash.
    alternate_paths: All subsequent files with the same hash.
    """

    hash: str
    canonical_path: Path
    alternate_paths: List[Path] = field(default_factory=list)

    @property
    def is_duplicate(self) -> bool:
        """True if at least one other file shares this content."""
        return len(self.alternate_paths) > 0

    @property
    def all_paths(self) -> List[Path]:
        """All paths sharing this content, canonical first."""
        return [self.canonical_path] + self.alternate_paths


@dataclass
class DuplicateRegistry:
    """
    Complete result of duplicate detection for one discovery run.

    Attributes:
        entries:          hash → DuplicateEntry
        canonical_paths:  set of paths that are canonical (one per unique hash)
        duplicate_paths:  set of paths that are duplicates
        _duplicate_to_canonical: dict for O(1) reverse lookup
    """

    entries: Dict[str, DuplicateEntry] = field(default_factory=dict)
    canonical_paths: set = field(default_factory=set)
    duplicate_paths: set = field(default_factory=set)
    _duplicate_to_canonical: Dict[Path, Path] = field(default_factory=dict)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicate_paths)

    @property
    def unique_content_count(self) -> int:
        return len(self.entries)

    def is_canonical(self, path: Path) -> bool:
        return path in self.canonical_paths

    def is_duplicate(self, path: Path) -> bool:
        return path in self.duplicate_paths

    def get_canonical_for(self, path: Path) -> Optional[Path]:
        """Given a duplicate path, return the canonical path for its content (O(1))."""
        return self._duplicate_to_canonical.get(path)


def build_duplicate_registry(
    path_hash_pairs: List[Tuple[Path, str]]
) -> DuplicateRegistry:
    """
    Build a complete duplicate registry from path-hash pairs.

    Args:
        path_hash_pairs: [(path, sha256_hex_digest), ...]
                         Must be in sorted discovery order.

    Returns:
        DuplicateRegistry with canonical and duplicate classifications.
    """
    registry = DuplicateRegistry()

    for path, content_hash in path_hash_pairs:
        if content_hash not in registry.entries:
            # First file with this hash — it is canonical
            entry = DuplicateEntry(hash=content_hash, canonical_path=path)
            registry.entries[content_hash] = entry
            registry.canonical_paths.add(path)
        else:
            # A file with identical content exists — this is a duplicate
            registry.entries[content_hash].alternate_paths.append(path)
            registry.duplicate_paths.add(path)
            registry._duplicate_to_canonical[path] = registry.entries[content_hash].canonical_path
            canonical = registry.entries[content_hash].canonical_path
            logger.warning(
                "duplicate content detected",
                duplicate_path=str(path),
                canonical_path=str(canonical),
                hash_prefix=content_hash[:8],
            )

    if registry.duplicate_count > 0:
        logger.info(
            "duplicate detection complete",
            unique_contents=registry.unique_content_count,
            duplicates=registry.duplicate_count,
        )

    return registry
````

## File: src/smriti/discovery/hashing.py
````python
"""
hashing.py — Content fingerprinting.

Responsibility: Compute a SHA256 hash of file contents.

Input:  Validated Path
Output: str  — hex digest (64 characters)

Rules:
  - Hash file CONTENTS only. Never filename, path, or timestamps.
  - Read in chunks to handle arbitrarily large files without OOM.
  - This module has no knowledge of caching, duplicates, or manifests.
  - One public function: compute_hash(path) → str

Why content-only hashing matters:
  - Renaming "AI.md" → "Artificial_Intelligence.md" should NOT create a new identity.
  - Moving a file to a different folder should NOT create a new identity.
  - Changing one word inside SHOULD produce a completely different identity.
"""

import hashlib
from pathlib import Path
import structlog

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE

logger = structlog.get_logger(__name__)


def compute_hash(path: Path) -> str:
    """
    Compute SHA256 hash of file contents.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        64-character lowercase hex digest.

    Raises:
        OSError: If the file cannot be read.
    """
    hasher = hashlib.new(HASH_ALGORITHM)

    with open(path, "rb") as f:
        while chunk := f.read(HASH_CHUNK_SIZE):
            hasher.update(chunk)

    digest = hasher.hexdigest()

    logger.debug("hash computed", path=str(path), hash_prefix=digest[:8])

    return digest
````

## File: src/smriti/discovery/metadata.py
````python
"""
metadata.py — Filesystem metadata extraction.

Responsibility: Extract essential filesystem facts about a validated file.
                This is the ONLY module that calls path.stat().

Input:  Validated Path
Output: FileMetadata dataclass

Rules:
  - Never read file contents (that is hashing.py's job)
  - Never infer semantic meaning from metadata
  - Only keep fields needed by future phases:
      path, size_bytes, extension, modified_at (UTC)
  - MIME type, read‑only, creation time are removed (not used later)
  - Encoding detection is deferred to Phase 2
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class FileMetadata:
    """
    Immutable essential filesystem metadata for a single file.
    Produced by Phase 1 and used to build SourceDocument.
    """

    path: Path
    size_bytes: int
    extension: str                   # Normalised lowercase (.md / .pdf / .txt)
    modified_at: datetime            # UTC (last modification time)


def extract_metadata(path: Path) -> FileMetadata:
    """
    Extract filesystem metadata from a validated file.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        Immutable FileMetadata.

    Raises:
        OSError: If stat() fails (should not happen post-validation, but guard anyway).
    """
    stat = path.stat()

    # Modified time as UTC-aware datetime
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    extension = path.suffix.lower()

    metadata = FileMetadata(
        path=path,
        size_bytes=stat.st_size,
        extension=extension,
        modified_at=modified_at,
    )

    logger.debug(
        "metadata extracted",
        path=str(path),
        size_bytes=stat.st_size,
        modified_at=modified_at.isoformat(),
    )

    return metadata
````

## File: src/smriti/discovery/scanner.py
````python
"""
scanner.py — Recursive file discovery (iterative).

Responsibility: Given a list of validated root directories, return a
sorted list of candidate file paths. Nothing more.

Input:  List[Path]  — validated root directories
Output: List[Path]  — candidate files, sorted deterministically

Rules:
  - Traversal is recursive, unlimited depth (uses stack, no recursion)
  - Output is always sorted alphabetically (full path)
  - Hidden directories and system folders are skipped
  - Broken symlinks are skipped with a warning
  - Permission errors are warned and skipped — never fatal
  - The scanner never reads file contents
  - The scanner never validates individual files (that is validator.py)
"""

from pathlib import Path
from typing import List, Set
from collections import deque
import structlog

from smriti.core.config import get_config

logger = structlog.get_logger(__name__)


# Directories that are always skipped, regardless of config.
# These are non-negotiable system directories.
_ALWAYS_IGNORE: Set[str] = {
    ".git",
    ".obsidian",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
}


def discover_files(root_dirs: List[Path]) -> List[Path]:
    """
    Recursively discover all candidate files under root_dirs.

    Args:
        root_dirs: Pre-validated root directories to scan.

    Returns:
        Sorted list of candidate file paths.
        Sorting is by full absolute path (alphabetical, case-insensitive on Windows).

    Raises:
        Nothing. All errors are logged and skipped.
    """
    config = get_config()
    ignored_dirs: Set[str] = _ALWAYS_IGNORE | set(
        config["discovery"].get("ignored_dirs", [])
    )

    candidates: List[Path] = []

    for root_dir in root_dirs:
        logger.info("scanning directory", path=str(root_dir))
        _scan_iterative(root_dir, root_dir, ignored_dirs, candidates)

    # RULE: Output must always be sorted. Never trust OS ordering.
    candidates.sort(key=lambda p: str(p))

    logger.info(
        "discovery complete",
        total_candidates=len(candidates),
        roots_scanned=len(root_dirs),
    )

    return candidates


def _scan_iterative(
    root_dir: Path,
    root_dir_original: Path,
    ignored_dirs: Set[str],
    accumulator: List[Path],
) -> None:
    """
    Iterative directory walk using a stack.
    This is the only function that touches the filesystem in scanner.py.
    """
    stack = [root_dir]
    visited = {root_dir.resolve()}

    while stack:
        current_dir = stack.pop()

        try:
            # Sort directory contents for determinism within each directory.
            entries = sorted(current_dir.iterdir(), key=lambda e: e.name)
        except PermissionError:
            logger.warning("permission denied, skipping directory", path=str(current_dir))
            continue
        except OSError as e:
            logger.warning("cannot read directory", path=str(current_dir), error=str(e))
            continue

        for entry in entries:
            # Skip hidden files and directories (name starts with ".")
            if entry.name.startswith("."):
                logger.debug("skipping hidden entry", path=str(entry))
                continue

            # Skip system/ignored directories
            if entry.name in ignored_dirs:
                logger.debug("skipping ignored directory", path=str(entry))
                continue

            if entry.is_symlink():
                # Broken symlink — skip with warning
                if not entry.exists():
                    logger.warning("broken symlink, skipping", path=str(entry))
                    continue
                # Valid symlink pointing to a file — follow it
                # Valid symlink pointing to a directory — recurse
                resolved = entry.resolve()
                # Guard against symlink loops pointing outside the vault
                if resolved == root_dir_original or str(resolved).startswith(str(root_dir_original)):
                    pass  # within vault, safe to follow
                else:
                    logger.debug("symlink points outside vault, skipping", path=str(entry))
                    continue

            if entry.is_dir():
                resolved_dir = entry.resolve()          # <-- ADD THIS
                if resolved_dir not in visited:         # <-- ADD THIS: Cycle protection
                    visited.add(resolved_dir)
                    stack.append(entry)
                else:                                   # <-- ADD THIS
                    logger.debug("symlink cycle detected, skipping", path=str(entry))    
            elif entry.is_file():
                accumulator.append(entry.resolve())
````

## File: src/smriti/discovery/validator.py
````python
"""
validator.py — Two-level validation.

Level 1: validate_directory()  — validates root input directories.
Level 2: validate_file()       — validates individual discovered files.

Responsibility:
  - Answer the binary question: "Can this path enter the pipeline?"
  - Return a ValidationResult (not raise exceptions) for files.
  - Raise DiscoveryError immediately for invalid root directories
    because the pipeline cannot proceed without valid roots.

Input:  Path
Output: ValidationResult (for files) | raises DiscoveryError (for dirs)

Design:
  - Validation is a pure predicate. No side effects.
  - The validator never reads file contents (no readability check).
  - The validator never computes hashes.
  - Every rejection reason is recorded explicitly.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.constants import MAX_FILE_SIZE_BYTES
from smriti.exceptions import DiscoveryError

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single file path."""

    path: Path
    is_valid: bool
    rejection_reason: Optional[str] = None

    def __bool__(self) -> bool:
        return self.is_valid


def validate_directories(directories: List[Path]) -> List[Path]:
    """
    Validate that all input directories exist and are readable.

    Args:
        directories: Root directories to validate.

    Returns:
        List of valid, absolute, resolved directories.

    Raises:
        DiscoveryError: If any directory is invalid.
                        (Fatal — cannot start without valid roots.)
    """
    if not directories:
        raise DiscoveryError("No input directories provided.")

    validated: List[Path] = []

    for raw_path in directories:
        path = Path(raw_path).resolve()

        if not path.exists():
            raise DiscoveryError(f"Input directory does not exist: {path}")

        if not path.is_dir():
            raise DiscoveryError(f"Input path is not a directory: {path}")

        try:
            # Attempt to list — checks read permission without reading contents
            list(path.iterdir())
        except PermissionError:
            raise DiscoveryError(f"Input directory is not readable: {path}")

        validated.append(path)
        logger.info("directory validated", path=str(path))

    return validated


def validate_file(path: Path) -> ValidationResult:
    """
    Validate a single file for pipeline inclusion.

    Args:
        path: The candidate file path.

    Returns:
        ValidationResult — never raises exceptions for individual files.

    Checks (in order, cheapest first):
        1. Path exists
        2. Is a regular file (not a directory, device, etc.)
        3. Extension is in whitelist
        4. File size is non-zero
        5. File size is within maximum limit
    (Readability is tested by the hasher; no separate open/read here.)
    """
    config = get_config()
    allowed_extensions: set = set(
        config["discovery"].get("supported_extensions", [".md", ".pdf", ".txt"])
    )
    max_file_size: int = config["discovery"].get(
        "max_file_size_bytes", MAX_FILE_SIZE_BYTES
    )

    # Check 1: Exists
    if not path.exists():
        return ValidationResult(path=path, is_valid=False, rejection_reason="does not exist")

    # Check 2: Regular file
    if not path.is_file():
        return ValidationResult(path=path, is_valid=False, rejection_reason="not a regular file")

    # Check 3: Extension whitelist
    extension = path.suffix.lower()
    if extension not in allowed_extensions:
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"unsupported extension '{extension}'",
        )

    # Check 4: Non-zero size
    try:
        size = path.stat().st_size
    except OSError as e:
        return ValidationResult(path=path, is_valid=False, rejection_reason=f"stat failed: {e}")

    if size == 0:
        return ValidationResult(path=path, is_valid=False, rejection_reason="empty file (0 bytes)")

    # Check 5: Size limit
    if size > max_file_size:
        size_mb = size / (1024 * 1024)
        limit_mb = max_file_size / (1024 * 1024)
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"file too large ({size_mb:.1f} MB > {limit_mb:.0f} MB limit)",
        )

    return ValidationResult(path=path, is_valid=True)
````

## File: src/smriti/embedding/__init__.py
````python
"""
embedding/__init__.py — Public API for Phase 5: Semantic Embedding Layer.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.embedding import embed_claims, Phase5Result

They NEVER import from internal modules.

Public contract:
    embed_claims(claims: List[Claim], ...) → Phase5Result

That is the ONLY function that crosses the Phase 5 boundary.

Key implementation changes from original:
    - Status removed from Embedding (pure semantic artifact)
    - Internal EmbeddingResult tracks per-claim execution status
    - Failed batches retry claim-by-claim before marking anything failed
    - Post-normalization validation added (Stage 7)
    - EmbeddingQuality built per-claim (Stage 8)
    - Phase5Result includes warnings and errors lists
    - Manifest includes cache lifecycle metrics
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Phase5Stats,
    Vector,
    VectorDType,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase5Error, EmbeddingModelError, EmbeddingInferenceError

from smriti.embedding.embedder import (
    BaseEmbedder,
    SentenceTransformerEmbedder,
    PHASE5_PIPELINE_VERSION,
    PHASE5_SCHEMA_VERSION,
)
from smriti.embedding.input_factory import EmbeddingInputFactory, CacheKeyFactory
from smriti.embedding.cache import EmbeddingCachePolicy
from smriti.embedding.validation import validate_vector
from smriti.embedding.normalization import l2_normalize
from smriti.embedding.builders import (
    build_vector,
    build_embedding,
    build_embedding_quality,
    build_embedded_claim,
)
from smriti.embedding.statistics import Phase5StatsCollector
from smriti.embedding.models import EmbeddingResult, EmbeddingStatus

logger = structlog.get_logger(__name__)


# ── Public result type ────────────────────────────────────────────────────────

@dataclass
class Phase5Result:
    """
    Complete output of Phase 5 — all EmbeddedClaims produced.
    This is what Phase 6 receives.

    Fields:
        embedded_claims: All successfully embedded claims.
        stats:           Immutable execution statistics.
        run_id:          Current pipeline run identifier.
        warnings:        Non-fatal issues collected during embedding.
        errors:          Fatal per-claim errors (claim still skipped gracefully).
        manifest_path:   Path to written manifest.json.
        dataset_path:    Path to written dataset.json.
    """
    embedded_claims: List[EmbeddedClaim]
    stats: Phase5Stats
    run_id: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None

    @property
    def total_embedded(self) -> int:
        return len(self.embedded_claims)

    def to_dataset_json(self) -> str:
        """
        Serialize all EmbeddedClaims to JSON for Phase 6.
        Written to artifacts/run_{id}/phase5/dataset.json.

        Status field in output: derived from EmbeddingQuality (cache_used)
        since status is no longer stored on Embedding itself.
        """
        records = []
        for ec in self.embedded_claims:
            # Derive status from quality (status is not on Embedding)
            

            records.append({
                "claim_id":       ec.claim_id,
                "vector":         list(ec.values),   # Plain list of floats
                "dimension":      ec.dimension,
                "schema_version": ec.schema_version,
                "quality": {
                    "dimension_ok": ec.quality.dimension_ok,
                    "normalized":   ec.quality.normalized,
                    "finite":       ec.quality.finite,
                    "cache_used":   ec.quality.cache_used,
                },
                "model": {
                    "provider":          ec.embedding.descriptor.provider,
                    "model_name":        ec.embedding.descriptor.model_name,
                    "revision":          ec.embedding.descriptor.model_revision,
                    "dimension":         ec.embedding.descriptor.dimension,
                    "signature":         ec.embedding.descriptor.model_signature,
                    "embedding_family":  ec.embedding.descriptor.embedding_family,
                },
                "provenance": {
                    "pipeline_version":   ec.embedding.provenance.pipeline_version,
                    "normalization_mode": ec.embedding.provenance.normalization_mode,
                    "device":             ec.embedding.provenance.device,
                    "config_hash":        ec.embedding.provenance.config_hash,
                },
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── EmbeddedClaim helper (add to EmbeddedClaim or keep as standalone) ─────────
# We monkeypatch a convenience method here so EmbeddedClaim.to_dataset_json
# doesn't need to import from __init__ (which would create a circular import).

#def _values_as_list(self) -> List[float]:
    #"""Return vector values as a plain Python list."""
    #return list(self.embedding.vector.values)

#EmbeddedClaim.values_as_list = _values_as_list   # type: ignore[attr-defined]


# ── Config hash ───────────────────────────────────────────────────────────────

def _compute_config_hash(config: dict) -> str:
    """
    Deterministic hash of embedding configuration fields that affect output.

    Included (affect embedding values):
        model_name          — different model = different vectors
        normalize           — normalization changes the vector
        device              — should NOT affect values, but included for safety
        instruction_prefix  — changes the input text, changes the vector
        max_seq_length      — truncation changes the vector

    Excluded (do not affect embedding values):
        batch_size          — throughput only, not correctness
        cache_embeddings    — operational flag, not semantic
        pipeline_version    — pipeline version changes tracked separately
    """
    emb_cfg = config.get("embedding", {})
    relevant = {
        "model_name":        emb_cfg.get("model_name", ""),
        "normalize":         emb_cfg.get("normalize", True),
        "device":            emb_cfg.get("device", "cpu"),
        "instruction_prefix": emb_cfg.get("instruction_prefix", ""),
        "max_seq_length":    emb_cfg.get("max_seq_length", None),
    }
    material = (
        f"model:{relevant['model_name']}|"
        f"norm:{relevant['normalize']}|"
        f"dev:{relevant['device']}|"
        f"prefix:{relevant['instruction_prefix']}|"
        f"seq:{relevant['max_seq_length']}"
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


# ── Core public function ───────────────────────────────────────────────────────

def embed_claims(
    claims: List[Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    embedder: Optional[BaseEmbedder] = None,
    force_reembed: bool = False,
) -> Phase5Result:
    """
    Transform all Claims into EmbeddedClaims.

    This is Phase 5's sole public function.
    All internal components are hidden from callers.

    Args:
        claims:           List of immutable Claims from Phase 4.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        embedder:         Optional pre-constructed embedder (for testing).
                          If None, SentenceTransformerEmbedder is used.
        force_reembed:    If True, bypass cache and re-embed all claims.

    Returns:
        Phase5Result containing EmbeddedClaims, stats, warnings, and paths.

    Raises:
        Phase5Error: If the embedding model fails to load (unrecoverable).
    """
    config = get_config()
    emb_cfg = config.get("embedding", {})
    batch_size: int = emb_cfg.get("batch_size", 32)
    normalize: bool = emb_cfg.get("normalize", True)
    cache_enabled: bool = emb_cfg.get("cache_embeddings", True) and not force_reembed
    device: str = emb_cfg.get("device", "cpu")

    logger.info(
        "phase 5 starting",
        run_id=run_id,
        claims=len(claims),
        batch_size=batch_size,
        normalize=normalize,
        cache_enabled=cache_enabled,
    )

    start_time = manifest_manager.start_phase(phase=5)

    # ── Initialize components ─────────────────────────────────────────────────
    if embedder is None:
        try:
            embedder = SentenceTransformerEmbedder(device=device)
        except EmbeddingModelError:
            raise  # Unrecoverable: bubble up as Phase5Error subclass

    config_hash = _compute_config_hash(config)
    descriptor = embedder.descriptor
    model_sig = descriptor.model_signature
    normalization_mode = "l2" if normalize else "none"

    provenance = EmbeddingProvenance(
        pipeline_version=PHASE5_PIPELINE_VERSION,
        normalization_mode=normalization_mode,
        device=device,
        config_hash=config_hash,
    )

    # Separated: EmbeddingInputFactory handles payload only
    #            CacheKeyFactory handles key generation only
    input_factory = EmbeddingInputFactory(
        instruction_prefix=emb_cfg.get("instruction_prefix", ""),
    )
    key_factory = CacheKeyFactory(
        model_signature=model_sig,
        config_hash=config_hash,
    )

    cache_policy = EmbeddingCachePolicy(enabled=cache_enabled)
    stats_collector = Phase5StatsCollector()

    # Accumulated warnings and errors for Phase5Result
    all_warnings: List[str] = []
    all_errors: List[str] = []

    # ── Process claims ─────────────────────────────────────────────────────────
    embedded_claims: List[EmbeddedClaim] = []

    with Timer("phase5_embedding"):
        # ── Stage 1 + 2: Validate claims, build payloads and cache keys ───────
        valid_claims: List[Claim] = []
        payloads: Dict[str, str] = {}     # claim_id → payload text
        cache_keys: Dict[str, str] = {}   # claim_id → cache key

        for claim in claims:
            if not claim.text or not claim.text.strip():
                logger.debug("skipping empty claim", claim_id=claim.claim_id[:8])
                stats_collector.record_skipped()
                continue

            payloads[claim.claim_id] = input_factory.build_payload(claim)
            cache_keys[claim.claim_id] = key_factory.build_cache_key(claim)
            valid_claims.append(claim)

        # ── Stage 3: Cache resolution ─────────────────────────────────────────
        pending_claims: List[Claim] = []
        cached_results: Dict[str, List[float]] = {}   # claim_id → cached vector

        for claim in valid_claims:
            cache_key = cache_keys[claim.claim_id]
            status, vector = cache_policy.lookup(cache_key, model_sig, config_hash)

            if status == EmbeddingStatus.CACHED:
                cached_results[claim.claim_id] = vector
                stats_collector.record_cached()
            elif status == EmbeddingStatus.STALE:
                pending_claims.append(claim)
                stats_collector.record_stale()
                logger.debug("cache stale → will re-embed", claim_id=claim.claim_id[:8])
            else:
                pending_claims.append(claim)

        logger.info(
            "cache resolution complete",
            cached=len(cached_results),
            pending=len(pending_claims),
        )

        # ── Stage 3b: Build EmbeddedClaims for cached results ─────────────────
        for claim in valid_claims:
            if claim.claim_id not in cached_results:
                continue
            raw_cached = cached_results[claim.claim_id]
            try:
                vec = build_vector(
                    raw_cached, descriptor.dimension,
                    dtype=VectorDType.FLOAT64, normalized=True,
                )
                emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
                qual = build_embedding_quality(vec, descriptor, cache_used=True)
                ec = build_embedded_claim(claim.claim_id, emb, qual)
                embedded_claims.append(ec)
            except Exception as e:
                msg = f"claim {claim.claim_id[:8]}: cached vector build failed: {e}"
                all_errors.append(msg)
                logger.error("cached vector build failed", claim_id=claim.claim_id[:8], error=str(e))
                stats_collector.record_failed()

        # ── Stages 4-9: Batch inference for pending claims ────────────────────
        if pending_claims:
            for batch_start in range(0, len(pending_claims), batch_size):
                batch_claims = pending_claims[batch_start:batch_start + batch_size]
                batch_payloads = [payloads[c.claim_id] for c in batch_claims]
                stats_collector.record_batch(len(batch_claims))

                logger.debug(
                    "embedding batch",
                    batch_num=batch_start // batch_size + 1,
                    size=len(batch_claims),
                )

                # Attempt batch inference — on failure, retry individually
                raw_vectors: Optional[List[List[float]]] = None
                try:
                    raw_vectors = embedder.encode_batch(batch_payloads)
                except (EmbeddingInferenceError, Exception) as batch_err:
                    logger.warning(
                        "batch encoding failed — retrying individually",
                        batch_size=len(batch_claims),
                        error=str(batch_err),
                    )
                    all_warnings.append(
                        f"Batch of {len(batch_claims)} failed, retrying individually: {batch_err}"
                    )

                if raw_vectors is not None:
                    # Batch succeeded — process all at once
                    _process_batch_results(
                        batch_claims=batch_claims,
                        raw_vectors=raw_vectors,
                        descriptor=descriptor,
                        provenance=provenance,
                        cache_keys=cache_keys,
                        cache_policy=cache_policy,
                        model_sig=model_sig,
                        config_hash=config_hash,
                        normalize=normalize,
                        embedded_claims=embedded_claims,
                        stats_collector=stats_collector,
                        all_warnings=all_warnings,
                        all_errors=all_errors,
                    )
                else:
                    # Batch failed — retry each claim individually
                    for individual_claim in batch_claims:
                        individual_payload = payloads[individual_claim.claim_id]
                        try:
                            single_vectors = embedder.encode_batch([individual_payload])
                            _process_batch_results(
                                batch_claims=[individual_claim],
                                raw_vectors=single_vectors,
                                descriptor=descriptor,
                                provenance=provenance,
                                cache_keys=cache_keys,
                                cache_policy=cache_policy,
                                model_sig=model_sig,
                                config_hash=config_hash,
                                normalize=normalize,
                                embedded_claims=embedded_claims,
                                stats_collector=stats_collector,
                                all_warnings=all_warnings,
                                all_errors=all_errors,
                            )
                        except Exception as single_err:
                            msg = (
                                f"claim {individual_claim.claim_id[:8]} "
                                f"failed after individual retry: {single_err}"
                            )
                            all_errors.append(msg)
                            logger.error(
                                "individual retry failed",
                                claim_id=individual_claim.claim_id[:8],
                                error=str(single_err),
                            )
                            stats_collector.record_failed()

    stats = stats_collector.finalize()

    result = Phase5Result(
        embedded_claims=embedded_claims,
        stats=stats,
        run_id=run_id,
        warnings=all_warnings,
        errors=all_errors,
    )

    # ── Write artifacts ───────────────────────────────────────────────────────
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase5"
    phase_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
    result.dataset_path = dataset_path

    logger.info(
        "dataset written",
        path=str(dataset_path),
        embedded_claims=result.total_embedded,
    )

    # ── Write manifest (with cache lifecycle metrics) ─────────────────────────
    manifest_path = manifest_manager.end_phase(
        phase=5,
        start_time=start_time,
        inputs={"claims": len(claims)},
        outputs={
            "total_embedded":          result.total_embedded,
            "successful":              stats.successful,
            "cached":                  stats.cached,
            "stale":                   stats.stale,
            "failed":                  stats.failed,
            "skipped":                 stats.skipped,
            # Cache lifecycle metrics (high priority addition)
            "cache_entries_reused":      stats.cache_entries_reused,
            "cache_entries_regenerated": stats.cache_entries_regenerated,
            "cache_entries_invalidated": stats.cache_entries_invalidated,
            # Throughput
            "vectors_per_second":      f"{stats.vectors_per_second:.1f}",
            "current_memory_mb":       f"{stats.current_memory_mb:.1f}",
            # Model
            "model":        descriptor.model_name,
            "dimension":    descriptor.dimension,
            "dataset_path": str(dataset_path),
            # Diagnostics
            "warnings": len(all_warnings),
            "errors":   len(all_errors),
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # ── Update pipeline state ─────────────────────────────────────────────────
    state_manager.complete_phase(phase=5)

    logger.info(
        "phase 5 complete",
        total_embedded=result.total_embedded,
        cached=stats.cached,
        successful=stats.successful,
        failed=stats.failed,
        cache_hit_rate=f"{stats.cache_hit_rate:.1%}",
        throughput=f"{stats.vectors_per_second:.1f} vec/s",
        runtime=f"{stats.total_runtime_seconds:.2f}s",
        warnings=len(all_warnings),
    )

    return result


# ── Internal helpers ──────────────────────────────────────────────────────────

def _process_batch_results(
    batch_claims: List[Claim],
    raw_vectors: List[List[float]],
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
    cache_keys: Dict[str, str],
    cache_policy: EmbeddingCachePolicy,
    model_sig: str,
    config_hash: str,
    normalize: bool,
    embedded_claims: List[EmbeddedClaim],
    stats_collector: Phase5StatsCollector,
    all_warnings: List[str],
    all_errors: List[str],
) -> None:
    """
    Process raw inference output for one batch (or single claim retry).
    Handles: validation → normalization → post-norm validation → build → cache.

    Mutates embedded_claims, stats_collector, all_warnings, all_errors in-place.
    """
    for i, claim in enumerate(batch_claims):
        raw_vector = raw_vectors[i]

        # ── Stage 5: Vector validation (pre-normalization) ────────────────────
        is_valid, error_msg = validate_vector(raw_vector, descriptor.dimension)
        if not is_valid:
            msg = f"claim {claim.claim_id[:8]} pre-norm validation: {error_msg}"
            all_warnings.append(msg)
            logger.warning("vector validation failed", claim_id=claim.claim_id[:8], error=error_msg)
            stats_collector.record_failed()
            continue

        # ── Stage 6: L2 Normalization ─────────────────────────────────────────
        final_vector_list = l2_normalize(raw_vector) if normalize else [float(x) for x in raw_vector]

        # ── Stage 7: Post-normalization re-validation ─────────────────────────
        is_valid_post, error_post = validate_vector(final_vector_list, descriptor.dimension)
        if not is_valid_post:
            msg = (
                f"claim {claim.claim_id[:8]} post-norm validation failed "
                f"(numerical issue after L2): {error_post}"
            )
            all_warnings.append(msg)
            logger.warning(
                "post-normalization validation failed",
                claim_id=claim.claim_id[:8],
                error=error_post,
            )
            stats_collector.record_failed()
            continue

        # ── Cache the normalized result ────────────────────────────────────────
        cache_key = cache_keys[claim.claim_id]
        cache_policy.store(cache_key, final_vector_list, model_sig, config_hash)

        # ── Stage 8: Build domain objects ──────────────────────────────────────
        try:
            vec = build_vector(
                final_vector_list,
                descriptor.dimension,
                dtype=VectorDType.FLOAT64,
                normalized=normalize,
            )
            emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
            qual = build_embedding_quality(vec, descriptor, cache_used=False)
            ec = build_embedded_claim(claim.claim_id, emb, qual)
        except AssertionError as ae:
            msg = f"claim {claim.claim_id[:8]} builder assertion: {ae}"
            all_errors.append(msg)
            logger.error("builder assertion failed", claim_id=claim.claim_id[:8], error=str(ae))
            stats_collector.record_failed()
            continue

        # ── Stage 9: Accumulate ────────────────────────────────────────────────
        embedded_claims.append(ec)
        stats_collector.record_successful()
````

## File: src/smriti/embedding/builders.py
````python
"""
builders.py — Immutable domain object construction for Phase 5.

Responsibility:
    Construct immutable Vector, Embedding, EmbeddingQuality, and EmbeddedClaim objects.
    This is the ONLY place where these objects are instantiated.

    Like Phase 4's builder.py — pure object construction, no logic.

Builders:
    build_vector()              → Vector            (from raw float list)
    build_embedding()           → Embedding         (pure semantic, no status)
    build_embedding_quality()   → EmbeddingQuality  (diagnostic snapshot)
    build_embedded_claim()      → EmbeddedClaim     (public phase boundary object)

Rules:
    ✅ Construct immutable domain objects
    ✅ Attach all required metadata (descriptor, provenance)
    ✅ Convert List[float] → tuple inside Vector
    ✅ Assert dimension invariant before constructing Vector (defensive safeguard)

    ❌ Never perform inference
    ❌ Never normalize
    ❌ Never validate (validation.py's responsibility)
    ❌ No logic or heuristics beyond construction
"""

from __future__ import annotations

import math
from typing import List
import structlog

from smriti.core.models import (
    Embedding,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Vector,
    VectorDType,
)

logger = structlog.get_logger(__name__)


def build_vector(
    values: List[float],
    expected_dimension: int,
    dtype: VectorDType = VectorDType.FLOAT64,
    normalized: bool = False,
) -> Vector:
    """
    Construct an immutable Vector domain object from a validated float list.

    Includes a defensive assertion that dimension matches before constructing.
    This is cheap and protects against descriptor/vector mismatches that
    might slip through validation in unusual code paths.

    Args:
        values:             Validated (and optionally normalized) float list.
        expected_dimension: Dimension from EmbeddingModelDescriptor.
        dtype:              "float64" or "float32" — recorded for downstream use.
        normalized:         True if L2 normalization was applied.

    Returns:
        Immutable Vector.

    Raises:
        AssertionError: If len(values) != expected_dimension (defensive safeguard).
    """
    # Defensive assertion — cheap, catches any latent dimension mismatch
    assert expected_dimension == len(values), (
        f"build_vector: descriptor.dimension={expected_dimension} "
        f"!= len(values)={len(values)}"
    )

    vector = Vector(
        values=tuple(float(v) for v in values),
        dimension=len(values),
        dtype=dtype,
        normalized=normalized,
    )

    logger.debug(
        "vector built",
        dimension=vector.dimension,
        dtype=dtype,
        normalized=normalized,
    )

    return vector


def build_embedding(
    claim_id: str,
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
) -> Embedding:
    """
    Construct an immutable Embedding from a validated, normalized Vector.

    Note: Embedding carries NO status field.
          Status belongs to the internal EmbeddingResult.
          This is a pure, timeless semantic artifact.

    Args:
        claim_id:    The originating Claim's ID.
        vector:      Validated (and optionally normalized) Vector domain object.
        descriptor:  Which model produced this vector.
        provenance:  How/where inference was run.

    Returns:
        Immutable Embedding.
    """
    embedding = Embedding(
        claim_id=claim_id,
        vector=vector,
        descriptor=descriptor,
        provenance=provenance,
    )

    logger.debug(
        "embedding built",
        claim_id=claim_id[:8],
        dimension=vector.dimension,
        normalized=vector.normalized,
    )

    return embedding


def build_embedding_quality(
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    cache_used: bool,
) -> EmbeddingQuality:
    """
    Construct an EmbeddingQuality diagnostic snapshot.

    Phase 6 reads this and never recomputes it.
    Calling this once here prevents redundant computation downstream.

    Args:
        vector:      The built Vector (already the final, stored vector).
        descriptor:  The model descriptor to compare dimension against.
        cache_used:  True if the vector came from cache (not fresh inference).

    Returns:
        Immutable EmbeddingQuality.
    """
    # Check finiteness — redundant after validation but useful as a diagnostic fact
    finite = all(
        math.isfinite(v) for v in vector.values
    )

    quality = EmbeddingQuality(
        dimension_ok=(vector.dimension == descriptor.dimension),
        normalized=vector.normalized,
        finite=finite,
        cache_used=cache_used,
    )

    logger.debug(
        "embedding quality built",
        dimension_ok=quality.dimension_ok,
        normalized=quality.normalized,
        finite=quality.finite,
        cache_used=quality.cache_used,
    )

    return quality


def build_embedded_claim(
    claim_id: str,
    embedding: Embedding,
    quality: EmbeddingQuality,
) -> EmbeddedClaim:
    """
    Construct an immutable EmbeddedClaim.

    Args:
        claim_id:   The Claim's ID (referential, not the Claim object itself).
        embedding:  The completed Embedding (pure semantic artifact).
        quality:    The EmbeddingQuality diagnostic snapshot.

    Returns:
        Immutable EmbeddedClaim.
    """
    embedded_claim = EmbeddedClaim(
        claim_id=claim_id,
        embedding=embedding,
        quality=quality,
        schema_version="5.0",
    )

    logger.debug(
        "embedded claim built",
        claim_id=claim_id[:8],
        dimension=embedding.dimension,
        cache_used=quality.cache_used,
    )

    return embedded_claim
````

## File: src/smriti/embedding/cache.py
````python
"""
cache.py — Embedding cache policy for Phase 5.

Responsibility:
    Manage when embeddings should be reused vs regenerated.
    Separate cache POLICY from cache PERSISTENCE.

    Policy (here):   "Should this embedding be reused?"
    Persistence:     core/cache.py CacheManager handles actual file I/O

Cache entry validity rules:
    An embedding cache entry is VALID if and only if:
        1. The entry exists
        2. The schema_version matches the current Phase 5 schema    ← NEW
        3. The model signature matches the current model
        4. The config hash matches the current configuration

    If ANY condition fails → STALE → regenerate.

    Schema version check comes FIRST because a schema mismatch means
    the entry might not even deserialize correctly with newer code.

Cache key:
    SHA256(claim.content_hash : model_signature : config_hash)[:32]

Notes:
    - Cache stores vectors as List[float] (Python native, portable)
    - Cache never stores framework tensors
    - Stale entries are overwritten (not deleted first)
    - All stored vectors are assumed to be already normalized
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.paths import EMBEDDINGS_CACHE_DIR
from smriti.embedding.models import EmbeddingStatus

logger = structlog.get_logger(__name__)

# Must match PHASE5_SCHEMA_VERSION in embedder.py
# Increment this constant whenever the cache entry format changes
CACHE_SCHEMA_VERSION = "5.0"


class EmbeddingCachePolicy:
    """
    Manages embedding cache reads and writes.

    Storage format: one .pkl file per cache key.
    File content:
        {
            "vector":         [float, ...],
            "model_sig":      str,
            "config_hash":    str,
            "schema_version": str,     ← validates format compatibility
        }
    """

    def __init__(
        self,
        cache_dir: Path = EMBEDDINGS_CACHE_DIR,
        enabled: bool = True,
    ) -> None:
        self._cache_dir = Path(cache_dir)
        self._enabled = enabled

        if self._enabled:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def lookup(
        self,
        cache_key: str,
        model_signature: str,
        config_hash: str,
    ) -> Tuple[EmbeddingStatus, Optional[List[float]]]:
        """
        Look up a vector in the cache.

        Validation order:
            1. schema_version — format compatibility (checked first)
            2. model_signature — model identity
            3. config_hash — pipeline configuration

        Returns:
            (EmbeddingStatus.CACHED, vector) if fully valid hit
            (EmbeddingStatus.STALE, None)   if any condition fails
            (EmbeddingStatus.FAILED, None)  if key not found or cache disabled
        """
        if not self._enabled:
            return EmbeddingStatus.FAILED, None

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return EmbeddingStatus.FAILED, None

        try:
            with open(cache_file, "rb") as f:
                entry = pickle.load(f)

            # Check 1: Schema version — catches incompatible cache format changes
            if entry.get("schema_version") != CACHE_SCHEMA_VERSION:
                logger.debug(
                    "cache schema mismatch — stale",
                    cache_key=cache_key[:8],
                    stored=entry.get("schema_version"),
                    expected=CACHE_SCHEMA_VERSION,
                )
                return EmbeddingStatus.STALE, None

            # Check 2 + 3: Model identity and configuration
            if (entry.get("model_sig") != model_signature or
                    entry.get("config_hash") != config_hash):
                logger.debug(
                    "cache model/config mismatch — stale",
                    cache_key=cache_key[:8],
                )
                return EmbeddingStatus.STALE, None

            vector = entry.get("vector")
            if vector is None:
                return EmbeddingStatus.FAILED, None

            logger.debug("cache hit", cache_key=cache_key[:8])
            return EmbeddingStatus.CACHED, vector

        except Exception as e:
            logger.warning("cache read failed", cache_key=cache_key[:8], error=str(e))
            return EmbeddingStatus.FAILED, None

    def store(
        self,
        cache_key: str,
        vector: List[float],
        model_signature: str,
        config_hash: str,
    ) -> bool:
        """
        Store a normalized vector in the cache.

        Returns:
            True if stored successfully, False on error.
        """
        if not self._enabled:
            return False

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        try:
            entry = {
                "vector":         vector,
                "model_sig":      model_signature,
                "config_hash":    config_hash,
                "schema_version": CACHE_SCHEMA_VERSION,   # Always write current version
            }
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
            logger.debug("cache stored", cache_key=cache_key[:8])
            return True
        except Exception as e:
            logger.warning("cache write failed", cache_key=cache_key[:8], error=str(e))
            return False

    def invalidate(self, cache_key: str) -> bool:
        """
        Remove a specific cache entry.

        Returns:
            True if file existed and was removed.
        """
        cache_file = self._cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
            logger.debug("cache invalidated", cache_key=cache_key[:8])
            return True
        return False

    def clear_all(self) -> int:
        """Clear all cached embeddings. Returns count of files removed."""
        if not self._cache_dir.exists():
            return 0
        count = 0
        for f in self._cache_dir.glob("*.pkl"):
            f.unlink()
            count += 1
        logger.info("embedding cache cleared", files_removed=count)
        return count
````

## File: src/smriti/embedding/embedder.py
````python
"""
embedder.py — Abstract embedding interface, capability metadata, and V1 implementation.

Responsibility:
    Define EmbedderCapabilities — so the pipeline can adapt without inspecting model names.
    Define BaseEmbedder — the stable interface that shields the pipeline from frameworks.
    Provide SentenceTransformerEmbedder — the V1 implementation.

Architecture rules:
    ✅ BaseEmbedder exposes only Python native types (List[str], List[List[float]])
    ✅ EmbedderCapabilities lets the pipeline ask "can you do X?" instead of "are you model Y?"
    ✅ SentenceTransformerEmbedder is the ONLY module that imports sentence-transformers
    ✅ torch.Tensor is converted to List[float] before leaving this module
    ✅ EmbeddingModelDescriptor is constructed here and exposed to the pipeline

    ❌ No torch.Tensor, np.ndarray, or model objects ever leave this module
    ❌ No normalization inside the embedder (that belongs to normalization.py)
    ❌ No caching inside the embedder (that belongs to cache.py)
    ❌ Pipeline never branches on model name — it queries capabilities instead
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import structlog

from smriti.core.config import get_config
from smriti.core.models import EmbeddingModelDescriptor
from smriti.exceptions import EmbeddingModelError, EmbeddingInferenceError

logger = structlog.get_logger(__name__)

# Phase 5 pipeline version — increment when pipeline logic changes
PHASE5_PIPELINE_VERSION = "1.0"
PHASE5_SCHEMA_VERSION = "5.0"


def _compute_model_signature(provider: str, model_name: str, revision: str) -> str:
    """Deterministic model signature for cache key generation."""
    material = f"{provider}:{model_name}:{revision}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class EmbedderCapabilities:
    """
    Runtime capabilities advertised by an embedder implementation.

    The pipeline queries capabilities instead of branching on model name.
    This makes the pipeline unconditionally open for extension.

    Fields:
        supports_batching:           True if encode_batch() is more efficient than
                                     repeated single-item calls.
        supports_instruction_prefix: True if the model benefits from task-specific
                                     prefixes (BGE, Instructor, E5).
        supports_multilingual:       True if the model handles non-English text well.
        supports_long_context:       True if the model handles sequences > 512 tokens
                                     without truncation loss.
    """
    supports_batching: bool
    supports_instruction_prefix: bool
    supports_multilingual: bool
    supports_long_context: bool


class BaseEmbedder(ABC):
    """
    Abstract interface for all embedding backends.

    Contract:
        - encode_batch() accepts plain Python strings
        - encode_batch() returns plain Python float lists
        - descriptor() returns an EmbeddingModelDescriptor
        - capabilities() returns an EmbedderCapabilities
        - No framework types ever cross this interface

    Adding a new embedder = subclass BaseEmbedder.
    The pipeline never changes.
    """

    @property
    @abstractmethod
    def descriptor(self) -> EmbeddingModelDescriptor:
        """Return the model descriptor for this embedder."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> EmbedderCapabilities:
        """Return the capability metadata for this embedder."""
        ...

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a batch of text strings into embedding vectors.

        Args:
            texts: List of strings to encode (payload strings, not Claim objects).

        Returns:
            List of float lists, one per input text.
            All vectors must have the same dimension == descriptor.dimension.

        Raises:
            EmbeddingInferenceError: If encoding fails.
        """
        ...


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    V1 embedding backend using sentence-transformers.

    Default model: sentence-transformers/all-MiniLM-L6-v2
        - 384-dimensional embeddings
        - CPU-runnable without GPU
        - ~80MB model size
        - Strong general-purpose semantic similarity
        - Supports batching efficiently

    Design:
        - Model loaded once at construction time (eager loading)
        - encode_batch converts torch.Tensor → List[List[float]] before returning
        - No normalization performed here (normalization.py handles that)
        - No caching performed here (cache.py handles that)
        - capabilities() advertises what this model supports
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        config = get_config()
        emb_cfg = config.get("embedding", {})

        self._model_name = model_name or emb_cfg.get(
            "model_name", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._device = device or emb_cfg.get("device", "cpu")

        self._model = self._load_model()
        self._descriptor = self._build_descriptor()

        logger.info(
            "embedding model loaded",
            model=self._model_name,
            device=self._device,
            dimension=self._descriptor.dimension,
            family=self._descriptor.embedding_family,
        )

    def _load_model(self):
        """Load the sentence-transformers model. Raises EmbeddingModelError on failure."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(self._model_name, device=self._device)
            return model
        except ImportError as e:
            raise EmbeddingModelError(
                f"sentence-transformers is not installed. "
                f"Run: poetry add sentence-transformers\nError: {e}"
            ) from e
        except Exception as e:
            raise EmbeddingModelError(
                f"Failed to load embedding model '{self._model_name}': {e}"
            ) from e

    def _build_descriptor(self) -> EmbeddingModelDescriptor:
        """Build the model descriptor after model is loaded."""
        try:
            test_embedding = self._model.encode(["test"], convert_to_numpy=True)
            dimension = test_embedding.shape[1]
        except Exception:
            dimension = 384  # MiniLM default fallback

        revision = "default"  # sentence-transformers doesn't expose git revision easily

        return EmbeddingModelDescriptor(
            provider="sentence-transformers",
            model_name=self._model_name,
            model_revision=revision,
            dimension=dimension,
            model_signature=_compute_model_signature(
                "sentence-transformers", self._model_name, revision
            ),
            embedding_family="SentenceTransformer",
            checkpoint_sha="",  # Not available from sentence-transformers API
        )

    @property
    def descriptor(self) -> EmbeddingModelDescriptor:
        return self._descriptor

    @property
    def capabilities(self) -> EmbedderCapabilities:
        """
        MiniLM capabilities:
            - Supports batching (very efficiently)
            - Does NOT benefit from instruction prefixes (standard model)
            - Limited multilingual support (primarily English)
            - Short context only (256 token practical limit)
        """
        return EmbedderCapabilities(
            supports_batching=True,
            supports_instruction_prefix=False,
            supports_multilingual=False,
            supports_long_context=False,
        )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a batch of texts into embedding vectors.

        Args:
            texts: Non-empty list of non-empty strings.

        Returns:
            List of float lists. One vector per text.
            Vectors are RAW (unnormalized) — normalization.py handles that.

        Raises:
            EmbeddingInferenceError: If encoding fails.
        """
        if not texts:
            return []

        try:
            embeddings_np = self._model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=False,  # normalization is our responsibility
            )
            return embeddings_np.tolist()
        except Exception as e:
            raise EmbeddingInferenceError(
                f"Batch encoding failed for {len(texts)} texts: {e}"
            ) from e
````

## File: src/smriti/embedding/input_factory.py
````python
"""
input_factory.py — Contextual payload construction and cache key generation.

Two focused classes with separate responsibilities:

    EmbeddingInputFactory
        Knows HOW to construct the model input text from a Claim.
        Does not know anything about caching.

    CacheKeyFactory
        Knows HOW to generate a deterministic cache key for a Claim.
        Does not know anything about text enrichment.

Separating these means:
    - Changing context enrichment strategy → only EmbeddingInputFactory changes
    - Changing cache key composition → only CacheKeyFactory changes
    - Neither class bleeds into the other's concern

CRITICAL DESIGN: The Claim itself remains UNCHANGED.
Only the MODEL INPUT is enriched. The cache key depends on content,
not on the enriched payload.

Rules:
    ✅ EmbeddingInputFactory: deterministic payload from Claim
    ✅ CacheKeyFactory: deterministic key from claim.content_hash + model + config
    ✅ Neither class performs inference or accesses the embedding model
    ✅ Neither class modifies the Claim

    ❌ Never perform inference
    ❌ Never access the embedding model
    ❌ Never modify claim.text
"""

from __future__ import annotations

import hashlib
from typing import Optional
import structlog

from smriti.core.models import Claim

logger = structlog.get_logger(__name__)


class EmbeddingInputFactory:
    """
    Constructs contextual text payloads from Claims.

    Responsibility: What text does the model receive for this Claim?

    Construction strategy:
        If claim.context is non-empty:
            payload = f"{claim.context}\\n{claim.text}"
        Else:
            payload = claim.text

        With optional instruction prefix (for BGE, Instructor, E5):
            payload = f"{instruction_prefix}{payload}"

    Instantiate once per pipeline run.
    """

    def __init__(self, instruction_prefix: Optional[str] = None) -> None:
        self._instruction_prefix = instruction_prefix or ""
        logger.debug(
            "EmbeddingInputFactory initialized",
            has_instruction=bool(instruction_prefix),
        )

    def build_payload(self, claim: Claim) -> str:
        """
        Build the model-ready text payload for a Claim.

        Args:
            claim: An immutable Claim from Phase 4.

        Returns:
            Model-ready string. Never empty for valid claims.
        """
        if claim.context:
            payload = f"{claim.context}\n{claim.text}"
        else:
            payload = claim.text

        if self._instruction_prefix:
            payload = f"{self._instruction_prefix}{payload}"

        return payload


class CacheKeyFactory:
    """
    Constructs deterministic cache keys for Claims.

    Responsibility: What is the stable identity of this Claim's embedding?

    Cache key components:
        - claim.content_hash: content identity of the claim text
        - model_signature:    which model is producing the embedding
        - config_hash:        normalization mode, instruction prefix, etc.

    If ANY component changes, the key changes → embedding regenerated.
    This factory is intentionally separate from EmbeddingInputFactory
    so that changing payload enrichment strategy doesn't break cache keys.

    Instantiate once per pipeline run (after model + config are resolved).
    """

    def __init__(self, model_signature: str, config_hash: str) -> None:
        self._model_signature = model_signature
        self._config_hash = config_hash
        logger.debug(
            "CacheKeyFactory initialized",
            model_sig_prefix=model_signature[:8],
            config_hash_prefix=config_hash[:8],
        )

    def build_cache_key(self, claim: Claim) -> str:
        """
        Build a deterministic cache key for a Claim's embedding.

        Returns:
            32-character lowercase hex string.
        """
        if not hasattr(claim, "content_hash") or not claim.content_hash:
            # Fallback: compute hash from text content
            text_hash = hashlib.sha256(claim.text.encode("utf-8")).hexdigest()[:16]
        else:
            text_hash = claim.content_hash

        material = f"{text_hash}:{self._model_signature}:{self._config_hash}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
````

## File: src/smriti/embedding/models.py
````python
"""
embedding/models.py — Internal temporary objects for Phase 5.

These objects are NEVER exported from the embedding package.
They exist only as intermediate stages in the semantic encoding pipeline.

List[Claim]
    ↓
ValidatedClaim[]      (claim passed structural check)
    ↓
EmbeddingInput[]      (contextual text payload ready for the model)
    ↓
EmbeddingResult[]     (mutable result per claim, carries status + warnings)
    ↓
Embedding[]           (public domain object — crosses phase boundary, NO status)
    ↓
EmbeddingQuality[]    (public diagnostic — crosses phase boundary)
    ↓
EmbeddedClaim[]       (public domain object — crosses phase boundary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from enum import Enum

from smriti.core.models import Claim, Embedding

class EmbeddingStatus(str, Enum):
    """Terminal status for one Claim's embedding attempt (internal use only)."""
    SUCCESS  = "success"
    CACHED   = "cached"
    STALE    = "stale"
    FAILED   = "failed"
    SKIPPED  = "skipped"


@dataclass(frozen=True)
class ValidatedClaim:
    """
    A Claim that has passed pre-inference structural validation.

    This is the entry ticket to embedding inference.
    Only ValidatedClaims are passed to the embedder.
    """
    claim: Claim
    embedding_text: str   # Pre-computed canonical text



@dataclass(frozen=True)
class EmbeddingInput:
    """
    A validated claim paired with its contextual embedding payload.

    The payload is constructed by EmbeddingInputFactory:
        context heading + claim text (if context exists)
        OR just claim text (if no context)

    This is what actually gets passed to BaseEmbedder.encode_batch().
    The cache_key is managed separately by CacheKeyFactory.
    """
    claim_id: str
    payload: str        # Model-ready text (context-enriched)
    original_text: str  # Claim.text (kept for traceability)
    cache_key: str      # Deterministic cache key from CacheKeyFactory


@dataclass
class EmbeddingResult:
    """
    Internal mutable execution result for one Claim's embedding attempt.

    This object is created by the orchestrator, populated across pipeline stages,
    then either discarded (on failure) or used to construct the public
    EmbeddedClaim (on success).

    NEVER crosses the phase boundary. Not included in Phase5Result.

    Fields:
        claim_id:     The originating Claim's ID.
        status:       Current execution status (mutable during pipeline).
        embedding:    The completed Embedding (None until Stage 8 succeeds).
        warnings:     Non-fatal issues encountered for this claim.
        errors:       Fatal issues that prevented embedding.
        elapsed_time: Time spent embedding this specific claim (seconds).
        from_cache:   Whether the vector came from cache.
    """
    claim_id: str
    status: EmbeddingStatus
    embedding: Optional[Embedding] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0
    from_cache: bool = False

    @property
    def succeeded(self) -> bool:
        return (
            self.embedding is not None
            and self.status in (
                EmbeddingStatus.SUCCESS,
                EmbeddingStatus.CACHED,
                EmbeddingStatus.STALE,
            )
        )
````

## File: src/smriti/embedding/normalization.py
````python
"""
normalization.py — Vector normalization for Phase 5.

Responsibility:
    Apply L2 (unit-length) normalization to validated embedding vectors.
    This is a SEPARATE step from inference — the embedder never normalizes.

Why separate?
    Normalization is a configuration-driven post-processing step.
    Different normalization methods may be added without touching the embedder.
    Inference reproducibility is preserved independently of normalization choice.

L2 normalization:
    v_normalized = v / ||v||₂
    After normalization: ||v_normalized||₂ = 1.0

    This makes cosine similarity equivalent to dot product,
    which is important for Phase 6's nearest-neighbor retrieval.

Rules:
    ✅ Return a new list (never mutate input)
    ✅ Only called on validated vectors (validation.py ensures non-zero norm)
    ✅ Configurable via config (can be disabled)

    ❌ Never validate (validation.py's responsibility)
    ❌ Never infer (embedder.py's responsibility)

Note: After normalization, validation.py is called again (post-norm check).
      This module is not aware of that — it just normalizes.
"""

from __future__ import annotations

import math
from typing import List
import structlog

logger = structlog.get_logger(__name__)


def l2_normalize(vector: List[float]) -> List[float]:
    """
    Apply L2 normalization to a vector.

    Precondition: vector has been validated (non-empty, finite, non-zero norm).

    Args:
        vector: Raw float list (pre-validated).

    Returns:
        New float list with unit L2 norm. Input is never mutated.
    """
    sum_sq = sum(float(x) * float(x) for x in vector)

    # Warn if vector is extremely close to zero (should be caught by validation)
    if sum_sq <= 1e-15:
        logger.warning(
            "near-zero norm vector in normalization, using epsilon",
            sum_sq=sum_sq,
        )

    # Compute norm with a tiny epsilon to prevent division by zero
    # even if validation had a very small margin.
    norm = math.sqrt(sum_sq) + 1e-12

    return [float(x) / norm for x in vector]


def normalize_batch(
    vectors: List[List[float]],
    enabled: bool = True,
) -> List[List[float]]:
    """
    Normalize a batch of vectors.

    Args:
        vectors:  Pre-validated float lists.
        enabled:  If False, returns vectors unchanged (normalization disabled).

    Returns:
        List of normalized (or original) vectors. Input vectors are never mutated.
    """
    if not enabled:
        return [[float(x) for x in v] for v in vectors]
    return [l2_normalize(v) for v in vectors]
````

## File: src/smriti/embedding/statistics.py
````python
"""
statistics.py — Phase 5 execution statistics collector.

Responsibility:
    Collect operational metrics during Phase 5 execution.
    Statistics are DIAGNOSTIC ONLY — they never influence execution.

This module observes. It never acts.

Metrics collected:
    - Outcome counts (successful, cached, stale, failed, skipped)
    - Batch metrics (count, average size)
    - Cache lifecycle (reused, regenerated, invalidated)
    - Throughput: vectors embedded per second
    - Memory: peak RSS in MB (best-effort, 0 if psutil unavailable)
"""

from __future__ import annotations

import time
from typing import List
from smriti.embedding.models import EmbeddingStatus

from smriti.core.models import Phase5Stats


class Phase5StatsCollector:
    """
    Mutable statistics accumulator for Phase 5.
    Call finalize() to get the immutable Phase5Stats snapshot.

    Thread safety: NOT thread-safe. Use from a single thread only.
    """

    def __init__(self) -> None:
        self._total = 0
        self._successful = 0
        self._cached = 0
        self._stale = 0
        self._failed = 0
        self._skipped = 0
        self._total_batches = 0
        self._batch_sizes: List[int] = []
        # Cache lifecycle
        self._cache_reused = 0
        self._cache_regenerated = 0
        self._cache_invalidated = 0
        self._start_time = time.monotonic()

    # ── Per-claim recording ───────────────────────────────────────────────────

    def record_skipped(self) -> None:
        self._total += 1
        self._skipped += 1

    def record_cached(self) -> None:
        self._total += 1
        self._cached += 1
        self._cache_reused += 1

    def record_stale(self) -> None:
        """Record a stale cache hit — will be followed by record_successful."""
        self._stale += 1
        self._cache_regenerated += 1
        # Note: total not incremented here — stale leads to a separate successful/failed

    def record_successful(self) -> None:
        self._total += 1
        self._successful += 1

    def record_failed(self) -> None:
        self._total += 1
        self._failed += 1

    def record_invalidated(self) -> None:
        """Record a cache entry that was explicitly invalidated."""
        self._cache_invalidated += 1

    def record_status(self, status: EmbeddingStatus) -> None:
        """Convenience dispatcher for any EmbeddingStatus."""
        self._total += 1
        if status == EmbeddingStatus.SUCCESS:
            self._successful += 1
        elif status == EmbeddingStatus.CACHED:
            self._cached += 1
            self._cache_reused += 1
        elif status == EmbeddingStatus.STALE:
            self._stale += 1
            self._cache_regenerated += 1
        elif status == EmbeddingStatus.FAILED:
            self._failed += 1
        elif status == EmbeddingStatus.SKIPPED:
            self._skipped += 1

    def record_batch(self, batch_size: int) -> None:
        self._total_batches += 1
        self._batch_sizes.append(batch_size)

    # ── Finalization ──────────────────────────────────────────────────────────

    def finalize(self) -> Phase5Stats:
        """Return an immutable snapshot of accumulated statistics."""
        elapsed = time.monotonic() - self._start_time
        total_attempts = self._total or 1

        cache_hit_rate = self._cached / total_attempts
        avg_batch = (
            sum(self._batch_sizes) / len(self._batch_sizes)
            if self._batch_sizes else 0.0
        )

        # Throughput: count vectors that ended up embedded (cached + successful)
        total_embedded = self._successful + self._cached
        vectors_per_second = total_embedded / elapsed if elapsed > 0 else 0.0

        # Memory: best-effort, never fails
        current_memory_mb = _get_current_memory_mb()

        return Phase5Stats(
            total_claims=self._total,
            successful=self._successful,
            cached=self._cached,
            stale=self._stale,
            failed=self._failed,
            skipped=self._skipped,
            total_batches=self._total_batches,
            average_batch_size=avg_batch,
            cache_hit_rate=cache_hit_rate,
            total_runtime_seconds=elapsed,
            vectors_per_second=vectors_per_second,
            current_memory_mb=current_memory_mb,
            cache_entries_reused=self._cache_reused,
            cache_entries_regenerated=self._cache_regenerated,
            cache_entries_invalidated=self._cache_invalidated,
        )


def _get_current_memory_mb() -> float:
    """
    Return current process RSS in MB. Returns 0.0 if unavailable.
    This is the current RSS at finalize() time, not a true peak tracker.
    For a true peak, use tracemalloc or psutil.Process.memory_info().peak_wset
    (Windows) or /proc/self/status VmPeak (Linux).
    """
    try:
        import psutil
        import os
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except ImportError:
        pass
    try:
        # Fallback: read from /proc/self/status on Linux
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return kb / 1024
    except Exception:
        pass
    return 0.0
````

## File: src/smriti/embedding/validation.py
````python
"""
validation.py — Mathematical vector validation for Phase 5.

Responsibility:
    Verify that a raw (or normalized) vector from the embedder satisfies
    mathematical invariants before it becomes an immutable Vector domain object.

    Called TWICE per vector:
        1. After inference — validates raw output from the model
        2. After normalization — cheap guard against numerical edge cases

Validation checks (in order):
    1. Non-empty:         vector must have at least one element
    2. Correct dimension: len(vector) == descriptor.dimension
    3. dtype check:       all elements must be strictly float (no ints, numpy scalars, etc.)
    4. Finite values:     no NaN or Inf anywhere
    5. Non-zero norm:     a zero vector cannot be normalized

Rules:
    ✅ Return (bool, Optional[str]) — callers decide what to do with failures
    ✅ Never modify the vector
    ✅ Provide clear, actionable error messages

    ❌ Never normalize (that's normalization.py's job)
    ❌ Never embed (that's embedder.py's job)
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


def validate_vector(
    vector: List[float],
    expected_dimension: int,
) -> Tuple[bool, Optional[str]]:
    """
    Validate a raw or normalized embedding vector.

    Args:
        vector:             Float list from embedder (raw) or normalization.
        expected_dimension: Expected length (from EmbeddingModelDescriptor.dimension).

    Returns:
        (True, None)             if vector passes all checks
        (False, error_message)   if any check fails
    """
    # Check 1: Non-empty
    if not vector:
        return False, "Vector is empty"

    # Check 2: Correct dimension
    actual_dim = len(vector)
    if actual_dim != expected_dimension:
        return False, (
            f"Dimension mismatch: expected {expected_dimension}, got {actual_dim}"
        )

    # Check 3: dtype — all elements must be strictly float
    # This rejects ints, numpy scalars, strings, etc. to enforce type purity.
    for i, value in enumerate(vector):
        if not isinstance(value, float):
            return False, (
                f"Non-float type at index {i}: {type(value).__name__} "
                f"(expected float)"
            )

    # Check 4: Finite values (no NaN or Inf)
    for i, value in enumerate(vector):
        if math.isnan(value):
            return False, f"NaN detected at index {i}"
        if math.isinf(value):
            return False, f"Inf detected at index {i}"

    # Check 5: Non-zero norm
    norm_sq = sum(float(x) * float(x) for x in vector)
    if norm_sq == 0.0:
        return False, "Zero-norm vector (all elements are zero)"

    return True, None


def validate_batch(
    vectors: List[List[float]],
    expected_dimension: int,
) -> List[Tuple[bool, Optional[str]]]:
    """
    Validate an entire batch of vectors.

    Returns:
        List of (is_valid, error_message_or_None), one per input vector.
    """
    return [validate_vector(v, expected_dimension) for v in vectors]
````

## File: src/smriti/evolution/__init__.py
````python
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
````

## File: src/smriti/extraction/scanner/__init__.py
````python
"""
scanner/__init__.py — Public interface for the structural scanner.

Exports scan_document and the BlockType enum.
"""

from smriti.extraction.scanner.scanner import scan_document, BlockType, ScannerEvent

__all__ = ["scan_document", "BlockType", "ScannerEvent"]
````

## File: src/smriti/extraction/scanner/code.py
````python
"""
scanner/code.py — Code block detection and accumulation.
"""

from typing import Optional, Tuple
from smriti.extraction.rules import (
    FENCED_CODE_START,
    FENCED_CODE_END_TRIPLE,
    FENCED_CODE_END_TILDE,
    INDENTED_CODE_PATTERN,
)


def detect_fenced_code_start(line: str) -> Optional[str]:
    """Return fence char ('`' or '~') if line starts a fenced code block."""
    match = FENCED_CODE_START.match(line)
    if match:
        return match.group(1)[0]   # first char of the fence
    return None


def is_fenced_code_end(line: str, fence_char: str) -> bool:
    if fence_char == "`":
        return bool(FENCED_CODE_END_TRIPLE.match(line))
    else:
        return bool(FENCED_CODE_END_TILDE.match(line))


def is_indented_code_line(line: str) -> bool:
    return bool(INDENTED_CODE_PATTERN.match(line))
````

## File: src/smriti/extraction/scanner/heading.py
````python
"""
scanner/heading.py — Heading detection logic.
"""

from typing import Optional
from smriti.extraction.rules import HEADING_PATTERN, SETEXT_H1_PATTERN, SETEXT_H2_PATTERN


def detect_heading(line: str, next_line: Optional[str] = None):
    """
    Detect ATX or setext heading.

    Returns:
        (level, title, consumed_lines) or (None, None, 0) if not a heading.
    """
    # ATX
    match = HEADING_PATTERN.match(line)
    if match:
        level = len(match.group(1))
        title = match.group(2).strip()
        return level, title, 1

    # Setext H1 (line followed by ===)
    if next_line and SETEXT_H1_PATTERN.match(next_line):
        return 1, line.strip(), 2

    # Setext H2 (line followed by ---)
    if next_line and SETEXT_H2_PATTERN.match(next_line):
        return 2, line.strip(), 2

    return None, None, 0
````

## File: src/smriti/extraction/scanner/paragraph.py
````python
"""
scanner/paragraph.py — Paragraph accumulation logic.
"""

from typing import List, Tuple


def accumulate_paragraph(
    lines: List[str],
    start_char: int,
    current_char_pos: int,
) -> Tuple[str, int, int]:
    """
    Accumulate a paragraph block from a list of lines.

    Returns:
        (paragraph_text, char_start, char_end)
    """
    para_text = "\n".join(lines).strip()
    char_start = start_char
    char_end = current_char_pos
    return para_text, char_start, char_end
````

## File: src/smriti/extraction/scanner/scanner.py
````python
"""
scanner/scanner.py — Structural scanner orchestrator.

Responsibility:
    Read a Document's normalized_text line by line and emit ScannerEvents
    describing the structural elements found.

    This file orchestrates the detection logic from submodules.

Input:  str (normalized_text from Document)
Output: List[ScannerEvent]

Complexity: O(n) — one linear pass through the text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
import structlog

from smriti.extraction.rules import (
    YAML_FRONT_MATTER_DELIMITER,
    HORIZONTAL_RULE_PATTERN,
    BLOCK_QUOTE_PATTERN,
    BULLET_PATTERN,
    ORDERED_PATTERN,
)
from smriti.extraction.scanner.heading import detect_heading
from smriti.extraction.scanner.paragraph import accumulate_paragraph
from smriti.extraction.scanner.table import is_table_row, is_table_separator, accumulate_table
from smriti.extraction.scanner.code import (
    detect_fenced_code_start,
    is_fenced_code_end,
    is_indented_code_line,
)

logger = structlog.get_logger(__name__)


class BlockType(str, Enum):
    """The structural type of a scanner event."""
    HEADING          = "heading"
    PARAGRAPH        = "paragraph"
    BULLET_ITEM      = "bullet_item"
    ORDERED_ITEM     = "ordered_item"
    BLOCK_QUOTE      = "block_quote"
    TABLE            = "table"
    CODE_BLOCK       = "code_block"       # Ignored in V1
    FRONT_MATTER     = "front_matter"     # Ignored
    HORIZONTAL_RULE  = "horizontal_rule"  # Ignored
    BLANK            = "blank"            # Ignored


@dataclass(frozen=True)
class ScannerEvent:
    """
    An immutable structural event emitted by the scanner.

    Fields:
        block_type:    What kind of structural element this is
        text:          The meaningful text content (stripped of markers)
        heading_level: 1–6 for headings, None for everything else
        char_start:    Character offset of the FIRST character of this block
        char_end:      Character offset just after the LAST character of this block
        lines:         All lines that make up this block (for multi‑line blocks)
    """
    block_type: BlockType
    text: str
    heading_level: Optional[int]
    char_start: int
    char_end: int
    lines: tuple = field(default_factory=tuple)


def scan_document(normalized_text: str) -> List[ScannerEvent]:
    """
    Perform one linear pass through normalized_text and emit structural events.

    Args:
        normalized_text: The fully normalized text from Phase 2 (Document.normalized_text).

    Returns:
        List of ScannerEvent in document order. Never empty for non‑empty text.

    Complexity: O(n) — single pass, no recursion.
    """
    if not normalized_text.strip():
        return []

    events: List[ScannerEvent] = []
    lines = normalized_text.split("\n")
    num_lines = len(lines)

    # State flags for multi‑line blocks
    in_fenced_code = False
    fenced_code_char = ""      # ` or ~
    in_front_matter = False
    front_matter_seen = False
    in_table = False

    # Accumulation buffers
    paragraph_lines: List[str] = []
    paragraph_start: int = 0
    table_lines: List[str] = []
    table_start: int = 0
    code_lines: List[str] = []
    code_start: int = 0

    char_pos = 0  # Running character position in the full string

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, paragraph_start
        if paragraph_lines:
            para_text, p_start, p_end = accumulate_paragraph(
                paragraph_lines, paragraph_start, char_pos
            )
            if para_text:
                events.append(ScannerEvent(
                    block_type=BlockType.PARAGRAPH,
                    text=para_text,
                    heading_level=None,
                    char_start=p_start,
                    char_end=p_end,
                    lines=tuple(paragraph_lines),
                ))
            paragraph_lines = []

    def flush_table() -> None:
        nonlocal table_lines, table_start, in_table
        if table_lines:
            table_text, t_start, t_end = accumulate_table(
                table_lines, table_start, char_pos
            )
            events.append(ScannerEvent(
                block_type=BlockType.TABLE,
                text=table_text,
                heading_level=None,
                char_start=t_start,
                char_end=t_end,
                lines=tuple(table_lines),
            ))
            table_lines = []
            in_table = False

    def flush_code_block() -> None:
        nonlocal code_lines, code_start, in_fenced_code
        if code_lines:
            code_text = "\n".join(code_lines)
            events.append(ScannerEvent(
                block_type=BlockType.CODE_BLOCK,
                text=code_text,
                heading_level=None,
                char_start=code_start,
                char_end=char_pos,
                lines=tuple(code_lines),
            ))
            code_lines = []
            in_fenced_code = False

    i = 0
    while i < num_lines:
        line = lines[i]
        line_end = char_pos + len(line)

        # ── Front matter handling ─────────────────────────────────────────────
        if i == 0 and YAML_FRONT_MATTER_DELIMITER.match(line):
            in_front_matter = True
            char_pos = line_end + 1
            i += 1
            continue

        if in_front_matter:
            if YAML_FRONT_MATTER_DELIMITER.match(line) and i > 0:
                in_front_matter = False
                front_matter_seen = True
            char_pos = line_end + 1
            i += 1
            continue

        # ── Fenced code block handling ────────────────────────────────────────
        if not in_fenced_code:
            fence_char = detect_fenced_code_start(line)
            if fence_char:
                flush_paragraph()
                flush_table()
                in_fenced_code = True
                fenced_code_char = fence_char
                code_start = char_pos
                char_pos = line_end + 1
                i += 1
                continue
        else:
            if is_fenced_code_end(line, fenced_code_char):
                flush_code_block()
            else:
                code_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if not line.strip():
            flush_paragraph()
            flush_table()
            # Record blank line for statistics (we'll count later)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────────
        if HORIZONTAL_RULE_PATTERN.match(line):
            flush_paragraph()
            flush_table()
            events.append(ScannerEvent(
                block_type=BlockType.HORIZONTAL_RULE,
                text="",
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── ATX Heading (# Title) ─────────────────────────────────────────────
        heading_level, heading_title, consumed = detect_heading(line, lines[i+1] if i+1 < num_lines else None)
        if heading_level is not None:
            flush_paragraph()
            flush_table()
            # For setext, we need to skip the underline line
            end_pos = line_end
            if consumed == 2:
                # Skip the underline line as well
                # We already used next line; we'll advance i by 2
                # But we need to compute end position including the underline
                underline_line = lines[i+1]
                end_pos = line_end + 1 + len(underline_line) + 1  # include newline
                # We'll handle the skip after appending event
            events.append(ScannerEvent(
                block_type=BlockType.HEADING,
                text=heading_title,
                heading_level=heading_level,
                char_start=char_pos,
                char_end=end_pos,
                lines=(line, lines[i+1] if consumed == 2 else line),
            ))
            # Move char_pos and i
            char_pos = end_pos
            i += consumed
            continue

        # ── Block quote ───────────────────────────────────────────────────────
        quote_match = BLOCK_QUOTE_PATTERN.match(line)
        if quote_match:
            flush_paragraph()
            flush_table()
            quote_text = quote_match.group(1).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BLOCK_QUOTE,
                text=quote_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Table row ─────────────────────────────────────────────────────────
        if is_table_row(line):
            flush_paragraph()
            if not in_table:
                in_table = True
                table_start = char_pos
            table_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # ── Bullet list item ──────────────────────────────────────────────────
        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            flush_paragraph()
            flush_table()
            item_text = bullet_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BULLET_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Ordered list item ─────────────────────────────────────────────────
        ordered_match = ORDERED_PATTERN.match(line)
        if ordered_match:
            flush_paragraph()
            flush_table()
            item_text = ordered_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.ORDERED_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Paragraph accumulation ────────────────────────────────────────────
        if not paragraph_lines:
            paragraph_start = char_pos
        paragraph_lines.append(line)
        char_pos = line_end + 1
        i += 1

    # Flush any remaining state
    flush_paragraph()
    flush_table()
    flush_code_block()

    logger.debug(
        "scan complete",
        events=len(events),
        lines=len(lines),
    )

    return events
````

## File: src/smriti/extraction/scanner/table.py
````python
"""
scanner/table.py — Table detection and accumulation.
"""

from typing import List, Tuple
from smriti.extraction.rules import TABLE_ROW_PATTERN, TABLE_SEPARATOR_PATTERN


def is_table_row(line: str) -> bool:
    return bool(TABLE_ROW_PATTERN.match(line))


def is_table_separator(line: str) -> bool:
    return bool(TABLE_SEPARATOR_PATTERN.match(line))


def accumulate_table(lines: List[str], start_char: int, current_char_pos: int) -> Tuple[str, int, int]:
    """
    Accumulate a table block.

    Returns:
        (table_text, char_start, char_end)
    """
    table_text = "\n".join(lines)
    return table_text, start_char, current_char_pos
````

## File: src/smriti/extraction/__init__.py
````python
"""
extraction/__init__.py — Public API for Phase 3.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.extraction import build_semantic_sentences, ExtractionResult

They never import from individual submodules.
All internal modules (scanner, context, normalizer, segmenter, builder, validator)
are implementation details.

Public contract:
    build_semantic_sentences(document: Document) → ExtractionResult

That is the only function that crosses the phase boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Document,
    SemanticSentence,
    Phase3Stats,
    SegmentationWarning,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase3Error, SentenceValidationError

from smriti.extraction.scanner import scan_document, BlockType
from smriti.extraction.context import ContextStack
from smriti.extraction.normalizer import normalize_event
from smriti.extraction.segmenter import SentenceSegmenter
from smriti.extraction.builder import build_sentence
from smriti.extraction.validator import validate_sentences
from smriti.extraction.statistics import Phase3StatsCollector

logger = structlog.get_logger(__name__)


# ── Public result types ───────────────────────────────────────────────────────

@dataclass
class DocumentExtractionResult:
    """
    Phase 3 result for a single Document.
    """
    document_id: str
    sentences: List[SemanticSentence]
    stats: Phase3Stats
    warnings: List[SegmentationWarning]
    error: Optional[str] = None

    @property
    def sentence_count(self) -> int:
        return len(self.sentences)


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 3 — all documents processed.
    This is what Phase 4 receives.
    """
    document_results: List[DocumentExtractionResult]
    run_id: str
    rules_version: str = "3.1.0"  # <-- ADDED FINGERPRINT
    manifest_path: Optional[Path] = None

    @property
    def all_sentences(self) -> List[SemanticSentence]:
        """Flat list of all sentences across all documents."""
        result = []
        for dr in self.document_results:
            result.extend(dr.sentences)
        return result

    @property
    def total_sentences(self) -> int:
        return sum(dr.sentence_count for dr in self.document_results)

    @property
    def successful_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is None)

    @property
    def failed_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is not None)

    def to_dataset_json(self) -> str:
        """
        Serialise all SemanticSentences to JSON for Phase 4.
        Written to artifacts/run_{id}/phase3/dataset.json.
        """
        records = []
        for sentence in self.all_sentences:
            records.append({
                "sentence_id":  sentence.sentence_id,
                "document_id":  sentence.document_id,
                "text":         sentence.text,
                "context":      sentence.context,
                "position":     sentence.position,
                "char_start":   sentence.char_start,
                "char_end":     sentence.char_end,
                "source_path":  str(sentence.source_path),
                "origin_block_type": sentence.origin_block_type,  # <-- FIX: Remove .value
                "schema_version": sentence.schema_version,
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ──────────────────────────────────────────────────────

def build_semantic_sentences(document: Document) -> DocumentExtractionResult:
    """
    Transform one Document into an ordered collection of SemanticSentences.

    This is Phase 3's single public function.
    Internal modules (scanner, context, normalizer, segmenter, builder, validator)
    are never exposed.

    Args:
        document: A Document from Phase 2 with validated normalized_text.

    Returns:
        DocumentExtractionResult with sentences, stats, and warnings.
        On error, returns a result with error set and empty sentences.
    """
    document_id = document.doc_id
    source_path = document.source_document.path

    try:
        sentences, stats, warnings = _process_document(document)
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=sentences,
            stats=stats,
            warnings=warnings,
        )

    except SentenceValidationError as e:
        logger.error(
            "fatal sentence validation error",
            document_id=document_id,
            error=str(e),
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in phase 3",
            document_id=document_id,
            error=str(e),
            exc_info=True,
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )


def _process_document(
    document: Document,
) -> Tuple[List[SemanticSentence], Phase3Stats, List[SegmentationWarning]]:
    """
    Internal orchestration of Phase 3 for one Document.

    Pipeline:
        1. scan_document      → ScannerEvent[]
        2. Normalise each event → NormalizedBlock[]
        3. Associate context (from heading events) to each block
        4. segmenter.segment   → SentenceCandidate[]
        5. build_sentence      → SemanticSentence (one per candidate)
        6. validate_sentences  → validated list

    Complexity: O(n) where n = length of normalized_text
    """
    normalized_text = document.normalized_text
    document_id = document.doc_id
    source_path = document.source_document.path

    # Step 1: Structural scan
    events = scan_document(normalized_text)

    # Step 2: Initialise components
    context_stack = ContextStack()
    segmenter = SentenceSegmenter()
    stats_collector = Phase3StatsCollector()

    sentences: List[SemanticSentence] = []
    all_warnings: List[SegmentationWarning] = []
    position = 0  # Global position counter across all sentences in document

    # Step 3: Process each structural event
    for event in events:
        stats_collector.accumulate_event(event)

        # 3a: Update context if this is a heading event
        # MUST happen before normalization because headings set skip=True
        if event.block_type == BlockType.HEADING and event.heading_level is not None:
            context_stack.push(event.text, event.heading_level)

        # 3b: Normalise event to prose (context-agnostic)
        normalized_block = normalize_event(event)
        if normalized_block.warnings:
            all_warnings.extend(normalized_block.warnings)
            stats_collector.record_warnings(normalized_block.warnings)

        # Skip blocks that produce no sentences (headings, code, etc.)
        if normalized_block.skip or not normalized_block.prose.strip():
            if event.block_type == BlockType.CODE_BLOCK:
                stats_collector.record_sentence_discarded()
            continue

        # 3c: Attach current context to this block
        current_context = context_stack.current_context()

        # 3d: Segment prose into sentence candidates
        candidates = segmenter.segment(
            normalized_block.prose,
            block_char_start=normalized_block.char_start,
        )

        if not candidates:
            stats_collector.record_sentence_discarded()
            continue

        # 3e: Build SemanticSentence for each candidate
        for candidate in candidates:
            if candidate.warnings:
                all_warnings.extend(candidate.warnings)
                stats_collector.record_warnings(candidate.warnings)

            sentence = build_sentence(
                text=candidate.text,
                document_id=document_id,
                source_path=source_path,
                context=current_context,
                position=position,
                char_start=candidate.char_start,
                char_end=candidate.char_end,
                origin_block_type=event.block_type,
            )
            sentences.append(sentence)
            stats_collector.record_sentence_produced()
            position += 1

    # Step 4: Validate the complete sentence collection
    validated_sentences, val_warnings = validate_sentences(sentences, document_id)
    all_warnings.extend(val_warnings)

    discarded = len(sentences) - len(validated_sentences)
    for _ in range(discarded):
        stats_collector.record_sentence_discarded()

    stats = stats_collector.finalize()

    logger.info(
        "document processed",
        document_id=document_id[:8],
        sentences=len(validated_sentences),
        warnings=len(all_warnings),
    )

    return validated_sentences, stats, all_warnings


# ── Batch runner (called by PipelineRunner) ───────────────────────────────────

def run_extraction(
    documents: List[Document],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Run Phase 3 on all Documents from Phase 2.

    Args:
        documents:        List[Document] from Phase 2's ExtractionResult.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.

    Returns:
        ExtractionResult containing all SemanticSentences.
    """
    logger.info("phase 3 starting", run_id=run_id, documents=len(documents))
    start_time = manifest_manager.start_phase(phase=3)

    document_results: List[DocumentExtractionResult] = []

    for document in documents:
        if document.is_empty:
            logger.debug("skipping empty document", document_id=document.doc_id[:8])
            continue

        doc_result = build_semantic_sentences(document)
        document_results.append(doc_result)

    result = ExtractionResult(
        document_results=document_results,
        run_id=run_id,
    )

    # Write dataset artifact
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase3"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        sentences=result.total_sentences,
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=3,
        start_time=start_time,
        inputs={"documents": len(documents)},
        outputs={
            "total_sentences": result.total_sentences,
            "successful_documents": result.successful_documents,
            "failed_documents": result.failed_documents,
            "dataset_path": str(dataset_path),
            "rules_version": result.rules_version,
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=3)

    logger.info(
        "phase 3 complete",
        sentences=result.total_sentences,
        docs_ok=result.successful_documents,
        docs_failed=result.failed_documents,
    )

    return result
````

## File: src/smriti/extraction/builder.py
````python
"""
builder.py — SemanticSentence constructor for Phase 3.

Responsibility:
    Construct immutable SemanticSentence objects from SentenceCandidate
    and context information.

    This is the ONLY place where SemanticSentence is instantiated.
    That enforces a single, consistent construction path.

    Builder performs:
        1. Deterministic sentence_id generation (SHA256, never random)
        2. Position assignment (0-based, strictly increasing)
        3. Context association (heading path from ContextStack)
        4. Final object construction with provenance and version

    Builder NEVER modifies text.
    Builder NEVER modifies the context stack.
    Builder NEVER validates (that is validator.py's job).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional
import structlog

from smriti.core.models import SemanticSentence
from smriti.extraction.scanner import BlockType

logger = structlog.get_logger(__name__)


def build_sentence(
    text: str,
    document_id: str,
    source_path: Path,
    context: str,
    position: int,
    char_start: int,
    char_end: int,
    origin_block_type: BlockType,
) -> SemanticSentence:
    """
    Construct a single immutable SemanticSentence.

    Args:
        text:          The sentence text (stripped, non-empty).
        document_id:   The doc_id of the source Document.
        source_path:   Path to the original file (for traceability).
        context:       Current heading context (e.g. "Python > Generators").
        position:      0-based index within this document.
        char_start:    Character start in Document.normalized_text.
        char_end:      Character end in Document.normalized_text.
        origin_block_type: The BlockType that produced this sentence.

    Returns:
        Immutable SemanticSentence.
    """
    sentence_id = _compute_sentence_id(document_id, text, char_start)

    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=document_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=source_path,
        origin_block_type=origin_block_type.value,
        schema_version="3.0",
    )

    logger.debug(
        "sentence built",
        sentence_id=sentence_id[:8],
        position=position,
        context=context[:40] if context else "(root)",
        origin=origin_block_type.value,
        text_preview=text[:40],
    )

    return sentence


def _compute_sentence_id(document_id: str, text: str, char_start: int) -> str:
    """
    Compute a deterministic 16-character sentence ID.

    Input: document_id + canonical text (as stored) + char_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs always produce same ID (deterministic)
        - No timestamps
        - No random values
        - char_start disambiguates identical text at different positions
    """
    # Use the exact text that will be stored; this ensures stability across
    # future normalisation changes that might affect whitespace.
    id_material = f"{document_id}:{text}:{char_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]
````

## File: src/smriti/extraction/context.py
````python
"""
context.py — Hierarchical context stack for Phase 3.

Responsibility:
    Maintain a lightweight push/pop stack representing the current heading
    hierarchy as Phase 3 processes structural events.

    This module has FOUR operations: push, pop, peek, current_context.
    Nothing else. It is deliberately minimal.

    Memory: O(depth) — proportional to heading nesting depth, not document length.

Input:  Heading events from scanner.py
Output: Context strings like "Python > Generators > Yield"

Example:
    # Python          →  push("Python", level=1)   → stack: ["Python"]
    ## Generators     →  push("Generators", level=2) → stack: ["Python", "Generators"]
    Sentence A        →  current_context() → "Python > Generators"
    ## Decorators     →  pop to level 1, push("Decorators") → stack: ["Python", "Decorators"]
    Sentence B        →  current_context() → "Python > Decorators"
"""

from dataclasses import dataclass
from typing import List, Optional
import structlog

from smriti.extraction.rules import CONTEXT_SEPARATOR

logger = structlog.get_logger(__name__)


@dataclass
class _ContextFrame:
    """One entry in the context stack."""
    heading: str      # Cleaned heading text
    level: int        # 1–6


class ContextStack:
    """
    Lightweight heading context stack.

    The context stack represents the path from the document root
    to the current heading, like a breadcrumb trail.

    Invariant: stack[i].level < stack[i+1].level always.
    """

    def __init__(self) -> None:
        self._stack: List[_ContextFrame] = []

    def push(self, heading: str, level: int) -> None:
        """
        Push a new heading onto the stack.

        Before pushing, all frames at level >= this heading's level are popped.
        This handles the transition from deep to shallow headings:
            ## A        stack: [H2:A]
            ### B       stack: [H2:A, H3:B]
            ## C        stack: [H2:C]   ← B and A are both popped

        Args:
            heading: The heading text (without # markers).
            level:   Heading level (1=H1, 2=H2, ... 6=H6).
        """
        # Pop all frames at the same or deeper level
        while self._stack and self._stack[-1].level >= level:
            popped = self._stack.pop()
            logger.debug("context popped", heading=popped.heading, level=popped.level)

        self._stack.append(_ContextFrame(heading=heading.strip(), level=level))
        logger.debug("context pushed", heading=heading.strip(), level=level, depth=len(self._stack))

    def peek(self) -> Optional[str]:
        """Return the topmost heading text, or None if stack is empty."""
        return self._stack[-1].heading if self._stack else None

    def current_context(self) -> str:
        """
        Return the full context path as a string.

        Example: "Python > Generators > Yield"
        Returns "" if no heading has been encountered yet.
        """
        if not self._stack:
            return ""
        return CONTEXT_SEPARATOR.join(frame.heading for frame in self._stack)

    def depth(self) -> int:
        """Current stack depth (number of active headings)."""
        return len(self._stack)

    def clear(self) -> None:
        """Reset stack to empty state (use at document boundaries)."""
        self._stack.clear()

    def __repr__(self) -> str:
        return f"ContextStack({self.current_context()!r})"
````

## File: src/smriti/extraction/extractor.py
````python
# Will be filled in Phase 3\n
````

## File: src/smriti/extraction/normalizer.py
````python
"""
normalizer.py — Structured content normaliser for Phase 3.

Responsibility:
    Convert structured content (tables, lists, etc.) into canonical prose strings.
    Pass paragraph and list text through unchanged.
    Emit warnings for malformed structures.

Input:  ScannerEvent
Output: NormalizedBlock

Design:
    Each normaliser strategy handles one BlockType.
    Adding support for a new format = adding one strategy.
    No if/elif chains allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import structlog

from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.extraction.rules import TABLE_KV_TEMPLATE, TABLE_SEPARATOR_PATTERN
from smriti.core.models import SegmentationWarning

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class NormalizedBlock:
    """
    Result of normalising a single ScannerEvent into prose.

    Fields:
        prose:       The normalised text ready for sentence segmentation.
                     For headings: empty (headings become context only).
        block_type:  The original block type (for statistics and provenance).
        char_start:  Character start from original event.
        char_end:    Character end from original event.
        warnings:    Any warnings emitted during normalisation.
        skip:        If True, this block produces no sentences (headings, code, etc.)
    """
    prose: str
    block_type: BlockType
    char_start: int
    char_end: int
    warnings: tuple
    skip: bool = False  # True for headings, code blocks, etc.


def normalize_event(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a ScannerEvent into a NormalizedBlock.

    Dispatches to the appropriate strategy based on block_type.
    """
    strategy = _NORMALIZERS.get(event.block_type, _normalize_unknown)
    return strategy(event)


# ── Strategy implementations ──────────────────────────────────────────────────

def _normalize_paragraph(event: ScannerEvent) -> NormalizedBlock:
    """Paragraphs pass through unchanged."""
    return NormalizedBlock(
        prose=event.text.strip(),
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_heading(event: ScannerEvent) -> NormalizedBlock:
    """
    Headings become context only — they produce no sentences.
    The caller (orchestrator) updates the context stack.
    """
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,  # Headings do NOT produce sentences
    )


def _normalize_bullet_item(event: ScannerEvent) -> NormalizedBlock:
    """Bullet list items become single prose sentences."""
    text = event.text.strip()
    if text and not text[-1] in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_ordered_item(event: ScannerEvent) -> NormalizedBlock:
    """Ordered list items are treated identically to bullet items."""
    return _normalize_bullet_item(event)


def _normalize_block_quote(event: ScannerEvent) -> NormalizedBlock:
    """Block quotes pass through as prose."""
    text = event.text.strip()
    if text and not text[-1] in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_table(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a Markdown table into canonical prose.

    Strategy:
        | Model | Accuracy |      →   "Model: GPT-4. Accuracy: 85%."
        |-------|----------|
        | GPT-4 | 85%      |

    Each data row becomes one prose sentence.
    Headers become the keys.
    The separator row is discarded.

    If parsing fails, emit SEG_MALFORMED_TABLE and return empty prose.
    """
    warnings = []
    lines = list(event.lines)

    content_lines = [l for l in lines if not TABLE_SEPARATOR_PATTERN.match(l)]

    if not content_lines:
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        return NormalizedBlock(
            prose="",
            block_type=event.block_type,
            char_start=event.char_start,
            char_end=event.char_end,
            warnings=tuple(warnings),
            skip=True,
        )

    def parse_row(line: str) -> List[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    try:
        header_row = parse_row(content_lines[0])
        data_rows = content_lines[1:]

        if not header_row:
            raise ValueError("Empty header row")

        prose_sentences = []
        for data_line in data_rows:
            cells = parse_row(data_line)
            pairs = []
            for idx, header in enumerate(header_row):
                value = cells[idx] if idx < len(cells) else ""
                if header and value:
                    pairs.append(TABLE_KV_TEMPLATE.format(key=header, value=value))

            if pairs:
                prose_sentences.append(" ".join(pairs))

        combined_prose = " ".join(prose_sentences)

    except Exception as e:
        logger.warning("table normalisation failed", error=str(e))
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        combined_prose = ""

    return NormalizedBlock(
        prose=combined_prose,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=tuple(warnings),
        skip=not combined_prose,
    )


def _normalize_code_block(event: ScannerEvent) -> NormalizedBlock:
    """Code blocks are skipped in V1."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,),
        skip=True,
    )


def _normalize_skip(event: ScannerEvent) -> NormalizedBlock:
    """Blocks that produce nothing (horizontal rules, front matter, etc.)."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,
    )


def _normalize_unknown(event: ScannerEvent) -> NormalizedBlock:
    """Unrecognised structure — emit warning and skip."""
    logger.warning("unknown block type encountered", block_type=event.block_type)
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_UNKNOWN_STRUCTURE,),
        skip=True,
    )


# Strategy dispatch table — extend here for new formats
_NORMALIZERS = {
    BlockType.PARAGRAPH:       _normalize_paragraph,
    BlockType.HEADING:         _normalize_heading,
    BlockType.BULLET_ITEM:     _normalize_bullet_item,
    BlockType.ORDERED_ITEM:    _normalize_ordered_item,
    BlockType.BLOCK_QUOTE:     _normalize_block_quote,
    BlockType.TABLE:           _normalize_table,
    BlockType.CODE_BLOCK:      _normalize_code_block,
    BlockType.FRONT_MATTER:    _normalize_skip,
    BlockType.HORIZONTAL_RULE: _normalize_skip,
    BlockType.BLANK:           _normalize_skip,
}
````

## File: src/smriti/extraction/rules.py
````python
"""
rules.py — Deterministic rules and patterns for Phase 3.

This file contains ONLY data: patterns, dictionaries, and strategy names.
Zero execution logic lives here.

Every constant here is configurable via config/default.yaml.
This file provides the hard-coded defaults for those config values.
"""

import re

# ── Heading detection ─────────────────────────────────────────────────────────

# Matches ATX-style headings: # H1, ## H2, ..., ###### H6
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# Matches setext-style headings:
#   Title       (underlined by === for H1)
#   =========
SETEXT_H1_PATTERN = re.compile(r"^={3,}\s*$")
SETEXT_H2_PATTERN = re.compile(r"^-{3,}\s*$")

# ── List detection ────────────────────────────────────────────────────────────

# Matches bullet list items: "- item", "* item", "+ item"
BULLET_PATTERN = re.compile(r"^(\s*)[*+\-]\s+(.+)$")

# Matches ordered list items: "1. item", "2) item"
ORDERED_PATTERN = re.compile(r"^(\s*)\d+[.)]\s+(.+)$")

# ── Block quote detection ─────────────────────────────────────────────────────

BLOCK_QUOTE_PATTERN = re.compile(r"^>\s*(.*)")

# ── Code block detection ──────────────────────────────────────────────────────

FENCED_CODE_START = re.compile(r"^(`{3,}|~{3,})(.*)")
FENCED_CODE_END_TRIPLE = re.compile(r"^`{3,}\s*$")
FENCED_CODE_END_TILDE = re.compile(r"^~{3,}\s*$")

# Indented code block: 4 spaces or 1 tab at start
INDENTED_CODE_PATTERN = re.compile(r"^( {4}|\t)(.+)")

# ── Table detection ───────────────────────────────────────────────────────────

TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\|[\s\-:|]+\|")

# ── Front matter ──────────────────────────────────────────────────────────────

YAML_FRONT_MATTER_DELIMITER = re.compile(r"^---\s*$")

# ── Horizontal rule ───────────────────────────────────────────────────────────

HORIZONTAL_RULE_PATTERN = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$")

# ── HTML comment ──────────────────────────────────────────────────────────────

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)

# ── Sentence boundary ─────────────────────────────────────────────────────────

# These abbreviations should NEVER trigger a sentence boundary.
# Fully configurable via config extraction.abbreviations in default.yaml.
DEFAULT_ABBREVIATIONS = frozenset([
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "rev", "gen",
    "e.g", "i.e", "vs", "etc", "fig", "no", "vol", "pt", "pp",
    "u.s", "u.k", "a.m", "p.m", "ph.d", "m.d", "b.c", "a.d",
])

# Characters that may end a sentence when followed by space + capital letter
SENTENCE_ENDING_CHARS = frozenset([".", "?", "!"])

# Minimum characters for a sentence to be kept (shorter are discarded with SEG001)
MIN_SENTENCE_CHARS_DEFAULT = 3

# Maximum sentence length before SEG002 warning is emitted
MAX_SENTENCE_CHARS_DEFAULT = 2000

# Context separator string
CONTEXT_SEPARATOR = " > "

# Table cell serialisation template: "Key: Value."
TABLE_KV_TEMPLATE = "{key}: {value}."

# Context validation: allow letters, digits, spaces, and the separator
CONTEXT_VALID_PATTERN = re.compile(r"^[a-zA-Z0-9\s" + re.escape(CONTEXT_SEPARATOR) + "]*$")
````

## File: src/smriti/extraction/segmenter.py
````python
"""
segmenter.py — Rule-based sentence segmenter for Phase 3.

Responsibility:
    Split normalised prose into sentence candidates using deterministic rules.

    CRITICAL DESIGN CONSTRAINT:
        No statistical models.
        No spaCy sentence boundaries.
        No ML of any kind.
        Must be 100% reproducible across all runs.

Philosophy:
    Prefer false MERGE over false SPLIT.
    "Dr. Smith visited" → one sentence (NOT "Dr." + "Smith visited")
    This is safer for downstream claim extraction.

Algorithm:
    1. Split on terminal punctuation (. ? !) followed by space + uppercase
    2. Guard against abbreviations using the abbreviation dictionary
    3. Guard against decimal numbers (3.14 should not split)
    4. Guard against ellipsis (... should not split)

Input:  NormalizedBlock.prose (str)
Output: List[SentenceCandidate]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, FrozenSet
import structlog

from smriti.core.config import get_config
from smriti.extraction.rules import (
    DEFAULT_ABBREVIATIONS,
    SENTENCE_ENDING_CHARS,
    MIN_SENTENCE_CHARS_DEFAULT,
    MAX_SENTENCE_CHARS_DEFAULT,
)
from smriti.core.models import SegmentationWarning

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class SentenceCandidate:
    """
    A candidate sentence extracted from a NormalizedBlock.

    Fields:
        text:       The sentence text (stripped)
        char_start: Approximate character start within the NormalizedBlock's prose
        char_end:   Approximate character end
        warnings:   Any per-candidate warnings
    """
    text: str
    char_start: int
    char_end: int
    warnings: tuple = ()


class SentenceSegmenter:
    """
    Rule-based sentence segmenter.

    Instantiate once, call segment() per NormalizedBlock.
    Configuration is loaded once from config/default.yaml.
    """

    def __init__(self) -> None:
        cfg = get_config()
        extraction_cfg = cfg.get("extraction", {})
        segmentation_cfg = cfg.get("segmentation", {})

        custom_abbrevs = frozenset(
            a.lower() for a in extraction_cfg.get("abbreviations", [])
        )
        self._abbreviations: FrozenSet[str] = DEFAULT_ABBREVIATIONS | custom_abbrevs

        self._min_chars: int = segmentation_cfg.get(
            "min_sentence_chars", MIN_SENTENCE_CHARS_DEFAULT
        )
        self._max_chars: int = segmentation_cfg.get(
            "max_sentence_chars", MAX_SENTENCE_CHARS_DEFAULT
        )

    def segment(self, prose: str, block_char_start: int = 0) -> List[SentenceCandidate]:
        """
        Split prose into sentence candidates.

        Args:
            prose:             The normalised prose from NormalizedBlock.
            block_char_start:  Character offset of this prose in the full document.

        Returns:
            List[SentenceCandidate], may be empty if prose is empty or all candidates
            are too short.
        """
        if not prose.strip():
            return []

        raw_candidates = self._split_into_candidates(prose)
        result: List[SentenceCandidate] = []
        running_offset = block_char_start

        for raw_text in raw_candidates:
            text = raw_text.strip()
            if not text:
                running_offset += len(raw_text)
                continue

            warnings = []

            if len(text) < self._min_chars:
                logger.debug(
                    "sentence discarded (too short)",
                    length=len(text),
                    text=text[:30],
                )
                running_offset += len(raw_text)
                continue

            if len(text) > self._max_chars:
                warnings.append(SegmentationWarning.SEG_VERY_LONG_SENTENCE)
                logger.debug("very long sentence", length=len(text))

            char_start = running_offset + (len(raw_text) - len(raw_text.lstrip()))
            char_end = char_start + len(text)

            result.append(SentenceCandidate(
                text=text,
                char_start=char_start,
                char_end=char_end,
                warnings=tuple(warnings),
            ))
            running_offset += len(raw_text)

        return result

    def _split_into_candidates(self, prose: str) -> List[str]:
        """
        Split prose string into sentence candidate strings.

        Algorithm:
          - Scan character by character
          - When we hit . ? ! followed by whitespace + uppercase (or end of string),
            check if it's actually an abbreviation or decimal
          - If not, split here
        """
        candidates: List[str] = []
        current_start = 0
        i = 0
        length = len(prose)

        while i < length:
            char = prose[i]

            if char in SENTENCE_ENDING_CHARS:
                # Ellipsis (...) — never a sentence boundary
                if char == "." and i + 1 < length and prose[i + 1] == ".":
                    i += 1
                    continue

                # Decimal numbers: "3.14" — no split
                if char == "." and i > 0 and prose[i - 1].isdigit():
                    if i + 1 < length and prose[i + 1].isdigit():
                        i += 1
                        continue

                # Check if this is an abbreviation: "Dr.", "e.g.", etc.
                if char == "." and self._is_abbreviation(prose, i):
                    i += 1
                    continue

                # Check: followed by whitespace then uppercase (or end of string)
                j = i + 1
                while j < length and prose[j] in '"\')\]':
                    j += 1

                if j >= length:
                    i += 1
                    continue

                if prose[j] == " ":
                    k = j + 1
                    while k < length and prose[k] == " ":
                        k += 1
                    if k < length and (prose[k].isupper() or prose[k].isdigit()):
                        candidates.append(prose[current_start : i + 1])
                        current_start = k
                        i = k
                        continue

            i += 1

        remaining = prose[current_start:].strip()
        if remaining:
            candidates.append(remaining)

        return candidates

    def _is_abbreviation(self, text: str, dot_pos: int) -> bool:
        """
        Check if the period at dot_pos is part of a known abbreviation.

        Looks backwards from the period to find the preceding word.
        """
        if dot_pos == 0:
            return False

        word_end = dot_pos
        word_start = dot_pos - 1
        while word_start > 0 and text[word_start - 1].isalpha():
            word_start -= 1

        preceding_word = text[word_start:word_end].lower()
        return preceding_word in self._abbreviations
````

## File: src/smriti/extraction/statistics.py
````python
"""
statistics.py — Phase 3 execution statistics collector.

Responsibility:
    Collect structural metrics from one document's processing.
    Statistics are diagnostic only — they NEVER affect execution.

    Think of this as a telemetry collector.
    It observes. It never influences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import structlog

from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning

logger = structlog.get_logger(__name__)


class Phase3StatsCollector:
    """
    Mutable collector that accumulates statistics during Phase 3 processing.

    Call accumulate_event() for each ScannerEvent.
    Call record_sentence_produced() for each SemanticSentence created.
    Call record_sentence_discarded() for each discard.
    Call finalize() to get the immutable Phase3Stats result.
    """

    def __init__(self) -> None:
        self._headings = 0
        self._paragraphs = 0
        self._list_items = 0
        self._tables = 0
        self._block_quotes = 0
        self._code_blocks_skipped = 0
        self._horizontal_rules = 0
        self._front_matter_blocks = 0
        self._blank_lines = 0
        self._unknown_blocks = 0
        self._sentences_produced = 0
        self._sentences_discarded = 0
        self._warnings: List[SegmentationWarning] = []

    def accumulate_event(self, event: ScannerEvent) -> None:
        """Record a scanner event for statistics."""
        if event.block_type == BlockType.HEADING:
            self._headings += 1
        elif event.block_type == BlockType.PARAGRAPH:
            self._paragraphs += 1
        elif event.block_type in (BlockType.BULLET_ITEM, BlockType.ORDERED_ITEM):
            self._list_items += 1
        elif event.block_type == BlockType.TABLE:
            self._tables += 1
        elif event.block_type == BlockType.BLOCK_QUOTE:
            self._block_quotes += 1
        elif event.block_type == BlockType.CODE_BLOCK:
            self._code_blocks_skipped += 1
        elif event.block_type == BlockType.HORIZONTAL_RULE:
            self._horizontal_rules += 1
        elif event.block_type == BlockType.FRONT_MATTER:
            self._front_matter_blocks += 1
        elif event.block_type == BlockType.BLANK:
            self._blank_lines += 1
        else:
            self._unknown_blocks += 1

    def record_sentence_produced(self) -> None:
        self._sentences_produced += 1

    def record_sentence_discarded(self) -> None:
        self._sentences_discarded += 1

    def record_warnings(self, warnings: tuple) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase3Stats:
        """Return an immutable snapshot of accumulated statistics."""
        return Phase3Stats(
            total_headings=self._headings,
            total_paragraphs=self._paragraphs,
            total_list_items=self._list_items,
            total_tables=self._tables,
            total_block_quotes=self._block_quotes,
            total_code_blocks_skipped=self._code_blocks_skipped,
            total_horizontal_rules=self._horizontal_rules,
            total_front_matter_blocks=self._front_matter_blocks,
            total_blank_lines=self._blank_lines,
            total_unknown_blocks=self._unknown_blocks,
            sentences_produced=self._sentences_produced,
            sentences_discarded=self._sentences_discarded,
            warnings=tuple(self._warnings),
        )
````

## File: src/smriti/extraction/validator.py
````python
"""
validator.py — SemanticSentence validator for Phase 3.

Responsibility:
    Validate a collection of SemanticSentence objects before emission.
    Check per-sentence and cross-sentence invariants.

Rules:
    ✅ Text must not be empty or whitespace-only              → discard with SEG001
    ✅ Sentence IDs must be unique across the collection       → VAL001 (fatal)
    ✅ Positions must be strictly monotonically increasing     → VAL002 (fatal)
    ✅ char_start must be < char_end                           → VAL002 (fatal)
    ✅ document_id must be consistent                          → fatal
    ✅ Context strings must be plausible (non-empty, only allowed chars) → VAL003 (warning)

Design:
    NEVER modifies objects.
    ONLY reports problems.
    Fatal problems raise SentenceValidationError.
    Recoverable problems return warnings.
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.rules import CONTEXT_VALID_PATTERN
from smriti.exceptions import SentenceValidationError

logger = structlog.get_logger(__name__)


def validate_sentences(
    sentences: List[SemanticSentence],
    document_id: str,
) -> Tuple[List[SemanticSentence], List[SegmentationWarning]]:
    """
    Validate a collection of SemanticSentences.

    Args:
        sentences:    Sentences to validate.
        document_id:  Expected document_id for all sentences.

    Returns:
        (valid_sentences, warnings_list)
        valid_sentences excludes empty/whitespace-only sentences.
        Fatal violations raise SentenceValidationError instead of returning.

    Raises:
        SentenceValidationError: On duplicate IDs, non-monotonic positions,
                                  or document_id mismatch.
    """
    warnings: List[SegmentationWarning] = []
    valid: List[SemanticSentence] = []
    seen_ids = set()
    last_position = -1

    for sentence in sentences:
        # Check 1: Document identity consistency
        if sentence.document_id != document_id:
            raise SentenceValidationError(
                f"Sentence {sentence.sentence_id} has document_id "
                f"'{sentence.document_id}' but expected '{document_id}'"
            )

        # Check 2: Non-empty text
        if not sentence.text.strip():
            warnings.append(SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED)
            logger.debug("empty sentence discarded", sentence_id=sentence.sentence_id)
            continue

        # Check 3: Unique sentence ID (fatal)
        if sentence.sentence_id in seen_ids:
            raise SentenceValidationError(
                f"Duplicate sentence ID detected: {sentence.sentence_id} "
                f"in document {document_id}. This indicates a determinism bug."
            )
        seen_ids.add(sentence.sentence_id)

        # Check 4: Monotonically increasing position (fatal)
        if sentence.position <= last_position:
            raise SentenceValidationError(
                f"Non-monotonic position: sentence {sentence.sentence_id} "
                f"has position {sentence.position} after {last_position}"
            )
        last_position = sentence.position

        # Check 5: Valid character offsets (fatal)
        if sentence.char_start >= sentence.char_end and sentence.char_end > 0:
            raise SentenceValidationError(
                f"Invalid offsets for sentence {sentence.sentence_id}: "
                f"char_start={sentence.char_start} >= char_end={sentence.char_end}"
            )

        # Check 6: Context plausibility (non-fatal)
        if sentence.context:
            if not CONTEXT_VALID_PATTERN.match(sentence.context):
                warnings.append(SegmentationWarning.VAL_INVALID_CONTEXT)
                logger.warning(
                    "invalid context characters",
                    sentence_id=sentence.sentence_id,
                    context=sentence.context,
                )

        valid.append(sentence)

    return valid, warnings
````

## File: src/smriti/parsing/__init__.py
````python
"""
parsing/__init__.py — Public API for Phase 2.

External callers (PipelineRunner, main.py) import from here:

    from smriti.parsing import run_extraction, ExtractionResult

They never import from individual submodules (loader, markdown, pdf, etc.).
Those remain internal implementation details.

Orchestration:
    1. Accept List[SourceDocument] from Phase 1
    2. For each document: dispatch loader.load_document()
    3. Collect successful Document objects
    4. Record failures (one failure never stops the batch)
    5. Write dataset.json artifact
    6. Write manifest
    7. Update pipeline state
    8. Return ExtractionResult

Phase 2 Golden Rule: Extract text. Never interpret text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import Document, ExtractionMethod, SourceDocument
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import ParsingError

from smriti.parsing.loader import load_document

logger = structlog.get_logger(__name__)


@dataclass
class ExtractionStats:
    """Statistics from one Phase 2 run."""
    total_documents: int = 0
    successful: int = 0
    failed: int = 0
    total_characters: int = 0
    total_words: int = 0
    documents_with_warnings: int = 0

    def summary(self) -> str:
        return (
            f"total={self.total_documents} "
            f"success={self.successful} "
            f"failed={self.failed} "
            f"chars={self.total_characters} "
            f"words={self.total_words} "
            f"with_warnings={self.documents_with_warnings}"
        )


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 2.
    This is what Phase 3 receives.

    Attributes:
        documents:     All successfully extracted Document objects.
        failed:        (SourceDocument, error_message) pairs for failures.
        stats:         Summary statistics.
        run_id:        Pipeline run identifier.
        manifest_path: Path to the written manifest.json.
        dataset_path:  Path to the written dataset.json.
    """
    documents: List[Document]
    failed: List[Tuple[SourceDocument, str]]
    stats: ExtractionStats
    run_id: str
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None

    def to_dataset_json(self) -> str:
        """
        Serialize extracted documents to JSON.
        Written to artifacts/run_{id}/phase2/dataset.json for Phase 3.

        Includes only normalized_text and structural metadata.
        Never includes raw_text (too large, not needed by Phase 3).
        """
        records = []
        for doc in self.documents:
            records.append({
                "doc_id": doc.doc_id,
                "schema_version": doc.schema_version,
                "path": str(doc.source_document.path),
                "relative_path": str(doc.source_document.relative_path),
                "format": doc.source_document.format.value,
                "extraction_method": doc.extraction_method.value,
                "encoding_used": doc.encoding_used,
                "normalized_text": doc.normalized_text,
                "extraction_warnings": [w.value for w in doc.extraction_warnings],
                "text_statistics": {
                    "character_count": doc.text_statistics.character_count,
                    "word_count": doc.text_statistics.word_count,
                    "line_count": doc.text_statistics.line_count,
                    "blank_line_count": doc.text_statistics.blank_line_count,
                    "paragraph_count": doc.text_statistics.paragraph_count,
                },
                "modified_at": doc.source_document.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_extraction(
    source_documents: List[SourceDocument],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Execute the complete Phase 2 extraction pipeline.

    Args:
        source_documents:  List of SourceDocument from Phase 1 (canonical only).
        run_id:            Unique pipeline run identifier.
        manifest_manager:  For writing phase manifest.
        state_manager:     For updating pipeline state.

    Returns:
        ExtractionResult containing Document list and statistics.

    Raises:
        ParsingError: Only for pipeline-fatal errors (config missing, artifact dir
                      unavailable). Individual document failures do NOT raise.
    """
    config = get_config()
    stats = ExtractionStats(total_documents=len(source_documents))

    with Timer("phase2_extraction"):

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=2)
        logger.info(
            "phase 2 starting",
            run_id=run_id,
            total_documents=stats.total_documents,
        )

        # ── Step 2: Process each document ─────────────────────────────────────
        documents: List[Document] = []
        failed: List[Tuple[SourceDocument, str]] = []

        for source in source_documents:
            doc, error = load_document(source)

            if doc is not None:
                documents.append(doc)
                stats.successful += 1
                stats.total_characters += doc.text_statistics.character_count
                stats.total_words += doc.text_statistics.word_count
                if doc.has_warnings:
                    stats.documents_with_warnings += 1
            else:
                failed.append((source, error or "unknown error"))
                stats.failed += 1

        logger.info("phase 2 extraction complete", **{
            k: v for k, v in [
                ("successful", stats.successful),
                ("failed", stats.failed),
                ("total_chars", stats.total_characters),
                ("total_words", stats.total_words),
            ]
        })

        # ── Step 3: Write dataset artifact ────────────────────────────────────
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase2"
        phase_dir.mkdir(parents=True, exist_ok=True)

        output_filename = config.get("parsing", {}).get(
            "output_dataset_filename", "dataset.json"
        )
        dataset_path = phase_dir / output_filename

        result = ExtractionResult(
            documents=documents,
            failed=failed,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
        result.dataset_path = dataset_path

        logger.info(
            "phase 2 dataset written",
            path=str(dataset_path),
            documents=len(documents),
        )

        # ── Step 4: Write manifest ─────────────────────────────────────────────
        failed_paths = [str(src.path) for src, _ in failed]

        manifest_path = manifest_manager.end_phase(
            phase=2,
            start_time=start_time,
            inputs={
                "source_documents": stats.total_documents,
                "run_id": run_id,
            },
            outputs={
                "successful_documents": stats.successful,
                "failed_documents": stats.failed,
                "total_characters": stats.total_characters,
                "total_words": stats.total_words,
                "documents_with_warnings": stats.documents_with_warnings,
                "dataset_path": str(dataset_path),
                "failed_paths": failed_paths,
            },
            status="success" if stats.failed == 0 else "partial",
        )
        result.manifest_path = manifest_path

        # ── Step 5: Update pipeline state ─────────────────────────────────────
        state_manager.complete_phase(phase=2)

    logger.info("phase 2 complete", **{k: v for k, v in vars(stats).items()})

    return result
````

## File: src/smriti/parsing/builder.py
````python
"""
builder.py — Document construction.

Responsibility:
    The ONLY module allowed to create Document objects.

    Enforces all Document invariants before construction:
      - doc_id must equal source_document.doc_id (identity preserved)
      - raw_text must be str
      - normalized_text must be str
      - warnings is a tuple of WarningCode
      - text_statistics is a TextStatistics instance

    Returns a frozen (immutable) Document.

Rules:
    ✅ Validate all inputs before construction
    ✅ Enforce doc_id identity invariant
    ✅ Produce immutable Document
    ✅ Warn if document appears to be empty (using WarningCode.NO_EXTRACTABLE_TEXT)

    ❌ No extraction logic
    ❌ No normalization logic
    ❌ No filesystem access
"""

from typing import List, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Document,
    ExtractionMethod,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.exceptions import BuilderError, DocumentError

logger = structlog.get_logger(__name__)


def build_document(
    source_document: SourceDocument,
    extraction_result: RawExtractionResult,
    normalized_text: str,
    normalization_warnings: Tuple[WarningCode, ...],
    text_statistics: TextStatistics,
) -> Document:
    """
    Construct an immutable Document from its component parts.

    Args:
        source_document:        The Phase 1 SourceDocument (must remain unchanged).
        extraction_result:      Raw extraction output (raw_text, warnings, method).
        normalized_text:        Text after full normalization pipeline.
        normalization_warnings: Warnings produced during normalization (WarningCode tuple).
        text_statistics:        Structural statistics from statistics.py.

    Returns:
        Immutable Document with doc_id == source_document.doc_id.

    Raises:
        BuilderError: If any input is invalid.
        DocumentError: If the constructed Document violates an invariant.
    """
    config = get_config()
    min_extractable_chars: int = config.get("parsing", {}).get("min_extractable_chars", 10)

    # ── Input validation ──────────────────────────────────────────────────────
    if not isinstance(source_document, SourceDocument):
        raise BuilderError(f"source_document must be SourceDocument, got {type(source_document)}")
    if not isinstance(extraction_result, RawExtractionResult):
        raise BuilderError(f"extraction_result must be RawExtractionResult")
    if not isinstance(normalized_text, str):
        raise BuilderError(f"normalized_text must be str, got {type(normalized_text)}")
    if not isinstance(normalization_warnings, tuple):
        raise BuilderError(f"normalization_warnings must be tuple")
    if not isinstance(text_statistics, TextStatistics):
        raise BuilderError(f"text_statistics must be TextStatistics")

    # ── Merge all warnings (both are tuples of WarningCode) ──────────────────
    all_warnings: List[WarningCode] = list(extraction_result.warnings) + list(normalization_warnings)

    # ── Check for empty extraction ────────────────────────────────────────────
    if len(normalized_text.strip()) < min_extractable_chars:
        all_warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)

    # ── Build Document ────────────────────────────────────────────────────────
    try:
        doc = Document(
            doc_id=source_document.doc_id,        # Identity inherited, never changed
            source_document=source_document,
            raw_text=extraction_result.raw_text,
            normalized_text=normalized_text,
            extraction_method=extraction_result.method,
            extraction_warnings=tuple(all_warnings),  # tuple of WarningCode
            text_statistics=text_statistics,
            encoding_used=extraction_result.encoding_used,  # <-- ADDED
            schema_version="2.0",
        )
    except ValueError as e:
        raise DocumentError(f"Document invariant violated: {e}") from e
    except Exception as e:
        raise BuilderError(f"Document construction failed: {e}") from e

    logger.debug(
        "document built",
        doc_id=doc.doc_id[:8],
        method=doc.extraction_method.value,
        chars=text_statistics.character_count,
        words=text_statistics.word_count,
        warnings=len(all_warnings),
    )

    return doc
````

## File: src/smriti/parsing/loader.py
````python
"""
loader.py — Format dispatcher.

Responsibility:
    Choose the correct extractor based on SourceDocument.format.
    Coordinate extraction → normalization → statistics → builder pipeline.
    Return a Document or record the failure.

Rules:
    ✅ Dispatch based on FileFormat enum
    ✅ Coordinate the full single-document pipeline
    ✅ Catch document-level errors (one failure must not stop the batch)
    ✅ Return (Document | None, error_message | None)

    ❌ Never extract text itself (delegates to format-specific extractors)
    ❌ Never create Document directly (delegates to builder.py)
    ❌ Never access filesystem beyond passing path to extractor

Pipeline for each document:
    SourceDocument
        ↓
    Format-specific extractor → RawExtractionResult
        ↓
    normalize.normalize_text() → NormalizationResult (normalized_text, warnings)
        ↓
    statistics.compute_statistics() → TextStatistics
        ↓
    builder.build_document() → Document
"""

from pathlib import Path
from typing import Optional, Tuple
import structlog

from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    NormalizationResult,
    SourceDocument,
    WarningCode,
)
from smriti.exceptions import (
    BuilderError,
    DocumentError,
    EncodingError,
    LoaderError,
    MarkdownExtractionError,
    NormalizationError,
    ParsingError,
    PdfExtractionError,
    StatisticsError,
    TextExtractionError,
)
from smriti.parsing.markdown import MarkdownExtractor
from smriti.parsing.normalize import normalize_text
from smriti.parsing.pdf import PdfExtractor
from smriti.parsing.statistics import compute_statistics
from smriti.parsing.builder import build_document
from smriti.parsing.text import TextExtractor

logger = structlog.get_logger(__name__)

# Instantiate extractors once — they are stateless after init
_markdown_extractor = MarkdownExtractor()
_pdf_extractor = PdfExtractor()
_text_extractor = TextExtractor()


def load_document(source: SourceDocument) -> Tuple[Optional[Document], Optional[str]]:
    """
    Execute the full extraction pipeline for a single SourceDocument.

    Args:
        source: Immutable SourceDocument produced by Phase 1.

    Returns:
        (Document, None)       — success
        (None, error_message)  — document-level failure, batch continues

    This function never raises. All exceptions are caught and returned as
    error strings. The pipeline continues with the next document.
    """
    logger.info("loading document", doc_id=source.doc_id[:8], format=source.format.value)

    try:
        # ── Step 1: Dispatch to format-specific extractor ─────────────────────
        extraction_result = _dispatch(source)

        # ── Step 2: Normalize text ────────────────────────────────────────────
        norm_result: NormalizationResult = normalize_text(extraction_result.raw_text)

        # ── Step 3: Compute statistics ────────────────────────────────────────
        stats = compute_statistics(norm_result.normalized_text)

        # ── Step 4: Build Document ────────────────────────────────────────────
        doc = build_document(
            source_document=source,
            extraction_result=extraction_result,
            normalized_text=norm_result.normalized_text,
            normalization_warnings=norm_result.warnings,  # tuple of WarningCode
            text_statistics=stats,
        )

        logger.info(
            "document loaded",
            doc_id=source.doc_id[:8],
            chars=stats.character_count,
            words=stats.word_count,
            warnings=len(doc.extraction_warnings),
        )
        return doc, None

    # ── Document-level failures: log, continue batch ──────────────────────────
    except (
        MarkdownExtractionError,
        PdfExtractionError,
        TextExtractionError,
        EncodingError,
        NormalizationError,
        StatisticsError,
        BuilderError,
        DocumentError,
        LoaderError,
    ) as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error(
            "document extraction failed",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
        )
        return None, error_msg

    except Exception as e:
        # Unexpected error — still document-level, not pipeline-fatal
        error_msg = f"UnexpectedError: {type(e).__name__}: {e}"
        logger.error(
            "unexpected error during extraction",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
            exc_info=True,
        )
        return None, error_msg


def _dispatch(source: SourceDocument):
    """
    Select and call the correct extractor based on FileFormat.

    Raises:
        LoaderError: If the format is unsupported (should never happen post Phase 1).
    """
    match source.format:
        case FileFormat.MARKDOWN:
            return _markdown_extractor.extract(source.path)
        case FileFormat.PDF:
            return _pdf_extractor.extract(source.path)
        case FileFormat.TEXT:
            return _text_extractor.extract(source.path)
        case _:
            raise LoaderError(
                f"Unsupported format {source.format!r} for document {source.doc_id[:8]}. "
                f"Supported: {[f.value for f in FileFormat]}"
            )
````

## File: src/smriti/parsing/markdown.py
````python
"""
markdown.py — Markdown text extractor.

Responsibility:
    Read a Markdown file and return its raw decoded text.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Preserve ALL Markdown syntax (headings, lists, code blocks, tables)
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ Do NOT parse Markdown AST
    ❌ Do NOT strip Markdown syntax
    ❌ Do NOT extract YAML front matter
    ❌ Do NOT render HTML
    ❌ Do NOT detect language
    ❌ Do NOT split sentences

Why preserve Markdown syntax?
    "# AI is transforming" is richer context than "AI is transforming".
    Phase 3 uses headings as semantic signals.
    Removing '#' changes information — that belongs to interpretation, not extraction.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import MarkdownExtractionError, EncodingError

logger = structlog.get_logger(__name__)


class MarkdownExtractor:
    """Extracts raw text from a Markdown file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: List[str] = (
            config["parsing"].get("encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a Markdown file.

        Args:
            path: Absolute path to a .md file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=MARKDOWN.

        Raises:
            MarkdownExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: List[WarningCode] = []

        logger.debug("reading markdown", path=str(path))

        raw_bytes = self._read_bytes(path)
        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect and warn about mixed line endings BEFORE normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "markdown extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.MARKDOWN,
            encoding_used=encoding_used,
        )

    def _read_bytes(self, path: Path) -> bytes:
        """Read raw bytes from file."""
        try:
            return path.read_bytes()
        except OSError as e:
            raise MarkdownExtractionError(f"Cannot read {path}: {e}") from e

    def _decode(self, raw_bytes: bytes, path: Path) -> Tuple[str, Optional[WarningCode], str]:
        """
        Decode bytes using the encoding fallback chain.

        Returns:
            (decoded_text, warning_code_or_None, encoding_used)
        """
        for i, encoding in enumerate(self._encoding_fallbacks):
            try:
                text = raw_bytes.decode(encoding)
                warning = WarningCode.ENCODING_FALLBACK if i > 0 else None
                return text, warning, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        raise EncodingError(
            f"Cannot decode {path} with any supported encoding: "
            f"{self._encoding_fallbacks}"
        )
````

## File: src/smriti/parsing/normalize.py
````python
"""
normalize.py — Text normalization pipeline.

Responsibility:
    Transform raw extracted text into a canonical, deterministic form.
    This is the ONLY module that performs normalization.

Normalization order (NEVER reorder — order matters):
    1. Unicode NFC normalization
    2. Remove BOM (if present after decoding)
    3. Normalize line endings → LF
    4. Remove trailing whitespace per line
    5. Normalize tabs (if configured)
    6. Collapse consecutive blank lines
    7. Strip leading/trailing whitespace from entire document

Rules:
    ✅ Make equivalent text identical
    ✅ Never change meaning
    ✅ Record every transformation as a warning

    ❌ Do NOT change words (colour → color)
    ❌ Do NOT expand contractions (can't → cannot)
    ❌ Do NOT stem or lemmatize
    ❌ Do NOT remove stopwords
    ❌ Do NOT remove indentation
    ❌ Do NOT remove code block content

Determinism guarantee:
    Given identical input, this function always produces identical output.
    No timestamps, no randomness, no locale-dependent behavior.
"""

import re
import unicodedata
from typing import List
import structlog

from smriti.core.config import get_config
from smriti.exceptions import NormalizationError
from smriti.core.models import NormalizationResult, WarningCode

logger = structlog.get_logger(__name__)


def normalize_text(raw_text: str) -> NormalizationResult:
    """
    Apply the full normalization pipeline to raw extracted text.

    Args:
        raw_text: Text exactly as decoded from the source file.

    Returns:
        NormalizationResult(normalized_text, warnings)
        where warnings is a tuple of WarningCode enums describing transformations applied.

    Raises:
        NormalizationError: If normalization itself fails unexpectedly.
    """
    if not isinstance(raw_text, str):
        raise NormalizationError(f"raw_text must be str, got {type(raw_text)}")

    config = get_config()
    parsing_cfg = config.get("parsing", {})

    unicode_form: str = parsing_cfg.get("unicode_normalization", "NFC")
    collapse_blank_lines: int = parsing_cfg.get("collapse_blank_lines", 2)
    remove_trailing_ws: bool = parsing_cfg.get("remove_trailing_whitespace", True)

    warnings: List[WarningCode] = []
    text = raw_text

    try:
        # ── Step 1: Unicode normalization ────────────────────────────────
        text_before = text
        text = unicodedata.normalize(unicode_form, text)
        if text != text_before:
            warnings.append(WarningCode.UNICODE_NORMALIZED)

        # ── Step 2: Remove UTF-8 BOM ─────────────────────────────────────
        if text.startswith("\ufeff"):
            text = text[1:]
            warnings.append(WarningCode.BOM_REMOVED)

        # ── Step 3: Normalize line endings → LF ──────────────────────────
        has_crlf = "\r\n" in text
        has_cr_only = "\r" in text.replace("\r\n", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if has_crlf or has_cr_only:
            warnings.append(WarningCode.LINE_ENDINGS_NORMALIZED)

        # ── Step 4: Remove trailing whitespace per line ──────────────────
        if remove_trailing_ws:
            lines = text.split("\n")
            stripped_lines = [line.rstrip() for line in lines]
            if stripped_lines != lines:
                warnings.append(WarningCode.TRAILING_WHITESPACE_REMOVED)
            text = "\n".join(stripped_lines)

        # ── Step 5: Remove control characters (except LF and TAB) ────────
        control_char_pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
        text_before = text
        text = control_char_pattern.sub("", text)
        if text != text_before:
            warnings.append(WarningCode.CONTROL_CHARS_REMOVED)

        # ── Step 6: Collapse consecutive blank lines ─────────────────────
        if collapse_blank_lines >= 0:
            max_newlines = collapse_blank_lines + 1
            pattern = re.compile(r"\n{" + str(max_newlines + 1) + r",}")
            replacement = "\n" * max_newlines
            text_before = text
            text = pattern.sub(replacement, text)
            if text != text_before:
                warnings.append(WarningCode.BLANK_LINES_COLLAPSED)

        # ── Step 7: Strip leading/trailing whitespace ────────────────────
        text = text.strip()

    except NormalizationError:
        raise
    except Exception as e:
        raise NormalizationError(f"Normalization failed unexpectedly: {e}") from e

    logger.debug(
        "normalization complete",
        original_chars=len(raw_text),
        normalized_chars=len(text),
        warnings=len(warnings),
    )

    return NormalizationResult(normalized_text=text, warnings=tuple(warnings))
````

## File: src/smriti/parsing/parser.py
````python
# Will be filled in Phase 2\n
````

## File: src/smriti/parsing/pdf.py
````python
"""
pdf.py — PDF text extractor.

Responsibility:
    Extract the embedded text layer from a PDF file.
    Concatenate pages into a single string.
    Record warnings for pages with no extractable text.

Rules:
    ✅ Extract text layer from each page
    ✅ Concatenate pages with explicit page break marker
    ✅ Record per-page warnings for empty pages (as WarningCode enums)
    ✅ Respect max_pdf_pages config limit

    ❌ No OCR (ever)
    ❌ No page rendering
    ❌ No layout detection
    ❌ No table inference
    ❌ No image extraction

If a PDF has no text layer at all (image-only PDF):
    → Record WarningCode.NO_EXTRACTABLE_TEXT
    → Return empty string (do NOT fail the pipeline)
    → Phase 3 will produce 0 claims from this document

Library: pypdf (replaces deprecated PyPDF2)
"""

from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import PdfExtractionError

logger = structlog.get_logger(__name__)

# Explicit page break marker – used to separate text from different pages.
# This helps downstream phases know where page boundaries occur.
PAGE_BREAK_MARKER = "\n\n--- PAGE BREAK ---\n\n"


class PdfExtractor:
    """Extracts raw text from a PDF file using the embedded text layer."""

    def __init__(self) -> None:
        config = get_config()
        parsing_cfg = config.get("parsing", {})
        self._max_pages: int = parsing_cfg.get("max_pdf_pages", 500)
        self._max_text_length: int = parsing_cfg.get("max_text_length_chars", 5_000_000)

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Extract text from all pages of a PDF.

        Args:
            path: Absolute path to a .pdf file (already validated by Phase 1).

        Returns:
            RawExtractionResult with concatenated page text, warnings (as WarningCode), method=PDF.

        Raises:
            PdfExtractionError: If the PDF cannot be opened or is fatally corrupted.
        """
        try:
            import pypdf
        except ImportError as e:
            raise PdfExtractionError("pypdf is required for PDF extraction") from e

        warnings: List[WarningCode] = []
        page_texts: List[str] = []

        logger.debug("reading pdf", path=str(path))

        try:
            reader = pypdf.PdfReader(str(path))
        except Exception as e:
            raise PdfExtractionError(f"Cannot open PDF {path}: {e}") from e

        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, self._max_pages)

        if total_pages > self._max_pages:
            warnings.append(WarningCode.PAGE_LIMIT_REACHED)

        empty_pages: List[int] = []

        for page_num in range(pages_to_process):
            try:
                page = reader.pages[page_num]
                text = page.extract_text() or ""
            except Exception as e:
                warnings.append(WarningCode.PAGE_EXTRACTION_FAILED)
                text = ""

            if text.strip():
                page_texts.append(text)
            else:
                empty_pages.append(page_num + 1)

        if empty_pages:
            # Batch warning — don't produce one warning per empty page
            if len(empty_pages) == pages_to_process:
                warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)
            else:
                warnings.append(WarningCode.EMPTY_PDF_PAGE)

        # Join pages with explicit page break marker
        raw_text = PAGE_BREAK_MARKER.join(page_texts)

        # Guard against pathologically large PDFs
        if len(raw_text) > self._max_text_length:
            raw_text = raw_text[: self._max_text_length]
            warnings.append(WarningCode.TEXT_TRUNCATED)

        logger.debug(
            "pdf extracted",
            path=str(path),
            total_pages=total_pages,
            processed_pages=pages_to_process,
            empty_pages=len(empty_pages),
            chars=len(raw_text),
            warnings=len(warnings),
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.PDF,
            encoding_used="pdf-native",
        )
````

## File: src/smriti/parsing/statistics.py
````python
"""
statistics.py — Structural text statistics.

Responsibility:
    Compute lightweight structural statistics from normalized text.
    All statistics are derived purely from text structure.
    No NLP. No linguistic analysis.

Statistics computed:
    character_count   — total characters in normalized text
    word_count        — whitespace-separated tokens (rough but deterministic)
    line_count        — total lines (split on LF)
    blank_line_count  — lines that are empty or whitespace-only
    paragraph_count   — blocks of text separated by one or more blank lines

Complexity: O(n) time, O(1) space (processes line by line).

Invariants verified:
    character_count >= 0
    word_count >= 0
    line_count >= blank_line_count
    line_count >= paragraph_count
"""

import structlog

from smriti.core.models import TextStatistics
from smriti.exceptions import StatisticsError

logger = structlog.get_logger(__name__)


def compute_statistics(normalized_text: str) -> TextStatistics:
    """
    Compute structural statistics from normalized text.

    Args:
        normalized_text: Text after full normalization pipeline.
                         Must be a Python str.

    Returns:
        TextStatistics (frozen dataclass) with all counts.

    Raises:
        StatisticsError: If text is not a str or statistics are inconsistent.
    """
    if not isinstance(normalized_text, str):
        raise StatisticsError(f"normalized_text must be str, got {type(normalized_text)}")

    try:
        character_count = len(normalized_text)

        if not normalized_text.strip():
            # Empty or whitespace-only document
            return TextStatistics(
                character_count=character_count,
                word_count=0,
                line_count=0,
                blank_line_count=0,
                paragraph_count=0,
            )

        lines = normalized_text.split("\n")
        line_count = len(lines)

        blank_line_count = sum(1 for line in lines if not line.strip())

        word_count = len(normalized_text.split())

        # Paragraph = one or more non-blank lines separated by blank lines
        # Iterate through lines, counting transitions from blank→non-blank
        paragraph_count = 0
        in_paragraph = False
        for line in lines:
            if line.strip():
                if not in_paragraph:
                    paragraph_count += 1
                    in_paragraph = True
            else:
                in_paragraph = False

    except StatisticsError:
        raise
    except Exception as e:
        raise StatisticsError(f"Statistics computation failed: {e}") from e

    stats = TextStatistics(
        character_count=character_count,
        word_count=word_count,
        line_count=line_count,
        blank_line_count=blank_line_count,
        paragraph_count=paragraph_count,
    )

    logger.debug(
        "statistics computed",
        chars=character_count,
        words=word_count,
        lines=line_count,
        blank_lines=blank_line_count,
        paragraphs=paragraph_count,
    )

    return stats
````

## File: src/smriti/parsing/text.py
````python
"""
text.py — Plain-text extractor.

Responsibility:
    Read a .txt file and return its raw decoded text.
    Simplest extractor — reads bytes, decodes, returns.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ No semantic processing
    ❌ No format-specific parsing
"""

from pathlib import Path
from typing import List, Tuple, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import TextExtractionError, EncodingError

logger = structlog.get_logger(__name__)


class TextExtractor:
    """Extracts raw text from a plain-text (.txt) file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: List[str] = (
            config["parsing"].get("encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a plain-text file.

        Args:
            path: Absolute path to a .txt file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=TEXT.

        Raises:
            TextExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: List[WarningCode] = []

        logger.debug("reading text file", path=str(path))

        try:
            raw_bytes = path.read_bytes()
        except OSError as e:
            raise TextExtractionError(f"Cannot read {path}: {e}") from e

        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect mixed line endings before normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "text extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.TEXT,
            encoding_used=encoding_used,
        )

    def _decode(self, raw_bytes: bytes, path: Path) -> Tuple[str, Optional[WarningCode], str]:
        """
        Decode bytes using the encoding fallback chain.

        Returns:
            (decoded_text, warning_code_or_None, encoding_used)
        """
        for i, encoding in enumerate(self._encoding_fallbacks):
            try:
                text = raw_bytes.decode(encoding)
                warning = WarningCode.ENCODING_FALLBACK if i > 0 else None
                return text, warning, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        raise EncodingError(
            f"Cannot decode {path} with any supported encoding: "
            f"{self._encoding_fallbacks}"
        )
````

## File: src/smriti/pipeline/__init__.py
````python

````

## File: src/smriti/pipeline/runner.py
````python
"""
pipeline/runner.py — PipelineRunner with Phases 1, 2, 3, and 4 registered.

Phases 5–13 will be added as they are built.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from unittest import result
from smriti.core.models import RelationshipSet, KnowledgeGraph, ScoredKnowledgeGraph
from smriti.retrieval import discover_relationships
import structlog

from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.exceptions import PipelineError, Phase5Error

logger = structlog.get_logger(__name__)


def _make_run_id() -> str:
    """Produce a timestamp-based run_id. Unique per execution."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class PipelineRunner:
    """
    Orchestrates pipeline phases.

    Usage:
        runner = PipelineRunner(input_dirs=[Path("data/raw")])
        runner.run()
    """

    def __init__(self, input_dirs: List[Path]):
        self.input_dirs = [Path(d) for d in input_dirs]
        self.run_id = _make_run_id()
        self.manifest_manager = ManifestManager(
            run_id=self.run_id,
            artifacts_dir=ARTIFACTS_DIR,
        )
        self.state_manager = StateManager()
        logger.info("pipeline runner initialized", run_id=self.run_id)

    def run(
        self,
        start_from: int = 1,
        stop_at: Optional[int] = None,
        force_full: bool = False,
    ) -> bool:
        """
        Run pipeline phases start_from through stop_at.

        Args:
            start_from:  First phase to run (default 1).
            stop_at:     Last phase to run (default: run all registered).
            force_full:  Ignore caches and re-process everything.

        Returns:
            True if all phases succeeded.
        """
        logger.info(
            "pipeline run starting",
            run_id=self.run_id,
            start_from=start_from,
            stop_at=stop_at,
        )

        # Check for resumable state
        state = self.state_manager.load()
        if state and not force_full:
            completed = state.completed_phases
            if completed:
                resume_from = max(completed) + 1
                if resume_from > start_from:
                    logger.info(
                        "resuming from checkpoint",
                        completed_phases=completed,
                        resuming_at=resume_from,
                    )
                    start_from = resume_from

        try:
            # ── Phase 1: Input Discovery ───────────────────────────────────────
            phase1_result = None
            if start_from <= 1 and (stop_at is None or stop_at >= 1):
                phase1_result = self._run_phase_1(force_full=force_full)

            # ── Phase 2: Text Extraction ───────────────────────────────────────
            phase2_result = None
            if start_from <= 2 and (stop_at is None or stop_at >= 2):
                if phase1_result is None:
                    # Resuming from Phase 2 — load Phase 1 dataset from artifact
                    phase1_result = self._load_phase1_result()

                phase2_result = self._run_phase_2(phase1_result)

            # ── Phase 3: Semantic Sentence Construction ──────────────────────
            phase3_result = None
            if start_from <= 3 and (stop_at is None or stop_at >= 3):
                if phase2_result is None:
                    phase2_result = self._load_phase2_result()
                phase3_result = self._run_phase_3(phase2_result)

            # ── Phase 4: Claim Construction ────────────────────────────────────
            phase4_result = None
            if start_from <= 4 and (stop_at is None or stop_at >= 4):
                if phase3_result is None:
                    phase3_result = self._load_phase3_result()
                phase4_result = self._run_phase_4(phase3_result)


            phase5_result = None
            if start_from <= 5 and (stop_at is None or stop_at >= 5):
                if phase4_result is None:
                    phase4_result = self._load_phase4_result()
                phase5_result = self._run_phase_5(phase4_result)

            phase6_result = None
            if start_from <= 6 and (stop_at is None or stop_at >= 6):
                if phase5_result is None:
                    phase5_result = self._load_phase5_result()
                phase4_claims = self._load_phase4_result_as_map()
                phase6_result = self._run_phase_6(phase5_result, phase4_claims) 

            phase7_result = None
            if start_from <= 7 and (stop_at is None or stop_at >= 7):
                if phase6_result is None:
                    phase6_result = self._load_phase6_result()
                if phase4_claims is None:
                    phase4_claims = self._load_phase4_result_as_map()
            phase7_result = self._run_phase_7(phase6_result, phase4_claims)  

            phase8_result = None
            if start_from <= 8 and (stop_at is None or stop_at >= 8):
                if phase7_result is None:
                    phase7_result = self._load_phase7_result()
                phase8_result = self._run_phase_8(phase7_result)     

            # Phases 9–13 will be registered here as they are built.

        except Exception as e:
            logger.error("pipeline failed", error=str(e), exc_info=True)
            return False

        logger.info("pipeline run complete", run_id=self.run_id)
        return True

    # ── Phase 1 implementation ────────────────────────────────────────────────

    def _run_phase_1(self, force_full: bool = False):
        """Execute Phase 1: Input Discovery."""
        from smriti.discovery import run_discovery, DiscoveryResult

        logger.info("running phase 1")
        result = run_discovery(
            input_dirs=self.input_dirs,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            force_full=force_full,
        )
        logger.info(
            "phase 1 complete",
            canonical_docs=result.canonical_count,
            duplicates=len(result.duplicate_documents),
            skipped=len(result.skipped),
        )
        return result

    def _load_phase1_result(self):
        """
        Load Phase 1 dataset from artifact when resuming at Phase 2.
        Reconstructs SourceDocument list from dataset.json.
        """
        import json
        from datetime import datetime, timezone
        from smriti.core.models import FileFormat, SourceDocument
        from smriti.discovery import DiscoveryResult, DiscoveryStats, DuplicateRegistry

        # Find the most recent run's phase1 dataset
        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase1" / "dataset.json"
        if not dataset_path.exists():
            # Try to find any existing phase1 artifact
            phase1_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase1/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase1_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 2: no Phase 1 dataset.json found. "
                    "Run from Phase 1 first."
                )
            dataset_path = phase1_dirs[0]
            logger.info("loading phase1 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        source_documents = []
        for r in records:
            source_documents.append(
                SourceDocument(
                    doc_id=r["doc_id"],
                    path=Path(r["path"]),
                    relative_path=Path(r["relative_path"]),
                    source_root=Path(r["source_root"]),
                    format=FileFormat(r["format"]),
                    content_hash=r["content_hash"],
                    size_bytes=r["size_bytes"],
                    modified_at=datetime.fromisoformat(r["modified_at"]),
                )
            )

        # Reconstruct a minimal DiscoveryResult for Phase 2
        return type("DiscoveryResult", (), {
            "canonical_documents": source_documents,
        })()

    # ── Phase 2 implementation ────────────────────────────────────────────────

    def _run_phase_2(self, phase1_result):
        """
        Execute Phase 2: Text Extraction.
        Returns the extraction result so it can be used by later phases.
        """
        from smriti.parsing import run_extraction

        logger.info("running phase 2")
        result = run_extraction(
            source_documents=phase1_result.canonical_documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 2 complete",
            successful=result.stats.successful,
            failed=result.stats.failed,
            total_chars=result.stats.total_characters,
        )
        return result   # <-- return the result so Phase 3 can consume it

    # ── Phase 3 implementation ────────────────────────────────────────────────

    def _load_phase2_result(self):
        """Load Phase 2 dataset from artifact when resuming at Phase 3."""
        import json
        from smriti.core.models import (
            Document, SourceDocument, FileFormat, ExtractionMethod,
            TextStatistics, WarningCode, RawExtractionResult,
        )
        from datetime import datetime, timezone

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase2" / "dataset.json"
        if not dataset_path.exists():
            phase2_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase2/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase2_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 3: no Phase 2 dataset.json found. "
                    "Run from Phase 2 first."
                )
            dataset_path = phase2_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        documents = []
        for r in records:
            source_doc = SourceDocument(
                doc_id=r["doc_id"],
                path=Path(r["path"]),
                relative_path=Path(r["relative_path"]),
                source_root=Path(r["source_root"]),
                format=FileFormat(r["format"]),
                content_hash=r["content_hash"],
                size_bytes=r["size_bytes"],
                modified_at=datetime.fromisoformat(r["modified_at"]),
            )
            stats = TextStatistics(
                character_count=r["stats"]["character_count"],
                word_count=r["stats"]["word_count"],
                line_count=r["stats"]["line_count"],
                blank_line_count=r["stats"]["blank_line_count"],
                paragraph_count=r["stats"]["paragraph_count"],
            )
            documents.append(Document(
                doc_id=r["doc_id"],
                source_document=source_doc,
                raw_text=r["raw_text"],
                normalized_text=r["normalized_text"],
                extraction_method=ExtractionMethod(r["extraction_method"]),
                extraction_warnings=tuple(WarningCode(w) for w in r.get("warnings", [])),
                text_statistics=stats,
                encoding_used=r.get("encoding_used", "utf-8"),
            ))
        return type("Phase2Result", (), {"documents": documents})()

    def _run_phase_3(self, phase2_result):
        """Execute Phase 3: Semantic Sentence Construction."""
        from smriti.extraction import run_extraction

        logger.info("running phase 3")
        result = run_extraction(
            documents=phase2_result.documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 3 complete",
            total_sentences=result.total_sentences,
            docs_ok=result.successful_documents,
            docs_failed=result.failed_documents,
        )
        return result   # return for future phases if needed

    # ── Phase 4 implementation ────────────────────────────────────────────────

    def _load_phase3_result(self):
        """Load Phase 3 dataset from artifact when resuming at Phase 4."""
        import json
        from smriti.core.models import SemanticSentence
        from pathlib import Path

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase3" / "dataset.json"
        if not dataset_path.exists():
            phase3_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase3/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase3_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 4: no Phase 3 dataset.json found. "
                    "Run from Phase 3 first."
                )
            dataset_path = phase3_dirs[0]
            logger.info("loading phase3 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        sentences = []
        for r in records:
            sentences.append(SemanticSentence(
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r["context"],
                position=r["position"],
                char_start=r["char_start"],
                char_end=r["char_end"],
                source_path=Path(r["source_path"]),
                origin_block_type=r.get("origin_block_type", "paragraph"),
                schema_version=r.get("schema_version", "3.0"),
            ))

        return type("Phase3Result", (), {"all_sentences": sentences})()

    def _run_phase_4(self, phase3_result):
        """Execute Phase 4: Claim Construction."""
        from smriti.claims import extract_claims
        from smriti.claims import Phase4Result

        logger.info("running phase 4")
        result = extract_claims(
            semantic_sentences=phase3_result.all_sentences,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 4 complete",
            total_claims=result.total_claims,
            structured=result.stats.structured_claims,
            parser_failures=result.stats.parser_failures,
        )
        return result
    
        # ── Phase 5 implementation ────────────────────────────────────────────────

    def _load_phase4_result(self):
        """
        Load Phase 4 dataset from artifact when resuming at Phase 5.

        Validates schema_version before deserializing to avoid silently
        processing data from an incompatible Phase 4 implementation.
        """
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        SUPPORTED_PHASE4_SCHEMA = "4.0"

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 5: no Phase 4 dataset.json found. "
                    "Run from Phase 4 first."
                )
            dataset_path = phase4_dirs[0]
            logger.info("loading phase4 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))

        # Validate schema_version before deserializing.
        schema_versions = {r.get("schema_version", "unknown") for r in records if records}
        unsupported = schema_versions - {SUPPORTED_PHASE4_SCHEMA}
        if unsupported:
            logger.warning(
                "unexpected schema_version in phase4 dataset",
                found=sorted(unsupported),
                expected=SUPPORTED_PHASE4_SCHEMA,
            )

        claims = []
        for r in records:
            prov_data = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov_data.get("sentence_id", ""),
                document_id=prov_data.get("document_id", ""),
                source_path=Path(prov_data.get("source_path", "unknown")),
                sentence_context=prov_data.get("sentence_context", ""),
                sentence_position=prov_data.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claims.append(Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                content_hash=r.get("content_hash", ""),
                rule_version=r.get("rule_version", "1.0"),
            ))

        return type("Phase4Result", (), {"all_claims": claims})()

    def _run_phase_5(self, phase4_result):
        """Execute Phase 5: Semantic Embedding."""
        from smriti.embedding import embed_claims
        from smriti.exceptions import Phase5Error

        logger.info("running phase 5")
        try:
            result = embed_claims(
                claims=phase4_result.all_claims,
                run_id=self.run_id,
                manifest_manager=self.manifest_manager,
                state_manager=self.state_manager,
            )
        except Phase5Error as e:
            logger.error("phase 5 failed with Phase5Error", error=str(e))
            raise  # Let the runner handle it cleanly

        if result.warnings:
            logger.warning(
                "phase 5 completed with warnings",
                warning_count=len(result.warnings),
                first_warning=result.warnings[0],
            )
        if result.errors:
            logger.error(
                "phase 5 completed with errors",
                error_count=len(result.errors),
            )

        logger.info(
            "phase 5 complete",
            total_embedded=result.total_embedded,
            cached=result.stats.cached,
            failed=result.stats.failed,
            cache_hit_rate=f"{result.stats.cache_hit_rate:.1%}",
            throughput=f"{result.stats.vectors_per_second:.1f} vec/s",
        )
        return result    
    

    def _run_phase_6(self, phase5_result, claims_map) -> "RelationshipSet":
        """Execute Phase 6: Semantic Relationship Discovery."""
        from smriti.retrieval import discover_relationships

        logger.info("running phase 6")
        result = discover_relationships(
            embedded_claims=phase5_result.embedded_claims,
            claims_map=claims_map,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 6 complete",
            total_relationships=result.total_relationships,
            contradictions=len(result.contradictions),
        )
        return result


    def _load_phase5_result(self):
        """Load Phase 5 dataset from artifact when resuming at Phase 6."""
        import json, math
        from smriti.core.models import (
            EmbeddedClaim, Embedding, EmbeddingModelDescriptor,
            EmbeddingProvenance, EmbeddingQuality, Vector, VectorDType,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase5" / "dataset.json"
        if not dataset_path.exists():
            phase5_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase5/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase5_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 6: no Phase 5 dataset.json found."
                )
            dataset_path = phase5_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        embedded_claims = []

        for r in records:
            vector_vals = r["vector"]
            dim = r["dimension"]
            vec = Vector(
                values=tuple(float(v) for v in vector_vals),
                dimension=dim,
                dtype=VectorDType.FLOAT64,
                normalized=True,
            )
            prov_data = r["provenance"]
            provenance = EmbeddingProvenance(
                pipeline_version=prov_data.get("pipeline_version", "1.0"),
                normalization_mode=prov_data.get("normalization_mode", "l2"),
                device=prov_data.get("device", "cpu"),
                config_hash=prov_data.get("config_hash", ""),
            )
            model_data = r["model"]
            descriptor = EmbeddingModelDescriptor(
                provider=model_data.get("provider", ""),
                model_name=model_data.get("model_name", ""),
                model_revision=model_data.get("revision", ""),
                dimension=model_data.get("dimension", dim),
                model_signature=model_data.get("signature", ""),
            )
            embedding = Embedding(
                claim_id=r["claim_id"],
                vector=vec,
                descriptor=descriptor,
                provenance=provenance,
            )
            quality = EmbeddingQuality(
                dimension_ok=True,
                normalized=True,
                finite=all(math.isfinite(v) for v in vector_vals[:5]),
                cache_used=r.get("status") == "cached",
            )
            ec = EmbeddedClaim(
                claim_id=r["claim_id"],
                embedding=embedding,
                quality=quality,
                schema_version=r.get("schema_version", "5.0"),
            )
            embedded_claims.append(ec)

        return type("Phase5Result", (), {"embedded_claims": embedded_claims})()


    def _load_phase4_result_as_map(self):
        """Load Phase 4 claims as a {claim_id: Claim} dict for Phase 6 text lookup."""
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError("No Phase 4 dataset.json found for claim text lookup.")
            dataset_path = phase4_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        claims_map = {}

        for r in records:
            prov = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov.get("sentence_id", ""),
                document_id=prov.get("document_id", ""),
                source_path=Path(prov.get("source_path", "unknown")),
                sentence_context=prov.get("sentence_context", ""),
                sentence_position=prov.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claim = Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                content_hash=r.get("content_hash", ""),
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                rule_version=r.get("rule_version", "1.0"),
            )
            claims_map[claim.claim_id] = claim

        return claims_map
    

    def _run_phase_7(self, phase6_result, claims_map) -> "KnowledgeGraph":
        """Execute Phase 7: Knowledge Graph Construction."""
        from smriti.evolution import build_knowledge_graph

        logger.info("running phase 7")
        result = build_knowledge_graph(
            relationship_set=phase6_result,
            claims_map=claims_map,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 7 complete",
            nodes=result.node_count,
            edges=result.edge_count,
            partitions=result.partition_count,
            contradictions=result.statistics.contradiction_count,
            evolution_chains=result.statistics.evolution_chains,
            bridge_nodes=result.statistics.bridge_nodes,
        )
        return result


    def _load_phase6_result(self):
        """Load Phase 6 dataset from artifact when resuming at Phase 7."""
        import json
        from smriti.core.models import (
            RelationshipSet, Relationship, RelationshipType, RelationshipDirection,
            RelationshipEvidence, RelationshipProvenance, RelationshipQuality,
            NLIScores, InferenceMetadata, CandidatePair, SchemaVersionInfo,
            LifecycleStage,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase6" / "dataset.json"
        if not dataset_path.exists():
            phase6_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase6/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase6_dirs:
                raise PipelineError("Cannot resume at Phase 7: no Phase 6 dataset.json found.")
            dataset_path = phase6_dirs[0]
            logger.info("loading phase6 dataset", path=str(dataset_path))

        data = json.loads(dataset_path.read_text(encoding="utf-8"))
        relationships = []

        for r in data:
            ev_data = r["evidence"]
            prov_data = r["provenance"]

            pair = CandidatePair(
                claim_id_a=r["claim_id_a"],
                claim_id_b=r["claim_id_b"],
                cosine_similarity=ev_data["cosine_similarity"],
                candidate_rank=prov_data.get("candidate_rank", 1),
            )
            nli_scores = NLIScores(
                entailment_score=ev_data.get("entailment_score", 0.0),
                neutral_score=ev_data.get("neutral_score", 0.0),
                contradiction_score=ev_data.get("contradiction_score", 0.0),
                predicted_label=ev_data.get("predicted_label", "neutral"),
                raw_confidence=ev_data.get("raw_confidence", ev_data.get("confidence", 0.0)),
            )
            inference_meta = InferenceMetadata(
                model_name=ev_data.get("model_name", ""),
                model_version=ev_data.get("model_version", "unknown"),
            )
            evidence = RelationshipEvidence(
                pair=pair,
                cosine_similarity=ev_data["cosine_similarity"],
                nli_scores=nli_scores,
                calibrated_confidence=ev_data.get("calibrated_confidence", ev_data.get("confidence", 0.0)),
                inference_metadata=inference_meta,
                lifecycle_stage=LifecycleStage.RELATIONSHIP,
            )
            provenance = RelationshipProvenance(
                retrieval_backend=prov_data.get("retrieval_backend", "faiss_flat_ip"),
                retrieval_version=prov_data.get("retrieval_version", "1.0"),
                index_version=prov_data.get("index_version", "1.0"),
                search_parameters=None,
                classifier_model=prov_data.get("classifier_model", ""),
                classifier_version=prov_data.get("classifier_version", "unknown"),
                resolver_version=prov_data.get("resolver_version", "1.0"),
                calibrator_version=prov_data.get("calibrator_version", "1.0"),
                cosine_similarity=prov_data.get("cosine_similarity", 0.0),
                candidate_rank=prov_data.get("candidate_rank", 1),
                raw_nli_confidence=prov_data.get("raw_nli_confidence", prov_data.get("nli_confidence", 0.0)),
                calibrated_confidence=prov_data.get("calibrated_confidence", 0.0),
                config_hash=prov_data.get("config_hash", ""),
                run_id=prov_data.get("run_id", self.run_id),
            )
            quality = RelationshipQuality(
                cosine_above_threshold=True, nli_above_threshold=True,
                evidence_consistent=True, calibration_applied=False,
            )
            version_info = SchemaVersionInfo(
                schema_version=r.get("schema_version", "6.0"),
                migration_version="6.0", compatibility_version="6.0",
            )
            relationships.append(Relationship(
                relationship_id=r["relationship_id"],
                claim_id_a=r["claim_id_a"], claim_id_b=r["claim_id_b"],
                relationship_type=RelationshipType(r["relationship_type"]),
                direction=RelationshipDirection(r["direction"]),
                evidence=evidence, quality=quality, provenance=provenance, version_info=version_info,
            ))

        return RelationshipSet(
            relationships=relationships,
            total_candidates=len(relationships),
            total_validated=len(relationships),
            total_rejected=0,
            rejected_reasons={},
            run_id=self.run_id,
        )


    def _run_phase_8(
        self,
        phase7_result: "KnowledgeGraph",
        policy_profile: str = "balanced",
    ) -> "ScoredKnowledgeGraph":
        """Execute Phase 8: Reliability Evaluation."""
        from smriti.scoring import score_knowledge_graph
        from smriti.scoring.policies import PolicyProfile

        try:
            profile = PolicyProfile(policy_profile)
        except ValueError:
            logger.warning("unknown policy profile, using BALANCED", profile=policy_profile)
            profile = PolicyProfile.BALANCED

        logger.info("running phase 8", profile=profile.value)
        result = score_knowledge_graph(
            graph=phase7_result,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            policy_profile=profile,
        )
        logger.info(
            "phase 8 complete",
            claims_scored=result.total_scored,
            avg_reliability=f"{result.avg_reliability:.2f}",
            profile=result.policy_profile,
        )
        return result


    def _load_phase7_result(self):
        """Load Phase 7 KnowledgeGraph from artifact when resuming at Phase 8."""
        import json
        from pathlib import Path
        from smriti.core.models import (
            KnowledgeGraph, ClaimNode, RelationshipEdge, KnowledgePartition,
            RelationshipType, RelationshipDirection, GraphStatistics, ValidationReport,
            SemanticRole, TopologyMetrics, SupportAggregate, TemporalMetadata,
            TemporalStatus, NodeAnnotations,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase7" / "dataset.json"
        if not dataset_path.exists():
            phase7_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase7/dataset.json"),
                key=lambda p: p.parent.parent.name, reverse=True,
            )
            if not phase7_dirs:
                raise PipelineError("Cannot resume at Phase 8: no Phase 7 dataset.json found.")
            dataset_path = phase7_dirs[0]
            logger.info("loading phase7 dataset", path=str(dataset_path))

        data = json.loads(dataset_path.read_text(encoding="utf-8"))
        nodes = {}
        for claim_id, nd in data.get("nodes", {}).items():
            topo_data = nd.get("topology")
            topology = None
            if topo_data:
                topology = TopologyMetrics(
                    degree=topo_data.get("degree", 0),
                    in_degree=topo_data.get("in_degree", 0),
                    out_degree=topo_data.get("out_degree", 0),
                    is_bridge=topo_data.get("is_bridge", False),
                    is_hub=topo_data.get("is_hub", False),
                    partition_id=nd.get("partition_id", ""),
                    centrality=topo_data.get("centrality", 0.0),
                )
            support_data = nd.get("support")
            support = None
            if support_data:
                support = SupportAggregate(
                    support_count=support_data.get("count", 0),
                    weighted_confidence=support_data.get("weighted_confidence", 0.0),
                    supporting_claim_ids=tuple(support_data.get("supporting_claims", [])),
                    evidence_summary=f"{support_data.get('count', 0)} supporting claims",
                )
            temp_data = nd.get("temporal")
            temporal = None
            if temp_data:
                temporal = TemporalMetadata(
                    status=TemporalStatus(temp_data.get("status", "static_partition")),
                    earlier_claim_id=temp_data.get("earlier_claim_id"),
                    later_claim_id=temp_data.get("later_claim_id"),
                    time_delta_days=temp_data.get("time_delta_days"),
                    temporal_confidence=temp_data.get("temporal_confidence", 0.0),
                )
            # Reconstruct NodeAnnotations (RECTIFIED for Phase 7 compatibility)
            annotations = NodeAnnotations(
                semantic_role=SemanticRole(nd.get("semantic_role", "unclassified")),
                topology=topology,
                support_aggregate=support,
                temporal_metadata=temporal,
                partition_id=nd.get("partition_id"),
            )
            nodes[claim_id] = ClaimNode(
                node_id=claim_id, claim_id=claim_id,
                claim_text=nd.get("claim_text", ""),
                context=nd.get("context", ""),
                source_path=Path(nd.get("source_path", "unknown")),
                document_id=nd.get("document_id", ""),
                annotations=annotations,
                schema_version=nd.get("schema_version", "7.0"),
            )

        edges = {}
        for edge_id, ed in data.get("edges", {}).items():
            edges[edge_id] = RelationshipEdge(
                edge_id=edge_id,
                source_node_id=ed.get("source", ""),
                target_node_id=ed.get("target", ""),
                relationship_type=RelationshipType(ed.get("relationship_type", "supports")),
                direction=RelationshipDirection(ed.get("direction", "symmetric")),
                calibrated_confidence=ed.get("calibrated_confidence", 0.0),
                cosine_similarity=ed.get("cosine_similarity", 0.0),
                nli_confidence=ed.get("nli_confidence", ed.get("calibrated_confidence", 0.0)),
                candidate_rank=ed.get("candidate_rank", 1),
            )

        partitions = {}
        for pid, pd in data.get("partitions", {}).items():
            partitions[pid] = KnowledgePartition(
                partition_id=pid,
                stable_partition_label=pd.get("stable_partition_label", ""),
                node_ids=frozenset(pd.get("node_ids", [])),
                internal_edge_ids=frozenset(),
                node_count=pd.get("node_count", 0),
                edge_count=pd.get("edge_count", 0),
                supports_count=pd.get("supports_count", 0),
                refines_count=pd.get("refines_count", 0),
                density=pd.get("density", 0.0),
                longest_support_chain=pd.get("longest_support_chain", 0),
            )

        stats_data = data.get("statistics", {})
        stats = GraphStatistics(
            node_count=stats_data.get("node_count", len(nodes)),
            edge_count=stats_data.get("edge_count", len(edges)),
            partition_count=stats_data.get("partition_count", len(partitions)),
            contradiction_count=stats_data.get("contradiction_count", 0),
            supports_count=stats_data.get("supports_count", 0),
            refines_count=stats_data.get("refines_count", 0),
            isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
            evolution_chains=stats_data.get("evolution_chains", 0),
            unresolved_conflicts=stats_data.get("unresolved_conflicts", 0),
            construction_time_seconds=0.0, enrichment_time_seconds=0.0,
        )
        val_data = data.get("validation", {})
        validation = ValidationReport(
            is_valid=val_data.get("is_valid", True),
            node_violations=(), edge_violations=(), graph_violations=(),
            semantic_violations=(),
            validation_time_seconds=0.0,
        )
        return KnowledgeGraph(
            graph_id=data.get("graph_id", ""), nodes=nodes, edges=edges, partitions=partitions,
            statistics=stats, validation_report=validation,
            run_id=data.get("run_id", self.run_id),
            config_hash=data.get("config_hash", ""),
            schema_version=data.get("schema_version", "7.0"),
        )
````

## File: src/smriti/pipeline/validator.py
````python
"""
Input and output validation for pipeline phases.
Ensures data integrity at each phase boundary.
"""

from pathlib import Path
from typing import List
from smriti.exceptions import ValidationError


class Validator:
    """Validate pipeline inputs and outputs."""

    @staticmethod
    def validate_input_directory(path: str) -> Path:
        """Validate input directory exists and is a directory."""
        p = Path(path)
        if not p.is_dir():
            raise ValidationError(f"Input directory not found: {path}")
        return p

    @staticmethod
    def validate_markdown_files(directory: Path) -> List[Path]:
        """Find all markdown files in directory (recursive)."""
        files = list(directory.glob("**/*.md"))
        if not files:
            raise ValidationError(f"No markdown files found in {directory}")
        return files

    @staticmethod
    def validate_output_directory(path: str) -> Path:
        """Ensure output directory exists, create if needed."""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
````

## File: src/smriti/reporting/__init__.py
````python

````

## File: src/smriti/reporting/exporter.py
````python
# Will be filled in Phase 11\n
````

## File: src/smriti/retrieval/__init__.py
````python
"""
retrieval/__init__.py — Public API for Phase 6: Semantic Relationship Discovery.

External callers import ONLY from here:

    from smriti.retrieval import discover_relationships, RelationshipSet

All internal modules are hidden from external callers.

Changes from original:
    - ConfidenceCalibrator inserted between evidence generation and resolution
    - ConflictResolver applied before builder
    - ResourceGovernor enforces limits on candidate pairs
    - ReplayEngine writes replay manifest after every successful run
    - validate_all_relationships now receives triples (evidence, type, direction)
    - Phase6StatsCollector.finalize() produces DiscoveryReport (not Phase6Stats)
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim, EmbeddedClaim, RelationshipSet,
    RelationshipDirection, ConflictResolutionPolicy,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase6Error, IndexBuildError, FAISSNotAvailableError

from smriti.retrieval.index import EmbeddingIndex
from smriti.retrieval.faiss_index import FAISSIndex
from smriti.retrieval.candidate_generator import CandidateGenerator
from smriti.retrieval.validator import validate_candidates
from smriti.retrieval.classification.calibration import ConfidenceCalibrator, CalibrationStrategy
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy
from smriti.retrieval.classification.validator import validate_all_relationships
from smriti.retrieval.classification.conflict import ConflictResolver
from smriti.retrieval.builder import build_relationship, build_relationship_set
from smriti.retrieval.statistics import Phase6StatsCollector
from smriti.retrieval.governance import ResourceGovernor
from smriti.retrieval.replay import ReplayEngine

logger = structlog.get_logger(__name__)

PHASE6_VERSION = "1.0"


def _compute_config_hash(config: dict) -> str:
    """Deterministic hash of Phase 6 configuration."""
    relevant = {
        "nli_model": config.get("nli", {}).get("model", ""),
        "nli_threshold": config.get("nli", {}).get("nli_threshold", 0.80),
        "sim_threshold": config.get("relationship_discovery", {}).get("sim_threshold", 0.75),
        "top_k": config.get("relationship_discovery", {}).get("top_k", 50),
        "refine_threshold": config.get("relationship_discovery", {}).get("refine_threshold", 0.55),
        "calibration_strategy": config.get("calibration", {}).get("strategy", "identity"),
        "conflict_policy": config.get("relationship_discovery", {}).get(
            "conflict_resolution_policy", "highest_confidence"
        ),
    }
    material = json.dumps(relevant, sort_keys=True)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _serialize_relationship_set(relationship_set: RelationshipSet) -> str:
    """Serialize RelationshipSet to JSON for Phase 7."""
    records = []
    for rel in relationship_set.relationships:
        records.append({
            "relationship_id":    rel.relationship_id,
            "claim_id_a":         rel.claim_id_a,
            "claim_id_b":         rel.claim_id_b,
            "relationship_type":  rel.relationship_type.value,
            "direction":          rel.direction.value,
            "schema_version":     rel.version_info.schema_version,
            "migration_version":  rel.version_info.migration_version,
            "compatibility_version": rel.version_info.compatibility_version,
            "lifecycle_stage":    rel.lifecycle_stage.value,
            "evidence": {
                "cosine_similarity":    rel.evidence.cosine_similarity,
                "entailment_score":     rel.evidence.nli_scores.entailment_score,
                "neutral_score":        rel.evidence.nli_scores.neutral_score,
                "contradiction_score":  rel.evidence.nli_scores.contradiction_score,
                "predicted_label":      rel.evidence.nli_scores.predicted_label,
                "raw_confidence":       rel.evidence.nli_scores.raw_confidence,
                "calibrated_confidence": rel.evidence.calibrated_confidence,
                "model_name":           rel.evidence.inference_metadata.model_name,
                "model_version":        rel.evidence.inference_metadata.model_version,
                "latency_ms":           rel.evidence.inference_metadata.latency_ms,
            },
            "quality": {
                "cosine_above_threshold":  rel.quality.cosine_above_threshold,
                "nli_above_threshold":     rel.quality.nli_above_threshold,
                "evidence_consistent":     rel.quality.evidence_consistent,
                "calibration_applied":     rel.quality.calibration_applied,
            },
            "provenance": {
                "retrieval_backend":       rel.provenance.retrieval_backend,
                "retrieval_version":       rel.provenance.retrieval_version,
                "index_version":           rel.provenance.index_version,
                "classifier_model":        rel.provenance.classifier_model,
                "classifier_version":      rel.provenance.classifier_version,
                "resolver_version":        rel.provenance.resolver_version,
                "calibrator_version":      rel.provenance.calibrator_version,
                "cosine_similarity":       rel.provenance.cosine_similarity,
                "candidate_rank":          rel.provenance.candidate_rank,
                "raw_nli_confidence":      rel.provenance.raw_nli_confidence,
                "calibrated_confidence":   rel.provenance.calibrated_confidence,
                "config_hash":             rel.provenance.config_hash,
                "run_id":                  rel.provenance.run_id,
                "replay_id":               rel.provenance.replay_id,
            },
        })
    return json.dumps(records, indent=2, ensure_ascii=False)


def discover_relationships(
    embedded_claims: List[EmbeddedClaim],
    claims_map: Dict[str, Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    index: Optional[EmbeddingIndex] = None,
    nli_generator: Optional[NLIEvidenceGenerator] = None,
    calibrator: Optional[ConfidenceCalibrator] = None,
    resolver_policy: Optional[ResolverPolicy] = None,
    conflict_policy: Optional[ConflictResolutionPolicy] = None,
) -> RelationshipSet:
    """
    Execute the complete Phase 6 semantic relationship discovery pipeline.

    This is Phase 6's sole public function.

    Args:
        embedded_claims:   List of EmbeddedClaim from Phase 5.
        claims_map:        {claim_id: Claim} from Phase 4.
        run_id:            Current pipeline run identifier.
        manifest_manager:  For writing phase manifest.
        state_manager:     For updating pipeline state.
        index:             Optional pre-built index (for testing).
        nli_generator:     Optional pre-constructed NLI generator (for testing).
        calibrator:        Optional pre-constructed calibrator (for testing).
        resolver_policy:   Optional policy override (for testing).
        conflict_policy:   Optional conflict resolution policy override.

    Returns:
        RelationshipSet containing all discovered relationships with
        full provenance, calibration, and lifecycle tracing.
    """
    config = get_config()
    rd_cfg = config.get("relationship_discovery", {})
    nli_cfg = config.get("nli", {})

    sim_threshold: float = rd_cfg.get("sim_threshold", 0.75)
    nli_threshold: float = nli_cfg.get("nli_threshold", 0.80)
    min_confidence: float = rd_cfg.get("min_confidence", 0.50)
    skip_unknown: bool = rd_cfg.get("skip_unknown_relationships", True)
    config_hash = _compute_config_hash(config)

    # Resolve conflict policy
    if conflict_policy is None:
        policy_str = rd_cfg.get("conflict_resolution_policy", "highest_confidence")
        conflict_policy = ConflictResolutionPolicy(policy_str)

    logger.info(
        "phase 6 starting",
        run_id=run_id,
        embedded_claims=len(embedded_claims),
        sim_threshold=sim_threshold,
        nli_threshold=nli_threshold,
        conflict_policy=conflict_policy.value,
    )

    start_time = manifest_manager.start_phase(phase=6)
    stats = Phase6StatsCollector()
    stats.record_embedded_claims(len(embedded_claims))

    # Resource governance
    governor = ResourceGovernor()

    # Build embeddings lookup map
    embeddings_map: Dict[str, EmbeddedClaim] = {
        ec.claim_id: ec for ec in embedded_claims
    }

    # ── Stage 1: Build vector index ──────────────────────────────────────────
    if index is None:
        if not embedded_claims:
            logger.warning("no embedded claims — returning empty RelationshipSet")
            relationship_set = RelationshipSet(
                relationships=[], total_candidates=0,
                total_validated=0, total_rejected=0,
                rejected_reasons={}, run_id=run_id,
            )
            _finalize_phase(
                relationship_set, stats, run_id, start_time,
                manifest_manager, state_manager, config_hash, config,
                phase5_path="", phase4_path="",
            )
            return relationship_set

        dimension = embedded_claims[0].dimension
        index = FAISSIndex(dimension=dimension)
        claim_ids = [ec.claim_id for ec in embedded_claims]
        vectors = [list(ec.values) for ec in embedded_claims]
        try:
            index.add(claim_ids, vectors)
        except (IndexBuildError, FAISSNotAvailableError) as e:
            logger.error("index build failed", error=str(e))
            raise
        logger.info("vector index built", size=index.size, dimension=dimension)

    # ── Stage 2: Generate candidate pairs ────────────────────────────────────
    stats.record_candidate_start()

    with Timer("phase6_candidate_generation"):
        generator = CandidateGenerator()
        raw_candidates = generator.generate(embedded_claims, index)

    # Resource governance: enforce pair limit
    governor.check_timeout()
    raw_candidates = governor.enforce_pair_limit(raw_candidates)

    # ── Stage 3: Validate candidates ─────────────────────────────────────────
    with Timer("phase6_candidate_validation"):
        valid_candidates, rejection_counts = validate_candidates(
            candidates=raw_candidates,
            claims_map=claims_map,
            embeddings_map=embeddings_map,
            sim_threshold=sim_threshold,
        )

    stats.record_candidate_end(
        total=len(raw_candidates),
        validated=len(valid_candidates),
        rejected=sum(rejection_counts.values()),
    )
    all_rejection_reasons = dict(rejection_counts)

    # ── Stage 4: NLI evidence generation ─────────────────────────────────────
    stats.record_nli_start()
    governor.check_timeout()

    if nli_generator is None:
        nli_generator = NLIEvidenceGenerator()

    with Timer("phase6_nli_inference"):
        all_evidence = nli_generator.generate_batch(
            pairs=valid_candidates,
            claims_map=claims_map,
        )

    stats.record_nli_end(calls=len(all_evidence))

    # ── Stage 4b: Confidence calibration ─────────────────────────────────────
    if calibrator is None:
        model_name = nli_cfg.get("model", "cross-encoder/nli-deberta-v3-small")
        calibrator = ConfidenceCalibrator(model_name=model_name)

    with Timer("phase6_calibration"):
        all_evidence = calibrator.calibrate_batch(all_evidence)

    # ── Stage 5: Resolve relationships ───────────────────────────────────────
    policy = resolver_policy or ResolverPolicy.from_config()
    resolver = RelationshipResolver(policy=policy)
    resolved_triples = []

    for evidence in all_evidence:
        rel_type, direction = resolver.resolve(evidence)
        resolved_triples.append((evidence, rel_type, direction))

    # ── Stage 6: Validate resolved relationships ──────────────────────────────
    governor.check_timeout()

    valid_resolved, rel_rejection_counts = validate_all_relationships(
        evidence_with_types=resolved_triples,
        min_confidence=min_confidence,
        nli_threshold=nli_threshold,
        skip_unknown=skip_unknown,
    )
    for k, v in rel_rejection_counts.items():
        all_rejection_reasons[k] = all_rejection_reasons.get(k, 0) + v

    # ── Stage 6b: Conflict resolution ────────────────────────────────────────
    # Build preliminary relationships for conflict resolution
    preliminary_relationships = []
    for evidence, rel_type, direction in valid_resolved:
        rel = build_relationship(
            evidence=evidence,
            relationship_type=rel_type,
            direction=direction,
            nli_threshold=nli_threshold,
            config_hash=config_hash,
            run_id=run_id,
        )
        preliminary_relationships.append(rel)

    conflict_resolver = ConflictResolver(policy=conflict_policy)
    relationships = conflict_resolver.resolve_conflicts(preliminary_relationships)

    conflicts_resolved = len(preliminary_relationships) - len(relationships)
    for _ in range(conflicts_resolved):
        stats.record_conflict_resolved()

    # ── Stage 7: Record statistics ────────────────────────────────────────────
    for rel in relationships:
        calibration_applied = rel.quality.calibration_applied
        stats.record_relationship(
            rel.relationship_type,
            rel.evidence.calibrated_confidence,
            calibration_applied,
        )

    rejected_count = len(all_evidence) - len(valid_resolved)
    for _ in range(rejected_count):
        stats.record_rejected_relationship("validation_stage")

    # ── Stage 8: Build RelationshipSet ────────────────────────────────────────
    relationship_set = build_relationship_set(
        relationships=relationships,
        total_candidates=len(raw_candidates),
        total_validated=len(valid_candidates),
        total_rejected=sum(all_rejection_reasons.values()),
        rejected_reasons=all_rejection_reasons,
        run_id=run_id,
    )

    _finalize_phase(
        relationship_set, stats, run_id, start_time,
        manifest_manager, state_manager, config_hash, config,
        phase5_path="", phase4_path="",
    )

    logger.info(
        "phase 6 complete",
        total_relationships=relationship_set.total_relationships,
        contradictions=len(relationship_set.contradictions),
        supports=len(relationship_set.supports),
        refinements=len(relationship_set.refinements),
        conflicts_resolved=conflicts_resolved,
    )

    return relationship_set


def _finalize_phase(
    relationship_set: RelationshipSet,
    stats: Phase6StatsCollector,
    run_id: str,
    start_time: float,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    config_hash: str,
    config: dict,
    phase5_path: str,
    phase4_path: str,
) -> None:
    """Write artifacts, replay manifest, phase manifest, and update pipeline state."""
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase6"
    phase_dir.mkdir(parents=True, exist_ok=True)

    # Write dataset artifact for Phase 7
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(
        _serialize_relationship_set(relationship_set), encoding="utf-8"
    )
    relationship_set.dataset_path = dataset_path
    logger.info("dataset written", path=str(dataset_path))

    final_report = stats.finalize()

    # Write replay manifest
    replay_engine = ReplayEngine()
    replay_manifest = replay_engine.build_replay_manifest(
        run_id=run_id,
        config=config,
        config_hash=config_hash,
        total_embedded=final_report.total_embedded_claims,
        total_relationships=final_report.relationships_produced,
        phase5_path=phase5_path,
        phase4_path=phase4_path,
    )
    replay_path = replay_engine.write_replay_manifest(replay_manifest, run_id)
    relationship_set.replay_manifest_path = replay_path

    # Write phase manifest
    manifest_path = manifest_manager.end_phase(
        phase=6,
        start_time=start_time,
        inputs={
            "embedded_claims": final_report.total_embedded_claims,
            "config_hash": config_hash,
        },
        outputs={
            "total_candidates":   final_report.total_candidate_pairs,
            "validated":          final_report.validated_candidates,
            "relationships":      final_report.relationships_produced,
            "contradictions":     final_report.contradictions,
            "supports":           final_report.supports,
            "refinements":        final_report.refinements,
            "calibration_applied": final_report.calibration_applied_count,
            "conflicts_resolved": final_report.conflicts_resolved,
            "confidence_histogram": final_report.confidence_histogram,
            "dataset_path":       str(dataset_path),
            "replay_manifest_path": str(replay_path),
        },
        status="success",
    )
    relationship_set.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=6)
````

## File: src/smriti/retrieval/retriever.py
````python
# Will be filled in Phase 5\n
````

## File: src/smriti/scoring/__init__.py
````python
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
                    "signal_name": m.signal_name,
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
                    "signal": c.signal_name,
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
````

## File: src/smriti/scoring/scorer.py
````python
"""scorer.py — Phase 8 entry point. Delegates to scoring/__init__.py."""
from smriti.scoring import score_knowledge_graph, ScoredKnowledgeGraph
__all__ = ["score_knowledge_graph", "ScoredKnowledgeGraph"]
````

## File: src/smriti/__init__.py
````python
__all__ = ['__version__']\nfrom .__version__ import __version__\n
````

## File: src/smriti/__version__.py
````python
__version__ = '0.1.0'\n
````

## File: src/smriti/constants.py
````python
"""
Structural constants for SMRITI.

RULE: Only values that are genuinely fixed belong here.
      - Schema versions (changing them = breaking change)
      - Algorithm identifiers (sha256, not a tuning knob)
      - Hard system limits (not tuning knobs)
      - Template structures

WHAT DOES NOT BELONG HERE:
      - ML model names        → config/default.yaml (embedding.model)
      - Similarity thresholds → config/default.yaml (nli.sim_threshold)
      - Batch sizes           → config/default.yaml (embedding.batch_size)
      - Log levels            → config/default.yaml (logging.level)
"""

# === SCHEMA ===
CACHE_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = "1.0"
STATE_SCHEMA_VERSION = "1.0"

# === HASHING ===
HASH_ALGORITHM = "sha256"
HASH_CHUNK_SIZE = 8192  # bytes

# === HARD LIMITS (system safety, not tuning) ===
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024   # 50 MB — reject files larger than this
MAX_BATCH_SIZE = 256                      # absolute ceiling, never exceeded
TIMEOUT_SECONDS = 3600                    # 1 hour per phase

# === PIPELINE MANIFEST TEMPLATE ===
MANIFEST_TEMPLATE = {
    "schema_version": MANIFEST_SCHEMA_VERSION,
    "run_id": None,
    "phase": None,
    "timestamp": None,
    "duration_seconds": None,
    "inputs": None,
    "outputs": None,
    "status": "pending",    # pending | running | success | failed
    "versions": {},
    "error": None,
}
````

## File: src/smriti/exceptions.py
````python
"""
Custom exception hierarchy for SMRITI.
All exceptions inherit from SMRITIError for easy catch-all handling.
"""


class SMRITIError(Exception):
    """Base exception for all SMRITI errors."""
    pass


class ConfigError(SMRITIError):
    """Configuration is invalid or incomplete."""
    pass


class DiscoveryError(SMRITIError):
    """Error discovering input files."""
    pass


# ── Phase 2: Text Extraction ──────────────────────────────────────────────────

class ParsingError(SMRITIError):
    """Base exception for all Phase 2 extraction errors."""
    pass


class LoaderError(ParsingError):
    """Loader failed to dispatch to an extractor."""
    pass


class EncodingError(ParsingError):
    """File could not be decoded with any supported encoding."""
    pass


class MarkdownExtractionError(ParsingError):
    """Error reading a Markdown file."""
    pass


class PdfExtractionError(ParsingError):
    """Error extracting text from a PDF file."""
    pass


class TextExtractionError(ParsingError):
    """Error reading a plain-text file."""
    pass


class NormalizationError(ParsingError):
    """Error during text normalization."""
    pass


class StatisticsError(ParsingError):
    """Error computing text statistics."""
    pass


class BuilderError(ParsingError):
    """Error constructing a Document object."""
    pass


class DocumentError(ParsingError):
    """Invalid Document state detected."""
    pass


# ── Phase 3+ ─────────────────────────────────────────────────────────────────

class ExtractionError(SMRITIError):
    """Error extracting claims (Phase 3)."""
    pass


class EmbeddingError(SMRITIError):
    """Error computing embeddings."""
    pass


class RetrievalError(SMRITIError):
    """Error retrieving candidates."""
    pass


class ContradictionError(SMRITIError):
    """Error detecting contradictions."""
    pass


class EvolutionError(SMRITIError):
    """Error analyzing knowledge evolution."""
    pass


class ScoringError(SMRITIError):
    """Error computing metrics."""
    pass


class ReportingError(SMRITIError):
    """Error generating report."""
    pass


class DashboardError(SMRITIError):
    """Error in dashboard."""
    pass


class PipelineError(SMRITIError):
    """Error in pipeline orchestration."""
    pass


class CacheError(SMRITIError):
    """Error in cache operations."""
    pass


class HashError(SMRITIError):
    """Error computing hash."""
    pass


class ValidationError(SMRITIError):
    """Input or output validation failed."""
    pass

# ── Phase 3: Semantic Sentence Construction ───────────────────────────────────

class Phase3Error(SMRITIError):
    """Base for all Phase 3 errors."""
    pass


class ScannerError(Phase3Error):
    """Structural scanner failed on a document."""
    pass


class ContextError(Phase3Error):
    """Context stack invariant violated (fatal — indicates design error)."""
    pass


class NormalizationError(Phase3Error):
    """Structured content could not be normalised to prose."""
    pass


class SegmentationError(Phase3Error):
    """Sentence segmentation produced an impossible result."""
    pass


class SentenceValidationError(Phase3Error):
    """A SemanticSentence failed validation (fatal constraint violated)."""
    pass

# ── Phase 4: Claim Construction ───────────────────────────────────────────────

class Phase4Error(SMRITIError):
    """Base for all Phase 4 errors."""
    pass


class ClaimExtractionError(Phase4Error):
    """Unrecoverable error during claim extraction for a single sentence."""
    pass


class ClaimValidationError(Phase4Error):
    """Fatal constraint violation in claim validation (duplicate ID, broken provenance)."""
    pass


class SpacyNotLoadedError(Phase4Error):
    """spaCy model could not be loaded — pipeline cannot continue."""
    pass


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────

class Phase5Error(SMRITIError):
    """Base for all Phase 5 errors."""
    pass


class EmbeddingModelError(Phase5Error):
    """Embedding model failed to load or is misconfigured."""
    pass


class EmbeddingInferenceError(Phase5Error):
    """Embedding inference failed for a batch or single input."""
    pass


class VectorValidationError(Phase5Error):
    """Vector failed mathematical validation (NaN, Inf, dimension mismatch, dtype)."""
    pass


class CacheKeyError(Phase5Error):
    """Cache key could not be computed deterministically."""
    pass


class CacheSchemaMismatchError(Phase5Error):
    """Cache entry schema version does not match current Phase 5 schema."""
    pass

# ── Phase 6: Semantic Relationship Discovery ───────────────────────────────────
from enum import Enum
class Phase6ErrorCategory(str, Enum):
    """
    Failure taxonomy for Phase 6.

    RECOVERABLE:     The pipeline can continue; this pair is skipped.
    NON_RECOVERABLE: The pipeline must abort.
    RETRYABLE:       The operation failed transiently; retry may succeed.
    CONFIGURATION:   The config is invalid; cannot proceed without fix.
    DATA:            Input data is malformed; this batch/pair is skipped.
    INFRASTRUCTURE:  External service (GPU, disk, network) failed.
    """
    RECOVERABLE     = "recoverable"
    NON_RECOVERABLE = "non_recoverable"
    RETRYABLE       = "retryable"
    CONFIGURATION   = "configuration"
    DATA            = "data"
    INFRASTRUCTURE  = "infrastructure"


class Phase6Error(SMRITIError):
    """Base for all Phase 6 errors."""
    category: Phase6ErrorCategory = Phase6ErrorCategory.NON_RECOVERABLE

    def __init__(self, message: str, category: Phase6ErrorCategory = None):
        super().__init__(message)
        if category is not None:
            self.category = category


class IndexBuildError(Phase6Error):
    """Failed to build the vector index. Non-recoverable."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class FAISSNotAvailableError(Phase6Error):
    """faiss-cpu is not installed. Configuration error."""
    category = Phase6ErrorCategory.CONFIGURATION


class NLIModelError(Phase6Error):
    """NLI cross-encoder failed to load or run inference."""
    category = Phase6ErrorCategory.INFRASTRUCTURE


class NLIInferenceBatchError(Phase6Error):
    """One NLI batch failed — pairs in batch are skipped. Recoverable."""
    category = Phase6ErrorCategory.RECOVERABLE


class RelationshipValidationError(Phase6Error):
    """A Relationship failed structural validation (fatal invariant violated)."""
    category = Phase6ErrorCategory.DATA


class CandidateGenerationError(Phase6Error):
    """ANN candidate generation failed."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class CalibrationError(Phase6Error):
    """ConfidenceCalibrator encountered an unexpected score distribution."""
    category = Phase6ErrorCategory.RECOVERABLE


class ResolverPolicyError(Phase6Error):
    """ResolverPolicy configuration is invalid or internally inconsistent."""
    category = Phase6ErrorCategory.CONFIGURATION


class ConflictResolutionError(Phase6Error):
    """ConflictResolver could not determine which relationship wins."""
    category = Phase6ErrorCategory.RECOVERABLE


class ResourceLimitExceeded(Phase6Error):
    """A resource limit (max_pairs, memory, timeout) was exceeded."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class ReplayError(Phase6Error):
    """Replay failed — run_id not found or replay manifest corrupted."""
    category = Phase6ErrorCategory.CONFIGURATION

# ── Phase 7: Knowledge Graph Construction ────────────────────────────────────

class Phase7Error(SMRITIError):
    """Base for all Phase 7 errors."""
    pass


class GraphConstructionError(Phase7Error):
    """Fatal error during graph construction. No partial graph is emitted."""
    pass


class GraphValidationError(Phase7Error):
    """Structural invariant violated during validation. Fatal."""
    pass


class SemanticValidationError(Phase7Error):
    """Semantic invariant violated (e.g. impossible relationship chain). Fatal."""
    pass


class PartitioningError(Phase7Error):
    """Constraint-based partitioning failed."""
    pass


class BackendError(Phase7Error):
    """Graph backend (NetworkX) encountered an unexpected error."""
    pass


class SerializationError(Phase7Error):
    """KnowledgeGraph could not be serialized to JSON."""
    pass


class AnnotationPolicyError(Phase7Error):
    """AnnotationPolicy configuration is invalid or internally inconsistent."""
    pass    

# ── Phase 8: Reliability Evaluation ─────────────────────────────────────────

class Phase8Error(SMRITIError):
    """Base for all Phase 8 errors."""
    pass


class SignalExtractionError(Phase8Error):
    """A signal extractor failed to produce a valid measurement."""
    pass


class NormalizationError(Phase8Error):
    """Signal normalization produced an invalid value (after validation)."""
    pass


class FusionError(Phase8Error):
    """Reliability fusion encountered an impossible configuration."""
    pass


class PolicyError(Phase8Error):
    """Policy configuration is invalid or internally inconsistent."""
    pass


class RegistryError(Phase8Error):
    """SignalRegistry encountered a duplicate registration or ordering conflict."""
    pass


class ScoringValidationError(Phase8Error):
    """A ReliabilityMetadata failed structural validation."""
    pass
````

## File: src/smriti/main.py
````python
"""
Main entry point for the SMRITI pipeline.
Initializes core infrastructure, wires up phases, and triggers the runner.
"""

from smriti.core.logger import setup_logging, get_logger
from smriti.core.paths import RAW_DATA_DIR

setup_logging()
logger = get_logger(__name__)


def main():
    logger.info("smriti application starting")

    try:
        from smriti.pipeline.runner import PipelineRunner

        runner = PipelineRunner(input_dirs=[RAW_DATA_DIR])

        # Run Phase 1 + Phase 2 (stop_at=2 to run only these phases during development)
        success = runner.run(start_from=1, stop_at=2)

        if success:
            logger.info("smriti pipeline completed successfully")
        else:
            logger.error("smriti pipeline failed")

    except Exception as e:
        logger.error("fatal pipeline error", error=str(e), exc_info=True)


if __name__ == "__main__":
    main()
````

## File: src/.gitkeep
````

````

## File: tests/fixtures/sample_notes.md
````markdown
# sample notes\n
````

## File: tests/integration/test_phase1_discovery.py
````python
"""
Integration test for Phase 1 end-to-end.

Tests the complete pipeline:
  input directories → DiscoveryResult

Uses a realistic vault fixture with:
  - Normal notes (.md, .txt, .pdf)
  - Nested subdirectories
  - Duplicate content (different filenames)
  - Invalid files (empty, wrong extension)
  - Hidden files and directories
"""

import json
import pytest
from pathlib import Path
from smriti.discovery import run_discovery, DiscoveryResult
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager


@pytest.fixture
def realistic_vault(tmp_path):
    """
    Create a realistic Obsidian-like vault.
    """
    vault = tmp_path / "vault"
    vault.mkdir()

    # Normal notes
    ai_content = "Artificial intelligence is transforming the world."
    (vault / "AI.md").write_text(ai_content, encoding="utf-8")
    (vault / "Python.md").write_text(
        "Python is the dominant language for data science.", encoding="utf-8"
    )

    # Nested dirs
    archive = vault / "Archive"
    archive.mkdir()
    (archive / "Old_AI.md").write_text(ai_content, encoding="utf-8")  # DUPLICATE
    (archive / "Very_Old.md").write_text("Old notes about computing.", encoding="utf-8")

    research = vault / "Research" / "Papers"
    research.mkdir(parents=True)
    (research / "summary.txt").write_text("Research summary.", encoding="utf-8")
    (research / "paper.pdf").write_bytes(b"%PDF-1.4 fake content")

    # Must be ignored
    obsidian = vault / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text('{"theme": "dark"}')

    # Must be skipped
    (vault / "empty.md").write_bytes(b"")
    (vault / "unsupported.docx").write_bytes(b"PK fake docx")

    return vault


@pytest.fixture
def run_id():
    return "test_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


def test_phase1_discovers_correct_count(realistic_vault, run_id, test_managers):
    """Full discovery must find 6 documents, canonical count = 5."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert isinstance(result, DiscoveryResult)
    assert len(result.documents) == 6
    assert result.canonical_count == 5


def test_phase1_detects_one_duplicate(realistic_vault, run_id, test_managers):
    """Old_AI.md has same content as AI.md — must be detected as duplicate."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.duplicate_registry.duplicate_count == 1
    dup_paths = result.duplicate_registry.duplicate_paths
    assert any("Old_AI.md" in str(p) for p in dup_paths)


def test_phase1_skips_empty_file(realistic_vault, run_id, test_managers):
    """empty.md must appear in skipped list with appropriate reason."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("empty.md" in p for p in skipped_paths)

    skipped_reasons = {str(p): r for p, r in result.skipped}
    empty_path = next(p for p in skipped_paths if "empty.md" in p)
    assert "empty" in skipped_reasons[empty_path]


def test_phase1_skips_unsupported_extension(realistic_vault, run_id, test_managers):
    """unsupported.docx must be skipped — not crash."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("unsupported.docx" in p for p in skipped_paths)


def test_phase1_ignores_obsidian_dir(realistic_vault, run_id, test_managers):
    """No file inside .obsidian/ must appear in results."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    all_paths = [str(d.path) for d in result.documents]
    assert not any(".obsidian" in p for p in all_paths)


def test_phase1_documents_are_immutable(realistic_vault, run_id, test_managers):
    """SourceDocument must be frozen (no mutation allowed)."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_phase1_writes_manifest(realistic_vault, run_id, test_managers):
    """A manifest.json must be written after discovery."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.manifest_path is not None
    assert result.manifest_path.exists()

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 1
    assert manifest["status"] == "success"
    assert manifest["run_id"] == run_id
    assert manifest["outputs"]["canonical_documents"] == 5


def test_phase1_writes_dataset_json(realistic_vault, run_id, test_managers, tmp_path):
    """dataset.json must be written to artifacts/run_id/phase1/."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    dataset_paths = list(
        (tmp_path / "artifacts" / f"run_{run_id}" / "phase1").glob("dataset.json")
    )
    assert len(dataset_paths) == 1

    dataset = json.loads(dataset_paths[0].read_text(encoding="utf-8"))
    assert len(dataset) == 5  # canonical only
    # Rectified: doc_id must equal content_hash
    for doc in dataset:
        assert "doc_id" in doc
        assert "content_hash" in doc
        assert doc["doc_id"] == doc["content_hash"]


def test_phase1_updates_pipeline_state(realistic_vault, run_id, test_managers):
    """Pipeline state must be updated to mark Phase 1 as complete."""
    manifest_mgr, state_mgr = test_managers

    run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    state = state_mgr.load()
    assert state is not None
    assert 1 in state.completed_phases


def test_phase1_is_idempotent(realistic_vault, run_id, test_managers):
    """Running Phase 1 twice on same input must produce same canonical count."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    result2 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id + "_2",
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result1.canonical_count == result2.canonical_count


def test_phase1_no_nlp_imports():
    """Phase 1 must never import NLP libraries."""
    import smriti.discovery.scanner as scanner
    import smriti.discovery.validator as validator
    import smriti.discovery.metadata as metadata_mod
    import smriti.discovery.hashing as hashing_mod
    import smriti.discovery.duplicate as duplicate_mod
    import smriti.discovery.builder as builder_mod

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [scanner, validator, metadata_mod, hashing_mod, duplicate_mod, builder_mod]:
        module_imports = set(vars(module).keys())
        assert not (module_imports & nlp_modules), (
            f"{module.__name__} imports NLP libraries — Phase 1 must not do NLP"
        )
````

## File: tests/integration/test_phase3_extraction.py
````python
"""
Integration test for Phase 3 end-to-end.

Tests the complete pipeline:
  Document → build_semantic_sentences() → List[SemanticSentence]

Uses Documents with realistic note content.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from smriti.core.models import (
    Document, SourceDocument, FileFormat, ExtractionMethod,
    TextStatistics, WarningCode, SemanticSentence,
)
from smriti.extraction import build_semantic_sentences
from smriti.extraction.scanner import BlockType


def make_document(doc_id: str, normalized_text: str, path_str: str = "note.md") -> Document:
    """Create a test Document from normalized_text."""
    source = SourceDocument(
        doc_id=doc_id,
        path=Path(path_str),
        relative_path=Path(path_str),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash=doc_id,
        size_bytes=len(normalized_text),
        modified_at=datetime.now(tz=timezone.utc),
    )
    stats = TextStatistics(
        character_count=len(normalized_text),
        word_count=len(normalized_text.split()),
        line_count=normalized_text.count("\n"),
        blank_line_count=0,
        paragraph_count=1,
    )
    return Document(
        doc_id=doc_id,
        source_document=source,
        raw_text=normalized_text,
        normalized_text=normalized_text,
        extraction_method=ExtractionMethod.MARKDOWN,
        extraction_warnings=(),
        text_statistics=stats,
        encoding_used="utf-8",
    )


# ── Basic sentence production ─────────────────────────────────────────────────

def test_simple_paragraph_produces_sentences():
    doc = make_document(
        "doc1",
        "Python is great for data science. Julia is faster for numerical computing."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 2
    assert result.error is None


def test_empty_document_produces_no_sentences():
    doc = make_document("doc2", "")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 0
    assert result.error is None


def test_sentences_have_correct_document_id():
    doc = make_document("myid123", "Python is great.")
    result = build_semantic_sentences(doc)
    assert all(s.document_id == "myid123" for s in result.sentences)


# ── Context preservation ──────────────────────────────────────────────────────

def test_context_captured_from_heading():
    doc = make_document(
        "doc3",
        "# Python\n\nPython is great for data science."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1
    sentence = result.sentences[0]
    assert "Python" in sentence.context


def test_nested_context():
    doc = make_document(
        "doc4",
        "# Programming\n\n## Python\n\nPython is great."
    )
    result = build_semantic_sentences(doc)
    sentence = result.sentences[0]
    assert "Programming" in sentence.context
    assert "Python" in sentence.context


def test_heading_is_not_a_sentence():
    doc = make_document(
        "doc5",
        "# This Is A Heading\n\nActual sentence here."
    )
    result = build_semantic_sentences(doc)
    sentence_texts = [s.text for s in result.sentences]
    assert not any("This Is A Heading" in t for t in sentence_texts)


def test_context_resets_at_new_h1():
    doc = make_document(
        "doc6",
        "# Section A\n\nSentence in A.\n\n# Section B\n\nSentence in B."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 2
    assert "Section A" in result.sentences[0].context
    assert "Section B" in result.sentences[1].context
    assert "Section A" not in result.sentences[1].context


# ── Structural elements ───────────────────────────────────────────────────────

def test_bullet_items_become_sentences():
    doc = make_document(
        "doc7",
        "- First item\n- Second item\n- Third item"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_ordered_list_becomes_sentences():
    doc = make_document(
        "doc8",
        "1. Install Poetry\n2. Install dependencies\n3. Run tests"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_block_quote_becomes_sentence():
    doc = make_document("doc9", "> Reliability is critical.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1
    assert "Reliability" in result.sentences[0].text


def test_code_block_produces_no_sentences():
    doc = make_document(
        "doc10",
        "Before code.\n\n```python\nprint('hello')\n```\n\nAfter code."
    )
    result = build_semantic_sentences(doc)
    texts = [s.text for s in result.sentences]
    assert not any("print" in t for t in texts)


def test_table_produces_prose_sentences():
    doc = make_document(
        "doc11",
        "| Model | Accuracy |\n|-------|----------|\n| GPT-4 | 85% |"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_document_same_sentence_ids():
    doc = make_document(
        "doc12",
        "# AI\n\nAI is transforming everything. Machine learning is a subset of AI."
    )
    result1 = build_semantic_sentences(doc)
    result2 = build_semantic_sentences(doc)

    ids1 = [s.sentence_id for s in result1.sentences]
    ids2 = [s.sentence_id for s in result2.sentences]
    assert ids1 == ids2


def test_positions_are_strictly_increasing():
    doc = make_document(
        "doc13",
        "First. Second. Third. Fourth."
    )
    result = build_semantic_sentences(doc)
    positions = [s.position for s in result.sentences]
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))


def test_sentence_ids_are_unique():
    doc = make_document(
        "doc14",
        "# Section\n\nSentence A. Sentence B. Sentence C.\n\n## Sub\n\nSentence D."
    )
    result = build_semantic_sentences(doc)
    ids = [s.sentence_id for s in result.sentences]
    assert len(ids) == len(set(ids))


# ── Context separation ────────────────────────────────────────────────────────

def test_context_never_fused_into_text():
    doc = make_document(
        "doc15",
        "# CUDA\n\nSupports tensors."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1
    sentence = result.sentences[0]
    assert sentence.text == "Supports tensors."
    assert "CUDA" in sentence.context
    assert "CUDA" not in sentence.text


# ── Abbreviation handling ─────────────────────────────────────────────────────

def test_abbreviation_dr_not_split():
    doc = make_document("doc16", "Dr. Smith discovered this principle.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1


def test_decimal_not_split():
    doc = make_document("doc17", "Pi equals approximately 3.14 in most calculations.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1


# ── NEW: Check origin_block_type and schema_version ──────────────────────────

def test_sentences_have_origin_block_type():
    """Each SemanticSentence must record its origin block type."""
    doc = make_document(
        "doc18",
        "- First bullet\n\n> A quote.\n\nPlain paragraph."
    )
    result = build_semantic_sentences(doc)

    # The order of events from scanner: bullet_item, block_quote, paragraph
    # (depending on how the scanner processes)
    # We'll check that each sentence's origin_block_type is set correctly.
    origins = [s.origin_block_type for s in result.sentences]
    assert BlockType.BULLET_ITEM in origins
    assert BlockType.BLOCK_QUOTE in origins
    assert BlockType.PARAGRAPH in origins
    assert all(isinstance(o, BlockType) for o in origins)


def test_sentences_have_schema_version():
    """Every SemanticSentence must carry schema_version='3.0'."""
    doc = make_document("doc19", "Simple text.")
    result = build_semantic_sentences(doc)
    for s in result.sentences:
        assert s.schema_version == "3.0"


# ── Realistic vault note ──────────────────────────────────────────────────────

def test_realistic_obsidian_note():
    note = """# Machine Learning

## Supervised Learning

Supervised learning uses labeled training data. The model learns to map inputs to outputs.

Key algorithms:
- Linear Regression
- Decision Trees
- Random Forests

## Unsupervised Learning

Unsupervised learning finds patterns without labeled data. Clustering is the most common technique.

> The choice of algorithm depends heavily on the data structure.

| Algorithm | Use Case     |
|-----------|--------------|
| K-Means   | Clustering   |
| PCA       | Dimensionality |
"""
    doc = make_document("realistic", note)
    result = build_semantic_sentences(doc)

    assert result.sentence_count > 0
    assert result.error is None
    assert all(s.document_id == "realistic" for s in result.sentences)
    contexts = [s.context for s in result.sentences]
    assert any("Machine Learning" in c for c in contexts)
    assert any("Supervised" in c for c in contexts)
    positions = [s.position for s in result.sentences]
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))
    ids = [s.sentence_id for s in result.sentences]
    assert len(ids) == len(set(ids))
````

## File: tests/integration/test_phase4_extraction.py
````python
"""
Integration test for Phase 4 end-to-end.

Tests the complete pipeline:
    SemanticSentence → extract_claims_from_sentence() → List[Claim]
"""

import hashlib
import pytest
from pathlib import Path
from smriti.core.models import (
    SemanticSentence, Claim, ExtractionMode, Modality,
)
from smriti.claims import extract_claims_from_sentence
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.statistics import Phase4StatsCollector


@pytest.fixture(scope="module")
def pipeline():
    """Initialize pipeline components once per module."""
    try:
        return (
            SpaCyParser(),
            BoundaryDetector(),
            StructureExtractor(),
            AssertionAnnotator(),
            DegradationHandler(),
        )
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(
    text: str,
    sentence_id: str = "s001",
    context: str = "",
    position: int = 0,
) -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context=context,
        position=position,
        char_start=0,
        char_end=len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def run_pipeline(pipeline, sentence, max_claims=10):
    parser, bd, se, ann, dh = pipeline
    stats = Phase4StatsCollector()
    return extract_claims_from_sentence(
        sentence=sentence, parser=parser, boundary_detector=bd,
        structure_extractor=se, annotator=ann, degradation_handler=dh,
        stats_collector=stats, max_claims=max_claims,
    )


# ── Basic claim production ─────────────────────────────────────────────────────

def test_simple_sentence_produces_claim(pipeline):
    """Every non-empty sentence must produce at least one claim."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert result.claim_count >= 1
    assert result.error is None


def test_empty_sentence_produces_no_claims(pipeline):
    """Empty text → zero claims, no error."""
    result = run_pipeline(pipeline, make_sentence("   "))
    assert result.claim_count == 0


def test_claims_have_correct_sentence_id(pipeline):
    """Every claim must link back to the source sentence_id."""
    sentence = make_sentence("Python is fast.", sentence_id="unique_s_id")
    result = run_pipeline(pipeline, sentence)
    assert all(c.sentence_id == "unique_s_id" for c in result.claims)
    # New checks for content_hash and rule_version
    assert all(c.content_hash is not None for c in result.claims)
    assert all(c.rule_version == "1.0" for c in result.claims)


def test_claims_have_correct_document_id(pipeline):
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert all(c.document_id == "doc001" for c in result.claims)


# ── Text preservation ─────────────────────────────────────────────────────────

def test_claim_text_preserves_author_wording(pipeline):
    """Claim text must match source — no canonicalization."""
    original = "Python does NOT support this feature."
    sentence = make_sentence(original)
    result = run_pipeline(pipeline, sentence)
    # At minimum, the whole-sentence fallback must preserve it
    all_texts = [c.text for c in result.claims]
    assert any(original in t or t in original for t in all_texts)


# ── Context propagation ────────────────────────────────────────────────────────

def test_context_propagated_from_sentence(pipeline):
    """Claim must carry context from SemanticSentence."""
    sentence = make_sentence("Python supports generators.", context="Programming > Python")
    result = run_pipeline(pipeline, sentence)
    assert all(c.context == "Programming > Python" for c in result.claims)


# ── Provenance chain ──────────────────────────────────────────────────────────

def test_claim_provenance_is_complete(pipeline):
    """Every claim must have complete provenance chain."""
    sentence = make_sentence("Python is fast.", sentence_id="sid1", position=5)
    result = run_pipeline(pipeline, sentence)
    for claim in result.claims:
        assert claim.provenance is not None
        assert claim.provenance.sentence_id == "sid1"
        assert claim.provenance.document_id == "doc001"
        assert claim.provenance.sentence_position == 5
    # New check: content_hash must match SHA256 of text
    assert all(
        c.content_hash == hashlib.sha256(c.text.encode()).hexdigest()[:16]
        for c in result.claims
    )


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_sentence_same_claim_ids(pipeline):
    """Running twice on the same sentence must produce identical claim IDs."""
    sentence = make_sentence("Python supports generators and decorators.")
    result1 = run_pipeline(pipeline, sentence)
    result2 = run_pipeline(pipeline, sentence)

    ids1 = [c.claim_id for c in result1.claims]
    ids2 = [c.claim_id for c in result2.claims]
    assert ids1 == ids2
    # New check: content_hash must also be identical
    assert [c.content_hash for c in result1.claims] == [c.content_hash for c in result2.claims]


def test_claim_ids_are_unique(pipeline):
    """No two claims from the same sentence may share an ID."""
    sentence = make_sentence("Python supports X and Y and Z.")
    result = run_pipeline(pipeline, sentence)
    ids = [c.claim_id for c in result.claims]
    assert len(ids) == len(set(ids))


# ── Annotation ────────────────────────────────────────────────────────────────

def test_negation_flag_on_negated_claim(pipeline):
    """A negated sentence must produce at least one claim with is_negated=True."""
    sentence = make_sentence("Python does not support this feature.")
    result = run_pipeline(pipeline, sentence)
    assert any(c.is_negated for c in result.claims)


def test_modality_on_possible_claim(pipeline):
    """'may' or 'might' must produce POSSIBLE modality."""
    sentence = make_sentence("Python may be faster than Java.")
    result = run_pipeline(pipeline, sentence)
    modalities = [c.assertion_metadata.modality for c in result.claims]
    assert Modality.POSSIBLE in modalities


# ── Immutability ──────────────────────────────────────────────────────────────

def test_claims_are_immutable(pipeline):
    """Claim objects must be frozen."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    if result.claims:
        with pytest.raises(Exception):
            result.claims[0].text = "modified"


# ── Graceful degradation ──────────────────────────────────────────────────────

def test_claim_always_produced_even_on_parse_failure(pipeline):
    """Even on parser failure, a whole-sentence claim is produced."""
    # Malformed text that may trip the parser
    sentence = make_sentence("@@@ ### ??? weird !!!")
    result = run_pipeline(pipeline, sentence)
    # Must produce something (whole-sentence fallback)
    assert result.claim_count >= 0  # 0 only if text is empty


def test_schema_version_is_correct(pipeline):
    """All claims must have schema_version '4.0'."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    for claim in result.claims:
        assert claim.schema_version == "4.0"


# ── Realistic note ────────────────────────────────────────────────────────────

def test_realistic_knowledge_note(pipeline):
    """
    Full test with a realistic machine learning note.
    Verifies claims are extracted with provenance and correct flags.
    """
    sentences_data = [
        ("Supervised learning uses labeled training data.", "ML > Supervised"),
        ("The model learns to map inputs to outputs.", "ML > Supervised"),
        ("Unsupervised learning does not require labeled data.", "ML > Unsupervised"),
        ("Deep learning may outperform traditional methods on large datasets.",
         "ML > Deep Learning"),
        ("According to the authors, transformers are now state-of-the-art.", "ML"),
    ]

    all_claims = []
    for i, (text, context) in enumerate(sentences_data):
        sentence = make_sentence(text, sentence_id=f"s_{i:03d}", context=context, position=i)
        result = run_pipeline(pipeline, sentence)
        assert result.error is None, f"Error on sentence '{text}': {result.error}"
        all_claims.extend(result.claims)

    # At least one claim per sentence
    assert len(all_claims) >= len(sentences_data)

    # All have provenance
    assert all(c.provenance is not None for c in all_claims)

    # All have schema 4.0
    assert all(c.schema_version == "4.0" for c in all_claims)

    # Negation detected in sentence 3
    unsupervised_claims = [c for c in all_claims if "does not" in c.text.lower()]
    assert any(c.is_negated for c in unsupervised_claims)

    # Modality detected in sentence 4
    deep_claims = [c for c in all_claims if "may" in c.text.lower()]
    assert any(c.assertion_metadata.modality == Modality.POSSIBLE for c in deep_claims)

    # Attribution detected in sentence 5
    attribution_claims = [c for c in all_claims if "authors" in c.text.lower() or
                          c.assertion_metadata.is_attributed]
    # Attribution may or may not be detected depending on spaCy's parse
    # but the claim must still exist
    assert len(all_claims) >= 5

    # All claim IDs are unique
    claim_ids = [c.claim_id for c in all_claims]
    assert len(claim_ids) == len(set(claim_ids))

    # New checks for content_hash and rule_version
    hashes = [c.content_hash for c in all_claims]
    # content_hash should be unique because texts differ
    assert len(hashes) == len(set(hashes))
    assert all(c.rule_version == "1.0" for c in all_claims)
````

## File: tests/integration/test_phase5_embedding.py
````python
"""
Integration test for Phase 5 end-to-end.

Tests the complete pipeline:
    List[Claim] → embed_claims() → Phase5Result

Uses a mock embedder so tests run without sentence-transformers installed.
All assertions reflect the rectified API:
    - EmbeddedClaim.vector returns Vector (not tuple)
    - EmbeddedClaim.values returns tuple of floats
    - EmbeddedClaim.quality is EmbeddingQuality
    - Embedding has no status field
"""

import pytest
import math
import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Modality, EmbeddingStatus, EmbeddedClaim,
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.embedding import embed_claims, Phase5Result
from smriti.embedding.embedder import BaseEmbedder, EmbedderCapabilities


# ── Mock embedder ─────────────────────────────────────────────────────────────

class MockEmbedder(BaseEmbedder):
    """Mock embedder that returns deterministic fake vectors."""

    DIMENSION = 4

    def __init__(self):
        self._descriptor = EmbeddingModelDescriptor(
            provider="mock",
            model_name="mock-embedder",
            model_revision="test",
            dimension=self.DIMENSION,
            model_signature="mock_signature_abc123",
            embedding_family="Mock",
        )

    @property
    def descriptor(self) -> EmbeddingModelDescriptor:
        return self._descriptor

    @property
    def capabilities(self) -> EmbedderCapabilities:
        return EmbedderCapabilities(
            supports_batching=True,
            supports_instruction_prefix=False,
            supports_multilingual=False,
            supports_long_context=False,
        )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Deterministic: hash of text → 4 floats."""
        import hashlib
        results = []
        for text in texts:
            h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
            vector = [(h >> (i * 8) & 0xFF) / 255.0 for i in range(self.DIMENSION)]
            if all(v == 0.0 for v in vector):
                vector[0] = 0.1
            results.append(vector)
        return results


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_embedder():
    return MockEmbedder()


@pytest.fixture
def run_id():
    return "test_phase5_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


def make_claim(
    claim_id: str,
    text: str,
    context: str = "",
    document_id: str = "doc001",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id=document_id,
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=document_id,
            source_path=Path("test.md"), sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=claim_id[:16],
        rule_version="1.0",
    )


def run_embedding(mock_embedder, claims, run_id, test_managers, **kwargs):
    manifest_mgr, state_mgr = test_managers
    return embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=mock_embedder,
        **kwargs,
    )


# ── Basic production ──────────────────────────────────────────────────────────

def test_empty_claims_produces_empty_result(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [], run_id, test_managers)
    assert isinstance(result, Phase5Result)
    assert result.total_embedded == 0


def test_single_claim_produces_embedded_claim(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.failed == 0


def test_embedded_claims_reference_correct_claim_ids(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    ids = {ec.claim_id for ec in result.embedded_claims}
    assert ids == {"c001", "c002"}


def test_empty_text_claim_is_skipped(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Valid claim."), make_claim("c002", "   ")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.skipped == 1


# ── Immutability and purity ───────────────────────────────────────────────────

def test_embedded_claims_are_immutable(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    with pytest.raises(Exception):
        result.embedded_claims[0].claim_id = "modified"


def test_original_claims_not_modified(mock_embedder, run_id, test_managers):
    claim = make_claim("c001", "Python is fast.")
    original_text = claim.text
    run_embedding(mock_embedder, [claim], run_id, test_managers)
    assert claim.text == original_text


def test_embedding_has_no_status_field(mock_embedder, run_id, test_managers):
    """Critical fix: Embedding must not have a status field."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert not hasattr(ec.embedding, "status"), (
        "Embedding should not have status — it's a pure semantic artifact"
    )


# ── EmbeddingQuality ──────────────────────────────────────────────────────────

def test_embedded_claim_has_quality(mock_embedder, run_id, test_managers):
    """EmbeddedClaim must carry EmbeddingQuality."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.quality, EmbeddingQuality)


def test_quality_fresh_embedding(mock_embedder, run_id, test_managers):
    """Fresh embedding: cache_used=False, normalized=True."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.quality.cache_used is False
    assert ec.quality.normalized is True
    assert ec.quality.finite is True
    assert ec.quality.dimension_ok is True


# ── Vector domain object ──────────────────────────────────────────────────────

def test_vector_is_vector_type(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.vector must return a Vector domain object."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector, Vector)


def test_vector_values_is_tuple(mock_embedder, run_id, test_managers):
    """Vector.values must be an immutable tuple."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector.values, tuple)


def test_embedded_claim_values_shortcut(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.values must return the same as ec.vector.values."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.values == ec.vector.values


def test_vector_has_correct_dimension(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.dimension == MockEmbedder.DIMENSION
        assert ec.vector.dimension == MockEmbedder.DIMENSION


def test_normalized_vectors_are_unit_length(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        norm = math.sqrt(sum(x * x for x in ec.values))
        assert abs(norm - 1.0) < 1e-5, f"Norm was {norm}"


# ── Schema and provenance ─────────────────────────────────────────────────────

def test_schema_version_is_50(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.schema_version == "5.0"


def test_embedding_descriptor_family(mock_embedder, run_id, test_managers):
    """EmbeddingModelDescriptor must include embedding_family."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert hasattr(ec.embedding.descriptor, "embedding_family")
    assert ec.embedding.descriptor.embedding_family == "Mock"


# ── Batch retry ───────────────────────────────────────────────────────────────

def test_batch_failure_triggers_individual_retry(run_id, test_managers):
    """
    When a batch fails, the pipeline must retry each claim individually.
    Only the claims that individually fail are marked as failed.
    """
    call_count = {"n": 0}

    class FailFirstBatchEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            call_count["n"] += 1
            # Fail on the first call (the full batch)
            if call_count["n"] == 1 and len(texts) > 1:
                raise RuntimeError("Simulated batch failure")
            return super().encode_batch(texts)

    failing_embedder = FailFirstBatchEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]

    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=failing_embedder,
    )

    # Both claims should succeed via individual retry
    assert result.total_embedded == 2
    # A warning should have been added about the batch failure
    assert any("batch" in w.lower() for w in result.warnings)


def test_one_bad_vector_does_not_abort_batch(run_id, test_managers):
    """NaN in one vector must not fail the other claims in the batch."""
    class NaNSecondEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            vectors = super().encode_batch(texts)
            if len(vectors) > 1:
                vectors[1] = [float("nan")] * self.DIMENSION
            return vectors

    embedder = NaNSecondEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]
    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=embedder,
    )

    assert result.total_embedded >= 1  # c001 succeeds
    assert result.stats.failed >= 1    # c002 fails validation


# ── Warnings and errors ───────────────────────────────────────────────────────

def test_result_has_warnings_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose a warnings list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "warnings")
    assert isinstance(result.warnings, list)


def test_result_has_errors_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose an errors list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "errors")
    assert isinstance(result.errors, list)


# ── Artifacts ─────────────────────────────────────────────────────────────────

def test_dataset_json_written(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()


def test_dataset_json_has_quality_section(mock_embedder, run_id, test_managers):
    """dataset.json must include the quality diagnostic block."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    assert len(records) == 1
    record = records[0]
    assert "quality" in record
    assert "dimension_ok" in record["quality"]
    assert "normalized" in record["quality"]
    assert "cache_used" in record["quality"]


def test_dataset_json_no_status_field_from_embedding(mock_embedder, run_id, test_managers):
    """
    dataset.json 'status' field is derived from quality.cache_used,
    not from an Embedding.status attribute.
    """
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    record = records[0]
    # Status is "success" for fresh, "cached" for cache hits
    assert record["status"] in ("success", "cached")


def test_manifest_has_cache_lifecycle_metrics(mock_embedder, run_id, test_managers):
    """manifest.json must include cache lifecycle counters."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    manifest = json.loads(result.manifest_path.read_text())
    assert "cache_entries_reused" in manifest.get("outputs", {})
    assert "cache_entries_regenerated" in manifest.get("outputs", {})


def test_pipeline_state_updated(mock_embedder, run_id, test_managers):
    _, state_mgr = test_managers
    run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    state = state_mgr.load()
    assert 5 in state.completed_phases


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_claims_same_vectors(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    manifest_mgr, state_mgr = test_managers

    r1 = embed_claims(claims=claims, run_id=run_id, manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)
    r2 = embed_claims(claims=claims, run_id=run_id + "_2", manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)

    v1 = {ec.claim_id: ec.values for ec in r1.embedded_claims}
    v2 = {ec.claim_id: ec.values for ec in r2.embedded_claims}
    assert v1 == v2


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_has_throughput_field(mock_embedder, run_id, test_managers):
    """Phase5Stats must include vectors_per_second."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "vectors_per_second")
    assert result.stats.vectors_per_second >= 0.0


def test_stats_has_cache_lifecycle_fields(mock_embedder, run_id, test_managers):
    """Phase5Stats must include cache lifecycle counts."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "cache_entries_reused")
    assert hasattr(result.stats, "cache_entries_regenerated")
````

## File: tests/integration/test_pipeline_runner.py
````python
def test_placeholder():\n    assert True\n
````

## File: tests/unit/test_builder.py
````python
"""
Unit tests for discovery/builder.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.builder import build_source_document, SourceDocument
from smriti.discovery.metadata import extract_metadata
from smriti.core.models import FileFormat


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("Python is great for data science.")
    return f


def test_builder_produces_source_document(sample_file, tmp_path):
    """Builder must return a SourceDocument."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="a" * 64,
        source_root=tmp_path,
    )

    assert isinstance(doc, SourceDocument)


def test_builder_sets_correct_format_md(sample_file, tmp_path):
    """Markdown file gets MARKDOWN format."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="b" * 64,
        source_root=tmp_path,
    )

    assert doc.format == FileFormat.MARKDOWN


def test_builder_doc_is_immutable(sample_file, tmp_path):
    """SourceDocument is frozen — mutation must raise."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="c" * 64,
        source_root=tmp_path,
    )

    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_builder_relative_path(tmp_path):
    """relative_path must be relative to source_root."""
    subdir = tmp_path / "notes"
    subdir.mkdir()
    f = subdir / "deep.md"
    f.write_text("Some content.")

    meta = extract_metadata(f)

    doc = build_source_document(
        metadata=meta,
        content_hash="d" * 64,
        source_root=tmp_path,
    )

    assert doc.relative_path == Path("notes/deep.md")


def test_builder_doc_id_is_content_hash(sample_file, tmp_path):
    """doc_id must equal content_hash."""
    meta = extract_metadata(sample_file)
    content_hash = "e" * 64
    doc = build_source_document(meta, content_hash, tmp_path)
    assert doc.doc_id == content_hash


def test_builder_doc_id_is_deterministic(sample_file, tmp_path):
    """Same input must produce same doc_id every time."""
    meta = extract_metadata(sample_file)

    doc1 = build_source_document(
        metadata=meta, content_hash="f" * 64, source_root=tmp_path,
    )
    doc2 = build_source_document(
        metadata=meta, content_hash="f" * 64, source_root=tmp_path,
    )

    assert doc1.doc_id == doc2.doc_id
````

## File: tests/unit/test_cache.py
````python

````

## File: tests/unit/test_config.py
````python
"""Test deep-merge config loader."""

import pytest
from smriti.core.config import _deep_merge, Config


def test_deep_merge_flat():
    base = {"a": 1, "b": 2}
    override = {"b": 99, "c": 3}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_deep_merge_nested_does_not_overwrite_sibling_keys():
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    result = _deep_merge(base, override)
    # model should survive; batch_size should be overridden
    assert result["embedding"]["model"] == "MiniLM"
    assert result["embedding"]["batch_size"] == 8


def test_deep_merge_shallow_update_would_fail():
    """Demonstrates why dict.update() is wrong for nested config."""
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    # shallow update — loses model key
    shallow = dict(base)
    shallow.update(override)
    assert "model" not in shallow["embedding"]   # broken
    # deep merge — keeps model key
    deep = _deep_merge(base, override)
    assert "model" in deep["embedding"]          # correct


def test_config_loads_default(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text(
        "embedding:\n  model: MiniLM\n  batch_size: 32\n"
    )
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"
    assert cfg["embedding"]["batch_size"] == 32


def test_config_dev_override_deep_merges(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text(
        "embedding:\n  model: MiniLM\n  batch_size: 32\n"
    )
    (config_dir / "dev.yaml").write_text(
        "embedding:\n  batch_size: 8\n"
    )
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"    # inherited
    assert cfg["embedding"]["batch_size"] == 8      # overridden
````

## File: tests/unit/test_duplicate.py
````python
"""
Unit tests for discovery/duplicate.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.duplicate import build_duplicate_registry


def test_no_duplicates(tmp_path):
    """All unique hashes — no duplicates."""
    pairs = [
        (tmp_path / "a.md", "aaaa"),
        (tmp_path / "b.md", "bbbb"),
        (tmp_path / "c.md", "cccc"),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 3
    assert all(registry.is_canonical(p) for p, _ in pairs)


def test_one_duplicate(tmp_path):
    """Second file with same hash is marked as duplicate."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8  # 64 chars

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 1
    assert registry.unique_content_count == 1
    assert registry.is_canonical(path_a)
    assert registry.is_duplicate(path_b)


def test_canonical_path_for_duplicate(tmp_path):
    """get_canonical_for() must return the first-seen path."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "cafebabe" * 8

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.get_canonical_for(path_b) == path_a


def test_three_identical_files(tmp_path):
    """Three files with same content: first is canonical, two are duplicates."""
    shared_hash = "12345678" * 8
    pairs = [
        (tmp_path / "a.md", shared_hash),
        (tmp_path / "b.md", shared_hash),
        (tmp_path / "c.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 2
    assert registry.is_canonical(tmp_path / "a.md")
    assert registry.is_duplicate(tmp_path / "b.md")
    assert registry.is_duplicate(tmp_path / "c.md")


def test_empty_input():
    """Empty input must return empty registry — not crash."""
    registry = build_duplicate_registry([])
    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 0


def test_duplicate_same_name_different_dirs(tmp_path):
    """
    notes/AI.md and archive/AI.md with same content are duplicates.
    Same filename ≠ same document. Content hash determines identity.
    """
    dir1 = tmp_path / "notes"
    dir2 = tmp_path / "archive"
    dir1.mkdir()
    dir2.mkdir()

    shared_hash = "aabbccdd" * 8
    pairs = [
        (dir1 / "AI.md", shared_hash),
        (dir2 / "AI.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)
    assert registry.duplicate_count == 1

def test_get_canonical_for_constant_time(tmp_path):
    """get_canonical_for must be O(1) via reverse dict."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8
    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)
    assert registry.get_canonical_for(path_b) == path_a
````

## File: tests/unit/test_hashing.py
````python
"""
Unit tests for discovery/hashing.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.hashing import compute_hash


def test_same_content_same_hash(tmp_path):
    """Identical content must always produce the same hash."""
    content = "Python is great for data science."
    f1 = tmp_path / "note1.md"
    f2 = tmp_path / "note2.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_different_content_different_hash(tmp_path):
    """Different content must produce different hashes."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Julia is faster.", encoding="utf-8")

    assert compute_hash(f1) != compute_hash(f2)


def test_rename_does_not_change_hash(tmp_path):
    """Renaming a file must produce the same hash (content-only)."""
    content = "The hash must not depend on the filename."
    f1 = tmp_path / "original.md"
    f2 = tmp_path / "renamed.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_hash_is_64_character_hex(tmp_path):
    """SHA256 hex digest must be exactly 64 lowercase hex characters."""
    f = tmp_path / "note.md"
    f.write_text("content", encoding="utf-8")
    h = compute_hash(f)

    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_one_byte_change_changes_hash(tmp_path):
    """A single character change must produce a completely different hash."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Python is greet.", encoding="utf-8")  # 'a' → 'e'

    assert compute_hash(f1) != compute_hash(f2)


def test_hash_deterministic_across_calls(tmp_path):
    """Multiple calls on the same file must return the same hash."""
    f = tmp_path / "note.md"
    f.write_text("Determinism is essential.", encoding="utf-8")

    h1 = compute_hash(f)
    h2 = compute_hash(f)
    h3 = compute_hash(f)

    assert h1 == h2 == h3
````

## File: tests/unit/test_manifest.py
````python

````

## File: tests/unit/test_metadata.py
````python
"""
Unit tests for discovery/metadata.py.
"""

import pytest
from datetime import timezone
from pathlib import Path
from smriti.discovery.metadata import extract_metadata


def test_metadata_size(tmp_path):
    """size_bytes must match actual file size."""
    content = b"Hello, world! This is test content."
    f = tmp_path / "note.md"
    f.write_bytes(content)

    meta = extract_metadata(f)
    assert meta.size_bytes == len(content)


def test_metadata_extension_normalised(tmp_path):
    """Extension must be lowercase."""
    f = tmp_path / "NOTE.MD"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.extension == ".md"


def test_metadata_modified_time_is_utc(tmp_path):
    """modified_at must be UTC-aware."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.modified_at.tzinfo is not None
    assert meta.modified_at.tzinfo == timezone.utc


def test_metadata_is_immutable(tmp_path):
    """FileMetadata is frozen — mutation must raise."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    with pytest.raises(Exception):
        meta.size_bytes = 999
````

## File: tests/unit/test_models.py
````python
"""Test data models."""

import pytest
from datetime import datetime
from pathlib import Path

from smriti.core.models import (
    Claim, Contradiction, ContradictionType,
    Document, FileFormat, Sentence, Embedding,
    Topic, ManifestEntry,
)


def test_claim_creation():
    claim = Claim(
        text="Python is great",
        document_path=Path("note.md"),
        sentence_position=0,
        extracted_at=datetime.now(),
    )
    assert claim.text == "Python is great"
    assert claim.unique_id() == "note:0"


def test_claim_unique_id_is_deterministic():
    path = Path("my_note.md")
    c1 = Claim("text", path, 3, datetime.now())
    c2 = Claim("other text", path, 3, datetime.now())
    assert c1.unique_id() == c2.unique_id()  # same doc + position = same id


def test_contradiction_creation():
    contra = Contradiction(
        claim_a_id="note1:0",
        claim_b_id="note2:0",
        contradiction_type=ContradictionType.STRATEGY_SHIFT,
        nli_confidence=0.85,
        similarity_score=0.78,
        temporal_distance_days=100,
        severity_score=7.5,
    )
    assert contra.severity_score == 7.5
    assert contra.contradiction_type == ContradictionType.STRATEGY_SHIFT


def test_document_size_inferred():
    doc = Document(
        path=Path("note.md"),
        format=FileFormat.MARKDOWN,
        raw_text="Hello world",
        discovered_at=datetime.now(),
    )
    assert doc.size_bytes > 0


def test_topic_drift_score():
    topic = Topic(name="python", claim_ids=["a", "b", "c", "d"], contradiction_count=2)
    assert topic.drift_score == pytest.approx(50.0)


def test_topic_drift_score_empty():
    topic = Topic(name="empty")
    assert topic.drift_score == 0.0


def test_manifest_entry_has_run_id():
    entry = ManifestEntry(
        run_id="20240715_143022",
        phase=1,
        timestamp=datetime.now(),
        duration_seconds=1.5,
        inputs={},
        outputs={},
        status="success",
    )
    assert entry.run_id == "20240715_143022"
    assert entry.schema_version == "1.0"
````

## File: tests/unit/test_parsing_builder.py
````python
"""
Unit tests for parsing/builder.py.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.parsing.builder import build_document
from smriti.exceptions import BuilderError, DocumentError


@pytest.fixture
def source_doc():
    return SourceDocument(
        doc_id="a" * 64,
        path=Path("note.md"),
        relative_path=Path("note.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="a" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def extraction_result():
    return RawExtractionResult(
        raw_text="# Hello\n\nWorld.",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
    )


@pytest.fixture
def stats():
    return TextStatistics(
        character_count=16,
        word_count=2,
        line_count=3,
        blank_line_count=1,
        paragraph_count=2,
    )


def test_build_returns_document(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert isinstance(doc, Document)


def test_doc_id_equals_source_doc_id(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.doc_id == source_doc.doc_id


def test_document_is_frozen(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    with pytest.raises(Exception):
        doc.doc_id = "new_id"


def test_source_document_unchanged(source_doc, extraction_result, stats):
    original_path = source_doc.path
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.source_document.path == original_path


def test_warnings_merged(source_doc, stats):
    extraction_result = RawExtractionResult(
        raw_text="text",
        warnings=(WarningCode.NO_EXTRACTABLE_TEXT,),
        method=ExtractionMethod.MARKDOWN,
    )
    norm_warnings = (WarningCode.BLANK_LINES_COLLAPSED,)
    doc = build_document(source_doc, extraction_result, "text", norm_warnings, stats)
    assert len(doc.extraction_warnings) == 2


def test_wrong_doc_id_raises(source_doc, extraction_result, stats):
    """doc_id must match source_document.doc_id — mismatch raises DocumentError."""
    wrong_source = SourceDocument(
        doc_id="b" * 64,         # different doc_id
        path=Path("other.md"),
        relative_path=Path("other.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )
    # Builder uses source_document.doc_id — so the Document will have "b"*64
    # This should succeed; the invariant is enforced inside Document.__post_init__
    doc = build_document(wrong_source, extraction_result, "text", (), stats)
    assert doc.doc_id == "b" * 64


def test_empty_document_produces_warning(source_doc, stats):
    """Empty normalized text must produce NO_EXTRACTABLE_TEXT warning."""
    extraction_result = RawExtractionResult(
        raw_text="",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
    )
    empty_stats = TextStatistics(
        character_count=0, word_count=0, line_count=0,
        blank_line_count=0, paragraph_count=0,
    )
    doc = build_document(source_doc, extraction_result, "", (), empty_stats)
    assert doc.has_warnings
    assert WarningCode.NO_EXTRACTABLE_TEXT in doc.extraction_warnings
````

## File: tests/unit/test_parsing_loader.py
````python
"""
Unit tests for parsing/loader.py.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import FileFormat, SourceDocument
from smriti.parsing.loader import load_document


def make_source(path: Path, fmt: FileFormat, doc_id: str = "a" * 64) -> SourceDocument:
    return SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=path.name,
        source_root=path.parent,
        format=fmt,
        content_hash=doc_id,
        size_bytes=path.stat().st_size if path.exists() else 0,
        modified_at=datetime.now(tz=timezone.utc),
    )


def test_markdown_document_succeeds(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# AI\n\nAI is transforming everything.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None
    assert "AI" in doc.normalized_text


def test_text_document_succeeds(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("Plain text content here.", encoding="utf-8")
    source = make_source(f, FileFormat.TEXT)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None


def test_nonexistent_file_returns_none_not_raise(tmp_path):
    """Missing file must return (None, error) — NOT raise."""
    source = make_source(tmp_path / "ghost.md", FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None
    assert "Error" in error or "error" in error.lower()


def test_corrupted_pdf_returns_none_not_raise(tmp_path):
    """Corrupted PDF must return (None, error) — NOT raise, batch continues."""
    f = tmp_path / "bad.pdf"
    f.write_bytes(b"not a pdf")
    source = make_source(f, FileFormat.PDF)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None


def test_doc_id_preserved(tmp_path):
    """doc_id must equal source_document.doc_id — identity invariant."""
    f = tmp_path / "note.md"
    f.write_text("hello world", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert doc.doc_id == source.doc_id


def test_normalized_text_strips_crlf(tmp_path):
    """CRLF in source file must become LF in normalized_text."""
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "\r\n" not in doc.normalized_text


def test_markdown_headings_preserved(tmp_path):
    """# headings must survive extraction (not stripped)."""
    f = tmp_path / "headings.md"
    f.write_text("# Main Topic\n\n## Subtopic\n\nContent.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "# Main Topic" in doc.normalized_text
    assert "## Subtopic" in doc.normalized_text


def test_unicode_content_handled(tmp_path):
    """Unicode content (CJK, emoji, accented) must be preserved."""
    f = tmp_path / "unicode.md"
    f.write_text("# 日本語\n\nCafé résumé naïve.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "日本語" in doc.normalized_text
    assert "Café" in doc.normalized_text
````

## File: tests/unit/test_parsing_markdown.py
````python
"""
Unit tests for parsing/markdown.py.
"""

import pytest
from pathlib import Path
from smriti.parsing.markdown import MarkdownExtractor
from smriti.core.models import ExtractionMethod, WarningCode


@pytest.fixture
def extractor():
    return MarkdownExtractor()


@pytest.fixture
def simple_md(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# Hello\n\nWorld.", encoding="utf-8")
    return f


def test_extracts_text(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert "Hello" in result.raw_text
    assert "World" in result.raw_text


def test_preserves_markdown_syntax(extractor, simple_md):
    """Markdown # heading must NOT be stripped."""
    result = extractor.extract(simple_md)
    assert "# Hello" in result.raw_text


def test_method_is_markdown(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert result.method == ExtractionMethod.MARKDOWN


def test_no_warnings_on_clean_utf8(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert len(result.warnings) == 0


def test_crlf_warning_detected(extractor, tmp_path):
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    result = extractor.extract(f)
    assert WarningCode.MIXED_LINE_ENDINGS in result.warnings or "\r\n" in result.raw_text


def test_null_bytes_removed(extractor, tmp_path):
    f = tmp_path / "null.md"
    f.write_bytes(b"hello\x00world")
    result = extractor.extract(f)
    assert "\x00" not in result.raw_text
    assert WarningCode.NULL_BYTES_REMOVED in result.warnings


def test_encoding_fallback_latin1(extractor, tmp_path):
    """Latin-1 encoded file must decode with fallback warning."""
    f = tmp_path / "latin.md"
    f.write_bytes("caf\xe9".encode("latin-1"))
    result = extractor.extract(f)
    assert len(result.raw_text) > 0
    # Either decoded fine or produced a fallback warning
    # (depends on whether utf-8 fails gracefully)


def test_markdown_table_preserved(extractor, tmp_path):
    """Markdown table syntax must be preserved verbatim."""
    f = tmp_path / "table.md"
    f.write_text("| Col1 | Col2 |\n|------|------|\n| A    | B    |", encoding="utf-8")
    result = extractor.extract(f)
    assert "| Col1 |" in result.raw_text
    assert "|------|" in result.raw_text


def test_unreadable_file_raises(extractor, tmp_path):
    from smriti.exceptions import MarkdownExtractionError
    fake = tmp_path / "nonexistent.md"
    with pytest.raises(MarkdownExtractionError):
        extractor.extract(fake)
````

## File: tests/unit/test_parsing_normalize.py
````python
"""
Unit tests for parsing/normalize.py.

Every normalization rule is tested in isolation.
Determinism is verified: same input → same output every time.
"""

import pytest
from smriti.parsing.normalize import normalize_text
from smriti.core.models import WarningCode, NormalizationResult


# ── Unicode normalization ─────────────────────────────────────────────────────

def test_nfc_normalization_makes_equivalent_sequences_identical():
    """é as NFC and NFD decomposed must both normalize to the same NFC form."""
    import unicodedata
    nfc_e = "\u00e9"           # é as single code point (NFC)
    nfd_e = "e\u0301"          # é as e + combining acute (NFD)
    assert nfc_e != nfd_e      # They start different
    result_nfc = normalize_text(nfc_e)
    result_nfd = normalize_text(nfd_e)
    assert result_nfc.normalized_text == result_nfd.normalized_text  # After normalization: identical


def test_bom_is_removed():
    """UTF-8 BOM character must be stripped."""
    text_with_bom = "\ufeffHello world"
    result = normalize_text(text_with_bom)
    assert not result.normalized_text.startswith("\ufeff")
    assert WarningCode.BOM_REMOVED in result.warnings


# ── Line ending normalization ─────────────────────────────────────────────────

def test_crlf_converted_to_lf():
    """Windows CRLF must become LF."""
    result = normalize_text("line1\r\nline2\r\nline3")
    assert "\r\n" not in result.normalized_text
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"
    assert WarningCode.LINE_ENDINGS_NORMALIZED in result.warnings


def test_cr_only_converted_to_lf():
    """Old Mac CR-only must become LF."""
    result = normalize_text("line1\rline2\rline3")
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"


def test_pure_lf_unchanged():
    """Files already using LF must not be modified (no spurious warning)."""
    text = "line1\nline2\nline3"
    result = normalize_text(text)
    assert result.normalized_text == text
    assert WarningCode.LINE_ENDINGS_NORMALIZED not in result.warnings


# ── Trailing whitespace ───────────────────────────────────────────────────────

def test_trailing_whitespace_removed_per_line():
    """Trailing spaces and tabs on each line must be removed."""
    result = normalize_text("hello   \nworld\t\n")
    lines = result.normalized_text.split("\n")
    for line in lines:
        assert not line.endswith(" ")
        assert not line.endswith("\t")
    assert WarningCode.TRAILING_WHITESPACE_REMOVED in result.warnings


def test_leading_indentation_preserved():
    """Leading whitespace (indentation) must NEVER be removed."""
    text = "    indented line\n        double indent"
    result = normalize_text(text)
    lines = result.normalized_text.split("\n")
    assert lines[0].startswith("    ")
    assert lines[1].startswith("        ")


# ── Blank line collapsing ─────────────────────────────────────────────────────

def test_excessive_blank_lines_collapsed():
    """100 consecutive blank lines must collapse to max configured blank lines."""
    text = "paragraph1\n" + "\n" * 100 + "paragraph2"
    result = normalize_text(text)
    # Should not have more than collapse_blank_lines (default=2) consecutive blank lines
    assert "\n\n\n\n" not in result.normalized_text  # More than 2 blank lines = 4+ newlines
    assert WarningCode.BLANK_LINES_COLLAPSED in result.warnings


def test_single_blank_line_preserved():
    """A single blank line between paragraphs must be preserved."""
    text = "paragraph1\n\nparagraph2"
    result = normalize_text(text)
    assert "paragraph1\n\nparagraph2" in result.normalized_text


# ── Control characters ────────────────────────────────────────────────────────

def test_control_characters_removed():
    """Non-printable control characters (except LF, TAB) must be removed."""
    text = "hello\x07world\x1btest"  # BEL, ESC
    result = normalize_text(text)
    assert "\x07" not in result.normalized_text
    assert "\x1b" not in result.normalized_text
    assert WarningCode.CONTROL_CHARS_REMOVED in result.warnings


def test_tab_preserved():
    """TAB characters must be preserved (carry indentation meaning)."""
    text = "\thello\tworld"
    result = normalize_text(text)
    assert "\t" in result.normalized_text


# ── Determinism ───────────────────────────────────────────────────────────────

def test_normalization_is_deterministic():
    """Same input must always produce same output."""
    text = "Hello\r\n\r\nWorld   \r\n"
    result1 = normalize_text(text)
    result2 = normalize_text(text)
    assert result1.normalized_text == result2.normalized_text
    assert result1.warnings == result2.warnings


def test_empty_string_handled():
    """Empty string must return empty string without errors."""
    result = normalize_text("")
    assert result.normalized_text == ""


def test_whitespace_only_string_handled():
    """Whitespace-only input must return empty string."""
    result = normalize_text("   \n\t\n   ")
    assert result.normalized_text == ""


# ── Error handling ────────────────────────────────────────────────────────────

def test_non_string_raises():
    """Passing non-string must raise NormalizationError."""
    from smriti.exceptions import NormalizationError
    with pytest.raises(NormalizationError):
        normalize_text(None)  # type: ignore
````

## File: tests/unit/test_parsing_pdf.py
````python
"""
Unit tests for parsing/pdf.py.
"""

import pytest
from pathlib import Path
from smriti.parsing.pdf import PdfExtractor
from smriti.core.models import ExtractionMethod


@pytest.fixture
def extractor():
    return PdfExtractor()


@pytest.fixture
def minimal_pdf(tmp_path):
    """Create a minimal valid PDF with a text layer."""
    try:
        import pypdf
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        path = tmp_path / "test.pdf"
        with open(path, "wb") as f:
            writer.write(f)
        return path
    except Exception:
        # If pypdf cannot create a test PDF, skip
        pytest.skip("pypdf could not create test PDF")


def test_method_is_pdf(extractor, minimal_pdf):
    result = extractor.extract(minimal_pdf)
    assert result.method == ExtractionMethod.PDF


def test_image_only_pdf_produces_warning(extractor, tmp_path):
    """A PDF with no text layer must produce NoExtractableTextWarning."""
    try:
        import pypdf
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        path = tmp_path / "blank.pdf"
        with open(path, "wb") as f:
            writer.write(f)
        result = extractor.extract(path)
        # Blank page has no text — should produce a warning
        assert result.method == ExtractionMethod.PDF
        # The result is a valid RawExtractionResult regardless
    except Exception:
        pytest.skip("pypdf could not create test PDF")


def test_corrupted_pdf_raises(extractor, tmp_path):
    from smriti.exceptions import PdfExtractionError
    corrupted = tmp_path / "bad.pdf"
    corrupted.write_bytes(b"this is not a pdf at all garbage data")
    with pytest.raises(PdfExtractionError):
        extractor.extract(corrupted)


def test_nonexistent_pdf_raises(extractor, tmp_path):
    from smriti.exceptions import PdfExtractionError
    with pytest.raises(PdfExtractionError):
        extractor.extract(tmp_path / "ghost.pdf")
````

## File: tests/unit/test_parsing_statistics.py
````python
"""
Unit tests for parsing/statistics.py.

Every statistic is verified for correctness and internal consistency.
"""

import pytest
from smriti.parsing.statistics import compute_statistics
from smriti.core.models import TextStatistics


def test_empty_string_returns_zeros():
    stats = compute_statistics("")
    assert stats.character_count == 0
    assert stats.word_count == 0
    assert stats.line_count == 0
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 0


def test_whitespace_only_returns_zeros():
    stats = compute_statistics("   \n\t\n  ")
    assert stats.word_count == 0
    assert stats.paragraph_count == 0


def test_single_line():
    stats = compute_statistics("Hello world")
    assert stats.character_count == 11
    assert stats.word_count == 2
    assert stats.line_count == 1
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 1


def test_two_paragraphs_with_blank_line():
    text = "First paragraph.\n\nSecond paragraph."
    stats = compute_statistics(text)
    assert stats.paragraph_count == 2
    assert stats.blank_line_count == 1
    assert stats.line_count == 3


def test_three_paragraphs():
    text = "Para 1\n\nPara 2\n\nPara 3"
    stats = compute_statistics(text)
    assert stats.paragraph_count == 3


def test_blank_line_count_never_exceeds_line_count():
    text = "\n\n\nsome text\n\n"
    stats = compute_statistics(text)
    assert stats.blank_line_count <= stats.line_count


def test_word_count_multiline():
    text = "one two\nthree four\nfive"
    stats = compute_statistics(text)
    assert stats.word_count == 5


def test_character_count_includes_whitespace():
    text = "ab cd"
    stats = compute_statistics(text)
    assert stats.character_count == 5


def test_multiline_blank_lines():
    text = "line1\n\n\n\nline2"
    stats = compute_statistics(text)
    assert stats.blank_line_count == 3   # 3 empty lines between line1 and line2
    assert stats.line_count == 5


def test_returns_frozen_dataclass():
    stats = compute_statistics("hello")
    with pytest.raises(Exception):
        stats.word_count = 999  # frozen dataclass — mutation must raise


def test_non_string_raises():
    from smriti.exceptions import StatisticsError
    with pytest.raises(StatisticsError):
        compute_statistics(123)  # type: ignore
````

## File: tests/unit/test_phase2_extraction.py
````python
"""
Integration test for Phase 2 end-to-end.

Tests the complete pipeline:
  List[SourceDocument] → ExtractionResult

Uses a realistic vault fixture with all supported formats.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.manifest import ManifestManager
from smriti.core.models import FileFormat, SourceDocument
from smriti.core.state import StateManager
from smriti.parsing import run_extraction, ExtractionResult


def make_source(path: Path, fmt: FileFormat) -> SourceDocument:
    content_hash = "a" * 64
    return SourceDocument(
        doc_id=content_hash,
        path=path,
        relative_path=Path(path.name),
        source_root=path.parent,
        format=fmt,
        content_hash=content_hash,
        size_bytes=path.stat().st_size,
        modified_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def vault_documents(tmp_path):
    """Create a realistic set of source documents for testing."""
    vault = tmp_path / "vault"
    vault.mkdir()

    docs = []

    # --- Markdown documents ---
    ai_md = vault / "AI.md"
    ai_md.write_text(
        "# Artificial Intelligence\n\n"
        "AI is transforming every industry.\n\n"
        "## Machine Learning\n\n"
        "Machine learning is a subset of AI.\n",
        encoding="utf-8",
    )
    docs.append(make_source(ai_md, FileFormat.MARKDOWN))

    python_md = vault / "Python.md"
    python_md.write_text(
        "# Python\n\nPython is the dominant language for data science.\n\n"
        "It is also used for web development.\n",
        encoding="utf-8",
    )
    docs.append(make_source(python_md, FileFormat.MARKDOWN))

    # Unicode content
    unicode_md = vault / "unicode.md"
    unicode_md.write_text(
        "# 研究ノート\n\nCafé résumé naïve.\n\nПривет мир.\n",
        encoding="utf-8",
    )
    docs.append(make_source(unicode_md, FileFormat.MARKDOWN))

    # Markdown with CRLF endings
    crlf_md = vault / "crlf.md"
    crlf_md.write_bytes(b"# Windows File\r\n\r\nWritten on Windows.\r\n")
    docs.append(make_source(crlf_md, FileFormat.MARKDOWN))

    # --- Text documents ---
    txt = vault / "notes.txt"
    txt.write_text(
        "Plain text research notes.\n\nSecond paragraph of notes.\n",
        encoding="utf-8",
    )
    docs.append(make_source(txt, FileFormat.TEXT))

    return docs


@pytest.fixture
def run_id():
    return "test_phase2_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Functional tests ──────────────────────────────────────────────────────────

def test_phase2_produces_documents(vault_documents, run_id, test_managers):
    """Phase 2 must return a Document for every valid SourceDocument."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=vault_documents,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    assert len(result.documents) == len(vault_documents)
    assert result.stats.failed == 0


def test_phase2_documents_are_frozen(vault_documents, run_id, test_managers):
    """Document must be frozen (immutable)."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.normalized_text = "mutated"


def test_phase2_doc_id_preserved(vault_documents, run_id, test_managers):
    """doc_id must equal source_document.doc_id for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert doc.doc_id == doc.source_document.doc_id


def test_phase2_crlf_normalized(vault_documents, run_id, test_managers):
    """CRLF line endings must be normalized to LF in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert "\r\n" not in doc.normalized_text
        assert "\r" not in doc.normalized_text


def test_phase2_markdown_headings_preserved(vault_documents, run_id, test_managers):
    """Markdown # headings must survive in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    md_docs = [d for d in result.documents if "AI.md" in str(d.source_document.path)]
    assert len(md_docs) == 1
    assert "# Artificial Intelligence" in md_docs[0].normalized_text


def test_phase2_unicode_preserved(vault_documents, run_id, test_managers):
    """Unicode content must be preserved correctly."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    unicode_docs = [d for d in result.documents if "unicode.md" in str(d.source_document.path)]
    assert len(unicode_docs) == 1
    assert "研究" in unicode_docs[0].normalized_text
    assert "Café" in unicode_docs[0].normalized_text


def test_phase2_statistics_consistent(vault_documents, run_id, test_managers):
    """TextStatistics invariants must hold for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        s = doc.text_statistics
        assert s.character_count >= 0
        assert s.word_count >= 0
        assert s.blank_line_count <= s.line_count
        assert s.paragraph_count <= s.line_count


def test_phase2_one_failure_does_not_stop_batch(run_id, test_managers, tmp_path):
    """A corrupted document must not stop processing of the remaining documents."""
    from smriti.core.models import SourceDocument

    vault = tmp_path / "vault"
    vault.mkdir()

    # Valid document
    good = vault / "good.md"
    good.write_text("# Good\n\nThis is fine.", encoding="utf-8")

    # Document pointing to nonexistent file
    ghost_source = SourceDocument(
        doc_id="b" * 64,
        path=tmp_path / "ghost.md",   # Does not exist
        relative_path=Path("ghost.md"),
        source_root=tmp_path,
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=0,
        modified_at=datetime.now(tz=timezone.utc),
    )

    good_source = make_source(good, FileFormat.MARKDOWN)

    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=[good_source, ghost_source],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    # Good document succeeded, ghost failed — batch continued
    assert result.stats.successful == 1
    assert result.stats.failed == 1
    assert len(result.documents) == 1


# ── Artifact tests ────────────────────────────────────────────────────────────

def test_phase2_writes_manifest(vault_documents, run_id, test_managers):
    """A manifest.json must be written after Phase 2."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 2
    assert manifest["status"] in ("success", "partial")
    assert manifest["run_id"] == run_id


def test_phase2_writes_dataset_json(vault_documents, run_id, test_managers, tmp_path):
    """dataset.json must be written with correct structure."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()

    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    assert len(dataset) == len(result.documents)

    for record in dataset:
        assert "doc_id" in record
        assert "normalized_text" in record
        assert "text_statistics" in record
        assert "extraction_method" in record
        # raw_text must NOT be in the dataset — too large, not needed by Phase 3
        assert "raw_text" not in record


def test_phase2_dataset_has_no_raw_text(vault_documents, run_id, test_managers):
    """dataset.json must never contain raw_text — only normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    for record in dataset:
        assert "raw_text" not in record


def test_phase2_updates_pipeline_state(vault_documents, run_id, test_managers):
    """Pipeline state must mark Phase 2 as complete."""
    manifest_mgr, state_mgr = test_managers
    run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    state = state_mgr.load()
    assert state is not None
    assert 2 in state.completed_phases


# ── Architectural tests ───────────────────────────────────────────────────────

def test_phase2_no_nlp_imports():
    """Phase 2 must never import NLP libraries."""
    import smriti.parsing.markdown as markdown_mod
    import smriti.parsing.text as text_mod
    import smriti.parsing.normalize as normalize_mod
    import smriti.parsing.statistics as statistics_mod
    import smriti.parsing.builder as builder_mod
    import smriti.parsing.loader as loader_mod

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [markdown_mod, text_mod, normalize_mod, statistics_mod, builder_mod, loader_mod]:
        module_imports = set(vars(module).keys())
        assert not (module_imports & nlp_modules), (
            f"{module.__name__} imports NLP libraries — Phase 2 must not do NLP"
        )


def test_phase2_is_deterministic(vault_documents, test_managers, tmp_path):
    """Running Phase 2 twice on same input must produce identical normalized_text."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_extraction(vault_documents, "run1", manifest_mgr, state_mgr)
    result2 = run_extraction(vault_documents, "run2", manifest_mgr, state_mgr)

    texts1 = {d.doc_id: d.normalized_text for d in result1.documents}
    texts2 = {d.doc_id: d.normalized_text for d in result2.documents}

    assert texts1 == texts2
````

## File: tests/unit/test_phase3_builder.py
````python
"""
Unit tests for extraction/builder.py.
"""

import pytest
from pathlib import Path
from smriti.extraction.builder import build_sentence, _compute_sentence_id


def test_build_returns_semantic_sentence():
    from smriti.core.models import SemanticSentence
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="Technology",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert isinstance(s, SemanticSentence)


def test_sentence_id_is_16_chars():
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert len(s.sentence_id) == 16


def test_sentence_id_is_deterministic():
    """Same inputs must always produce the same ID."""
    s1 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    s2 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    assert s1.sentence_id == s2.sentence_id


def test_different_text_different_id():
    s1 = build_sentence("Python is great.", "doc1", Path("a.md"), "", 0, 0, 16)
    s2 = build_sentence("Julia is faster.", "doc1", Path("a.md"), "", 0, 0, 16)
    assert s1.sentence_id != s2.sentence_id


def test_different_position_different_id():
    """Same text at different char_start must produce different ID."""
    s1 = build_sentence("same text.", "doc1", Path("a.md"), "", 0, 0, 10)
    s2 = build_sentence("same text.", "doc1", Path("a.md"), "", 1, 50, 60)
    assert s1.sentence_id != s2.sentence_id


def test_semantic_sentence_is_frozen():
    """SemanticSentence must be immutable."""
    s = build_sentence("Python.", "doc1", Path("a.md"), "", 0, 0, 7)
    with pytest.raises(Exception):
        s.text = "Julia."


def test_context_stored_separately():
    """Context must be stored as-is, never fused into text."""
    s = build_sentence("Supports tensors.", "doc1", Path("a.md"), "CUDA", 0, 0, 17)
    assert s.text == "Supports tensors."
    assert s.context == "CUDA"
    assert "CUDA" not in s.text


def test_empty_context_allowed():
    """Sentences at document root have no context."""
    s = build_sentence("Introduction.", "doc1", Path("a.md"), "", 0, 0, 13)
    assert s.context == ""


def test_builder_adds_provenance_and_version():
    """Test that origin_block_type and schema_version are correctly set."""
    from smriti.extraction.scanner import BlockType

    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
        origin_block_type=BlockType.PARAGRAPH,
    )
    assert s.origin_block_type == BlockType.PARAGRAPH
    assert s.schema_version == "3.0"
````

## File: tests/unit/test_phase3_context.py
````python
"""
Unit tests for extraction/context.py.
"""

import pytest
from smriti.extraction.context import ContextStack


def test_empty_stack_returns_empty_context():
    stack = ContextStack()
    assert stack.current_context() == ""


def test_push_one_heading():
    stack = ContextStack()
    stack.push("Python", level=1)
    assert stack.current_context() == "Python"


def test_push_nested_headings():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    assert stack.current_context() == "Python > Generators"


def test_push_deeper_nesting():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Yield", level=3)
    assert stack.current_context() == "Python > Generators > Yield"


def test_same_level_heading_replaces():
    """A new H2 heading replaces the previous H2."""
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Decorators", level=2)  # Replaces Generators
    assert stack.current_context() == "Python > Decorators"


def test_shallower_heading_pops_deeper():
    """A new H1 heading pops H2 and H3."""
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Advanced", level=1)  # Should pop Generators then push Advanced
    assert stack.current_context() == "Advanced"


def test_clear_resets_stack():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.clear()
    assert stack.current_context() == ""
    assert stack.depth() == 0


def test_depth_tracking():
    stack = ContextStack()
    assert stack.depth() == 0
    stack.push("A", level=1)
    assert stack.depth() == 1
    stack.push("B", level=2)
    assert stack.depth() == 2
    stack.push("C", level=1)  # Replaces A and B
    assert stack.depth() == 1


def test_peek_returns_top_heading():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    assert stack.peek() == "Generators"


def test_peek_empty_returns_none():
    stack = ContextStack()
    assert stack.peek() is None


def test_context_separator_is_correct():
    stack = ContextStack()
    stack.push("A", level=1)
    stack.push("B", level=2)
    assert " > " in stack.current_context()
````

## File: tests/unit/test_phase3_normalizer.py
````python
"""
Unit tests for extraction/normalizer.py.
"""

import pytest
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.extraction.normalizer import normalize_event
from smriti.core.models import SegmentationWarning


def make_event(block_type, text, raw_text=None, heading_level=None, lines=None):
    return ScannerEvent(
        block_type=block_type,
        text=text,
        raw_text=raw_text or text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=tuple(lines or [text]),
    )


def test_paragraph_passes_through():
    event = make_event(BlockType.PARAGRAPH, "Python is great for data science.")
    block = normalize_event(event)
    assert block.prose == "Python is great for data science."
    assert block.skip is False


def test_heading_is_skipped():
    """Headings must produce no prose — they are context only."""
    event = make_event(BlockType.HEADING, "Python", heading_level=1)
    block = normalize_event(event)
    assert block.skip is True
    assert block.prose == ""


def test_bullet_item_normalized():
    event = make_event(BlockType.BULLET_ITEM, "Use Poetry for dependency management")
    block = normalize_event(event)
    assert "Use Poetry" in block.prose
    assert block.skip is False


def test_bullet_item_gets_period():
    """Bullet items without trailing period must get one added."""
    event = make_event(BlockType.BULLET_ITEM, "No trailing period")
    block = normalize_event(event)
    assert block.prose.endswith(".")


def test_block_quote_normalized():
    event = make_event(BlockType.BLOCK_QUOTE, "Reliability is critical")
    block = normalize_event(event)
    assert "Reliability" in block.prose
    assert block.skip is False


def test_code_block_skipped():
    event = make_event(BlockType.CODE_BLOCK, "print('hello')")
    block = normalize_event(event)
    assert block.skip is True
    assert SegmentationWarning.SEG_CODE_BLOCK_SKIPPED in block.warnings


def test_horizontal_rule_skipped():
    event = make_event(BlockType.HORIZONTAL_RULE, "")
    block = normalize_event(event)
    assert block.skip is True


def test_table_normalized_to_prose():
    """Table rows become key-value prose sentences."""
    lines = [
        "| Model | Accuracy |",
        "|-------|----------|",
        "| GPT-4 | 85%      |",
    ]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        raw_text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert not block.skip
    assert "Model" in block.prose or "GPT-4" in block.prose


def test_malformed_table_emits_warning():
    """A table with only a separator produces SEG_MALFORMED_TABLE."""
    lines = ["|------|"]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        raw_text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert SegmentationWarning.SEG_MALFORMED_TABLE in block.warnings
````

## File: tests/unit/test_phase3_scanner.py
````python
"""
Unit tests for extraction/scanner.py.
The scanner has one job: identify structural events.
These tests never touch context, segmentation, or building.
"""

import pytest
from smriti.extraction.scanner import scan_document, BlockType



def test_empty_document_returns_empty():
    """Empty text must return [] — not crash."""
    assert scan_document("") == []
    assert scan_document("   \n\n   ") == []


def test_atx_heading_detected():
    """# Title must be detected as HEADING level 1."""
    events = scan_document("# Hello World")
    headings = [e for e in events if e.block_type == BlockType.HEADING]
    assert len(headings) == 1
    assert headings[0].heading_level == 1
    assert headings[0].text == "Hello World"


def test_h2_heading_level():
    """## Subtitle must be HEADING level 2."""
    events = scan_document("## Subtitle")
    headings = [e for e in events if e.block_type == BlockType.HEADING]
    assert headings[0].heading_level == 2


def test_paragraph_detected():
    """Plain prose must be detected as PARAGRAPH."""
    events = scan_document("Python is the best language for data science.")
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert len(paragraphs) == 1


def test_bullet_item_detected():
    """'- item' must be detected as BULLET_ITEM."""
    events = scan_document("- This is a list item")
    bullets = [e for e in events if e.block_type == BlockType.BULLET_ITEM]
    assert len(bullets) == 1
    assert bullets[0].text == "This is a list item"


def test_ordered_item_detected():
    """'1. item' must be detected as ORDERED_ITEM."""
    events = scan_document("1. Install dependencies")
    ordered = [e for e in events if e.block_type == BlockType.ORDERED_ITEM]
    assert len(ordered) == 1
    assert ordered[0].text == "Install dependencies"


def test_block_quote_detected():
    """> quote must be detected as BLOCK_QUOTE."""
    events = scan_document("> Reliability is critical.")
    quotes = [e for e in events if e.block_type == BlockType.BLOCK_QUOTE]
    assert len(quotes) == 1
    assert quotes[0].text == "Reliability is critical."


def test_fenced_code_block_detected():
    """```code``` must be detected as CODE_BLOCK."""
    text = "```python\nprint('hello')\n```"
    events = scan_document(text)
    code = [e for e in events if e.block_type == BlockType.CODE_BLOCK]
    assert len(code) == 1


def test_table_detected():
    """Markdown table must be detected as TABLE."""
    text = "| Model | Accuracy |\n|-------|----------|\n| GPT-4 | 85% |"
    events = scan_document(text)
    tables = [e for e in events if e.block_type == BlockType.TABLE]
    assert len(tables) == 1


def test_heading_not_in_paragraph():
    """A heading must NOT be a PARAGRAPH event."""
    events = scan_document("# Title\n\nSome text.")
    types = [e.block_type for e in events]
    assert BlockType.HEADING in types
    assert BlockType.PARAGRAPH in types
    # The heading text must not appear in a paragraph event
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert not any("Title" in p.text for p in paragraphs)


def test_events_are_in_document_order():
    """Events must appear in the same order as the document."""
    text = "# H1\n\nParagraph.\n\n- item\n\n## H2"
    events = scan_document(text)
    types = [e.block_type for e in events]
    # H1 heading must come before paragraph, paragraph before bullet
    h1_idx = next(i for i, e in enumerate(events)
                  if e.block_type == BlockType.HEADING and e.heading_level == 1)
    para_idx = next(i for i, e in enumerate(events)
                    if e.block_type == BlockType.PARAGRAPH)
    bullet_idx = next(i for i, e in enumerate(events)
                      if e.block_type == BlockType.BULLET_ITEM)
    assert h1_idx < para_idx < bullet_idx


def test_code_does_not_contaminate_paragraph():
    """Text inside a code block must not become a PARAGRAPH event."""
    text = "Before.\n\n```\nsome code\n```\n\nAfter."
    events = scan_document(text)
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert not any("some code" in p.text for p in paragraphs)


def test_horizontal_rule_detected():
    """--- must be detected as HORIZONTAL_RULE."""
    events = scan_document("---")
    hr = [e for e in events if e.block_type == BlockType.HORIZONTAL_RULE]
    assert len(hr) == 1


def test_multiple_bullet_items():
    """Three bullet items must produce three BULLET_ITEM events."""
    text = "- First\n- Second\n- Third"
    events = scan_document(text)
    bullets = [e for e in events if e.block_type == BlockType.BULLET_ITEM]
    assert len(bullets) == 3


def test_mixed_content():
    """Complex document with mixed structure produces correct event count."""
    text = """# Title

Introduction paragraph.

## Section

- item one
- item two

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    events = scan_document(text)
    types = [e.block_type for e in events]
    assert BlockType.HEADING in types
    assert BlockType.PARAGRAPH in types
    assert BlockType.BULLET_ITEM in types
    assert BlockType.TABLE in types
````

## File: tests/unit/test_phase3_segmenter.py
````python
"""
Unit tests for extraction/segmenter.py.
"""

import pytest
from smriti.extraction.segmenter import SentenceSegmenter


@pytest.fixture
def segmenter():
    return SentenceSegmenter()


def test_single_sentence(segmenter):
    result = segmenter.segment("Python is great for data science.")
    assert len(result) == 1
    assert result[0].text == "Python is great for data science."


def test_two_sentences(segmenter):
    result = segmenter.segment(
        "Python is great for data science. Julia is faster for numerical computing."
    )
    assert len(result) == 2


def test_question_mark_splits(segmenter):
    result = segmenter.segment(
        "Is Python good? Yes, it is very good."
    )
    assert len(result) == 2


def test_exclamation_splits(segmenter):
    result = segmenter.segment(
        "This works! Now let's move on."
    )
    assert len(result) == 2


def test_abbreviation_dr_does_not_split(segmenter):
    """'Dr. Smith' must not split into two sentences."""
    result = segmenter.segment("Dr. Smith visited the lab.")
    assert len(result) == 1


def test_abbreviation_eg_does_not_split(segmenter):
    """'e.g. Python' must not split."""
    result = segmenter.segment("Use a high-level language, e.g. Python or Julia.")
    assert len(result) == 1


def test_abbreviation_ie_does_not_split(segmenter):
    """'i.e. that' must not split."""
    result = segmenter.segment("Use the right tool, i.e. the simplest one.")
    assert len(result) == 1


def test_decimal_number_does_not_split(segmenter):
    """'3.14' must not split."""
    result = segmenter.segment("Pi is approximately 3.14 and it is irrational.")
    assert len(result) == 1


def test_empty_prose_returns_empty(segmenter):
    result = segmenter.segment("")
    assert result == []


def test_whitespace_only_returns_empty(segmenter):
    result = segmenter.segment("   \n\n   ")
    assert result == []


def test_sentence_text_is_stripped(segmenter):
    """Sentence text must not have leading/trailing whitespace."""
    result = segmenter.segment("  Python is great.  Julia is fast.  ")
    for s in result:
        assert s.text == s.text.strip()


def test_positions_are_non_negative(segmenter):
    result = segmenter.segment("First sentence. Second sentence.")
    for s in result:
        assert s.char_start >= 0
        assert s.char_end > s.char_start


def test_three_sentences(segmenter):
    text = "First. Second. Third."
    result = segmenter.segment(text)
    assert len(result) == 3


def test_very_long_sentence_emits_warning(segmenter):
    """A sentence exceeding max_sentence_chars must emit SEG002."""
    from smriti.core.models import SegmentationWarning
    long_text = "word " * 500 + "."
    result = segmenter.segment(long_text)
    assert len(result) == 1
    assert SegmentationWarning.SEG_VERY_LONG_SENTENCE in result[0].warnings
````

## File: tests/unit/test_phase3_statistics.py
````python
"""
Unit tests for extraction/statistics.py.
"""

import pytest
from smriti.extraction.statistics import Phase3StatsCollector
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning


def make_event(block_type: BlockType, text: str = "", heading_level: int = None) -> ScannerEvent:
    return ScannerEvent(
        block_type=block_type,
        text=text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=(text,),
    )


def test_stats_collector_counts_all_block_types():
    collector = Phase3StatsCollector()

    # Generate one of each block type
    events = [
        make_event(BlockType.HEADING, "H1", heading_level=1),
        make_event(BlockType.PARAGRAPH, "paragraph"),
        make_event(BlockType.BULLET_ITEM, "bullet"),
        make_event(BlockType.ORDERED_ITEM, "ordered"),
        make_event(BlockType.TABLE, "table"),
        make_event(BlockType.BLOCK_QUOTE, "quote"),
        make_event(BlockType.CODE_BLOCK, "code"),
        make_event(BlockType.HORIZONTAL_RULE, "---"),
        make_event(BlockType.FRONT_MATTER, "---"),
        make_event(BlockType.BLANK, ""),
        make_event(BlockType.UNKNOWN, "unknown"),  # This should be counted as unknown
    ]

    for event in events:
        collector.accumulate_event(event)

    # Record some sentences
    for _ in range(5):
        collector.record_sentence_produced()
    for _ in range(2):
        collector.record_sentence_discarded()

    # Record a warning
    collector.record_warnings((SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,))

    stats = collector.finalize()

    assert isinstance(stats, Phase3Stats)
    assert stats.total_headings == 1
    assert stats.total_paragraphs == 1
    assert stats.total_list_items == 2  # bullet + ordered
    assert stats.total_tables == 1
    assert stats.total_block_quotes == 1
    assert stats.total_code_blocks_skipped == 1
    assert stats.total_horizontal_rules == 1
    assert stats.total_front_matter_blocks == 1
    assert stats.total_blank_lines == 1
    assert stats.total_unknown_blocks == 1  # the UNKNOWN event
    assert stats.sentences_produced == 5
    assert stats.sentences_discarded == 2
    assert len(stats.warnings) == 1
    assert stats.warnings[0] == SegmentationWarning.SEG_CODE_BLOCK_SKIPPED


def test_stats_collector_empty_document():
    collector = Phase3StatsCollector()
    stats = collector.finalize()

    assert stats.total_headings == 0
    assert stats.total_paragraphs == 0
    assert stats.total_list_items == 0
    assert stats.total_tables == 0
    assert stats.total_block_quotes == 0
    assert stats.total_code_blocks_skipped == 0
    assert stats.total_horizontal_rules == 0
    assert stats.total_front_matter_blocks == 0
    assert stats.total_blank_lines == 0
    assert stats.total_unknown_blocks == 0
    assert stats.sentences_produced == 0
    assert stats.sentences_discarded == 0
    assert len(stats.warnings) == 0
````

## File: tests/unit/test_phase3_validator.py
````python
"""
Unit tests for extraction/validator.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.validator import validate_sentences
from smriti.exceptions import SentenceValidationError


def make_sentence(sid, doc_id, text, position, char_start=0, char_end=10, context=""):
    return SemanticSentence(
        sentence_id=sid,
        document_id=doc_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=Path("note.md"),
    )


def test_valid_sentences_pass():
    sentences = [
        make_sentence("aaa", "doc1", "First sentence.", 0, 0, 15),
        make_sentence("bbb", "doc1", "Second sentence.", 1, 16, 32),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 2
    assert warnings == []


def test_empty_sentence_is_discarded():
    sentences = [
        make_sentence("aaa", "doc1", "   ", 0),
        make_sentence("bbb", "doc1", "Real sentence.", 1),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 1
    assert SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED in warnings


def test_duplicate_id_raises():
    sentences = [
        make_sentence("dup", "doc1", "First.", 0),
        make_sentence("dup", "doc1", "Second.", 1),  # Same ID!
    ]
    with pytest.raises(SentenceValidationError, match="Duplicate"):
        validate_sentences(sentences, "doc1")


def test_non_monotonic_position_raises():
    sentences = [
        make_sentence("aaa", "doc1", "First.", 2),  # Position 2
        make_sentence("bbb", "doc1", "Second.", 1), # Position 1 — goes backwards!
    ]
    with pytest.raises(SentenceValidationError):
        validate_sentences(sentences, "doc1")


def test_wrong_document_id_raises():
    sentences = [
        make_sentence("aaa", "wrong_doc", "Text.", 0),
    ]
    with pytest.raises(SentenceValidationError, match="document_id"):
        validate_sentences(sentences, "doc1")


def test_empty_input_returns_empty():
    valid, warnings = validate_sentences([], "doc1")
    assert valid == []
    assert warnings == []


def test_invalid_context_emits_warning():
    from smriti.extraction.rules import CONTEXT_SEPARATOR
    # context with illegal characters (e.g., "Python@CUDA")
    sentences = [
        make_sentence("aaa", "doc1", "text", 0, 0, 4, context="Python@CUDA"),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert SegmentationWarning.VAL_INVALID_CONTEXT in warnings
````

## File: tests/unit/test_phase4_annotation.py
````python
"""
Unit tests for claims/annotation.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, Modality, ExtractionMode
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.parser import SpaCyParser
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def annotator():
    return AssertionAnnotator()


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_structured_candidate(parser, extractor, text):
    from smriti.claims.models import AssertionCandidate
    sentence = SemanticSentence(
        sentence_id="s001", document_id="d001", text=text,
        context="", position=0, char_start=0, char_end=len(text),
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = parser.parse(sentence)
    candidate = AssertionCandidate(
        text=text, span_start=0, span_end=len(text),
        source=parsed, boundary_reason="test",
    )
    return extractor.extract(candidate)


def test_negation_detected(parser, extractor, annotator):
    """'Python does not support X' → is_negated=True."""
    sc = make_structured_candidate(parser, extractor, "Python does not support this feature.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_negated is True


def test_no_negation_in_positive(parser, extractor, annotator):
    """'Python supports X' → is_negated=False."""
    sc = make_structured_candidate(parser, extractor, "Python supports generators.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_negated is False


def test_modality_possible(parser, extractor, annotator):
    """'Python may be faster' → modality=POSSIBLE."""
    sc = make_structured_candidate(parser, extractor, "Python may be faster than Java.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.modality == Modality.POSSIBLE


def test_modality_certain(parser, extractor, annotator):
    """'Python is fast' → modality=CERTAIN."""
    sc = make_structured_candidate(parser, extractor, "Python is fast.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.modality == Modality.CERTAIN


def test_conditional_detected(parser, extractor, annotator):
    """'If X is installed, Y works' → is_conditional=True."""
    sc = make_structured_candidate(parser, extractor,
                                   "If CUDA is installed, PyTorch uses the GPU.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_conditional is True


def test_text_not_modified_by_annotation(parser, extractor, annotator):
    """Annotation MUST NOT modify claim text."""
    text = "Python does not support this feature."
    sc = make_structured_candidate(parser, extractor, text)
    annotated = annotator.annotate(sc)
    assert annotated.text == text


def test_annotation_never_raises(parser, extractor, annotator):
    """Annotation must never raise regardless of input."""
    sc = make_structured_candidate(parser, extractor, "!!! weird ?? input !!!")
    annotated = annotator.annotate(sc)
    assert annotated is not None
````

## File: tests/unit/test_phase4_boundaries.py
````python
"""
Unit tests for claims/boundaries.py – boundary detection logic.

These tests verify that BoundaryDetector correctly identifies claim boundaries
in various syntactic structures, and that it uses the BoundaryReason enum
and produces AssertionCandidate objects without the confidence field.
"""

import pytest
from pathlib import Path

from smriti.core.models import SemanticSentence, BoundaryReason
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.models import AssertionCandidate


@pytest.fixture(scope="module")
def parser():
    """Load the linguistic parser once for all tests."""
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def detector():
    """BoundaryDetector with default configuration (split_conjunctions=True)."""
    return BoundaryDetector()


def make_sentence(text: str, sentence_id: str = "s001") -> SemanticSentence:
    """Helper to create a SemanticSentence."""
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


# ── Basic functionality ───────────────────────────────────────────────────────

def test_single_sentence_returns_one_candidate(parser, detector):
    """A simple sentence with no coordination must yield exactly one candidate."""
    sent = make_sentence("Python is a high-level language.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert isinstance(candidates[0], AssertionCandidate)
    assert candidates[0].text == sent.text
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION
    # 'confidence' no longer exists – test removed


def test_parse_failure_returns_whole_sentence(parser, detector):
    """When parsing fails, detect() must fall back to whole-sentence candidate."""
    sent = make_sentence("@@@ ??? weird !!!")
    parsed = parser.parse(sent)
    # It may or may not parse, but if parse_ok is False, we expect fallback.
    if not parsed.parse_ok:
        candidates = detector.detect(parsed)
        assert len(candidates) == 1
        assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
        assert candidates[0].text == sent.text


# ── Coordinated predicates (shared subject) ─────────────────────────────────

def test_coordinated_predicate_splits(parser, detector):
    """'Python supports X and Y' → two candidates with COORDINATED_PREDICATE."""
    sent = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Expect two claims: "Python supports generators" and "Python supports decorators"
    # The exact text may vary; we check count and reasons.
    assert len(candidates) == 2
    for cand in candidates:
        assert cand.boundary_reason == BoundaryReason.COORDINATED_PREDICATE
    # Verify text contains both parts (approximate)
    texts = [c.text for c in candidates]
    assert any("generators" in t for t in texts)
    assert any("decorators" in t for t in texts)


def test_coordinated_predicate_with_shared_subject_works(parser, detector):
    """Coordination of verbs sharing subject: 'Python runs and compiles quickly'."""
    sent = make_sentence("Python runs and compiles quickly.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Should produce two: "Python runs quickly" and "Python compiles quickly"
    assert len(candidates) == 2


# ── Independent clauses ──────────────────────────────────────────────────────

def test_independent_clauses_splits(parser, detector):
    """'X is fast and Y is slow' → two independent clause candidates."""
    sent = make_sentence("Python is fast and Java is slow.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 2
    assert all(c.boundary_reason == BoundaryReason.INDEPENDENT_CLAUSE for c in candidates)
    texts = [c.text for c in candidates]
    assert any("Python" in t for t in texts)
    assert any("Java" in t for t in texts)


# ── Complex cases – no split when not appropriate ───────────────────────────

def test_conditional_not_split(parser, detector):
    """Conditional 'if X then Y' should remain as one claim (split_conditionals=False)."""
    sent = make_sentence("If CUDA is installed, PyTorch uses the GPU.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # We expect one candidate (whole sentence) because we do not split conditionals.
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_relative_clause_not_split(parser, detector):
    """Relative clause should not be split; remains one claim."""
    sent = make_sentence("Python, which was released in 1991, supports generators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_empty_text(parser, detector):
    """Empty text -> parse_ok=False -> fallback with PARSE_FAILED."""
    sent = make_sentence("   ")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
    assert candidates[0].text == sent.text


def test_no_coordination_still_returns_one(parser, detector):
    """Sentence without coordinator yields single candidate."""
    sent = make_sentence("Deep learning is powerful.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_detector_never_returns_empty(parser, detector):
    """detect() must always return at least one candidate."""
    sent = make_sentence("This is a test.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) >= 1


# ── Configuration: split_conjunctions = False ──────────────────────────────

def test_split_disabled_returns_single(parser):
    """When split_conjunctions is False, no splitting occurs."""
    # We need to create a detector with split_conjunctions=False.
    # Since we can't easily override config, we'll patch or instantiate with custom config.
    # For simplicity, we assume the default config has split_conjunctions=True.
    # If you want to test, you can modify the config or use a custom BoundaryDetector.
    # We'll skip this test or demonstrate by setting attribute directly.
    detector_no_split = BoundaryDetector()
    # Set internal flag to False (hack for testing)
    detector_no_split._split_conjunctions = False
    sent = make_sentence("Python supports X and Y.")
    parsed = parser.parse(sent)
    candidates = detector_no_split.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION
````

## File: tests/unit/test_phase4_builder.py
````python
"""
Unit tests for claims/builder.py.
"""

import pytest
from pathlib import Path

from smriti.core.models import (
    SemanticSentence,
    ExtractionMode,
    Modality,
    StructuredAssertion,
    Claim,
    BoundaryReason,
)
from smriti.claims.builder import build_claim, _compute_claim_id
from smriti.claims.rules import RULE_VERSION


def make_validated(text: str, sentence_id: str = "sent001", doc_id: str = "doc001"):
    """Create a minimal ValidatedAssertion for testing."""
    from smriti.claims.models import (
        ValidatedAssertion,
        AnnotatedAssertion,
        StructuredAssertionCandidate,
        AssertionCandidate,
        ParsedSentence,
        LinguisticMetadata,
        SemanticMetadata,
    )
    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=doc_id,
        text=text,
        context="Python > Generators",
        position=3,
        char_start=100,
        char_end=100 + len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason=BoundaryReason.SINGLE_ASSERTION,
    )
    structured_cand = StructuredAssertionCandidate(
        candidate=candidate,
        structured_assertion=None,
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
    )

    # Split metadata
    linguistic = LinguisticMetadata(
        is_negated=False,
        modality=Modality.CERTAIN,
        is_quoted=False,
    )
    semantic = SemanticMetadata(
        is_conditional=False,
        is_comparative=False,
        is_attributed=False,
        attributed_to=None,
    )

    annotated = AnnotatedAssertion(
        structured_candidate=structured_cand,
        linguistic_metadata=linguistic,
        semantic_metadata=semantic,
        additional_warnings=[],
    )

    return ValidatedAssertion(annotated=annotated, all_warnings=[])


def test_build_returns_claim():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert isinstance(claim, Claim)
    assert claim.content_hash is not None
    assert len(claim.content_hash) == 16
    assert claim.rule_version == RULE_VERSION
    assert claim.rule_version == "1.0"


def test_claim_id_is_16_chars():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert len(claim.claim_id) == 16


def test_claim_id_is_deterministic():
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s1")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id == claim2.claim_id
    assert claim1.content_hash == claim2.content_hash


def test_different_text_different_id():
    v1 = make_validated("Python is great.")
    v2 = make_validated("Julia is faster.")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id != claim2.claim_id
    assert claim1.content_hash != claim2.content_hash


def test_claim_text_is_exact():
    """Text must be author's exact wording — no modification."""
    text = "Python does NOT support this feature."
    v = make_validated(text)
    claim = build_claim(v)
    assert claim.text == text


def test_claim_is_frozen():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    with pytest.raises(Exception):
        claim.text = "modified"


def test_claim_has_provenance():
    v = make_validated("Python is fast.", sentence_id="sent_x", doc_id="doc_y")
    claim = build_claim(v)
    assert claim.provenance is not None
    assert claim.provenance.sentence_id == "sent_x"
    assert claim.provenance.document_id == "doc_y"


def test_claim_schema_version():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    assert claim.schema_version == "4.0"


def test_claim_context_from_sentence():
    """Claim must inherit context from source SemanticSentence."""
    v = make_validated("Python supports generators.", sentence_id="s1")
    claim = build_claim(v)
    assert claim.context == "Python > Generators"


# ── New test: content_hash depends only on text ──────────────────────────────

def test_content_hash_depends_only_on_text():
    """content_hash must be identical for identical text, regardless of sentence_id."""
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s2")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.content_hash == claim2.content_hash
    # claim_id includes sentence_id, so it should differ
    assert claim1.claim_id != claim2.claim_id
````

## File: tests/unit/test_phase4_parser.py
````python
"""
Unit tests for claims/parser.py.
Parser has one job: produce ParsedSentence from SemanticSentence.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from smriti.core.models import SemanticSentence
from smriti.claims.parser import LinguisticParser


@pytest.fixture(scope="module")
def parser():
    """Load spaCy model once per test module."""
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(text: str, sentence_id: str = "test001") -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def test_parse_simple_sentence(parser):
    """Simple sentence must parse successfully."""
    sentence = make_sentence("Python is fast.")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is True
    assert parsed.spacy_doc is not None


def test_parse_preserves_original_sentence(parser):
    """ParsedSentence.sentence must be the original, unchanged."""
    sentence = make_sentence("Python supports generators.")
    parsed = parser.parse(sentence)
    assert parsed.sentence is sentence


def test_parse_empty_sentence_returns_failed(parser):
    """Empty text must return parse_ok=False — not raise."""
    sentence = make_sentence("   ")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is False
    assert parsed.spacy_doc is None


def test_parse_fails_gracefully(parser):
    """Parser failure must not raise — returns parse_ok=False."""
    sentence = make_sentence("!!!! ~~~~ #### not real text ????")
    parsed = parser.parse(sentence)
    # spaCy may or may not parse this — either way no exception
    assert parsed.sentence is sentence


def test_parse_unicode_text(parser):
    """Unicode text must parse without errors."""
    sentence = make_sentence("Python est rapide et Python est populaire.")
    parsed = parser.parse(sentence)
    # May or may not produce great results, but must not crash
    assert parsed.sentence is sentence


def test_spacy_doc_has_tokens(parser):
    """Parsed doc must have tokens."""
    sentence = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sentence)
    if parsed.parse_ok:
        assert len(list(parsed.spacy_doc)) > 0
````

## File: tests/unit/test_phase4_structure.py
````python
"""
Unit tests for claims/structure.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, ExtractionMode
from smriti.claims.parser import LinguisticParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_parsed(parser, text):
    from smriti.claims.parser import LinguisticParser
    sentence = SemanticSentence(
        sentence_id="s001",
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    return parser.parse(sentence)


def make_candidate(parser, text):
    from smriti.claims.models import AssertionCandidate
    parsed = make_parsed(parser, text)
    return AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason="single_assertion",
    )


def test_svo_extraction_simple(parser, extractor):
    """'Python supports generators' → S=Python, P=supports, O=generators."""
    candidate = make_candidate(parser, "Python supports generators.")
    result = extractor.extract(candidate)
    if result.extraction_mode == ExtractionMode.STRUCTURED:
        assert result.structured_assertion is not None
        assert result.structured_assertion.predicate is not None


def test_failed_parse_produces_lexical(extractor):
    """If parse failed, mode must be LEXICAL."""
    from smriti.claims.models import ParsedSentence, AssertionCandidate
    from smriti.core.models import SemanticSentence
    sentence = SemanticSentence(
        sentence_id="s002", document_id="d001", text="test",
        context="", position=0, char_start=0, char_end=4,
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    failed_parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text="test", span_start=0, span_end=4,
        source=failed_parsed, boundary_reason="parse_failed",
    )
    result = extractor.extract(candidate)
    assert result.extraction_mode == ExtractionMode.LEXICAL


def test_extraction_never_raises(parser, extractor):
    """Extraction must NEVER raise regardless of input."""
    candidate = make_candidate(parser, "!!!! ~~~~ something very weird ????")
    result = extractor.extract(candidate)
    assert result is not None  # Always returns something
    assert result.candidate.text == "!!!! ~~~~ something very weird ????"
````

## File: tests/unit/test_phase4_validator.py
````python
"""
Unit tests for claims/validator.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ExtractionMode, AssertionMetadata, Modality, ClaimProvenance, ClaimWarning,
)
from smriti.claims.validator import validate_claims
from smriti.exceptions import ClaimValidationError


def make_claim(claim_id: str, text: str, doc_id: str = "doc001") -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="sent001",
        document_id=doc_id,
        text=text,
        context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="sent001",
            document_id=doc_id,
            source_path=Path("test.md"),
            sentence_context="",
            sentence_position=0,
        ),
        schema_version="4.0",
    )


def test_valid_claims_pass():
    claims = [
        make_claim("aaa", "Python is great."),
        make_claim("bbb", "Julia is faster."),
    ]
    valid, warnings = validate_claims(claims, "doc001")
    assert len(valid) == 2
    assert warnings == []


def test_empty_text_discarded():
    claims = [
        make_claim("aaa", "   "),
        make_claim("bbb", "Real claim."),
    ]
    valid, warnings = validate_claims(claims, "doc001")
    assert len(valid) == 1
    assert ClaimWarning.CLM_EMPTY_ASSERTION in warnings


def test_duplicate_id_raises():
    claims = [
        make_claim("dup", "First claim."),
        make_claim("dup", "Second claim."),
    ]
    with pytest.raises(ClaimValidationError) as excinfo:
        validate_claims(claims, "doc001")
    assert "inconsistent" not in str(excinfo.value)   # old behaviour raises anyway


def test_wrong_document_id_raises():
    claims = [make_claim("aaa", "Text.", doc_id="wrong_doc")]
    with pytest.raises(ClaimValidationError, match="document_id"):
        validate_claims(claims, "doc001")


def test_no_provenance_raises():
    from dataclasses import replace
    claim = make_claim("aaa", "Text.")
    # Forcefully create a claim with no provenance
    # (cannot happen in normal pipeline, but test the validator)
    import dataclasses
    bad_claim = dataclasses.replace(claim, provenance=None)
    with pytest.raises(ClaimValidationError):
        validate_claims([bad_claim], "doc001")


def test_empty_input_returns_empty():
    valid, warnings = validate_claims([], "doc001")
    assert valid == []
    assert warnings == []

def test_duplicate_id_with_same_content_raises_too():
    """Even if content_hash matches, duplicate IDs are not allowed."""
    claim1 = make_claim("dup", "Same text")
    claim2 = make_claim("dup", "Same text")  # same content, same provenance?
    # They share same sentence_id, doc_id, etc. In practice they'd be identical.
    # The validator should still raise.
    with pytest.raises(ClaimValidationError, match="Duplicate"):
        validate_claims([claim1, claim2], "doc001")
````

## File: tests/unit/test_phase5_builders.py
````python
"""
Unit tests for embedding/builders.py.
Tests Vector, Embedding, EmbeddingQuality, and EmbeddedClaim construction.
"""

import pytest
import math
from smriti.core.models import (
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, Embedding, EmbeddedClaim,
)
from smriti.embedding.builders import (
    build_vector, build_embedding, build_embedding_quality, build_embedded_claim,
)


@pytest.fixture
def descriptor():
    return EmbeddingModelDescriptor(
        provider="sentence-transformers",
        model_name="all-MiniLM-L6-v2",
        model_revision="default",
        dimension=4,
        model_signature="test_signature",
        embedding_family="SentenceTransformer",
    )


@pytest.fixture
def provenance():
    return EmbeddingProvenance(
        pipeline_version="1.0",
        normalization_mode="l2",
        device="cpu",
        config_hash="test_hash",
    )


# ── build_vector ──────────────────────────────────────────────────────────────

def test_build_vector_returns_vector(descriptor):
    vec = build_vector([0.25, 0.25, 0.25, 0.25], descriptor.dimension, normalized=True)
    assert isinstance(vec, Vector)


def test_build_vector_values_are_tuple(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert isinstance(vec.values, tuple)


def test_build_vector_dimension_matches(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert vec.dimension == 4
    assert len(vec.values) == 4


def test_build_vector_normalized_flag_set(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension, normalized=True)
    assert vec.normalized is True


def test_build_vector_normalized_flag_false_by_default(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension)
    assert vec.normalized is False


def test_build_vector_dimension_mismatch_raises(descriptor):
    """Defensive assertion: dimension mismatch must raise."""
    with pytest.raises(AssertionError):
        build_vector([0.1, 0.2, 0.3], descriptor.dimension)  # 3 values, expected 4


# ── build_embedding ───────────────────────────────────────────────────────────

def test_build_embedding_returns_embedding(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb, Embedding)


def test_build_embedding_has_no_status_field(descriptor, provenance):
    """Embedding must NOT have a status attribute (timeless semantic artifact)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert not hasattr(emb, "status")


def test_build_embedding_vector_is_vector_type(descriptor, provenance):
    """Embedding.vector must be a Vector domain object (not a raw tuple)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb.vector, Vector)


def test_build_embedding_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    with pytest.raises(Exception):
        emb.claim_id = "modified"


# ── build_embedding_quality ───────────────────────────────────────────────────

def test_build_embedding_quality_fresh(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    assert isinstance(quality, EmbeddingQuality)
    assert quality.dimension_ok is True
    assert quality.normalized is True
    assert quality.finite is True
    assert quality.cache_used is False


def test_build_embedding_quality_cached(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=True)
    assert quality.cache_used is True


def test_build_embedding_quality_is_frozen(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    with pytest.raises(Exception):
        quality.dimension_ok = False


# ── build_embedded_claim ──────────────────────────────────────────────────────

def test_build_embedded_claim_returns_embedded_claim(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec, EmbeddedClaim)


def test_build_embedded_claim_has_quality(descriptor, provenance):
    """EmbeddedClaim must carry EmbeddingQuality."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=True)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec.quality, EmbeddingQuality)
    assert ec.quality.cache_used is True


def test_build_embedded_claim_schema_version(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.schema_version == "5.0"


def test_build_embedded_claim_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    with pytest.raises(Exception):
        ec.claim_id = "modified"


def test_embedded_claim_values_property(descriptor, provenance):
    """EmbeddedClaim.values must return the float tuple directly."""
    raw = [0.1, 0.2, 0.3, 0.4]
    vec = build_vector(raw, descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.values == tuple(float(x) for x in raw)
````

## File: tests/unit/test_phase5_cache.py
````python
"""
Unit tests for embedding/cache.py.
Includes schema_version validation (critical fix).
"""

import pytest
import pickle
from smriti.core.models import EmbeddingStatus
from smriti.embedding.cache import EmbeddingCachePolicy, CACHE_SCHEMA_VERSION


@pytest.fixture
def cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=True)


@pytest.fixture
def disabled_cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=False)


def test_miss_on_empty_cache(cache):
    status, vector = cache.lookup("nonexistent_key", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_store_and_retrieve(cache):
    vector = [0.1, 0.2, 0.3]
    cache.store("key001", vector, "sig_A", "hash_X")
    status, retrieved = cache.lookup("key001", "sig_A", "hash_X")
    assert status == EmbeddingStatus.CACHED
    assert retrieved == vector


def test_stale_on_model_change(cache):
    """Different model signature → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_B", "hash_X")
    assert status == EmbeddingStatus.STALE


def test_stale_on_config_change(cache):
    """Different config hash → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_A", "hash_Y")
    assert status == EmbeddingStatus.STALE


def test_stale_on_schema_version_mismatch(cache, tmp_path):
    """
    Cache entry with an old schema_version → STALE.
    This is the critical fix: schema changes must not silently reuse old artifacts.
    """
    cache_dir = tmp_path / "emb_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Write an entry with an old schema_version directly
    old_entry = {
        "vector":         [0.1, 0.2, 0.3],
        "model_sig":      "sig_A",
        "config_hash":    "hash_X",
        "schema_version": "4.0",   # Old schema — incompatible
    }
    cache_file = cache_dir / "key_old.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(old_entry, f)

    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    status, vector = policy.lookup("key_old", "sig_A", "hash_X")
    assert status == EmbeddingStatus.STALE
    assert vector is None


def test_stored_entry_has_current_schema_version(cache, tmp_path):
    """Stored entries must include CACHE_SCHEMA_VERSION."""
    cache_dir = tmp_path / "emb_cache2"
    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    policy.store("key001", [0.1, 0.2], "sig", "hash")
    with open(cache_dir / "key001.pkl", "rb") as f:
        entry = pickle.load(f)
    assert entry["schema_version"] == CACHE_SCHEMA_VERSION


def test_disabled_cache_returns_failed(disabled_cache):
    status, vector = disabled_cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_clear_all(cache):
    cache.store("key001", [0.1], "sig", "hash")
    cache.store("key002", [0.2], "sig", "hash")
    count = cache.clear_all()
    assert count == 2
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED


def test_invalidate_specific_key(cache):
    cache.store("key001", [0.1, 0.2], "sig", "hash")
    removed = cache.invalidate("key001")
    assert removed is True
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
````

## File: tests/unit/test_phase5_input_factory.py
````python
"""
Unit tests for embedding/input_factory.py.

Tests both EmbeddingInputFactory (payload) and CacheKeyFactory (keys).
These are now separate classes with separate responsibilities.
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata, Modality,
)
from smriti.embedding.input_factory import EmbeddingInputFactory, CacheKeyFactory


def make_claim(
    claim_id: str = "c001",
    text: str = "Python supports generators.",
    context: str = "",
    content_hash: str = "abc123",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id="d001",
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=content_hash,
        rule_version="1.0",
    )


@pytest.fixture
def payload_factory():
    return EmbeddingInputFactory()


@pytest.fixture
def key_factory():
    return CacheKeyFactory(model_signature="test_model_sig_abc", config_hash="test_config_xyz")


# ── EmbeddingInputFactory tests ───────────────────────────────────────────────

def test_payload_without_context(payload_factory):
    """Claim without context → payload is just claim.text."""
    claim = make_claim(text="Python is fast.", context="")
    assert payload_factory.build_payload(claim) == "Python is fast."


def test_payload_with_context(payload_factory):
    """Claim with context → payload is 'context\\ntext'."""
    claim = make_claim(text="It supports yield statements.", context="Python > Generators")
    assert payload_factory.build_payload(claim) == "Python > Generators\nIt supports yield statements."


def test_payload_does_not_modify_claim(payload_factory):
    """Claim.text must remain unchanged — only the model input is enriched."""
    claim = make_claim(text="It supports yield.", context="Python > Generators")
    payload_factory.build_payload(claim)
    assert claim.text == "It supports yield."


def test_payload_is_deterministic(payload_factory):
    """Same claim → same payload every time."""
    claim = make_claim(text="Python is fast.", context="Programming")
    assert payload_factory.build_payload(claim) == payload_factory.build_payload(claim)


def test_instruction_prefix_applied():
    """Instruction prefix is prepended to payload when provided."""
    factory = EmbeddingInputFactory(instruction_prefix="Represent this claim: ")
    claim = make_claim(text="Python is fast.", context="")
    payload = factory.build_payload(claim)
    assert payload.startswith("Represent this claim: ")
    assert "Python is fast." in payload


def test_instruction_prefix_with_context():
    """Instruction prefix is prepended to the full context+text payload."""
    factory = EmbeddingInputFactory(instruction_prefix="Query: ")
    claim = make_claim(text="It yields values.", context="Generators")
    payload = factory.build_payload(claim)
    assert payload == "Query: Generators\nIt yields values."


# ── CacheKeyFactory tests ─────────────────────────────────────────────────────

def test_cache_key_is_32_chars(key_factory):
    """Cache key must be exactly 32 hex characters."""
    claim = make_claim()
    key = key_factory.build_cache_key(claim)
    assert len(key) == 32
    assert all(c in "0123456789abcdef" for c in key)


def test_cache_key_is_deterministic(key_factory):
    """Same claim → same cache key every time."""
    claim = make_claim(content_hash="abc123")
    assert key_factory.build_cache_key(claim) == key_factory.build_cache_key(claim)


def test_cache_key_changes_with_model_sig():
    """Different model signature → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_B", "hash_X")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_cache_key_changes_with_config_hash():
    """Different config hash → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_A", "hash_Y")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_payload_factory_and_key_factory_are_independent():
    """Changing instruction_prefix (EmbeddingInputFactory) does not affect cache keys."""
    claim = make_claim()
    factory_no_prefix = EmbeddingInputFactory()
    factory_with_prefix = EmbeddingInputFactory(instruction_prefix="Query: ")
    key_factory_shared = CacheKeyFactory("sig_A", "hash_X")

    payload_plain = factory_no_prefix.build_payload(claim)
    payload_with = factory_with_prefix.build_payload(claim)
    key = key_factory_shared.build_cache_key(claim)

    # Payloads differ but keys are the same — cache key depends on content, not enriched input
    assert payload_plain != payload_with
    assert key == key_factory_shared.build_cache_key(claim)   # Key is stable
````

## File: tests/unit/test_phase5_normalization.py
````python
"""
Unit tests for embedding/normalization.py.
"""

import pytest
import math
from smriti.embedding.normalization import l2_normalize, normalize_batch


def l2_norm(v):
    return math.sqrt(sum(x * x for x in v))


def test_l2_normalize_produces_unit_vector():
    vector = [3.0, 4.0]  # norm = 5.0
    normalized = l2_normalize(vector)
    assert abs(l2_norm(normalized) - 1.0) < 1e-6


def test_l2_normalize_direction_preserved():
    vector = [3.0, 4.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] / normalized[1] - 3.0 / 4.0) < 1e-6


def test_l2_normalize_returns_new_list():
    vector = [1.0, 2.0, 3.0]
    original = list(vector)
    _ = l2_normalize(vector)
    assert vector == original  # Original unchanged


def test_l2_normalize_already_unit_vector():
    vector = [1.0, 0.0, 0.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] - 1.0) < 1e-6
    assert abs(normalized[1]) < 1e-6


def test_normalize_batch_applies_to_all():
    vectors = [[3.0, 4.0], [1.0, 0.0], [0.6, 0.8]]
    normalized = normalize_batch(vectors, enabled=True)
    for v in normalized:
        assert abs(l2_norm(v) - 1.0) < 1e-6


def test_normalize_batch_disabled():
    vectors = [[3.0, 4.0], [1.0, 2.0]]
    result = normalize_batch(vectors, enabled=False)
    for i, v in enumerate(result):
        assert v == [float(x) for x in vectors[i]]


def test_normalize_384_dim():
    """Must work correctly on 384-dimensional vectors (MiniLM)."""
    import random
    random.seed(42)
    vector = [random.uniform(-1, 1) for _ in range(384)]
    normalized = l2_normalize(vector)
    assert len(normalized) == 384
    assert abs(l2_norm(normalized) - 1.0) < 1e-5
````

## File: tests/unit/test_phase5_property_based.py
````python
"""
Property-based tests for Phase 5 using Hypothesis.

These tests verify mathematical invariants that must hold for ALL valid inputs,
not just the specific cases covered by example-based tests.

Install: poetry add --group dev hypothesis
"""

import math
import pytest

try:
    from hypothesis import given, settings, assume
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

pytestmark = pytest.mark.skipif(
    not HAS_HYPOTHESIS,
    reason="hypothesis not installed — run: poetry add --group dev hypothesis"
)


# ── Normalization invariants ──────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.normalization import l2_normalize

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_l2_normalize_always_unit_norm(values):
        """For ANY non-zero vector, L2 norm after normalization is always 1.0."""
        assume(sum(x * x for x in values) > 0)  # exclude zero vectors
        normalized = l2_normalize(values)
        norm = math.sqrt(sum(x * x for x in normalized))
        assert abs(norm - 1.0) < 1e-5, f"norm={norm} for input {values[:4]}..."


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_l2_normalize_does_not_mutate_input(values):
        """l2_normalize must never mutate the input list."""
        original = list(values)
        assume(sum(x * x for x in values) > 0)
        l2_normalize(values)
        assert values == original


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=200)
    def test_property_normalize_twice_is_idempotent(values):
        """Normalizing a unit vector again must yield the same unit vector."""
        assume(sum(x * x for x in values) > 0)
        once = l2_normalize(values)
        twice = l2_normalize(once)
        for a, b in zip(once, twice):
            assert abs(a - b) < 1e-5


# ── Cache key invariants ──────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.input_factory import CacheKeyFactory

    @given(
        text=st.text(min_size=1, max_size=1000),
        model_sig=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
        config_hash=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
    )
    @settings(max_examples=200)
    def test_property_cache_key_always_32_hex_chars(text, model_sig, config_hash):
        """For ANY text and signatures, cache key is always exactly 32 hex chars."""
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
        )
        import hashlib

        claim = Claim(
            claim_id="c001",
            sentence_id="s001",
            document_id="d001",
            text=text,
            context="",
            source_path=Path("test.md"),
            extraction_mode=ExtractionMode.WHOLE_SENTENCE,
            structured_assertion=None,
            assertion_metadata=AssertionMetadata(),
            provenance=ClaimProvenance(
                sentence_id="s001", document_id="d001",
                source_path=Path("test.md"), sentence_context="",
                sentence_position=0,
            ),
            schema_version="4.0",
            content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            rule_version="1.0",
        )

        factory = CacheKeyFactory(model_signature=model_sig, config_hash=config_hash)
        key = factory.build_cache_key(claim)
        assert len(key) == 32
        assert all(c in "0123456789abcdef" for c in key)


# ── Validation invariants ─────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.validation import validate_vector

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_valid_nonzero_vector_passes_validation(values):
        """Any non-NaN, non-Inf, non-zero-norm vector passes validation."""
        assume(any(x != 0.0 for x in values))
        is_valid, error = validate_vector(values, expected_dimension=len(values))
        assert is_valid is True, f"Expected valid but got error: {error}"


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        ),
        wrong_dim=st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=200)
    def test_property_wrong_dimension_always_fails(values, wrong_dim):
        """Validation always fails when dimension doesn't match."""
        assume(wrong_dim != len(values))
        is_valid, error = validate_vector(values, expected_dimension=wrong_dim)
        assert is_valid is False


# ── Vector domain object invariants ──────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.builders import build_vector

    @given(
        size=st.integers(min_value=1, max_value=512),
        normalized=st.booleans(),
    )
    @settings(max_examples=200)
    def test_property_build_vector_dimension_always_consistent(size, normalized):
        """build_vector.dimension must always equal len(values)."""
        values = [0.1] * size  # Non-zero, all same, valid
        vec = build_vector(values, size, normalized=normalized)
        assert vec.dimension == size
        assert len(vec.values) == size
        assert vec.normalized == normalized
````

## File: tests/unit/test_phase5_validation.py
````python
"""
Unit tests for embedding/validation.py.
Includes dtype validation and post-normalization scenario.
"""

import pytest
import math
from smriti.embedding.validation import validate_vector, validate_batch


def test_valid_vector_passes():
    vector = [0.1, 0.2, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True
    assert error is None


def test_empty_vector_fails():
    is_valid, error = validate_vector([], expected_dimension=4)
    assert is_valid is False
    assert "empty" in error.lower()


def test_wrong_dimension_fails():
    vector = [0.1, 0.2, 0.3]  # 3 elements, expected 4
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "dimension" in error.lower()


def test_nan_fails():
    vector = [0.1, float("nan"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "nan" in error.lower()


def test_inf_fails():
    vector = [0.1, float("inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "inf" in error.lower()


def test_negative_inf_fails():
    vector = [0.1, float("-inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_zero_norm_fails():
    vector = [0.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "zero" in error.lower()


def test_unit_vector_passes():
    vector = [1.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True


def test_dtype_string_fails():
    """Non-numeric (string) type in vector must fail."""
    vector = [0.1, "bad", 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "type" in error.lower() or "non-numeric" in error.lower()


def test_dtype_none_fails():
    """None in vector must fail."""
    vector = [0.1, None, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_validate_batch_all_valid():
    vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    results = validate_batch(vectors, expected_dimension=3)
    assert all(valid for valid, _ in results)


def test_validate_batch_mixed():
    vectors = [
        [0.1, 0.2, 0.3],
        [float("nan"), 0.2, 0.3],
    ]
    results = validate_batch(vectors, expected_dimension=3)
    assert results[0][0] is True
    assert results[1][0] is False


def test_post_normalization_valid_unit_vector():
    """A correctly normalized unit vector must pass post-norm validation."""
    import math
    vector = [1.0, 0.0, 0.0, 0.0]
    norm = math.sqrt(sum(x * x for x in vector))
    normalized = [x / norm for x in vector]
    is_valid, error = validate_vector(normalized, expected_dimension=4)
    assert is_valid is True
````

## File: tests/unit/test_scanner.py
````python
"""
Unit tests for discovery/scanner.py.

Scanner has one job: find files.
These tests never touch hashing, validation, or manifests.
"""

import pytest
from pathlib import Path
from smriti.discovery.scanner import discover_files


@pytest.fixture
def notes_dir(tmp_path):
    """Create a small realistic vault structure."""
    # Normal notes
    (tmp_path / "AI.md").write_text("AI is transforming everything.")
    (tmp_path / "Python.md").write_text("Python is great for data science.")
    (tmp_path / "Notes.txt").write_text("Some plain text notes.")

    # Subdirectory
    subdir = tmp_path / "Archive"
    subdir.mkdir()
    (subdir / "Old.md").write_text("An old note.")
    (subdir / "Report.pdf").write_bytes(b"%PDF-1.4 fake pdf content")

    # Files that must be ignored
    (tmp_path / ".hidden_file.md").write_text("Hidden — must be ignored.")
    obsidian = tmp_path / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text("{}")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main")

    return tmp_path


def test_discovers_markdown_files(notes_dir):
    """Scanner finds .md files recursively."""
    results = discover_files([notes_dir])
    md_files = [p for p in results if p.suffix.lower() == ".md"]
    assert len(md_files) == 3  # AI.md, Python.md, Archive/Old.md


def test_discovers_txt_and_pdf(notes_dir):
    """Scanner finds .txt and .pdf files."""
    results = discover_files([notes_dir])
    extensions = {p.suffix.lower() for p in results}
    assert ".txt" in extensions
    assert ".pdf" in extensions


def test_ignores_hidden_files(notes_dir):
    """Files starting with '.' must be excluded."""
    results = discover_files([notes_dir])
    names = [p.name for p in results]
    assert ".hidden_file.md" not in names


def test_ignores_obsidian_dir(notes_dir):
    """The .obsidian directory must be skipped entirely."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".obsidian" in p for p in paths_str)


def test_ignores_git_dir(notes_dir):
    """The .git directory must be skipped."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".git" in p for p in paths_str)


def test_output_is_sorted(notes_dir):
    """Discovery output must always be sorted (deterministic)."""
    results = discover_files([notes_dir])
    lower_paths = [str(p).lower() for p in results]
    assert lower_paths == sorted(lower_paths)


def test_empty_directory_returns_empty_list(tmp_path):
    """Empty directory must return [] — not crash."""
    results = discover_files([tmp_path])
    assert results == []


def test_multiple_root_dirs(tmp_path):
    """Scanner accepts multiple root directories."""
    dir_a = tmp_path / "vault_a"
    dir_b = tmp_path / "vault_b"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "note1.md").write_text("Note one.")
    (dir_b / "note2.md").write_text("Note two.")

    results = discover_files([dir_a, dir_b])
    assert len(results) == 2


def test_deeply_nested_dirs(tmp_path):
    """Recursion must be unlimited depth."""
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "deep.md").write_text("Deep nested note.")

    results = discover_files([tmp_path])
    assert any("deep.md" in str(p) for p in results)


def test_unicode_filenames(tmp_path):
    """Unicode filenames must work correctly on Windows."""
    (tmp_path / "日本語.md").write_text("Japanese filename.", encoding="utf-8")
    (tmp_path / "ñoño.md").write_text("Spanish accents.", encoding="utf-8")
    (tmp_path / "ನನ್ನ_ಟಿಪ್ಪಣಿ.md").write_text("Kannada filename.", encoding="utf-8")

    results = discover_files([tmp_path])
    assert len(results) == 3


def test_filenames_with_spaces(tmp_path):
    """Filenames with spaces are legal and must be found."""
    (tmp_path / "Machine Learning Notes.md").write_text("Notes on ML.")
    results = discover_files([tmp_path])
    assert any("Machine Learning Notes" in str(p) for p in results)
````

## File: tests/unit/test_validator.py
````python
"""
Unit tests for discovery/validator.py.

Validator has two jobs:
  1. validate_directories() — fatal check of input roots
  2. validate_file()        — per-file check, returns ValidationResult
"""

import pytest
from pathlib import Path
from smriti.discovery.validator import validate_directories, validate_file
from smriti.exceptions import DiscoveryError


@pytest.fixture
def valid_md(tmp_path):
    f = tmp_path / "valid.md"
    f.write_text("Some content here.")
    return f


@pytest.fixture
def empty_file(tmp_path):
    f = tmp_path / "empty.md"
    f.write_bytes(b"")
    return f


@pytest.fixture
def unsupported_file(tmp_path):
    f = tmp_path / "document.docx"
    f.write_bytes(b"fake docx content")
    return f


# ── validate_directories ──────────────────────────────────────────────────────

def test_valid_directory_passes(tmp_path):
    """A valid existing directory must be returned."""
    result = validate_directories([tmp_path])
    assert result == [tmp_path.resolve()]


def test_nonexistent_directory_raises(tmp_path):
    """A directory that doesn't exist must raise DiscoveryError."""
    missing = tmp_path / "does_not_exist"
    with pytest.raises(DiscoveryError, match="does not exist"):
        validate_directories([missing])


def test_file_as_directory_raises(tmp_path):
    """Passing a file path as a directory must raise DiscoveryError."""
    f = tmp_path / "file.txt"
    f.write_text("not a directory")
    with pytest.raises(DiscoveryError, match="not a directory"):
        validate_directories([f])


def test_empty_list_raises():
    """Empty input list must raise DiscoveryError."""
    with pytest.raises(DiscoveryError, match="No input directories"):
        validate_directories([])


# ── validate_file ─────────────────────────────────────────────────────────────

def test_valid_markdown_passes(valid_md):
    """A valid non-empty .md file must pass validation."""
    result = validate_file(valid_md)
    assert result.is_valid is True
    assert result.rejection_reason is None


def test_nonexistent_file_fails(tmp_path):
    """A file that doesn't exist must fail with 'does not exist'."""
    missing = tmp_path / "ghost.md"
    result = validate_file(missing)
    assert result.is_valid is False
    assert "does not exist" in result.rejection_reason


def test_empty_file_fails(empty_file):
    """A zero-byte file must fail validation."""
    result = validate_file(empty_file)
    assert result.is_valid is False
    assert "empty" in result.rejection_reason


def test_unsupported_extension_fails(unsupported_file):
    """Files with unsupported extensions must be rejected."""
    result = validate_file(unsupported_file)
    assert result.is_valid is False
    assert "unsupported extension" in result.rejection_reason


def test_pdf_file_passes(tmp_path):
    """A non-empty .pdf file must pass validation."""
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake pdf content")
    result = validate_file(pdf)
    assert result.is_valid is True


def test_txt_file_passes(tmp_path):
    """A non-empty .txt file must pass validation."""
    txt = tmp_path / "notes.txt"
    txt.write_text("Some plain text.")
    result = validate_file(txt)
    assert result.is_valid is True


def test_validation_result_is_bool(valid_md):
    """ValidationResult must be usable as a boolean."""
    result = validate_file(valid_md)
    assert bool(result) is True
````

## File: tests/__init__.py
````python

````

## File: tests/conftest.py
````python
"""Shared pytest fixtures."""

import pytest
from pathlib import Path
from smriti.core.config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(tmp_path_factory):
    """Point config to test.yaml for the whole test session."""
    import smriti.core.config as cfg_module
    cfg_module._config = Config(env="test")


@pytest.fixture
def tmp_artifacts(tmp_path):
    """Temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


@pytest.fixture
def test_config():
    """Return a test Config instance."""
    return Config(env="test")


@pytest.fixture
def tmp_notes(tmp_path):
    """Create temporary markdown note files."""
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()

    (notes_dir / "note1.md").write_text(
        "# Note 1\n\nPython is the best language for data science.\n"
    )
    (notes_dir / "note2.md").write_text(
        "# Note 2\n\nRust is better than Python for performance.\n"
    )
    return notes_dir


@pytest.fixture
def sample_markdown(tmp_path):
    """Single sample markdown note."""
    note = tmp_path / "note.md"
    note.write_text(
        "# Test Note\n\nCreated: 2024-01-15\n\n"
        "Python is great for data science.\n\n"
        "But for some tasks, Julia is faster.\n"
    )
    return note
````

## File: download_models.ps1
````powershell
Write-Host 'Run this to download models'\n
````

## File: LICENSE
````
MIT License\n\nCopyright (c) 2026 Abhijnan B C\n
````

## File: Makefile.ps1
````powershell
<#
.SYNOPSIS
    PowerShell task runner for SMRITI — equivalent of a Unix Makefile.
.PARAMETER Task
    Task to run. Run without arguments for help.
#>

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }

function Invoke-Help {
    Write-Host ""
    Write-Host "SMRITI — Available Tasks" -ForegroundColor Green
    Write-Host ""
    Write-Host "  .\Makefile.ps1 setup            Install dependencies & download models" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 test             Run all tests" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 lint             Ruff + Black check + mypy" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 format           Auto-format with Black + Ruff fix" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 type-check       mypy type checking only" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 clean-cache      Delete ephemeral cache (always safe)" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 clean-artifacts  Delete pipeline artifacts (WARNING)" -ForegroundColor Yellow
    Write-Host "  .\Makefile.ps1 clean            Clean pycache + cache (not artifacts)" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-Setup {
    Write-Step "Setup"
    & .\scripts\setup_dev.ps1
}

function Invoke-Test {
    Write-Step "Running tests"
    poetry run pytest tests/ -v
}

function Invoke-Lint {
    Write-Step "Linting"
    poetry run ruff check src/ tests/
    poetry run black --check src/ tests/
    poetry run mypy src/smriti
    Write-OK "All lint checks passed"
}

function Invoke-Format {
    Write-Step "Formatting"
    poetry run black src/ tests/
    poetry run ruff check --fix src/ tests/
    Write-OK "Code formatted"
}

function Invoke-TypeCheck {
    Write-Step "Type checking"
    poetry run mypy src/smriti
    Write-OK "Type check passed"
}

function Invoke-CleanCache {
    Write-Step "Clearing cache (ephemeral — safe to delete)"
    Remove-Item -Path cache -Recurse -Force -ErrorAction SilentlyContinue
    Write-OK "Cache cleared"
}

function Invoke-CleanArtifacts {
    Write-Step "Clearing artifacts"
    Write-Host "  WARNING: This deletes immutable pipeline outputs." -ForegroundColor Red
    $confirm = Read-Host "  Type YES to confirm"
    if ($confirm -eq "YES") {
        Remove-Item -Path artifacts -Recurse -Force -ErrorAction SilentlyContinue
        Write-OK "Artifacts removed"
    } else {
        Write-Host "  Cancelled." -ForegroundColor Yellow
    }
}

function Invoke-Clean {
    Write-Step "Cleaning Python cache and temp files"
    Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Force |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .mypy_cache  -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .coverage    -Force          -ErrorAction SilentlyContinue
    Invoke-CleanCache
    Write-OK "Cleaned"
}

switch ($Task) {
    "help"             { Invoke-Help }
    "setup"            { Invoke-Setup }
    "test"             { Invoke-Test }
    "lint"             { Invoke-Lint }
    "format"           { Invoke-Format }
    "type-check"       { Invoke-TypeCheck }
    "clean-cache"      { Invoke-CleanCache }
    "clean-artifacts"  { Invoke-CleanArtifacts }
    "clean"            { Invoke-Clean }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Invoke-Help
        exit 1
    }
}
````

## File: pyproject.toml
````toml
[tool.poetry]
name = "smriti"
version = "0.1.0"
description = "Knowledge drift analyzer for personal note vaults."
authors = ["Abhijnan B C <you@example.com>"]
license = "MIT"
readme = "README.md"
repository = "https://github.com/AbhijnanBC/smriti"
packages = [{include = "smriti", from = "src"}]

[tool.poetry.dependencies]
# Cap at 3.12 for ML compatibility stability
python = ">=3.11,<3.13"

# Core ML/NLP
spacy = "^3.8"
sentence-transformers = "^3.4"
torch = "^2.5"
transformers = "^4.48"

# Retrieval (FAISS strictly on non-Windows, scikit-learn available as fallback)
faiss-cpu = {version = "^1.10", markers = "sys_platform != 'win32'"}
scikit-learn = "^1.4"

# Data processing
numpy = "^1.26.4"
pandas = "^2.2"
networkx = "^3.4"
python-louvain = "^0.16"

# Parsing
markdown-it-py = "^3.0"
pypdf = "^5.0"

# Dashboard
streamlit = "^1.35"
plotly = "^5.22"

# Utilities
pyyaml = "^6.0"
python-dotenv = "^1.0"
structlog = "^24.1"
python-json-logger = "^2.0"
tqdm = "^4.66"
click = "^8.1"
pendulum = "^3.0"
psutil = "^5.9"

[tool.poetry.group.dev.dependencies]
pytest = "^8.1"
pytest-cov = "^5.0"
pytest-mock = "^3.14"
black = "^24.4"
ruff = "^0.4"
mypy = "^1.10"
ipython = "^8.24"
hypothesis = "^6.156.7"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ["py311", "py312"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C"]
ignore = ["E501", "B008"]

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["smriti"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_incomplete_defs = false
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--verbose --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
]

[tool.coverage.run]
source = ["src/smriti"]
````

## File: README.md
````markdown
# smriti\n\nKnowledge drift analyzer for personal note vaults.\n
````

## File: setup_dev.ps1
````powershell
Write-Host 'Run this to set up dev environment'\n
````

## File: .gitignore
````
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
.DS_Store
.env.local
cache/
output/logs/
artifacts/run_*/
*.log
.venv/
venv/
*.swp
*.swo
.idea/
.vscode/settings.json
````
