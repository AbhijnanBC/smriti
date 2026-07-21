"""
context.py — WorkspaceContext for Phase 10.

WorkspaceContext bundles all workspace dependencies into one clean injection.
Workspaces receive one context object, not 5-6 separate arguments.

Avoids the anti-pattern of:
    workspace.render(state_manager, client, policy_engine, nav_engine, logger)

Instead:
    workspace.render(context)

RECTIFIED: Decomposed WorkspaceContext into three explicit domains to prevent
"God Object" bloat. Each domain groups related concerns:

    InteractionContext   → user intent, session bounds, policy
    RenderingContext     → UI feedback, visual state, notifications
    InfrastructureContext → data access, logging, system services

WorkspaceContext composes them and provides convenience properties for
backward compatibility during refactoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.dashboard.services.client import ServiceClient
from smriti.dashboard.policies.policies import PolicyEngine
from smriti.dashboard.notifications.notification_center import NotificationCenter


@dataclass(frozen=True)
class InteractionContext:
    """
    Handles the user's intent and session bounds.
    Contains state manager and policy engine.
    """
    state_manager: EpistemicStateManager
    policy_engine: PolicyEngine


@dataclass(frozen=True)
class RenderingContext:
    """
    Handles UI feedback and visual state.
    Contains notification center.
    """
    notification_center: NotificationCenter


@dataclass(frozen=True)
class InfrastructureContext:
    """
    Handles data access and system logging.
    Contains service client and logger.
    """
    client: ServiceClient
    logger: Any  # structlog logger instance


@dataclass(frozen=True)
class WorkspaceContext:
    """
    Composed dependency bundle for workspace rendering.
    Divided into explicit domains to prevent "God Object" bloat.
    """
    interaction: InteractionContext
    rendering: RenderingContext
    infrastructure: InfrastructureContext

    # ── Convenience properties for backward compatibility ──────────────────────
    @property
    def state_manager(self) -> EpistemicStateManager:
        return self.interaction.state_manager

    @property
    def state(self):
        return self.interaction.state_manager.state

    @property
    def client(self) -> ServiceClient:
        return self.infrastructure.client

    @property
    def policy_engine(self) -> PolicyEngine:
        return self.interaction.policy_engine

    @property
    def notification_center(self) -> NotificationCenter:
        return self.rendering.notification_center

    @property
    def logger(self):
        return self.infrastructure.logger