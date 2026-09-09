"""Unit tests for dashboard/events/event_bus.py."""

import pytest
import time
from smriti.core.models import InteractionEvent, InteractionEventType
from smriti.dashboard.events.event_bus import (
    InteractionEventBus,
    HistorySubscriber,
    WorkspaceSyncSubscriber,
)


def make_event(event_type: InteractionEventType) -> InteractionEvent:
    return InteractionEvent(
        event_type=event_type,
        payload={"test": True},
        timestamp_ms=time.monotonic() * 1000,
        session_id="test_session",
    )


def test_event_bus_publishes_to_subscribers():
    bus = InteractionEventBus()
    history = HistorySubscriber()
    bus.subscribe(history)

    bus.publish(make_event(InteractionEventType.CLAIM_SELECTED))
    assert len(history.history) == 1


def test_event_bus_logs_all_events():
    bus = InteractionEventBus()
    bus.publish(make_event(InteractionEventType.CLAIM_SELECTED))
    bus.publish(make_event(InteractionEventType.FILTER_APPLIED))
    assert bus.event_count() == 2


def test_event_bus_isolates_subscriber_failures():
    """A failing subscriber must not prevent others from receiving the event."""
    class BrokenSubscriber:
        @property
        def subscribed_types(self): return []
        def on_event(self, event): raise RuntimeError("intentional failure")

    bus = InteractionEventBus()
    history = HistorySubscriber()
    bus.subscribe(BrokenSubscriber())
    bus.subscribe(history)

    # Should not raise
    bus.publish(make_event(InteractionEventType.CLAIM_SELECTED))
    assert len(history.history) == 1


def test_workspace_sync_subscriber_flags_on_matching_event():
    sync = WorkspaceSyncSubscriber()
    event = make_event(InteractionEventType.CLAIM_SELECTED)
    sync.on_event(event)
    assert sync.consume_sync_flag() is True


def test_workspace_sync_subscriber_clears_after_consume():
    sync = WorkspaceSyncSubscriber()
    sync.on_event(make_event(InteractionEventType.CLAIM_SELECTED))
    sync.consume_sync_flag()
    assert sync.consume_sync_flag() is False


def test_history_subscriber_receives_all_events():
    bus = InteractionEventBus()
    history = HistorySubscriber()
    bus.subscribe(history)

    for et in [InteractionEventType.CLAIM_SELECTED,
               InteractionEventType.WORKSPACE_ACTIVATED,
               InteractionEventType.FILTER_APPLIED]:
        bus.publish(make_event(et))

    assert len(history.history) == 3


def test_event_bus_type_filter():
    """WorkspaceSyncSubscriber only responds to workspace-affecting events."""
    # EXPLAINABILITY_CHANGED is NOT in WORKSPACE_EVENTS. Calling on_event()
    # directly bypasses the bus's type filter (on_event unconditionally sets
    # the pending flag) — so this must go through the bus itself, with a
    # fresh subscriber, to actually exercise InteractionEventBus.publish()'s
    # filtering logic (sub_types check) rather than pre-polluting the flag.
    sync = WorkspaceSyncSubscriber()
    bus = InteractionEventBus()
    bus.subscribe(sync)
    bus.publish(make_event(InteractionEventType.EXPLAINABILITY_CHANGED))
    assert sync.consume_sync_flag() is False