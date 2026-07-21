"""
quality.py — Operational Quality Model (§11.27).

Observability measures; quality defines objectives.
Each KPI has a definition, target, measurement method, and
violation policy. These are engineering commitments, not aspirations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional


class ViolationPolicy(str, Enum):
    LOG_ONLY  = "log_only"    # Log violation; continue
    DEGRADE   = "degrade"     # Switch to degraded mode
    ALERT     = "alert"       # Emit an operational alert
    TERMINATE = "terminate"   # Halt (reserved for critical invariants)


@dataclass(frozen=True)
class QualityObjective:
    """
    A single operational quality KPI with measurable targets.
    """
    name:             str
    definition:       str
    target_value:     float
    unit:             str
    measurement:      str
    violation_policy: ViolationPolicy
    warning_threshold: float
    critical_threshold: float

    def evaluate(self, current_value: float) -> str:
        if current_value <= self.warning_threshold:
            return "ok"
        if current_value <= self.critical_threshold:
            return "warning"
        return "critical"


class QualityModel:
    """
    The complete SMRITI operational quality model.

    Pre-populated with canonical KPIs derived from the architecture.
    """

    OBJECTIVES: tuple[QualityObjective, ...] = (

        QualityObjective(
            name="startup_time",
            definition="Wall-clock time from process start to ACTIVE state",
            target_value=5.0,
            unit="seconds",
            measurement="RuntimeCoordinator.start() wall time",
            violation_policy=ViolationPolicy.LOG_ONLY,
            warning_threshold=5.0,
            critical_threshold=15.0,
        ),

        QualityObjective(
            name="query_p95_latency",
            definition="95th-percentile latency for knowledge queries",
            target_value=200.0,
            unit="milliseconds",
            measurement="MetricsCollector.histogram('query_latency_ms').p95",
            violation_policy=ViolationPolicy.DEGRADE,
            warning_threshold=200.0,
            critical_threshold=1000.0,
        ),

        QualityObjective(
            name="recovery_time",
            definition="Time from DEGRADED entry to ACTIVE restoration",
            target_value=10.0,
            unit="seconds",
            measurement="RuntimeCoordinator.attempt_recovery() wall time",
            violation_policy=ViolationPolicy.ALERT,
            warning_threshold=10.0,
            critical_threshold=60.0,
        ),

        QualityObjective(
            name="cache_hit_ratio",
            definition="Ratio of cache hits to total cache lookups",
            target_value=0.80,
            unit="ratio",
            measurement="cache_hits_total / (cache_hits_total + cache_misses_total)",
            violation_policy=ViolationPolicy.LOG_ONLY,
            warning_threshold=0.60,
            critical_threshold=0.30,
        ),

        QualityObjective(
            name="memory_ceiling",
            definition="Maximum resident set size during operation",
            target_value=512.0,
            unit="megabytes",
            measurement="psutil.Process().memory_info().rss / 1e6",
            violation_policy=ViolationPolicy.DEGRADE,
            warning_threshold=512.0,
            critical_threshold=1024.0,
        ),

        QualityObjective(
            name="operational_correctness",
            definition="Rate of responses with no validation errors",
            target_value=1.0,
            unit="ratio",
            measurement="1.0 - (errors_total / requests_total)",
            violation_policy=ViolationPolicy.ALERT,
            warning_threshold=0.99,
            critical_threshold=0.95,
        ),
    )

    @classmethod
    def get(cls, name: str) -> Optional[QualityObjective]:
        for obj in cls.OBJECTIVES:
            if obj.name == name:
                return obj
        return None