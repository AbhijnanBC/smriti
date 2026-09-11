"""
notification_center.py — NotificationCenter for Phase 10.

Collects notifications generated during a render cycle and
renders them at the top of the Streamlit page.

Notification types:
    INFO    — Informational (green)
    WARNING — Policy limit reached (yellow)
    ERROR   — Retrieval or render failure (red)
    SUCCESS — Export complete, restore complete (green)

Rules:
    ✅ Notifications are transient (cleared after each render)
    ✅ Always rendered before workspace content
    ❌ Never used for business logic
    ❌ Never blocks rendering
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Notification:
    level: NotificationLevel
    message: str
    detail: dict[str, Any] = None


class NotificationCenter:
    """Collects and renders transient notifications. One instance per session."""

    def __init__(self) -> None:
        self._queue: list[Notification] = []

    def info(self, message: str, detail: dict[str, Any] = None) -> None:
        self._queue.append(Notification(NotificationLevel.INFO, message, detail))

    def warning(self, message: str, detail: dict[str, Any] = None) -> None:
        self._queue.append(Notification(NotificationLevel.WARNING, message, detail))

    def error(self, message: str, detail: dict[str, Any] = None) -> None:
        self._queue.append(Notification(NotificationLevel.ERROR, message, detail))

    def success(self, message: str, detail: dict[str, Any] = None) -> None:
        self._queue.append(Notification(NotificationLevel.SUCCESS, message, detail))

    def enqueue(self, event_type: str, payload: dict[str, Any]) -> None:
        """Route an event type to an appropriate notification message."""
        if event_type == "export_requested":
            fmt = payload.get("format", "json").upper()
            self.info(f"Export requested — preparing {fmt} download.")
        elif event_type == "workspace_restored":
            self.success("Workspace state restored from snapshot.")

    def render(self) -> None:
        """
        Render all queued notifications and clear the queue.
        Call this once per render cycle, before workspace content.
        """
        for notif in self._queue:
            if notif.level == NotificationLevel.INFO:
                st.info(notif.message)
            elif notif.level == NotificationLevel.WARNING:
                st.warning(notif.message)
            elif notif.level == NotificationLevel.ERROR:
                st.error(notif.message)
            elif notif.level == NotificationLevel.SUCCESS:
                st.success(notif.message)
        self._queue.clear()

    def has_errors(self) -> bool:
        return any(n.level == NotificationLevel.ERROR for n in self._queue)

    def clear(self) -> None:
        self._queue.clear()
