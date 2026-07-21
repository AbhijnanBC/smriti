"""
dependency.py — Dependency Architecture & Boundary Matrix (§11.10).

Formalizes the allowed and forbidden dependency directions across all
architectural layers. The boundary matrix is the authoritative reference
for all import decisions.

Layer Hierarchy (top → bottom):
    Presentation Layer
        ↓ (can access)
    Interaction Layer
        ↓
    Knowledge API
        ↓
    Knowledge Services
        ↓
    Knowledge Graph
        ↓
    Artifacts

No upward dependencies are permitted. No layer may skip levels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Dict


@dataclass(frozen=True)
class LayerBoundary:
    """Formal description of a single architectural layer's dependency contract."""
    layer:           str
    can_access:      FrozenSet[str]
    cannot_access:   FrozenSet[str]
    public_interface: FrozenSet[str]
    owner:           str


# ── The canonical boundary matrix ────────────────────────────────────────────
# This is the single authoritative reference. Architecture tests enforce it.

BOUNDARY_MATRIX: Dict[str, LayerBoundary] = {

    "presentation": LayerBoundary(
        layer="presentation",
        can_access=frozenset({"presentation_models", "view_registry"}),
        cannot_access=frozenset({"knowledge_api", "scoring", "evolution", "phase_8", "phase_9"}),
        public_interface=frozenset({"BaseView", "ViewRegistry"}),
        owner="dashboard.views",
    ),

    "interaction": LayerBoundary(
        layer="interaction",
        can_access=frozenset({"workspace_context", "service_client", "presentation_models"}),
        cannot_access=frozenset({"knowledge_graph", "scoring_internals", "graph_construction"}),
        public_interface=frozenset({"BaseWorkspace", "WorkspaceRegistry"}),
        owner="dashboard.workspaces",
    ),

    "knowledge_api": LayerBoundary(
        layer="knowledge_api",
        can_access=frozenset({"read_store", "index_registry", "domain_services"}),
        cannot_access=frozenset({"dashboard", "presentation", "streamlit"}),
        public_interface=frozenset({"KnowledgeAccessService", "ApplicationService"}),
        owner="api",
    ),

    "knowledge_services": LayerBoundary(
        layer="knowledge_services",
        can_access=frozenset({"read_store", "scoring", "evolution"}),
        cannot_access=frozenset({"dashboard", "interaction", "presentation"}),
        public_interface=frozenset({"QueryService", "ExplainService", "ExportService"}),
        owner="api.services",
    ),

    "knowledge_graph": LayerBoundary(
        layer="knowledge_graph",
        can_access=frozenset({"core.models", "artifacts"}),
        cannot_access=frozenset({"dashboard", "api", "interaction", "presentation"}),
        public_interface=frozenset({"KnowledgeGraph", "ScoredKnowledgeGraph"}),
        owner="evolution",
    ),

    "artifacts": LayerBoundary(
        layer="artifacts",
        can_access=frozenset({"core.paths", "core.models"}),
        cannot_access=frozenset({"dashboard", "api", "evolution", "scoring"}),
        public_interface=frozenset({"ARTIFACTS_DIR"}),
        owner="core",
    ),
}


class DependencyMatrix:
    """
    Validates import decisions against the boundary matrix.

    Usage:
        matrix = DependencyMatrix()
        matrix.assert_allowed("presentation", "knowledge_api")  # raises
        matrix.assert_allowed("knowledge_api", "read_store")    # passes
    """

    def __init__(self) -> None:
        self._matrix = BOUNDARY_MATRIX

    def is_allowed(self, from_layer: str, to_layer: str) -> bool:
        boundary = self._matrix.get(from_layer)
        if boundary is None:
            return True  # Unknown layer — allow (conservative)
        return to_layer not in boundary.cannot_access

    def assert_allowed(self, from_layer: str, to_layer: str) -> None:
        """
        Raise if the dependency direction is forbidden.

        Raises:
            ValueError: if the dependency violates the boundary matrix.
        """
        if not self.is_allowed(from_layer, to_layer):
            boundary = self._matrix[from_layer]
            raise ValueError(
                f"Forbidden dependency: {from_layer} → {to_layer}. "
                f"Layer '{from_layer}' (owned by {boundary.owner}) "
                f"must not access '{to_layer}'."
            )

    def get_boundary(self, layer: str) -> LayerBoundary | None:
        return self._matrix.get(layer)