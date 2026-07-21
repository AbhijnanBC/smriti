"""
trust.py — Trust Boundaries & Security Model (§11.11).

Defines architectural trust — not cybersecurity. Establishes which
data is trusted, validated, immutable, or controlled at each boundary.

Trust Boundary Flow:
    User
      ↓  (BOUNDARY: validate all input)
    Dashboard (Interaction Layer)
      ↓  (BOUNDARY: DTOs — typed, validated)
    Knowledge API
      ↓  (BOUNDARY: read-only — no mutations)
    Read Store
      ↓  (BOUNDARY: immutable — no writes)
    Knowledge Graph (source of truth)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class TrustLevel(str, Enum):
    """Classification of data trust at each architectural boundary."""
    TRUSTED       = "trusted"       # Internal, typed, validated
    VALIDATED     = "validated"     # External input that passed validation
    IMMUTABLE     = "immutable"     # Cannot be modified — read-only contract
    CONTROLLED    = "controlled"    # Access mediated through an explicit interface
    PROHIBITED    = "prohibited"    # Access is architecturally forbidden


@dataclass(frozen=True)
class TrustBoundary:
    """
    Formal trust boundary between two architectural layers.

    Specifies what is trusted, what must be validated, and what is
    forbidden at each crossing point.
    """
    name:                   str
    from_layer:             str
    to_layer:               str
    trusted_data:           FrozenSet[str]
    validated_data:         FrozenSet[str]
    immutable_data:         FrozenSet[str]
    controlled_interfaces:  FrozenSet[str]
    prohibited_access:      FrozenSet[str]


class TrustModel:
    """
    The complete SMRITI architectural trust model.

    Used by the compliance layer and architecture tests to verify
    that no component crosses a prohibited trust boundary.
    """

    BOUNDARIES: tuple[TrustBoundary, ...] = (

        TrustBoundary(
            name="user_to_dashboard",
            from_layer="user",
            to_layer="dashboard",
            trusted_data=frozenset(),
            validated_data=frozenset({"search_query", "workspace_selection", "export_format"}),
            immutable_data=frozenset(),
            controlled_interfaces=frozenset({"InteractionDispatcher"}),
            prohibited_access=frozenset({"KnowledgeAPI", "ReadStore", "KnowledgeGraph"}),
        ),

        TrustBoundary(
            name="dashboard_to_knowledge_api",
            from_layer="dashboard",
            to_layer="knowledge_api",
            trusted_data=frozenset({"PresentationModel", "DTOs"}),
            validated_data=frozenset({"KnowledgeRequest"}),
            immutable_data=frozenset({"KnowledgeResponse"}),
            controlled_interfaces=frozenset({"ServiceClient", "KnowledgeAccessService"}),
            prohibited_access=frozenset({"ReadStore", "MemoryStore", "ScoredKnowledgeGraph"}),
        ),

        TrustBoundary(
            name="knowledge_api_to_read_store",
            from_layer="knowledge_api",
            to_layer="read_store",
            trusted_data=frozenset({"ClaimDTO", "SchemaRegistry"}),
            validated_data=frozenset(),
            immutable_data=frozenset({"MemoryStore", "KnowledgeSnapshot"}),
            controlled_interfaces=frozenset({"ReadStore", "KnowledgeSnapshot"}),
            prohibited_access=frozenset({"Dashboard", "Session", "EpistemicState"}),
        ),

        TrustBoundary(
            name="read_store_to_knowledge_graph",
            from_layer="read_store",
            to_layer="knowledge_graph",
            trusted_data=frozenset(),
            validated_data=frozenset(),
            immutable_data=frozenset({"KnowledgeGraph", "ScoredKnowledgeGraph"}),
            controlled_interfaces=frozenset({"ReadStore"}),
            prohibited_access=frozenset({"Dashboard", "API", "Interaction"}),
        ),
    )

    @classmethod
    def get_boundary(cls, from_layer: str, to_layer: str) -> TrustBoundary | None:
        for b in cls.BOUNDARIES:
            if b.from_layer == from_layer and b.to_layer == to_layer:
                return b
        return None

    @classmethod
    def is_access_prohibited(cls, from_layer: str, target: str) -> bool:
        for b in cls.BOUNDARIES:
            if b.from_layer == from_layer and target in b.prohibited_access:
                return True
        return False