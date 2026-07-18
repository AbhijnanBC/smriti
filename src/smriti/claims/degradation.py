"""
degradation.py — Failure recovery hierarchy for Phase 4.

Responsibility:
    Apply the graceful degradation hierarchy when structured extraction fails.
    NEVER loses information — only loses structure.

Hierarchy (tried in order, first success wins):
    1. ExtractionMode.STRUCTURED    — Full SVO: S + P + O
    2. ExtractionMode.PARTIAL       — Partial SVO: at least S+P or P+O
    3. ExtractionMode.LEXICAL       — No SVO: lexical text span from boundary
    4. ExtractionMode.WHOLE_SENTENCE — Parse failed: entire sentence text

Philosophy:
    Structure is optional.
    Information is mandatory.
    A Claim must ALWAYS be produced from every AssertionCandidate.

Rules:
    ✅ Produce a Claim from every candidate, regardless of extraction success
    ✅ Record warnings for every degradation step
    ✅ Preserve original text unchanged

    ❌ Never discard an assertion
    ❌ Never invent structure to avoid degradation
    ❌ Never elevate ExtractionMode (degradation only goes down)
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.models import ExtractionMode, ClaimWarning
from smriti.claims.models import AnnotatedAssertion, ValidatedAssertion

logger = structlog.get_logger(__name__)


class DegradationHandler:
    """
    Applies the failure degradation hierarchy.
    """

    def apply(self, annotated: AnnotatedAssertion) -> ValidatedAssertion:
        """
        Apply degradation rules and return a ValidatedAssertion.

        Args:
            annotated: AnnotatedAssertion from annotation.py.

        Returns:
            ValidatedAssertion (never None — always something).
        """
        mode = annotated.extraction_mode
        warnings: List[ClaimWarning] = list(annotated.additional_warnings)
        warnings.extend(annotated.structured_candidate.warnings)

        if mode == ExtractionMode.STRUCTURED:
            # Best case — no degradation needed
            logger.debug("extraction mode: STRUCTURED")

        elif mode == ExtractionMode.PARTIAL:
            # Partial structure — acceptable, add warning
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            logger.debug("extraction mode: PARTIAL")

        elif mode == ExtractionMode.LEXICAL:
            # No structure — whole text span preserved
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: LEXICAL (fallback)")

        elif mode == ExtractionMode.WHOLE_SENTENCE:
            # Parser completely failed — sentence text used as-is
            warnings.append(ClaimWarning.CLM_PARSER_FAILURE)
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: WHOLE_SENTENCE (total fallback)")

        return ValidatedAssertion(
            annotated=annotated,
            all_warnings=warnings,
        )