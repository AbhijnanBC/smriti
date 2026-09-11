"""
contracts.py — Interface Contract Architecture (§11.46).

Defines formal interface contracts for every public API in SMRITI.
Contracts specify:
    - Name, module, owner, version
    - Stability level (from governance)
    - Method signatures (descriptions)
    - Input/output schemas (descriptive)

The ContractRegistry is the authoritative source for interface contracts.
It is used by governance, documentation, and compliance verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from smriti.governance.evolution import StabilityLevel


@dataclass(frozen=True)
class InterfaceDescriptor:
    """
    Formal description of a public interface contract.

    Contracts are immutable once registered. Updates require a new version.
    """

    name: str
    module: str
    owner: str
    stability: StabilityLevel
    version: str
    methods: dict[str, str] = field(default_factory=dict)  # method_name -> description
    input_schema: dict[str, str] = field(default_factory=dict)  # param_name -> type description
    output_schema: str = ""  # return type description
    is_deprecated: bool = False
    deprecation_message: str = ""


class ContractRegistry:
    """
    Registry of all public interface contracts.

    Contracts are registered at startup. The registry is immutable
    after initialization (no modification of existing contracts).
    """

    def __init__(self) -> None:
        self._contracts: dict[str, InterfaceDescriptor] = {}
        self._populate_defaults()

    def _populate_defaults(self) -> None:
        """Pre-populate canonical SMRITI interface contracts."""
        defaults = [
            InterfaceDescriptor(
                name="KnowledgeAccessService",
                module="smriti.api",
                owner="api",
                stability=StabilityLevel.STABLE,
                version="1.0",
                methods={
                    "query": "Execute a knowledge query and return results.",
                    "explain": "Return explanations for a given claim.",
                    "export": "Export query results in specified format.",
                },
                input_schema={
                    "query": "string (search terms or structured query)",
                    "limit": "int (max results, default 20)",
                    "projection": "list of strings (fields to include)",
                },
                output_schema="KnowledgeResponse (contains claims, scores, metadata)",
            ),
            InterfaceDescriptor(
                name="PipelineRunner",
                module="smriti.pipeline.runner",
                owner="pipeline",
                stability=StabilityLevel.STABLE,
                version="1.0",
                methods={
                    "run": "Execute the full pipeline from Phase 0 to Phase 11.",
                },
                input_schema={
                    "start_from": "int (phase to start from, default 0)",
                    "stop_at": "int (phase to stop at, default None)",
                },
                output_schema="PipelineResult (contains run_id, manifest path)",
            ),
            InterfaceDescriptor(
                name="RuntimeCoordinator",
                module="smriti.runtime.coordinator",
                owner="runtime",
                stability=StabilityLevel.STABLE,
                version="1.0",
                methods={
                    "start": "Initialize and activate the runtime.",
                    "stop": "Gracefully shut down the runtime.",
                    "mark_degraded": "Transition to DEGRADED state.",
                    "attempt_recovery": "Attempt to recover from DEGRADED state.",
                    "health_status": "Return current health snapshot.",
                },
                input_schema={
                    "run_id": "string (unique identifier for this execution)",
                    "reason": "string (optional reason for state transitions)",
                },
                output_schema="RuntimeStatus (includes state, health, uptime)",
            ),
            InterfaceDescriptor(
                name="TelemetryCollector",
                module="smriti.observability.telemetry",
                owner="observability",
                stability=StabilityLevel.EXPERIMENTAL,
                version="0.1",
                methods={
                    "emit": "Record a TelemetryEvent.",
                    "record_metric": "Record a MetricPoint.",
                    "start_span": "Start a trace span.",
                    "finish_span": "Finish a trace span.",
                    "flush": "Drain all buffered telemetry.",
                },
                input_schema={
                    "event": "TelemetryEvent",
                    "point": "MetricPoint",
                    "span": "TraceSpan",
                },
                output_schema="dict (telemetry data on flush)",
            ),
            InterfaceDescriptor(
                name="HealthMonitor",
                module="smriti.observability.health",
                owner="observability",
                stability=StabilityLevel.STABLE,
                version="1.0",
                methods={
                    "register": "Register a health check.",
                    "run_all": "Execute all registered checks.",
                    "overall_status": "Aggregate health status.",
                    "health_report": "Return complete health report.",
                },
                input_schema={
                    "check": "HealthCheck",
                },
                output_schema="HealthReport (contains statuses and metrics)",
            ),
        ]
        for contract in defaults:
            self._contracts[contract.name] = contract

    def register(self, contract: InterfaceDescriptor) -> None:
        """Register a new contract (must not already exist)."""
        if contract.name in self._contracts:
            raise ValueError(f"Contract '{contract.name}' already registered.")
        self._contracts[contract.name] = contract

    def get(self, name: str) -> InterfaceDescriptor | None:
        """Retrieve a contract by name."""
        return self._contracts.get(name)

    def list_contracts(self) -> list[InterfaceDescriptor]:
        """Return all registered contracts."""
        return list(self._contracts.values())

    def stable_contracts(self) -> list[InterfaceDescriptor]:
        """Return only STABLE contracts."""
        return [c for c in self._contracts.values() if c.stability == StabilityLevel.STABLE]

    def deprecated_contracts(self) -> list[InterfaceDescriptor]:
        """Return only deprecated contracts."""
        return [c for c in self._contracts.values() if c.is_deprecated]


__all__ = [
    "InterfaceDescriptor",
    "ContractRegistry",
]
