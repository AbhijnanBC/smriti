"""
lifecycle.py — Runtime Lifecycle Model (§11.2) + OperationalTimeline (NEW P2-5).

RECTIFIED (P0-2): Lifecycle phase entries now publish ArchitectureEvents.
RECTIFIED (P2-5): OperationalTimeline records Bootstrap→Configuration→Activation→
                  Recovery→Shutdown for diagnostics.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

import structlog

from smriti.exceptions import RuntimeException

logger = structlog.get_logger(__name__)


class LifecyclePhase(str, Enum):
    SYSTEM_INSTALLATION = "SYSTEM_INSTALLATION"
    BOOTSTRAP = "BOOTSTRAP"
    CONFIGURATION_LOADING = "CONFIGURATION_LOADING"
    DEPENDENCY_CONSTRUCTION = "DEPENDENCY_CONSTRUCTION"
    INFRASTRUCTURE_INITIALIZATION = "INFRASTRUCTURE_INITIALIZATION"
    RUNTIME_READY = "RUNTIME_READY"
    OPERATIONAL_EXECUTION = "OPERATIONAL_EXECUTION"
    GRACEFUL_SHUTDOWN = "GRACEFUL_SHUTDOWN"
    PERSISTENT_CLEANUP = "PERSISTENT_CLEANUP"


_PHASE_ORDER: list[LifecyclePhase] = [
    LifecyclePhase.SYSTEM_INSTALLATION,
    LifecyclePhase.BOOTSTRAP,
    LifecyclePhase.CONFIGURATION_LOADING,
    LifecyclePhase.DEPENDENCY_CONSTRUCTION,
    LifecyclePhase.INFRASTRUCTURE_INITIALIZATION,
    LifecyclePhase.RUNTIME_READY,
    LifecyclePhase.OPERATIONAL_EXECUTION,
    LifecyclePhase.GRACEFUL_SHUTDOWN,
    LifecyclePhase.PERSISTENT_CLEANUP,
]

_PHASE_INDEX: dict[LifecyclePhase, int] = {p: i for i, p in enumerate(_PHASE_ORDER)}


@dataclass
class LifecycleGate:
    phase: LifecyclePhase
    description: str
    check: Callable[[], bool]

    def evaluate(self) -> bool:
        try:
            return self.check()
        except Exception:
            return False


@dataclass
class LifecycleRecord:
    phase: LifecyclePhase
    entered_at: float = field(default_factory=time.monotonic)
    exited_at: float | None = None
    success: bool = True
    notes: str = ""

    @property
    def duration_seconds(self) -> float | None:
        if self.exited_at is not None:
            return self.exited_at - self.entered_at
        return None


# ── OperationalTimeline (NEW P2-5) ────────────────────────────────────────────


class TimelineStage(str, Enum):
    """High-level stages for the operational timeline."""

    BOOTSTRAP = "bootstrap"
    CONFIGURATION = "configuration"
    ACTIVATION = "activation"
    RECOVERY = "recovery"
    SHUTDOWN = "shutdown"


@dataclass
class TimelineEntry:
    """One entry in the operational timeline."""

    stage: TimelineStage
    entered_at: float = field(default_factory=time.monotonic)
    exited_at: float | None = None
    notes: str = ""

    @property
    def duration_ms(self) -> float | None:
        if self.exited_at is not None:
            return (self.exited_at - self.entered_at) * 1000
        return None


class OperationalTimeline:
    """
    RECTIFIED (P2-5): Records the high-level operational stages of one runtime execution.

    Stages: Bootstrap → Configuration → Activation → (Recovery*) → Shutdown
    Useful for diagnostics, latency analysis, and Phase 12 evaluation.
    """

    def __init__(self) -> None:
        self._entries: list[TimelineEntry] = []
        self._current: TimelineEntry | None = None

    def enter(self, stage: TimelineStage, notes: str = "") -> None:
        """Record entry into a timeline stage."""
        if self._current is not None:
            self._current.exited_at = time.monotonic()
            self._entries.append(self._current)
        self._current = TimelineEntry(stage=stage, notes=notes)
        logger.debug("timeline_stage_entered", stage=stage.value, notes=notes)

    def exit_current(self) -> None:
        if self._current is not None:
            self._current.exited_at = time.monotonic()
            self._entries.append(self._current)
            self._current = None

    def to_dict(self) -> list:
        return [
            {
                "stage": e.stage.value,
                "entered_at": e.entered_at,
                "duration_ms": e.duration_ms,
                "notes": e.notes,
            }
            for e in self._entries
        ]

    @property
    def all_entries(self) -> list[TimelineEntry]:
        return list(self._entries)


class RuntimeLifecycle:
    """Governs the complete lifecycle of the SMRITI operational runtime."""

    def __init__(self, run_id: str = "") -> None:
        self._current: LifecyclePhase = LifecyclePhase.SYSTEM_INSTALLATION
        self._records: list[LifecycleRecord] = []
        self._gates: dict[LifecyclePhase, list[LifecycleGate]] = {}
        self._active_record: LifecycleRecord | None = None
        self._run_id = run_id
        self.timeline = OperationalTimeline()

    def enter_phase(self, phase: LifecyclePhase, notes: str = "") -> None:
        expected_idx = _PHASE_INDEX[self._current] + 1
        requested_idx = _PHASE_INDEX[phase]
        if requested_idx != expected_idx:
            raise RuntimeException(
                f"Lifecycle phase ordering violated: currently in "
                f"{self._current.value}, cannot advance to {phase.value} "
                f"(expected {_PHASE_ORDER[expected_idx].value})"
            )
        for gate in self._gates.get(phase, []):
            if not gate.evaluate():
                raise RuntimeException(
                    f"Lifecycle gate failed for phase {phase.value}: {gate.description}"
                )
        if self._active_record is not None:
            self._active_record.exited_at = time.monotonic()
            self._records.append(self._active_record)
        record = LifecycleRecord(phase=phase, notes=notes)
        self._active_record = record
        self._current = phase

        # Update operational timeline (RECTIFIED P2-5)
        stage_map = {
            LifecyclePhase.BOOTSTRAP: TimelineStage.BOOTSTRAP,
            LifecyclePhase.CONFIGURATION_LOADING: TimelineStage.CONFIGURATION,
            LifecyclePhase.DEPENDENCY_CONSTRUCTION: TimelineStage.CONFIGURATION,
            LifecyclePhase.INFRASTRUCTURE_INITIALIZATION: TimelineStage.ACTIVATION,
            LifecyclePhase.RUNTIME_READY: TimelineStage.ACTIVATION,
            LifecyclePhase.OPERATIONAL_EXECUTION: TimelineStage.ACTIVATION,
            LifecyclePhase.GRACEFUL_SHUTDOWN: TimelineStage.SHUTDOWN,
            LifecyclePhase.PERSISTENT_CLEANUP: TimelineStage.SHUTDOWN,
        }
        if phase in stage_map:
            self.timeline.enter(stage_map[phase], notes=notes)

        # Publish ArchitectureEvent (RECTIFIED P0-2)
        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.LIFECYCLE_STARTED,
            source="runtime.lifecycle",
            run_id=self._run_id,
            phase=phase.value,
            notes=notes,
        )

        logger.info("lifecycle_phase_entered", phase=phase.value, notes=notes)

    def complete_current_phase(self, success: bool = True) -> None:
        if self._active_record is not None:
            self._active_record.exited_at = time.monotonic()
            self._active_record.success = success
            self._records.append(self._active_record)
            self._active_record = None
            logger.info("lifecycle_phase_complete", phase=self._current.value, success=success)

    def register_gate(self, gate: LifecycleGate) -> None:
        self._gates.setdefault(gate.phase, []).append(gate)

    @property
    def current_phase(self) -> LifecyclePhase:
        return self._current

    @property
    def history(self) -> list[LifecycleRecord]:
        return list(self._records)

    def is_past(self, phase: LifecyclePhase) -> bool:
        return _PHASE_INDEX[self._current] > _PHASE_INDEX[phase]

    def has_reached(self, phase: LifecyclePhase) -> bool:
        return _PHASE_INDEX[self._current] >= _PHASE_INDEX[phase]
