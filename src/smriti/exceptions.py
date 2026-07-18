"""
Custom exception hierarchy for SMRITI.
All exceptions inherit from SMRITIError for easy catch-all handling.
"""


class SMRITIError(Exception):
    """Base exception for all SMRITI errors."""
    pass


class ConfigError(SMRITIError):
    """Configuration is invalid or incomplete."""
    pass


class DiscoveryError(SMRITIError):
    """Error discovering input files."""
    pass


# ── Phase 2: Text Extraction ──────────────────────────────────────────────────

class ParsingError(SMRITIError):
    """Base exception for all Phase 2 extraction errors."""
    pass


class LoaderError(ParsingError):
    """Loader failed to dispatch to an extractor."""
    pass


class EncodingError(ParsingError):
    """File could not be decoded with any supported encoding."""
    pass


class MarkdownExtractionError(ParsingError):
    """Error reading a Markdown file."""
    pass


class PdfExtractionError(ParsingError):
    """Error extracting text from a PDF file."""
    pass


class TextExtractionError(ParsingError):
    """Error reading a plain-text file."""
    pass


class NormalizationError(ParsingError):
    """Error during text normalization."""
    pass


class StatisticsError(ParsingError):
    """Error computing text statistics."""
    pass


class BuilderError(ParsingError):
    """Error constructing a Document object."""
    pass


class DocumentError(ParsingError):
    """Invalid Document state detected."""
    pass


# ── Phase 3+ ─────────────────────────────────────────────────────────────────

class ExtractionError(SMRITIError):
    """Error extracting claims (Phase 3)."""
    pass


class EmbeddingError(SMRITIError):
    """Error computing embeddings."""
    pass


class RetrievalError(SMRITIError):
    """Error retrieving candidates."""
    pass


class ContradictionError(SMRITIError):
    """Error detecting contradictions."""
    pass


class EvolutionError(SMRITIError):
    """Error analyzing knowledge evolution."""
    pass


class ScoringError(SMRITIError):
    """Error computing metrics."""
    pass


class ReportingError(SMRITIError):
    """Error generating report."""
    pass


class DashboardError(SMRITIError):
    """Error in dashboard."""
    pass


class PipelineError(SMRITIError):
    """Error in pipeline orchestration."""
    pass


class CacheError(SMRITIError):
    """Error in cache operations."""
    pass


class HashError(SMRITIError):
    """Error computing hash."""
    pass


class ValidationError(SMRITIError):
    """Input or output validation failed."""
    pass

# ── Phase 3: Semantic Sentence Construction ───────────────────────────────────

class Phase3Error(SMRITIError):
    """Base for all Phase 3 errors."""
    pass


class ScannerError(Phase3Error):
    """Structural scanner failed on a document."""
    pass


class ContextError(Phase3Error):
    """Context stack invariant violated (fatal — indicates design error)."""
    pass


class NormalizationError(Phase3Error):
    """Structured content could not be normalised to prose."""
    pass


class SegmentationError(Phase3Error):
    """Sentence segmentation produced an impossible result."""
    pass


class SentenceValidationError(Phase3Error):
    """A SemanticSentence failed validation (fatal constraint violated)."""
    pass

# ── Phase 4: Claim Construction ───────────────────────────────────────────────

class Phase4Error(SMRITIError):
    """Base for all Phase 4 errors."""
    pass


class ClaimExtractionError(Phase4Error):
    """Unrecoverable error during claim extraction for a single sentence."""
    pass


class ClaimValidationError(Phase4Error):
    """Fatal constraint violation in claim validation (duplicate ID, broken provenance)."""
    pass


class SpacyNotLoadedError(Phase4Error):
    """spaCy model could not be loaded — pipeline cannot continue."""
    pass


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────

class Phase5Error(SMRITIError):
    """Base for all Phase 5 errors."""
    pass


class EmbeddingModelError(Phase5Error):
    """Embedding model failed to load or is misconfigured."""
    pass


class EmbeddingInferenceError(Phase5Error):
    """Embedding inference failed for a batch or single input."""
    pass


class VectorValidationError(Phase5Error):
    """Vector failed mathematical validation (NaN, Inf, dimension mismatch, dtype)."""
    pass


class CacheKeyError(Phase5Error):
    """Cache key could not be computed deterministically."""
    pass


class CacheSchemaMismatchError(Phase5Error):
    """Cache entry schema version does not match current Phase 5 schema."""
    pass