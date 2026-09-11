"""
context.py — OperationalContext (§11.1 rectified).

RECTIFIED (P0-1): Introduces OperationalContext as the single immutable
object representing "this execution." All Phase 11 components receive
OperationalContext instead of six independent objects.

Before rectification, Phase 11 passed around:
    RuntimeContext, ConfigurationContext, DependencyGraph,
    RuntimeManifest, ResourceGovernor, TelemetryCollector
    (six separate objects → coupling, argument count inflation)

After rectification:
    OperationalContext (one immutable record)
    → coordinator.start() receives run_id
    → everything else reads from ctx

Immutability contract:
    OperationalContext is frozen after construction.
    Sub-objects that are mutable (RuntimeContext, ResourceGovernor)
    are accessed via properties that return their current state snapshots.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TelemetryContext:
    """Telemetry configuration for this execution."""

    run_id: str
    max_buffer: int = 10_000
    enabled: bool = True


@dataclass(frozen=True)
class QualityContext:
    """Quality objective thresholds for this execution."""

    startup_target_seconds: float = 5.0
    query_p95_target_ms: float = 200.0
    memory_ceiling_mb: float = 512.0
    recovery_target_seconds: float = 10.0


@dataclass(frozen=True)
class OperationalContext:
    """
    RECTIFIED (P0-1): Single immutable object representing one SMRITI execution.

    Every Phase 11 component receives this context.
    Eliminates the need to pass six separate objects through the call stack.

    Design decisions:
        - Frozen dataclass: immutable after construction
        - Sub-objects: captured at construction time (snapshots)
        - Mutable sub-components (ResourceGovernor): referenced by identity;
          their internal state is mutable but the reference is frozen
        - start_timestamp: monotonic (not wall clock) for duration calculation

    Usage:
        ctx = OperationalContext.create(run_id="20250101_120000", ...)
        coordinator.start_with_context(ctx)
        scheduler.bind(ctx)
        health_coordinator.bind(ctx)
    """

    run_id: str
    start_timestamp: float
    telemetry_ctx: TelemetryContext
    quality_ctx: QualityContext
    # Mutable sub-components: referenced, not copied
    _resource_governor: Any = field(compare=False, hash=False, repr=False)
    _config_raw: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    config_hash: str = ""
    env: str = "development"
    architecture_version: str = "11.0"

    @classmethod
    def create(
        cls,
        run_id: str,
        resource_governor=None,
        config_raw: dict[str, Any] = None,
        config_hash: str = "",
        env: str = "development",
        telemetry_max_buffer: int = 10_000,
        quality_startup_target: float = 5.0,
        quality_query_p95_ms: float = 200.0,
        quality_memory_mb: float = 512.0,
    ) -> OperationalContext:
        """Factory method: the canonical way to build an OperationalContext."""
        from smriti.infrastructure.resources import ResourceGovernor

        gov = resource_governor or ResourceGovernor()
        return cls(
            run_id=run_id,
            start_timestamp=time.monotonic(),
            telemetry_ctx=TelemetryContext(
                run_id=run_id,
                max_buffer=telemetry_max_buffer,
            ),
            quality_ctx=QualityContext(
                startup_target_seconds=quality_startup_target,
                query_p95_target_ms=quality_query_p95_ms,
                memory_ceiling_mb=quality_memory_mb,
            ),
            _resource_governor=gov,
            _config_raw=config_raw or {},
            config_hash=config_hash,
            env=env,
        )

    @property
    def resource_governor(self):
        return self._resource_governor

    @property
    def uptime_seconds(self) -> float:
        return time.monotonic() - self.start_timestamp

    def config_get(self, key: str, default: Any = None) -> Any:
        return self._config_raw.get(key, default)
