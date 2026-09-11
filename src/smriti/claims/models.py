from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from smriti.core.models import (  # Note: BoundaryReason now in core.models
    BoundaryReason,
    ClaimWarning,
    ExtractionMode,
    Modality,  # NEW import
    SemanticSentence,
    StructuredAssertion,
)

# ── NEW: Internal Split Metadata ──────────────────────────────────────────────


@dataclass
class LinguisticMetadata:
    is_negated: bool
    modality: Modality
    is_quoted: bool


@dataclass
class SemanticMetadata:
    is_conditional: bool
    is_comparative: bool
    is_attributed: bool
    attributed_to: str | None


@dataclass
class ParsedSentence:
    sentence: SemanticSentence
    spacy_doc: Any | None
    parse_ok: bool
    parse_error: str | None = None


@dataclass
class AssertionCandidate:
    text: str
    span_start: int
    span_end: int
    source: ParsedSentence
    boundary_reason: BoundaryReason  # now Enum
    # confidence removed (Priority 2)
    # NEW: exact source-token provenance (Part 2 — multi-span claim provenance).
    # source_char_spans are (start, end) character-offset pairs into
    # source.sentence.text — one pair per CONTIGUOUS run of tokens actually
    # used to build `text`. source_token_ids are the corresponding spaCy
    # Token.i indices, in sentence order. Both default to empty tuples for
    # candidates built without token-level tracking (e.g. legacy/manual
    # construction in tests) — builder.py falls back to the whole-sentence
    # span in that case.
    source_char_spans: tuple = field(default_factory=tuple)
    source_token_ids: tuple = field(default_factory=tuple)


@dataclass
class StructuredAssertionCandidate:
    candidate: AssertionCandidate
    structured_assertion: StructuredAssertion | None
    extraction_mode: ExtractionMode
    warnings: list[ClaimWarning] = field(default_factory=list)


@dataclass
class AnnotatedAssertion:
    structured_candidate: StructuredAssertionCandidate
    linguistic_metadata: LinguisticMetadata  # <-- REPLACED
    semantic_metadata: SemanticMetadata  # <-- REPLACED
    additional_warnings: list[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.structured_candidate.candidate.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.structured_candidate.extraction_mode


@dataclass
class ValidatedAssertion:
    annotated: AnnotatedAssertion
    all_warnings: list[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.annotated.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.annotated.extraction_mode

    @property
    def structured_assertion(self) -> StructuredAssertion | None:
        return self.annotated.structured_candidate.structured_assertion

    @property
    def linguistic_metadata(self) -> LinguisticMetadata:  # <-- ADDED
        return self.annotated.linguistic_metadata

    @property
    def semantic_metadata(self) -> SemanticMetadata:  # <-- ADDED
        return self.annotated.semantic_metadata

    @property
    def source_sentence(self) -> SemanticSentence:
        return self.annotated.structured_candidate.candidate.source.sentence

    @property
    def span_start(self) -> int:
        return self.annotated.structured_candidate.candidate.span_start

    @property
    def source_char_spans(self) -> tuple:
        return self.annotated.structured_candidate.candidate.source_char_spans

    @property
    def source_token_ids(self) -> tuple:
        return self.annotated.structured_candidate.candidate.source_token_ids

    @property
    def reconstruction_rule(self) -> str:
        return self.annotated.structured_candidate.candidate.boundary_reason.value
