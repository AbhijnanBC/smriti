"""
confidence.py — Engineering Confidence Index (ECI) computation.

The ECI answers: "Can the engineering architecture itself be trusted?"
This is independent of scientific confidence (SCI).

ECI Dimensions (each 0–100):
    Architecture:     Architectural invariants verified
    Runtime:          Phase 11 runtime validated
    Infrastructure:   Dependency, config, ownership verified
    Observability:    Health, telemetry, metrics verified
    Governance:       ADRs, policies, compliance verified
    Integration:      Phase-to-phase connections validated
    Compliance:       Manifest, traceability, versioning verified
"""

from __future__ import annotations

from typing import List, Dict
from smriti.core.models import (
    VerificationResult,
    VerificationStatus,
    EngineeringConfidenceIndex,
)


# Domain prefix → ECI dimension mapping
DOMAIN_DIMENSION = {
    "ARCH": "architecture",
    "DEP":  "infrastructure",
    "INV":  "runtime",
    "CONT": "integration",
    "COMP": "compliance",
    "OBS":  "observability",
    "GOV":  "governance",
}

# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
    "architecture":    0.25,
    "runtime":         0.15,
    "infrastructure":  0.15,
    "observability":   0.10,
    "governance":      0.15,
    "integration":     0.15,
    "compliance":      0.05,
}


def compute_eci(results: List[VerificationResult]) -> EngineeringConfidenceIndex:
    """
    Compute the Engineering Confidence Index from verification results.

    Algorithm:
        1. Group results by ECI dimension
        2. Compute pass rate per dimension (0.0–1.0)
        3. Scale to 0–100
        4. Compute weighted aggregate

    Readiness levels:
        0: < 40 ECI
        1: 40–59 ECI
        2: 60–74 ECI
        3: 75–84 ECI
        4: 85–94 ECI
        5: >= 95 ECI (Engineering Complete)
    """
    dimension_scores: Dict[str, float] = {k: 100.0 for k in DIMENSION_WEIGHTS}

    # Group by dimension
    dimension_results: Dict[str, List[VerificationResult]] = {k: [] for k in DIMENSION_WEIGHTS}

    for result in results:
        prefix = result.rule_id.split("-")[0] if "-" in result.rule_id else "ARCH"
        dimension = DOMAIN_DIMENSION.get(prefix, "architecture")
        dimension_results[dimension].append(result)

    # Compute pass rate per dimension
    for dimension, dim_results in dimension_results.items():
        if not dim_results:
            continue
        passed = sum(1 for r in dim_results if r.status == VerificationStatus.PASSED)
        total = len(dim_results)
        dimension_scores[dimension] = (passed / total) * 100.0

    # Compute weighted aggregate.
    # RECTIFIED: renormalize across only the dimensions that actually have
    # verification results. dimension_scores defaults every dimension to
    # 100.0 (see above) so untested dimensions have a defined value to
    # report individually, but blindly including them at full weight in the
    # aggregate silently assumes "no data" == "fully verified" — which lets
    # ECI stay high even when the one dimension that IS covered scores
    # poorly (e.g. today's ARCHITECTURAL_RULES registry only emits "ARCH"
    # rule_ids, so 75% of DIMENSION_WEIGHTS would otherwise be dead weight
    # fixed at 100). Only measured dimensions count toward the aggregate.
    measured_weight = sum(
        weight for dim, weight in DIMENSION_WEIGHTS.items() if dimension_results[dim]
    )
    if measured_weight > 0:
        overall = sum(
            dimension_scores[dim] * weight
            for dim, weight in DIMENSION_WEIGHTS.items()
            if dimension_results[dim]
        ) / measured_weight
    else:
        overall = 0.0

    # Determine readiness level
    if overall >= 95:
        level = 5
    elif overall >= 85:
        level = 4
    elif overall >= 75:
        level = 3
    elif overall >= 60:
        level = 2
    elif overall >= 40:
        level = 1
    else:
        level = 0

    return EngineeringConfidenceIndex(
        architecture_confidence=dimension_scores["architecture"],
        runtime_confidence=dimension_scores["runtime"],
        infrastructure_confidence=dimension_scores["infrastructure"],
        observability_confidence=dimension_scores["observability"],
        governance_confidence=dimension_scores["governance"],
        integration_confidence=dimension_scores["integration"],
        compliance_confidence=dimension_scores["compliance"],
        overall_confidence=round(overall, 2),
        engineering_readiness_level=level,
    )


def compute_verification_coverage(results: List[VerificationResult]) -> list:
    """
    Compute coverage statistics per rule category.
    Returns list of VerificationCoverage.
    """
    from smriti.core.models import VerificationCoverage

    categories: Dict[str, List[VerificationResult]] = {}
    for result in results:
        prefix = result.rule_id.split("-")[0] if "-" in result.rule_id else "ARCH"
        categories.setdefault(prefix, []).append(result)

    coverages = []
    for cat, cat_results in sorted(categories.items()):
        total = len(cat_results)
        passed = sum(1 for r in cat_results if r.status == VerificationStatus.PASSED)
        failed = sum(1 for r in cat_results if r.status == VerificationStatus.FAILED)
        skipped = sum(1 for r in cat_results if r.status == VerificationStatus.SKIPPED)
        coverages.append(VerificationCoverage(
            category=cat,
            total_rules=total,
            rules_passed=passed,
            rules_failed=failed,
            rules_skipped=skipped,
            coverage_percentage=round((passed / total) * 100.0, 1) if total > 0 else 0.0,
        ))
    return coverages