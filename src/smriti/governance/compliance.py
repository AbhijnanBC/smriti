"""
compliance.py — Architectural Compliance Model (§11.35).

Architecture should be verifiable. Every compliance rule has
a purpose, a verification method, a violation severity, and
a remediation strategy.

This module provides:
    1. ComplianceRule definitions
    2. AST-based static analysis for import boundary enforcement
    3. ComplianceEngine that runs all rules and reports results
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class ViolationSeverity(str, Enum):
    ERROR = "error"  # CI must fail
    WARNING = "warning"  # CI reports but passes
    INFO = "info"  # Informational only


@dataclass
class ComplianceRule:
    """A single verifiable architectural compliance rule."""

    rule_id: str
    description: str
    severity: ViolationSeverity
    check: Callable[[], ComplianceResult]
    remediation: str


@dataclass
class Violation:
    """A single compliance violation instance."""

    rule_id: str
    file: str
    message: str
    severity: ViolationSeverity


@dataclass
class ComplianceResult:
    """Result of running one compliance rule."""

    rule_id: str
    passed: bool
    violations: list[Violation] = field(default_factory=list)
    notes: str = ""


class ComplianceEngine:
    """
    Runs all registered compliance rules and aggregates results.

    Designed to be called from:
        - Architecture tests (pytest)
        - CI pipelines (Makefile)
        - Runtime health checks
    """

    def __init__(self, src_root: Path = Path("src/smriti")) -> None:
        self._src = src_root
        self._rules: dict[str, ComplianceRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register the canonical SMRITI compliance rules."""

        self.register(
            ComplianceRule(
                rule_id="CR-001",
                description="No dashboard module imports from Phase 8 (scoring) directly.",
                severity=ViolationSeverity.ERROR,
                check=lambda: self._check_forbidden_import(
                    layer_dir="dashboard",
                    forbidden={"smriti.scoring", "smriti.reliability_scorer"},
                    rule_id="CR-001",
                ),
                remediation="Use KnowledgeAPI (Phase 9) to access scored data. Never import scoring directly.",
            )
        )

        self.register(
            ComplianceRule(
                rule_id="CR-002",
                description="Views do not import ServiceClient directly.",
                severity=ViolationSeverity.ERROR,
                check=lambda: self._check_forbidden_import(
                    layer_dir="dashboard/views",
                    forbidden={"services.client", "ServiceClient"},
                    rule_id="CR-002",
                ),
                remediation="Views receive PresentationModels from workspaces. Never call ServiceClient.",
            )
        )

        self.register(
            ComplianceRule(
                rule_id="CR-003",
                description="Observability modules do not import from dashboard.",
                severity=ViolationSeverity.ERROR,
                check=lambda: self._check_forbidden_import(
                    layer_dir="observability",
                    forbidden={"smriti.dashboard", "streamlit"},
                    rule_id="CR-003",
                ),
                remediation="Observability is framework-agnostic. Never import dashboard modules.",
            )
        )

        self.register(
            ComplianceRule(
                rule_id="CR-004",
                description="Runtime modules do not import from api or dashboard.",
                severity=ViolationSeverity.ERROR,
                check=lambda: self._check_forbidden_import(
                    layer_dir="runtime",
                    forbidden={"smriti.api", "smriti.dashboard", "streamlit"},
                    rule_id="CR-004",
                ),
                remediation="Runtime is platform-agnostic. It coordinates, never serves requests.",
            )
        )

        self.register(
            ComplianceRule(
                rule_id="CR-005",
                description="Governance modules do not import from dashboard or runtime.",
                severity=ViolationSeverity.WARNING,
                check=lambda: self._check_forbidden_import(
                    layer_dir="governance",
                    forbidden={"smriti.dashboard", "smriti.runtime", "streamlit"},
                    rule_id="CR-005",
                ),
                remediation="Governance is static analysis only. Keep it dependency-free.",
            )
        )

    def register(self, rule: ComplianceRule) -> None:
        self._rules[rule.rule_id] = rule

    def run_all(self) -> dict[str, ComplianceResult]:
        """Execute all compliance rules and return results."""
        results: dict[str, ComplianceResult] = {}
        for rule_id, rule in self._rules.items():
            try:
                result = rule.check()
                results[rule_id] = result
                status = "PASS" if result.passed else "FAIL"
                logger.info("compliance_rule_evaluated", rule_id=rule_id, status=status)
            except Exception as exc:
                results[rule_id] = ComplianceResult(
                    rule_id=rule_id,
                    passed=False,
                    notes=f"Check raised exception: {exc}",
                )
        return results

    def has_errors(self, results: dict[str, ComplianceResult]) -> bool:
        """True if any ERROR-severity rules failed."""
        for rule_id, result in results.items():
            if not result.passed:
                rule = self._rules.get(rule_id)
                if rule and rule.severity == ViolationSeverity.ERROR:
                    return True
        return False

    def _check_forbidden_import(
        self,
        layer_dir: str,
        forbidden: set[str],
        rule_id: str,
    ) -> ComplianceResult:
        target = self._src / layer_dir
        if not target.exists():
            return ComplianceResult(
                rule_id=rule_id, passed=True, notes="Directory not found — skipped."
            )

        violations: list[Violation] = []
        for filepath in target.rglob("*.py"):
            try:
                tree = ast.parse(filepath.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import | ast.ImportFrom):
                    if isinstance(node, ast.Import):
                        names = [a.name for a in node.names]
                    else:
                        names = [node.module or ""]
                    for name in names:
                        if any(f in name for f in forbidden):
                            violations.append(
                                Violation(
                                    rule_id=rule_id,
                                    file=str(filepath.relative_to(self._src.parent.parent)),
                                    message=f"Forbidden import: '{name}'",
                                    severity=ViolationSeverity.ERROR,
                                )
                            )

        return ComplianceResult(
            rule_id=rule_id,
            passed=len(violations) == 0,
            violations=violations,
        )
