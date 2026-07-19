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


# ── Phase 6 contract: CandidatePair → RelationshipSet ─────────────────────────

class RelationshipType(str, Enum):
    """
    The semantic relationship type between two Claims.

    ⚠️  This enum is governed by the Relationship Ontology Specification
    in docs/relationship_ontology.md. Any change to these values requires
    updating that document first.

    Rules:
        - CONTRADICTS is symmetric; SUPPORTS and REFINES are directional.
        - UNKNOWN must never be persisted to Phase 7.
        - NEUTRAL should not be persisted to Phase 7 (configurable).
    """
    CONTRADICTS   = "contradicts"    # Symmetric: claims assert opposing facts
    SUPPORTS      = "supports"       # Directional: claim_a reinforces claim_b
    REFINES       = "refines"        # Directional: claim_a qualifies/narrows claim_b
    NEUTRAL       = "neutral"        # Symmetric: semantically close, no direction
    UNKNOWN       = "unknown"        # Resolver could not classify (never persist)


class RelationshipDirection(str, Enum):
    """
    Direction of a relationship between claim_a and claim_b.

    Ontology constraints:
        CONTRADICTS → always SYMMETRIC
        SUPPORTS    → always A_TO_B or B_TO_A
        REFINES     → always A_TO_B or B_TO_A
        NEUTRAL     → always SYMMETRIC
    """
    A_TO_B      = "a_to_b"       # claim_a → claim_b
    B_TO_A      = "b_to_a"       # claim_b → claim_a
    SYMMETRIC   = "symmetric"    # Both directions are equivalent


class LifecycleStage(str, Enum):
    """
    Explicit lifecycle of a claim pair through the Phase 6 pipeline.

    Every object in the pipeline belongs to exactly one stage.
    Transitions are one-way; no object can move backward.

    CANDIDATE              → discovered by ANN, not yet validated
    VALIDATED_CANDIDATE    → passed all candidate validation checks
    EVIDENCE               → NLI inference completed; raw scores available
    CALIBRATED_EVIDENCE    → scores adjusted by ConfidenceCalibrator
    RESOLVED               → RelationshipType assigned by resolver
    VALIDATED_RELATIONSHIP → passed confidence and consistency checks
    RELATIONSHIP           → immutable Relationship object constructed
    REJECTED               → failed at any stage; not in final RelationshipSet
    """
    CANDIDATE              = "candidate"
    VALIDATED_CANDIDATE    = "validated_candidate"
    EVIDENCE               = "evidence"
    CALIBRATED_EVIDENCE    = "calibrated_evidence"
    RESOLVED               = "resolved"
    VALIDATED_RELATIONSHIP = "validated_relationship"
    RELATIONSHIP           = "relationship"
    REJECTED               = "rejected"


@dataclass(frozen=True)
class RetrievalSearchParameters:
    """
    Parameters used during ANN search for this candidate pair.

    Enables exact reproduction of retrieval behavior during debugging or replay.
    """
    top_k: int
    sim_threshold: float
    index_type: str         # e.g. "faiss_flat_ip"
    index_version: str      # e.g. "1.0"


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
    A pair of semantically similar claims discovered by ANN search.

    This is the entry ticket to the classification pipeline.
    Every CandidatePair that passes validation proceeds to NLI evidence generation.

    Fields:
        claim_id_a:           First claim's ID (always ≤ claim_id_b lexicographically)
        claim_id_b:           Second claim's ID
        cosine_similarity:    Cosine similarity from FAISS ANN search (0.0–1.0)
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
    ENTAILMENT    = "entailment"
    NEUTRAL       = "neutral"
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
    predicted_label: str         # "entailment" | "neutral" | "contradiction"
    raw_confidence: float        # max of the three scores, before calibration


@dataclass(frozen=True)
class RelationshipEvidence:
    """
    Complete evidence record for one CandidatePair.

    Contains:
        - pair:             The candidate pair this evidence was gathered for
        - cosine_similarity: From Phase 5 ANN search
        - nli_scores:       Raw NLI evidence (pure scores)
        - calibrated_confidence: Calibrated confidence after ConfidenceCalibrator
        - inference_metadata:  Model + runtime metadata (separated from scores)
        - lifecycle_stage:  EVIDENCE or CALIBRATED_EVIDENCE

    Replaces the original flat RelationshipEvidence which mixed scores and metadata.
    """
    pair: "CandidatePair"
    cosine_similarity: float
    nli_scores: "NLIScores"
    calibrated_confidence: float          # After calibration; use this for thresholding
    inference_metadata: "InferenceMetadata"
    lifecycle_stage: "LifecycleStage" = LifecycleStage.EVIDENCE

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
        search_parameters:    Full ANN search parameters for exact reproduction
        classifier_model:     NLI model name
        classifier_version:   NLI model version
        resolver_version:     Resolver policy version
        calibrator_version:   ConfidenceCalibrator version
        cosine_similarity:    Similarity from ANN search
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
    replay_id: Optional[str] = None


@dataclass(frozen=True)
class RelationshipQuality:
    """Pre-computed quality diagnostics for a Relationship."""
    cosine_above_threshold: bool
    nli_above_threshold: bool
    evidence_consistent: bool   # entailment+contradiction don't both exceed threshold
    calibration_applied: bool   # Whether ConfidenceCalibrator changed the confidence
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
    relationships: List["Relationship"]
    total_candidates: int
    total_validated: int
    total_rejected: int
    rejected_reasons: Dict[str, int]
    run_id: str
    version_info: "SchemaVersionInfo" = None
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None
    replay_manifest_path: Optional[Path] = None

    def __post_init__(self):
        if self.version_info is None:
            self.version_info = SchemaVersionInfo(
                schema_version="6.0",
                migration_version="6.0",
                compatibility_version="6.0",
            )

    @property
    def total_relationships(self) -> int:
        return len(self.relationships)

    @property
    def contradictions(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.CONTRADICTS]

    @property
    def supports(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refinements(self) -> List["Relationship"]:
        return [r for r in self.relationships
                if r.relationship_type == RelationshipType.REFINES]


class RelationshipDeduplicationPolicy(str, Enum):
    """
    Policy for handling duplicate relationships (same pair, same type, different runs).

    KEEP_FIRST:     Keep the relationship from the first run that discovered it.
    KEEP_LATEST:    Keep the relationship from the most recent run.
    KEEP_HIGHEST_CONFIDENCE: Keep the relationship with the highest calibrated confidence.
    KEEP_ALL:       Keep all copies (dangerous for graph construction; use for audit).
    """
    KEEP_FIRST              = "keep_first"
    KEEP_LATEST             = "keep_latest"
    KEEP_HIGHEST_CONFIDENCE = "keep_highest_confidence"
    KEEP_ALL                = "keep_all"


class ConflictResolutionPolicy(str, Enum):
    """
    Policy for resolving type conflicts between runs (same pair, different RelationshipType).

    Example: Run 1 says SUPPORTS, Run 2 says CONTRADICTS — which wins?

    LATEST_WINS:       The most recent run's classification wins.
    HIGHEST_CONFIDENCE: The classification with highest calibrated_confidence wins.
    MOST_SPECIFIC:      Priority: CONTRADICTS > REFINES > SUPPORTS > NEUTRAL > UNKNOWN.
    CONSERVATIVE:       Only keep the relationship if all runs agree on the type.
    """
    LATEST_WINS         = "latest_wins"
    HIGHEST_CONFIDENCE  = "highest_confidence"
    MOST_SPECIFIC       = "most_specific"
    CONSERVATIVE        = "conservative"

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
    FOUNDATIONAL_CLAIM  = "foundational_claim"   # High centrality, many SUPPORTS edges
    BRIDGE_CLAIM        = "bridge_claim"          # Articulation point: removal disconnects partition
    EVIDENCE_HUB        = "evidence_hub"          # Many incoming SUPPORTS edges
    REFINEMENT_ROOT     = "refinement_root"       # Source of many REFINES edges
    PERIPHERAL_CLAIM    = "peripheral_claim"      # Low degree, mostly disconnected
    LEAF_CLAIM          = "leaf_claim"            # No outgoing semantic edges
    UNCLASSIFIED        = "unclassified"          # Insufficient topology data


class TemporalStatus(str, Enum):
    """Status of temporal analysis for a contradiction boundary."""
    EVOLUTION_CHAIN     = "evolution_chain"       # Reliable semantic timestamps → evolved
    STATIC_PARTITION    = "static_partition"      # No timestamp ordering → competing beliefs
    UNRESOLVED_CONFLICT = "unresolved_conflict"   # Identical timestamps → cannot determine
    NO_TIMESTAMP        = "no_timestamp"          # Claim.timestamp unavailable → disabled


@dataclass(frozen=True)
class TopologyMetrics:
    """
    Graph-derived structural information for one ClaimNode.
    Computed by TopologyAnalyzer within each partition.

    Bridge detection uses NetworkX articulation_points, not degree-heuristics.
    Density is computed as directed: edges / (n * (n-1)), n = partition size.
    """
    degree: int                      # Total edges (in + out)
    in_degree: int                   # Incoming edges (being supported/contradicted)
    out_degree: int                  # Outgoing edges (supporting/contradicting others)
    is_bridge: bool                  # True articulation point (NetworkX algorithm)
    is_hub: bool                     # Significantly above-average degree (config-driven)
    partition_id: str                # Which partition this node belongs to
    centrality: float = 0.0          # Normalized in-degree centrality (in_degree / (N-1))


@dataclass(frozen=True)
class SupportAggregate:
    """
    Aggregated semantic support for one ClaimNode within its partition.

    PROVENANCE ROOT DEFINITION:
    This aggregate includes ALL transitive supporting claims. In a chain where 
    A -> B -> C, both A and B are considered supporting claims of C. 
    The supporting_claim_ids tuple contains the unique IDs of all such claims, 
    ensuring no claim is double-counted even if multiple paths exist.
    """
    support_count: int
    weighted_confidence: float
    supporting_claim_ids: tuple
    evidence_summary: str         # Human-readable summary


@dataclass(frozen=True)
class TemporalMetadata:
    """
    Temporal evolution metadata for one contradiction boundary.

    RECTIFIED: populated from Claim.timestamp (semantic timestamp),
    never from filesystem st_mtime. If Claim.timestamp is None,
    status is NO_TIMESTAMP rather than inferring from the filesystem.
    """
    status: TemporalStatus
    earlier_claim_id: Optional[str]  # claim_id of the earlier claim (if EVOLUTION_CHAIN)
    later_claim_id: Optional[str]    # claim_id of the later claim (if EVOLUTION_CHAIN)
    time_delta_days: Optional[float] # Days between timestamps
    temporal_confidence: float       # Confidence in the temporal ordering (0.0–1.0)


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
    partition_id: Optional[str] = None
    stable_partition_label: Optional[str] = None  # Incremental-friendly label (P2-5)


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
    def partition_id(self) -> Optional[str]:
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
        - All nodes within a partition are reachable via SUPPORTS/REFINES
        - Partition membership is exclusive
    """
    partition_id: str                        # SHA256(sorted_node_ids)[:12] — deterministic
    stable_partition_label: tuple              # sorted ",".join(node_ids) — incremental-friendly
    node_ids: frozenset
    internal_edge_ids: frozenset
    node_count: int
    edge_count: int
    supports_count: int
    refines_count: int
    density: float                           # Directed: edge_count / (n * (n-1)); 0 if n<=1
    longest_support_chain: int
    schema_version: str = "7.0"


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
    bridge_nodes: int                        # True articulation points (P0-3 fix)
    hub_nodes: int
    evolution_chains: int
    unresolved_conflicts: int
    construction_time_seconds: float
    enrichment_time_seconds: float


@dataclass(frozen=True)
class ValidationReport:
    is_valid: bool
    node_violations: tuple
    edge_violations: tuple
    graph_violations: tuple
    semantic_warnings: tuple   # Renamed from semantic_violations
    validation_time_seconds: float

    @property
    def total_violations(self) -> int:
        return (
            len(self.node_violations) + len(self.edge_violations)
            + len(self.graph_violations)
        )


@dataclass(frozen=True)
class KnowledgeGraph:
    """
    The immutable canonical semantic representation of the entire corpus.
    Phase 7's output and Phase 8's input.

    KnowledgeGraph is NOT a live graph database.
    It is a frozen artifact representing the state of knowledge at one point in time.
    """
    graph_id: str
    nodes: Dict[str, "ClaimNode"]
    edges: Dict[str, "RelationshipEdge"]
    partitions: Dict[str, "KnowledgePartition"]
    statistics: "GraphStatistics"
    validation_report: "ValidationReport"
    run_id: str
    config_hash: str
    schema_version: str = "7.0"

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
    def contradiction_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.CONTRADICTS]

    @property
    def supports_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.SUPPORTS]

    @property
    def refines_edges(self) -> List["RelationshipEdge"]:
        return [e for e in self.edges.values()
                if e.relationship_type == RelationshipType.REFINES]

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
    VERY_HIGH = "very_high"   # RI >= 80
    HIGH      = "high"        # RI >= 65
    MODERATE  = "moderate"    # RI >= 45
    LOW       = "low"         # RI >= 25
    VERY_LOW  = "very_low"    # RI < 25

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
    MEASURED    = "measured"     # Derived from full graph data
    ESTIMATED   = "estimated"    # Derived but with incomplete data
    UNAVAILABLE = "unavailable"  # Cannot be computed (e.g., no provenance)
    DEFAULT     = "default"      # Using policy default (no signal data)

    


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
    normalized_value: float           # Owned by extractor (P1-2 fix)
    status: SignalStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    normalization_strategy: str          # e.g. "log_scale", "linear", "step_function"
    status: SignalStatus
    quality_flags: tuple                  # e.g. ("low_sample_count", "echo_chamber_risk")
    dependency_list: tuple                # e.g. ("support_aggregate", "topology.centrality")
    diagnostics: Dict[str, Any] = field(default_factory=dict)


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
    direction: str               # "positive" | "negative"
    label: str                   # For explanation generation
    raw_value: float = 0.0       # Pre-normalization, for DecisionRecord


@dataclass(frozen=True)
class ContributionSet:
    """
    RECTIFIED (P0-2): The complete set of ContributionCandidates for one claim.

    This is what the Fusion Engine receives. It contains everything needed
    to compute the Reliability Index without the Fusion Engine knowing anything
    about individual signal semantics.
    """
    candidates: tuple               # Tuple[ContributionCandidate, ...]
    evidence_completeness: float    # Fraction of signals with actual measurements
    claim_id: str                   # For logging/tracing


@dataclass(frozen=True)
class ComponentScore:
    """One signal's contribution to the final Reliability Index."""
    signal_id: SignalID
    normalized_value: float    # From ContributionCandidate (0.0–1.0)
    policy_weight: float       # From policy (0.0–1.0)
    adjusted_value: float      # After policy interactions
    contribution: float        # = adjusted_value * policy_weight * 100 (or negative)
    direction: str             # "positive" or "negative"
    explanation: str           # Human-readable reason


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
    policy_interactions: tuple           # e.g. ("echo_chamber_discount_applied",)
    constraints_activated: tuple         # e.g. ("no_evidence_cap: 60.0",)
    contribution_order: tuple            # signal names by descending |contribution|
    raw_reliability: float
    constrained_reliability: float
    final_reliability: float
    uncertainty_components: tuple        # (component_name, contribution) tuples
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
    statuses: Dict[str, str] = field(default_factory=dict)


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
    graph_fingerprint: str             # NEW (P1-3): which profile was active
    graph_schema_version: str
    fusion_algorithm: str
    normalization_version: str
    computed_at_run_id: str
    signal_extractor_versions: Dict[str, str]
    registry_order: tuple            # NEW: ordered list of registered signal names


@dataclass(frozen=True)
class ReliabilityHistory:
    """
    RECTIFIED (P1-5): Architecture stub for confidence evolution tracking.

    Not active in production (requires cross-run storage).
    Architecture is wired up so Phase 9/10 can activate it.
    """
    claim_id: str
    history: tuple   # Tuple of (run_id, reliability_index, timestamp_iso) triples


@dataclass(frozen=True)
class ReliabilityMetadata:
    """
    The complete reliability profile for one ClaimNode.

    RECTIFIED: Now includes SignalManifest list and ReliabilityDecisionRecord.

    Fields:
        claim_id:               Links to KnowledgeGraph.nodes[claim_id]
        reliability_index:      Final score 0–100
        uncertainty_score:      Measurement uncertainty 0–100
        evidence_completeness:  Fraction of signals with actual measurements
        signal_vector:          All normalized signal measurements (for serialization)
        signal_manifests:       Per-signal derivation traces (NEW P0-4)
        component_scores:       Per-signal contributions (fully explainable)
        decision_record:        Full policy decision path (NEW P0-5)
        explanation:            Structured human-readable explanation
        calibration_label:      Human-friendly tier with semantic contract
        audit:                  Full reproducibility audit trail
        policy_version:         Which policy version produced this score
        schema_version:         "8.0"
    """
    claim_id: str
    reliability_index: float
    uncertainty_score: float
    evidence_completeness: float
    signal_vector: SignalVector
    signal_manifests: tuple            # Tuple[SignalManifest, ...] — NEW (P0-4)
    component_scores: tuple
    decision_record: ReliabilityDecisionRecord  # NEW (P0-5)
    explanation: ReliabilityExplanation
    calibration_label: CalibrationLabel
    audit: ReliabilityAudit
    policy_version: str
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
    reliability: Dict[str, ReliabilityMetadata]
    policy_snapshot: Dict[str, Any]
    policy_profile: str              # NEW (P1-3): which profile was used
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

    def get_reliability(self, claim_id: str) -> Optional[ReliabilityMetadata]:
        return self.reliability.get(claim_id)

    def top_reliable(self, n: int = 10) -> List[ReliabilityMetadata]:
        return sorted(
            self.reliability.values(),
            key=lambda m: m.reliability_index,
            reverse=True,
        )[:n]

    def least_reliable(self, n: int = 10) -> List[ReliabilityMetadata]:
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
    calibration_histogram: Dict[str, int]  # e.g., {"VERY_HIGH": 12, "LOW": 3}

@dataclass(frozen=True)
class Phase8Telemetry:
    """Complete telemetry payload for a Phase 8 execution."""
    policy_version: str
    policy_profile: str
    execution: ExecutionStats
    knowledge: KnowledgeStats


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

