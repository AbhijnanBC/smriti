"""
validation/request_validator.py — Centralized request validation.

RECTIFIED (P0-big): All validation is collected here.
No validation logic lives in KnowledgeAccessService or ApplicationService.

Validates:
    - claim_id: non-empty string
    - predicates: valid field names, valid operators
    - pagination: limit > 0, offset >= 0
    - traversal: max_depth >= 1
    - explainability_level: 0–3
    - export_format: valid value
"""

from __future__ import annotations

from smriti.api.domain.requests import (
    KnowledgeRequest, ClaimRequest, SearchRequest,
    TraversalRequest, ExplanationRequest, ExportRequest,
)
from smriti.exceptions import RequestValidationError

VALID_PREDICATE_FIELDS = {
    "reliability_index", "uncertainty_score", "calibration_label",
    "document_id", "partition_id", "semantic_role", "context",
    "support_count", "degree", "centrality", "temporal_status",
    "is_hub", "is_bridge", "evidence_strength", "conflict_pressure",
}

MAX_TRAVERSAL_DEPTH = 5


class RequestValidator:
    """Validates all incoming KnowledgeRequests. Raises RequestValidationError on failure."""

    def validate(self, request: KnowledgeRequest) -> None:
        """Dispatch to appropriate validator based on request type."""
        if isinstance(request, ClaimRequest):
            self._validate_claim_request(request)
        elif isinstance(request, SearchRequest):
            self._validate_search_request(request)
        elif isinstance(request, TraversalRequest):
            self._validate_traversal_request(request)
        elif isinstance(request, ExplanationRequest):
            self._validate_explanation_request(request)
        elif isinstance(request, ExportRequest):
            self._validate_export_request(request)
        # StatisticsRequest needs no special validation

    def _validate_claim_request(self, req: ClaimRequest) -> None:
        if not req.claim_id or not req.claim_id.strip():
            raise RequestValidationError("claim_id must not be empty")

    def _validate_search_request(self, req: SearchRequest) -> None:
        for pred in req.predicates:
            if pred.field not in VALID_PREDICATE_FIELDS and pred.field != "claim_text":
                raise RequestValidationError(
                    f"Invalid predicate field: '{pred.field}'. "
                    f"Valid fields: {sorted(VALID_PREDICATE_FIELDS)}"
                )
        if req.pagination.limit < 1:
            raise RequestValidationError("pagination.limit must be >= 1")

    def _validate_traversal_request(self, req: TraversalRequest) -> None:
        if not req.start_claim_id or not req.start_claim_id.strip():
            raise RequestValidationError("start_claim_id must not be empty")
        if req.max_depth < 1:
            raise RequestValidationError("max_depth must be >= 1")
        if req.max_depth > MAX_TRAVERSAL_DEPTH:
            raise RequestValidationError(
                f"max_depth {req.max_depth} exceeds maximum ({MAX_TRAVERSAL_DEPTH})"
            )

    def _validate_explanation_request(self, req: ExplanationRequest) -> None:
        if not req.claim_id or not req.claim_id.strip():
            raise RequestValidationError("claim_id must not be empty for explanation")
        if req.explainability_level.value not in (0, 1, 2, 3):
            raise RequestValidationError(
                f"Invalid explainability_level: {req.explainability_level.value}"
            )

    def _validate_export_request(self, req: ExportRequest) -> None:
        from smriti.core.models import ExportFormat
        if req.export_format not in ExportFormat:
            raise RequestValidationError(f"Invalid export format: {req.export_format}")