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
    Step 3: Apply Union-Find on SUPPORTS/REFINES/EQUIVALENT edges, but only
            merge nodes that have the SAME color. This ensures contradicting
            claims are never merged into the same partition even if they
            share a neighbor.
    Step 4: Build KnowledgePartition for each Union-Find group.

Complexity: O(N + E) — BFS coloring + Union-Find with path compression.

Invariant guaranteed:
    No two nodes connected by CONTRADICTS will ever be in the same partition.
    This holds even in the presence of shared SUPPORTS neighbors.

STATUS (P1-5, external "reality check" review — partitioning-method
comparison): this hard-constraint algorithm remains the ONLY partitioner
wired into production (evolution/__init__.py -> evolution/construction.py).
A "weighted-constraint variant" (evaluation/partitioning/
run_partitioning_comparison.py::weighted_constraint_variant) was built and
measured for comparison -- on the real reference graph it recovers
meaningfully more SUPPORTS/REFINES/EQUIVALENT structure (99 -> 85
partitions, 55.6% -> 41.2% singleton rate, 32 -> 17 structural edges cut)
at the cost of exactly 1 realized contradiction violation (vs. the 0 this
module guarantees) out of 22 constraints it soft-drops to escape odd
cycles. That is a real, disclosed trade-off, not a strict improvement, and
it has NOT been promoted here: this module still enforces the hard
zero-violation guarantee, unconditionally. Do not wire the weighted
variant into this function without an explicit decision to trade away
that guarantee.
"""

from __future__ import annotations

import dataclasses
import hashlib
from collections import deque

import structlog

from smriti.core.models import (
    KnowledgePartition,
    NodeAnnotations,
    RelationshipType,
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
    contradiction_constraints: dict[str, set[str]] = {nid: set() for nid in all_node_ids}
    for edge in ctx.edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            contradiction_constraints[edge.source_node_id].add(edge.target_node_id)
            contradiction_constraints[edge.target_node_id].add(edge.source_node_id)

    # ── Step 2: 2-color the contradiction graph ───────────────────────────────
    # Color 0 and Color 1 are the two contradiction "sides".
    # Nodes that CONTRADICT each other must have different colors.
    # If not 2-colorable (odd cycle), each node in the conflicting group
    # gets a unique color (conservative: separate partition per node).
    node_color: dict[str, int] = {}
    color_counter = [2]  # Colors 0 and 1 are standard; higher = isolated

    def collect_component(start: str) -> set[str]:
        """BFS over the contradiction graph to collect a full connected component."""
        component: set[str] = set()
        queue = deque([start])
        while queue:
            n = queue.popleft()
            if n in component:
                continue
            component.add(n)
            for neighbor in contradiction_constraints.get(n, set()):
                if neighbor not in component:
                    queue.append(neighbor)
        return component

    def try_bipartite_color(component: set[str]) -> dict[str, int] | None:
        """
        Attempt to 2-color a connected component in isolation (a fresh, local
        dict — never touching node_color directly). Returns None if the
        component contains an odd contradiction cycle (not 2-colorable).

        Isolating the attempt is essential: a BFS that writes partial colors
        directly into node_color and bails out on the first conflict leaves
        already-visited nodes holding colors that were never validated
        against edges the BFS had not reached yet — exactly the kind of
        edge an odd cycle produces. Attempting in a scratch dict and only
        committing on full success avoids leaking that inconsistent state.
        """
        colors: dict[str, int] = {}
        start = min(component)
        colors[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in contradiction_constraints.get(node, set()):
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[node]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[node]:
                    return None  # Odd cycle — not 2-colorable
        return colors

    # Nodes with no contradiction constraints at all share a common default
    # color so that SUPPORTS/REFINES chains among them can freely merge.
    for node_id in sorted(all_node_ids):
        if not contradiction_constraints[node_id]:
            node_color[node_id] = 0

    # Process connected components of the contradiction graph that have constraints.
    for node_id in sorted(all_node_ids):
        if node_id in node_color:
            continue
        component = collect_component(node_id)
        colors = try_bipartite_color(component)
        if colors is not None:
            node_color.update(colors)
        else:
            # Odd contradiction cycle detected (e.g. A contradicts B contradicts
            # C contradicts A). DESIGN DECISION: degrade the ENTIRE component
            # into singleton partitions rather than attempting approximate
            # graph-cut optimization — every node in the component gets its
            # own unique color, so no two of them can ever be merged in
            # Step 3, regardless of which pair the odd cycle involved.
            for n in sorted(component):
                node_color[n] = color_counter[0]
                color_counter[0] += 1

    # ── Step 3: Union-Find on SUPPORTS/REFINES edges (same-color only) ────────
    parent: dict[str, str] = {nid: nid for nid in all_node_ids}

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
        # EQUIVALENT claims (bidirectional-NLI rewrite) say the same thing;
        # they must be co-located at least as strongly as SUPPORTS/REFINES.
        if edge.relationship_type in (
            RelationshipType.SUPPORTS,
            RelationshipType.REFINES,
            RelationshipType.EQUIVALENT,
        ):
            union(edge.source_node_id, edge.target_node_id)

    # ── Step 4: Build KnowledgePartition for each Union-Find group ───────────
    # Group nodes by their root in Union-Find
    groups: dict[str, set[str]] = {}
    for node_id in sorted(all_node_ids):
        root = find(node_id)
        groups.setdefault(root, set()).add(node_id)

    partitions: dict[str, KnowledgePartition] = {}
    node_to_partition: dict[str, str] = {}

    for root, group_nodes in groups.items():
        node_ids = frozenset(group_nodes)
        partition_id = _compute_partition_id(node_ids)
        stable_label = tuple(sorted(node_ids))  # Store as a sorted tuple

        # Find internal edges (SUPPORTS/REFINES/EQUIVALENT within this partition)
        internal_edges = {}
        supports_count = 0
        refines_count = 0
        equivalent_count = 0

        for edge_id, edge in ctx.edges.items():
            if (
                edge.source_node_id in node_ids
                and edge.target_node_id in node_ids
                and edge.relationship_type != RelationshipType.CONTRADICTS
            ):
                internal_edges[edge_id] = edge
                if edge.relationship_type == RelationshipType.SUPPORTS:
                    supports_count += 1
                elif edge.relationship_type == RelationshipType.REFINES:
                    refines_count += 1
                elif edge.relationship_type == RelationshipType.EQUIVALENT:
                    equivalent_count += 1

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
            equivalent_count=equivalent_count,
        )
        partitions[partition_id] = partition
        for nid in node_ids:
            node_to_partition[nid] = partition_id

    # ── Verify all nodes assigned ─────────────────────────────────────────────
    unassigned = all_node_ids - set(node_to_partition.keys())
    if unassigned:
        raise PartitioningError(
            f"Partitioning left {len(unassigned)} nodes unassigned: " f"{sorted(unassigned)[:5]}"
        )

    # ── Verify partition invariant: no CONTRADICTS within any partition ────────
    for partition in partitions.values():
        for edge_id, edge in ctx.edges.items():
            if (
                edge.relationship_type == RelationshipType.CONTRADICTS
                and edge.source_node_id in partition.node_ids
                and edge.target_node_id in partition.node_ids
            ):
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

    adj: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for edge in internal_edges.values():
        if edge.relationship_type == RelationshipType.SUPPORTS:
            adj[edge.source_node_id].append(edge.target_node_id)

    def dfs_length(node: str, visited: set[str]) -> int:
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
