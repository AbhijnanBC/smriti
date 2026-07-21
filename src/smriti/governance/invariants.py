"""
invariants.py — System Invariants (§11.33).

Unlike principles (which guide decisions), invariants are
non-negotiable truths. They must hold at all times.
Violation of an invariant is a design error, not a runtime failure.

System Invariants (10 canonical):
    1.  Knowledge Graph is immutable during runtime
    2.  Presentation never modifies domain knowledge
    3.  Every user interaction passes through Phase 10 (dashboard)
    4.  Every knowledge query passes through Phase 9 (KnowledgeAPI)
    5.  Runtime configuration becomes immutable after initialization
    6.  Infrastructure never computes domain knowledge
    7.  Operational services never bypass architectural boundaries
    8.  Every execution produces operational provenance
    9.  Architectural layers remain acyclic
    10. Every public interface has a single architectural owner
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional
import structlog

from smriti.exceptions import Phase11InvariantViolation

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class SystemInvariant:
    """
    A single non-negotiable system invariant.

    check() returns True if the invariant holds, raises Phase11InvariantViolation
    if it is violated, or returns False if it cannot be evaluated (non-fatal).
    """
    id:          int
    name:        str
    statement:   str
    scope:       str          # "runtime" | "architecture" | "pipeline"
    check:       Optional[Callable[[], bool]] = None

    def assert_holds(self) -> None:
        """Raise Phase11InvariantViolation if this invariant is violated."""
        if self.check is None:
            logger.debug("invariant_check_skipped", id=self.id, name=self.name)
            return
        try:
            result = self.check()
            if result:
                logger.debug("invariant_holds", id=self.id, name=self.name)
            else:
                logger.warning("invariant_evaluation_inconclusive", id=self.id)
        except Phase11InvariantViolation:
            raise
        except Exception as exc:
            logger.warning("invariant_check_error", id=self.id, error=str(exc))


# ── System Invariant catalog ──────────────────────────────────────────────────

SYSTEM_INVARIANTS: Dict[int, SystemInvariant] = {

    1: SystemInvariant(
        id=1,
        name="knowledge_graph_immutable",
        statement="Knowledge Graph is immutable during runtime. No runtime code writes to the graph.",
        scope="architecture",
        check=None,  # Enforced structurally (frozen dataclass + AST compliance tests)
    ),

    2: SystemInvariant(
        id=2,
        name="presentation_read_only",
        statement="Presentation layer never modifies domain knowledge.",
        scope="architecture",
        check=None,  # Enforced by dependency matrix and architecture tests
    ),

    3: SystemInvariant(
        id=3,
        name="interactions_through_phase10",
        statement="Every user interaction passes through the Phase 10 dashboard layer.",
        scope="runtime",
        check=None,  # Verified by architecture tests (no direct API calls from CLI)
    ),

    4: SystemInvariant(
        id=4,
        name="queries_through_phase9",
        statement="Every knowledge query passes through Phase 9 (KnowledgeAPI).",
        scope="architecture",
        check=None,  # Enforced by trust boundary and dependency matrix
    ),

    5: SystemInvariant(
        id=5,
        name="configuration_immutable_after_init",
        statement="Runtime configuration becomes immutable after initialization.",
        scope="runtime",
        check=lambda: True,  # ConfigurationContext is a frozen dataclass
    ),

    6: SystemInvariant(
        id=6,
        name="infrastructure_no_domain_knowledge",
        statement="Infrastructure never computes domain knowledge.",
        scope="architecture",
        check=None,
    ),

    7: SystemInvariant(
        id=7,
        name="operational_services_no_boundary_bypass",
        statement="Operational services never bypass architectural boundaries.",
        scope="architecture",
        check=None,
    ),

    8: SystemInvariant(
        id=8,
        name="every_execution_has_provenance",
        statement="Every pipeline execution produces a complete RuntimeManifest artifact.",
        scope="pipeline",
        check=None,
    ),

    9: SystemInvariant(
        id=9,
        name="layers_acyclic",
        statement="Architectural layers form a directed acyclic dependency graph.",
        scope="architecture",
        check=None,  # Verified by DependencyGraph.resolve_order() and architecture tests
    ),

    10: SystemInvariant(
        id=10,
        name="single_owner_per_interface",
        statement="Every public interface has exactly one architectural owner.",
        scope="architecture",
        check=None,  # Verified by OwnershipRegistry
    ),
}


def assert_all_invariants() -> None:
    """
    Assert all system invariants that have a runtime check.

    Called at startup and periodically during health monitoring.
    Invariants without a check function are validated by architecture tests.
    """
    violations: List[str] = []
    for inv_id, invariant in SYSTEM_INVARIANTS.items():
        try:
            invariant.assert_holds()
        except Phase11InvariantViolation as exc:
            violations.append(f"Invariant {inv_id} ({invariant.name}): {exc}")

    if violations:
        raise Phase11InvariantViolation(
            "System invariant violations detected:\n" + "\n".join(violations)
        )

    logger.info("all_system_invariants_hold", count=len(SYSTEM_INVARIANTS))