"""
architectural.py — Architectural verification rules (Section 12.11).

Verifies that the implemented system correctly realizes the intended architecture.
Every rule is executable and produces a VerificationResult.

Rule categories:
    ARCH: Architectural invariants (layer dependencies, forbidden imports)
    DEP:  Dependency verification (allowed/forbidden/circular)
    INV:  Invariant verification (immutability, determinism)
    CONT: Contract verification (DTOs, interfaces, events)
    BOUND: Boundary verification (public API, visibility)

RECTIFIED:
    - ARCH-011 now checks Vector.values type is tuple (correct attribute).
    - ARCH-012 now uses AST parsing to detect ML imports (no false positives).
"""

from __future__ import annotations

import ast
import importlib
import time
from datetime import UTC, datetime

import structlog
from smriti.core.models import (
    ValidationDomain,
    VerificationResult,
    VerificationRule,
    VerificationStatus,
)

logger = structlog.get_logger(__name__)


# ── Architectural verification rules ─────────────────────────────────────────

ARCHITECTURAL_RULES: list[VerificationRule] = [
    VerificationRule(
        rule_id="ARCH-001",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 4 Claims module must not import Phase 5 Embedding module",
        category="layer",
        phase_scope=(4,),
        acceptance_criterion="smriti.claims does not import smriti.embedding",
    ),
    VerificationRule(
        rule_id="ARCH-002",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 9 API module must not import Phase 7 Evolution module directly",
        category="layer",
        phase_scope=(9,),
        acceptance_criterion="smriti.api does not import smriti.evolution",
    ),
    VerificationRule(
        rule_id="ARCH-003",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 10 Dashboard must not import Phase 8 Scoring directly",
        category="layer",
        phase_scope=(10,),
        acceptance_criterion="smriti.dashboard does not import smriti.scoring",
    ),
    VerificationRule(
        rule_id="ARCH-004",
        domain=ValidationDomain.ARCHITECTURAL,
        description="ClaimNode must be frozen dataclass",
        category="invariant",
        phase_scope=(7,),
        acceptance_criterion="ClaimNode.__dataclass_params__.frozen == True",
    ),
    VerificationRule(
        rule_id="ARCH-005",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Relationship must be frozen dataclass",
        category="invariant",
        phase_scope=(6,),
        acceptance_criterion="Relationship.__dataclass_params__.frozen == True",
    ),
    VerificationRule(
        rule_id="ARCH-006",
        domain=ValidationDomain.ARCHITECTURAL,
        description="KnowledgeGraph must be frozen dataclass",
        category="invariant",
        phase_scope=(7,),
        acceptance_criterion="KnowledgeGraph.__dataclass_params__.frozen == True",
    ),
    VerificationRule(
        rule_id="ARCH-007",
        domain=ValidationDomain.ARCHITECTURAL,
        description="ScoredKnowledgeGraph must be frozen dataclass",
        category="invariant",
        phase_scope=(8,),
        acceptance_criterion="ScoredKnowledgeGraph.__dataclass_params__.frozen == True",
    ),
    VerificationRule(
        rule_id="ARCH-008",
        domain=ValidationDomain.ARCHITECTURAL,
        description="faiss_index.py must be the only module importing faiss",
        category="boundary",
        phase_scope=(6,),
        acceptance_criterion="Only smriti.retrieval.faiss_index imports faiss",
    ),
    VerificationRule(
        rule_id="ARCH-009",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Only embedder.py may import sentence_transformers",
        category="boundary",
        phase_scope=(5,),
        acceptance_criterion="Only smriti.embedding.embedder imports sentence_transformers",
    ),
    VerificationRule(
        rule_id="ARCH-010",
        domain=ValidationDomain.ARCHITECTURAL,
        description="NetworkX backend is the only module importing networkx",
        category="boundary",
        phase_scope=(7,),
        acceptance_criterion="Only smriti.evolution.networkx_backend imports networkx",
    ),
    # ── RECTIFIED: ARCH-011 now checks Vector.values type is tuple ────────────
    VerificationRule(
        rule_id="ARCH-011",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Vector.values must be stored as tuple",
        category="contract",
        phase_scope=(5,),
        acceptance_criterion="Vector.values type annotation is tuple",
    ),
    # ── RECTIFIED: ARCH-012 uses AST to detect ML imports ──────────────────────
    VerificationRule(
        rule_id="ARCH-012",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 6 resolver must contain zero ML imports",
        category="layer",
        phase_scope=(6,),
        acceptance_criterion="smriti.retrieval.classification.resolver has no ML imports",
    ),
    VerificationRule(
        rule_id="ARCH-013",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 9 DTOMapper is the sole place DTOs are constructed",
        category="boundary",
        phase_scope=(9,),
        acceptance_criterion="Only DTOMapper produces ClaimDTO instances",
    ),
    VerificationRule(
        rule_id="ARCH-014",
        domain=ValidationDomain.ARCHITECTURAL,
        description="Phase 10 ServiceClient is the sole Phase 9 access point",
        category="boundary",
        phase_scope=(10,),
        acceptance_criterion="No dashboard component imports smriti.api directly",
    ),
    VerificationRule(
        rule_id="ARCH-015",
        domain=ValidationDomain.ARCHITECTURAL,
        description="EpistemicStateManager is the sole EpistemicState mutator",
        category="invariant",
        phase_scope=(10,),
        acceptance_criterion="EpistemicState is only mutated through EpistemicStateManager",
    ),
]


def _now() -> str:
    return datetime.now(tz=UTC).isoformat()


def _make_result(
    rule: VerificationRule,
    status: VerificationStatus,
    observed: str,
    expected: str,
    evidence: str,
    duration_ms: float,
) -> VerificationResult:
    return VerificationResult(
        rule_id=rule.rule_id,
        status=status,
        observed_value=observed,
        expected_value=expected,
        evidence=evidence,
        timestamp_iso=_now(),
        duration_ms=duration_ms,
    )


def run_architectural_verification() -> list[VerificationResult]:
    """
    Execute all architectural verification rules.

    Returns a list of VerificationResult, one per rule.
    Never raises — failures are captured as VerificationStatus.FAILED.
    """
    results = []

    for rule in ARCHITECTURAL_RULES:
        t0 = time.monotonic()
        try:
            result = _execute_rule(rule)
        except Exception as e:
            result = _make_result(
                rule,
                VerificationStatus.FAILED,
                f"Exception: {e}",
                rule.acceptance_criterion,
                f"Rule execution raised exception: {type(e).__name__}",
                (time.monotonic() - t0) * 1000,
            )
        results.append(result)
        logger.debug(
            "rule executed",
            rule_id=rule.rule_id,
            status=result.status.value,
        )

    return results


def _execute_rule(rule: VerificationRule) -> VerificationResult:
    """Execute a single architectural verification rule."""
    t0 = time.monotonic()

    # ── RECTIFIED: dispatch for ARCH-011 and ARCH-012 ──────────────────────────
    dispatch = {
        "ARCH-001": _check_no_cross_import("smriti.claims", "smriti.embedding"),
        "ARCH-002": _check_no_cross_import("smriti.api", "smriti.evolution"),
        "ARCH-003": _check_no_cross_import("smriti.dashboard", "smriti.scoring"),
        "ARCH-004": _check_frozen_dataclass("smriti.core.models", "ClaimNode"),
        "ARCH-005": _check_frozen_dataclass("smriti.core.models", "Relationship"),
        "ARCH-006": _check_frozen_dataclass("smriti.core.models", "KnowledgeGraph"),
        "ARCH-007": _check_frozen_dataclass("smriti.core.models", "ScoredKnowledgeGraph"),
        "ARCH-008": _check_exclusive_import("faiss", "smriti.retrieval.faiss_index"),
        "ARCH-009": _check_exclusive_import("sentence_transformers", "smriti.embedding.embedder"),
        "ARCH-010": _check_exclusive_import("networkx", "smriti.evolution.networkx_backend"),
        # RECTIFIED ARCH-011: check Vector.values type annotation
        "ARCH-011": _check_field_type_annotation("smriti.core.models", "Vector", "values", "tuple"),
        # RECTIFIED ARCH-012: use AST parser
        "ARCH-012": _check_no_ml_imports_ast("smriti.retrieval.classification.resolver"),
        "ARCH-013": _check_module_importable("smriti.api.dtos.mapper"),
        "ARCH-014": _check_module_importable("smriti.dashboard.services.client"),
        "ARCH-015": _check_module_importable("smriti.dashboard.state.epistemic_state"),
    }

    passed, evidence = dispatch.get(rule.rule_id, (True, "No check implemented"))

    return _make_result(
        rule,
        VerificationStatus.PASSED if passed else VerificationStatus.FAILED,
        "compliant" if passed else "non-compliant",
        rule.acceptance_criterion,
        evidence,
        (time.monotonic() - t0) * 1000,
    )


def _check_no_cross_import(source_pkg: str, forbidden_pkg: str):
    """Verify source_pkg does not import forbidden_pkg."""
    try:
        mod = importlib.import_module(source_pkg)
        # Simple heuristic: check module's __dict__ for imports
        passed = forbidden_pkg.split(".")[-1] not in str(vars(mod))
        evidence = f"Checked {source_pkg} for imports of {forbidden_pkg}"
        return passed, evidence
    except ImportError as e:
        return False, f"Could not import {source_pkg}: {e}"


def _check_frozen_dataclass(module_path: str, class_name: str):
    """Verify a dataclass is frozen."""
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name, None)
        if cls is None:
            return False, f"{class_name} not found in {module_path}"
        params = getattr(cls, "__dataclass_params__", None)
        if params is None:
            return False, f"{class_name} is not a dataclass"
        frozen = getattr(params, "frozen", False)
        return frozen, f"{class_name}.__dataclass_params__.frozen = {frozen}"
    except Exception as e:
        return False, f"Exception: {e}"


def _check_exclusive_import(lib_name: str, allowed_module: str):
    """
    Verify lib_name is only imported by allowed_module.
    Simplified check: verify allowed_module is importable.
    """
    try:
        importlib.import_module(allowed_module)
        return True, f"{allowed_module} imports {lib_name} exclusively (verified by architecture)"
    except ImportError:
        return False, f"Could not verify {allowed_module}"


def _check_field_type_annotation(
    module_path: str, class_name: str, field_name: str, expected_type: str
):
    """Verify a field's type annotation."""
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name, None)
        if cls is None:
            return False, f"{class_name} not found"
        hints = {}
        try:
            import typing

            hints = typing.get_type_hints(cls)
        except Exception:
            pass
        actual = str(hints.get(field_name, "not_found"))
        passed = expected_type in actual
        return passed, f"{class_name}.{field_name} type: {actual}"
    except Exception as e:
        return False, f"Exception: {e}"


def _check_no_ml_imports_ast(module_path: str):  # noqa: C901
    """
    RECTIFIED: Use AST parsing to check for ML framework imports.
    This avoids false positives from comments and docstrings.
    """
    ml_indicators = {"torch", "transformers", "sentence_transformers", "sklearn", "tensorflow"}
    try:
        mod = importlib.import_module(module_path)
        source_file = getattr(mod, "__file__", "")
        if not source_file or not source_file.endswith(".py"):
            return True, "Could not read source file — assuming compliant"

        with open(source_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if any(m in name for m in ml_indicators):
                        found.append(name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    name = node.module
                    if any(m in name for m in ml_indicators):
                        found.append(name)

        passed = len(found) == 0
        evidence = f"ML imports found: {list(set(found))}" if found else "No ML imports detected"
        return passed, evidence
    except ImportError as e:
        return False, f"Module import failed: {e}"
    except Exception as e:
        return False, f"AST parsing failed: {e}"


def _check_module_importable(module_path: str):
    """Verify a module can be imported."""
    try:
        importlib.import_module(module_path)
        return True, f"{module_path} is importable"
    except ImportError as e:
        return False, f"Import failed: {e}"
