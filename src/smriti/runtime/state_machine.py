"""
state_machine.py — Runtime State Machine (§11.3).

RECTIFIED (P0-2): State transitions now publish ArchitectureEvents to EventBus.

States:
    UNINITIALIZED → BOOTSTRAPPING → READY → ACTIVE
    ACTIVE → DEGRADED → RECOVERING → ACTIVE
    Any operational state → TERMINATING → TERMINATED
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, FrozenSet, List, Optional
import structlog

from smriti.exceptions import RuntimeException

logger = structlog.get_logger(__name__)


class RuntimeState(str, Enum):
    """Canonical runtime states of the SMRITI platform."""
    UNINITIALIZED = "UNINITIALIZED"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    READY         = "READY"
    ACTIVE        = "ACTIVE"
    DEGRADED      = "DEGRADED"
    RECOVERING    = "RECOVERING"
    TERMINATING   = "TERMINATING"
    TERMINATED    = "TERMINATED"


_PERMITTED_TRANSITIONS: Dict[RuntimeState, FrozenSet[RuntimeState]] = {
    RuntimeState.UNINITIALIZED: frozenset({RuntimeState.BOOTSTRAPPING}),
    RuntimeState.BOOTSTRAPPING: frozenset({RuntimeState.READY, RuntimeState.TERMINATED}),
    RuntimeState.READY:         frozenset({RuntimeState.ACTIVE, RuntimeState.TERMINATING}),
    RuntimeState.ACTIVE:        frozenset({RuntimeState.DEGRADED, RuntimeState.TERMINATING}),
    RuntimeState.DEGRADED:      frozenset({RuntimeState.RECOVERING, RuntimeState.TERMINATING}),
    RuntimeState.RECOVERING:    frozenset({RuntimeState.ACTIVE, RuntimeState.DEGRADED, RuntimeState.TERMINATING}),
    RuntimeState.TERMINATING:   frozenset({RuntimeState.TERMINATED}),
    RuntimeState.TERMINATED:    frozenset(),
}


@dataclass
class StateTransitionRecord:
    from_state:  RuntimeState
    to_state:    RuntimeState
    reason:      str
    timestamp:   float = field(default_factory=time.monotonic)


class RuntimeStateMachine:
    """Thread-safe finite state machine for runtime lifecycle transitions."""

    def __init__(self, run_id: str = "") -> None:
        self._state   = RuntimeState.UNINITIALIZED
        self._lock    = threading.Lock()
        self._history: List[StateTransitionRecord] = []
        self._observers: List[Callable[[RuntimeState, RuntimeState, str], None]] = []
        self._run_id  = run_id

    @property
    def state(self) -> RuntimeState:
        return self._state

    def transition(self, target: RuntimeState, reason: str = "") -> None:
        with self._lock:
            current = self._state
            permitted = _PERMITTED_TRANSITIONS.get(current, frozenset())
            if target not in permitted:
                raise RuntimeException(
                    f"Illegal state transition: {current.value} → {target.value}. "
                    f"Permitted: {[s.value for s in permitted]}"
                )
            self._state = target
            record = StateTransitionRecord(from_state=current, to_state=target, reason=reason)
            self._history.append(record)

        # Publish ArchitectureEvent (RECTIFIED P0-2)
        from smriti.runtime.events import publish, ArchitectureEventType
        publish(
            ArchitectureEventType.RUNTIME_ACTIVATED
            if target == RuntimeState.ACTIVE
            else ArchitectureEventType.SHUTDOWN_INITIATED
            if target == RuntimeState.TERMINATING
            else ArchitectureEventType.RECOVERY_STARTED
            if target == RuntimeState.RECOVERING
            else ArchitectureEventType.LIFECYCLE_STARTED,
            source="runtime.state_machine",
            run_id=self._run_id,
            from_state=current.value,
            to_state=target.value,
            reason=reason,
        )

        logger.info(
            "runtime_state_transition",
            from_state=current.value, to_state=target.value, reason=reason,
        )
        for observer in self._observers:
            try:
                observer(current, target, reason)
            except Exception as exc:
                logger.warning("state_observer_error", error=str(exc))

    def register_observer(self, callback: Callable[[RuntimeState, RuntimeState, str], None]) -> None:
        self._observers.append(callback)

    def is_operational(self) -> bool:
        return self._state in {RuntimeState.ACTIVE, RuntimeState.DEGRADED}

    def is_terminal(self) -> bool:
        return self._state == RuntimeState.TERMINATED

    @property
    def history(self) -> List[StateTransitionRecord]:
        return list(self._history)

    def current_state_entry_time(self) -> Optional[float]:
        if self._history:
            return self._history[-1].timestamp
        return None