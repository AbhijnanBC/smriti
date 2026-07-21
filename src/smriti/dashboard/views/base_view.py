"""
base_view.py — BaseView ABC for Phase 10.

Every view component implements this contract:
    render()   — produce Streamlit output
    refresh()  — called by ViewCoordinator when state changes
    supports() — declares if this view can handle current state
    dispose()  — cleanup when view is removed from composition

Rules:
    ✅ Views receive PresentationModels — never raw dicts
    ✅ Views never call ServiceClient directly
    ✅ Views never call state transitions directly (raise Command instead)
    ❌ Views never import from services/ or workspaces/
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseView(ABC):
    """Abstract base for all Phase 10 views."""

    @abstractmethod
    def render(self) -> None:
        """Produce Streamlit output from current model data."""
        ...

    def refresh(self, **kwargs: Any) -> None:
        """
        Called by ViewCoordinator when upstream state changes.
        Update internal model data. Default is no-op.
        """
        pass

    def supports(self, context: Any) -> bool:
        """
        Return True if this view can be meaningfully rendered
        in the given WorkspaceContext. Default: always True.
        """
        return True

    def dispose(self) -> None:
        """
        Release any resources held by this view.
        Called when view is removed from composition. Default: no-op.
        """
        pass

    @property
    def view_name(self) -> str:
        """Unique name for this view type (used by ViewRegistry)."""
        return type(self).__name__