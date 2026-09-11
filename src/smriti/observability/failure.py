"""
failure.py — Failure Taxonomy + Failure Escalation Ladder (§11.20 rectified).

RECTIFIED (P2-4): Original failure handling was:
    Failure → Recovery (binary)

Correct model is a formal escalation ladder:
    Detect → Classify → Isolate → Recover → Escalate → Terminate

Each stage has defined conditions, actions, and exit criteria.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class FailureCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    INTERACTION = "interaction"
    KNOWLEDGE_API = "knowledge_api"
    WORKSPACE = "workspace"
    PERSISTENCE = "persistence"
    EXTERNAL_DEPENDENCY = "external_dependency"
    INTERNAL_UNEXPECTED = "internal_unexpected"
    OBSERVABILITY = "observability"


class FailureSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IsolationStrategy(str, Enum):
    TERMINATE = "terminate"
    DEGRADE = "degrade"
    SKIP = "skip"
    IGNORE = "ignore"


class PropagationPolicy(str, Enum):
    PROPAGATE = "propagate"
    CONTAIN = "contain"
    LOG_ONLY = "log_only"


class RecoveryPolicy(str, Enum):
    REBUILD = "rebuild"
    RESTORE = "restore"
    RETRY = "retry"
    NONE = "none"


@dataclass(frozen=True)
class FailureTaxonomyEntry:
    category: FailureCategory
    severity: FailureSeverity
    isolation_strategy: IsolationStrategy
    propagation_policy: PropagationPolicy
    recovery_policy: RecoveryPolicy
    source_modules: tuple
    description: str


FAILURE_TAXONOMY: dict = {
    FailureCategory.CONFIGURATION: FailureTaxonomyEntry(
        category=FailureCategory.CONFIGURATION,
        severity=FailureSeverity.CRITICAL,
        isolation_strategy=IsolationStrategy.TERMINATE,
        propagation_policy=PropagationPolicy.PROPAGATE,
        recovery_policy=RecoveryPolicy.NONE,
        source_modules=("smriti.core.config",),
        description="Configuration is invalid or missing — system cannot start.",
    ),
    FailureCategory.INFRASTRUCTURE: FailureTaxonomyEntry(
        category=FailureCategory.INFRASTRUCTURE,
        severity=FailureSeverity.CRITICAL,
        isolation_strategy=IsolationStrategy.TERMINATE,
        propagation_policy=PropagationPolicy.PROPAGATE,
        recovery_policy=RecoveryPolicy.NONE,
        source_modules=("smriti.runtime", "smriti.infrastructure"),
        description="Core runtime infrastructure failed to initialize.",
    ),
    FailureCategory.KNOWLEDGE_API: FailureTaxonomyEntry(
        category=FailureCategory.KNOWLEDGE_API,
        severity=FailureSeverity.HIGH,
        isolation_strategy=IsolationStrategy.DEGRADE,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.RETRY,
        source_modules=("smriti.api",),
        description="Knowledge API failed to serve a request.",
    ),
    FailureCategory.WORKSPACE: FailureTaxonomyEntry(
        category=FailureCategory.WORKSPACE,
        severity=FailureSeverity.MEDIUM,
        isolation_strategy=IsolationStrategy.SKIP,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.RESTORE,
        source_modules=("smriti.dashboard.workspaces",),
        description="A dashboard workspace failed to render or activate.",
    ),
    FailureCategory.PERSISTENCE: FailureTaxonomyEntry(
        category=FailureCategory.PERSISTENCE,
        severity=FailureSeverity.HIGH,
        isolation_strategy=IsolationStrategy.DEGRADE,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.REBUILD,
        source_modules=("smriti.core",),
        description="Artifact read or write failed.",
    ),
    FailureCategory.RESOURCE: FailureTaxonomyEntry(
        category=FailureCategory.RESOURCE,
        severity=FailureSeverity.MEDIUM,
        isolation_strategy=IsolationStrategy.DEGRADE,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.REBUILD,
        source_modules=("smriti.infrastructure.resources",),
        description="A governed resource exceeded its policy limits.",
    ),
    FailureCategory.INTERACTION: FailureTaxonomyEntry(
        category=FailureCategory.INTERACTION,
        severity=FailureSeverity.MEDIUM,
        isolation_strategy=IsolationStrategy.SKIP,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.NONE,
        source_modules=("smriti.dashboard.controller",),
        description="User interaction failed.",
    ),
    FailureCategory.EXTERNAL_DEPENDENCY: FailureTaxonomyEntry(
        category=FailureCategory.EXTERNAL_DEPENDENCY,
        severity=FailureSeverity.HIGH,
        isolation_strategy=IsolationStrategy.DEGRADE,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.RETRY,
        source_modules=("smriti.embedding", "smriti.retrieval"),
        description="External model or library failed.",
    ),
    FailureCategory.OBSERVABILITY: FailureTaxonomyEntry(
        category=FailureCategory.OBSERVABILITY,
        severity=FailureSeverity.LOW,
        isolation_strategy=IsolationStrategy.IGNORE,
        propagation_policy=PropagationPolicy.LOG_ONLY,
        recovery_policy=RecoveryPolicy.NONE,
        source_modules=("smriti.observability",),
        description="Telemetry or metrics collection failed — execution continues.",
    ),
    FailureCategory.INTERNAL_UNEXPECTED: FailureTaxonomyEntry(
        category=FailureCategory.INTERNAL_UNEXPECTED,
        severity=FailureSeverity.HIGH,
        isolation_strategy=IsolationStrategy.DEGRADE,
        propagation_policy=PropagationPolicy.CONTAIN,
        recovery_policy=RecoveryPolicy.NONE,
        source_modules=("*",),
        description="Unclassified unexpected internal failure.",
    ),
}


# ── Failure Escalation Ladder (NEW P2-4) ──────────────────────────────────────


class EscalationStage(str, Enum):
    """
    RECTIFIED (P2-4): Formal failure escalation ladder.

    Replace binary Failure → Recovery with:
    Detect → Classify → Isolate → Recover → Escalate → Terminate
    """

    DETECT = "detect"  # Failure observed
    CLASSIFY = "classify"  # Category and severity assigned
    ISOLATE = "isolate"  # Blast radius contained
    RECOVER = "recover"  # Automatic recovery attempted
    ESCALATE = "escalate"  # Human intervention required
    TERMINATE = "terminate"  # System must stop


@dataclass
class EscalationRecord:
    """Tracks one failure through the escalation ladder."""

    failure_id: str
    category: FailureCategory
    current_stage: EscalationStage
    history: list[str] = field(default_factory=list)
    recovery_attempt: int = 0
    max_recovery_attempts: int = 3
    resolved: bool = False

    def advance(self, stage: EscalationStage, notes: str = "") -> None:
        self.history.append(f"{stage.value}: {notes}")
        self.current_stage = stage
        logger.info(
            "failure_escalation_advance",
            failure_id=self.failure_id,
            stage=stage.value,
            category=self.category.value,
        )


class FailureEscalationLadder:
    """
    RECTIFIED (P2-4): Manages failure escalation through defined stages.

    Usage:
        ladder = FailureEscalationLadder()
        record = ladder.detect(exc, source="api.query_service")
        record = ladder.classify(record)
        record = ladder.isolate(record)
        if not ladder.recover(record):
            ladder.escalate(record)
    """

    def __init__(self) -> None:
        self._taxonomy = FailureTaxonomy()
        import uuid

        self._id_gen = lambda: str(uuid.uuid4())[:8]

    def detect(self, exc: Exception, source: str) -> EscalationRecord:
        """Stage 1: Detect a failure."""
        failure_id = self._id_gen()
        failure_record = self._taxonomy.classify(exc, source)
        record = EscalationRecord(
            failure_id=failure_id,
            category=failure_record.category,
            current_stage=EscalationStage.DETECT,
        )
        record.advance(EscalationStage.DETECT, notes=f"source={source}")
        return record

    def classify(self, record: EscalationRecord) -> EscalationRecord:
        """Stage 2: Assign category and severity."""
        policy = FAILURE_TAXONOMY.get(record.category)
        severity = policy.severity.value if policy else "unknown"
        record.advance(EscalationStage.CLASSIFY, notes=f"severity={severity}")
        return record

    def isolate(self, record: EscalationRecord) -> EscalationRecord:
        """Stage 3: Apply isolation strategy."""
        policy = FAILURE_TAXONOMY.get(record.category)
        strategy = policy.isolation_strategy.value if policy else "ignore"
        record.advance(EscalationStage.ISOLATE, notes=f"strategy={strategy}")
        return record

    def recover(self, record: EscalationRecord) -> bool:
        """Stage 4: Attempt recovery. Returns True if successful."""
        if record.recovery_attempt >= record.max_recovery_attempts:
            record.advance(EscalationStage.ESCALATE, notes="max_attempts_exceeded")
            return False
        record.recovery_attempt += 1
        record.advance(EscalationStage.RECOVER, notes=f"attempt={record.recovery_attempt}")
        # Actual recovery logic delegated to RuntimeCoordinator
        return False  # Override in subclass or bind to coordinator.attempt_recovery()

    def escalate(self, record: EscalationRecord) -> None:
        """Stage 5: Require human intervention."""
        record.advance(EscalationStage.ESCALATE, notes="human_intervention_required")
        logger.error(
            "failure_requires_human_intervention",
            failure_id=record.failure_id,
            category=record.category.value,
        )

    def terminate(self, record: EscalationRecord) -> None:
        """Stage 6: System must stop."""
        record.advance(EscalationStage.TERMINATE, notes="system_terminated")
        logger.critical("failure_terminal", failure_id=record.failure_id)


@dataclass
class FailureRecord:
    """Observable record of a single failure event."""

    category: FailureCategory
    message: str
    source: str
    timestamp: float = field(default_factory=time.monotonic)
    traceback_str: str = ""
    resolved: bool = False

    @classmethod
    def from_exception(
        cls, exc: Exception, category: FailureCategory, source: str
    ) -> FailureRecord:
        return cls(
            category=category,
            message=str(exc),
            source=source,
            traceback_str=traceback.format_exc(),
        )


class FailureTaxonomy:
    """Classifies exceptions and produces FailureRecords."""

    def classify(self, exc: Exception, source: str) -> FailureRecord:

        category = self._infer_category(exc, source)
        record = FailureRecord.from_exception(exc, category, source)
        logger.warning("failure_classified", category=category.value, source=source)
        return record

    def policy_for(self, category: FailureCategory) -> FailureTaxonomyEntry:
        return FAILURE_TAXONOMY.get(category, FAILURE_TAXONOMY[FailureCategory.INTERNAL_UNEXPECTED])

    def _infer_category(self, exc: Exception, source: str) -> FailureCategory:
        from smriti import exceptions as smex

        if isinstance(exc, smex.ConfigError):
            return FailureCategory.CONFIGURATION
        if isinstance(exc, smex.RuntimeException | smex.InfrastructureException):
            return FailureCategory.INFRASTRUCTURE
        if isinstance(exc, smex.CacheError):
            return FailureCategory.RESOURCE
        if "api" in source or "knowledge" in source:
            return FailureCategory.KNOWLEDGE_API
        if "dashboard" in source or "workspace" in source:
            return FailureCategory.WORKSPACE
        if "infrastructure" in source or "runtime" in source:
            return FailureCategory.INFRASTRUCTURE
        return FailureCategory.INTERNAL_UNEXPECTED
