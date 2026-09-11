"""
views/claim_view_builder.py — ClaimViewBuilder.

RECTIFIED (P0-5): View construction is now separated from DTO mapping.
DTOMapper ONLY does View → DTO.
ClaimViewBuilder constructs ClaimView from raw records.

Raw Record (from ReadStore)
    ↓
ClaimViewBuilder.build()
    ↓
ClaimView (internal domain object)
    ↓
DTOMapper.claim_to_dto()
    ↓
ClaimDTO (external DTO)
"""

from __future__ import annotations

from typing import Any

from smriti.api.domain.views import ClaimView


class ClaimViewBuilder:
    """Constructs ClaimView from raw ReadStore records."""

    def build(
        self,
        record: dict[str, Any],
        rel_record: dict[str, Any] | None = None,
    ) -> ClaimView:
        """Build a ClaimView from raw claim + reliability records."""
        rel = rel_record or {}
        exp = rel.get("explanation", {})
        comp_scores = rel.get("component_scores", [])
        audit = rel.get("audit", {})
        sv = rel.get("signal_vector", {})

        return ClaimView(
            claim_id=record.get("claim_id", ""),
            claim_text=record.get("claim_text", ""),
            context=record.get("context", ""),
            document_id=record.get("document_id", ""),
            source_path=record.get("source_path", ""),
            partition_id=record.get("partition_id"),
            semantic_role=record.get("semantic_role", "unclassified"),
            reliability_index=record.get("reliability_index", 0.0),
            uncertainty_score=record.get("uncertainty_score", 100.0),
            evidence_completeness=record.get("evidence_completeness", 0.0),
            calibration_label=record.get("calibration_label", "very_low"),
            policy_version=record.get("policy_version", ""),
            degree=record.get("degree", 0),
            in_degree=record.get("in_degree", 0),
            centrality=record.get("centrality", 0.0),
            is_hub=record.get("is_hub", False),
            is_bridge=record.get("is_bridge", False),
            support_count=record.get("support_count", 0),
            weighted_confidence=record.get("weighted_confidence", 0.0),
            temporal_status=record.get("temporal_status", "unknown"),
            temporal_confidence=record.get("temporal_confidence", 0.0),
            time_delta_days=record.get("time_delta_days"),
            evidence_strength=sv.get("evidence_strength", 0.0),
            evidence_independence=sv.get("evidence_independence", 0.0),
            source_diversity=sv.get("source_diversity", 0.0),
            topology_strength=sv.get("topology_strength", 0.0),
            conflict_pressure=sv.get("conflict_pressure", 0.0),
            temporal_stability=sv.get("temporal_stability", 0.0),
            component_scores=tuple(comp_scores),
            explanation_summary=exp.get("summary", ""),
            explanation_dominant_signal=exp.get("dominant_signal", ""),
            explanation_limiting_signal=exp.get("limiting_signal", ""),
            explanation_strengths=tuple(exp.get("strengths", [])),
            explanation_weaknesses=tuple(exp.get("weaknesses", [])),
            explanation_recommendations=tuple(exp.get("recommendations", [])),
            audit_policy_version=audit.get("policy_version", ""),
            audit_fusion_algorithm=audit.get("fusion_algorithm", ""),
            audit_run_id=audit.get("computed_at_run_id", ""),
        )
