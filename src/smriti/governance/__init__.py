"""governance/__init__.py — Public API for Phase 11 Part 4."""

from smriti.governance.adr import ADR, ADRCategory, ADRRegistry, ADRStatus
from smriti.governance.compliance import ComplianceEngine, ComplianceResult, ComplianceRule
from smriti.governance.evolution import (
    DeprecationRecord,
    EvolutionStrategy,
    InterfaceContract,
    deprecated,
    experimental,  # optional, but good to have
    internal,
    stable,  # <-- ADDED
)
from smriti.governance.invariants import SYSTEM_INVARIANTS, SystemInvariant, assert_all_invariants
from smriti.governance.principles import PRINCIPLES, ArchitecturalPrinciple
from smriti.governance.risk import ArchitecturalRisk, RiskRegister, RiskSeverity

__all__ = [
    "ArchitecturalPrinciple",
    "PRINCIPLES",
    "SystemInvariant",
    "SYSTEM_INVARIANTS",
    "assert_all_invariants",
    "ADR",
    "ADRStatus",
    "ADRCategory",
    "ADRRegistry",
    "ComplianceRule",
    "ComplianceResult",
    "ComplianceEngine",
    "EvolutionStrategy",
    "DeprecationRecord",
    "InterfaceContract",
    "stable",  # <-- ADDED
    "experimental",  # optional
    "internal",
    "deprecated",
    "ArchitecturalRisk",
    "RiskSeverity",
    "RiskRegister",
]
