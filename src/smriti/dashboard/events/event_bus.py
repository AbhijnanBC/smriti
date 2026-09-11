"""
event_bus.py — InteractionEventBus for Phase 10.

Every state transition publishes an event.
Subscribers receive events and react (workspace sync, history, analytics).

Architecture:
    State Transition
        │
        ▼
    InteractionEvent (immutable)
        │
        ▼
    InteractionEventBus.publish()
        │
        ├── WorkspaceSynchronizerSubscriber
        ├── HistorySubscriber
        ├── NotificationSubscriber
        └── AnalyticsSubscriber

Rules:
    ✅ EventBus is the single publication channel
    ✅ Subscribers are registered at session bootstrap
    ✅ Subscriber failures are isolated (one failure does not halt others)
    ❌ EventBus never mutates EpistemicState directly
    ❌ Subscribers never call each other
"""

from __future__ import annotations

from typing import Protocol

import structlog
from smriti.core.models import InteractionEvent, InteractionEventType

logger = structlog.get_logger(__name__)


class EventSubscriber(Protocol):
    """Protocol for event bus subscribers."""

    def on_event(self, event: InteractionEvent) -> None:
        """Handle a published event. Must not raise — absorb internally."""
        ...

    @property
    def subscribed_types(self) -> list[InteractionEventType]:
        """Event types this subscriber wants. Empty = all events."""
        ...


class InteractionEventBus:
    """
    Publishes InteractionEvents to registered subscribers.
    One instance per session (stored in st.session_state).
    """

    def __init__(self) -> None:
        self._subscribers: list[EventSubscriber] = []
        self._event_log: list[InteractionEvent] = []

    def subscribe(self, subscriber: EventSubscriber) -> None:
        """Register a subscriber. Called once during session bootstrap."""
        self._subscribers.append(subscriber)

    def publish(self, event: InteractionEvent) -> None:
        """
        Publish an event to all relevant subscribers.
        Subscriber failures are caught and logged — never re-raised.
        """
        self._event_log.append(event)
        for subscriber in self._subscribers:
            # Check type filter
            sub_types = subscriber.subscribed_types
            if sub_types and event.event_type not in sub_types:
                continue
            try:
                subscriber.on_event(event)
            except Exception as exc:
                logger.warning(
                    "event subscriber failed",
                    subscriber=type(subscriber).__name__,
                    event_type=event.event_type.value,
                    error=str(exc),
                )

    @property
    def event_log(self) -> list[InteractionEvent]:
        """Read-only copy of all published events."""
        return list(self._event_log)

    def event_count(self, event_type: InteractionEventType = None) -> int:
        """Count events, optionally filtered by type."""
        if event_type is None:
            return len(self._event_log)
        return sum(1 for e in self._event_log if e.event_type == event_type)


# ── Built-in Subscribers ──────────────────────────────────────────────────────


class HistorySubscriber:
    """Logs every event for session analytics (read-only history)."""

    def __init__(self) -> None:
        self._history: list[InteractionEvent] = []

    @property
    def subscribed_types(self) -> list[InteractionEventType]:
        return []  # All events

    def on_event(self, event: InteractionEvent) -> None:
        self._history.append(event)

    @property
    def history(self) -> list[InteractionEvent]:
        return list(self._history)


class WorkspaceSyncSubscriber:
    """
    Notifies the WorkspaceSynchronizer when workspace-affecting events arrive.
    Stores pending sync flags consumed by the RenderCoordinator.
    """

    WORKSPACE_EVENTS = {
        InteractionEventType.WORKSPACE_ACTIVATED,
        InteractionEventType.WORKSPACE_CLOSED,
        InteractionEventType.WORKSPACE_SUSPENDED,
        InteractionEventType.WORKSPACE_RESUMED,
        InteractionEventType.CLAIM_SELECTED,
        InteractionEventType.FILTER_APPLIED,
        InteractionEventType.SEARCH_SUBMITTED,
    }

    def __init__(self) -> None:
        self._pending_sync = False

    @property
    def subscribed_types(self) -> list[InteractionEventType]:
        return list(self.WORKSPACE_EVENTS)

    def on_event(self, event: InteractionEvent) -> None:
        self._pending_sync = True
        logger.debug("workspace sync flagged", event_type=event.event_type.value)

    def consume_sync_flag(self) -> bool:
        """Returns True and clears flag if sync is pending."""
        if self._pending_sync:
            self._pending_sync = False
            return True
        return False


class NotificationSubscriber:
    """Routes events to the NotificationCenter."""

    NOTIFICATION_EVENTS = {
        InteractionEventType.EXPORT_REQUESTED,
        InteractionEventType.WORKSPACE_RESTORED,
        InteractionEventType.COMMAND_DISPATCHED,
    }

    def __init__(self, notification_center) -> None:
        self._nc = notification_center

    @property
    def subscribed_types(self) -> list[InteractionEventType]:
        return list(self.NOTIFICATION_EVENTS)

    def on_event(self, event: InteractionEvent) -> None:
        self._nc.enqueue(event.event_type.value, event.payload)


class StreamlitLifecycleSubscriber:
    """
    Makes the EventBus a first-class orchestrator.
    Listens for UI-altering events and triggers the Streamlit rerun.
    Views NO LONGER call st.rerun().
    """

    @property
    def subscribed_types(self) -> list[InteractionEventType]:
        # Subscribe to all events, or selectively filter WORKSPACE_EVENTS
        # We subscribe to everything except NOTIFICATION_SENT to avoid excessive reruns.
        return []  # All events

    def on_event(self, event: InteractionEvent) -> None:
        # Note: In Streamlit, calling st.rerun() immediately halts execution.
        # Ensure this subscriber is registered LAST in the session bootstrap.
        import streamlit as st

        # Only rerun if it's a state-mutating event (skip notifications)
        if event.event_type != InteractionEventType.NOTIFICATION_SENT:
            st.rerun()
