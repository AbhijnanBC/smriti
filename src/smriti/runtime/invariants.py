"""invariants.py — Operational Invariants (§11.6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from smriti.exceptions import Phase11InvariantViolation

if TYPE_CHECKING:
    from smriti.runtime.coordinator import RuntimeCoordinator

logger = structlog.get_logger(__name__)


def assert_runtime_invariants(coordinator: RuntimeCoordinator) -> None:
    _assert_configuration_frozen(coordinator)
    _assert_dependency_graph_acyclic(coordinator)
    _assert_runtime_context_present(coordinator)


def _assert_configuration_frozen(coordinator: RuntimeCoordinator) -> None:
    if coordinator.config_context is None:
        raise Phase11InvariantViolation(
            "Invariant 6 violated: ConfigurationContext must be set after startup."
        )
    logger.debug("invariant_6_passed", config_hash=coordinator.config_context.config_hash)


def _assert_dependency_graph_acyclic(coordinator: RuntimeCoordinator) -> None:
    try:
        coordinator.dependency_graph.resolve_order()
    except ValueError as exc:
        raise Phase11InvariantViolation(f"Dependency graph cycle detected: {exc}") from exc
    logger.debug("invariant_acyclic_passed")


def _assert_runtime_context_present(coordinator: RuntimeCoordinator) -> None:
    from smriti.runtime.state_machine import RuntimeState

    if coordinator.state in {RuntimeState.ACTIVE, RuntimeState.DEGRADED}:
        if coordinator.runtime_context is None:
            raise Phase11InvariantViolation(
                f"Invariant 5 violated: RuntimeContext must be present when state is "
                f"{coordinator.state.value}."
            )
    logger.debug("invariant_5_passed")
