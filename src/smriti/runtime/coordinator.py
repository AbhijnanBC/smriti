"""
coordinator.py — RuntimeCoordinator (§11.5 rectified).

RECTIFIED (P0-3): RuntimeCoordinator now orchestrates sub-coordinators
instead of managing everything itself. It delegates to:
    LifecycleManager       — phase advancement
    DependencyCoordinator  — dependency graph
    HealthCoordinator      — health checks
    ShutdownCoordinator    — shutdown handlers
    ExecutionCoordinator   — request/error counts

RuntimeCoordinator responsibilities (after split):
    1. Wire sub-coordinators together
    2. Execute startup sequence (calls sub-coordinators in order)
    3. Expose unified introspection properties
    4. Handle emergency shutdown

RECTIFIED (P0-1): Accepts OperationalContext for richer initialization.
RECTIFIED (P0-4): Integrates CapabilityModel.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

import structlog

from smriti.governance import stable
from smriti.runtime.capabilities import CapabilityModel
from smriti.runtime.composition import ConfigurationContext, DependencyGraph, RuntimeContext
from smriti.runtime.dependency_coordinator import DependencyCoordinator
from smriti.runtime.execution_coordinator import ExecutionCoordinator
from smriti.runtime.health_coordinator import HealthCoordinator
from smriti.runtime.invariants import assert_runtime_invariants
from smriti.runtime.lifecycle import LifecyclePhase
from smriti.runtime.lifecycle_manager import LifecycleManager
from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine

logger = structlog.get_logger(__name__)


class ShutdownCoordinator:
    """Manages ordered, graceful shutdown of all registered services."""

    def __init__(self) -> None:
        self._handlers = []

    def register(self, name: str, handler: Callable[[], None], priority: int = 50) -> None:
        self._handlers.append((priority, name, handler))

    def execute(self) -> None:
        ordered = sorted(self._handlers, key=lambda t: t[0])
        for priority, name, handler in ordered:
            try:
                logger.info("shutdown_handler_executing", name=name, priority=priority)
                handler()
            except Exception as exc:
                logger.error("shutdown_handler_failed", name=name, error=str(exc))


@stable("1.0")
class RuntimeCoordinator:
    """
    Central orchestrator — orchestrates sub-coordinators, never manages directly.

    RECTIFIED (P0-3): No longer owns lifecycle/health/dependency/execution logic.
    Each sub-coordinator is injected at construction or created with defaults.
    """

    def __init__(self) -> None:
        self._state_machine = RuntimeStateMachine()
        self._lifecycle_mgr = LifecycleManager()
        self._dep_coordinator = DependencyCoordinator()
        self._health_coordinator = HealthCoordinator()
        self._exec_coordinator = ExecutionCoordinator()
        self._shutdown = ShutdownCoordinator()
        self._capabilities = CapabilityModel()
        self._config_ctx: ConfigurationContext | None = None
        self._lock = threading.Lock()
        self._run_id: str = ""

    # ── Lifecycle API ─────────────────────────────────────────────────────────

    def start(self, run_id: str) -> None:
        """Execute the complete startup sequence via sub-coordinators."""
        self._run_id = run_id
        self._state_machine._run_id = run_id
        self._lifecycle_mgr._lifecycle._run_id = run_id
        logger.info("runtime_coordinator_start", run_id=run_id)

        self._state_machine.transition(RuntimeState.BOOTSTRAPPING, "startup initiated")
        self._lifecycle_mgr.advance(LifecyclePhase.BOOTSTRAP, "coordinator.start()")

        try:
            self._phase_load_configuration()
            self._phase_construct_dependencies()
            self._phase_initialize_infrastructure(run_id)
        except Exception as exc:
            logger.error("startup_failed", error=str(exc))
            self._emergency_shutdown()
            raise

        self._state_machine.transition(RuntimeState.READY, "all dependencies ready")
        self._lifecycle_mgr.advance(LifecyclePhase.RUNTIME_READY)
        self._lifecycle_mgr.complete()

        self._state_machine.transition(RuntimeState.ACTIVE, "runtime activated")
        self._lifecycle_mgr.advance(LifecyclePhase.OPERATIONAL_EXECUTION)

        assert_runtime_invariants(self)
        logger.info("runtime_coordinator_active", run_id=run_id)

    def stop(self, reason: str = "normal_shutdown") -> None:
        logger.info("runtime_coordinator_stopping", reason=reason)
        self._state_machine.transition(RuntimeState.TERMINATING, reason)
        self._lifecycle_mgr.complete()
        self._lifecycle_mgr.advance(LifecyclePhase.GRACEFUL_SHUTDOWN)
        self._shutdown.execute()
        self._lifecycle_mgr.complete()
        self._lifecycle_mgr.advance(LifecyclePhase.PERSISTENT_CLEANUP)
        self._lifecycle_mgr.complete()
        self._state_machine.transition(RuntimeState.TERMINATED, "shutdown complete")
        logger.info("runtime_coordinator_terminated")

    def mark_degraded(self, reason: str) -> None:
        if self._state_machine.state == RuntimeState.ACTIVE:
            self._state_machine.transition(RuntimeState.DEGRADED, reason)
            logger.warning("runtime_degraded", reason=reason)

    def attempt_recovery(self) -> bool:
        if self._state_machine.state != RuntimeState.DEGRADED:
            return False
        self._state_machine.transition(RuntimeState.RECOVERING, "recovery attempt")
        try:
            all_healthy = self._health_coordinator.all_healthy()
            if all_healthy:
                self._state_machine.transition(RuntimeState.ACTIVE, "recovery successful")
                logger.info("runtime_recovered")
                return True
            else:
                self._state_machine.transition(RuntimeState.DEGRADED, "recovery failed")
                return False
        except Exception as exc:
            self._state_machine.transition(RuntimeState.DEGRADED, f"recovery error: {exc}")
            return False

    # ── Health ────────────────────────────────────────────────────────────────

    def register_health_check(self, name: str, check: Callable[[], bool]) -> None:
        self._health_coordinator.register(name, check)

    def health_status(self) -> dict[str, Any]:
        return {
            "runtime_state": self._state_machine.state.value,
            "lifecycle_phase": self._lifecycle_mgr.current_phase.value,
            "is_operational": self._state_machine.is_operational(),
            "checks": self._health_coordinator.run_all(),
            "capabilities": self._capabilities.snapshot(),
            "uptime_seconds": self._exec_coordinator.uptime_seconds(),
        }

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def state(self) -> RuntimeState:
        return self._state_machine.state

    @property
    def config_context(self) -> ConfigurationContext | None:
        return self._config_ctx

    @property
    def runtime_context(self) -> RuntimeContext | None:
        if self._run_id:
            return RuntimeContext(
                run_id=self._run_id,
                request_count=self._exec_coordinator.request_count,
                error_count=self._exec_coordinator.error_count,
            )
        return None

    @property
    def dependency_graph(self) -> DependencyGraph:
        return self._dep_coordinator.graph

    @property
    def capabilities(self) -> CapabilityModel:
        return self._capabilities

    @property
    def lifecycle_manager(self) -> LifecycleManager:
        return self._lifecycle_mgr

    # ── Internal startup phases ───────────────────────────────────────────────

    def _phase_load_configuration(self) -> None:
        self._lifecycle_mgr.advance(LifecyclePhase.CONFIGURATION_LOADING)
        import hashlib
        import json

        from smriti.core.config import get_config

        cfg = get_config()
        raw = {k: cfg.get(k) for k in ["pipeline", "extraction", "embedding", "runtime"]}
        cfg_hash = hashlib.sha256(
            json.dumps(raw, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        self._config_ctx = ConfigurationContext(
            env=cfg.env,
            config_hash=cfg_hash,
            loaded_at=time.monotonic(),
            raw=raw,
        )
        self._lifecycle_mgr.complete()

        # Publish ArchitectureEvent (RECTIFIED P0-2)
        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.CONFIGURATION_LOADED,
            source="runtime.coordinator",
            run_id=self._run_id,
            env=cfg.env,
            config_hash=cfg_hash,
        )
        logger.info("configuration_loaded", env=cfg.env, hash=cfg_hash)

    def _phase_construct_dependencies(self) -> None:
        self._lifecycle_mgr.advance(LifecyclePhase.DEPENDENCY_CONSTRUCTION)
        order = self._dep_coordinator.validate()

        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.DEPENDENCY_VALIDATED,
            source="runtime.coordinator",
            run_id=self._run_id,
            resolved_order=order,
        )
        self._lifecycle_mgr.complete()

    def _phase_initialize_infrastructure(self, run_id: str) -> None:
        self._lifecycle_mgr.advance(LifecyclePhase.INFRASTRUCTURE_INITIALIZATION)
        self._lifecycle_mgr.complete()

    def _emergency_shutdown(self) -> None:
        try:
            self._state_machine.transition(RuntimeState.TERMINATING, "emergency shutdown")
            self._shutdown.execute()
            self._state_machine.transition(RuntimeState.TERMINATED, "emergency shutdown complete")
        except Exception:
            pass
