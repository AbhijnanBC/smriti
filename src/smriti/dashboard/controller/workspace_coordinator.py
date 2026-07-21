"""
workspace_coordinator.py — WorkspaceCoordinator for Phase 10.

Manages workspace lifecycle transitions.
When a workspace is activated, the previous one is suspended.
When a suspended workspace resumes, on_resume() is called.

This is distinct from the per-workspace ViewCoordinator:
    WorkspaceCoordinator  → manages WHICH workspace is active
    ViewCoordinator       → manages which VIEWS compose one workspace
"""

from __future__ import annotations

from typing import Optional
import structlog

from smriti.core.models import WorkspaceType
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext

logger = structlog.get_logger(__name__)


class WorkspaceCoordinator:
    """
    Tracks the active workspace and manages lifecycle transitions.
    One instance per session.
    """

    def __init__(self) -> None:
        self._active_workspace: Optional[BaseWorkspace] = None
        self._active_type: Optional[WorkspaceType] = None

    def transition(
        self,
        new_type: WorkspaceType,
        registry,
        context: WorkspaceContext,
    ) -> BaseWorkspace:
        """
        Transition to a new workspace type.
        Suspends the current one, activates the new one.
        """
        if self._active_workspace and self._active_type != new_type:
            try:
                self._active_workspace.on_suspend()
            except Exception as e:
                logger.warning("workspace suspend failed", error=str(e))

        workspace = registry.get(new_type)

        if self._active_type == new_type and self._active_workspace:
            # Resuming previously suspended workspace
            try:
                workspace.on_resume(context)
            except Exception as e:
                logger.warning("workspace resume failed", error=str(e))
        else:
            # Fresh activation
            try:
                workspace.on_activate(context)
            except Exception as e:
                logger.warning("workspace activate failed", error=str(e))

        self._active_workspace = workspace
        self._active_type = new_type
        return workspace

    def dispose_active(self) -> None:
        """Dispose the currently active workspace."""
        if self._active_workspace:
            try:
                self._active_workspace.on_dispose()
            except Exception as e:
                logger.warning("workspace dispose failed", error=str(e))
            self._active_workspace = None
            self._active_type = None