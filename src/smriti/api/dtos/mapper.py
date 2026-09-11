"""
mapper.py — DTOMapper: converts KnowledgeViews → DTOs.

RECTIFIED (P0-5): DTOMapper ONLY maps View → DTO.
It NEVER constructs views. raw_record_to_claim_view() has been REMOVED.
View construction is now ClaimViewBuilder.build().

RECTIFIED (ProjectionPolicy): Uses PROJECTION_POLICY_MAP to define
exactly which fields are allowed per projection level, centralising
all projection rules in predicates.py.
"""

from __future__ import annotations

from typing import Any

import structlog
from smriti.api.domain.predicates import PROJECTION_POLICY_MAP, ProjectionPolicy
from smriti.api.domain.views import (
    ClaimView,
)
from smriti.api.dtos.claim_dto import ClaimDTO, ComponentScoreDTO
from smriti.api.dtos.schema_registry import schema_registry
from smriti.core.models import ProjectionLevel

logger = structlog.get_logger(__name__)


class DTOMapper:
    """
    Converts KnowledgeView objects → DTOs.
    Instantiate once per KnowledgeAPI instance.
    NEVER constructs views.
    """

    def claim_to_dto(self, view: ClaimView, level: ProjectionLevel) -> ClaimDTO:
        """
        Convert ClaimView → ClaimDTO with field projection using ProjectionPolicy.

        The policy defines exactly which fields are allowed to leave the API.
        """
        policy = PROJECTION_POLICY_MAP[level]
        schema_ver = schema_registry.get_version_string("ClaimDTO")

        # ── Build the complete dictionary of all possible fields ──────────────
        all_fields: dict[str, Any] = {
            # Always included
            "claim_id": view.claim_id,
            "claim_text": view.claim_text,
            "context": view.context,
            "reliability_index": round(view.reliability_index, 2),
            "calibration_label": view.calibration_label,
            "uncertainty_score": round(view.uncertainty_score, 2),
            "schema_version": schema_ver,
            # STANDARD+
            "document_id": view.document_id,
            "source_path": view.source_path,
            "partition_id": view.partition_id,
            "semantic_role": view.semantic_role,
            "degree": view.degree,
            "centrality": round(view.centrality, 4),
            "support_count": view.support_count,
            # DETAILED+
            "temporal_status": view.temporal_status,
            "evidence_strength": round(view.evidence_strength, 3),
            "conflict_pressure": round(view.conflict_pressure, 3),
            "evidence_completeness": round(view.evidence_completeness, 3),
            # EXPLAINABILITY+
            "explanation_summary": view.explanation_summary,
            "dominant_signal": view.explanation_dominant_signal,
            "limiting_signal": view.explanation_limiting_signal,
            "recommendations": list(view.explanation_recommendations),
            # FULL_AUDIT
            "policy_version": view.audit_policy_version,
            "audit_run_id": view.audit_run_id,
        }

        # ── Build component_scores (nested DTO) ──────────────────────────────
        if view.component_scores:
            all_fields["component_scores"] = [
                ComponentScoreDTO(
                    signal_name=c.get("signal_name", ""),
                    contribution=round(c.get("contribution", 0.0), 3),
                    direction=c.get("direction", "positive"),
                    explanation=c.get("explanation", ""),
                )
                for c in view.component_scores
            ]
        else:
            all_fields["component_scores"] = []

        # ── Filter fields using the projection policy ─────────────────────────
        filtered_fields = self._apply_projection_policy(all_fields, policy)

        return ClaimDTO(**filtered_fields)

    def _apply_projection_policy(
        self, fields: dict[str, Any], policy: ProjectionPolicy
    ) -> dict[str, Any]:
        """
        Apply the ProjectionPolicy to filter fields.

        - If allowed_fields is non-empty, keep only those fields.
        - If excluded_fields is non-empty, remove those fields.
        - Allowed takes precedence over excluded.
        """
        if policy.allowed_fields:
            # Keep only allowed fields
            return {k: v for k, v in fields.items() if k in policy.allowed_fields}

        # If no allowed_fields, use all fields (but exclude if needed)
        result = dict(fields)
        for ex in policy.excluded_fields:
            result.pop(ex, None)
        return result
