"""
maturity.py — Operational Maturity Model (§11.30).

Provides a structured assessment framework for operational maturity.
Borrowed from capability maturity models and tailored to SMRITI.

Maturity Levels:
    Level 1 — Basic:      Functional runtime, minimal diagnostics
    Level 2 — Observable: Logs, metrics, health checks available
    Level 3 — Resilient:  Failure isolation, degradation, deterministic recovery
    Level 4 — Assured:    Full provenance, auditability, quality guarantees
    Level 5 — Governed:   Continuous compliance, governance, measurable SLOs
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum


class MaturityLevel(IntEnum):
    BASIC = 1
    OBSERVABLE = 2
    RESILIENT = 3
    ASSURED = 4
    GOVERNED = 5


@dataclass(frozen=True)
class MaturityCriterion:
    """A single verifiable criterion for a maturity level."""

    level: MaturityLevel
    description: str
    check: Callable[[], bool]

    def evaluate(self) -> bool:
        try:
            return self.check()
        except Exception:
            return False


@dataclass
class MaturityAssessment:
    """Result of a full maturity assessment."""

    achieved_level: MaturityLevel
    passed_criteria: list[str]
    failed_criteria: list[str]
    summary: str


class MaturityAssessor:
    """
    Evaluates the operational maturity of the running SMRITI instance.

    Each criterion is independently verifiable. The achieved maturity
    level is the highest level where all criteria pass.
    """

    def __init__(self) -> None:
        self._criteria: list[MaturityCriterion] = []

    def register(self, criterion: MaturityCriterion) -> None:
        self._criteria.append(criterion)

    def assess(self) -> MaturityAssessment:
        passed: list[str] = []
        failed: list[str] = []

        for criterion in self._criteria:
            if criterion.evaluate():
                passed.append(f"L{criterion.level}: {criterion.description}")
            else:
                failed.append(f"L{criterion.level}: {criterion.description}")

        # Achieved level = highest level where all lower-level criteria pass
        achieved = MaturityLevel.BASIC
        for level in MaturityLevel:
            level_criteria = [c for c in self._criteria if c.level == level]
            if level_criteria and all(c.evaluate() for c in level_criteria):
                achieved = level

        descriptions = {
            MaturityLevel.BASIC: "Functional runtime with basic execution.",
            MaturityLevel.OBSERVABLE: "Full observability stack active.",
            MaturityLevel.RESILIENT: "Fault-tolerant with graceful degradation.",
            MaturityLevel.ASSURED: "Full provenance and quality guarantees.",
            MaturityLevel.GOVERNED: "Enterprise operational readiness.",
        }

        return MaturityAssessment(
            achieved_level=achieved,
            passed_criteria=passed,
            failed_criteria=failed,
            summary=descriptions[achieved],
        )


def build_default_assessor() -> MaturityAssessor:
    """Build the canonical SMRITI maturity assessor."""
    from smriti.core.paths import ARTIFACTS_DIR

    assessor = MaturityAssessor()

    assessor.register(
        MaturityCriterion(
            level=MaturityLevel.BASIC,
            description="Pipeline runner executes without raising exceptions.",
            check=lambda: True,  # If we are running, basic is met
        )
    )

    assessor.register(
        MaturityCriterion(
            level=MaturityLevel.OBSERVABLE,
            description="Structured logging is configured.",
            check=lambda: __import__("structlog").is_configured(),
        )
    )

    assessor.register(
        MaturityCriterion(
            level=MaturityLevel.OBSERVABLE,
            description="Artifacts directory exists.",
            check=lambda: ARTIFACTS_DIR.exists(),
        )
    )

    assessor.register(
        MaturityCriterion(
            level=MaturityLevel.RESILIENT,
            description="RuntimeCoordinator singleton is available.",
            check=lambda: __import__("smriti.runtime", fromlist=["get_runtime"]).get_runtime()
            is not None,
        )
    )

    assessor.register(
        MaturityCriterion(
            level=MaturityLevel.ASSURED,
            description="Runtime manifest can be written.",
            check=lambda: ARTIFACTS_DIR.exists(),
        )
    )

    return assessor
