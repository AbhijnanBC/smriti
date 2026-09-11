"""
ownership.py — Operational Ownership Model (§11.18 addition).

Every infrastructure subsystem has exactly one architectural owner.
This file is the authoritative single-source-of-truth for ownership.

Principle: Every subsystem has exactly one owner,
           and every owner has one clearly defined responsibility.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubsystemOwnership:
    """Ownership declaration for a single SMRITI subsystem."""

    subsystem: str
    owner: str
    responsibility: str
    module_path: str


# ── Canonical ownership table ─────────────────────────────────────────────────

OWNERSHIP_TABLE: dict[str, SubsystemOwnership] = {
    "configuration": SubsystemOwnership(
        subsystem="Configuration",
        owner="ConfigurationManager",
        responsibility="Load, freeze, and expose immutable runtime configuration.",
        module_path="smriti.core.config",
    ),
    "runtime_state": SubsystemOwnership(
        subsystem="RuntimeState",
        owner="RuntimeCoordinator",
        responsibility="Coordinate runtime lifecycle, state transitions, and health.",
        module_path="smriti.runtime.coordinator",
    ),
    "resources": SubsystemOwnership(
        subsystem="Resources",
        owner="ResourceGovernor",
        responsibility="Allocate, track, and release all operational resources.",
        module_path="smriti.infrastructure.resources",
    ),
    "policies": SubsystemOwnership(
        subsystem="Policies",
        owner="PolicyEngine",
        responsibility="Enforce interaction policies across dashboard workspaces.",
        module_path="smriti.dashboard.policies.policies",
    ),
    "telemetry": SubsystemOwnership(
        subsystem="Telemetry",
        owner="TelemetryCollector",
        responsibility="Collect, aggregate, and export operational events and metrics.",
        module_path="smriti.observability.telemetry",
    ),
    "dependency_graph": SubsystemOwnership(
        subsystem="DependencyGraph",
        owner="DependencyCoordinator",
        responsibility="Construct, validate, and resolve component dependencies.",
        module_path="smriti.runtime.composition",
    ),
    "knowledge_api": SubsystemOwnership(
        subsystem="KnowledgeAPI",
        owner="KnowledgeAccessService",
        responsibility="Provide controlled read-only access to the knowledge graph.",
        module_path="smriti.api",
    ),
    "observability": SubsystemOwnership(
        subsystem="Observability",
        owner="ObservabilityLayer",
        responsibility="Make system behavior visible without modifying it.",
        module_path="smriti.observability",
    ),
    "provenance": SubsystemOwnership(
        subsystem="Provenance",
        owner="ProvenanceBuilder",
        responsibility="Record and persist the runtime manifest for reproducibility.",
        module_path="smriti.infrastructure.provenance",
    ),
}


class OwnershipRegistry:
    """
    Queryable registry for subsystem ownership.

    Used by governance and compliance checks.
    """

    def __init__(self) -> None:
        self._table = OWNERSHIP_TABLE.copy()

    def owner_of(self, subsystem: str) -> SubsystemOwnership | None:
        return self._table.get(subsystem.lower().replace(" ", "_"))

    def all_subsystems(self) -> list[SubsystemOwnership]:
        return list(self._table.values())

    def is_registered(self, subsystem: str) -> bool:
        return subsystem.lower().replace(" ", "_") in self._table
