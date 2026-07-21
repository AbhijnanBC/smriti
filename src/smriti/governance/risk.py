"""
risk.py — Architectural Risk Management (§11.31 addition).

Explicitly identifies, classifies, and tracks architectural risks.
Every mature architecture names its risks rather than hiding them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RiskSeverity(str, Enum):
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"


@dataclass(frozen=True)
class ArchitecturalRisk:
    """A single identified architectural risk with mitigation."""
    risk_id:    str
    name:       str
    description: str
    severity:   RiskSeverity
    mitigation: str
    owner:      str
    status:     str = "open"   # "open" | "mitigated" | "accepted"


# ── Canonical risk register for Phase 11 ─────────────────────────────────────

PHASE11_RISKS: List[ArchitecturalRisk] = [
    ArchitecturalRisk(
        risk_id="R-001",
        name="Architectural Drift",
        description="Over time, new features are added without checking the dependency matrix.",
        severity=RiskSeverity.HIGH,
        mitigation="ADRs + architecture test suite (test_phase11_architecture.py) run on every PR.",
        owner="governance.compliance",
        status="mitigated",
    ),
    ArchitecturalRisk(
        risk_id="R-002",
        name="Layer Violations",
        description="A developer imports from a forbidden layer, creating hidden coupling.",
        severity=RiskSeverity.HIGH,
        mitigation="ComplianceEngine CR-001 through CR-005 fail CI on violation.",
        owner="governance.compliance",
        status="mitigated",
    ),
    ArchitecturalRisk(
        risk_id="R-003",
        name="Knowledge Mutation at Runtime",
        description="A runtime service accidentally writes to the KnowledgeGraph.",
        severity=RiskSeverity.HIGH,
        mitigation="KnowledgeGraph and ScoredKnowledgeGraph are immutable dataclasses.",
        owner="governance.invariants",
        status="mitigated",
    ),
    ArchitecturalRisk(
        risk_id="R-004",
        name="Configuration Drift Between Runs",
        description="Two runs produce different results because configuration changed silently.",
        severity=RiskSeverity.HIGH,
        mitigation="RuntimeManifest captures config_hash; Phase 12 can detect config drift.",
        owner="infrastructure.provenance",
        status="mitigated",
    ),
    ArchitecturalRisk(
        risk_id="R-005",
        name="Uncontrolled Feature Growth",
        description="New workspaces bypass EvolutionStrategy and break phase boundaries.",
        severity=RiskSeverity.MEDIUM,
        mitigation="Extension architecture requires entry point registration + compliance gate.",
        owner="blueprint.extension",
        status="open",
    ),
    ArchitecturalRisk(
        risk_id="R-006",
        name="Interface Instability",
        description="Public API changes break downstream consumers without notice.",
        severity=RiskSeverity.MEDIUM,
        mitigation="InterfaceGovernance tracks stability levels; breaking changes require new ADR.",
        owner="governance.evolution",
        status="open",
    ),
]


class RiskRegister:
    """Registry and query interface for architectural risks."""

    def __init__(self) -> None:
        self._risks: Dict[str, ArchitecturalRisk] = {r.risk_id: r for r in PHASE11_RISKS}

    def get(self, risk_id: str) -> ArchitecturalRisk | None:
        return self._risks.get(risk_id)

    def open_risks(self) -> List[ArchitecturalRisk]:
        return [r for r in self._risks.values() if r.status == "open"]

    def high_severity(self) -> List[ArchitecturalRisk]:
        return [r for r in self._risks.values() if r.severity == RiskSeverity.HIGH]

    def summary(self) -> Dict[str, int]:
        return {
            "total":     len(self._risks),
            "open":      sum(1 for r in self._risks.values() if r.status == "open"),
            "mitigated": sum(1 for r in self._risks.values() if r.status == "mitigated"),
            "high":      sum(1 for r in self._risks.values() if r.severity == RiskSeverity.HIGH),
        }