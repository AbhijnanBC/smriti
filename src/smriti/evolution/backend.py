"""
backend.py — Abstract graph backend interface for Phase 7.

RECTIFIED (P2-2): Added predecessors() and successors() to the interface
for cleaner directional traversal. get_neighbors() remains for undirected use.

Rules:
    ✅ Returns plain Python types only (no NetworkX types)
    ✅ Every implementation is interchangeable
    ❌ Never performs semantic reasoning
    ❌ Never performs partitioning/aggregation/annotation
    ❌ Never constructs Relationship objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any, Optional


@dataclass(frozen=True)
class EdgeTuple:
    """A minimal edge representation returned by GraphBackend."""
    source: str
    target: str
    edge_id: str
    relationship_type: str
    confidence: float


class GraphBackend(ABC):
    """Abstract graph backend for Phase 7."""

    @property
    @abstractmethod
    def node_count(self) -> int: ...

    @property
    @abstractmethod
    def edge_count(self) -> int: ...

    @abstractmethod
    def add_node(self, node_id: str, **attrs: Any) -> None:
        """Add a node. Silently updates if node already exists."""
        ...

    @abstractmethod
    def add_edge(
        self, source: str, target: str, edge_id: str,
        relationship_type: str, confidence: float, **attrs: Any,
    ) -> None:
        """Add a directed edge."""
        ...

    @abstractmethod
    def has_node(self, node_id: str) -> bool: ...

    @abstractmethod
    def has_edge(self, source: str, target: str, edge_id: str) -> bool: ...

    @abstractmethod
    def get_neighbors(self, node_id: str) -> List[str]:
        """Return IDs of all adjacent nodes (in + out, deduplicated)."""
        ...

    @abstractmethod
    def predecessors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes with edges pointing TO node_id."""
        ...

    @abstractmethod
    def successors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes that node_id points TO."""
        ...

    @abstractmethod
    def get_out_edges(self, node_id: str) -> List[EdgeTuple]:
        """Return all edges leaving node_id."""
        ...

    @abstractmethod
    def get_in_edges(self, node_id: str) -> List[EdgeTuple]:
        """Return all edges entering node_id."""
        ...

    @abstractmethod
    def all_edges(self) -> List[EdgeTuple]: ...

    @abstractmethod
    def all_node_ids(self) -> List[str]:
        """Return all node IDs in deterministic sorted order."""
        ...

    @abstractmethod
    def connected_components_undirected(self) -> List[List[str]]:
        """
        Return connected components ignoring edge direction.
        Each component is a sorted list of node IDs.
        Sorted by size (largest first), then by first node ID.
        """
        ...

    @abstractmethod
    def subgraph(self, node_ids: List[str]) -> "GraphBackend":
        """Return a subgraph containing only the specified nodes."""
        ...

    @abstractmethod
    def in_degree(self, node_id: str) -> int: ...

    @abstractmethod
    def out_degree(self, node_id: str) -> int: ...

    @abstractmethod
    def degree(self, node_id: str) -> int: ...

    @abstractmethod
    def remove_edges_of_type(self, relationship_type: str) -> "GraphBackend":
        """Return a new backend with all edges of the given type removed."""
        ...

    @abstractmethod
    def articulation_points(self) -> List[str]:
        """
        Return all articulation points (bridge nodes) in the undirected projection.
        Implemented using NetworkX nx.articulation_points().
        RECTIFIED (P0-3): replaces degree-1 heuristic.
        """
        ...