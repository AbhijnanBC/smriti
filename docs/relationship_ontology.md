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