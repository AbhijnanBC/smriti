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
    - Follows SUPPORTS and EQUIVALENT edges within the same partition
      (RECTIFIED, bidirectional-NLI rewrite: an EQUIVALENT claim restates
      the same proposition and is genuine corroborating evidence for it,
      same as SUPPORTS)
    - Counts each unique supporting claim_id exactly ONCE (supporting_claim_ids)
    - RECTIFIED (provenance/reliability redesign): additionally collapses
      EQUIVALENT-linked supporters into evidence groups
      (independent_evidence_group_ids), one representative claim_id per
      group, so a paraphrase of an already-counted supporter does not
      inflate source-diversity or evidence-independence signals as a
      second, independent piece of evidence -- those signals should read
      independent_evidence_group_ids, not supporting_claim_ids.
    - CONTRADICTS edges never contribute support
    - Aggregation never modifies edge confidence values
    - Never crosses partition boundaries
"""

from __future__ import annotations

import dataclasses
from collections import deque

import structlog

from smriti.core.models import NodeAnnotations, RelationshipType, SupportAggregate
from smriti.evolution.context import SemanticReasoningContext

logger = structlog.get_logger(__name__)


# Implements union-find-based transitive evidence aggregation (BFS +
# EQUIVALENT-cycle handling + equivalence-class deduplication, per the
# RECTIFIED comments throughout); each step is independently documented
# and load-bearing for correctness, not accidental complexity.
def run_evidence_aggregation(ctx: SemanticReasoningContext) -> None:  # noqa: C901
    """
    Aggregate SUPPORTS evidence for every node within its partition.
    Counts unique provenance root claim IDs, not traversal paths.
    """
    aggregates: dict[str, SupportAggregate] = {}

    for _partition_id, partition in ctx.partitions.items():
        partition_node_ids = partition.node_ids

        # Precompute: for each node, which SUPPORTS edges point TO it (same partition)
        incoming_supports: dict[str, list] = {nid: [] for nid in partition_node_ids}
        # Also track: for each supporting claim, its edge confidence
        claim_confidence: dict[str, float] = {}  # claim_id → confidence of its direct support edge

        for edge in ctx.edges.values():
            if (
                edge.relationship_type in (RelationshipType.SUPPORTS, RelationshipType.EQUIVALENT)
                and edge.target_node_id in partition_node_ids
                and edge.source_node_id in partition_node_ids
            ):
                incoming_supports[edge.target_node_id].append(edge)
                # Store per-claim confidence for the first direct edge encountered
                if edge.source_node_id not in claim_confidence:
                    claim_confidence[edge.source_node_id] = edge.calibrated_confidence
                # EQUIVALENT is symmetric (unlike SUPPORTS): claim_a and
                # claim_b each support the other, but source/target on the
                # stored edge are fixed by claim_id_a/claim_id_b's
                # lexicographic order, not by direction. Mirror the edge so
                # the source node also sees the target as a supporter.
                if edge.relationship_type == RelationshipType.EQUIVALENT:
                    mirrored = dataclasses.replace(
                        edge,
                        source_node_id=edge.target_node_id,
                        target_node_id=edge.source_node_id,
                        edge_id=f"{edge.edge_id}_equiv_mirror",
                    )
                    incoming_supports[mirrored.target_node_id].append(mirrored)
                    if mirrored.source_node_id not in claim_confidence:
                        claim_confidence[mirrored.source_node_id] = mirrored.calibrated_confidence

        for node_id in partition_node_ids:
            # BFS: collect all transitive UNIQUE CLAIM IDs (not unique paths)
            # RECTIFIED (P0-2): supporting_ids tracks claim IDs seen,
            # ensuring each supporting claim is counted at most once regardless
            # of how many paths lead from it to node_id.
            supporting_ids: set[str] = set()
            total_confidence = 0.0

            # RECTIFIED (provenance/reliability redesign): union-find over
            # EQUIVALENT-linked supporters, so a paraphrase reachable via an
            # EQUIVALENT edge collapses into the same evidence group as the
            # claim it restates, instead of counting as a second, independent
            # supporter. Scoped to this node's own BFS -- "equivalent within
            # THIS claim's evidence" -- not a global equivalence partition.
            equiv_parent: dict[str, str] = {}

            # `parent` is bound as a default argument (evaluated once, at
            # definition time, to *this* iteration's equiv_parent dict)
            # rather than captured by reference from the enclosing loop --
            # each node_id iteration gets its own fresh equiv_parent, and
            # binding it late would tie every iteration's _find/_union to
            # whichever dict happens to be current when they're eventually
            # called, which is only safe here because they're always called
            # within the same iteration that defines them.
            def _find(x: str, parent: dict[str, str] = equiv_parent) -> str:
                root = x
                while parent.get(root, root) != root:
                    root = parent[root]
                while parent.get(x, x) != root:
                    parent[x], x = root, parent.get(x, root)
                return root

            def _union(a: str, b: str, parent: dict[str, str] = equiv_parent) -> None:
                ra, rb = _find(a, parent), _find(b, parent)
                if ra != rb:
                    parent[ra] = rb

            # RECTIFIED (external review, P1-2 "evidence aggregation /
            # double counting"): track the hop distance (BFS depth) at
            # which each supporting claim is FIRST discovered. Since the
            # queue is processed in strict FIFO order and children are
            # always enqueued at depth+1, the first discovery of any
            # claim is necessarily its shortest path from node_id -- a
            # claim also reachable the long way around some other path is
            # still classified by the short path, not the long one.
            hop_distance: dict[str, int] = {}
            queue = deque((edge, 1) for edge in incoming_supports.get(node_id, []))
            visited_edge_ids: set[str] = set()

            while queue:
                edge, depth = queue.popleft()
                if edge.edge_id in visited_edge_ids:
                    continue
                visited_edge_ids.add(edge.edge_id)

                source_id = edge.source_node_id
                # RECTIFIED (bidirectional-NLI rewrite): EQUIVALENT is
                # mutual support (A supports B AND B supports A via the
                # mirrored edge above), which forms a genuine 2-cycle in
                # this BFS's traversal graph -- something a strictly
                # directional SUPPORTS/REFINES DAG could never produce
                # between the same two claims. Walking that cycle
                # (node_id -> B -> node_id) would otherwise re-discover
                # node_id itself as its own "transitive supporter." A claim
                # can never count as evidence for itself.
                if source_id != node_id and source_id not in supporting_ids:
                    # First time we reach this claim — count its contribution
                    supporting_ids.add(source_id)
                    total_confidence += claim_confidence.get(source_id, edge.calibrated_confidence)
                    hop_distance[source_id] = depth
                if (
                    edge.relationship_type == RelationshipType.EQUIVALENT
                    and edge.source_node_id != node_id
                    and edge.target_node_id != node_id
                ):
                    _union(edge.source_node_id, edge.target_node_id)
                # Always BFS further upstream (even if we've seen source_id before,
                # there may be new unique supporters upstream)
                for upstream_edge in incoming_supports.get(source_id, []):
                    if upstream_edge.edge_id not in visited_edge_ids:
                        queue.append((upstream_edge, depth + 1))

            # One representative claim_id per EQUIVALENT-equivalence-class
            # among the supporters; a supporter with no EQUIVALENT edge to
            # any other supporter is its own singleton group. The union-find
            # root is an arbitrary member of the class, not necessarily
            # deterministic across dict-iteration order -- pick the
            # lexicographically smallest actual member of each group as the
            # stable, reproducible representative instead.
            group_members: dict[str, list] = {}
            for cid in supporting_ids:
                group_members.setdefault(_find(cid), []).append(cid)
            independent_evidence_group_ids = tuple(
                sorted(min(members) for members in group_members.values())
            )

            # Each evidence group's hop distance is the SHORTEST hop
            # distance among its members (P1-2): if any member of a
            # semantic-duplicate group is directly reachable, the group as
            # a whole counts as direct evidence, not derived.
            direct_ids, derived_ids, multi_hop_ids = [], [], []
            group_hop_distance: dict[str, int] = {}
            for members in group_members.values():
                rep = min(members)
                min_hop = min(hop_distance.get(m, 1) for m in members)
                group_hop_distance[rep] = min_hop
                if min_hop <= 1:
                    direct_ids.append(rep)
                elif min_hop == 2:
                    derived_ids.append(rep)
                else:
                    multi_hop_ids.append(rep)
            direct_evidence_group_ids = tuple(sorted(direct_ids))
            derived_evidence_group_ids = tuple(sorted(derived_ids))
            multi_hop_evidence_group_ids = tuple(sorted(multi_hop_ids))

            # Discounted evidence strength/confidence: each evidence
            # group should contribute policy.evidence.{direct,derived,
            # multi_hop}_evidence_weight instead of a flat 1.0. Phase 7
            # (this module) has no access to Phase 8's ReliabilityPolicy
            # config -- deliberately, to keep phase boundaries clean --
            # so the RAW per-group hop classification is stored above
            # (direct/derived/multi_hop_evidence_group_ids) and only a
            # DEFAULT-weighted value is precomputed here; scoring/
            # signals/evidence.py recomputes with the ACTUAL configured
            # policy weights from these group-id tuples rather than
            # trusting this default.
            group_confidence: dict[str, float] = {}
            for members in group_members.values():
                rep = min(members)
                confs = [claim_confidence.get(m, 0.0) for m in members]
                group_confidence[rep] = sum(confs) / len(confs) if confs else 0.0
            # Provisional discounted values using this module's own default
            # weights (1.0 / 0.6 / 0.3, mirroring EvidencePolicy's
            # defaults) so this field is never None for a real aggregate
            # -- signals/evidence.py recomputes with the ACTUAL configured
            # policy weights rather than trusting this default blindly,
            # but a sensible default here keeps this dataclass field
            # self-consistent for any other reader.
            default_weights = {"direct": 1.0, "derived": 0.6, "multi_hop": 0.3}
            weighted_group_sum = (
                default_weights["direct"] * len(direct_evidence_group_ids)
                + default_weights["derived"] * len(derived_evidence_group_ids)
                + default_weights["multi_hop"] * len(multi_hop_evidence_group_ids)
            )
            weighted_conf_numerator = (
                sum(
                    default_weights["direct"] * group_confidence[g]
                    for g in direct_evidence_group_ids
                )
                + sum(
                    default_weights["derived"] * group_confidence[g]
                    for g in derived_evidence_group_ids
                )
                + sum(
                    default_weights["multi_hop"] * group_confidence[g]
                    for g in multi_hop_evidence_group_ids
                )
            )
            discounted_evidence_strength = round(weighted_group_sum, 6)
            discounted_weighted_confidence = (
                round(weighted_conf_numerator / weighted_group_sum, 6)
                if weighted_group_sum > 0
                else 0.0
            )

            # Weighted confidence = mean over unique supporting claims
            weighted_confidence = total_confidence / len(supporting_ids) if supporting_ids else 0.0
            summary = (
                f"{len(supporting_ids)} unique supporting claim(s), "
                f"avg confidence {weighted_confidence:.2f}"
                if supporting_ids
                else "No supporting evidence"
            )

            aggregates[node_id] = SupportAggregate(
                support_count=len(supporting_ids),
                weighted_confidence=round(weighted_confidence, 6),
                supporting_claim_ids=tuple(sorted(supporting_ids)),
                evidence_summary=summary,
                independent_evidence_group_ids=independent_evidence_group_ids,
                independent_evidence_group_count=len(independent_evidence_group_ids),
                direct_evidence_group_ids=direct_evidence_group_ids,
                derived_evidence_group_ids=derived_evidence_group_ids,
                multi_hop_evidence_group_ids=multi_hop_evidence_group_ids,
                discounted_evidence_strength=discounted_evidence_strength,
                discounted_weighted_confidence=discounted_weighted_confidence,
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
