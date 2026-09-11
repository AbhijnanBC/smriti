"""
observability/__init__.py — Public API for Phase 11 Part 3.

RECTIFIED: Exports FailureEscalationLadder, EscalationStage, RuntimeContract.
"""

from smriti.observability.degradation import (
    DegradationLevel,
    DegradationRegistry,
    ServiceDegradation,
)
from smriti.observability.failure import (
    EscalationRecord,
    EscalationStage,
    FailureCategory,
    FailureEscalationLadder,
    FailureRecord,
    FailureTaxonomy,
)
from smriti.observability.health import (
    RUNTIME_CONTRACTS,
    HealthCheck,
    HealthMonitor,
    HealthStatus,
    RuntimeContract,
    build_default_health_monitor,
)
from smriti.observability.maturity import MaturityAssessor, MaturityLevel
from smriti.observability.metrics import Counter, Gauge, Histogram, MetricsCollector
from smriti.observability.quality import QualityModel, QualityObjective
from smriti.observability.telemetry import MetricPoint, TelemetryCollector, TelemetryEvent

__all__ = [
    "FailureCategory",
    "FailureRecord",
    "FailureTaxonomy",
    "FailureEscalationLadder",
    "EscalationStage",
    "EscalationRecord",
    "DegradationLevel",
    "ServiceDegradation",
    "DegradationRegistry",
    "HealthStatus",
    "HealthCheck",
    "HealthMonitor",
    "RuntimeContract",
    "RUNTIME_CONTRACTS",
    "build_default_health_monitor",
    "MetricsCollector",
    "Counter",
    "Gauge",
    "Histogram",
    "TelemetryEvent",
    "TelemetryCollector",
    "MetricPoint",
    "QualityObjective",
    "QualityModel",
    "MaturityLevel",
    "MaturityAssessor",
]
