"""predicates.py — Filter predicates, sort specs, pagination, projections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, List, Optional
from smriti.core.models import SortOrder, ProjectionLevel, PredicateOperator


@dataclass(frozen=True)
class Predicate:
    """
    A single filter condition.
    Example: Predicate("reliability_index", GTE, 80.0)
    """
    field: str
    operator: PredicateOperator
    value: Any

    def matches(self, field_value: Any) -> bool:
        try:
            if self.operator == PredicateOperator.EQ:   return field_value == self.value
            if self.operator == PredicateOperator.NEQ:  return field_value != self.value
            if self.operator == PredicateOperator.GT:   return field_value > self.value
            if self.operator == PredicateOperator.GTE:  return field_value >= self.value
            if self.operator == PredicateOperator.LT:   return field_value < self.value
            if self.operator == PredicateOperator.LTE:  return field_value <= self.value
            if self.operator == PredicateOperator.IN:   return field_value in self.value
        except TypeError:
            return False
        return False

    def canonical_key(self) -> str:
        """Canonical string for normalization — enables order-independent plan_ids."""
        return f"{self.field}:{self.operator.value}:{self.value}"


@dataclass(frozen=True)
class SortSpec:
    """
    Deterministic sort specification.
    Always include a tiebreaker (claim_id ASC) to guarantee determinism.
    """
    field: str
    order: SortOrder = SortOrder.DESC
    tiebreaker_field: str = "claim_id"
    tiebreaker_order: SortOrder = SortOrder.ASC


@dataclass(frozen=True)
class Pagination:
    """Pagination parameters. Required for all collection responses."""
    limit: int = 50
    offset: int = 0

    def __post_init__(self):
        object.__setattr__(self, "limit", max(1, min(self.limit, 1000)))
        object.__setattr__(self, "offset", max(0, self.offset))


@dataclass(frozen=True)
class Projection:
    """Which projection level the client is requesting."""
    level: ProjectionLevel = ProjectionLevel.STANDARD


# ── Projection Policy ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProjectionPolicy:
    """
    Defines exactly what data is allowed to leave the API.
    Used by DTOMapper to filter fields dynamically.
    """
    allowed_fields: FrozenSet[str]
    excluded_fields: FrozenSet[str]
    explainability_visibility: bool
    audit_visibility: bool


# ── Predefined policies for each ProjectionLevel ────────────────────────────

SUMMARY_POLICY = ProjectionPolicy(
    allowed_fields=frozenset([
        "claim_id", "claim_text", "reliability_index", "calibration_label",
        "uncertainty_score"
    ]),
    excluded_fields=frozenset(),
    explainability_visibility=False,
    audit_visibility=False,
)

STANDARD_POLICY = ProjectionPolicy(
    allowed_fields=frozenset([
        "claim_id", "claim_text", "reliability_index", "calibration_label",
        "uncertainty_score", "document_id", "source_path", "partition_id",
        "semantic_role", "degree", "centrality", "support_count"
    ]),
    excluded_fields=frozenset(),
    explainability_visibility=False,
    audit_visibility=False,
)

DETAILED_POLICY = ProjectionPolicy(
    allowed_fields=frozenset([
        "claim_id", "claim_text", "reliability_index", "calibration_label",
        "uncertainty_score", "document_id", "source_path", "partition_id",
        "semantic_role", "degree", "centrality", "support_count",
        "temporal_status", "evidence_strength", "conflict_pressure",
        "evidence_completeness"
    ]),
    excluded_fields=frozenset(),
    explainability_visibility=False,
    audit_visibility=False,
)

EXPLAINABILITY_POLICY = ProjectionPolicy(
    allowed_fields=frozenset([
        "claim_id", "claim_text", "reliability_index", "calibration_label",
        "uncertainty_score", "document_id", "source_path", "partition_id",
        "semantic_role", "degree", "centrality", "support_count",
        "temporal_status", "evidence_strength", "conflict_pressure",
        "evidence_completeness",
        "explanation_summary", "dominant_signal", "limiting_signal",
        "component_scores", "recommendations"
    ]),
    excluded_fields=frozenset(),
    explainability_visibility=True,
    audit_visibility=False,
)

FULL_AUDIT_POLICY = ProjectionPolicy(
    allowed_fields=frozenset([
        "claim_id", "claim_text", "reliability_index", "calibration_label",
        "uncertainty_score", "document_id", "source_path", "partition_id",
        "semantic_role", "degree", "centrality", "support_count",
        "temporal_status", "evidence_strength", "conflict_pressure",
        "evidence_completeness",
        "explanation_summary", "dominant_signal", "limiting_signal",
        "component_scores", "recommendations",
        "policy_version", "audit_run_id"
    ]),
    excluded_fields=frozenset(),
    explainability_visibility=True,
    audit_visibility=True,
)


# ── Map from ProjectionLevel to ProjectionPolicy ─────────────────────────────

PROJECTION_POLICY_MAP: dict[ProjectionLevel, ProjectionPolicy] = {
    ProjectionLevel.SUMMARY:         SUMMARY_POLICY,
    ProjectionLevel.STANDARD:        STANDARD_POLICY,
    ProjectionLevel.DETAILED:        DETAILED_POLICY,
    ProjectionLevel.EXPLAINABILITY:  EXPLAINABILITY_POLICY,
    ProjectionLevel.FULL_AUDIT:      FULL_AUDIT_POLICY,
}