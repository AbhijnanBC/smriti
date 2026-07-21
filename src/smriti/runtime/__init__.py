"""
runtime/__init__.py — Public API for Phase 11 Part 1.

RECTIFIED: Exports OperationalContext, ArchitectureEvent, EventBus,
CapabilityModel, RuntimeScheduler, sub-coordinators.
"""

from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine
from smriti.runtime.coordinator import RuntimeCoordinator
from smriti.runtime.lifecycle import RuntimeLifecycle, LifecyclePhase, OperationalTimeline
from smriti.runtime.invariants import assert_runtime_invariants
from smriti.runtime.context import OperationalContext, TelemetryContext, QualityContext
from smriti.runtime.events import ArchitectureEvent, ArchitectureEventType, EventBus, get_event_bus, publish
from smriti.runtime.capabilities import CapabilityModel, Capability
from smriti.runtime.scheduler import RuntimeScheduler

_coordinator: "RuntimeCoordinator | None" = None


def get_runtime() -> "RuntimeCoordinator":
    global _coordinator
    if _coordinator is None:
        _coordinator = RuntimeCoordinator()
    return _coordinator


__all__ = [
    "RuntimeState", "RuntimeStateMachine",
    "RuntimeCoordinator",
    "RuntimeLifecycle", "LifecyclePhase", "OperationalTimeline",
    "assert_runtime_invariants",
    "get_runtime",
    "OperationalContext", "TelemetryContext", "QualityContext",
    "ArchitectureEvent", "ArchitectureEventType", "EventBus", "get_event_bus", "publish",
    "CapabilityModel", "Capability",
    "RuntimeScheduler",
]