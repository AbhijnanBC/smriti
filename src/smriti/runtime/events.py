"""
events.py — ArchitectureEvent model and EventBus (§11.1 rectified).

RECTIFIED (P0-2): Introduces a universal ArchitectureEvent model.

Before rectification, every subsystem logged independently:
    logger.info("runtime_state_transition", ...)   # runtime
    logger.info("lifecycle_phase_entered", ...)    # lifecycle
    logger.info("resource_allocated", ...)         # resources
    (no shared model → no cross-subsystem analysis possible)

After rectification:
    All subsystems publish ArchitectureEvents to EventBus.
    TelemetryCollector subscribes to EventBus (observer pattern).
    Telemetry never reaches into subsystems — it only observes events.

Events defined:
    LifecycleStarted          → lifecycle phase entered
    ConfigurationLoaded       → config frozen
    RuntimeActivated          → ACTIVE state entered
    DependencyValidated       → dependency graph verified
    RecoveryStarted           → RECOVERING state entered
    RecoveryFinished          → ACTIVE restored from RECOVERING
    ShutdownInitiated         → TERMINATING state entered
    ComplianceViolation       → a compliance rule failed
    InvariantViolation        → a system invariant was violated
    ManifestWritten           → RuntimeManifest artifact created
    CapabilityChanged         → a capability was enabled/disabled
    SchedulerTick             → periodic scheduler fired

Event Schema Versioning (NEW):
    Each ArchitectureEvent carries `event_schema_version` to allow
    downstream systems to parse event payloads across versions.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ArchitectureEventType(str, Enum):
    """All recognized Phase 11 architecture event types."""

    LIFECYCLE_STARTED = "LifecycleStarted"
    CONFIGURATION_LOADED = "ConfigurationLoaded"
    RUNTIME_ACTIVATED = "RuntimeActivated"
    DEPENDENCY_VALIDATED = "DependencyValidated"
    RECOVERY_STARTED = "RecoveryStarted"
    RECOVERY_FINISHED = "RecoveryFinished"
    SHUTDOWN_INITIATED = "ShutdownInitiated"
    COMPLIANCE_VIOLATION = "ComplianceViolation"
    INVARIANT_VIOLATION = "InvariantViolation"
    MANIFEST_WRITTEN = "ManifestWritten"
    CAPABILITY_CHANGED = "CapabilityChanged"
    SCHEDULER_TICK = "SchedulerTick"
    HEALTH_CHECK_COMPLETED = "HealthCheckCompleted"
    RESOURCE_ALLOCATED = "ResourceAllocated"
    RESOURCE_RELEASED = "ResourceReleased"
    SERVICE_REGISTERED = "ServiceRegistered"
    SERVICE_RETIRED = "ServiceRetired"


@dataclass(frozen=True)
class ArchitectureEvent:
    """
    RECTIFIED (P0-2): Universal architecture event with schema versioning.

    Every Phase 11 subsystem publishes these to EventBus.
    TelemetryCollector subscribes to EventBus and converts events to
    TelemetryEvents without any direct subsystem coupling.

    Fields:
        event_id:              Unique per-event UUID (8 chars)
        event_type:            Canonical event type
        source:                Module path that published this event
        run_id:                Which execution produced this event
        timestamp:             Monotonic seconds since process start
        event_schema_version:  Version of the event payload schema (e.g., "1.0")
        payload:               Event-specific context (type-safe but flexible)
    """

    event_id: str
    event_type: ArchitectureEventType
    source: str
    run_id: str
    timestamp: float
    event_schema_version: str = "1.0"  # NEW: schema version for consumers
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: ArchitectureEventType,
        source: str,
        run_id: str = "",
        event_schema_version: str = "1.0",
        **payload: Any,
    ) -> ArchitectureEvent:
        """
        Factory method for creating an ArchitectureEvent.

        Args:
            event_type: The type of event.
            source: Module path of the publisher.
            run_id: Execution identifier.
            event_schema_version: Override the schema version if needed.
            payload: Arbitrary event context.

        Returns:
            A new ArchitectureEvent instance.
        """
        return cls(
            event_id=str(uuid.uuid4())[:8],
            event_type=event_type,
            source=source,
            run_id=run_id,
            timestamp=time.monotonic(),
            event_schema_version=event_schema_version,  # NEW: version field set
            payload=dict(payload),
        )


EventSubscriber = Callable[[ArchitectureEvent], None]


class EventBus:
    """
    RECTIFIED (P0-2): Central publish-subscribe bus for ArchitectureEvents.

    Decouples:
        Publishers (runtime, lifecycle, resources, health) — they emit events
        Observers (telemetry, metrics, logger) — they subscribe and react

    Design:
        - Thread-safe publication and subscription
        - Subscribers are called outside the publish lock (no deadlock)
        - Subscriber exceptions are caught and logged (never propagate)
        - Silent drop if bus is disabled (observability must not affect behavior)
    """

    def __init__(self) -> None:
        self._subscribers: dict[ArchitectureEventType, list[EventSubscriber]] = {}
        self._wildcard_subscribers: list[EventSubscriber] = []
        self._lock = threading.Lock()
        self._enabled = True
        self._event_count = 0

    def subscribe(
        self,
        subscriber: EventSubscriber,
        event_type: ArchitectureEventType | None = None,
    ) -> None:
        """
        Subscribe to events.
        If event_type is None, subscriber receives all events (wildcard).
        """
        with self._lock:
            if event_type is None:
                self._wildcard_subscribers.append(subscriber)
            else:
                self._subscribers.setdefault(event_type, []).append(subscriber)

    def publish(self, event: ArchitectureEvent) -> None:
        """
        Publish an event to all matching subscribers.
        Never raises — subscriber failures are logged only.
        """
        if not self._enabled:
            return

        with self._lock:
            typed_subs = list(self._subscribers.get(event.event_type, []))
            wildcard_subs = list(self._wildcard_subscribers)
            self._event_count += 1

        # Call subscribers outside lock to prevent deadlock
        logger.debug(
            "architecture_event",
            event_type=event.event_type.value,
            source=event.source,
            run_id=event.run_id,
            event_schema_version=event.event_schema_version,
        )
        for sub in typed_subs + wildcard_subs:
            try:
                sub(event)
            except Exception as exc:
                logger.warning("event_subscriber_error", error=str(exc))

    def disable(self) -> None:
        """Disable the bus (events silently dropped — never raises)."""
        self._enabled = False

    @property
    def event_count(self) -> int:
        with self._lock:
            return self._event_count


# Process-level singleton EventBus
_event_bus: EventBus | None = None
_bus_lock = threading.Lock()


def get_event_bus() -> EventBus:
    """Return the process-level EventBus singleton."""
    global _event_bus
    if _event_bus is None:
        with _bus_lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus


def publish(
    event_type: ArchitectureEventType,
    source: str,
    run_id: str = "",
    event_schema_version: str = "1.0",
    **payload: Any,
) -> None:
    """
    Convenience function: create and publish an ArchitectureEvent.

    Args:
        event_type: Event type.
        source: Publisher module path.
        run_id: Execution identifier.
        event_schema_version: Override schema version if needed.
        payload: Arbitrary event data.
    """
    event = ArchitectureEvent.create(
        event_type=event_type,
        source=source,
        run_id=run_id,
        event_schema_version=event_schema_version,
        **payload,
    )
    get_event_bus().publish(event)
