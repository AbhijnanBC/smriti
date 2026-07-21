"""
telemetry.py — Telemetry Architecture (§11.25 rectified).

RECTIFIED (P0-2): TelemetryCollector now subscribes to EventBus.
Instead of subsystems calling telemetry.emit() directly,
telemetry observes ArchitectureEvents from EventBus.

This means:
    - Telemetry never reaches INTO subsystems
    - Adding telemetry for a new event = subscribe to that event type
    - Removing telemetry has zero impact on subsystem code
    - Observability is truly passive
"""

from __future__ import annotations
from smriti.governance import experimental

import time
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class EventSeverity(str, Enum):
    DEBUG    = "debug"
    INFO     = "info"
    WARNING  = "warning"
    ERROR    = "error"
    CRITICAL = "critical"


@dataclass
class TelemetryEvent:
    """Discrete operational event with structured context."""
    event_id:   str
    event_type: str
    severity:   EventSeverity
    source:     str
    timestamp:  float
    context:    Dict[str, Any] = field(default_factory=dict)
    run_id:     str = ""

    @classmethod
    def create(cls, event_type: str, severity: EventSeverity, source: str,
               run_id: str = "", **context: Any) -> "TelemetryEvent":
        return cls(
            event_id=str(uuid.uuid4())[:8],
            event_type=event_type, severity=severity,
            source=source, timestamp=time.time(),
            context=context, run_id=run_id,
        )

    @classmethod
    def from_architecture_event(cls, arch_event) -> "TelemetryEvent":
        """RECTIFIED (P0-2): Convert ArchitectureEvent → TelemetryEvent."""
        return cls(
            event_id=arch_event.event_id,
            event_type=arch_event.event_type.value,
            severity=EventSeverity.INFO,
            source=arch_event.source,
            timestamp=time.time(),
            context=dict(arch_event.payload),
            run_id=arch_event.run_id,
        )


@dataclass
class MetricPoint:
    metric_name: str
    value:       float
    unit:        str
    timestamp:   float = field(default_factory=time.time)
    labels:      Dict[str, str] = field(default_factory=dict)


@dataclass
class TraceSpan:
    trace_id:   str
    span_id:    str
    parent_id:  Optional[str]
    operation:  str
    started_at: float
    ended_at:   Optional[float] = None

    @property
    def duration_ms(self) -> Optional[float]:
        if self.ended_at:
            return (self.ended_at - self.started_at) * 1000
        return None

    def finish(self) -> None:
        self.ended_at = time.monotonic()

@experimental("0.1")
class TelemetryCollector:
    """
    RECTIFIED (P0-2): Collects telemetry by subscribing to EventBus.

    Also supports direct emit() for backward compatibility.
    """

    MAX_BUFFER = 10_000

    def __init__(self, run_id: str = "") -> None:
        self._run_id  = run_id
        self._events: List[TelemetryEvent] = []
        self._metrics: List[MetricPoint]   = []
        self._spans:   List[TraceSpan]     = []
        self._lock    = threading.Lock()

    def subscribe_to_event_bus(self) -> None:
        """
        RECTIFIED (P0-2): Subscribe to EventBus to passively observe all events.
        Call this once after construction to wire up passive telemetry.
        """
        from smriti.runtime.events import get_event_bus
        get_event_bus().subscribe(self._on_architecture_event)
        logger.debug("telemetry_subscribed_to_event_bus", run_id=self._run_id)

    def _on_architecture_event(self, arch_event) -> None:
        """Callback: convert ArchitectureEvent → TelemetryEvent and buffer."""
        t_event = TelemetryEvent.from_architecture_event(arch_event)
        with self._lock:
            if len(self._events) < self.MAX_BUFFER:
                self._events.append(t_event)

    def emit(self, event: TelemetryEvent) -> None:
        """Backward-compatible direct emit."""
        with self._lock:
            if len(self._events) < self.MAX_BUFFER:
                self._events.append(event)

    def record_metric(self, point: MetricPoint) -> None:
        with self._lock:
            if len(self._metrics) < self.MAX_BUFFER:
                self._metrics.append(point)

    def start_span(self, operation: str, trace_id: Optional[str] = None) -> TraceSpan:
        return TraceSpan(
            trace_id=trace_id or str(uuid.uuid4())[:8],
            span_id=str(uuid.uuid4())[:8],
            parent_id=None,
            operation=operation,
            started_at=time.monotonic(),
        )

    def finish_span(self, span: TraceSpan) -> None:
        span.finish()
        with self._lock:
            if len(self._spans) < self.MAX_BUFFER:
                self._spans.append(span)

    def flush(self) -> Dict[str, List]:
        with self._lock:
            data = {
                "events":  list(self._events),
                "metrics": list(self._metrics),
                "spans":   list(self._spans),
            }
            self._events.clear()
            self._metrics.clear()
            self._spans.clear()
        return data

    def event_count(self) -> int:
        with self._lock:
            return len(self._events)