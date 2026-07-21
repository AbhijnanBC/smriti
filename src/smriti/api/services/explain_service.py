"""explain_service.py — Four-level explainability service."""

from __future__ import annotations

import time
import structlog
import dataclasses

from smriti.api.domain.requests import ExplanationRequest
from smriti.api.domain.responses import KnowledgeResponse, make_response_meta
from smriti.api.planner.plan import PhysicalPlan
from smriti.api.store.read_store import ReadStore
from smriti.core.models import ExplainabilityLevel, ExecutionContext
from smriti.exceptions import ClaimNotFoundError

logger = structlog.get_logger(__name__)


class ExplainabilityService:
    """Delivers decision records at 4 explainability levels."""

    def __init__(self, store: ReadStore) -> None:
        self._store = store

    def execute_explanation(
        self, request: ExplanationRequest, plan: PhysicalPlan, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        t0 = time.monotonic()

        rel_record = self._store.fetch_relationship(request.claim_id)
        if rel_record is None:
            raise ClaimNotFoundError(
                f"No reliability record for claim '{request.claim_id}'"
            )

        level = request.explainability_level
        result = self._build_explanation_dto(rel_record, level)

        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=1,
        )
        return KnowledgeResponse(data=result, meta=make_response_meta(ctx))

    def _build_explanation_dto(self, rel_record: dict, level: ExplainabilityLevel) -> dict:
        exp = rel_record.get("explanation", {})
        dto = {
            "claim_id": rel_record["claim_id"],
            "reliability_index": rel_record["reliability_index"],
            "calibration_label": rel_record["calibration_label"],
            "uncertainty_score": rel_record["uncertainty_score"],
            "explainability_level": level.value,
        }
        if level >= ExplainabilityLevel.SUMMARY:
            dto.update({
                "summary": exp.get("summary", ""),
                "dominant_signal": exp.get("dominant_signal", ""),
                "limiting_signal": exp.get("limiting_signal", ""),
            })
        if level >= ExplainabilityLevel.DETAILED:
            dto.update({
                "component_scores": rel_record.get("component_scores", []),
                "signal_vector": rel_record.get("signal_vector", {}),
                "signal_statuses": rel_record.get("signal_statuses", {}),
                "strengths": exp.get("strengths", []),
                "weaknesses": exp.get("weaknesses", []),
            })
        if level >= ExplainabilityLevel.FULL_AUDIT:
            dto.update({
                "recommendations": exp.get("recommendations", []),
                "audit": rel_record.get("audit", {}),
                "policy_snapshot": rel_record.get("policy_snapshot", {}),
                "schema_version": rel_record.get("schema_version", "8.0"),
            })
        return dto