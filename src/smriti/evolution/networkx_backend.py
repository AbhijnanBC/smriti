"""
networkx_backend.py — NetworkX implementation of GraphBackend.

This is the ONLY module in Phase 7 that imports networkx.

RECTIFIED (P0-3): articulation_points() uses nx.articulation_points()
on the undirected projection — the true graph-theoretic definition,
not degree-1 heuristic.

RECTIFIED (P2-2): predecessors() and successors() added.
"""

from __future__ import annotations

from typing import Any

import structlog

from smriti.evolution.backend import EdgeTuple, GraphBackend
from smriti.exceptions import BackendError

logger = structlog.get_logger(__name__)


class NetworkXBackend(GraphBackend):
    """NetworkX MultiDiGraph implementation of GraphBackend."""

    def __init__(self) -> None:
        try:
            import networkx as nx

            self._G = nx.MultiDiGraph()
            self._nx = nx
        except ImportError as e:
            raise BackendError(
                f"networkx is not installed. Run: poetry add networkx\nError: {e}"
            ) from e

    @property
    def node_count(self) -> int:
        return self._G.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self._G.number_of_edges()

    def add_node(self, node_id: str, **attrs: Any) -> None:
        self._G.add_node(node_id, **attrs)

    def add_edge(
        self,
        source: str,
        target: str,
        edge_id: str,
        relationship_type: str,
        confidence: float,
        **attrs: Any,
    ) -> None:
        self._G.add_edge(
            source,
            target,
            key=edge_id,
            edge_id=edge_id,
            relationship_type=relationship_type,
            confidence=confidence,
            **attrs,
        )

    def has_node(self, node_id: str) -> bool:
        return self._G.has_node(node_id)

    def has_edge(self, source: str, target: str, edge_id: str) -> bool:
        return self._G.has_edge(source, target, key=edge_id)

    def get_neighbors(self, node_id: str) -> list[str]:
        successors = set(self._G.successors(node_id))
        predecessors = set(self._G.predecessors(node_id))
        return sorted(successors | predecessors)

    def predecessors(self, node_id: str) -> list[str]:
        """Return nodes with edges pointing TO node_id."""
        return sorted(self._G.predecessors(node_id))

    def successors(self, node_id: str) -> list[str]:
        """Return nodes that node_id points TO."""
        return sorted(self._G.successors(node_id))

    def get_out_edges(self, node_id: str) -> list[EdgeTuple]:
        edges = []
        for _, target, data in self._G.out_edges(node_id, data=True):
            edges.append(
                EdgeTuple(
                    source=node_id,
                    target=target,
                    edge_id=data.get("edge_id", ""),
                    relationship_type=data.get("relationship_type", ""),
                    confidence=data.get("confidence", 0.0),
                )
            )
        return edges

    def get_in_edges(self, node_id: str) -> list[EdgeTuple]:
        edges = []
        for source, _, data in self._G.in_edges(node_id, data=True):
            edges.append(
                EdgeTuple(
                    source=source,
                    target=node_id,
                    edge_id=data.get("edge_id", ""),
                    relationship_type=data.get("relationship_type", ""),
                    confidence=data.get("confidence", 0.0),
                )
            )
        return edges

    def all_edges(self) -> list[EdgeTuple]:
        edges = []
        for source, target, data in self._G.edges(data=True):
            edges.append(
                EdgeTuple(
                    source=source,
                    target=target,
                    edge_id=data.get("edge_id", ""),
                    relationship_type=data.get("relationship_type", ""),
                    confidence=data.get("confidence", 0.0),
                )
            )
        return sorted(edges, key=lambda e: (e.source, e.target, e.edge_id))

    def all_node_ids(self) -> list[str]:
        return sorted(self._G.nodes())

    def connected_components_undirected(self) -> list[list[str]]:
        undirected = self._G.to_undirected()
        components = list(self._nx.connected_components(undirected))
        return sorted(
            [sorted(c) for c in components],
            key=lambda c: (-len(c), c[0] if c else ""),
        )

    def subgraph(self, node_ids: list[str]) -> NetworkXBackend:
        sub = self._G.subgraph(node_ids).copy()
        new_backend = NetworkXBackend.__new__(NetworkXBackend)
        new_backend._nx = self._nx
        new_backend._G = sub
        return new_backend

    def in_degree(self, node_id: str) -> int:
        return self._G.in_degree(node_id)

    def out_degree(self, node_id: str) -> int:
        return self._G.out_degree(node_id)

    def degree(self, node_id: str) -> int:
        return self._G.degree(node_id)

    def remove_edges_of_type(self, relationship_type: str) -> NetworkXBackend:
        new_backend = NetworkXBackend.__new__(NetworkXBackend)
        new_backend._nx = self._nx
        new_backend._G = self._G.copy()
        edges_to_remove = [
            (u, v, k)
            for u, v, k, d in new_backend._G.edges(data=True, keys=True)
            if d.get("relationship_type") == relationship_type
        ]
        new_backend._G.remove_edges_from(edges_to_remove)
        return new_backend

    def articulation_points(self) -> list[str]:
        """
        Return true articulation points using NetworkX.

        RECTIFIED (P0-3): Uses nx.articulation_points() on the undirected
        projection. This is the correct graph-theoretic definition:
        a node whose removal disconnects the graph.
        degree == 1 is NOT a valid bridge-detection heuristic.

        Example where old code was wrong:
            A → B → C (chain of 3)
            B has degree 2 and is the only articulation point.
            Old code: is_bridge=False (degree != 1)
            Fixed code: is_bridge=True (nx.articulation_points detects B)
        """
        if self._G.number_of_nodes() < 2:
            return []
        undirected = self._G.to_undirected()
        try:
            return sorted(self._nx.articulation_points(undirected))
        except Exception:
            return []
