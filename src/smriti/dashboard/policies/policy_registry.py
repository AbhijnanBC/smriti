"""
policy_registry.py — PolicyRegistry for Phase 10.

Policies are pluggable. Register named policy sets;
the active policy is selected by the interaction session.
Enables future per-workspace, per-user, or per-organization policies.
"""

from __future__ import annotations

from typing import Dict
from smriti.dashboard.policies.policies import InteractionPolicy, load_interaction_policy


class PolicyRegistry:
    """
    Registry of named InteractionPolicy instances.
    'default' is always present.
    """

    def __init__(self) -> None:
        self._policies: Dict[str, InteractionPolicy] = {
            "default": load_interaction_policy(),
        }
        self._active_name: str = "default"

    def register(self, name: str, policy: InteractionPolicy) -> None:
        """Register a named policy."""
        self._policies[name] = policy

    def activate(self, name: str) -> None:
        """Set the active policy by name."""
        if name not in self._policies:
            raise KeyError(f"Policy '{name}' not registered.")
        self._active_name = name

    @property
    def active(self) -> InteractionPolicy:
        return self._policies[self._active_name]

    @property
    def active_name(self) -> str:
        return self._active_name

    def all_names(self) -> list:
        return list(self._policies.keys())