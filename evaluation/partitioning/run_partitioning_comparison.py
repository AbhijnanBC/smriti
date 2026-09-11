"""
Partitioning-method comparison (P1-5, external "reality check" review).

The review asked for a scientific comparison of the current constraint-based
signed/2-colored partitioning algorithm (evolution/partitioning.py) against
the alternatives it superseded or could have chosen instead, on the SAME
real graph, measuring the same metrics for each:

    1. naive_connected_components   -- ignore relationship type entirely;
                                        any edge (including CONTRADICTS)
                                        merges its endpoints.
    2. contradiction_edge_deletion  -- the pre-P0-1-fix algorithm: delete
                                        CONTRADICTS edges, then connected
                                        components on what remains. Broken
                                        on the documented counter-example
                                        (A supports X, C supports X, A
                                        contradicts C -- A and C still end
                                        up merged via the shared neighbor X).
    3. constraint_based_signed_coloring -- the CURRENT production algorithm
                                        (calls the real, unmodified
                                        evolution.partitioning.run_partitioning
                                        -- not a re-implementation, so this
                                        comparison can never silently drift
                                        from what production actually does).
                                        Guarantees zero contradiction
                                        violations by construction, at the
                                        cost of shattering an entire odd
                                        contradiction cycle into singletons.
    4. weighted_constraint_variant  -- optional variant: on an odd cycle,
                                        instead of giving up on the whole
                                        component, iteratively drops the
                                        LOWEST-CONFIDENCE CONTRADICTS edge
                                        in that component and retries
                                        2-coloring. Preserves more SUPPORTS/
                                        REFINES/EQUIVALENT structure, at the
                                        cost of a small number of measured,
                                        confidence-weighted contradiction
                                        violations (the whole point of
                                        reporting contradiction_violations
                                        as a metric, not a pass/fail gate).

Run against the real, current SMRITI-Reference graph (reference_vault
run 20260911_125340 -- re-pointed here per P1-4, "PLEASE FIX AND SAVE
ME" review round, since the prior RUN_ID predated this session's
resolver/corpus fixes), loaded via the actual production loader
(PipelineRunner._load_phase7_result). No synthetic data, no re-run.

RECTIFIED (P1-4): purity, fragmentation, and ARI/NMI (also requested by
that review round) are NOT reported here -- all three require a
ground-truth reference partition to compare against, and
SMRITI-Reference has no hand-labeled "true" claim-cluster assignment
(it is real prose with LLM-derived relationship labels, not a
constructed corpus with known partition membership). Fabricating a
synthetic ground truth for this specific, real corpus after the fact
would be worse than not reporting these metrics; violation rate,
partition count, singleton rate, and structural-edge retention/cut
(all computable without ground truth) remain the metrics reported
below.

Run with: poetry run python evaluation/partitioning/run_partitioning_comparison.py
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from smriti.pipeline.runner import PipelineRunner
from smriti.core.models import RelationshipType, RelationshipEdge
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning

RUN_ID = "20260911_125340"  # RECTIFIED (P1-4, "PLEASE FIX AND SAVE ME" review round):
# the previous RUN_ID (20260910_163252) predates this session's resolver/
# corpus fixes -- re-pointed at the current reference_vault run (phases
# 1-12, run today) so this comparison is not measuring a stale resolver.
OUT_PATH = str(ROOT / "evaluation" / "partitioning" / "results.json")

STRUCTURAL_TYPES = (RelationshipType.SUPPORTS, RelationshipType.REFINES, RelationshipType.EQUIVALENT)


# ── Method 1: naive connected components (ignores relationship type) ───────

def naive_connected_components(node_ids: Set[str], edges: Dict[str, RelationshipEdge]) -> Dict[str, str]:
    parent = {n: n for n in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for edge in edges.values():
        union(edge.source_node_id, edge.target_node_id)

    return {n: find(n) for n in node_ids}


# ── Method 2: contradiction-edge deletion (the pre-P0-1-fix algorithm) ─────

def contradiction_edge_deletion(node_ids: Set[str], edges: Dict[str, RelationshipEdge]) -> Dict[str, str]:
    parent = {n: n for n in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for edge in edges.values():
        if edge.relationship_type in STRUCTURAL_TYPES:
            union(edge.source_node_id, edge.target_node_id)
        # CONTRADICTS edges are simply ignored (deleted), NOT used as a
        # constraint the way method 3/4 use them -- this is exactly the bug:
        # deleting the direct edge does nothing about a transitive path
        # through a shared SUPPORTS neighbor.

    return {n: find(n) for n in node_ids}


# ── Method 3: the current production algorithm, called directly (not reimplemented) ──

def constraint_based_signed_coloring(node_ids: Set[str], edges: Dict[str, RelationshipEdge]) -> Dict[str, str]:
    nodes_map = {}  # run_partitioning only reads ctx.nodes.keys() and reassigns annotations
    from smriti.core.models import ClaimNode
    from pathlib import Path as _Path
    for nid in node_ids:
        nodes_map[nid] = ClaimNode(
            node_id=nid, claim_id=nid, claim_text="", context="",
            source_path=_Path("x.md"), document_id="d",
        )
    ctx = SemanticReasoningContext(
        nodes=nodes_map, edges=dict(edges), backend=NetworkXBackend(),
        run_id="comparison", config_hash="comparison",
    )
    run_partitioning(ctx)
    return dict(ctx.node_to_partition)


# ── Method 4: weighted-constraint variant (soft-drops low-confidence CONTRADICTS) ──

def weighted_constraint_variant(
    node_ids: Set[str], edges: Dict[str, RelationshipEdge],
) -> Tuple[Dict[str, str], List[Tuple[str, str, float]]]:
    """Same 2-coloring + Union-Find skeleton as the production algorithm,
    but on an odd cycle, drops the lowest-confidence CONTRADICTS edge in
    that specific component and retries instead of singleton-izing the
    whole component. Returns (partition_map, dropped_edges) where
    dropped_edges records exactly which CONTRADICTS constraints were not
    enforced, and at what confidence -- the measured, disclosed cost of
    this variant's better structure preservation."""
    contradiction_constraints: Dict[str, Set[str]] = {n: set() for n in node_ids}
    edge_confidence: Dict[Tuple[str, str], float] = {}
    for edge in edges.values():
        if edge.relationship_type == RelationshipType.CONTRADICTS:
            a, b = edge.source_node_id, edge.target_node_id
            contradiction_constraints[a].add(b)
            contradiction_constraints[b].add(a)
            key = tuple(sorted((a, b)))
            # If multiple CONTRADICTS edges exist between the same pair,
            # keep the lowest confidence (most conservative estimate of
            # how much we'd be violating by dropping it).
            edge_confidence[key] = min(edge_confidence.get(key, 1.0), edge.calibrated_confidence)

    def collect_component(start, constraints):
        component = set()
        queue = deque([start])
        while queue:
            n = queue.popleft()
            if n in component:
                continue
            component.add(n)
            for neighbor in constraints.get(n, set()):
                if neighbor not in component:
                    queue.append(neighbor)
        return component

    def attempt_color(component, constraints):
        colors = {}
        start = min(component)
        colors[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in constraints.get(node, set()):
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[node]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[node]:
                    return None
        return colors

    node_color: Dict[str, int] = {}
    dropped_edges: List[Tuple[str, str, float]] = []
    working_constraints = {n: set(s) for n, s in contradiction_constraints.items()}

    for node_id in sorted(node_ids):
        if not contradiction_constraints[node_id]:
            node_color[node_id] = 0

    for node_id in sorted(node_ids):
        if node_id in node_color:
            continue
        component = collect_component(node_id, working_constraints)
        colors = attempt_color(component, working_constraints)
        while colors is None:
            # Find the lowest-confidence CONTRADICTS edge within this
            # component and drop it, then retry.
            weakest_pair, weakest_conf = None, None
            for a in component:
                for b in working_constraints.get(a, set()):
                    if b in component and a < b:
                        conf = edge_confidence.get((a, b), 1.0)
                        if weakest_conf is None or conf < weakest_conf:
                            weakest_pair, weakest_conf = (a, b), conf
            if weakest_pair is None:
                # Should not happen (a non-2-colorable component always has
                # at least one edge); fail safe to singleton coloring.
                colors = {n: i for i, n in enumerate(sorted(component))}
                break
            a, b = weakest_pair
            working_constraints[a].discard(b)
            working_constraints[b].discard(a)
            dropped_edges.append((a, b, weakest_conf))
            colors = attempt_color(component, working_constraints)
        node_color.update(colors)

    parent = {n: n for n in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb and node_color.get(ra) == node_color.get(rb):
            parent[ra] = rb

    for edge in edges.values():
        if edge.relationship_type in STRUCTURAL_TYPES:
            union(edge.source_node_id, edge.target_node_id)

    return {n: find(n) for n in node_ids}, dropped_edges


# ── Metrics ──────────────────────────────────────────────────────────────

def compute_metrics(
    node_ids: Set[str], edges: Dict[str, RelationshipEdge], partition_map: Dict[str, str],
) -> Dict:
    groups: Dict[str, Set[str]] = {}
    for n, root in partition_map.items():
        groups.setdefault(root, set()).add(n)

    contradiction_violations = 0
    structural_retained = {t.value: 0 for t in STRUCTURAL_TYPES}
    structural_cut = {t.value: 0 for t in STRUCTURAL_TYPES}

    for edge in edges.values():
        same_partition = partition_map.get(edge.source_node_id) == partition_map.get(edge.target_node_id)
        if edge.relationship_type == RelationshipType.CONTRADICTS and same_partition:
            contradiction_violations += 1
        elif edge.relationship_type in STRUCTURAL_TYPES:
            if same_partition:
                structural_retained[edge.relationship_type.value] += 1
            else:
                structural_cut[edge.relationship_type.value] += 1

    sizes = [len(g) for g in groups.values()]
    partition_count = len(groups)
    singleton_count = sum(1 for s in sizes if s == 1)

    densities = []
    for group in groups.values():
        n = len(group)
        if n <= 1:
            continue
        internal = sum(
            1 for e in edges.values()
            if e.source_node_id in group and e.target_node_id in group
            and e.relationship_type != RelationshipType.CONTRADICTS
        )
        max_directed = n * (n - 1)
        densities.append(internal / max_directed)

    return {
        "partition_count": partition_count,
        "node_count": len(node_ids),
        "singleton_count": singleton_count,
        "singleton_rate": round(singleton_count / partition_count, 4) if partition_count else 0.0,
        "avg_partition_size": round(sum(sizes) / partition_count, 4) if partition_count else 0.0,
        "largest_partition_size": max(sizes) if sizes else 0,
        "contradiction_violations": contradiction_violations,
        "structural_edges_retained": structural_retained,
        "structural_edges_cut": structural_cut,
        "total_structural_cut": sum(structural_cut.values()),
        "avg_density_multi_node_partitions": round(sum(densities) / len(densities), 6) if densities else 0.0,
    }


def main():
    class _RunIdOnly:
        run_id = RUN_ID

    graph = PipelineRunner._load_phase7_result(_RunIdOnly())
    node_ids = set(graph.nodes.keys())
    edges = dict(graph.edges)
    print(f"Loaded graph: {len(node_ids)} nodes, {len(edges)} edges (run_id={RUN_ID})")

    contradiction_count = sum(1 for e in edges.values() if e.relationship_type == RelationshipType.CONTRADICTS)
    structural_count = sum(1 for e in edges.values() if e.relationship_type in STRUCTURAL_TYPES)
    print(f"  {contradiction_count} CONTRADICTS edges, {structural_count} SUPPORTS/REFINES/EQUIVALENT edges")

    results = {}

    pm1 = naive_connected_components(node_ids, edges)
    results["naive_connected_components"] = compute_metrics(node_ids, edges, pm1)

    pm2 = contradiction_edge_deletion(node_ids, edges)
    results["contradiction_edge_deletion"] = compute_metrics(node_ids, edges, pm2)

    pm3 = constraint_based_signed_coloring(node_ids, edges)
    results["constraint_based_signed_coloring_CURRENT_PRODUCTION"] = compute_metrics(node_ids, edges, pm3)

    pm4, dropped = weighted_constraint_variant(node_ids, edges)
    metrics4 = compute_metrics(node_ids, edges, pm4)
    metrics4["soft_dropped_contradiction_edges"] = len(dropped)
    metrics4["soft_dropped_edge_confidences"] = sorted(round(c, 4) for _, _, c in dropped)
    results["weighted_constraint_variant"] = metrics4

    results["_meta"] = {
        "run_id": RUN_ID,
        "total_nodes": len(node_ids),
        "total_edges": len(edges),
        "total_contradiction_edges": contradiction_count,
        "total_structural_edges": structural_count,
    }

    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nWrote {OUT_PATH}\n")
    print(f"{'method':<45} {'violations':>10} {'partitions':>10} {'singleton%':>10} {'struct_cut':>10}")
    for name, m in results.items():
        if name == "_meta":
            continue
        print(
            f"{name:<45} {m['contradiction_violations']:>10} {m['partition_count']:>10} "
            f"{m['singleton_rate']*100:>9.1f}% {m['total_structural_cut']:>10}"
        )


if __name__ == "__main__":
    main()
