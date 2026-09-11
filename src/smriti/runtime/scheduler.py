"""
scheduler.py — RuntimeScheduler (§11.5 rectified).

RECTIFIED (P1-2): Phase 11 assumed synchronous orchestration exclusively.
RuntimeScheduler enables periodic background operations:
    - Periodic health checks
    - Telemetry flush
    - Cache cleanup signals
    - Compliance scan
    - Quality evaluation
    - Manifest rotation

Design:
    - Simple threading.Timer loop (not a full job scheduler)
    - All scheduled tasks are observational (never modify domain knowledge)
    - Tasks publish ArchitectureEvents on completion
    - Scheduler stops cleanly on shutdown
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ScheduledTask:
    """Definition of one periodic task."""

    name: str
    interval_seconds: float
    task: Callable[[], None]
    last_run: float | None = None
    run_count: int = 0


class RuntimeScheduler:
    """
    RECTIFIED (P1-2): Periodic task scheduler for Phase 11 background operations.

    Usage:
        scheduler = RuntimeScheduler()
        scheduler.register("health_check", interval=30.0, task=run_health_check)
        scheduler.register("telemetry_flush", interval=60.0, task=flush_telemetry)
        scheduler.start()
        # ... runtime runs ...
        scheduler.stop()
    """

    def __init__(self, tick_interval: float = 1.0) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._tick_interval = tick_interval
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        interval_seconds: float,
        task: Callable[[], object],
    ) -> None:
        """
        Register a periodic task.

        RECTIFIED (publication-readiness audit): `task` was typed
        `Callable[[], None]`, but the scheduler discards whatever a task
        returns (see `_run_loop`) and at least one real caller
        (`pipeline/runner.py`'s health-check registration) passes a task
        that returns `dict[str, bool]`, which mypy correctly flagged as
        an incompatible-type error against the old, too-strict signature.
        Widened to `Callable[[], object]` to match actual behavior
        instead of narrowing the caller.
        """
        with self._lock:
            self._tasks[name] = ScheduledTask(
                name=name,
                interval_seconds=interval_seconds,
                task=task,
            )
        logger.debug("scheduler_task_registered", name=name, interval=interval_seconds)

    def start(self) -> None:
        """Start the scheduler background thread."""
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="smriti-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info("runtime_scheduler_started")

    def stop(self) -> None:
        """Stop the scheduler cleanly."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("runtime_scheduler_stopped")

    def _run_loop(self) -> None:
        from smriti.runtime.events import ArchitectureEventType, publish

        while self._running:
            now = time.monotonic()
            with self._lock:
                tasks = dict(self._tasks)

            for name, task_def in tasks.items():
                if (
                    task_def.last_run is None
                    or now - task_def.last_run >= task_def.interval_seconds
                ):
                    try:
                        task_def.task()
                        task_def.last_run = now
                        task_def.run_count += 1
                        publish(
                            ArchitectureEventType.SCHEDULER_TICK,
                            source="runtime.scheduler",
                            task_name=name,
                            run_count=task_def.run_count,
                        )
                    except Exception as exc:
                        logger.warning("scheduler_task_failed", name=name, error=str(exc))

            time.sleep(self._tick_interval)

    @property
    def registered_tasks(self) -> list:
        with self._lock:
            return list(self._tasks.keys())
