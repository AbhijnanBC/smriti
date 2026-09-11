"""
statistics.py — Phase 4 execution statistics collector.

Responsibility:
    Collect operational metrics during Phase 4 processing.
    Statistics are DIAGNOSTIC ONLY — they never affect execution.

Design:
    This module observes. It never influences.
    Think of it as a telemetry layer.
"""

from __future__ import annotations

from smriti.core.models import AssertionType, ClaimWarning, ExtractionMode, Phase4Stats


class Phase4StatsCollector:
    """
    Mutable collector that accumulates Phase 4 statistics.
    Call finalize() to get the immutable Phase4Stats result.
    """

    def __init__(self) -> None:
        self._sentences = 0
        self._claims = 0
        self._structured = 0
        self._partial = 0
        self._lexical = 0
        self._whole_sentence = 0
        self._parser_failures = 0
        self._boundary_splits = 0
        self._negated = 0
        self._modal = 0
        self._attributed = 0
        self._discarded_non_assertions = 0
        self._discarded_by_type: dict[str, int] = {}
        self._warnings: list[ClaimWarning] = []

    def record_sentence_processed(self) -> None:
        self._sentences += 1

    def record_parser_failure(self) -> None:
        self._parser_failures += 1

    def record_classification(self, assertion_type: AssertionType) -> None:
        """
        Record the outcome of the Stage 1.5 assertion-type classification.
        Only non-DECLARATIVE_ASSERTION classifications count as "discarded" —
        DECLARATIVE_ASSERTION sentences proceed to Claim construction and are
        counted separately via record_claim().
        """
        if assertion_type == AssertionType.DECLARATIVE_ASSERTION:
            return
        self._discarded_non_assertions += 1
        key = assertion_type.value
        self._discarded_by_type[key] = self._discarded_by_type.get(key, 0) + 1

    def record_boundary_split(self, count: int) -> None:
        """Record that a sentence was split into `count` claims."""
        if count > 1:
            self._boundary_splits += 1

    def record_claim(
        self, mode: ExtractionMode, is_negated: bool, is_modal: bool, is_attributed: bool
    ) -> None:
        self._claims += 1
        if mode == ExtractionMode.STRUCTURED:
            self._structured += 1
        elif mode == ExtractionMode.PARTIAL:
            self._partial += 1
        elif mode == ExtractionMode.LEXICAL:
            self._lexical += 1
        elif mode == ExtractionMode.WHOLE_SENTENCE:
            self._whole_sentence += 1

        if is_negated:
            self._negated += 1
        if is_modal:
            self._modal += 1
        if is_attributed:
            self._attributed += 1

    def record_warnings(self, warnings: list[ClaimWarning]) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase4Stats:
        return Phase4Stats(
            total_sentences_processed=self._sentences,
            total_claims_produced=self._claims,
            structured_claims=self._structured,
            partial_claims=self._partial,
            lexical_claims=self._lexical,
            whole_sentence_claims=self._whole_sentence,
            parser_failures=self._parser_failures,
            boundary_splits=self._boundary_splits,
            negated_claims=self._negated,
            modal_claims=self._modal,
            attributed_claims=self._attributed,
            total_discarded_non_assertions=self._discarded_non_assertions,
            discarded_by_type=dict(self._discarded_by_type),
            warnings=tuple(self._warnings),
        )
