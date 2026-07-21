"""
state_taxonomy.py — Runtime State Taxonomy (§11.12).

Formally separates runtime information into three non-overlapping categories.
Eliminates ambiguity between "state" and "resources" — a common source of
architectural decay.

Three Categories:
    1. Business State   — domain knowledge, claims, reliability scores
    2. Runtime State    — session, interaction history, navigation
    3. Operational State — cache, indexes, configuration, metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class StateCategory(str, Enum):
    """Classification of every piece of state in SMRITI."""
    BUSINESS    = "business"     # Domain knowledge — immutable during runtime
    RUNTIME     = "runtime"      # Session / interaction — mutable, ephemeral
    OPERATIONAL = "operational"  # Infrastructure — disposable, reconstructible


@dataclass(frozen=True)
class StateDescriptor:
    """Formal description of a state variable in the taxonomy."""
    name:              str
    category:          StateCategory
    owner:             str
    lifetime:          str    # "pipeline_run" | "session" | "request" | "indefinite"
    mutability:        str    # "immutable" | "mutable" | "append-only"
    persistence:       str    # "artifact" | "session" | "in-memory" | "disk"
    recovery_strategy: str    # "rebuild" | "restore" | "discard"


# ── Business State ────────────────────────────────────────────────────────────

class BusinessState:
    """
    Business State catalog — domain knowledge representations.

    Invariant: Business state is NEVER mutated during operational runtime.
    All business state originates from the pipeline and is read-only.
    """

    DESCRIPTORS: tuple[StateDescriptor, ...] = (
        StateDescriptor(
            name="KnowledgeGraph",
            category=StateCategory.BUSINESS,
            owner="evolution",
            lifetime="pipeline_run",
            mutability="immutable",
            persistence="artifact",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="ScoredKnowledgeGraph",
            category=StateCategory.BUSINESS,
            owner="scoring",
            lifetime="pipeline_run",
            mutability="immutable",
            persistence="artifact",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="ClaimViews",
            category=StateCategory.BUSINESS,
            owner="api.views",
            lifetime="pipeline_run",
            mutability="immutable",
            persistence="in-memory",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="ReliabilityScores",
            category=StateCategory.BUSINESS,
            owner="scoring",
            lifetime="pipeline_run",
            mutability="immutable",
            persistence="artifact",
            recovery_strategy="rebuild",
        ),
    )


# ── Runtime State ─────────────────────────────────────────────────────────────

class RuntimeStateCategory:
    """
    Runtime State catalog — session and interaction state.

    Runtime state is mutable and ephemeral. It is discarded at session end.
    """

    DESCRIPTORS: tuple[StateDescriptor, ...] = (
        StateDescriptor(
            name="Session",
            category=StateCategory.RUNTIME,
            owner="dashboard.state",
            lifetime="session",
            mutability="mutable",
            persistence="session",
            recovery_strategy="discard",
        ),
        StateDescriptor(
            name="InteractionHistory",
            category=StateCategory.RUNTIME,
            owner="dashboard.controller",
            lifetime="session",
            mutability="append-only",
            persistence="session",
            recovery_strategy="discard",
        ),
        StateDescriptor(
            name="EpistemicState",
            category=StateCategory.RUNTIME,
            owner="dashboard.state",
            lifetime="session",
            mutability="mutable",
            persistence="session",
            recovery_strategy="restore",
        ),
        StateDescriptor(
            name="WorkspaceActivation",
            category=StateCategory.RUNTIME,
            owner="dashboard.workspaces",
            lifetime="session",
            mutability="mutable",
            persistence="session",
            recovery_strategy="discard",
        ),
    )


# ── Operational State ─────────────────────────────────────────────────────────

class OperationalState:
    """
    Operational State catalog — infrastructure and caching.

    Operational state is disposable — it can always be reconstructed
    without loss of domain knowledge or session correctness.
    """

    DESCRIPTORS: tuple[StateDescriptor, ...] = (
        StateDescriptor(
            name="ClaimViewCache",
            category=StateCategory.OPERATIONAL,
            owner="api.store",
            lifetime="pipeline_run",
            mutability="mutable",
            persistence="in-memory",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="IndexRegistry",
            category=StateCategory.OPERATIONAL,
            owner="api.index",
            lifetime="pipeline_run",
            mutability="immutable",
            persistence="in-memory",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="RuntimeManifest",
            category=StateCategory.OPERATIONAL,
            owner="infrastructure.provenance",
            lifetime="pipeline_run",
            mutability="append-only",
            persistence="artifact",
            recovery_strategy="rebuild",
        ),
        StateDescriptor(
            name="TelemetryBuffer",
            category=StateCategory.OPERATIONAL,
            owner="observability",
            lifetime="session",
            mutability="append-only",
            persistence="in-memory",
            recovery_strategy="discard",
        ),
    )