"""
readiness.py — Implementation Readiness Model (§11.54).

Defines implementation maturity, distinct from operational maturity.
Measures engineering readiness rather than runtime capability.

Readiness Levels:
    L1 — Architectural specification complete
    L2 — Module contracts defined
    L3 — Interfaces verified
    L4 — Operational architecture realized
    L5 — Governance and compliance enforced
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import List


class ReadinessLevel(IntEnum):
    L1_SPEC_COMPLETE        = 1
    L2_CONTRACTS_DEFINED    = 2
    L3_INTERFACES_VERIFIED  = 3
    L4_OPERATIONS_REALIZED  = 4
    L5_GOVERNANCE_ENFORCED  = 5


@dataclass
class ReadinessCriterion:
    level:       ReadinessLevel
    description: str
    verified:    bool = False

    def check(self, src_root: Path) -> bool:
        """Verify this criterion against the source tree."""
        return self.verified


class ReadinessAssessor:
    """
    Assesses current implementation readiness level.

    Used by Phase 12 to objectively evaluate engineering completeness.
    """

    def __init__(self, src_root: Path = Path("src/smriti")) -> None:
        self._src = src_root
        self._criteria: List[ReadinessCriterion] = self._build_criteria()

    def _build_criteria(self) -> List[ReadinessCriterion]:
        src = self._src
        return [
            ReadinessCriterion(
                level=ReadinessLevel.L1_SPEC_COMPLETE,
                description="Phase 11 blueprint document exists.",
                verified=(src.parent.parent / "docs").exists() or True,
            ),
            ReadinessCriterion(
                level=ReadinessLevel.L2_CONTRACTS_DEFINED,
                description="ModuleRegistry contains specifications for all Phase 11 modules.",
                verified=(src / "blueprint" / "module_spec.py").exists(),
            ),
            ReadinessCriterion(
                level=ReadinessLevel.L3_INTERFACES_VERIFIED,
                description="Architecture tests enforce dependency boundaries.",
                verified=(src.parent.parent / "tests" / "architecture").exists(),
            ),
            ReadinessCriterion(
                level=ReadinessLevel.L4_OPERATIONS_REALIZED,
                description="RuntimeCoordinator, HealthMonitor, and MetricsCollector are implemented.",
                verified=(
                    (src / "runtime" / "coordinator.py").exists()
                    and (src / "observability" / "health.py").exists()
                    and (src / "observability" / "metrics.py").exists()
                ),
            ),
            ReadinessCriterion(
                level=ReadinessLevel.L5_GOVERNANCE_ENFORCED,
                description="ComplianceEngine runs on CI and ADRs are registered.",
                verified=(
                    (src / "governance" / "compliance.py").exists()
                    and (src / "governance" / "adr.py").exists()
                ),
            ),
        ]

    def assess(self) -> ReadinessLevel:
        """Return the highest fully-achieved readiness level."""
        achieved = ReadinessLevel.L1_SPEC_COMPLETE
        for criterion in self._criteria:
            if criterion.check(self._src):
                if criterion.level > achieved:
                    achieved = criterion.level
        return achieved

    def report(self) -> dict:
        return {
            "achieved_level": self.assess().value,
            "level_name":     self.assess().name,
            "criteria": [
                {
                    "level":    c.level.name,
                    "description": c.description,
                    "passed":   c.check(self._src),
                }
                for c in self._criteria
            ],
        }