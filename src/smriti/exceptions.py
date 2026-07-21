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

# ── Phase 6: Semantic Relationship Discovery ───────────────────────────────────
from enum import Enum
class Phase6ErrorCategory(str, Enum):
    """
    Failure taxonomy for Phase 6.

    RECOVERABLE:     The pipeline can continue; this pair is skipped.
    NON_RECOVERABLE: The pipeline must abort.
    RETRYABLE:       The operation failed transiently; retry may succeed.
    CONFIGURATION:   The config is invalid; cannot proceed without fix.
    DATA:            Input data is malformed; this batch/pair is skipped.
    INFRASTRUCTURE:  External service (GPU, disk, network) failed.
    """
    RECOVERABLE     = "recoverable"
    NON_RECOVERABLE = "non_recoverable"
    RETRYABLE       = "retryable"
    CONFIGURATION   = "configuration"
    DATA            = "data"
    INFRASTRUCTURE  = "infrastructure"


class Phase6Error(SMRITIError):
    """Base for all Phase 6 errors."""
    category: Phase6ErrorCategory = Phase6ErrorCategory.NON_RECOVERABLE

    def __init__(self, message: str, category: Phase6ErrorCategory = None):
        super().__init__(message)
        if category is not None:
            self.category = category


class IndexBuildError(Phase6Error):
    """Failed to build the vector index. Non-recoverable."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class FAISSNotAvailableError(Phase6Error):
    """faiss-cpu is not installed. Configuration error."""
    category = Phase6ErrorCategory.CONFIGURATION


class NLIModelError(Phase6Error):
    """NLI cross-encoder failed to load or run inference."""
    category = Phase6ErrorCategory.INFRASTRUCTURE


class NLIInferenceBatchError(Phase6Error):
    """One NLI batch failed — pairs in batch are skipped. Recoverable."""
    category = Phase6ErrorCategory.RECOVERABLE


class RelationshipValidationError(Phase6Error):
    """A Relationship failed structural validation (fatal invariant violated)."""
    category = Phase6ErrorCategory.DATA


class CandidateGenerationError(Phase6Error):
    """ANN candidate generation failed."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class CalibrationError(Phase6Error):
    """ConfidenceCalibrator encountered an unexpected score distribution."""
    category = Phase6ErrorCategory.RECOVERABLE


class ResolverPolicyError(Phase6Error):
    """ResolverPolicy configuration is invalid or internally inconsistent."""
    category = Phase6ErrorCategory.CONFIGURATION


class ConflictResolutionError(Phase6Error):
    """ConflictResolver could not determine which relationship wins."""
    category = Phase6ErrorCategory.RECOVERABLE


class ResourceLimitExceeded(Phase6Error):
    """A resource limit (max_pairs, memory, timeout) was exceeded."""
    category = Phase6ErrorCategory.NON_RECOVERABLE


class ReplayError(Phase6Error):
    """Replay failed — run_id not found or replay manifest corrupted."""
    category = Phase6ErrorCategory.CONFIGURATION

# ── Phase 7: Knowledge Graph Construction ────────────────────────────────────

class Phase7Error(SMRITIError):
    """Base for all Phase 7 errors."""
    pass


class GraphConstructionError(Phase7Error):
    """Fatal error during graph construction. No partial graph is emitted."""
    pass


class GraphValidationError(Phase7Error):
    """Structural invariant violated during validation. Fatal."""
    pass


class SemanticValidationError(Phase7Error):
    """Semantic invariant violated (e.g. impossible relationship chain). Fatal."""
    pass


class PartitioningError(Phase7Error):
    """Constraint-based partitioning failed."""
    pass


class BackendError(Phase7Error):
    """Graph backend (NetworkX) encountered an unexpected error."""
    pass


class SerializationError(Phase7Error):
    """KnowledgeGraph could not be serialized to JSON."""
    pass


class AnnotationPolicyError(Phase7Error):
    """AnnotationPolicy configuration is invalid or internally inconsistent."""
    pass    

# ── Phase 8: Reliability Evaluation ─────────────────────────────────────────

class Phase8Error(SMRITIError):
    """Base for all Phase 8 errors."""
    pass


class SignalExtractionError(Phase8Error):
    """A signal extractor failed to produce a valid measurement."""
    pass


class NormalizationError(Phase8Error):
    """Signal normalization produced an invalid value (after validation)."""
    pass


class FusionError(Phase8Error):
    """Reliability fusion encountered an impossible configuration."""
    pass


class PolicyError(Phase8Error):
    """Policy configuration is invalid or internally inconsistent."""
    pass


class RegistryError(Phase8Error):
    """SignalRegistry encountered a duplicate registration or ordering conflict."""
    pass


class ScoringValidationError(Phase8Error):
    """A ReliabilityMetadata failed structural validation."""
    pass

# ── Phase 9: Knowledge Access Layer ──────────────────────────────────────────

class Phase9Error(SMRITIError):
    """Base for all Phase 9 errors."""
    pass


class RequestValidationError(Phase9Error):
    """Incoming request failed validation."""
    code: str = "VALIDATION_ERROR"


class ClaimNotFoundError(Phase9Error):
    """Requested claim_id does not exist in the current snapshot."""
    code: str = "NOT_FOUND"


class QueryPlanError(Phase9Error):
    """Planner could not produce a valid plan."""
    code: str = "QUERY_ERROR"


class ReadStoreError(Phase9Error):
    """ReadStore encountered an unexpected error."""
    code: str = "EXECUTION_ERROR"


class ExportError(Phase9Error):
    """Export service failed to serialize knowledge."""
    code: str = "EXPORT_ERROR"


class CacheError(Phase9Error):
    """Knowledge view cache encountered an error."""
    code: str = "CACHE_ERROR"


class TraversalDepthExceededError(Phase9Error):
    """Traversal exceeded the configured maximum depth."""
    code: str = "TRAVERSAL_DEPTH_EXCEEDED"


class IndexError(Phase9Error):
    """Index registry or builder encountered an error."""
    code: str = "INDEX_ERROR"


class NormalizationError(Phase9Error):
    """QueryNormalizer could not canonicalize the request."""
    code: str = "NORMALIZATION_ERROR"

# ── Phase 10: Human Knowledge Interaction Layer ───────────────────────────────

class Phase10Error(SMRITIError):
    """Base for all Phase 10 errors."""
    pass


class WorkspaceNotFoundError(Phase10Error):
    """Requested workspace type is not registered."""
    pass


class InteractionPolicyViolationError(Phase10Error):
    """User action violates an interaction policy."""
    pass


class PresentationError(Phase10Error):
    """A presentation component failed to render."""
    pass


class WorkspaceSerializationError(Phase10Error):
    """Workspace state could not be serialized or restored."""
    pass


class ServiceClientError(Phase10Error):
    """ServiceClient failed to retrieve data from Phase 9."""
    pass


class CommandDispatchError(Phase10Error):
    """A command could not be dispatched (policy rejection or state conflict)."""
    pass


class ViewRegistryError(Phase10Error):
    """A requested view type is not registered."""
    pass


class ExportPipelineError(Phase10Error):
    """An export exporter failed."""
    pass    


# ── Phase 11: Architectural Error Hierarchy ──────────────────────────────────

class ArchitectureException(SMRITIError):
    """Root of all architectural and operational errors."""
    pass

class RuntimeException(ArchitectureException):
    """State machine violations and lifecycle errors."""
    pass

class InfrastructureException(ArchitectureException):
    """Resource budgets, dependency cycles, and telemetry failures."""
    pass

class ComplianceException(ArchitectureException):
    """Architectural compliance rule violations."""
    pass

class PolicyException(ArchitectureException):
    """Interaction or operational policy violations."""
    pass

class GovernanceException(ArchitectureException):
    """ADR conflicts, version incompatibility, or interface stability violations."""
    pass

class Phase11InvariantViolation(ArchitectureException):
    """Raised when a system invariant is violated during Phase 11 runtime."""
    pass
class CapabilityException(ArchitectureException):
    """Invocation of an unavailable or degraded capability."""
    pass

class SchedulerException(ArchitectureException):
    """Background task or periodic scheduler failures."""
    pass

# ── Backward Compatibility Aliases ──────────────────────────────────────────
# These allow old code to continue working

Phase11RuntimeError = RuntimeException
Phase11LifecycleError = RuntimeException
Phase11CapabilityError = CapabilityException
ResourceBudgetExceeded = InfrastructureException
ArchitectureEventError = InfrastructureException
SchedulerError = SchedulerException
Phase11ComplianceError = ComplianceException
Phase11GovernanceError = GovernanceException
Phase11InvariantViolation = Phase11InvariantViolation


# ── Phase 12: Scientific Validation Framework ──────────────────────────────────

class Phase12Error(SMRITIError):
    """Base for all Phase 12 errors."""
    pass

class VerificationRuleError(Phase12Error):
    """A verification rule failed in a way that prevents further execution."""
    pass

class GroundTruthError(Phase12Error):
    """Ground truth repository is missing, corrupt, or incompatible."""
    pass

class ExperimentError(Phase12Error):
    """An experiment failed to execute."""
    pass

class CertificationError(Phase12Error):
    """Certification level could not be determined."""
    pass

class ReproducibilityError(Phase12Error):
    """Reproducibility assessment could not be completed."""
    pass

class GateViolationError(Phase12Error):
    """A certification gate was violated — used for strict mode only."""
    pass

class EvidenceConflictError(Phase12Error):
    """An evidence conflict could not be resolved."""
    pass

class AssumptionViolationError(Phase12Error):
    """A registered assumption was detected as violated."""
    pass