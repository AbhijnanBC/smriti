"""
state_ownership.py — State Ownership Graph (§11.12 rectified).

RECTIFIED (P2-3): State taxonomy (BusinessState, RuntimeStateCategory,
OperationalState) was excellent but ownership relationships were not defined.

StateOwnershipGraph defines:
    RuntimeContext   owns  Session
    Session          owns  InteractionHistory
    ConfigContext    owns  PolicySnapshot
    ResourceGovernor owns  ResourceHandle

This prevents ambiguous ownership and clarifies lifetime responsibility.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OwnershipRelation:
    """One ownership relationship: owner → owned."""

    owner: str  # e.g. "RuntimeContext"
    owned: str  # e.g. "Session"
    lifetime: str  # "inherits" | "independent" | "scoped"
    notes: str = ""


# ── Canonical ownership graph ─────────────────────────────────────────────────

OWNERSHIP_RELATIONS: list[OwnershipRelation] = [
    OwnershipRelation(
        owner="RuntimeContext",
        owned="Session",
        lifetime="inherits",
        notes="Session lifetime is bounded by RuntimeContext lifetime.",
    ),
    OwnershipRelation(
        owner="Session",
        owned="InteractionHistory",
        lifetime="inherits",
        notes="History is discarded when session ends.",
    ),
    OwnershipRelation(
        owner="Session",
        owned="EpistemicState",
        lifetime="inherits",
        notes="Epistemic state is session-scoped.",
    ),
    OwnershipRelation(
        owner="ConfigurationContext",
        owned="PolicySnapshot",
        lifetime="inherits",
        notes="Policy snapshot is frozen alongside configuration.",
    ),
    OwnershipRelation(
        owner="ResourceGovernor",
        owned="ResourceHandle",
        lifetime="scoped",
        notes="Handles are released when ResourceGovernor.release() is called.",
    ),
    OwnershipRelation(
        owner="OperationalContext",
        owned="ResourceGovernor",
        lifetime="inherits",
        notes="ResourceGovernor lifetime is bounded by the execution context.",
    ),
    OwnershipRelation(
        owner="OperationalContext",
        owned="TelemetryCollector",
        lifetime="inherits",
        notes="Telemetry is flushed when context ends.",
    ),
]


class StateOwnershipGraph:
    """
    RECTIFIED (P2-3): Queryable state ownership graph.

    Usage:
        graph = StateOwnershipGraph()
        graph.owned_by("Session")          → ["InteractionHistory", "EpistemicState"]
        graph.owner_of("InteractionHistory") → "Session"
    """

    def __init__(self) -> None:
        self._relations: list[OwnershipRelation] = list(OWNERSHIP_RELATIONS)

    def owned_by(self, owner: str) -> list[str]:
        return [r.owned for r in self._relations if r.owner == owner]

    def owner_of(self, owned: str) -> str | None:
        for r in self._relations:
            if r.owned == owned:
                return r.owner
        return None

    def ownership_chain(self, start: str) -> list[str]:
        """Return full ownership chain from start to root."""
        chain = [start]
        current = start
        visited = set()
        while True:
            parent = self.owner_of(current)
            if parent is None or parent in visited:
                break
            chain.append(parent)
            visited.add(current)
            current = parent
        return chain

    def all_relations(self) -> list[OwnershipRelation]:
        return list(self._relations)

    def register(self, relation: OwnershipRelation) -> None:
        """Add a custom ownership relation."""
        self._relations.append(relation)
