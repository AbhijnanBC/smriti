"""
session.py — Streamlit session_state management for Phase 10.

The session is the transient container for all Phase 10 subsystems.
Initialization happens exactly once per browser session.
All subsystems are re-used within the session.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional

from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.dashboard.services.client import ServiceClient
from smriti.dashboard.events.event_bus import (
    InteractionEventBus,
    HistorySubscriber,
    WorkspaceSyncSubscriber,
    NotificationSubscriber,
)
from smriti.dashboard.notifications.notification_center import NotificationCenter

SESSION_KEY_INITIALIZED    = "smriti_initialized"
SESSION_KEY_STATE_MGR      = "smriti_state_manager"
SESSION_KEY_CLIENT         = "smriti_client"
SESSION_KEY_API            = "smriti_api"
SESSION_KEY_EVENT_BUS      = "smriti_event_bus"
SESSION_KEY_NOTIF_CENTER   = "smriti_notification_center"
SESSION_KEY_HISTORY_SUB    = "smriti_history_subscriber"
SESSION_KEY_SYNC_SUB       = "smriti_sync_subscriber"


def initialize_session(api) -> None:
    """
    Initialize the Streamlit session exactly once per browser session.
    Subsequent calls are no-ops.
    """
    if st.session_state.get(SESSION_KEY_INITIALIZED):
        return

    run_id = api.run_id

    # Build subsystems
    notification_center = NotificationCenter()
    event_bus = InteractionEventBus()
    history_sub = HistorySubscriber()
    sync_sub = WorkspaceSyncSubscriber()
    notif_sub = NotificationSubscriber(notification_center)

    event_bus.subscribe(history_sub)
    event_bus.subscribe(sync_sub)
    event_bus.subscribe(notif_sub)

    state_manager = EpistemicStateManager(run_id=run_id, event_bus=event_bus)
    client = ServiceClient(api=api)

    # Store in session_state
    st.session_state[SESSION_KEY_INITIALIZED]  = True
    st.session_state[SESSION_KEY_STATE_MGR]    = state_manager
    st.session_state[SESSION_KEY_CLIENT]       = client
    st.session_state[SESSION_KEY_API]          = api
    st.session_state[SESSION_KEY_EVENT_BUS]    = event_bus
    st.session_state[SESSION_KEY_NOTIF_CENTER] = notification_center
    st.session_state[SESSION_KEY_HISTORY_SUB]  = history_sub
    st.session_state[SESSION_KEY_SYNC_SUB]     = sync_sub


def get_state_manager() -> EpistemicStateManager:
    return st.session_state[SESSION_KEY_STATE_MGR]

def get_client() -> ServiceClient:
    return st.session_state[SESSION_KEY_CLIENT]

def get_api():
    return st.session_state[SESSION_KEY_API]

def get_event_bus() -> InteractionEventBus:
    return st.session_state[SESSION_KEY_EVENT_BUS]

def get_notification_center() -> NotificationCenter:
    return st.session_state[SESSION_KEY_NOTIF_CENTER]

def get_history_subscriber() -> HistorySubscriber:
    return st.session_state[SESSION_KEY_HISTORY_SUB]

def get_sync_subscriber() -> WorkspaceSyncSubscriber:
    return st.session_state[SESSION_KEY_SYNC_SUB]