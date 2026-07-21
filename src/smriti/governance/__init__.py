"""governance/__init__.py — Public API for Phase 11 Part 4."""

from smriti.governance.principles  import ArchitecturalPrinciple, PRINCIPLES
from smriti.governance.invariants  import SystemInvariant, SYSTEM_INVARIANTS, assert_all_invariants
from smriti.governance.adr         import ADR, ADRStatus, ADRCategory, ADRRegistry
from smriti.governance.compliance  import ComplianceRule, ComplianceResult, ComplianceEngine
from smriti.governance.evolution   import (
    EvolutionStrategy,
    DeprecationRecord,
    InterfaceContract,
    stable,          # <-- ADDED
    experimental,    # optional, but good to have
    internal,
    deprecated,
)
from smriti.governance.risk        import ArchitecturalRisk, RiskSeverity, RiskRegister

__all__ = [
    "ArchitecturalPrinciple", "PRINCIPLES",
    "SystemInvariant", "SYSTEM_INVARIANTS", "assert_all_invariants",
    "ADR", "ADRStatus", "ADRCategory", "ADRRegistry",
    "ComplianceRule", "ComplianceResult", "ComplianceEngine",
    "EvolutionStrategy", "DeprecationRecord", "InterfaceContract",
    "stable",          # <-- ADDED
    "experimental",    # optional
    "internal",
    "deprecated",
    "ArchitecturalRisk", "RiskSeverity", "RiskRegister",
]