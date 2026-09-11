"""
configuration.py — Configuration Architecture (§11.13).

Defines the hierarchical configuration system where lower levels
may override higher levels following declared inheritance rules.

Hierarchy (highest → lowest priority):
    Feature Flags    (runtime toggles)
        ↑ overrides
    Runtime          (operational knobs)
        ↑ overrides
    Workspace        (per-workspace settings)
        ↑ overrides
    Interaction      (dashboard behavior)
        ↑ overrides
    Knowledge API    (API behavior)
        ↑ overrides
    Pipeline         (phase parameters)
        ↑ overrides
    Global           (project-wide defaults)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConfigurationLevel(str, Enum):
    GLOBAL = "global"
    PIPELINE = "pipeline"
    KNOWLEDGE_API = "knowledge_api"
    INTERACTION = "interaction"
    WORKSPACE = "workspace"
    RUNTIME = "runtime"
    FEATURE_FLAGS = "feature_flags"


@dataclass(frozen=True)
class LevelDescriptor:
    """Formal description of one configuration hierarchy level."""

    level: ConfigurationLevel
    scope: str
    owner: str
    can_inherit: frozenset[ConfigurationLevel]
    mutable: bool  # False = frozen after initialization
    validation: str  # "strict" | "lenient" | "none"


LEVEL_DESCRIPTORS: dict[ConfigurationLevel, LevelDescriptor] = {
    ConfigurationLevel.GLOBAL: LevelDescriptor(
        level=ConfigurationLevel.GLOBAL,
        scope="Project-wide defaults applying to all phases and subsystems.",
        owner="smriti.core.config",
        can_inherit=frozenset(),
        mutable=False,
        validation="strict",
    ),
    ConfigurationLevel.PIPELINE: LevelDescriptor(
        level=ConfigurationLevel.PIPELINE,
        scope="Pipeline execution parameters (phase control, batch sizes).",
        owner="smriti.pipeline",
        can_inherit=frozenset({ConfigurationLevel.GLOBAL}),
        mutable=False,
        validation="strict",
    ),
    ConfigurationLevel.KNOWLEDGE_API: LevelDescriptor(
        level=ConfigurationLevel.KNOWLEDGE_API,
        scope="API behavior (budget, cache, projection levels).",
        owner="smriti.api",
        can_inherit=frozenset({ConfigurationLevel.PIPELINE, ConfigurationLevel.GLOBAL}),
        mutable=False,
        validation="strict",
    ),
    ConfigurationLevel.INTERACTION: LevelDescriptor(
        level=ConfigurationLevel.INTERACTION,
        scope="Dashboard interaction behavior (policies, workspace defaults).",
        owner="smriti.dashboard",
        can_inherit=frozenset({ConfigurationLevel.KNOWLEDGE_API}),
        mutable=False,
        validation="lenient",
    ),
    ConfigurationLevel.WORKSPACE: LevelDescriptor(
        level=ConfigurationLevel.WORKSPACE,
        scope="Per-workspace overrides for view and export behavior.",
        owner="smriti.dashboard.workspaces",
        can_inherit=frozenset({ConfigurationLevel.INTERACTION}),
        mutable=True,
        validation="lenient",
    ),
    ConfigurationLevel.RUNTIME: LevelDescriptor(
        level=ConfigurationLevel.RUNTIME,
        scope="Operational runtime parameters (health intervals, timeouts).",
        owner="smriti.runtime",
        can_inherit=frozenset({ConfigurationLevel.GLOBAL}),
        mutable=False,
        validation="strict",
    ),
    ConfigurationLevel.FEATURE_FLAGS: LevelDescriptor(
        level=ConfigurationLevel.FEATURE_FLAGS,
        scope="Toggleable feature enablement for incremental rollout.",
        owner="smriti.infrastructure",
        can_inherit=frozenset({ConfigurationLevel.RUNTIME}),
        mutable=True,
        validation="none",
    ),
}


class ConfigurationHierarchy:
    """
    Resolves configuration values through the hierarchy.

    Resolution order: highest-priority level first (Feature Flags → Global).
    """

    _PRIORITY = [
        ConfigurationLevel.FEATURE_FLAGS,
        ConfigurationLevel.WORKSPACE,
        ConfigurationLevel.RUNTIME,
        ConfigurationLevel.INTERACTION,
        ConfigurationLevel.KNOWLEDGE_API,
        ConfigurationLevel.PIPELINE,
        ConfigurationLevel.GLOBAL,
    ]

    def __init__(self) -> None:
        self._data: dict[ConfigurationLevel, dict[str, Any]] = {
            lvl: {} for lvl in ConfigurationLevel
        }

    def set(self, level: ConfigurationLevel, key: str, value: Any) -> None:
        descriptor = LEVEL_DESCRIPTORS[level]
        if not descriptor.mutable:
            raise TypeError(
                f"Configuration level '{level.value}' is immutable — "
                f"values cannot be set after initialization."
            )
        self._data[level][key] = value

    def load_immutable(self, level: ConfigurationLevel, data: dict[str, Any]) -> None:
        """Populate an immutable level (called once during initialization)."""
        descriptor = LEVEL_DESCRIPTORS[level]
        if descriptor.mutable:
            raise TypeError(f"Use set() for mutable level '{level.value}'.")
        self._data[level].update(data)

    def get(self, key: str, default: Any = None) -> Any:
        for level in self._PRIORITY:
            if key in self._data[level]:
                return self._data[level][key]
        return default

    def describe(self, level: ConfigurationLevel) -> LevelDescriptor:
        return LEVEL_DESCRIPTORS[level]
