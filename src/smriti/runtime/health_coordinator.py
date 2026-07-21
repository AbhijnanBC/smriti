"""
health_coordinator.py — HealthCoordinator (§11.5 rectified).

RECTIFIED: Now accepts a DependencyGraph and updates node health
based on health check results.
"""

from __future__ import annotations

from typing import Callable, Dict, Any, Optional
import structlog

from smriti.runtime.composition import DependencyGraph, DependencyHealth

logger = structlog.get_logger(__name__)


class HealthCoordinator:
    """
    Owns health check registration and execution.

    RECTIFIED: Wired to DependencyGraph to reflect subsystem health.
    """

    def __init__(self, dependency_graph: Optional[DependencyGraph] = None) -> None:
        self._checks: Dict[str, Callable[[], bool]] = {}
        # Map check name -> dependency node name (if applicable)
        self._check_to_node: Dict[str, str] = {}
        self._graph = dependency_graph

    def register(
        self,
        name: str,
        check: Callable[[], bool],
        dependency_node: Optional[str] = None,
    ) -> None:
        """
        Register a health check.

        Args:
            name: Unique check name.
            check: Callable returning True if healthy.
            dependency_node: If set, the health status of this check
                             will update the corresponding DependencyNode.
        """
        self._checks[name] = check
        if dependency_node:
            self._check_to_node[name] = dependency_node
        logger.debug("health_check_registered", name=name, node=dependency_node)

    def run_all(self) -> Dict[str, bool]:
        """
        Execute all checks and update dependency graph health accordingly.
        Returns a dict of check name -> healthy (bool).
        """
        results: Dict[str, bool] = {}
        for name, check in self._checks.items():
            try:
                healthy = bool(check())
                results[name] = healthy
                # Update dependency graph if mapped
                node_name = self._check_to_node.get(name)
                if node_name and self._graph:
                    new_health = DependencyHealth.HEALTHY if healthy else DependencyHealth.UNAVAILABLE
                    self._graph.set_health(node_name, new_health)
            except Exception as exc:
                results[name] = False
                node_name = self._check_to_node.get(name)
                if node_name and self._graph:
                    self._graph.set_health(node_name, DependencyHealth.UNAVAILABLE)
                logger.warning("health_check_failed", name=name, error=str(exc))
        return results

    def all_healthy(self) -> bool:
        return all(self.run_all().values())

    def status(self) -> Dict[str, Any]:
        return self.run_all()

    def bind_graph(self, graph: DependencyGraph) -> None:
        """Inject the dependency graph after construction if needed."""
        self._graph = graph