"""
dependency_coordinator.py — DependencyCoordinator (§11.5 rectified).

RECTIFIED (P0-3): Owns dependency graph construction and validation.
"""

from __future__ import annotations

from smriti.runtime.composition import DependencyGraph, DependencyNode
from smriti.exceptions import RuntimeException
import structlog

logger = structlog.get_logger(__name__)


class DependencyCoordinator:
    """Owns dependency graph construction, validation, and resolution order."""

    def __init__(self) -> None:
        self._graph = DependencyGraph()

    def register(self, node: DependencyNode) -> None:
        self._graph.register(node)

    def validate(self) -> list:
        """Validate acyclicity. Returns resolved order or raises."""
        try:
            order = self._graph.resolve_order()
            logger.debug("dependency_graph_validated", order=order)
            return order
        except ValueError as exc:
            raise RuntimeException(f"Dependency graph invalid: {exc}") from exc

    def get(self, name: str) -> DependencyNode:
        return self._graph.get(name)

    def all_initialized(self) -> bool:
        return self._graph.all_initialized()

    @property
    def graph(self) -> DependencyGraph:
        return self._graph