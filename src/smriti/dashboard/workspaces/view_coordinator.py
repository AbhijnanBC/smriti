"""
view_coordinator.py — ViewCoordinator for Phase 10.

The ViewCoordinator sits between every workspace and its views.
It owns:
    - View lifecycle (creation, refresh, dispose)
    - Synchronization (when state changes, which views refresh)
    - Dependency ordering (views refreshed in correct order)
    - Visibility rules (which views render given current state)

This keeps workspaces focused on investigative objectives.
Orchestration logic lives here, not in each workspace.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import structlog

from smriti.dashboard.views.base_view import BaseView
from smriti.dashboard.workspaces.context import WorkspaceContext

logger = structlog.get_logger(__name__)


class ViewCoordinator:
    """
    Manages the lifecycle and synchronization of views within a workspace.

    Usage:
        coordinator = ViewCoordinator()
        coordinator.register("search",    search_view)
        coordinator.register("result_list", result_list_view)
        coordinator.register("inspector", inspector_view)
        coordinator.render_all(context)
    """

    def __init__(self) -> None:
        self._views: Dict[str, BaseView] = {}
        self._render_order: List[str] = []

    def register(self, name: str, view: BaseView, position: int = None) -> None:
        """Register a view. Position controls render order."""
        self._views[name] = view
        if name not in self._render_order:
            if position is not None:
                self._render_order.insert(position, name)
            else:
                self._render_order.append(name)

    def refresh_all(self, **kwargs) -> None:
        """
        Propagate state updates to all registered views.
        Each view's refresh() is called with matching kwargs.
        """
        for name in self._render_order:
            view = self._views.get(name)
            if view is None:
                continue
            try:
                view.refresh(**kwargs)
            except TypeError:
                # View doesn't accept these kwargs — skip gracefully
                view.refresh()
            except Exception as exc:
                logger.warning("view refresh failed", view=name, error=str(exc))

    def render_all(self, context: WorkspaceContext) -> None:
        """
        Render all views that support the current context, in order.
        Failures in one view do not prevent others from rendering.
        """
        for name in self._render_order:
            view = self._views.get(name)
            if view is None:
                continue
            if not view.supports(context):
                continue
            try:
                view.render()
            except Exception as exc:
                logger.error("view render failed", view=name, error=str(exc))
                import streamlit as st
                st.error(f"View '{name}' failed to render: {exc}")

    def render_named(self, name: str, context: WorkspaceContext) -> None:
        """Render one named view."""
        view = self._views.get(name)
        if view and view.supports(context):
            try:
                view.render()
            except Exception as exc:
                logger.error("view render failed", view=name, error=str(exc))

    def dispose_all(self) -> None:
        """Dispose all registered views (call on workspace de-activation)."""
        for view in self._views.values():
            try:
                view.dispose()
            except Exception as exc:
                logger.warning("view dispose failed", error=str(exc))
        self._views.clear()
        self._render_order.clear()

    def get(self, name: str) -> Optional[BaseView]:
        return self._views.get(name)