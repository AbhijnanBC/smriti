"""
composition.py — Runtime Composition Architecture (§11.4).

RECTIFIED: Added dynamic health tracking for dependency nodes.
Allows HealthCoordinator and CapabilityModel to reflect runtime health
of subsystems (e.g., FAISS, embedding models) and propagate status.

DependencyHealth states:
    INITIALIZING → during bootstrap
    HEALTHY      → fully operational
    SLOW         → degraded performance but usable
    UNAVAILABLE  → failed, dependent features must degrade
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class DependencyHealth(str, Enum):
    """Health status of a dependency node."""
    INITIALIZING = "initializing"
    HEALTHY      = "healthy"
    SLOW         = "slow"
    UNAVAILABLE  = "unavailable"


@dataclass(frozen=True)
class ConfigurationContext:
    """Immutable runtime configuration snapshot (frozen after CONFIGURATION_LOADING)."""
    env:         str
    config_hash: str
    loaded_at:   float
    raw:         Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)


@dataclass
class RuntimeContext:
    """Mutable operational context for the current execution."""
    run_id:        str
    started_at:    float = field(default_factory=time.monotonic)
    request_count: int   = 0
    error_count:   int   = 0
    warning_count: int   = 0

    def increment_requests(self) -> None:
        self.request_count += 1

    def increment_errors(self) -> None:
        self.error_count += 1

    def uptime_seconds(self) -> float:
        return time.monotonic() - self.started_at


@dataclass
class DependencyNode:
    """
    A single node in the dependency graph.

    RECTIFIED: Added `health` field to track runtime health.
    """
    name:        str
    instance:    Any
    depends_on:  tuple = field(default_factory=tuple)
    initialized: bool = False
    owner:       str  = ""
    health:      DependencyHealth = DependencyHealth.INITIALIZING


class DependencyGraph:
    """
    Acyclic dependency graph for runtime component management.

    RECTIFIED: Added `set_health()` to update node health.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, DependencyNode] = {}

    def register(self, node: DependencyNode) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Duplicate dependency node: {node.name}")
        self._nodes[node.name] = node

    def resolve_order(self) -> list:
        visited: set = set()
        order: list = []

        def visit(name: str, stack: set) -> None:
            if name in stack:
                raise ValueError(f"Dependency cycle detected at: {name}")
            if name in visited:
                return
            stack.add(name)
            node = self._nodes.get(name)
            if node:
                for dep in node.depends_on:
                    visit(dep, stack)
            stack.discard(name)
            visited.add(name)
            order.append(name)

        for name in self._nodes:
            visit(name, set())
        return order

    def get(self, name: str) -> Optional[DependencyNode]:
        return self._nodes.get(name)

    def all_initialized(self) -> bool:
        return all(n.initialized for n in self._nodes.values())

    # ── RECTIFIED: Health tracking ──────────────────────────────────────────

    def set_health(self, name: str, health: DependencyHealth) -> None:
        """
        Update the health status of a dependency node.
        If the node does not exist, raises ValueError.

        The HealthCoordinator should call this when a subsystem health
        check changes.
        """
        node = self._nodes.get(name)
        if node is None:
            raise ValueError(f"Unknown dependency node: {name}")
        node.health = health
        # Optionally, propagate health changes to dependents here.
        # For now, we let the CapabilityModel poll or subscribe to events.

    def get_health(self, name: str) -> Optional[DependencyHealth]:
        """Return the health status of a node, or None if node not found."""
        node = self._nodes.get(name)
        return node.health if node else None

    def get_dependents(self, name: str) -> list[str]:
        """
        Return a list of nodes that directly depend on the given node.
        Used for propagation logic (e.g., if FAISS becomes UNAVAILABLE,
        all dependents should degrade).
        """
        result = []
        for node in self._nodes.values():
            if name in node.depends_on:
                result.append(node.name)
        return result