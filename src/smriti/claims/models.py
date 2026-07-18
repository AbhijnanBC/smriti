from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any

from smriti.core.models import (           # Note: BoundaryReason now in core.models
    SemanticSentence,
    StructuredAssertion,
    AssertionMetadata,
    ExtractionMode,
    ClaimWarning,
    BoundaryReason, 
    Modality,                  # NEW import
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
    attributed_to: Optional[str]


@dataclass
class ParsedSentence:
    sentence: SemanticSentence
    spacy_doc: Optional[Any]
    parse_ok: bool
    parse_error: Optional[str] = None


@dataclass
class AssertionCandidate:
    text: str
    span_start: int
    span_end: int
    source: ParsedSentence
    boundary_reason: BoundaryReason   # now Enum
    # confidence removed (Priority 2)


@dataclass
class StructuredAssertionCandidate:
    candidate: AssertionCandidate
    structured_assertion: Optional[StructuredAssertion]
    extraction_mode: ExtractionMode
    warnings: List[ClaimWarning] = field(default_factory=list)


@dataclass
class AnnotatedAssertion:
    structured_candidate: StructuredAssertionCandidate
    linguistic_metadata: LinguisticMetadata  # <-- REPLACED
    semantic_metadata: SemanticMetadata      # <-- REPLACED
    additional_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.structured_candidate.candidate.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.structured_candidate.extraction_mode


@dataclass
class ValidatedAssertion:
    annotated: AnnotatedAssertion
    all_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.annotated.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.annotated.extraction_mode

    @property
    def structured_assertion(self) -> Optional[StructuredAssertion]:
        return self.annotated.structured_candidate.structured_assertion

    @property
    def linguistic_metadata(self) -> LinguisticMetadata:   # <-- ADDED
        return self.annotated.linguistic_metadata

    @property
    def semantic_metadata(self) -> SemanticMetadata:       # <-- ADDED
        return self.annotated.semantic_metadata

    @property
    def source_sentence(self) -> SemanticSentence:
        return self.annotated.structured_candidate.candidate.source.sentence

    @property
    def span_start(self) -> int:
        return self.annotated.structured_candidate.candidate.span_start