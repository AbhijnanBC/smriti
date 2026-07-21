"""
adr.py — Architectural Decision Record (ADR) Framework (§11.34).

Every significant architectural decision in SMRITI is documented as an ADR.
ADRs are immutable once accepted — they can only be superseded, never edited.

ADR Lifecycle:
    PROPOSED → ACCEPTED → (optionally) SUPERSEDED
              → REJECTED (terminal, no reopen)

ADR Template fields:
    1.  Identifier
    2.  Title
    3.  Status
    4.  Context
    5.  Problem
    6.  Alternatives
    7.  Decision
    8.  Rationale
    9.  Consequences
    10. Related ADRs
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ADRStatus(str, Enum):
    PROPOSED   = "proposed"
    ACCEPTED   = "accepted"
    REJECTED   = "rejected"
    SUPERSEDED = "superseded"


class ADRCategory(str, Enum):
    RUNTIME        = "runtime"
    KNOWLEDGE      = "knowledge"
    API            = "api"
    INTERACTION    = "interaction"
    INFRASTRUCTURE = "infrastructure"
    GOVERNANCE     = "governance"
    PERFORMANCE    = "performance"
    EVOLUTION      = "evolution"


@dataclass
class ADR:
    """
    Architectural Decision Record.

    Once ACCEPTED, content fields (decision, rationale, consequences)
    are effectively immutable — modifications require superseding this ADR.
    """
    adr_id:       str
    title:        str
    status:       ADRStatus
    category:     ADRCategory
    context:      str
    problem:      str
    alternatives: List[str]
    decision:     str
    rationale:    str
    consequences: List[str]
    related_adrs: List[str] = field(default_factory=list)
    created_at:   float = field(default_factory=time.time)
    accepted_at:  Optional[float] = None
    superseded_by: Optional[str] = None

    def accept(self) -> None:
        if self.status != ADRStatus.PROPOSED:
            raise ValueError(f"ADR {self.adr_id} cannot be accepted from status {self.status.value}.")
        self.status = ADRStatus.ACCEPTED
        self.accepted_at = time.time()
        logger.info("adr_accepted", adr_id=self.adr_id, title=self.title)

    def supersede(self, new_adr_id: str) -> None:
        if self.status != ADRStatus.ACCEPTED:
            raise ValueError(f"Only ACCEPTED ADRs can be superseded.")
        self.status = ADRStatus.SUPERSEDED
        self.superseded_by = new_adr_id
        logger.info("adr_superseded", adr_id=self.adr_id, by=new_adr_id)

    def to_markdown(self) -> str:
        alts = "\n".join(f"- {a}" for a in self.alternatives)
        cons = "\n".join(f"- {c}" for c in self.consequences)
        related = ", ".join(self.related_adrs) or "None"
        return f"""# ADR-{self.adr_id}: {self.title}

**Status:** {self.status.value}
**Category:** {self.category.value}

## Context
{self.context}

## Problem
{self.problem}

## Alternatives Considered
{alts}

## Decision
{self.decision}

## Rationale
{self.rationale}

## Consequences
{cons}

## Related ADRs
{related}
"""


class ADRRegistry:
    """
    Registry of all Architectural Decision Records.

    ADRs are the living constitution of SMRITI.
    This registry is the authoritative source for all architectural decisions.
    """

    def __init__(self) -> None:
        self._adrs: Dict[str, ADR] = {}
        self._populate_phase11_adrs()

    def _populate_phase11_adrs(self) -> None:
        """Pre-populate Phase 11 ADRs."""
        adr_0011 = ADR(
            adr_id="0011",
            title="Adopt RuntimeCoordinator as sole lifecycle orchestrator",
            status=ADRStatus.ACCEPTED,
            category=ADRCategory.RUNTIME,
            context="Phase 11 introduces an operational runtime layer above Phases 1–10.",
            problem="Without a central coordinator, lifecycle state is scattered across modules.",
            alternatives=[
                "Allow each module to manage its own lifecycle",
                "Use a global dictionary for lifecycle state",
                "Extend PipelineRunner to own lifecycle",
            ],
            decision="Introduce RuntimeCoordinator as the single lifecycle orchestrator.",
            rationale="Single ownership prevents distributed state bugs and enforces invariants.",
            consequences=[
                "All startup/shutdown must go through RuntimeCoordinator.",
                "PipelineRunner registers with but does not own lifecycle.",
                "Health monitoring is centralized.",
            ],
            related_adrs=["0012"],
        )
        adr_0011.accepted_at = time.time()

        adr_0012 = ADR(
            adr_id="0012",
            title="RuntimeManifest written on every pipeline execution",
            status=ADRStatus.ACCEPTED,
            category=ADRCategory.GOVERNANCE,
            context="Research reproducibility requires complete execution records.",
            problem="Without a manifest, it is impossible to reconstruct the exact conditions of a run.",
            alternatives=[
                "Log configuration to stdout only",
                "Store only phase summaries",
            ],
            decision="Write a RuntimeManifest JSON artifact after every successful pipeline execution.",
            rationale=(
                "The manifest captures all version information needed to reproduce a run exactly. "
                "This satisfies the operational provenance invariant (Invariant 8)."
            ),
            consequences=[
                "Every run produces a manifest artifact.",
                "Manifests are immutable after writing.",
                "Phase 12 can read manifests to verify reproducibility.",
            ],
            related_adrs=["0011"],
        )
        adr_0012.accepted_at = time.time()

        self._adrs["0011"] = adr_0011
        self._adrs["0012"] = adr_0012

    def register(self, adr: ADR) -> None:
        if adr.adr_id in self._adrs:
            raise ValueError(f"ADR {adr.adr_id} already registered.")
        self._adrs[adr.adr_id] = adr

    def get(self, adr_id: str) -> Optional[ADR]:
        return self._adrs.get(adr_id)

    def all_accepted(self) -> List[ADR]:
        return [a for a in self._adrs.values() if a.status == ADRStatus.ACCEPTED]

    def export_markdown(self, output_dir: Path) -> None:
        """Write all ADRs as individual markdown files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        for adr in self._adrs.values():
            path = output_dir / f"ADR-{adr.adr_id}.md"
            path.write_text(adr.to_markdown(), encoding="utf-8")
        logger.info("adrs_exported", count=len(self._adrs), dir=str(output_dir))