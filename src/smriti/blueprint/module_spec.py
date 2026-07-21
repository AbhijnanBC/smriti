"""
module_spec.py — Module Architecture (§11.45).

Every SMRITI module must conform to this specification.
The specification defines ownership, interface contracts,
dependency declarations, and lifecycle.

Module Specification fields:
    purpose        — what this module does (single responsibility)
    inputs         — what it accepts
    outputs        — what it produces
    dependencies   — declared module dependencies
    public_interfaces — names that form the public API
    internal_components — names that must not be imported directly
    owner          — single owning architectural region
    replaceability — can it be swapped without affecting architecture?
    lifecycle      — "pipeline_run" | "session" | "request" | "indefinite"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List


@dataclass(frozen=True)
class ModuleSpecification:
    """
    Formal specification of a SMRITI module.

    Used by:
        - Architecture tests (verify public interface boundaries)
        - Documentation generation
        - Compliance engine (verify dependency declarations match imports)
    """
    module_path:          str
    purpose:              str
    inputs:               FrozenSet[str]
    outputs:              FrozenSet[str]
    dependencies:         FrozenSet[str]
    public_interfaces:    FrozenSet[str]
    internal_components:  FrozenSet[str]
    owner:                str
    replaceability:       bool
    lifecycle:            str


class ModuleRegistry:
    """Registry of all formal module specifications."""

    def __init__(self) -> None:
        self._specs: Dict[str, ModuleSpecification] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        specs = [
            ModuleSpecification(
                module_path="smriti.runtime",
                purpose="Govern the operational lifecycle and state transitions of the SMRITI platform.",
                inputs=frozenset({"run_id", "ConfigurationContext"}),
                outputs=frozenset({"RuntimeContext", "HealthStatus", "RuntimeManifest"}),
                dependencies=frozenset({"smriti.core.config", "smriti.core.paths", "smriti.exceptions"}),
                public_interfaces=frozenset({"RuntimeCoordinator", "RuntimeState", "get_runtime"}),
                internal_components=frozenset({"_coordinator", "_state_machine", "_lifecycle"}),
                owner="runtime",
                replaceability=True,
                lifecycle="indefinite",
            ),
            ModuleSpecification(
                module_path="smriti.observability",
                purpose="Make system behavior visible through metrics, health checks, and telemetry.",
                inputs=frozenset({"RuntimeContext", "MetricsCollector"}),
                outputs=frozenset({"HealthReport", "MetricsSnapshot", "TelemetryEvent"}),
                dependencies=frozenset({"smriti.core.config", "smriti.exceptions"}),
                public_interfaces=frozenset({"HealthMonitor", "MetricsCollector", "TelemetryCollector"}),
                internal_components=frozenset({"_events", "_metrics", "_spans"}),
                owner="observability",
                replaceability=True,
                lifecycle="indefinite",
            ),
            ModuleSpecification(
                module_path="smriti.governance",
                purpose="Enforce architectural correctness through rules, ADRs, and compliance verification.",
                inputs=frozenset({"source_files", "ADR"}),
                outputs=frozenset({"ComplianceResult", "MaturityAssessment"}),
                dependencies=frozenset({"smriti.exceptions"}),
                public_interfaces=frozenset({"ComplianceEngine", "ADRRegistry", "RiskRegister"}),
                internal_components=frozenset({"_rules", "_adrs", "_risks"}),
                owner="governance",
                replaceability=False,    # Governance must be architecturally stable
                lifecycle="indefinite",
            ),
            ModuleSpecification(
                module_path="smriti.infrastructure",
                purpose="Provide operational infrastructure (resources, trust, provenance, ownership).",
                inputs=frozenset({"ConfigurationContext", "run_id"}),
                outputs=frozenset({"RuntimeManifest", "ResourceHandle", "OwnershipTable"}),
                dependencies=frozenset({"smriti.core.config", "smriti.core.paths", "smriti.exceptions"}),
                public_interfaces=frozenset({"ResourceGovernor", "ProvenanceBuilder", "OwnershipRegistry"}),
                internal_components=frozenset({"_handles", "_policies"}),
                owner="infrastructure",
                replaceability=True,
                lifecycle="indefinite",
            ),
        ]
        for spec in specs:
            self._specs[spec.module_path] = spec

    def register(self, spec: ModuleSpecification) -> None:
        self._specs[spec.module_path] = spec

    def get(self, module_path: str) -> ModuleSpecification | None:
        return self._specs.get(module_path)

    def all_specs(self) -> List[ModuleSpecification]:
        return list(self._specs.values())