"""
traceability.py — Architectural Traceability Model (§11.56 addition).

Every implementation artifact is traceable back to the architecture.

Traceability chain:
    Requirement
        ↓
    Architectural Principle
        ↓
    System Invariant
        ↓
    ADR
        ↓
    Module
        ↓
    Interface
        ↓
    Implementation
        ↓
    Operational Verification
        ↓
    Evaluation Result

This enables Phase 12 to evaluate not only whether the system works,
but whether every result is traceable to the architectural decisions
that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TraceabilityLink:
    """
    A single link in the architectural traceability chain.
    """
    artifact_id:    str      # unique ID for this artifact (e.g., "MOD-runtime")
    artifact_type:  str      # "requirement" | "principle" | "invariant" | "adr" | "module" | "test"
    name:           str
    traced_to:      Optional[str]   # parent artifact_id (None = root)
    description:    str


class TraceabilityMatrix:
    """
    Complete traceability matrix for SMRITI Phase 11.

    Allows Phase 12 to verify that every evaluation result
    can be traced back to an architectural decision.
    """

    def __init__(self) -> None:
        self._links: Dict[str, TraceabilityLink] = {}
        self._populate_phase11()

    def _populate_phase11(self) -> None:
        links = [
            # ── Requirements ─────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="REQ-reproducibility",
                artifact_type="requirement",
                name="Research Reproducibility",
                traced_to=None,
                description="All pipeline results must be reproducible given the same inputs.",
            ),
            TraceabilityLink(
                artifact_id="REQ-observability",
                artifact_type="requirement",
                name="Operational Observability",
                traced_to=None,
                description="System behavior must be inspectable at runtime.",
            ),
            # ── Principles ───────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="PRIN-determinism",
                artifact_type="principle",
                name="Determinism",
                traced_to="REQ-reproducibility",
                description="Identical inputs produce identical outputs.",
            ),
            TraceabilityLink(
                artifact_id="PRIN-observability",
                artifact_type="principle",
                name="Observability",
                traced_to="REQ-observability",
                description="Every significant operational event is recorded.",
            ),
            # ── Invariants ───────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="INV-8",
                artifact_type="invariant",
                name="Invariant 8: Every execution has provenance",
                traced_to="PRIN-determinism",
                description="RuntimeManifest is written for every execution.",
            ),
            TraceabilityLink(
                artifact_id="INV-5",
                artifact_type="invariant",
                name="Invariant 5: Configuration immutable after init",
                traced_to="PRIN-determinism",
                description="ConfigurationContext is frozen after CONFIGURATION_LOADING.",
            ),
            # ── ADRs ─────────────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="ADR-0012",
                artifact_type="adr",
                name="ADR-0012: RuntimeManifest on every execution",
                traced_to="INV-8",
                description="Decision to write manifest artifact for reproducibility.",
            ),
            # ── Modules ──────────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="MOD-provenance",
                artifact_type="module",
                name="smriti.infrastructure.provenance",
                traced_to="ADR-0012",
                description="ProvenanceBuilder implements the manifest writing contract.",
            ),
            # ── Tests ─────────────────────────────────────────────────────────
            TraceabilityLink(
                artifact_id="TEST-provenance",
                artifact_type="test",
                name="test_phase11_architecture.py::test_provenance_builder",
                traced_to="MOD-provenance",
                description="Verifies ProvenanceBuilder produces complete manifests.",
            ),
        ]
        for link in links:
            self._links[link.artifact_id] = link

    def register(self, link: TraceabilityLink) -> None:
        self._links[link.artifact_id] = link

    def trace_chain(self, artifact_id: str) -> List[TraceabilityLink]:
        """Return the full traceability chain from artifact to root."""
        chain: List[TraceabilityLink] = []
        current_id: Optional[str] = artifact_id
        visited: set[str] = set()
        while current_id and current_id not in visited:
            link = self._links.get(current_id)
            if link is None:
                break
            chain.append(link)
            visited.add(current_id)
            current_id = link.traced_to
        return chain

    def all_links(self) -> List[TraceabilityLink]:
        return list(self._links.values())