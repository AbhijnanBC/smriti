"""
base.py — BaseWorkspace ABC with full lifecycle for Phase 10.

Every workspace:
    1. Declares its WorkspaceProfile (what it is)
    2. Coordinates a ViewCoordinator (which views compose it)
    3. Implements investigative objective logic
    4. Follows lifecycle: on_create → on_activate → on_suspend → on_resume → on_dispose

Rules:
    ✅ Workspaces coordinate — they do NOT render directly
    ✅ Views render themselves via ViewCoordinator
    ✅ Data flows Workspace → ViewCoordinator.refresh_all() → Views
    ❌ Workspace never calls st.* directly (except header + error fallback)
    ❌ Workspace never passes raw dicts to views
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import streamlit as st
from smriti.core.models import WorkspaceProfile, WorkspaceStatus
from smriti.dashboard.workspaces.context import WorkspaceContext
from smriti.dashboard.workspaces.view_coordinator import ViewCoordinator


class BaseWorkspace(ABC):
    """Abstract base for all Knowledge Workspaces."""

    def __init__(self) -> None:
        self._coordinator: ViewCoordinator = ViewCoordinator()
        self._status: WorkspaceStatus = WorkspaceStatus.CREATED
        self.on_create()

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def profile(self) -> WorkspaceProfile:
        """Workspace identity and cognitive characteristics."""
        ...

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_create(self) -> None:
        """Called once when workspace instance is created. Override to build views."""
        pass

    def on_activate(self, context: WorkspaceContext) -> None:
        """Called when workspace becomes the active workspace."""
        self._status = WorkspaceStatus.ACTIVE

    def on_suspend(self) -> None:
        """Called when workspace loses focus (another workspace activated)."""
        self._status = WorkspaceStatus.SUSPENDED

    def on_resume(self, context: WorkspaceContext) -> None:
        """Called when a suspended workspace regains focus."""
        self._status = WorkspaceStatus.ACTIVE

    def on_dispose(self) -> None:
        """Called when workspace is permanently removed."""
        self._coordinator.dispose_all()
        self._status = WorkspaceStatus.DISPOSED

    # ── Main entry point ──────────────────────────────────────────────────────

    def render(self, context: WorkspaceContext) -> None:
        """
        Main render method called by RenderCoordinator each cycle.
        Subclasses override _fetch_and_refresh() to load data and
        update views, then call self._coordinator.render_all(context).
        """
        self.header()
        try:
            self._fetch_and_refresh(context)
            self._coordinator.render_all(context)
        except Exception as exc:
            st.error(f"Workspace error: {exc}")
            context.notification_center.error(f"{self.profile.workspace_type.value} failed: {exc}")

    @abstractmethod
    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        """
        Fetch data from ServiceClient (via context.client),
        convert to PresentationModels, call coordinator.refresh_all().
        """
        ...

    def header(self) -> None:
        """Render workspace header (shared across all workspaces)."""
        st.markdown(f"### {self.profile.workspace_type.value.replace('_', ' ').title()} Workspace")
        st.caption(f"Objective: {self.profile.investigative_objective}")

    @property
    def status(self) -> WorkspaceStatus:
        return self._status

    @property
    def coordinator(self) -> ViewCoordinator:
        return self._coordinator
