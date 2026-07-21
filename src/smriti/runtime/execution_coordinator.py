"""
execution_coordinator.py — ExecutionCoordinator (§11.5 rectified).

RECTIFIED (P0-3): Owns request count, error count, uptime tracking.
"""

from __future__ import annotations

import threading
import time


class ExecutionCoordinator:
    """Tracks execution-level metrics (requests, errors, uptime)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._request_count = 0
        self._error_count = 0
        self._warning_count = 0
        self._started_at = time.monotonic()

    def increment_requests(self) -> None:
        with self._lock:
            self._request_count += 1

    def increment_errors(self) -> None:
        with self._lock:
            self._error_count += 1

    def increment_warnings(self) -> None:
        with self._lock:
            self._warning_count += 1

    @property
    def request_count(self) -> int:
        with self._lock:
            return self._request_count

    @property
    def error_count(self) -> int:
        with self._lock:
            return self._error_count

    def uptime_seconds(self) -> float:
        return time.monotonic() - self._started_at

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "request_count": self._request_count,
                "error_count":   self._error_count,
                "warning_count": self._warning_count,
                "uptime_seconds": self.uptime_seconds(),
            }