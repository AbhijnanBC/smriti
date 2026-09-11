"""
principles.py — Architectural Principles (§11.32).

These are the permanent engineering principles of SMRITI.
Every future architectural decision is justified against these principles.
Principles are not rules — they are lenses for evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitecturalPrinciple:
    """A single named architectural principle with rationale."""

    name: str
    statement: str
    rationale: str
    examples: tuple[str, ...]


PRINCIPLES: dict[str, ArchitecturalPrinciple] = {
    "determinism": ArchitecturalPrinciple(
        name="Determinism",
        statement="Given identical inputs and configuration, SMRITI produces identical outputs.",
        rationale="Research reproducibility requires that results can be independently verified.",
        examples=(
            "Pipeline hashing uses config_hash to detect configuration drift.",
            "RuntimeManifest captures all versions needed to reproduce a run.",
        ),
    ),
    "reproducibility": ArchitecturalPrinciple(
        name="Reproducibility",
        statement="Every execution produces a complete provenance record sufficient to reconstruct it.",
        rationale="Operational provenance enables post-hoc debugging and research validation.",
        examples=(
            "RuntimeManifest is written to artifacts on every run.",
            "Git commit hash is captured in the manifest.",
        ),
    ),
    "immutability": ArchitecturalPrinciple(
        name="Immutability",
        statement="Domain knowledge and configuration are immutable during operational runtime.",
        rationale="Mutable knowledge during serving creates non-determinism and race conditions.",
        examples=(
            "KnowledgeGraph is built once by the pipeline; never written to by the dashboard.",
            "ConfigurationContext is a frozen dataclass after initialization.",
        ),
    ),
    "separation_of_concerns": ArchitecturalPrinciple(
        name="Separation of Concerns",
        statement="Each layer owns exactly one architectural responsibility.",
        rationale="Clear ownership prevents coupling and enables independent evolution.",
        examples=(
            "Dashboard never computes reliability scores (that is Phase 8's concern).",
            "Knowledge API never renders Streamlit widgets.",
        ),
    ),
    "explicit_interfaces": ArchitecturalPrinciple(
        name="Explicit Interfaces",
        statement="All cross-layer communication passes through declared public interfaces.",
        rationale="Explicit contracts prevent hidden coupling and enable compliance verification.",
        examples=(
            "Dashboard always calls KnowledgeAPI through ServiceClient.",
            "Workspaces receive data as DTOs, not raw dicts.",
        ),
    ),
    "observability": ArchitecturalPrinciple(
        name="Observability",
        statement="Every significant operational event is recorded and inspectable.",
        rationale="Operational trust requires that system behavior is never opaque.",
        examples=(
            "Every runtime state transition is logged with reason.",
            "Every lifecycle phase entry and exit is recorded.",
        ),
    ),
    "graceful_degradation": ArchitecturalPrinciple(
        name="Graceful Degradation",
        statement="Partial functionality is always preferred over total failure.",
        rationale="Research workflows tolerate reduced capability far better than complete outages.",
        examples=(
            "If explainability fails, claims are returned without explanations.",
            "If FAISS is unavailable, keyword search continues.",
        ),
    ),
    "replaceability": ArchitecturalPrinciple(
        name="Replaceability",
        statement="Every infrastructure component is replaceable without affecting domain logic.",
        rationale="Long-term maintainability requires that implementation choices are not permanent.",
        examples=(
            "NetworkX backend is replaceable with any graph library.",
            "FAISS index is replaceable with scikit-learn fallback.",
        ),
    ),
    "platform_independence": ArchitecturalPrinciple(
        name="Platform Independence",
        statement="Architecture does not prescribe deployment technologies or cloud providers.",
        rationale="Research software must remain reproducible across environments and institutions.",
        examples=(
            "No Docker references in architectural code.",
            "No cloud SDK imports in smriti.core or smriti.runtime.",
        ),
    ),
    "single_responsibility": ArchitecturalPrinciple(
        name="Single Responsibility",
        statement="Every module, class, and function has exactly one reason to change.",
        rationale="Focused components are easier to test, verify, and evolve independently.",
        examples=(
            "ManifestManager only manages manifest writes — not state transitions.",
            "FailureTaxonomy only classifies failures — not recovers from them.",
        ),
    ),
}
