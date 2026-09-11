"""
lifecycle_manager.py — LifecycleManager (§11.5 rectified).

RECTIFIED (P0-3): RuntimeCoordinator was becoming a God Object.
Split into focused sub-coordinators. RuntimeCoordinator only orchestrates.

LifecycleManager owns:
    - Phase advancement logic
    - Gate registration
    - Phase records
    - OperationalTimeline
"""

from __future__ import annotations

import structlog

from smriti.runtime.lifecycle import LifecycleGate, LifecyclePhase, RuntimeLifecycle

logger = structlog.get_logger(__name__)


class LifecycleManager:
    """Owns phase advancement and lifecycle gate evaluation."""

    def __init__(self, run_id: str = "") -> None:
        self._lifecycle = RuntimeLifecycle(run_id=run_id)

    def advance(self, phase: LifecyclePhase, notes: str = "") -> None:
        self._lifecycle.enter_phase(phase, notes)

    def complete(self, success: bool = True) -> None:
        self._lifecycle.complete_current_phase(success)

    def register_gate(self, gate: LifecycleGate) -> None:
        self._lifecycle.register_gate(gate)

    @property
    def current_phase(self) -> LifecyclePhase:
        return self._lifecycle.current_phase

    @property
    def history(self):
        return self._lifecycle.history

    @property
    def timeline(self):
        return self._lifecycle.timeline

    def has_reached(self, phase: LifecyclePhase) -> bool:
        return self._lifecycle.has_reached(phase)
