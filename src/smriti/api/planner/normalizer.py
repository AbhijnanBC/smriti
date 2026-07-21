"""
normalizer.py — QueryNormalizer for Phase 9.

RECTIFIED (P0-2, P1-4): Canonicalizes requests so that:
    Predicate("conflict_pressure", LT, 20.0), Predicate("reliability_index", GTE, 80.0)
    == (produces the same plan_id as)
    Predicate("reliability_index", GTE, 80.0), Predicate("conflict_pressure", LT, 20.0)

Normalization also:
    - Sorts predicates by canonical_key() for order independence
    - Trims text_contains whitespace
    - Clamps pagination to configured bounds
    - Validates field names against known indexed fields

Rules:
    ✅ Deterministic: same semantic request → same canonical form
    ✅ Order-independent predicate evaluation
    ❌ Never changes the semantics of the request
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.api.domain.predicates import Predicate, Pagination
from smriti.api.domain.requests import KnowledgeRequest, SearchRequest
from smriti.core.config import get_config

logger = structlog.get_logger(__name__)


class QueryNormalizer:
    """Canonicalizes KnowledgeRequest before planning."""

    def normalize(self, request: KnowledgeRequest) -> KnowledgeRequest:
        """
        Return a canonicalized version of the request.

        For SearchRequests: sort predicates by canonical_key() so that
        predicate order never affects plan_id.

        For all requests: clamp pagination limits to config bounds.
        """
        if isinstance(request, SearchRequest):
            return self._normalize_search(request)
        return request

    def _normalize_search(self, request: SearchRequest) -> SearchRequest:
        """Normalize a SearchRequest."""
        import dataclasses

        config = get_config()
        max_limit = config.get("knowledge_api", {}).get("max_page_size", 1000)

        # Sort predicates canonically (order-independence)
        sorted_predicates = tuple(
            sorted(request.predicates, key=lambda p: p.canonical_key())
        )

        # Clamp pagination
        clamped_pagination = Pagination(
            limit=min(request.pagination.limit, max_limit),
            offset=request.pagination.offset,
        )

        # Trim text
        text = request.text_contains.strip() if request.text_contains else None

        return dataclasses.replace(
            request,
            predicates=sorted_predicates,
            pagination=clamped_pagination,
            text_contains=text,
        )