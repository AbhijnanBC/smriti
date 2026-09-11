"""
policy_hierarchy.py — Policy Hierarchy (§11.13 rectified).

RECTIFIED (P1-4): PolicyHierarchy mirrors ConfigurationHierarchy.
Just as configuration has a hierarchy (Global → Feature Flags),
policies should too.

Policy Hierarchy (highest → lowest priority):
    Feature Policy     (feature-specific toggles)
    Workspace Policy   (per-workspace overrides)
    Interaction Policy (dashboard defaults)
    Runtime Policy     (operational constraints)
    Global Policy      (project-wide defaults)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PolicyLevel(str, Enum):
    GLOBAL = "global"
    RUNTIME = "runtime"
    INTERACTION = "interaction"
    WORKSPACE = "workspace"
    FEATURE = "feature"


@dataclass(frozen=True)
class PolicyDescriptor:
    """Formal description of one policy hierarchy level."""

    level: PolicyLevel
    scope: str
    owner: str
    overridable: bool  # Can lower-level policies override this?
    validation: str


POLICY_LEVEL_DESCRIPTORS: dict[PolicyLevel, PolicyDescriptor] = {
    PolicyLevel.GLOBAL: PolicyDescriptor(
        level=PolicyLevel.GLOBAL,
        scope="Project-wide defaults for all interactions and runtime.",
        owner="governance",
        overridable=True,
        validation="strict",
    ),
    PolicyLevel.RUNTIME: PolicyDescriptor(
        level=PolicyLevel.RUNTIME,
        scope="Runtime operational policies (timeouts, resource limits).",
        owner="infrastructure",
        overridable=True,
        validation="strict",
    ),
    PolicyLevel.INTERACTION: PolicyDescriptor(
        level=PolicyLevel.INTERACTION,
        scope="Dashboard interaction policies (search behavior, export limits).",
        owner="dashboard",
        overridable=True,
        validation="lenient",
    ),
    PolicyLevel.WORKSPACE: PolicyDescriptor(
        level=PolicyLevel.WORKSPACE,
        scope="Per-workspace policy overrides.",
        owner="dashboard.workspaces",
        overridable=True,
        validation="lenient",
    ),
    PolicyLevel.FEATURE: PolicyDescriptor(
        level=PolicyLevel.FEATURE,
        scope="Feature-specific policy toggles.",
        owner="features",
        overridable=False,
        validation="none",
    ),
}


class PolicyHierarchy:
    """
    RECTIFIED (P1-4): Resolves policy values through a formal hierarchy.

    Resolution order: FEATURE (highest) → GLOBAL (lowest).
    """

    _PRIORITY = [
        PolicyLevel.FEATURE,
        PolicyLevel.WORKSPACE,
        PolicyLevel.INTERACTION,
        PolicyLevel.RUNTIME,
        PolicyLevel.GLOBAL,
    ]

    def __init__(self) -> None:
        self._data: dict[PolicyLevel, dict[str, Any]] = {level: {} for level in PolicyLevel}

    def set(self, level: PolicyLevel, key: str, value: Any) -> None:
        self._data[level][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        for level in self._PRIORITY:
            if key in self._data[level]:
                return self._data[level][key]
        return default

    def effective_policy(self) -> dict[str, Any]:
        """Return merged policy (higher levels take precedence)."""
        result: dict[str, Any] = {}
        for level in reversed(self._PRIORITY):
            result.update(self._data[level])
        return result
