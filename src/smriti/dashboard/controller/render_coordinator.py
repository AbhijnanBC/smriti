"""
render_coordinator.py — RenderCoordinator for Phase 10.

Owns the workspace rendering decision each Streamlit cycle.

Responsibilities:
    ✅ Build WorkspaceContext from session subsystems
    ✅ Retrieve the active workspace from WorkspaceRegistry
    ✅ Validate graph policy before rendering
    ✅ Call workspace.render(context)
    ✅ Surface errors through NotificationCenter
    ❌ Never renders workspace content itself
    ❌ Never calls ServiceClient directly
"""

from __future__ import annotations

import streamlit as st
import structlog

from smriti.dashboard.workspaces.context import (
    WorkspaceContext,
    InteractionContext,
    RenderingContext,
    InfrastructureContext,
)
from smriti.exceptions import WorkspaceNotFoundError

logger = structlog.get_logger(__name__)


class RenderCoordinator:
    """Coordinates the per-cycle workspace render."""

    def render(
        self,
        registry,
        state_manager,
        client,
        policy_engine,
        notification_center,
    ) -> None:
        """
        Build context and render the active workspace.
        All errors are surfaced to the user via st.error, never silently swallowed.
        """
        state = state_manager.state

        # Policy: validate graph size before any render
        node_count = client.node_count
        allowed, reason = policy_engine.validate_graph_size(node_count)
        if not allowed:
            notification_center.warning(f"Policy limit: {reason}")

        # Render notifications first
        notification_center.render()

        # Build the three sub-contexts (RECTIFIED for WorkspaceContext)
        interaction = InteractionContext(
            state_manager=state_manager,
            policy_engine=policy_engine,
        )
        rendering = RenderingContext(
            notification_center=notification_center,
        )
        infrastructure = InfrastructureContext(
            client=client,
            logger=logger,
        )

        context = WorkspaceContext(
            interaction=interaction,
            rendering=rendering,
            infrastructure=infrastructure,
        )

        # Get and render workspace
        try:
            workspace = registry.get(state.workspace_type)
            workspace.render(context)
        except WorkspaceNotFoundError as e:
            st.error(f"Workspace not registered: {e}")
        except Exception as e:
            st.error(f"Workspace rendering error: {e}")
            st.exception(e)