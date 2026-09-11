"""
Data models for SMRITI.
Define once, use everywhere.
These are the contracts between phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from smriti.core.config import get_config

# ── Enums ────────────────────────────────────────────────────────────────────


class FileFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class ContradictionType(str, Enum):
    DIRECT_REVERSAL = "direct_reversal"
    REFINEMENT = "refinement"
    STRATEGY_SHIFT = "strategy_shift"
    DEFINITION_CHANGE = "definition_change"


class ExtractionMethod(str, Enum):
    """Which extractor was used to produce raw_text."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class WarningCode(str, Enum):
    """Strict taxonomy of extraction and normalization warnings."""

    UNICODE_NORMALIZED = "unicode_normalized"
    BOM_REMOVED = "bom_removed"
    LINE_ENDINGS_NORMALIZED = "line_endings_normalized"
    TRAILING_WHITESPACE_REMOVED = "trailing_whitespace_removed"
    CONTROL_CHARS_REMOVED = "control_chars_removed"
    BLANK_LINES_COLLAPSED = "blank_lines_collapsed"
    MIXED_LINE_ENDINGS = "mixed_line_endings"
    NULL_BYTES_REMOVED = "null_bytes_removed"
    ENCODING_FALLBACK = "encoding_fallback"
    PAGE_LIMIT_REACHED = "page_limit_reached"
    PAGE_EXTRACTION_FAILED = "page_extraction_failed"
    EMPTY_PDF_PAGE = "empty_pdf_page"
    NO_EXTRACTABLE_TEXT = "no_extractable_text"
    TEXT_TRUNCATED = "text_truncated"


# ── Phase 3 Warning Codes ────────────────────────────────────────────────────


class SegmentationWarning(str, Enum):
    """Warning codes specific to Phase 3 semantic sentence construction."""

    SEG_EMPTY_SENTENCE_DISCARDED = "SEG001"  # Empty string after strip
    SEG_VERY_LONG_SENTENCE = "SEG002"  # Exceeds max_sentence_chars
    SEG_UNKNOWN_STRUCTURE = "SEG003"  # Structural element not recognised
    SEG_MALFORMED_TABLE = "SEG004"  # Table could not be parsed
    SEG_CODE_BLOCK_SKIPPED = "SEG005"  # Code block skipped (V1)
    CTX_STACK_IMBALANCE = "CTX001"  # Context stack depth mismatch
    VAL_DUPLICATE_SENTENCE_ID = "VAL001"  # Two sentences share an ID (fatal)
    VAL_INVALID_POSITION_ORDER = "VAL002"  # Non-monotonic positions (fatal)
    VAL_INVALID_CONTEXT = "VAL003"  # Context string malformed


# ── Phase 4 Warning Codes ─────────────────────────────────────────────────────


class ClaimWarning(str, Enum):
    """Warning codes specific to Phase 4 claim construction."""

    CLM_PARSER_FAILURE = "CLM001"
    CLM_BOUNDARY_AMBIGUITY = "CLM002"
    CLM_STRUCTURE_UNAVAILABLE = "CLM003"
    CLM_FALLBACK_ACTIVATED = "CLM004"
    CLM_EMPTY_ASSERTION = "CLM005"
    CLM_DUPLICATE_CLAIM_ID = "CLM006"  # Fatal if inconsistent
    CLM_INVALID_PROVENANCE = "CLM007"
    CLM_VALIDATION_FAILURE = "CLM008"
    CLM_EXCEEDED_MAX_CLAIMS = "CLM009"
    CLM_UNSUPPORTED_SYNTAX = "CLM010"


class ExtractionMode(str, Enum):
    STRUCTURED = "structured"
    PARTIAL = "partial"
    LEXICAL = "lexical"
    WHOLE_SENTENCE = "whole_sentence"


class Modality(str, Enum):
    CERTAIN = "certain"
    POSSIBLE = "possible"
    PROBABLE = "probable"
    IMPOSSIBLE = "impossible"
    REQUIRED = "required"
    UNKNOWN = "unknown"


class BoundaryReason(str, Enum):
    """Enum for deterministic boundary detection reasons."""

    SINGLE_ASSERTION = "single_assertion"
    COORDINATED_PREDICATE = "coordinated_predicate"
    INDEPENDENT_CLAUSE = "independent_clause"
    PARSE_FAILED = "parse_failed"
    CONDITIONAL_SPLIT = "conditional_split"  # reserved
    RELATIVE_CLAUSE = "relative_clause"
    COORDINATION = "coordination"


class AssertionType(str, Enum):
    """
    Grammatical/structural classification of a candidate span, assigned by
    claims.classifier.AssertionClassifier BEFORE any Claim object is built.

    Only DECLARATIVE_ASSERTION proceeds into the claim-construction pipeline
    (boundary detection → structure extraction → annotation → degradation →
    Claim). Every other type is recorded as a DiscardedCandidate instead, so
    nothing about the source document is ever silently dropped — it is simply
    routed away from the knowledge graph.

    DECLARATIVE_ASSERTION   -- a real declarative statement asserting something
                               (may be full SVO, or degrade to partial/lexical/
                               whole-sentence — completeness is orthogonal to
                               being an assertion at all).
    PROCEDURAL_INSTRUCTION  -- an imperative/instructional step
                               ("Heat the oil in a pan.").
    QUESTION                -- interrogative.
    HEADING                 -- a markdown heading or heading-like fragment
                               with no verb (leaked "## X", bare "**X**", or a
                               short bare title-case noun phrase).
    METADATA                -- bibliographic/attribution lines
                               ("**Source:** X", "**Contradicts:** Y").
    LIST_ITEM                -- a bare noun-phrase list item with no assertion
                               ("Coconut oil.", "2 tbsp ghee").
    TABLE_CELL               -- content that originated inside a markdown
                               table cell (origin_block_type == "table").
    FRAGMENT                 -- garbled/truncated/incoherent text with no
                               coherent assertion (including unparseable text).
    CODE                     -- code block content.
    QUOTE                    -- blockquote content.
    """

    DECLARATIVE_ASSERTION = "declarative_assertion"
    PROCEDURAL_INSTRUCTION = "procedural_instruction"
    QUESTION = "question"
    HEADING = "heading"
    METADATA = "metadata"
    LIST_ITEM = "list_item"
    TABLE_CELL = "table_cell"
    FRAGMENT = "fragment"
    CODE = "code"
    QUOTE = "quote"


@dataclass(frozen=True)
class DiscardedCandidate:
    """
    A SemanticSentence classified as something other than DECLARATIVE_ASSERTION,
    and therefore never turned into a Claim.

    This is the audit trail that keeps Phase 4 lossless: every sentence that
    is filtered out of the knowledge graph is still recorded here, in full,
    with the reason it was excluded — so the source document remains fully
    recoverable even though only genuine assertions reach downstream phases.

    Fields:
        sentence_id:        The originating SemanticSentence's ID.
        document_id:        doc_id of the source Document.
        text:               The exact sentence text (unmodified).
        assertion_type:      The AssertionType this candidate was classified as.
        origin_block_type:  BlockType string from Phase 3 (e.g. "table", "heading").
        reason:             Short machine-readable reason code from the classifier
                            (e.g. "regex_bold_label_colon", "imperative_base_form_verb").
        source_path:        Path to the original file (for traceability).
        context:            Heading path (same as SemanticSentence.context).
    """

    sentence_id: str
    document_id: str
    text: str
    assertion_type: AssertionType
    origin_block_type: str
    reason: str
    source_path: Path
    context: str = ""


# ── Phase 3 contract: Document → SemanticSentence ────────────────────────────


@dataclass(frozen=True)
class SemanticSentence:
    """
    The immutable public output of Phase 3.

    This is the contract boundary between document processing and knowledge processing.
    Phase 4+ never needs to understand Markdown, headings, or document structure.
    Everything structural is fully encapsulated here.

    Fields:
        sentence_id:       Deterministic SHA256‑based identifier (16 hex chars)
        document_id:       doc_id of the source Document (links back to Phase 2)
        text:              The sentence text exactly as it appears (canonical prose)
        context:           Heading path under which this sentence appears, or empty string
                           Example: "Python > Generators > Yield"
                           Stored SEPARATELY from text — never fused.
        position:          0‑based sequence number within this document
        char_start:        Character offset in Document.normalized_text where sentence begins
                           (for generated prose, refers to the start of the block)
        char_end:          Character offset in Document.normalized_text where sentence ends
                           (for generated prose, refers to the end of the block)
        source_path:       Path to the original file (for traceability)
        origin_block_type: BlockType that produced this sentence (stored as string)
        schema_version:    Version of this data structure

    All offsets refer to Document.normalized_text; they are traceability offsets,
    not reconstructed offsets into generated prose.
    """

    sentence_id: str
    document_id: str
    text: str
    context: str  # "Python > Generators" or "" if at root
    position: int
    char_start: int
    char_end: int
    source_path: Path
    origin_block_type: str  # e.g., "paragraph", "heading", etc.
    schema_version: str = "3.0"


# ── Phase 3 result ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Phase3Stats:
    """Structural statistics collected during Phase 3 for a single Document."""

    total_headings: int = 0
    total_paragraphs: int = 0
    total_list_items: int = 0
    total_tables: int = 0
    total_block_quotes: int = 0
    total_code_blocks_skipped: int = 0
    total_horizontal_rules: int = 0
    total_front_matter_blocks: int = 0
    total_blank_lines: int = 0
    total_unknown_blocks: int = 0
    sentences_produced: int = 0
    sentences_discarded: int = 0
    warnings: tuple = field(default_factory=tuple)


# ── Phase 1 contract: Discovery → Parsing ────────────────────────────────────


@dataclass(frozen=True)
class DocumentProvenance:
    """
    RECTIFIED (external review, P1-1 "provenance/source lineage"): source
    identity, previously nowhere in the schema, made first-class:
    source_id -> document_id -> claim_id -> relationship -> evidence -> score.

    A document's PATH (SourceDocument.path/relative_path) identifies WHERE
    the file lives on disk. This identifies WHAT it actually is, when the
    document itself discloses that -- who wrote or published it, when, and
    whether it is a copy/derivative of some other source. All fields are
    Optional and default to None (never inferred, never fabricated): most
    documents in most corpora disclose none of this, and reporting
    UNAVAILABLE is strictly more honest than guessing from the filesystem.

    Populated by smriti.parsing.provenance.extract_document_provenance()
    from two concrete, real sources found in this project's own corpora,
    neither previously consumed:
      - YAML frontmatter (```---\\nkey: value\\n---```), e.g.
        data/raw/stress_vault/*.md's `date: 2024-07-01` line.
      - An inline ``**Source:** X`` attribution line immediately following
        the document's H1 heading, e.g. data/raw/reference_vault/*.md's
        ``**Source:** Apache Hadoop Documentation`` lines -- present in
        53 real documents and, until this fix, extracted only as claim
        noise (correctly discarded by the assertion classifier as
        METADATA) with the attribution information itself never captured
        anywhere.

    source_id, when a document's frontmatter declares one explicitly, is
    the identity of the underlying SOURCE, distinct from document_id: two
    different document files (two different document_ids) that declare
    the same source_id are copies/republications of the same underlying
    source, not two independent ones -- this is what P1-1's independence
    signals key on when available (see scoring/signals/provenance.py).
    parent_source_id records citation lineage (this document derives from,
    or quotes, another declared source) when the document says so; it is
    never inferred from content similarity.

    RECTIFIED (P1-6, "PLEASE FIX AND SAVE ME" review round): declared
    publisher/domain identity is not equivalent to independent epistemic
    origin -- a Reuters article, a blog quoting that article, and a note
    quoting the blog can look like three documents and two domains while
    actually being one information source repeated three times.
    publisher_id, canonical_url, lineage_id, and evidence_origin_id are
    schema-level additions for this, distinct from the free-text fields
    above them: publisher_id would be a normalized publisher identity
    (so "Reuters", "reuters.com", and "Reuters News Agency" resolve to
    one identity rather than three unrelated publisher strings);
    canonical_url would be a normalized url (stripping tracking
    parameters, resolving redirects); lineage_id would group every
    document in this project's corpora that share the same
    derivation chain (walked transitively through parent_source_id) under
    one identifier; evidence_origin_id would be the root/ultimate source
    that chain traces back to. As of this fix, NO document in any corpus
    this project holds discloses parent_source_id, source_id-as-a-
    frontmatter-key, or anything a normalization function could resolve
    these four fields from (verified directly against every corpus's raw
    markdown, not assumed) -- so exactly like claim_valid_from/to on
    Claim (P1-11), these four fields exist in the schema and always
    default to None; no inference or normalization logic is implemented
    to populate them yet, because there is no real data in this project
    to test that logic against. Document diversity (distinct document_id
    count), publisher diversity (distinct publisher string count), source-
    origin diversity (distinct source_id count), and lineage diversity
    (distinct lineage_id count) are four DIFFERENT things scoring/signals/
    provenance.py's source_diversity signal should eventually report
    separately rather than conflating -- today it can only compute the
    first two, since source_id disclosure is already rare and lineage_id
    has no data to populate it with at all.
    """

    source_id: str | None = None
    author: str | None = None
    publisher: str | None = None
    domain: str | None = None
    url: str | None = None
    publication_date: datetime | None = None
    parent_source_id: str | None = None
    publisher_id: str | None = None
    canonical_url: str | None = None
    lineage_id: str | None = None
    evidence_origin_id: str | None = None
    extraction_method: str = "none"  # "yaml_frontmatter" | "inline_source_line" | "none"

    @property
    def is_available(self) -> bool:
        return self.extraction_method != "none"


@dataclass(frozen=True)
class SourceDocument:
    """
    The immutable, file‑centric representation of one discovered document.
    Produced by Phase 1, consumed by Phase 2.
    """

    doc_id: str
    path: Path
    relative_path: Path
    source_root: Path
    format: FileFormat
    content_hash: str
    size_bytes: int
    modified_at: datetime


# ── Phase 2 extraction models ────────────────────────────────────────────────


@dataclass(frozen=True)
class TextStatistics:
    character_count: int
    word_count: int
    line_count: int
    blank_line_count: int
    paragraph_count: int


@dataclass(frozen=True)
class RawExtractionResult:
    raw_text: str
    warnings: tuple[WarningCode, ...]
    method: ExtractionMethod
    encoding_used: str


@dataclass(frozen=True)
class NormalizationResult:
    normalized_text: str
    warnings: tuple[WarningCode, ...]


@dataclass(frozen=True)
class Document:
    """The final enriched document produced by Phase 2."""

    doc_id: str
    source_document: SourceDocument
    raw_text: str
    normalized_text: str
    extraction_method: ExtractionMethod
    extraction_warnings: tuple[WarningCode, ...]
    text_statistics: TextStatistics
    encoding_used: str
    schema_version: str = "2.0"
    # RECTIFIED (external review, P1-1): source identity, parsed from the
    # document's own disclosed frontmatter/attribution line where present
    # (smriti.parsing.provenance), never inferred. Defaults to an
    # all-None DocumentProvenance() (is_available=False), not to None
    # itself, so every consumer can rely on the field always being a
    # DocumentProvenance instance.
    provenance: DocumentProvenance = field(default_factory=DocumentProvenance)

    @property
    def has_warnings(self) -> bool:
        return len(self.extraction_warnings) > 0

    @property
    def is_empty(self) -> bool:
        return len(self.normalized_text.strip()) == 0


# ── Phase 4 contract: SemanticSentence → Claim ───────────────────────────────


@dataclass(frozen=True)
class StructuredAssertion:
    subject: str | None = None
    predicate: str | None = None
    object: str | None = None
    negation_marker: str | None = None
    modality_marker: str | None = None

    @property
    def is_complete(self) -> bool:
        return all([self.subject, self.predicate, self.object])

    @property
    def is_partial(self) -> bool:
        return any([self.subject, self.predicate, self.object])


@dataclass(frozen=True)
class AssertionMetadata:
    is_negated: bool = False
    modality: Modality = Modality.CERTAIN
    is_conditional: bool = False
    is_comparative: bool = False
    is_attributed: bool = False
    attributed_to: str | None = None
    is_quoted: bool = False


@dataclass(frozen=True)
class ClaimProvenance:
    """
    Provenance chain linking a Claim back to its originating SemanticSentence.

    Fields:
        sentence_id:          The originating SemanticSentence's ID.
        document_id:          doc_id of the source Document.
        source_path:          Path to the original file.
        sentence_context:     Heading path (same as SemanticSentence.context).
        sentence_position:    0-based position of the sentence in its document.
        source_char_spans:    Tuple of (start, end) character-offset pairs
                               INTO THE ORIGINAL SENTENCE TEXT (SemanticSentence.text),
                               one pair per contiguous run of tokens actually
                               used to build this claim. A single-assertion or
                               whole-sentence claim has exactly one span
                               covering the whole sentence; a coordinated-
                               predicate/object split (e.g. "Python supports
                               generators and decorators." → two claims) has
                               one span for the shared subject+verb run and a
                               second span for the conjunct actually used by
                               THIS claim — never the other conjunct's tokens.
        source_token_ids:     Tuple of spaCy token indices (Token.i) actually
                               used to build this claim, in original sentence
                               order. Empty if the sentence could not be parsed.
        reconstruction_rule:  How this claim's text was assembled from the
                               source sentence. Mirrors BoundaryReason, e.g.
                               "single_assertion", "coordinated_predicate",
                               "independent_clause", "parse_failed".
    """

    sentence_id: str
    document_id: str
    source_path: Path
    sentence_context: str
    sentence_position: int
    source_char_spans: tuple = ()
    source_token_ids: tuple = ()
    reconstruction_rule: str = "single_assertion"


@dataclass(frozen=True)
class Claim:
    """
    An atomic claim (SVO triple or full sentence). Produced by Phase 4.

    Fields:
        claim_id:            Deterministic identifier (SHA256 of content hash + metadata)
        sentence_id:         The ID of the SemanticSentence this claim originated from
        document_id:         doc_id of the source Document
        text:                The claim text (exact substring or full sentence)
        content_hash:        SHA256 of the exact text (for deduplication)
        context:             Heading path (same as SemanticSentence.context)
        source_path:         Path to the original file
        extraction_mode:     How this claim was constructed (structured/partial/lexical/whole_sentence)
        structured_assertion: Optional SVO triple (if extracted with a parser)
        assertion_metadata:  Negation, modality, attribution, etc.
        provenance:          Link back to the original sentence
        schema_version:      Version of this data structure
        rule_version:        Version of the extraction rules used
        timestamp:           RECTIFIED (external review, P1-3 "temporal
                              metadata"): the SEMANTIC assertion time this
                              claim's source document discloses (from its
                              DocumentProvenance.publication_date, itself
                              parsed from YAML frontmatter or similar --
                              never filesystem mtime). None for the
                              overwhelming majority of documents today,
                              which disclose no date at all -- this is the
                              honest common case, not an error.
                              evolution/temporal.py has read this field
                              (falling back to NO_TIMESTAMP status when
                              None) since long before this field actually
                              existed on Claim; the pipeline runner
                              populates it as a post-Phase-4 enrichment
                              step (never inside claims/builder.py itself,
                              which has no access to document-level
                              provenance and should not need it) using the
                              exact same document_provenance map P1-1
                              built for source-identity signals. In the
                              review terminology below, this field IS
                              claim_assertion_time -- kept under its
                              original name rather than renamed, since
                              every existing reader of this field already
                              depends on that name.
        claim_valid_from:    RECTIFIED (P1-11, "PLEASE FIX AND SAVE ME"
                              review round): schema-level extension,
                              distinct from timestamp/claim_assertion_time.
                              A claim like "Python 3.12 was released in
                              2023" has a document date (when it was
                              written) and an assertion time (roughly, when
                              it was written -- usually the same as the
                              document date) that are BOTH different from
                              the claim's own validity interval (the fact
                              became true in 2023 and, for a released-
                              software-version claim, remains true
                              indefinitely after). No extractor populates
                              this field yet -- there is no temporal-
                              expression parser in this pipeline -- so it
                              is always None today. Per the review's own
                              explicit instruction, this field's absence is
                              never inferred or backfilled from timestamp
                              or any other field; None means "not known,"
                              not "same as the assertion time."
        claim_valid_to:      Symmetric with claim_valid_from -- the end of
                              the claim's validity interval, if any (None
                              for claims with no known end, which is not
                              the same as "known to be still valid").
                              Always None today, same caveat as above.
        temporal_expression: The raw natural-language temporal phrase the
                              claim text itself contains, if any (e.g. "in
                              2023", "as of last year") -- kept separate
                              from the parsed claim_valid_from/to because a
                              vague or relative expression may be
                              extractable as text before (or without ever)
                              being resolvable to a concrete date. Always
                              None today; no extractor populates it yet.
        temporal_confidence: Confidence in the temporal_expression parse
                              once a parser exists, in [0.0, 1.0]. Always
                              None today.
    """

    claim_id: str
    sentence_id: str
    document_id: str
    text: str
    content_hash: str
    context: str
    source_path: Path
    extraction_mode: ExtractionMode
    structured_assertion: StructuredAssertion | None
    assertion_metadata: AssertionMetadata
    provenance: ClaimProvenance
    schema_version: str = "4.0"
    rule_version: str = "1.0"
    timestamp: datetime | None = None
    claim_valid_from: datetime | None = None
    claim_valid_to: datetime | None = None
    temporal_expression: str | None = None
    temporal_confidence: float | None = None

    @property
    def is_svo(self) -> bool:
        return (
            self.extraction_mode == ExtractionMode.STRUCTURED
            and self.structured_assertion is not None
            and self.structured_assertion.is_complete
        )

    @property
    def is_negated(self) -> bool:
        return self.assertion_metadata.is_negated

    @property
    def subject(self) -> str | None:
        return self.structured_assertion.subject if self.structured_assertion else None

    @property
    def predicate(self) -> str | None:
        return self.structured_assertion.predicate if self.structured_assertion else None

    @property
    def object(self) -> str | None:
        return self.structured_assertion.object if self.structured_assertion else None


@dataclass(frozen=True)
class Phase4Stats:
    total_sentences_processed: int = 0
    total_claims_produced: int = 0
    structured_claims: int = 0
    partial_claims: int = 0
    lexical_claims: int = 0
    whole_sentence_claims: int = 0
    parser_failures: int = 0
    boundary_splits: int = 0
    negated_claims: int = 0
    modal_claims: int = 0
    attributed_claims: int = 0
    total_discarded_non_assertions: int = 0  # NEW: sentences classified as non-DECLARATIVE
    discarded_by_type: dict[str, int] = field(default_factory=dict)  # NEW: per-AssertionType counts
    warnings: tuple = field(default_factory=tuple)


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────


class VectorDType(str, Enum):
    FLOAT32 = "float32"
    FLOAT64 = "float64"


@dataclass(frozen=True)
class Vector:
    """
    A typed, self-describing embedding vector.

    This is the lowest-level geometric primitive in Phase 5.
    All higher-level objects (Embedding, EmbeddedClaim) reference a Vector.

    Design:
        Replaces the raw `tuple` that was previously embedded in Embedding.
        This future-proofs for: quantization, sparse vectors, binary vectors,
        multimodal vectors — without touching Phase 6.

    Fields:
        values:     Immutable float tuple (the actual numbers).
        dimension:  Length of values (redundant but self-documenting).
        dtype:      "float64" or "float32" — guards against object-type contamination.
        normalized: True if L2 norm has been applied (||values||₂ ≈ 1.0).
    """

    values: tuple
    dimension: int
    dtype: VectorDType = VectorDType.FLOAT64
    normalized: bool = False

    def __post_init__(self):
        if len(self.values) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: values has {len(self.values)} elements "
                f"but dimension={self.dimension}"
            )

    def to_list(self) -> list:
        """Return values as a plain Python list (for serialization, FAISS, etc.)."""
        return list(self.values)

    def __len__(self) -> int:
        return self.dimension


@dataclass(frozen=True)
class EmbeddingModelDescriptor:
    """
    Identifies the exact semantic encoder that produced an embedding.

    All fields together form the model signature used in cache key generation.
    Any change to any field invalidates all cached embeddings.

    Fields:
        provider:         "sentence-transformers", "openai", "bge", etc.
        model_name:       "all-MiniLM-L6-v2"
        model_revision:   Git revision hash of model weights
        dimension:        Embedding dimension (384 for MiniLM)
        model_signature:  SHA256 of (provider + model_name + revision)
        embedding_family: High-level family: "SentenceTransformer", "OpenAI", "BGE", "Instructor"
        checkpoint_sha:   Optional content-addressable SHA if available (beyond HF revision)
    """

    provider: str
    model_name: str
    model_revision: str
    dimension: int
    model_signature: str  # Deterministic: SHA256(provider:model_name:revision)
    embedding_family: str = ""  # e.g. "SentenceTransformer", "OpenAI", "BGE"
    checkpoint_sha: str = ""  # Content-addressable checkpoint hash if available


@dataclass(frozen=True)
class EmbeddingProvenance:
    """
    Execution metadata for one embedding — lightweight, non-semantic.

    Fields:
        pipeline_version:   Phase 5 implementation version
        normalization_mode: "l2" or "none"
        device:             "cpu" / "cuda" / "mps"
        config_hash:        SHA256 of the embedding config section
    """

    pipeline_version: str
    normalization_mode: str
    device: str
    config_hash: str


@dataclass(frozen=True)
class EmbeddingQuality:
    """
    Per-claim diagnostic snapshot produced during Phase 5.

    Phase 6 reads these — it never recomputes them.
    Invaluable when debugging large vaults with thousands of claims.

    Fields:
        dimension_ok:  True if vector.dimension == descriptor.dimension
        normalized:    True if L2 normalization was applied
        finite:        True if all values are finite (no NaN or Inf)
        cache_used:    True if vector came from cache (not fresh inference)
    """

    dimension_ok: bool
    normalized: bool
    finite: bool
    cache_used: bool


@dataclass(frozen=True)
class Embedding:
    """
    The canonical semantic artifact produced by Phase 5 for one Claim.

    DESIGN PRINCIPLE: Embedding is a timeless semantic object.
    It does NOT carry execution status (cached / fresh / stale).
    Execution metadata belongs to EmbeddingResult (internal) and EmbeddingQuality.

    Fields:
        claim_id:   Links back to the originating Claim (referential integrity)
        vector:     Validated, normalized Vector domain object
        descriptor: Which model produced this vector
        provenance: How/where the inference was run
    """

    claim_id: str
    vector: Vector
    descriptor: EmbeddingModelDescriptor
    provenance: EmbeddingProvenance

    @property
    def dimension(self) -> int:
        return self.vector.dimension

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience)."""
        return self.vector.values


@dataclass(frozen=True)
class EmbeddedClaim:
    """
    The bridge between symbolic knowledge (Claim) and numeric geometry (Embedding).

    Phase 6 receives List[EmbeddedClaim] and uses them for similarity search.

    Design:
        Claim is NOT duplicated here — only its ID is referenced.
        This preserves referential integrity and avoids unnecessary duplication.
        Phase 6 looks up the Claim by claim_id when needed.

        quality provides pre-computed diagnostics so Phase 6 never has to
        re-derive normalization status, dimension correctness, etc.
    """

    claim_id: str
    embedding: Embedding
    quality: EmbeddingQuality
    schema_version: str = "5.0"

    @property
    def vector(self) -> Vector:
        return self.embedding.vector

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience for Phase 6 / FAISS)."""
        return self.embedding.vector.values

    @property
    def dimension(self) -> int:
        return self.embedding.dimension

    @property
    def is_cached(self) -> bool:
        return self.quality.cache_used


@dataclass(frozen=True)
class Phase5Stats:
    """Statistics collected during one Phase 5 execution."""

    total_claims: int = 0
    successful: int = 0
    cached: int = 0
    stale: int = 0
    failed: int = 0
    skipped: int = 0
    total_batches: int = 0
    average_batch_size: float = 0.0
    cache_hit_rate: float = 0.0
    total_runtime_seconds: float = 0.0
    vectors_per_second: float = 0.0
    current_memory_mb: float = 0.0
    cache_entries_reused: int = 0
    cache_entries_regenerated: int = 0
    cache_entries_invalidated: int = 0


# ── Phase 6 contract: CandidatePair → RelationshipSet ─────────────────────────


class RelationshipType(str, Enum):
    """
    The semantic relationship type between two Claims.

    ⚠️  This enum is governed by the Relationship Ontology Specification
    in docs/relationship_ontology.md. Any change to these values requires
    updating that document first.

    RECTIFIED (external review, bidirectional-NLI rewrite): the resolver
    previously ran NLI in one fixed direction only (claim_a as premise,
    claim_b as hypothesis, an artifact of claim_id_a/claim_id_b's
    lexicographic canonicalization, not of semantic direction), so it
    could never tell "A entails B" apart from "B entails A" apart from
    "both" -- SUPPORTS was always emitted as A_TO_B by construction, and
    two logically equivalent claims were indistinguishable from one
    merely supporting the other. EQUIVALENT is new; SUPPORTS/REFINES now
    reflect the genuine entailment direction NLI actually found.

    Rules:
        - CONTRADICTS and EQUIVALENT are symmetric; SUPPORTS and REFINES
          are directional (the direction NLI's own bidirectional
          entailment check found, not an artifact of ID ordering).
        - UNKNOWN means the resolver abstained (ABSTAIN): confidence too
          low, or no direction dominant either way. It must never be
          persisted to Phase 7.
        - NEUTRAL should not be persisted to Phase 7 (configurable).
    """

    CONTRADICTS = "contradicts"  # Symmetric: claims assert opposing facts
    SUPPORTS = "supports"  # Directional: one claim one-way entails the other
    REFINES = (
        "refines"  # Directional: one-way entailment where the entailing claim is also more specific
    )
    EQUIVALENT = "equivalent"  # Symmetric: each claim entails the other (bidirectional entailment)
    NEUTRAL = "neutral"  # Symmetric: semantically close, no direction
    UNKNOWN = "unknown"  # Resolver abstained (ABSTAIN); never persist


class RelationshipDirection(str, Enum):
    """
    Direction of a relationship between claim_a and claim_b.

    Ontology constraints:
        CONTRADICTS → always SYMMETRIC
        EQUIVALENT  → always SYMMETRIC
        SUPPORTS    → A_TO_B or B_TO_A, per NLI's actual bidirectional
                      entailment result (never assumed from ID order)
        REFINES     → A_TO_B or B_TO_A, same basis as SUPPORTS
        NEUTRAL     → always SYMMETRIC
    """

    A_TO_B = "a_to_b"  # claim_a → claim_b
    B_TO_A = "b_to_a"  # claim_b → claim_a
    SYMMETRIC = "symmetric"  # Both directions are equivalent


class ResolutionStatus(str, Enum):
    """
    RECTIFIED (external review, P0-4): UNKNOWN was, in the RelationshipType
    enum above, one value among six -- indistinguishable in the type
    system from a genuine semantic relation like CONTRADICTS. Conceptually
    it is not a relation at all: CONTRADICTS/SUPPORTS/REFINES/EQUIVALENT/
    NEUTRAL are claims about how two propositions relate; "the resolver
    could not decide" is a claim about the resolver's own confidence, a
    different kind of fact entirely. This enum makes that distinction a
    first-class type rather than a comment.

    This does NOT remove RelationshipType.UNKNOWN (a breaking change to
    the persisted schema and every existing call site comparing against
    it was judged disproportionate to the remaining scope of this
    remediation) -- see RelationshipDecision and to_decision() below for
    the additive, non-breaking way to consume this distinction. New code,
    and especially new *reporting* code, should reason in terms of
    ResolutionStatus, not `== RelationshipType.UNKNOWN`.
    """

    RESOLVED = "resolved"  # The resolver committed to a semantic relation type
    ABSTAINED = "abstained"  # The resolver had insufficient/ambiguous evidence


@dataclass(frozen=True)
class RelationshipDecision:
    """
    RECTIFIED (external review, P0-4): the resolver's output reframed as
    "a relation type, conditional on having resolved one at all" rather
    than "one of six co-equal relation types, one of which happens to
    mean abstain." relation_type is None exactly when status is ABSTAINED
    -- there is no relation to report, not a relation called "unknown."

    Construct via to_decision(relationship_type, direction, ...), never
    directly, so the None-iff-ABSTAINED invariant is enforced in one place.
    """

    relation_type: "RelationshipType | None"
    direction: "RelationshipDirection"
    status: ResolutionStatus
    confidence: float | None = None
    abstention_reason: str | None = None


def to_decision(
    relationship_type: "RelationshipType",
    direction: "RelationshipDirection",
    confidence: float | None = None,
    abstention_reason: str | None = None,
) -> RelationshipDecision:
    """The single place RelationshipType.UNKNOWN is translated into the
    conceptually correct (relation_type=None, status=ABSTAINED) form.
    Every consumer that wants to reason about abstention rather than
    relation type should go through this function rather than comparing
    against RelationshipType.UNKNOWN directly."""
    if relationship_type == RelationshipType.UNKNOWN:
        return RelationshipDecision(
            relation_type=None,
            direction=direction,
            status=ResolutionStatus.ABSTAINED,
            confidence=confidence,
            abstention_reason=abstention_reason
            or "insufficient or ambiguous NLI evidence in either direction",
        )
    return RelationshipDecision(
        relation_type=relationship_type,
        direction=direction,
        status=ResolutionStatus.RESOLVED,
        confidence=confidence,
    )


class LifecycleStage(str, Enum):
    """
    Explicit lifecycle of a claim pair through the Phase 6 pipeline.

    Every object in the pipeline belongs to exactly one stage.
    Transitions are one-way; no object can move backward.

    CANDIDATE              → discovered by exact FAISS retrieval, not yet validated
    VALIDATED_CANDIDATE    → passed all candidate validation checks
    EVIDENCE               → NLI inference completed; raw scores available
    CALIBRATED_EVIDENCE    → scores adjusted by ConfidenceCalibrator
    RESOLVED               → RelationshipType assigned by resolver
    VALIDATED_RELATIONSHIP → passed confidence and consistency checks
    RELATIONSHIP           → immutable Relationship object constructed
    REJECTED               → failed at any stage; not in final RelationshipSet
    """

    CANDIDATE = "candidate"
    VALIDATED_CANDIDATE = "validated_candidate"
    EVIDENCE = "evidence"
    CALIBRATED_EVIDENCE = "calibrated_evidence"
    RESOLVED = "resolved"
    VALIDATED_RELATIONSHIP = "validated_relationship"
    RELATIONSHIP = "relationship"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RetrievalSearchParameters:
    """
    Parameters used during exact cosine-similarity retrieval (FAISS IndexFlatIP) for this candidate pair.

    Enables exact reproduction of retrieval behavior during debugging or replay.
    """

    top_k: int
    sim_threshold: float
    index_type: str  # e.g. "faiss_flat_ip"
    index_version: str  # e.g. "1.0"


@dataclass(frozen=True)
class RetrievalQuality:
    """
    Quality signal for the retrieval stage of a CandidatePair.

    Fields:
        exact_match:          claim_id_a and claim_id_b share identical text (duplicate)
        duplicate_removed:    A duplicate was detected and eliminated
        below_threshold:      The pair was below the sim_threshold (should not occur post-filter)
        high_density_region:  Both claims have many neighbors (dense semantic region)
        isolated_claim:       One or both claims had very few neighbors (isolated semantics)
    """

    exact_match: bool = False
    duplicate_removed: bool = False
    below_threshold: bool = False
    high_density_region: bool = False
    isolated_claim: bool = False


@dataclass(frozen=True)
class CandidatePair:
    """
    A pair of semantically similar claims discovered by exact nearest-neighbor
    search via FAISS's flat inner-product index (IndexFlatIP).

    This is the entry ticket to the classification pipeline.
    Every CandidatePair that passes validation proceeds to NLI evidence generation.

    Fields:
        claim_id_a:           First claim's ID (always ≤ claim_id_b lexicographically)
        claim_id_b:           Second claim's ID
        cosine_similarity:    Cosine similarity from exact FAISS IndexFlatIP retrieval (0.0–1.0)
        candidate_rank:       Rank of claim_b in claim_a's neighbor list (1 = nearest)
        retrieval_backend:    Backend used for retrieval (e.g. "faiss_flat_ip")
        index_version:        Version of the retrieval index
        search_parameters:    Full search parameters for exact reproduction
        retrieval_quality:    Quality signals for this retrieval result
        lifecycle_stage:      Always CANDIDATE when first created
    """

    claim_id_a: str
    claim_id_b: str
    cosine_similarity: float
    candidate_rank: int
    retrieval_backend: str = "faiss_flat_ip"
    index_version: str = "1.0"
    search_parameters: Optional["RetrievalSearchParameters"] = None
    retrieval_quality: Optional["RetrievalQuality"] = None
    lifecycle_stage: "LifecycleStage" = LifecycleStage.CANDIDATE

    def pair_key(self) -> str:
        """Canonical pair identifier (order-independent)."""
        a, b = sorted([self.claim_id_a, self.claim_id_b])
        return f"{a}:{b}"


@dataclass(frozen=True)
class NLILabel(str, Enum):
    """NLI labels from the cross-encoder model."""

    ENTAILMENT = "entailment"
    NEUTRAL = "neutral"
    CONTRADICTION = "contradiction"


@dataclass(frozen=True)
class InferenceMetadata:
    """
    Operational metadata about the NLI inference run.

    Separated from NLI scores to keep evidence clean.
    Fields:
        model_name:        NLI model identifier
        model_version:     Model version / revision (from HF hub)
        runtime_seconds:   Wall-clock time for this pair's inference
        device:            "cpu" | "cuda" | "mps"
        batch_index:       Which batch this pair was processed in
        latency_ms:        Per-pair inference latency in milliseconds
    """

    model_name: str
    model_version: str = "unknown"
    runtime_seconds: float = 0.0
    device: str = "cpu"
    batch_index: int = 0
    latency_ms: float = 0.0


@dataclass(frozen=True)
class NLIScores:
    """
    Raw NLI evidence scores from the cross-encoder.

    This is pure evidence — no model metadata here.
    Interpretation belongs to ConfidenceCalibrator → RelationshipResolver.

    Fields:
        entailment_score:       P(entailment | claim_a, claim_b)
        neutral_score:          P(neutral | claim_a, claim_b)
        contradiction_score:    P(contradiction | claim_a, claim_b)
        predicted_label:        argmax label from the cross-encoder
        raw_confidence:         max(E, N, C) — before calibration
    """

    entailment_score: float
    neutral_score: float
    contradiction_score: float
    predicted_label: str  # "entailment" | "neutral" | "contradiction"
    raw_confidence: float  # max of the three scores, before calibration


@dataclass(frozen=True)
class RelationshipEvidence:
    """
    Complete evidence record for one CandidatePair.

    Contains:
        - pair:             The candidate pair this evidence was gathered for
        - cosine_similarity: From Phase 5 exact cosine-similarity retrieval (FAISS IndexFlatIP)
        - nli_scores:       Raw NLI evidence for claim_a-as-premise / claim_b-as-hypothesis
                             ("A -> B" direction; kept as the primary field name for
                             backward compatibility with every consumer that reads
                             evidence.nli_scores expecting a single-direction score).
        - nli_scores_b_to_a: RECTIFIED (bidirectional-NLI rewrite): NLI evidence for
                             the REVERSE direction (claim_b-as-premise / claim_a-as-
                             hypothesis). None only for evidence generated by legacy
                             single-direction code paths (e.g. some unit-test fixtures);
                             production Phase 6 always populates this. Required to tell
                             "A entails B" apart from "B entails A" apart from "both"
                             (EQUIVALENT) apart from "neither" -- a fixed single-direction
                             NLI call cannot distinguish these, and previously SUPPORTS
                             was always emitted as A_TO_B regardless of which claim
                             actually did the entailing.
        - calibrated_confidence: Calibrated confidence after ConfidenceCalibrator,
                             for the primary A->B direction.
        - calibrated_confidence_b_to_a: RECTIFIED (external "reality check"
                             review round 3, P0-5 "directional confidence
                             is still wrong"): the SAME calibration applied
                             to the reverse (B->A) direction. Before this
                             field existed, every persisted relationship's
                             confidence was the A->B calibrated value
                             regardless of which direction the resolver
                             actually chose -- e.g. a resolver decision of
                             B_TO_A (because e_ba=0.91 dominated e_ab=0.41)
                             still reported the A->B reading (0.41-derived)
                             as "the" confidence, contaminating
                             RelationshipQuality.nli_above_threshold and
                             every downstream consumer of that scalar
                             (evidence strength, reliability, conflict
                             pressure, Phase 6 statistics). See
                             retrieval.classification.resolver.compute_decision_confidence()
                             for the per-relation-type formula that now
                             selects/combines the two calibrated readings
                             correctly. None only when nli_scores_b_to_a is
                             None (legacy single-direction evidence).
        - inference_metadata:  Model + runtime metadata (separated from scores)
        - lifecycle_stage:  EVIDENCE or CALIBRATED_EVIDENCE

    Replaces the original flat RelationshipEvidence which mixed scores and metadata.
    """

    pair: "CandidatePair"
    cosine_similarity: float
    nli_scores: "NLIScores"
    calibrated_confidence: float  # After calibration; use this for thresholding
    inference_metadata: "InferenceMetadata"
    lifecycle_stage: "LifecycleStage" = LifecycleStage.EVIDENCE
    nli_scores_b_to_a: Optional["NLIScores"] = None
    calibrated_confidence_b_to_a: float | None = None

    # Convenience accessors (backward-compatible with resolver and tests)
    @property
    def entailment_score(self) -> float:
        return self.nli_scores.entailment_score

    @property
    def neutral_score(self) -> float:
        return self.nli_scores.neutral_score

    @property
    def contradiction_score(self) -> float:
        return self.nli_scores.contradiction_score

    @property
    def predicted_label(self) -> str:
        return self.nli_scores.predicted_label

    @property
    def confidence(self) -> float:
        return self.calibrated_confidence

    @property
    def model_name(self) -> str:
        return self.inference_metadata.model_name


@dataclass(frozen=True)
class RelationshipProvenance:
    """
    Complete audit trail for one Relationship.

    Every relationship must know exactly how it was discovered.
    Enables reproducibility, debugging, future auditing, and replay.

    Fields:
        retrieval_backend:    "faiss_flat_ip" etc.
        retrieval_version:    Phase 6 implementation version
        index_version:        Index build version
        search_parameters:    Full retrieval search parameters (FAISS IndexFlatIP) for exact reproduction
        classifier_model:     NLI model name
        classifier_version:   NLI model version
        resolver_version:     Resolver policy version
        calibrator_version:   ConfidenceCalibrator version
        cosine_similarity:    Similarity from exact FAISS IndexFlatIP retrieval
        candidate_rank:       Neighbor rank
        raw_nli_confidence:   Confidence before calibration
        calibrated_confidence: Confidence after calibration
        config_hash:          SHA256 of relevant config
        run_id:               Pipeline run identifier
        replay_id:            If this was a replay, the original run_id; else None
    """

    retrieval_backend: str
    retrieval_version: str
    index_version: str
    search_parameters: Optional["RetrievalSearchParameters"]
    classifier_model: str
    classifier_version: str
    resolver_version: str
    calibrator_version: str
    cosine_similarity: float
    candidate_rank: int
    raw_nli_confidence: float
    calibrated_confidence: float
    config_hash: str
    run_id: str
    replay_id: str | None = None


@dataclass(frozen=True)
class RelationshipQuality:
    """Pre-computed quality diagnostics for a Relationship."""

    cosine_above_threshold: bool
    nli_above_threshold: bool
    evidence_consistent: bool  # entailment+contradiction don't both exceed threshold
    calibration_applied: bool  # Whether ConfidenceCalibrator changed the confidence
    retrieval_quality: Optional["RetrievalQuality"] = None


@dataclass(frozen=True)
class SchemaVersionInfo:
    """
    Schema version information for artifact evolution.

    Fields:
        schema_version:        Current schema version (e.g. "6.0")
        migration_version:     Minimum version that can read this artifact (e.g. "6.0")
        compatibility_version: Maximum backward-compatible version (e.g. "5.0" = breaks Phase 5 readers)

    Migration contract:
        When schema_version bumps to 6.1:
            - migration_version stays "6.0" if old Phase 7 readers can still read it
            - migration_version bumps to "6.1" if breaking change
            - compatibility_version reflects the oldest reader still compatible
    """

    schema_version: str
    migration_version: str
    compatibility_version: str


@dataclass(frozen=True)
class Relationship:
    """
    An immutable, fully-traced semantic relationship between two Claims.

    This is Phase 6's canonical output.
    Phase 7 consumes List[Relationship] for temporal reasoning.

    Fields:
        relationship_id:    Deterministic SHA256-based ID (16 hex chars)
        claim_id_a:         First claim
        claim_id_b:         Second claim
        relationship_type:  The semantic relationship (CONTRADICTS, SUPPORTS, etc.)
        direction:          Symmetric or directional (see ontology spec)
        evidence:           Full evidence record (NLI scores + metadata)
        quality:            Pre-computed quality diagnostics
        provenance:         Complete audit trail
        version_info:       Schema/migration/compatibility versions
        lifecycle_stage:    Always RELATIONSHIP when fully constructed
    """

    relationship_id: str
    claim_id_a: str
    claim_id_b: str
    relationship_type: RelationshipType
    direction: RelationshipDirection
    evidence: "RelationshipEvidence"
    quality: RelationshipQuality
    provenance: RelationshipProvenance
    version_info: "SchemaVersionInfo"
    lifecycle_stage: "LifecycleStage" = LifecycleStage.RELATIONSHIP

    # Backward-compatible property
    @property
    def schema_version(self) -> str:
        return self.version_info.schema_version

    def is_contradiction(self) -> bool:
        return self.relationship_type == RelationshipType.CONTRADICTS

    def is_support(self) -> bool:
        return self.relationship_type == RelationshipType.SUPPORTS

    def involves(self, claim_id: str) -> bool:
        return claim_id in (self.claim_id_a, self.claim_id_b)


@dataclass
class RelationshipSet:
    """
    The complete output of Phase 6.
    This is what Phase 7 receives.

    Fields:
        relationships:          All discovered relationships
        total_candidates:       How many candidate pairs were evaluated
        total_validated:        How many passed candidate validation
        total_rejected:         How many were rejected (all stages combined)
        rejected_reasons:       Counts by rejection reason
        run_id:                 Pipeline run identifier
        version_info:           Schema/migration/compatibility versions for this set
        replay_manifest_path:   Path to the replay manifest (for deterministic replay)
    """

    relationships: list["Relationship"]
    total_candidates: int
    total_validated: int
    total_rejected: int
    rejected_reasons: dict[str, int]
    run_id: str
    version_info: "SchemaVersionInfo" = field(
        default_factory=lambda: SchemaVersionInfo(
            schema_version="6.0",
            migration_version="6.0",
            compatibility_version="6.0",
        )
    )
    manifest_path: Path | None = None
    dataset_path: Path | None = None
    replay_manifest_path: Path | None = None

    @property
    def total_relationships(self) -> int:
        return len(self.relationships)

    @property
    def contradictions(self) -> list["Relationship"]:
        return [
            r for r in self.relationships if r.relationship_type == RelationshipType.CONTRADICTS
        ]

    @property
    def supports(self) -> list["Relationship"]:
        return [r for r in self.relationships if r.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refinements(self) -> list["Relationship"]:
        return [r for r in self.relationships if r.relationship_type == RelationshipType.REFINES]

    @property
    def equivalents(self) -> list["Relationship"]:
        return [r for r in self.relationships if r.relationship_type == RelationshipType.EQUIVALENT]


class RelationshipDeduplicationPolicy(str, Enum):
    """
    Policy for handling duplicate relationships (same pair, same type, different runs).

    KEEP_FIRST:     Keep the relationship from the first run that discovered it.
    KEEP_LATEST:    Keep the relationship from the most recent run.
    KEEP_HIGHEST_CONFIDENCE: Keep the relationship with the highest calibrated confidence.
    KEEP_ALL:       Keep all copies (dangerous for graph construction; use for audit).
    """

    KEEP_FIRST = "keep_first"
    KEEP_LATEST = "keep_latest"
    KEEP_HIGHEST_CONFIDENCE = "keep_highest_confidence"
    KEEP_ALL = "keep_all"


class ConflictResolutionPolicy(str, Enum):
    """
    Policy for resolving type conflicts between runs (same pair, different RelationshipType).

    Example: Run 1 says SUPPORTS, Run 2 says CONTRADICTS — which wins?

    LATEST_WINS:       The most recent run's classification wins.
    HIGHEST_CONFIDENCE: The classification with highest calibrated_confidence wins.
    MOST_SPECIFIC:      Priority: CONTRADICTS > REFINES > SUPPORTS > NEUTRAL > UNKNOWN.
    CONSERVATIVE:       Only keep the relationship if all runs agree on the type.
    """

    LATEST_WINS = "latest_wins"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_SPECIFIC = "most_specific"
    CONSERVATIVE = "conservative"


# ── Phase 7: Knowledge Graph Construction ────────────────────────────────────


class SemanticRole(str, Enum):
    """
    Semantic role annotation derived from graph topology.

    Converted from topology numbers → domain concepts.
    DESCRIPTIVE, not inferential — describes structural importance.

    All thresholds that determine these roles are configured in
    AnnotationPolicy (config/default.yaml: knowledge_graph.annotation).
    No threshold values are hardcoded in annotation.py.
    """

    FOUNDATIONAL_CLAIM = "foundational_claim"  # High centrality, many SUPPORTS edges
    BRIDGE_CLAIM = "bridge_claim"  # Articulation point: removal disconnects partition
    EVIDENCE_HUB = "evidence_hub"  # Many incoming SUPPORTS edges
    REFINEMENT_ROOT = "refinement_root"  # Source of many REFINES edges
    PERIPHERAL_CLAIM = "peripheral_claim"  # Low degree, mostly disconnected
    LEAF_CLAIM = "leaf_claim"  # No outgoing semantic edges
    UNCLASSIFIED = "unclassified"  # Insufficient topology data


class TemporalStatus(str, Enum):
    """Status of temporal analysis for a contradiction boundary."""

    EVOLUTION_CHAIN = "evolution_chain"  # Reliable semantic timestamps → evolved
    STATIC_PARTITION = "static_partition"  # No timestamp ordering → competing beliefs
    UNRESOLVED_CONFLICT = "unresolved_conflict"  # Identical timestamps → cannot determine
    NO_TIMESTAMP = "no_timestamp"  # Claim.timestamp unavailable → disabled


@dataclass(frozen=True)
class TopologyMetrics:
    """
    Graph-derived structural information for one ClaimNode.
    Computed by TopologyAnalyzer within each partition.

    Bridge detection uses NetworkX articulation_points, not degree-heuristics.
    Density is computed as directed: edges / (n * (n-1)), n = partition size.
    """

    degree: int  # Total edges (in + out)
    in_degree: int  # Incoming edges (being supported/contradicted)
    out_degree: int  # Outgoing edges (supporting/contradicting others)
    is_bridge: bool  # True articulation point (NetworkX algorithm)
    is_hub: bool  # Significantly above-average degree (config-driven)
    partition_id: str  # Which partition this node belongs to
    centrality: float = 0.0  # Normalized in-degree centrality (in_degree / (N-1))


@dataclass(frozen=True)
class SupportAggregate:
    """
    Aggregated semantic support for one ClaimNode within its partition.

    PROVENANCE ROOT DEFINITION:
    This aggregate includes ALL transitive supporting claims. In a chain where
    A -> B -> C, both A and B are considered supporting claims of C.
    The supporting_claim_ids tuple contains the unique IDs of all such claims,
    ensuring no claim is double-counted even if multiple paths exist.

    RECTIFIED (provenance/reliability redesign, external review): counting
    every unique supporting claim_id as one independent piece of evidence
    conflates "distinct claim" with "distinct evidence" -- two claims linked
    by an EQUIVALENT edge (a paraphrase, restated in different words) are
    semantic duplicates, not two independently-arrived-at corroborations,
    but each previously counted separately toward source diversity and
    evidence independence. independent_evidence_group_ids collapses
    supporting_claim_ids into equivalence classes (claims mutually reachable
    via EQUIVALENT edges among the supporters of THIS node are one group;
    every other supporting claim is its own singleton group) and reports one
    representative claim_id per group. Downstream signals that measure
    "how many supporters does this claim have" (e.g. MOST_SPECIFIC-style
    counts) should keep using supporting_claim_ids; signals that measure
    "how many independent sources corroborate this claim" (source diversity,
    evidence independence) should use independent_evidence_group_ids instead.
    Defaults to empty/None so existing call sites that construct this
    dataclass without the new fields (fixtures, tests predating this
    rectification) remain valid -- absence is a legacy-fixture signal, not a
    claim that zero evidence groups exist.

    RECTIFIED (external review, P1-2 "evidence aggregation / double
    counting"): collapsing semantic duplicates (above) fixes ONE of the
    two ways this aggregate could overstate corroboration. The other is
    hop distance: "A supports B, B supports C" makes A a transitive
    supporter of C, but A is not independent evidence FOR C in the way a
    claim that directly supports C is -- A's support is mediated entirely
    through B, and if B turns out to be wrong, A's contribution to C was
    never real corroboration at all. Every independent_evidence_group_id
    is now classified by the SHORTEST path length (hop distance) at which
    any of its members was reached from this node:
        direct_evidence_group_ids        - hop distance == 1
        derived_evidence_group_ids       - hop distance == 2 ("one-hop derived")
        multi_hop_evidence_group_ids     - hop distance >= 3
    discounted_evidence_strength and discounted_weighted_confidence apply
    policy.evidence.{direct,derived,multi_hop}_evidence_weight (default
    1.0 / 0.6 / 0.3 -- an engineering-judgment starting point, not
    cross-validated) to these three tiers; EvidenceStrengthExtractor uses
    them instead of raw support_count/weighted_confidence. A claim
    reached at multiple hop distances via different paths is classified
    by its SHORTEST path -- being also reachable the long way around does
    not make genuinely direct evidence less direct.
    """

    support_count: int
    weighted_confidence: float
    supporting_claim_ids: tuple
    evidence_summary: str  # Human-readable summary
    independent_evidence_group_ids: tuple = ()
    independent_evidence_group_count: int | None = None
    direct_evidence_group_ids: tuple = ()
    derived_evidence_group_ids: tuple = ()
    multi_hop_evidence_group_ids: tuple = ()
    discounted_evidence_strength: float | None = None
    discounted_weighted_confidence: float | None = None


@dataclass(frozen=True)
class TemporalMetadata:
    """
    Temporal evolution metadata for one contradiction boundary.

    RECTIFIED: populated from Claim.timestamp (semantic timestamp),
    never from filesystem st_mtime. If Claim.timestamp is None,
    status is NO_TIMESTAMP rather than inferring from the filesystem.
    """

    status: TemporalStatus
    earlier_claim_id: str | None  # claim_id of the earlier claim (if EVOLUTION_CHAIN)
    later_claim_id: str | None  # claim_id of the later claim (if EVOLUTION_CHAIN)
    time_delta_days: float | None  # Days between timestamps
    temporal_confidence: float  # Confidence in the temporal ordering (0.0–1.0)


@dataclass(frozen=True)
class NodeAnnotations:
    """
    All enrichment annotations for one ClaimNode, grouped into a single container.

    RECTIFIED (P1-2): ClaimNode no longer stores topology, support, temporal,
    semantic role, and partition_id as flat fields. These are grouped here.
    ClaimNode.annotations is a single Optional[NodeAnnotations].

    This decouples the enrichment lifecycle from the domain model.
    """

    semantic_role: SemanticRole = SemanticRole.UNCLASSIFIED
    topology: Optional["TopologyMetrics"] = None
    support_aggregate: Optional["SupportAggregate"] = None
    temporal_metadata: Optional["TemporalMetadata"] = None
    partition_id: str | None = None
    stable_partition_label: str | None = None  # Incremental-friendly label (P2-5)


@dataclass(frozen=True)
class ClaimNode:
    """
    One canonical semantic claim inside the KnowledgeGraph.

    RECTIFIED (P1-2): All enrichment data lives in NodeAnnotations.
    ClaimNode itself only holds identity + raw claim data.
    Backward-compatible property accessors are provided for all original fields.

    Fields:
        node_id:       Deterministic ID == claim_id from Phase 4
        claim_id:      Reference to the originating Claim
        claim_text:    Original claim text
        context:       Heading context (e.g. "Python > Generators")
        source_path:   Original file path
        document_id:   Which document produced this claim
        annotations:   All topology/support/temporal/role/partition data
        schema_version: "7.0"
    """

    node_id: str
    claim_id: str
    claim_text: str
    context: str
    source_path: Path
    document_id: str
    annotations: Optional["NodeAnnotations"] = None
    schema_version: str = "7.0"

    # ── Backward-compatible accessors ──────────────────────────────────────────
    @property
    def semantic_role(self) -> "SemanticRole":
        if self.annotations:
            return self.annotations.semantic_role
        return SemanticRole.UNCLASSIFIED

    @property
    def topology(self) -> Optional["TopologyMetrics"]:
        return self.annotations.topology if self.annotations else None

    @property
    def support_aggregate(self) -> Optional["SupportAggregate"]:
        return self.annotations.support_aggregate if self.annotations else None

    @property
    def temporal_metadata(self) -> Optional["TemporalMetadata"]:
        return self.annotations.temporal_metadata if self.annotations else None

    @property
    def partition_id(self) -> str | None:
        return self.annotations.partition_id if self.annotations else None


@dataclass(frozen=True)
class RelationshipEdge:
    """
    One semantic relationship inside the KnowledgeGraph.

    Invariants:
        - source_node_id and target_node_id must reference existing ClaimNodes
        - relationship_type is NEVER UNKNOWN
        - NEUTRAL is absent unless configuration explicitly permits it
        - Every edge is unique (pair + type)
    """

    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: "RelationshipType"
    direction: "RelationshipDirection"
    calibrated_confidence: float
    cosine_similarity: float
    nli_confidence: float
    candidate_rank: int
    schema_version: str = "7.0"


@dataclass(frozen=True)
class KnowledgePartition:
    """
    One internally consistent semantic context within the KnowledgeGraph.

    RECTIFIED (P1-5): density is DIRECTED: edges / (n * (n-1)) where n = node count.
    This is documented explicitly. Previously the formula was ambiguous.

    RECTIFIED (P2-5): stable_partition_label added alongside SHA256-based partition_id.
    stable_partition_label is the sorted comma-separated list of node_ids, enabling
    comparison across incremental runs without rehashing.

    Invariants:
        - No CONTRADICTS edges exist WITHIN a partition
        - All nodes within a partition are reachable via SUPPORTS/REFINES/EQUIVALENT
        - Partition membership is exclusive
    """

    partition_id: str  # SHA256(sorted_node_ids)[:12] — deterministic
    stable_partition_label: tuple  # sorted tuple of node_ids — incremental-friendly
    node_ids: frozenset
    internal_edge_ids: frozenset
    node_count: int
    edge_count: int
    supports_count: int
    refines_count: int
    density: float  # Directed: edge_count / (n * (n-1)); 0 if n<=1
    longest_support_chain: int
    schema_version: str = "7.0"
    equivalent_count: int = 0  # EQUIVALENT edges internal to this partition


@dataclass(frozen=True)
class GraphStatistics:
    """Graph-wide statistics for one KnowledgeGraph."""

    node_count: int
    edge_count: int
    partition_count: int
    contradiction_count: int
    supports_count: int
    refines_count: int
    isolated_nodes: int
    bridge_nodes: int  # True articulation points (P0-3 fix)
    hub_nodes: int
    evolution_chains: int
    unresolved_conflicts: int
    construction_time_seconds: float
    enrichment_time_seconds: float
    equivalent_count: int = 0  # EQUIVALENT edges graph-wide


@dataclass(frozen=True)
class ValidationReport:
    is_valid: bool
    node_violations: tuple
    edge_violations: tuple
    graph_violations: tuple
    semantic_warnings: tuple  # Renamed from semantic_violations
    validation_time_seconds: float

    @property
    def total_violations(self) -> int:
        return len(self.node_violations) + len(self.edge_violations) + len(self.graph_violations)


@dataclass(frozen=True)
class KnowledgeGraph:
    """
    The immutable canonical semantic representation of the entire corpus.
    Phase 7's output and Phase 8's input.

    KnowledgeGraph is NOT a live graph database.
    It is a frozen artifact representing the state of knowledge at one point in time.
    """

    graph_id: str
    nodes: dict[str, "ClaimNode"]
    edges: dict[str, "RelationshipEdge"]
    partitions: dict[str, "KnowledgePartition"]
    statistics: "GraphStatistics"
    validation_report: "ValidationReport"
    run_id: str
    config_hash: str
    schema_version: str = "7.0"
    # RECTIFIED (external review, P1-1 "provenance/source lineage"):
    # source identity keyed by document_id, populated once from Phase 2's
    # Document artifacts. A side-table rather than a field threaded
    # through ClaimNode/RelationshipEdge -- document-level identity is
    # naturally one-per-document, not one-per-claim, and a side-table
    # avoids duplicating it onto every claim from the same document while
    # still being directly reachable from any signal extractor that
    # already receives this graph (scoring/signals/provenance.py,
    # independence.py). Missing keys mean "no disclosed provenance for
    # that document" (the common case), not an error.
    document_provenance: dict[str, "DocumentProvenance"] = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def partition_count(self) -> int:
        return len(self.partitions)

    @property
    def contradiction_edges(self) -> list["RelationshipEdge"]:
        return [
            e for e in self.edges.values() if e.relationship_type == RelationshipType.CONTRADICTS
        ]

    @property
    def supports_edges(self) -> list["RelationshipEdge"]:
        return [e for e in self.edges.values() if e.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refines_edges(self) -> list["RelationshipEdge"]:
        return [e for e in self.edges.values() if e.relationship_type == RelationshipType.REFINES]

    def get_node(self, claim_id: str) -> Optional["ClaimNode"]:
        return self.nodes.get(claim_id)

    def get_partition_for_node(self, claim_id: str) -> Optional["KnowledgePartition"]:
        node = self.nodes.get(claim_id)
        if node and node.partition_id:
            return self.partitions.get(node.partition_id)
        return None


@dataclass(frozen=True)
class Phase7Stats:
    """Statistics collected during Phase 7 execution."""

    input_relationships: int = 0
    input_filtered: int = 0
    nodes_created: int = 0
    edges_created: int = 0
    partitions_created: int = 0
    contradictions_as_boundaries: int = 0
    evolution_chains_detected: int = 0
    unresolved_conflicts: int = 0
    construction_time_seconds: float = 0.0
    enrichment_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    validation_passed: bool = False


# ── Phase 7 contract: Contradiction → Scoring ────────────────────────────────


@dataclass
class Contradiction:
    """A detected contradiction between two claims. Produced by Phase 7."""

    claim_a_id: str
    claim_b_id: str
    contradiction_type: ContradictionType
    nli_confidence: float  # Gate 2 output
    similarity_score: float  # Gate 1 output
    temporal_distance_days: int
    severity_score: float  # Gate 3 final score
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def __repr__(self) -> str:
        return (
            f"Contradiction({self.claim_a_id[:20]} vs {self.claim_b_id[:20]}, "
            f"type={self.contradiction_type}, severity={self.severity_score:.2f})"
        )


# ── Phase 8: Reliability Evaluation ──────────────────────────────────────────


class CalibrationLabel(str, Enum):
    """
    Human-readable reliability tier derived from Reliability Index.

    RECTIFIED (P1-4): Each label now has a semantic contract that Phase 9
    can consume without guessing. The contract is documented here and enforced
    by the Validation Checklist.

    Contracts:
        VERY_HIGH: Multiple independent, high-confidence sources, no significant
                   contradiction. Display with full confidence.
        HIGH:      Well-supported, minor concerns only. Display normally.
        MODERATE:  Some support but notable gaps, limited independence, or weak
                   conflict present. Note caveats.
        LOW:       Weak/dependent evidence or moderate conflict. Flag for review.
        VERY_LOW:  No meaningful support or overwhelmed by contradiction. Mark unverified.

    Calibration changes representation, NOT underlying evidence.
    """

    VERY_HIGH = "very_high"  # RI >= 80
    HIGH = "high"  # RI >= 65
    MODERATE = "moderate"  # RI >= 45
    LOW = "low"  # RI >= 25
    VERY_LOW = "very_low"  # RI < 25


class SignalID(str, Enum):
    """Canonical registry of all known signal identities."""

    EVIDENCE_STRENGTH = "evidence_strength"
    EVIDENCE_INDEPENDENCE = "evidence_independence"
    SOURCE_DIVERSITY = "source_diversity"
    TOPOLOGY_STRENGTH = "topology_strength"
    HUB_SCORE = "hub_score"
    BRIDGE_SCORE = "bridge_score"
    CONFLICT_PRESSURE = "conflict_pressure"
    TEMPORAL_STABILITY = "temporal_stability"


class SignalStatus(str, Enum):
    """Quality status for a single extracted signal."""

    MEASURED = "measured"  # Derived from full graph data
    ESTIMATED = "estimated"  # Derived but with incomplete data
    UNAVAILABLE = "unavailable"  # Cannot be computed (e.g., no provenance)
    DEFAULT = "default"  # Using policy default (no signal data)


@dataclass(frozen=True)
class RawSignal:
    """
    Raw measurement from one signal extractor, before normalization.

    Fields:
        name:              Signal identifier (matches ContributionCandidate.signal_name)
        raw_value:         The raw measurement (units depend on signal, may exceed [0,1])
        normalized_value:  Value after extractor-owned normalization (always in [0,1])
        status:            Quality status of this measurement
        metadata:          Extractor-specific diagnostic metadata
    """

    name: str
    raw_value: float
    normalized_value: float  # Owned by extractor (P1-2 fix)
    status: SignalStatus
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SignalManifest:
    """
    RECTIFIED (P0-4): Full derivation trace for one signal, one claim.

    This is NOT the same as an audit trail (which covers versioning).
    This covers derivation: WHY this signal has this value.

    Fields:
        signal_name:           Signal identifier
        extractor_version:     Version of the extractor that produced this signal
        raw_value:             Before normalization
        normalized_value:      After extractor-owned normalization
        normalization_strategy: Description of the strategy used (e.g., "log_scale")
        status:                Signal quality status
        quality_flags:         List of quality issues detected (e.g., ["low_sample"])
        dependency_list:       Which graph fields this signal depended on
        diagnostics:           Arbitrary extractor-specific diagnostic data
    """

    signal_id: SignalID
    extractor_version: str
    raw_value: float
    normalized_value: float
    normalization_strategy: str  # e.g. "log_scale", "linear", "step_function"
    status: SignalStatus
    quality_flags: tuple  # e.g. ("low_sample_count", "echo_chamber_risk")
    dependency_list: tuple  # e.g. ("support_aggregate", "topology.centrality")
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContributionCandidate:
    """
    RECTIFIED (P0-2): What the Fusion Engine receives for one signal.

    Fusion engine receives a list of ContributionCandidates and knows NOTHING
    about what the signals mean — it only knows: normalized_value, policy_weight,
    direction, and label. This is the key architectural fix that decouples Fusion
    from signal semantics.

    Fields:
        signal_name:       Identifier (opaque to Fusion)
        normalized_value:  In [0,1]
        policy_weight:     From policy (how important is this signal)
        direction:         "positive" (higher = more reliable) or "negative" (higher = less reliable)
        label:             Human-readable signal label for explanation generation
        raw_value:         Original pre-normalization value (for DecisionRecord)
    """

    signal_id: SignalID
    normalized_value: float
    policy_weight: float
    direction: str  # "positive" | "negative"
    label: str  # For explanation generation
    raw_value: float = 0.0  # Pre-normalization, for DecisionRecord


@dataclass(frozen=True)
class ContributionSet:
    """
    RECTIFIED (P0-2): The complete set of ContributionCandidates for one claim.

    This is what the Fusion Engine receives. It contains everything needed
    to compute the Reliability Index without the Fusion Engine knowing anything
    about individual signal semantics.
    """

    candidates: tuple  # Tuple[ContributionCandidate, ...]
    evidence_completeness: float  # Fraction of signals with actual measurements
    claim_id: str  # For logging/tracing


@dataclass(frozen=True)
class ComponentScore:
    """One signal's contribution to the final Reliability Index."""

    signal_id: SignalID
    normalized_value: float
    policy_weight: float
    adjusted_value: float
    contribution: float
    direction: str
    explanation: str

    @property
    def signal_name(self) -> str:
        """Backward-compatible alias for signal_id.value."""
        return self.signal_id.value


@dataclass(frozen=True)
class ReliabilityDecisionRecord:
    """
    RECTIFIED (P0-5): Full decision path for one claim's reliability score.

    Contains everything needed to understand exactly WHY a claim received
    its reliability index — from policy interactions to constraints activated.

    Invaluable for:
        - Benchmarking policy profiles against each other
        - Debugging unexpected scores
        - Future academic documentation
        - Phase 9 surfacing "why" explanations to users

    Fields:
        claim_id:                  Which claim this covers
        policy_interactions:       List of interactions applied (e.g., "echo_chamber_discount")
        constraints_activated:     List of constraints that fired (e.g., "no_evidence_cap")
        contribution_order:        Signal names in decreasing absolute contribution order
        raw_reliability:           Before constraints
        constrained_reliability:   After constraints, before clamping
        final_reliability:         After clamping to [0, 100]
        uncertainty_components:    What drove the uncertainty score
        dominant_adjustment:       The single most impactful policy interaction
    """

    claim_id: str
    policy_interactions: tuple  # e.g. ("echo_chamber_discount_applied",)
    constraints_activated: tuple  # e.g. ("no_evidence_cap: 60.0",)
    contribution_order: tuple  # signal names by descending |contribution|
    raw_reliability: float
    constrained_reliability: float
    final_reliability: float
    uncertainty_components: tuple  # (component_name, contribution) tuples
    dominant_adjustment: str


@dataclass(frozen=True)
class SignalVector:
    """
    All normalized signal measurements for one ClaimNode.
    All values are in [0.0, 1.0].

    Kept for backward compatibility with existing normalization tests.
    In the rectified architecture, ContributionSet is the primary fusion input.
    SignalVector is assembled from ContributionCandidates for serialization.
    """

    evidence_strength: float
    evidence_independence: float
    source_diversity: float
    topology_strength: float
    conflict_pressure: float
    temporal_stability: float
    evidence_completeness: float
    statuses: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ReliabilityExplanation:
    """Structured explanation for a Reliability Index."""

    summary: str
    strengths: tuple
    weaknesses: tuple
    dominant_signal: str
    limiting_signal: str
    recommendations: tuple


@dataclass(frozen=True)
class ReliabilityAudit:
    """Reproducibility audit trail for one ReliabilityMetadata."""

    policy_version: str
    policy_profile: str
    graph_fingerprint: str  # NEW (P1-3): which profile was active
    graph_schema_version: str
    fusion_algorithm: str
    normalization_version: str
    computed_at_run_id: str
    signal_extractor_versions: dict[str, str]
    registry_order: tuple  # NEW: ordered list of registered signal names


@dataclass(frozen=True)
class ReliabilityHistory:
    """
    RECTIFIED (P1-5): Architecture stub for confidence evolution tracking.

    Not active in production (requires cross-run storage).
    Architecture is wired up so Phase 9/10 can activate it.
    """

    claim_id: str
    history: tuple  # Tuple of (run_id, reliability_index, timestamp_iso) triples


@dataclass(frozen=True)
class ReliabilityMetadata:
    """
    The complete reliability profile for one ClaimNode.

    RECTIFIED: Now includes SignalManifest list and ReliabilityDecisionRecord.

    Fields:
        claim_id:               Links to KnowledgeGraph.nodes[claim_id]
        reliability_index:      Final score 0–100, EVIDENCE family only
                                 (evidence_strength, evidence_independence,
                                 source_diversity, conflict_pressure,
                                 temporal_stability). RECTIFIED (P1-4,
                                 external "reality check" review): no longer
                                 blends in graph-structure signals -- see
                                 importance_index for those.
        uncertainty_score:      Measurement uncertainty 0–100
        evidence_completeness:  Fraction of signals with actual measurements
        signal_vector:          All normalized signal measurements (for serialization)
        signal_manifests:       Per-signal derivation traces (NEW P0-4)
        component_scores:       Per-signal contributions (fully explainable),
                                 EVIDENCE family only
        decision_record:        Full policy decision path (NEW P0-5), EVIDENCE family only
        explanation:            Structured human-readable explanation
        calibration_label:      Human-friendly tier with semantic contract
        audit:                  Full reproducibility audit trail
        policy_version:         Which policy version produced this score
        importance_index:       NEW (P1-4): final score 0-100, IMPORTANCE
                                 family only (topology_strength, hub_score,
                                 bridge_score) -- how structurally central
                                 this claim is in the graph, independent of
                                 how well it is evidenced. Computed by the
                                 SAME generic fusion engine as
                                 reliability_index, just given a different,
                                 independently-reweighted ContributionSet.
        importance_component_scores: Per-signal contributions to importance_index
        importance_decision_record:  Decision path for importance_index
        schema_version:         "8.0"
    """

    claim_id: str
    reliability_index: float
    uncertainty_score: float
    evidence_completeness: float
    signal_vector: SignalVector
    signal_manifests: tuple  # Tuple[SignalManifest, ...] — NEW (P0-4)
    component_scores: tuple
    decision_record: ReliabilityDecisionRecord  # NEW (P0-5)
    explanation: ReliabilityExplanation
    calibration_label: CalibrationLabel
    audit: ReliabilityAudit
    policy_version: str
    importance_index: float = 0.0  # NEW (P1-4)
    importance_component_scores: tuple = ()  # NEW (P1-4)
    importance_decision_record: ReliabilityDecisionRecord | None = None  # NEW (P1-4)
    schema_version: str = "8.0"


@dataclass(frozen=True)
class ScoringGlobalStats:
    """Graph-wide statistics computed once and shared by all signal extractors."""

    max_support_count: int
    avg_support_count: float
    max_in_degree: int
    avg_degree: float
    max_contradiction_partners: int
    avg_contradiction_partners: float
    max_source_diversity: int
    max_temporal_confidence: float
    node_count: int
    partition_count: int
    contradiction_count: int
    supports_count: int


@dataclass(frozen=True)
class ScoredKnowledgeGraph:
    """
    Phase 8's canonical output: KnowledgeGraph + reliability overlay.

    The original KnowledgeGraph remains immutable.
    Reliability metadata lives in a separate dict indexed by claim_id.

    Design allows:
        - Multiple scoring policies on the same graph (via PolicyProfile)
        - Policy comparisons side by side
        - Future phases choosing which scoring profile to consume
    """

    graph: "KnowledgeGraph"
    reliability: dict[str, ReliabilityMetadata]
    policy_snapshot: dict[str, Any]
    policy_profile: str  # NEW (P1-3): which profile was used
    global_stats: ScoringGlobalStats
    run_id: str
    schema_version: str = "8.0"

    @property
    def total_scored(self) -> int:
        return len(self.reliability)

    @property
    def avg_reliability(self) -> float:
        if not self.reliability:
            return 0.0
        return sum(m.reliability_index for m in self.reliability.values()) / len(self.reliability)

    def get_reliability(self, claim_id: str) -> ReliabilityMetadata | None:
        return self.reliability.get(claim_id)

    def top_reliable(self, n: int = 10) -> list[ReliabilityMetadata]:
        return sorted(
            self.reliability.values(),
            key=lambda m: m.reliability_index,
            reverse=True,
        )[:n]

    def least_reliable(self, n: int = 10) -> list[ReliabilityMetadata]:
        return sorted(
            self.reliability.values(),
            key=lambda m: m.reliability_index,
        )[:n]


@dataclass(frozen=True)
class ExecutionStats:
    """Runtime and performance metrics for the Phase 8 engine."""

    total_runtime_seconds: float
    signal_extraction_seconds: float
    fusion_seconds: float
    registered_signal_count: int


@dataclass(frozen=True)
class KnowledgeStats:
    """Scientific and epistemic metrics for the evaluated graph."""

    total_claims_scored: int
    avg_reliability_index: float
    avg_uncertainty_score: float
    calibration_histogram: dict[str, int]  # e.g., {"VERY_HIGH": 12, "LOW": 3}
    high_reliability_count: int = 0  # RECTIFIED: claims with RI >= 65
    low_reliability_count: int = 0  # RECTIFIED: claims with RI < 45


@dataclass(frozen=True)
class Phase8Telemetry:
    """Complete telemetry payload for a Phase 8 execution."""

    policy_version: str
    policy_profile: str
    execution: ExecutionStats
    knowledge: KnowledgeStats


# ── Phase 9: Knowledge Access Layer ──────────────────────────────────────────


class QueryFamily(str, Enum):
    """The five fundamental query families Phase 9 supports."""

    POINT = "point"
    FILTER = "filter"
    TRAVERSAL = "traversal"
    AGGREGATION = "aggregation"
    EXPLAINABILITY = "explainability"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ProjectionLevel(str, Enum):
    """
    Projection level controlling how much data is returned.
    Clients request the level they need — responses are predictable.
    """

    SUMMARY = "summary"
    STANDARD = "standard"
    DETAILED = "detailed"
    EXPLAINABILITY = "explainability"
    FULL_AUDIT = "full_audit"


class NavigationMode(str, Enum):
    LOCAL = "local"
    PATH = "path"
    PROVENANCE = "provenance"


class ExplainabilityLevel(int, Enum):
    """
    Explainability depth for responses.
    Integer enum for easy >= comparison.
    """

    NONE = 0
    SUMMARY = 1
    DETAILED = 2
    FULL_AUDIT = 3


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    GRAPHML = "graphml"


class PredicateOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


@dataclass(frozen=True)
class ExecutionBudget:
    """
    Hard constraints for query execution to prevent resource exhaustion.

    Injected into ExecutionContext so services can check limits without
    hardcoded constants.
    """

    max_traversal_depth: int
    max_returned_rows: int
    timeout_ms: float
    max_export_size_mb: float

    @classmethod
    def from_config(cls) -> "ExecutionBudget":
        """Load execution budget from config/default.yaml."""
        config = get_config()
        api_cfg = config.get("knowledge_api", {})
        budget_cfg = api_cfg.get("execution_budget", {})
        return cls(
            max_traversal_depth=budget_cfg.get("max_traversal_depth", 5),
            max_returned_rows=budget_cfg.get("max_returned_rows", 10_000),
            timeout_ms=budget_cfg.get("timeout_ms", 30_000.0),
            max_export_size_mb=budget_cfg.get("max_export_size_mb", 100.0),
        )


@dataclass(frozen=True)
class ExecutionContext:
    """
    Shared execution context flowing through all pipeline stages.

    Replaces passing 10 arguments through every method.
    Immutable — stages create new contexts via dataclasses.replace().

    Fields:
        request_id:      Unique per-request UUID
        run_id:          Snapshot identifier
        api_version:     "1.0"
        query_family:    Which query family this is
        projection_level: Requested projection
        explain_level:   Requested explainability depth
        plan_id:         Set after planning (empty before)
        cache_hit:       Set after cache check
        planner_ms:      Set after planning
        execution_ms:    Set after execution
        total_ms:        Set after full pipeline
        rows_returned:   Set after execution
        budget:          ExecutionBudget for resource limits (NEW)
    """

    request_id: str
    run_id: str
    api_version: str
    query_family: str
    projection_level: str
    explain_level: int
    plan_id: str = ""
    cache_hit: bool = False
    planner_ms: float = 0.0
    execution_ms: float = 0.0
    total_ms: float = 0.0
    rows_returned: int = 0
    budget: ExecutionBudget = field(default_factory=ExecutionBudget.from_config)


@dataclass(frozen=True)
class ResponseMeta:
    """
    Metadata envelope attached to every Phase 9 response.
    Produced from ExecutionContext at the end of the pipeline.
    """

    request_id: str
    run_id: str
    api_version: str
    query_family: str
    execution_plan_id: str
    cache_hit: bool
    planner_ms: float
    execution_ms: float
    total_ms: float
    rows_returned: int
    projection_used: str


@dataclass(frozen=True)
class Phase9Stats:
    """Statistics for Phase 9 initialization."""

    nodes_indexed: int = 0
    edges_indexed: int = 0
    partitions_indexed: int = 0
    reliability_records_loaded: int = 0
    index_build_seconds: float = 0.0
    run_id: str = ""
    api_version: str = "1.0"
    capability_count: int = 0


# ── Phase 10: Human Knowledge Interaction Layer ────────────────────────────────


class WorkspaceType(str, Enum):
    """All registered knowledge workspace types."""

    RESEARCH = "research"
    RELIABILITY = "reliability"
    CONFLICT = "conflict"
    AUDIT = "audit"
    PROVENANCE = "provenance"
    STATISTICS = "statistics"
    TOPOLOGY = "topology"


class EpistemicLens(str, Enum):
    """
    The investigative perspective through which knowledge is interpreted.
    Different lenses activate different workspace compositions and
    presentation priorities without changing the underlying knowledge.
    """

    EXPLORATION = "exploration"  # General browsing
    RELIABILITY = "reliability"  # Trust evaluation
    EVIDENCE = "evidence"  # Evidence quality
    CONFLICT = "conflict"  # Contradiction investigation
    TOPOLOGY = "topology"  # Graph structure
    AUDIT = "audit"  # Full decision audit
    PROVENANCE = "provenance"  # Knowledge lineage


class InteractionIntent(str, Enum):
    """
    What the user is trying to accomplish.
    Intent → Lens → Workspace (deterministic selection chain).
    """

    EXPLORE_KNOWLEDGE = "explore_knowledge"
    EVALUATE_RELIABILITY = "evaluate_reliability"
    INVESTIGATE_CONFLICT = "investigate_conflict"
    AUDIT_REASONING = "audit_reasoning"
    TRACE_PROVENANCE = "trace_provenance"
    UNDERSTAND_STRUCTURE = "understand_structure"
    ANALYZE_STATISTICS = "analyze_statistics"


class InteractionEventType(str, Enum):
    """Every possible user action is one of these event types."""

    CLAIM_SELECTED = "claim_selected"
    CLAIM_DESELECTED = "claim_deselected"
    WORKSPACE_ACTIVATED = "workspace_activated"
    WORKSPACE_CLOSED = "workspace_closed"
    WORKSPACE_SUSPENDED = "workspace_suspended"
    WORKSPACE_RESUMED = "workspace_resumed"
    LENS_CHANGED = "lens_changed"
    FILTER_APPLIED = "filter_applied"
    FILTER_REMOVED = "filter_removed"
    SEARCH_SUBMITTED = "search_submitted"
    NAVIGATION_REQUESTED = "navigation_requested"
    EXPLAINABILITY_CHANGED = "explainability_changed"
    COMPARISON_STARTED = "comparison_started"
    COMPARISON_ENDED = "comparison_ended"
    EXPORT_REQUESTED = "export_requested"
    WORKSPACE_SERIALIZED = "workspace_serialized"
    WORKSPACE_RESTORED = "workspace_restored"
    COMMAND_DISPATCHED = "command_dispatched"
    NOTIFICATION_SENT = "notification_sent"


@dataclass(frozen=True)
class InteractionEvent:
    """An immutable event produced by every user action."""

    event_type: InteractionEventType
    payload: dict[str, Any]  # Event-specific data
    timestamp_ms: float  # Monotonic timestamp for ordering
    session_id: str


@dataclass(frozen=True)
class WorkspaceCapabilities:
    """Declares what a workspace is capable of."""

    supports_search: bool = True
    supports_comparison: bool = False
    supports_export: bool = True
    supports_graph: bool = False
    supports_audit: bool = False
    max_views: int = 4


@dataclass(frozen=True)
class WorkspaceVersion:
    """Versioning for workspace schema compatibility."""

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class WorkspaceStatus(str, Enum):
    """Lifecycle status of a workspace instance."""

    CREATED = "created"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class WorkspaceProfile:
    """
    Describes the cognitive characteristics of one workspace type.
    Behavior, not layout. Policy, not pixels.
    """

    workspace_type: WorkspaceType
    investigative_objective: str
    default_lens: EpistemicLens
    default_explainability: int  # ExplainabilityLevel value
    primary_views: tuple  # View names in composition order
    navigation_strategy: str
    max_results_per_page: int = 20
    capabilities: WorkspaceCapabilities = field(default_factory=WorkspaceCapabilities)
    version: WorkspaceVersion = field(default_factory=WorkspaceVersion)


@dataclass
class EpistemicState:
    """
    The single source of truth for the current interaction session.

    This is the session's epistemic memory:
        What is the user investigating?
        What have they selected?
        Where have they navigated?
        What filters are active?

    MUTABLE by design (session state evolves as the user interacts).
    Never persisted across sessions (transient).
    Serializable for workspace restoration within a session.
    """

    # Current investigative context
    workspace_type: WorkspaceType = WorkspaceType.RESEARCH
    active_lens: EpistemicLens = EpistemicLens.EXPLORATION
    intent: InteractionIntent = InteractionIntent.EXPLORE_KNOWLEDGE

    # Selection
    selected_claim_id: str | None = None
    comparison_claim_ids: tuple = field(default_factory=tuple)

    # Search + filters
    search_query: str = ""
    active_filters: dict[str, Any] = field(default_factory=dict)
    sort_field: str = "reliability_index"
    sort_order: str = "desc"
    page: int = 0
    page_size: int = 20

    # Explainability
    explainability_level: int = 0  # ExplainabilityLevel.NONE

    # Navigation
    breadcrumbs: list[dict[str, str]] = field(default_factory=list)
    navigation_history: list[str] = field(default_factory=list)

    # Workspace status
    workspace_status: WorkspaceStatus = WorkspaceStatus.CREATED

    # Run context
    run_id: str = ""
    session_id: str = ""


@dataclass(frozen=True)
class Phase10Stats:
    """Statistics for one Phase 10 dashboard session initialization."""

    workspaces_registered: int = 0
    api_version: str = "1.0"
    run_id: str = ""


# ── Phase 8 contract: Evolution ───────────────────────────────────────────────


@dataclass
class Topic:
    """A topic/theme grouping related claims. Produced by Phase 8."""

    name: str
    claim_ids: list[str] = field(default_factory=list)
    contradiction_count: int = 0

    @property
    def drift_score(self) -> float:
        """Drift score for this topic (0–100)."""
        if not self.claim_ids:
            return 0.0
        return min(100.0, (self.contradiction_count / len(self.claim_ids)) * 100)


@dataclass
class EvolutionChain:
    """Temporal chain of related claims showing how a belief evolved."""

    topic: str
    claim_ids: list[str]  # Ordered by timestamp
    stages: list[dict[str, Any]] = field(default_factory=list)


# ── Manifest and state ────────────────────────────────────────────────────────


@dataclass
class ManifestEntry:
    """Record of a completed phase. Written by ManifestManager after each phase."""

    run_id: str  # unique per execution
    phase: int
    timestamp: datetime
    duration_seconds: float
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    status: str  # pending | running | success | failed
    schema_version: str = "1.0"  # version manifest format
    error: str | None = None
    versions: dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineState:
    """Current state of pipeline execution. Persisted for resume capability."""

    started_at: datetime
    current_phase: int
    completed_phases: list[int] = field(default_factory=list)
    manifests: list[ManifestEntry] = field(default_factory=list)

    def is_resumable(self) -> bool:
        """Can pipeline be resumed from checkpoint?"""
        return len(self.manifests) > 0


# ── Internal embedding models (not exported) ────────────────────────────────
# These are used internally by Phase 5; they never cross the phase boundary.

# ── Phase 12: Scientific Validation Framework ─────────────────────────────────


class CertificationLevel(int, Enum):
    """
    8-level research certification hierarchy.
    Each level requires ALL previous levels — this is a gate, not a score.
    """

    PROTOTYPE = 0  # Code exists and runs
    ARCHITECTURALLY_VERIFIED = 1  # All architectural invariants pass
    ENGINEERING_VALIDATED = 2  # All engineering contracts satisfied
    SCIENTIFICALLY_EVALUATED = 3  # All 6 scientific domains evaluated
    STATISTICALLY_VERIFIED = 4  # Statistical rigor established
    REPRODUCIBLE = 5  # Independent reproduction confirmed
    PUBLICATION_READY = 6  # All publication criteria met
    RESEARCH_CERTIFIED = 7  # Living Research System established


class EvidenceGrade(str, Enum):
    """Evidence strength grades — borrowed from evidence-based disciplines."""

    A = "A"  # Multiple independent experiments
    B = "B"  # One experiment + baseline comparison
    C = "C"  # Single controlled experiment
    D = "D"  # Observational / retrospective
    E = "E"  # Hypothesis only


class ValidationDomain(str, Enum):
    ARCHITECTURAL = "architectural"
    ENGINEERING = "engineering"
    SCIENTIFIC = "scientific"
    OPERATIONAL = "operational"
    RESEARCH = "research"


class VerificationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    PENDING = "pending"
    # An experiment whose required reference/gold data does not exist yet.
    # Distinct from FAILED (which means "we measured it and it fell short")
    # and from PASSED (which means "we measured it and it met the bar") —
    # NOT_EVALUABLE means no real measurement was possible, and must never
    # be silently defaulted to a passing numeric value (e.g. 1.0) to make a
    # downstream index look complete.
    NOT_EVALUABLE = "not_evaluable"


class ScientificDomain(str, Enum):
    # The five canonical research-claim domains (RC1-RC5, frozen — see
    # evaluation/certification/claims.py). Each maps 1:1 to a research
    # claim backed (or not yet backed) by real reference data.
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"  # RC1
    RELATIONSHIP_RESOLUTION = "relationship_resolution"  # RC2
    KNOWLEDGE_GRAPH = "knowledge_graph"  # RC3
    RELIABILITY_SCORING = "reliability_scoring"  # RC4
    EXPLAINABILITY = "explainability"  # RC5
    # Not research-claim domains — these are engineering/infrastructure
    # properties (embedding determinism, retrieval index correctness), not
    # scientific claims about SMRITI's semantic accuracy. Verified, if at
    # all, by the ECI/architectural-rule layer, never by a "scientific
    # experiment" with a fabricated ground truth.
    EMBEDDING_QUALITY = "embedding_quality"
    RETRIEVAL = "retrieval"


class ArtifactReadinessLevel(str, Enum):
    """
    RECTIFIED (P1-6): Readiness is not binary. Mirrors standard journal
    reviewer language for the ordinal levels.

    RECTIFIED (P2, external "reality check" review): renamed from
    PublicationReadinessLevel. What this actually measures is whether the
    evidence and tooling this codebase can verify exist (artifact
    readiness) -- not a human-reviewer judgment of a paper's novelty,
    ethics, or writing quality, which no code can assess. See
    evaluation/certification/artifact_readiness.py.
    """

    COMPLETE = "complete"  # All criteria met — ready to submit
    MINOR_REVISION = "minor_revision"  # Small gaps, easily addressed
    MAJOR_REVISION = "major_revision"  # Significant work required
    NOT_READY = "not_ready"  # Fundamental gaps remain


class ExperimentLifecycleState(str, Enum):
    """
    RECTIFIED (P1-2): Formal lifecycle for experiments.
    Enforces pre-registration principle.
    """

    DRAFT = "draft"  # Being designed
    REGISTERED = "registered"  # Formally committed (acceptance criteria locked)
    APPROVED = "approved"  # Ready to execute
    EXECUTED = "executed"  # Results available
    VALIDATED = "validated"  # Results reviewed and accepted
    ARCHIVED = "archived"  # Permanently recorded


class GateDecision(str, Enum):
    """RECTIFIED (P0-1): Certification gate decision — not a score."""

    PASS = "pass"  # Gate criteria met — proceed to next gate
    BLOCK = "block"  # Gate criteria not met — certification stops here


@dataclass(frozen=True)
class ValidationPrinciple:
    """One of the 8 validation principles."""

    number: int
    name: str
    statement: str


@dataclass(frozen=True)
class VerificationRule:
    """A single executable architectural verification rule."""

    rule_id: str
    domain: ValidationDomain
    description: str
    category: str
    phase_scope: tuple
    acceptance_criterion: str


@dataclass(frozen=True)
class VerificationResult:
    rule_id: str
    status: VerificationStatus
    observed_value: str
    expected_value: str
    evidence: str
    timestamp_iso: str
    duration_ms: float


@dataclass(frozen=True)
class VerificationCoverage:
    category: str
    total_rules: int
    rules_passed: int
    rules_failed: int
    rules_skipped: int
    coverage_percentage: float


@dataclass(frozen=True)
class EngineeringVerificationIndex:
    """
    ECI -- answers 'Can the engineering architecture itself be trusted?'

    RECTIFIED (P2, "FINAL REVIEW" round): renamed from
    EngineeringConfidenceIndex. Every field here is a rule-coverage
    percentage (what fraction of this dimension's architectural/
    verification rules pass), not a statistical confidence measure --
    the same "confidence implies a validated statistical property this
    doesn't have" naming problem already fixed for
    ScientificConfidenceIndex -> ResearchEvidenceCoverage. The
    abbreviation ECI is kept (it appears throughout the paper and
    reports) but now expands to Engineering Verification Index.
    """

    architecture_confidence: float
    runtime_confidence: float
    infrastructure_confidence: float
    observability_confidence: float
    governance_confidence: float
    integration_confidence: float
    compliance_confidence: float
    overall_confidence: float  # Continuous 0–100 (RECTIFIED P0-2: not a gate)
    engineering_readiness_level: int  # 0–5


@dataclass(frozen=True)
class EvaluationProtocol:
    """
    RECTIFIED (P1-1): Full protocol specification for an experiment.

    Every experiment must have a protocol committed before execution.
    """

    protocol_id: str
    experiment_id: str
    execution_steps: tuple  # Ordered steps as strings
    stopping_criteria: str  # When to stop early
    expected_runtime_seconds: float
    failure_conditions: tuple  # What constitutes a failure
    acceptance_logic: str  # How to decide pass/fail
    rollback_procedure: str  # How to undo if needed
    reviewer_notes: str


@dataclass(frozen=True)
class ExperimentDesign:
    """
    Complete experimental design specification.
    RECTIFIED (P1-2): Now includes lifecycle_state.

    RECTIFIED (P0-A, "FINAL REVIEW" round): _evaluate_acceptance() in
    evaluation/scientific/experiment.py used to assume every metric in
    acceptance_criteria is higher-is-better (`metrics[metric] < threshold`
    -> FAILED). EXP-003's contradiction_violation_rate is lower-is-better
    (threshold 0.0 is a MAXIMUM, not a minimum) -- under the old generic
    logic, a violation rate of 0.10 evaluates `0.10 < 0.0` -> False ->
    PASSED, exactly backwards. assess_research_claims() already had its
    own correct special-case handling for this (`inverted = claim_id ==
    "RC3"`), but that only protected the CLAIM-level assessment, not the
    EXPERIMENT-level ExperimentResult.status that same claim's evidence
    is built from, and the hardcoding was duplicated with a different
    keying scheme (claim_id there, metric name here) rather than sharing
    one source of truth. acceptance_directions makes the direction part
    of the experiment specification itself: metric name -> "higher_is_better"
    or "lower_is_better". A metric absent from this dict defaults to
    "higher_is_better" (the correct default for every experiment except
    EXP-003 today), so this is purely additive for EXP-001/002/004/005.
    """

    experiment_id: str
    scientific_domain: ScientificDomain
    hypothesis: str
    independent_variables: tuple
    dependent_variables: tuple
    controlled_variables: tuple
    confounding_variables: tuple
    ground_truth_version: str
    acceptance_criteria: dict[str, float]
    random_seed: int
    lifecycle_state: ExperimentLifecycleState = ExperimentLifecycleState.REGISTERED
    acceptance_directions: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    run_id: str
    metrics: dict[str, float]
    raw_outputs: dict[str, Any]
    execution_time_seconds: float
    manifest_path: str | None
    status: VerificationStatus


@dataclass(frozen=True)
class StatisticalAnalysis:
    metric_name: str
    values: tuple
    mean: float
    std_dev: float
    median: float
    min_value: float
    max_value: float
    ci_lower: float
    ci_upper: float
    coefficient_of_variation: float
    n_samples: int


@dataclass(frozen=True)
class EffectSize:
    metric_name: str
    condition_a: str
    condition_b: str
    cohens_d: float
    magnitude: str


@dataclass(frozen=True)
class ReproducibilityAssessment:
    experiment_id: str
    n_runs: int
    mean_metric: float
    std_dev_metric: float
    coefficient_of_variation: float
    reproducibility_level: str
    is_reproducible: bool


@dataclass(frozen=True)
class ThreatToValidity:
    threat_id: str
    category: str
    description: str
    mitigation: str
    residual_risk: str


@dataclass(frozen=True)
class ScienceEvidence:
    """One piece of scientific evidence from one experiment."""

    evidence_id: str
    experiment_id: str
    scientific_domain: ScientificDomain
    metric_name: str
    observed_value: float
    threshold: float
    grade: EvidenceGrade
    supports_claim: str
    statistical_analysis: StatisticalAnalysis | None


@dataclass(frozen=True)
class ResearchClaim:
    """
    RECTIFIED (P0-3): Enriched scientific claim object.

    Original was metadata-only (statement, confidence, supported).
    Now a proper scientific object with research question, hypotheses,
    assumptions, threats, and applicability.
    """

    claim_id: str
    statement: str
    scientific_domain: ScientificDomain
    evidence_ids: tuple
    evidence_grade: EvidenceGrade
    is_supported: bool
    confidence_score: float  # Continuous 0.0–1.0

    # RECTIFIED (P0-3): Scientific fields
    research_question: str = ""  # The question this claim addresses
    null_hypothesis: str = ""  # H₀: what would falsify this claim
    assumptions: tuple = ()  # Assumptions underlying this claim
    threats: tuple = ()  # Known threats to this specific claim
    supporting_limitations: tuple = ()  # Limitations the evidence rests on
    applicability: str = ""  # Where this claim is valid


@dataclass(frozen=True)
class AssumptionRecord:
    """
    RECTIFIED (P1-3): First-class system assumption record.

    Every major assumption underlying SMRITI's outputs should be registered.

    RECTIFIED (P0-B, "FINAL REVIEW" round): affected_claims previously used
    a stale RC-00N identifier scheme (RC-001..RC-006) that never matched
    the frozen canonical claim registry (RC1..RC5, evaluation/certification/
    claims.py) -- get_assumptions_for_claim("RC1") could never find an
    assumption recorded as affected_claims=("RC-001",). Several
    validation_experiment values were also conceptually wrong (an
    experiment ID that exists and runs, but does not actually test the
    assumption it was attached to -- e.g. a FAISS-accuracy assumption
    pointed at the reliability-metamorphic experiment). validation_status
    makes the actual epistemic state explicit rather than implied by
    whether validation_experiment happens to be non-null:
        "validated"           -- validation_experiment genuinely,
                                  directly tests this specific assumption.
        "partially_validated"  -- validation_experiment provides indirect
                                  or end-to-end evidence (e.g. a downstream
                                  task-level metric that would degrade if
                                  this assumption were false, but does not
                                  isolate the assumption itself).
        "unvalidated"          -- no current experiment tests this
                                  assumption at all; validation_experiment
                                  must be None whenever this is set, rather
                                  than pointing at an experiment that does
                                  not actually exercise the claim (the
                                  specific bug this fix closes).
    """

    assumption_id: str
    description: str
    affected_modules: tuple  # Which modules rely on this assumption
    affected_claims: (
        tuple  # Which research claims depend on this -- must be a subset of CANONICAL_CLAIM_IDS
    )
    phase: int  # Which phase makes this assumption
    risk_if_violated: str  # "low" | "medium" | "high"
    validation_experiment: str | None  # Which experiment tests this, or None if unvalidated
    validation_status: str = "unvalidated"  # "validated" | "partially_validated" | "unvalidated"


@dataclass(frozen=True)
class LimitationRecord:
    """
    RECTIFIED (P1-4): Known architectural limitation record.

    A limitation is a known boundary, NOT a risk.
    Limitations are architectural facts; threats are risks.
    """

    limitation_id: str
    description: str
    affected_module: str
    affected_claims: tuple
    severity: str  # "minor" | "moderate" | "significant"
    possible_future_work: str


@dataclass(frozen=True)
class EvidenceConflict:
    """
    RECTIFIED (P1-5): A conflict between two pieces of evidence on the same claim.
    """

    conflict_id: str
    claim_id: str
    evidence_a_id: str  # Experiment supporting the claim
    evidence_b_id: str  # Experiment contradicting the claim
    conflict_type: str  # "contradicts" | "partially_contradicts"
    resolution: str  # How conflict was resolved
    confidence_impact: float  # Change to claim confidence score
    reviewer_note: str


@dataclass(frozen=True)
class CertificationGateResult:
    """
    RECTIFIED (P0-1): Result of one certification gate evaluation.

    Certification is a sequence of pass/block gates, NOT a weighted average.
    """

    gate_number: int
    gate_name: str
    decision: GateDecision
    rationale: str
    metric_observed: float | None = None
    metric_required: float | None = None
    blocking_reason: str = ""


@dataclass(frozen=True)
class ResearchEvidenceCoverage:
    """
    RECTIFIED (P2, external "reality check" review): renamed from
    ScientificConfidenceIndex. "Confidence" implied a validated statistical
    confidence measure; what this dataclass actually reports is coverage --
    how much of the system has been measured at all, and by what grade of
    evidence, not a calibrated probability that SMRITI's claims are true.
    Continuous 0-100. Separate from the certification gate (see gates.py).

    RECTIFIED (P1-A, "FINAL REVIEW" round): the pass-rate field is named
    experiment_pass_rate, not accuracy_confidence, and is computed as
    passed / TOTAL registered experiments (not passed / measured). The
    previous accuracy_confidence = passed / measured formula let a
    NOT_EVALUABLE experiment silently vanish from its own denominator --
    e.g. 4 PASSED + 1 NOT_EVALUABLE reported 100% "accuracy" instead of
    80%. measurement_coverage = measured / total (renamed from
    statistical_support, same formula) is reported alongside it so a
    missing experiment cannot masquerade as "not a failure, therefore
    excluded" in either number.
    """

    experiment_pass_rate: float
    consistency_confidence: float
    robustness_confidence: float
    generalization_confidence: float
    interpretability_confidence: float
    measurement_coverage: float
    overall_coverage: float  # Continuous 0–100
    evidence_grade: EvidenceGrade


@dataclass(frozen=True)
class ArtifactReadinessAssessment:
    """
    RECTIFIED (P1-6): Readiness level (not binary).
    RECTIFIED (P2, external "reality check" review): renamed from
    PublicationReadinessAssessment -- see ArtifactReadinessLevel.
    """

    readiness_level: ArtifactReadinessLevel  # COMPLETE / MINOR / MAJOR / NOT_READY
    criteria_met: tuple
    criteria_missing: tuple
    criteria_partial: tuple
    revision_notes: str

    # Backward compat
    @property
    def overall_ready(self) -> bool:
        return self.readiness_level == ArtifactReadinessLevel.COMPLETE

    @property
    def missing_criteria(self) -> tuple:
        return self.criteria_missing


@dataclass(frozen=True)
class EvaluationManifest:
    """
    RECTIFIED (P2-1): Evaluation-specific reproducibility manifest.

    Different from RuntimeManifest (Phase 11) — captures evaluation parameters.
    """

    manifest_id: str
    run_id: str
    experiment_ids: tuple
    ground_truth_versions: dict[str, str]  # experiment_id → GT version
    policy_version: str
    random_seeds: dict[str, int]  # experiment_id → seed
    metrics_evaluated: tuple
    acceptance_criteria: dict[str, float]
    software_versions: dict[str, str]  # library → version
    hardware_description: str  # real OS/CPU/RAM/GPU string, detected at run time
    created_at: str


@dataclass(frozen=True)
class MetricDefinition:
    """
    RECTIFIED (P2-3): First-class metric object.

    Metrics are no longer hardcoded — they are registered objects.
    """

    metric_name: str
    definition: str
    formula: str
    units: str
    range_min: float
    range_max: float
    interpretation: str  # What a high/low score means
    direction: str  # "higher_is_better" | "lower_is_better"
    dependencies: tuple  # Which other metrics this requires


@dataclass(frozen=True)
class DatasetSuitabilityAssessment:
    """
    RECTIFIED (P2-2): Assesses whether a dataset is appropriate for an experiment.
    """

    dataset_id: str
    experiment_id: str
    coverage_score: float  # 0.0–1.0 domain coverage
    balance_score: float  # Class/type balance
    bias_risk: str  # "low" | "medium" | "high"
    representativeness: str  # How representative of real usage
    noise_level: str  # "low" | "medium" | "high"
    completeness_score: float  # Fraction with complete annotations
    missing_value_rate: float  # Fraction with missing fields
    ground_truth_quality: float  # Overall GT quality score
    is_suitable: bool


@dataclass(frozen=True)
class CertificationReport:
    """
    RECTIFIED (P0-big): CertificationReport is ONE artifact in the package.

    The gate-based certification record (not the top-level container).
    overall_confidence_index is kept for backward compatibility with tests
    but is no longer used to determine certification level.
    """

    report_id: str
    run_id: str
    timestamp_iso: str

    # Part 2 outputs
    verification_results: tuple
    verification_coverage: tuple
    engineering_confidence: EngineeringVerificationIndex

    # Part 3 outputs
    experiment_results: tuple
    science_evidence: tuple
    research_claims: tuple

    # Part 4 outputs
    statistical_analyses: tuple
    reproducibility_assessments: tuple
    threats_to_validity: tuple
    research_evidence_coverage: ResearchEvidenceCoverage

    # Part 5 outputs (RECTIFIED)
    artifact_readiness: ArtifactReadinessAssessment  # Now ordinal
    gate_results: tuple  # NEW: gate-by-gate decisions
    certification_level: CertificationLevel
    certification_rationale: str

    # Summary metrics
    total_rules_passed: int
    total_rules_failed: int
    engineering_confidence_index: float
    research_evidence_coverage_index: float
    overall_confidence_index: float  # Kept for backward compat (no longer drives gates)

    schema_version: str = "12.1"


@dataclass(frozen=True)
class ResearchAssurancePackage:
    """
    RECTIFIED (P0-big): Top-level container for all Phase 12 outputs.

    CertificationReport is one component of this package.
    This architecture scales to multiple publications and repeated evaluation cycles.
    """

    package_id: str
    run_id: str
    created_at: str
    certification_report: CertificationReport
    experiment_registry: tuple  # All ExperimentDesign objects
    evidence_ledger: tuple  # All ScienceEvidence objects
    evaluation_manifest: "EvaluationManifest"
    assumption_registry: tuple  # All AssumptionRecord objects
    limitation_registry: tuple  # All LimitationRecord objects
    evidence_conflicts: tuple  # All resolved EvidenceConflict objects
    integrity_checksums: dict[str, str]  # artifact → SHA256
    schema_version: str = "12.1"

    @property
    def certification_level(self) -> CertificationLevel:
        return self.certification_report.certification_level

    @property
    def eci(self) -> float:
        return self.certification_report.engineering_confidence_index

    @property
    def evidence_coverage(self) -> float:
        return self.certification_report.research_evidence_coverage_index


@dataclass(frozen=True)
class Phase12Stats:
    """Statistics for one Phase 12 execution."""

    rules_executed: int = 0
    rules_passed: int = 0
    rules_failed: int = 0
    experiments_run: int = 0
    evidence_items_produced: int = 0
    research_claims_assessed: int = 0
    certification_level: int = 0
    gates_passed: int = 0
    gates_blocked: int = 0
    eci: float = 0.0
    evidence_coverage: float = 0.0
    total_runtime_seconds: float = 0.0
