# SMRITI Phase 7: Semantic Relationship Ontology & Graph Traversal Specification

This document defines the canonical ontology for semantic relationships discovered in Phase 6 and establishes the strict mathematical and traversal rules for the Phase 7 Knowledge Graph construction. 

All downstream consumers, graph traversal algorithms, and temporal reasoning engines must adhere to these invariants.

**RECTIFIED (external review, bidirectional-NLI rewrite):** Phase 6 previously ran NLI in one fixed direction per candidate pair (claim_a as premise, claim_b as hypothesis — an artifact of the pair's lexicographic ID ordering, not of semantic direction). That made it structurally impossible to tell "A entails B" apart from "B entails A" apart from "both claims entail each other" (logical equivalence) apart from "neither" — `SUPPORTS` was always emitted `A_TO_B` regardless of which claim actually did the entailing. Phase 6 now runs NLI in both directions for every candidate pair and adds `EQUIVALENT` to the ontology below. `UNKNOWN` is unchanged in meaning but is now more precisely understood as **ABSTAIN**: the resolver had insufficient or ambiguous evidence in either direction, not that it "guessed wrong."

**RECTIFIED (external review, P0-4 — "UNKNOWN is a resolution status, not a relation type"):** `RelationshipType.UNKNOWN` sitting in the same enum as `CONTRADICTS`/`SUPPORTS`/`REFINES`/`EQUIVALENT`/`NEUTRAL` invites treating it as a sixth relation — reporting "UNKNOWN classification accuracy" as if some correct label existed, when the entire point of abstaining is that the resolver committed to no label at all. `smriti.core.models` now defines `ResolutionStatus` (`RESOLVED` / `ABSTAINED`) and `RelationshipDecision` (`relation_type: Optional[RelationshipType]`, `direction`, `status`, `confidence`, `abstention_reason`), with `relation_type` set to `None` exactly when `status == ABSTAINED` — never `RelationshipType.UNKNOWN` masquerading as a relation. `RelationshipResolver.resolve_as_decision()` produces this directly. `RelationshipType.UNKNOWN` itself is **not removed** (that would break the persisted schema and every existing consumer comparing against it — judged disproportionate to the remaining scope of this remediation); `to_decision()` is the one place that translates between the two representations, so no other code should need to compare against `RelationshipType.UNKNOWN` directly going forward. **All evaluation and reporting code must reason in `ResolutionStatus` terms**: report abstention rate / selective-prediction coverage against pairs a resolver *should* abstain on, never "accuracy" against UNKNOWN as if it were a predicted label competing with the real ones.

---

### 1. Ingestion & Discard Policy

Phase 7 treats the `RelationshipSet` output from Phase 6 as an immutable stream of edges. Before any graph construction begins, the following ingestion filters must be applied:

*   **Valid Edges:** `SUPPORTS`, `CONTRADICTS`, `REFINES`, and `EQUIVALENT` relationships are explicitly ingested into the graph structure.
*   **Neutral Edges:** `NEUTRAL` relationships are dropped during ingestion to prevent graph bloat, as they represent semantic proximity without logical direction.
*   **The Discard Policy:** `UNKNOWN` (ABSTAIN) relationships are strictly dropped at the Phase 6 boundary. They must never enter the Phase 7 graph, as they represent insufficient evidence to commit to any of the other five verdicts and cannot be safely traversed.

---

### 2. Semantic Edge Definitions & Transitivity

The Phase 7 Knowledge Graph relies on the specific mathematical properties of each relationship type to perform safe logical reasoning.

| Relationship Type | Directionality | Transitivity | Graph Usage |
| :--- | :--- | :--- | :--- |
| **SUPPORTS** | Directional (A → B or B → A, per NLI's actual one-way entailment result) | **True** | Builds corroboration chains. If A supports B, and B supports C, the graph infers A indirectly supports C. |
| **CONTRADICTS** | Symmetric (A ↔ B) | **False** | Identifies factual collisions. If A contradicts B, and B contradicts C, A does not necessarily contradict C. |
| **REFINES** | Directional (A → B or B → A) | **False** | Tracks concept elaboration: one-way entailment where the entailing claim is also meaningfully more specific/detailed than the entailed claim (`classification/specificity.py`). Narrowing scope repeatedly may alter the premise, so transitivity cannot be assumed. |
| **EQUIVALENT** | Symmetric (A ↔ B) | **True** (within the equivalence class) | Both claims entail each other — they assert the same proposition in different words. Equivalence classes should be treated as a single logical unit (Phase 7 co-locates equivalent claims in the same partition via Union-Find, same as SUPPORTS/REFINES). **RECTIFIED (provenance/reliability redesign):** Phase 7's evidence aggregation (`aggregation.py`) now collapses EQUIVALENT-linked supporters into evidence groups (`SupportAggregate.independent_evidence_group_ids`, one representative claim_id per equivalence class), and Phase 8's `SourceDiversityExtractor`/`EvidenceIndependenceExtractor` measure over that collapsed set — an equivalent restatement no longer counts as independent corroborating evidence. `SupportAggregate.supporting_claim_ids` itself is unaffected (still every raw supporter, for signals that measure support volume rather than evidence independence). |

`UNKNOWN` (ABSTAIN) carries no directionality or transitivity claim — it is dropped before reaching this table's concerns at all (§1).

---

### 3. Graph Traversal & Boundary Rules

When querying or walking the Phase 7 Knowledge Graph, traversal algorithms must respect structural boundaries to prevent the fusion of incompatible realities into a single context window.

*   **The Contradiction Partition:** `CONTRADICTS` edges act as strict graph partitions. A standard logical traversal (e.g., aggregating facts about a specific topic) must stop immediately upon encountering a `CONTRADICTS` edge.
*   **Graph Bifurcation:** When a contradiction is encountered, the graph effectively bifurcates into competing states of reality. The traversal algorithm must not fuse claims from across the contradiction boundary into a cohesive summary.
*   **Temporal Resolution:** To resolve graph partitions, traversal algorithms must inspect the `ClaimProvenance` timestamps of the conflicting nodes. Graph algorithms must weight these edges by timestamp, allowing the system to prefer the most recent claim as the "current" reality while preserving the older claim strictly as historical evolution.