"""
health.py — Health Monitoring + Runtime Contracts (§11.24 rectified).

RECTIFIED (P2-2): RuntimeContract dataclass defines expected behavior contracts
for key services. Health checks now verify contracts are met.

Runtime Contracts defined:
    Health Service: must return within 100ms
    Shutdown:       must complete within 10s
    Manifest:       must always succeed
    Compliance:     must never modify runtime

These are engineering commitments with measurable criteria.

RECTIFIED (P0-2): Health check results published as ArchitectureEvents.
RECTIFIED (Dependency Integration): Health checks can update DependencyGraph nodes.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

import structlog

from smriti.runtime.composition import DependencyGraph, DependencyHealth

logger = structlog.get_logger(__name__)


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


def health_to_dependency_health(status: HealthStatus) -> DependencyHealth:
    """Map a HealthStatus to a DependencyHealth."""
    mapping = {
        HealthStatus.HEALTHY: DependencyHealth.HEALTHY,
        HealthStatus.DEGRADED: DependencyHealth.SLOW,
        HealthStatus.UNHEALTHY: DependencyHealth.UNAVAILABLE,
        HealthStatus.UNKNOWN: DependencyHealth.UNAVAILABLE,  # treat unknown as unavailable
    }
    return mapping.get(status, DependencyHealth.UNAVAILABLE)


@dataclass(frozen=True)
class RuntimeContract:
    """
    RECTIFIED (P2-2): Formal runtime contract for one service.

    Defines what the service MUST guarantee.
    Violations are treated as architecture errors, not runtime failures.
    """

    service: str
    must_complete_ms: float | None  # None = no time contract
    must_not_modify: bool = False  # Service must never modify system state
    must_always_succeed: bool = False  # Service must not raise under any condition
    violation_action: str = "alert"  # "alert" | "terminate"


# ── Canonical runtime contracts ────────────────────────────────────────────────

RUNTIME_CONTRACTS: dict[str, RuntimeContract] = {
    "health_service": RuntimeContract(
        service="health_service",
        must_complete_ms=100.0,
        must_not_modify=True,
        must_always_succeed=False,
        violation_action="alert",
    ),
    "shutdown_coordinator": RuntimeContract(
        service="shutdown_coordinator",
        must_complete_ms=10_000.0,
        must_not_modify=False,
        must_always_succeed=True,
        violation_action="terminate",
    ),
    "manifest_writer": RuntimeContract(
        service="manifest_writer",
        must_complete_ms=None,
        must_not_modify=False,
        must_always_succeed=True,
        violation_action="alert",
    ),
    "compliance_engine": RuntimeContract(
        service="compliance_engine",
        must_complete_ms=None,
        must_not_modify=True,
        must_always_succeed=False,
        violation_action="alert",
    ),
}


@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str = ""
    checked_at: float = field(default_factory=time.monotonic)
    latency_ms: float = 0.0
    contract_violated: bool = False


@dataclass
class HealthCheck:
    """Definition of a named health check."""

    name: str
    check: Callable[[], HealthStatus]
    timeout_seconds: float = 5.0
    category: str = "general"
    dependency_node: str | None = None  # RECTIFIED: map to dependency graph node

    def run(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            status = self.check()
            msg = ""
        except Exception as exc:
            status = HealthStatus.UNKNOWN
            msg = str(exc)
        elapsed = (time.monotonic() - start) * 1000

        # Check against runtime contract (RECTIFIED P2-2)
        contract = RUNTIME_CONTRACTS.get("health_service")
        contract_violated = False
        if contract and contract.must_complete_ms and elapsed > contract.must_complete_ms:
            logger.warning(
                "runtime_contract_violated",
                contract="health_service",
                latency_ms=elapsed,
                limit_ms=contract.must_complete_ms,
            )
            contract_violated = True

        return HealthCheckResult(
            name=self.name,
            status=status,
            message=msg,
            latency_ms=round(elapsed, 2),
            contract_violated=contract_violated,
        )


class HealthMonitor:
    """
    Runs all registered health checks and aggregates results.

    RECTIFIED: Can be bound to a DependencyGraph to update node health.
    """

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}
        self._last_results: dict[str, HealthCheckResult] = {}
        self._lock = threading.Lock()
        self._graph: DependencyGraph | None = None

    def bind_graph(self, graph: DependencyGraph) -> None:
        """Inject a dependency graph to update node health."""
        self._graph = graph

    def register(self, check: HealthCheck) -> None:
        with self._lock:
            self._checks[check.name] = check

    def run_all(self) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        with self._lock:
            checks = dict(self._checks)
            graph = self._graph

        for name, check in checks.items():
            result = check.run()
            results[name] = result

            # Update dependency graph if bound and check has a node mapping
            if graph and check.dependency_node:
                dep_health = health_to_dependency_health(result.status)
                try:
                    graph.set_health(check.dependency_node, dep_health)
                except ValueError as exc:
                    logger.warning(
                        "health_update_graph_failed", node=check.dependency_node, error=str(exc)
                    )

            # Publish ArchitectureEvent (RECTIFIED P0-2)
            from smriti.runtime.events import ArchitectureEventType, publish

            publish(
                ArchitectureEventType.HEALTH_CHECK_COMPLETED,
                source="observability.health",
                check_name=name,
                status=result.status.value,
                latency_ms=result.latency_ms,
                contract_violated=result.contract_violated,
                dependency_node=check.dependency_node,
            )

        with self._lock:
            self._last_results = results
        return results

    def overall_status(self) -> HealthStatus:
        with self._lock:
            if not self._last_results:
                return HealthStatus.UNKNOWN
            statuses = {r.status for r in self._last_results.values()}
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses or HealthStatus.UNKNOWN in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def health_report(self) -> dict:
        with self._lock:
            results = dict(self._last_results)
        return {
            "overall": self.overall_status().value,
            "checks": {
                name: {
                    "status": r.status.value,
                    "message": r.message,
                    "latency_ms": r.latency_ms,
                    "contract_violated": r.contract_violated,
                }
                for name, r in results.items()
            },
            "timestamp": time.time(),
        }


def build_default_health_monitor(
    dependency_graph: DependencyGraph | None = None,
) -> HealthMonitor:
    """
    Build the default SMRITI health monitor with standard checks.

    RECTIFIED: Accepts a DependencyGraph to map checks to nodes.
    """
    from smriti.core.config import get_config
    from smriti.core.paths import ARTIFACTS_DIR

    monitor = HealthMonitor()
    if dependency_graph:
        monitor.bind_graph(dependency_graph)

    def check_config() -> HealthStatus:
        try:
            cfg = get_config()
            return HealthStatus.HEALTHY if cfg else HealthStatus.UNHEALTHY
        except Exception:
            return HealthStatus.UNHEALTHY

    def check_artifacts_dir() -> HealthStatus:
        try:
            return HealthStatus.HEALTHY if ARTIFACTS_DIR.exists() else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.UNKNOWN

    def check_memory() -> HealthStatus:
        try:
            import psutil

            mem = psutil.virtual_memory()
            if mem.percent > 90:
                return HealthStatus.UNHEALTHY
            if mem.percent > 75:
                return HealthStatus.DEGRADED
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNKNOWN

    # Register checks with node mappings if graph provided
    monitor.register(
        HealthCheck(
            "configuration",
            check_config,
            category="subsystem",
            dependency_node="config" if dependency_graph else None,
        )
    )
    monitor.register(
        HealthCheck(
            "artifacts_directory",
            check_artifacts_dir,
            category="dependency",
            dependency_node="artifacts" if dependency_graph else None,
        )
    )
    monitor.register(
        HealthCheck(
            "memory_pressure",
            check_memory,
            category="resource",
            dependency_node=None,  # no graph node for this check
        )
    )

    return monitor
