"""
observability/__init__.py — Public API for Phase 11 Part 3.

RECTIFIED: Exports FailureEscalationLadder, EscalationStage, RuntimeContract.
"""

from smriti.observability.failure    import (
    FailureCategory, FailureRecord, FailureTaxonomy,
    FailureEscalationLadder, EscalationStage, EscalationRecord,
)
from smriti.observability.degradation import DegradationLevel, ServiceDegradation, DegradationRegistry
from smriti.observability.health      import (
    HealthStatus, HealthCheck, HealthMonitor, RuntimeContract, RUNTIME_CONTRACTS,
    build_default_health_monitor,
)
from smriti.observability.metrics     import MetricsCollector, Counter, Gauge, Histogram
from smriti.observability.telemetry   import TelemetryEvent, TelemetryCollector, MetricPoint
from smriti.observability.quality     import QualityObjective, QualityModel
from smriti.observability.maturity    import MaturityLevel, MaturityAssessor

__all__ = [
    "FailureCategory", "FailureRecord", "FailureTaxonomy",
    "FailureEscalationLadder", "EscalationStage", "EscalationRecord",
    "DegradationLevel", "ServiceDegradation", "DegradationRegistry",
    "HealthStatus", "HealthCheck", "HealthMonitor",
    "RuntimeContract", "RUNTIME_CONTRACTS", "build_default_health_monitor",
    "MetricsCollector", "Counter", "Gauge", "Histogram",
    "TelemetryEvent", "TelemetryCollector", "MetricPoint",
    "QualityObjective", "QualityModel",
    "MaturityLevel", "MaturityAssessor",
]