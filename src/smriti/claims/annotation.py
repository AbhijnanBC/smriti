"""
annotation.py — Semantic metadata annotation for Phase 4.

Responsibility:
    Add semantic metadata to a StructuredAssertionCandidate.
    Detect: negation, modality, attribution, conditional, comparison, quotation.

Rules:
    ✅ Annotate text with semantic flags
    ✅ Record metadata accurately

    ❌ NEVER modify text
    ❌ NEVER rewrite claims
    ❌ NEVER perform semantic inference
    ❌ NEVER change ExtractionMode

The text remains exactly as the author wrote it.
Metadata is additive, never transformative.
"""

from __future__ import annotations

import structlog

from smriti.claims.models import (
    AnnotatedAssertion,
    LinguisticMetadata,
    SemanticMetadata,
    StructuredAssertionCandidate,
)
from smriti.claims.rules import (
    ATTRIBUTION_VERBS,
    COMPARISON_MARKERS,
    MODALITY_IMPOSSIBLE,
    MODALITY_POSSIBLE,
    MODALITY_PROBABLE,
    MODALITY_REQUIRED,
    NEGATION_MARKERS,
)
from smriti.core.models import Modality

logger = structlog.get_logger(__name__)


class AssertionAnnotator:
    """
    Annotates assertions with semantic metadata.
    """

    def annotate(self, candidate: StructuredAssertionCandidate) -> AnnotatedAssertion:
        """
        Annotate an assertion with semantic metadata.

        Args:
            candidate: StructuredAssertionCandidate from structure.py.

        Returns:
            AnnotatedAssertion with metadata populated.
        """
        parsed = candidate.candidate.source
        text = candidate.candidate.text.lower()

        # ── Linguistic metadata ──────────────────────────────────────────────────
        is_negated = self._detect_negation(parsed, text)
        modality = self._detect_modality(parsed, text)
        is_quoted = self._detect_quotation(text)

        linguistic = LinguisticMetadata(
            is_negated=is_negated,
            modality=modality,
            is_quoted=is_quoted,
        )

        # ── Semantic metadata ────────────────────────────────────────────────────
        is_conditional = self._detect_conditional(parsed, text)
        is_comparative = self._detect_comparative(text)
        is_attributed, attributed_to = self._detect_attribution(parsed)

        semantic = SemanticMetadata(
            is_conditional=is_conditional,
            is_comparative=is_comparative,
            is_attributed=is_attributed,
            attributed_to=attributed_to,
        )

        logger.debug(
            "assertion annotated",
            negated=is_negated,
            modality=modality.value,
            conditional=is_conditional,
            attributed=is_attributed,
        )

        return AnnotatedAssertion(
            structured_candidate=candidate,
            linguistic_metadata=linguistic,
            semantic_metadata=semantic,
        )

    def _detect_negation(self, parsed, text_lower: str) -> bool:
        """Detect negation via spaCy dep_ or keyword scan."""
        # spaCy negation detection (more accurate)
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ == "neg":
                    return True

        # Keyword fallback
        words = set(text_lower.split())
        return bool(words & NEGATION_MARKERS)

    def _detect_modality(self, parsed, text_lower: str) -> Modality:
        """Detect modality from auxiliary verbs."""
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ in ("aux", "auxpass"):
                    lemma = token.lemma_.lower()
                    if lemma in MODALITY_IMPOSSIBLE:
                        return Modality.IMPOSSIBLE
                    if lemma in MODALITY_REQUIRED:
                        return Modality.REQUIRED
                    if lemma in MODALITY_PROBABLE:
                        return Modality.PROBABLE
                    if lemma in MODALITY_POSSIBLE:
                        return Modality.POSSIBLE

        # Keyword fallback
        words = set(text_lower.split())
        if words & MODALITY_IMPOSSIBLE:
            return Modality.IMPOSSIBLE
        if words & MODALITY_REQUIRED:
            return Modality.REQUIRED
        if words & MODALITY_PROBABLE:
            return Modality.PROBABLE
        if words & MODALITY_POSSIBLE:
            return Modality.POSSIBLE

        return Modality.CERTAIN

    def _detect_conditional(self, parsed, text_lower: str) -> bool:
        """Detect conditional clauses (if/unless/when)."""
        conditional_markers = {"if", "unless", "when", "whenever", "provided", "assuming"}
        words = set(text_lower.split())
        return bool(words & conditional_markers)

    def _detect_comparative(self, text_lower: str) -> bool:
        """Detect comparative claims ("faster than", "better than")."""
        words = set(text_lower.split())
        return bool(words & COMPARISON_MARKERS)

    def _detect_attribution(self, parsed) -> tuple:
        """
        Detect attribution: "X says Y" / "According to X, Y".

        Returns:
            (is_attributed: bool, attributed_to: Optional[str])
        """
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return False, None

        for token in parsed.spacy_doc:
            if token.lemma_.lower() in ATTRIBUTION_VERBS:
                # Find the subject of the attribution verb
                subjects = [t for t in token.children if t.dep_ in ("nsubj", "nsubjpass")]
                if subjects:
                    attributed_to = subjects[0].text
                    return True, attributed_to

        return False, None

    def _detect_quotation(self, text_lower: str) -> bool:
        """Detect direct quotations (text contains quotes)."""
        return '"' in text_lower or "'" in text_lower
