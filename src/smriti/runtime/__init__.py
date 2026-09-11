"""
runtime/__init__.py — Public API for Phase 11 Part 1.

RECTIFIED: Exports OperationalContext, ArchitectureEvent, EventBus,
CapabilityModel, RuntimeScheduler, sub-coordinators.
"""

from smriti.runtime.capabilities import Capability, CapabilityModel
from smriti.runtime.context import OperationalContext, QualityContext, TelemetryContext
from smriti.runtime.coordinator import RuntimeCoordinator
from smriti.runtime.events import (
    ArchitectureEvent,
    ArchitectureEventType,
    EventBus,
    get_event_bus,
    publish,
)
from smriti.runtime.invariants import assert_runtime_invariants
from smriti.runtime.lifecycle import LifecyclePhase, OperationalTimeline, RuntimeLifecycle
from smriti.runtime.scheduler import RuntimeScheduler
from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine

_coordinator: "RuntimeCoordinator | None" = None


def get_runtime() -> "RuntimeCoordinator":
    global _coordinator
    if _coordinator is None:
        _coordinator = RuntimeCoordinator()
    return _coordinator


__all__ = [
    "RuntimeState",
    "RuntimeStateMachine",
    "RuntimeCoordinator",
    "RuntimeLifecycle",
    "LifecyclePhase",
    "OperationalTimeline",
    "assert_runtime_invariants",
    "get_runtime",
    "OperationalContext",
    "TelemetryContext",
    "QualityContext",
    "ArchitectureEvent",
    "ArchitectureEventType",
    "EventBus",
    "get_event_bus",
    "publish",
    "CapabilityModel",
    "Capability",
    "RuntimeScheduler",
]
