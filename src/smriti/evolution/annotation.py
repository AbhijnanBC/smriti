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