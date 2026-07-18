"""
Data models for SMRITI.
Define once, use everywhere.
These are the contracts between phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


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
    SEG_EMPTY_SENTENCE_DISCARDED   = "SEG001"   # Empty string after strip
    SEG_VERY_LONG_SENTENCE         = "SEG002"   # Exceeds max_sentence_chars
    SEG_UNKNOWN_STRUCTURE          = "SEG003"   # Structural element not recognised
    SEG_MALFORMED_TABLE            = "SEG004"   # Table could not be parsed
    SEG_CODE_BLOCK_SKIPPED         = "SEG005"   # Code block skipped (V1)
    CTX_STACK_IMBALANCE            = "CTX001"   # Context stack depth mismatch
    VAL_DUPLICATE_SENTENCE_ID      = "VAL001"   # Two sentences share an ID (fatal)
    VAL_INVALID_POSITION_ORDER     = "VAL002"   # Non-monotonic positions (fatal)
    VAL_INVALID_CONTEXT            = "VAL003"   # Context string malformed


# ── Phase 4 Warning Codes ─────────────────────────────────────────────────────

class ClaimWarning(str, Enum):
    """Warning codes specific to Phase 4 claim construction."""
    CLM_PARSER_FAILURE          = "CLM001"
    CLM_BOUNDARY_AMBIGUITY      = "CLM002"
    CLM_STRUCTURE_UNAVAILABLE   = "CLM003"
    CLM_FALLBACK_ACTIVATED      = "CLM004"
    CLM_EMPTY_ASSERTION         = "CLM005"
    CLM_DUPLICATE_CLAIM_ID      = "CLM006"  # Fatal if inconsistent
    CLM_INVALID_PROVENANCE      = "CLM007"
    CLM_VALIDATION_FAILURE      = "CLM008"
    CLM_EXCEEDED_MAX_CLAIMS     = "CLM009"
    CLM_UNSUPPORTED_SYNTAX      = "CLM010"


class ExtractionMode(str, Enum):
    STRUCTURED    = "structured"
    PARTIAL       = "partial"
    LEXICAL       = "lexical"
    WHOLE_SENTENCE = "whole_sentence"


class Modality(str, Enum):
    CERTAIN    = "certain"
    POSSIBLE   = "possible"
    PROBABLE   = "probable"
    IMPOSSIBLE = "impossible"
    REQUIRED   = "required"
    UNKNOWN    = "unknown"


class BoundaryReason(str, Enum):
    """Enum for deterministic boundary detection reasons."""
    SINGLE_ASSERTION       = "single_assertion"
    COORDINATED_PREDICATE  = "coordinated_predicate"
    INDEPENDENT_CLAUSE     = "independent_clause"
    PARSE_FAILED           = "parse_failed"
    CONDITIONAL_SPLIT      = "conditional_split"      # reserved
    RELATIVE_CLAUSE        = "relative_clause"
    COORDINATION           = "coordination"


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
    context: str           # "Python > Generators" or "" if at root
    position: int
    char_start: int
    char_end: int
    source_path: Path
    origin_block_type: str   # e.g., "paragraph", "heading", etc.
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

    @property
    def has_warnings(self) -> bool:
        return len(self.extraction_warnings) > 0

    @property
    def is_empty(self) -> bool:
        return len(self.normalized_text.strip()) == 0


# ── Phase 4 contract: SemanticSentence → Claim ───────────────────────────────

@dataclass(frozen=True)
class StructuredAssertion:
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    negation_marker: Optional[str] = None
    modality_marker: Optional[str] = None

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
    attributed_to: Optional[str] = None
    is_quoted: bool = False


@dataclass(frozen=True)
class ClaimProvenance:
    sentence_id: str
    document_id: str
    source_path: Path
    sentence_context: str
    sentence_position: int


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
    """
    claim_id: str
    sentence_id: str
    document_id: str
    text: str
    content_hash: str
    context: str
    source_path: Path
    extraction_mode: ExtractionMode
    structured_assertion: Optional[StructuredAssertion]
    assertion_metadata: AssertionMetadata
    provenance: ClaimProvenance
    schema_version: str = "4.0"
    rule_version: str = "1.0"

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
    def subject(self) -> Optional[str]:
        return self.structured_assertion.subject if self.structured_assertion else None

    @property
    def predicate(self) -> Optional[str]:
        return self.structured_assertion.predicate if self.structured_assertion else None

    @property
    def object(self) -> Optional[str]:
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
    model_signature: str   # Deterministic: SHA256(provider:model_name:revision)
    embedding_family: str = ""   # e.g. "SentenceTransformer", "OpenAI", "BGE"
    checkpoint_sha: str = ""     # Content-addressable checkpoint hash if available


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


# ── Phase 6 contract: Retrieval → Contradiction ──────────────────────────────

@dataclass
class CandidatePair:
    """Two claims that might contradict. Produced by Phase 6, consumed by Phase 7."""
    claim_a_id: str
    claim_b_id: str
    similarity_score: float     # Cosine similarity from FAISS


# ── Phase 7 contract: Contradiction → Scoring ────────────────────────────────

@dataclass
class Contradiction:
    """A detected contradiction between two claims. Produced by Phase 7."""
    claim_a_id: str
    claim_b_id: str
    contradiction_type: ContradictionType
    nli_confidence: float       # Gate 2 output
    similarity_score: float     # Gate 1 output
    temporal_distance_days: int
    severity_score: float       # Gate 3 final score
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def __repr__(self) -> str:
        return (
            f"Contradiction({self.claim_a_id[:20]} vs {self.claim_b_id[:20]}, "
            f"type={self.contradiction_type}, severity={self.severity_score:.2f})"
        )


# ── Phase 8 contract: Evolution ───────────────────────────────────────────────

@dataclass
class Topic:
    """A topic/theme grouping related claims. Produced by Phase 8."""
    name: str
    claim_ids: List[str] = field(default_factory=list)
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
    claim_ids: List[str]                    # Ordered by timestamp
    stages: List[Dict[str, Any]] = field(default_factory=list)


# ── Manifest and state ────────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    """Record of a completed phase. Written by ManifestManager after each phase."""
    run_id: str                             # unique per execution
    phase: int
    timestamp: datetime
    duration_seconds: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str                             # pending | running | success | failed
    schema_version: str = "1.0"            # version manifest format
    error: Optional[str] = None
    versions: Dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineState:
    """Current state of pipeline execution. Persisted for resume capability."""
    started_at: datetime
    current_phase: int
    completed_phases: List[int] = field(default_factory=list)
    manifests: List[ManifestEntry] = field(default_factory=list)

    def is_resumable(self) -> bool:
        """Can pipeline be resumed from checkpoint?"""
        return len(self.manifests) > 0


# ── Internal embedding models (not exported) ────────────────────────────────
# These are used internally by Phase 5; they never cross the phase boundary.

