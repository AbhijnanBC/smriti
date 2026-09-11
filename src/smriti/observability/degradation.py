"""
degradation.py — Graceful Degradation Model (§11.22).

Defines explicit degradation states for every service.
SMRITI prefers partial functionality over total failure.

For every service, defines:
    Normal    → all capabilities available
    Degraded  → reduced capability, core function preserved
    Unavailable → service offline, dependent features disabled
    Recovered → back to Normal after repair
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class DegradationLevel(str, Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RECOVERED = "recovered"


@dataclass
class ServiceDegradation:
    """
    Degradation contract for a single service.

    Specifies what the system does at each degradation level
    instead of treating failures as binary.
    """

    service_name: str
    current_level: DegradationLevel = DegradationLevel.NORMAL
    normal_behavior: str = ""
    degraded_behavior: str = ""
    unavailable_behavior: str = ""
    recovery_behavior: str = ""
    _history: list[DegradationLevel] = field(default_factory=list, repr=False)

    def degrade(self, reason: str = "") -> None:
        self._history.append(self.current_level)
        self.current_level = DegradationLevel.DEGRADED
        logger.warning("service_degraded", service=self.service_name, reason=reason)

    def mark_unavailable(self, reason: str = "") -> None:
        self._history.append(self.current_level)
        self.current_level = DegradationLevel.UNAVAILABLE
        logger.error("service_unavailable", service=self.service_name, reason=reason)

    def recover(self) -> None:
        self._history.append(self.current_level)
        self.current_level = DegradationLevel.RECOVERED
        logger.info("service_recovered", service=self.service_name)

    def restore_normal(self) -> None:
        self.current_level = DegradationLevel.NORMAL

    @property
    def is_operational(self) -> bool:
        return self.current_level in {DegradationLevel.NORMAL, DegradationLevel.DEGRADED}

    def describe_current_behavior(self) -> str:
        mapping = {
            DegradationLevel.NORMAL: self.normal_behavior,
            DegradationLevel.DEGRADED: self.degraded_behavior,
            DegradationLevel.UNAVAILABLE: self.unavailable_behavior,
            DegradationLevel.RECOVERED: self.recovery_behavior,
        }
        return mapping.get(self.current_level, "")


class DegradationRegistry:
    """
    Registry of all service degradation contracts.

    Pre-populated with the canonical SMRITI service degradation model.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceDegradation] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = [
            ServiceDegradation(
                service_name="explainability",
                normal_behavior="Return claims with full multi-signal explanations.",
                degraded_behavior="Return claims without explanation (explanation fields empty).",
                unavailable_behavior="Disable explainability button; display informative message.",
                recovery_behavior="Re-enable explanation when signal computation is available.",
            ),
            ServiceDegradation(
                service_name="export",
                normal_behavior="Export claims in JSON and CSV formats.",
                degraded_behavior="Export in JSON only if CSV encoder fails.",
                unavailable_behavior="Disable export panel; display retry button.",
                recovery_behavior="Re-enable full export on next successful encoder check.",
            ),
            ServiceDegradation(
                service_name="graph_visualization",
                normal_behavior="Render full interactive knowledge graph.",
                degraded_behavior="Render static list view of claims instead.",
                unavailable_behavior="Show empty state with reload option.",
                recovery_behavior="Switch back to interactive graph view.",
            ),
            ServiceDegradation(
                service_name="telemetry",
                normal_behavior="Collect and buffer all telemetry events.",
                degraded_behavior="Collect events in memory only (no persistence).",
                unavailable_behavior="Skip telemetry; continue pipeline execution.",
                recovery_behavior="Resume telemetry collection on next event.",
            ),
            ServiceDegradation(
                service_name="search",
                normal_behavior="Semantic + keyword hybrid search.",
                degraded_behavior="Keyword-only search if FAISS index unavailable.",
                unavailable_behavior="Search disabled; show placeholder.",
                recovery_behavior="Rebuild FAISS index and restore semantic search.",
            ),
        ]
        for svc in defaults:
            self._services[svc.service_name] = svc

    def register(self, service: ServiceDegradation) -> None:
        self._services[service.service_name] = service

    def get(self, name: str) -> ServiceDegradation | None:
        return self._services.get(name)

    def all_operational(self) -> bool:
        return all(s.is_operational for s in self._services.values())

    def degraded_services(self) -> list[str]:
        return [
            name
            for name, svc in self._services.items()
            if svc.current_level != DegradationLevel.NORMAL
        ]

    def status_snapshot(self) -> dict[str, str]:
        return {name: svc.current_level.value for name, svc in self._services.items()}
