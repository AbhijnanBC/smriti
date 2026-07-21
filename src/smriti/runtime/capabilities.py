"""
capabilities.py — Capability Model for Phase 11 (§11.4 rectified).

RECTIFIED (P0-4): The runtime knows states but not capabilities.
Graceful degradation should disable CAPABILITIES, not states.

Before rectification:
    RuntimeState.DEGRADED  (opaque — what degraded?)

After rectification:
    RuntimeState.DEGRADED +
    capabilities.EXPLAIN = False  (tells consumers exactly what is unavailable)

Capability definitions:
    QUERY         — basic claim lookup and search
    EXPORT        — export to JSON/CSV/GraphML
    EXPLAIN       — full multi-signal explanation
    SEARCH        — semantic + keyword hybrid search
    TRAVERSE      — graph traversal navigation
    STATISTICS    — aggregate statistics
    VISUALIZATION — interactive graph rendering (Phase 10)

Feature Status Model (RECTIFIED):
    INSTALLED   → code exists but not yet enabled
    ENABLED     → toggled ON in configuration
    AVAILABLE   → enabled AND dependencies are healthy
    DEGRADED    → available but running in a fallback mode
    UNAVAILABLE → enabled but dependencies are failing

Degradation contract:
    When a capability is disabled, a structured reason is recorded.
    Consumers check capabilities.is_usable("explain") before calling explain().
    Phase 10 shows appropriate UI messages based on capability state.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import structlog

from smriti.runtime.composition import DependencyGraph, DependencyHealth

logger = structlog.get_logger(__name__)


class Capability(str, Enum):
    """All runtime capabilities that can be individually enabled/disabled."""
    QUERY         = "query"
    EXPORT        = "export"
    EXPLAIN       = "explain"
    SEARCH        = "search"
    TRAVERSE      = "traverse"
    STATISTICS    = "statistics"
    VISUALIZATION = "visualization"


class FeatureStatus(str, Enum):
    """
    RECTIFIED: Status of a feature across its lifecycle.

    INSTALLED   → code exists in the distribution
    ENABLED     → toggled ON in configuration
    AVAILABLE   → enabled AND dependencies are healthy
    DEGRADED    → available but running in a fallback mode
    UNAVAILABLE → enabled but dependencies are failing
    """
    INSTALLED   = "installed"
    ENABLED     = "enabled"
    AVAILABLE   = "available"
    DEGRADED    = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class CapabilityState:
    """Current state of one capability, now with explicit FeatureStatus."""
    capability: Capability
    status: FeatureStatus = FeatureStatus.INSTALLED
    reason: str = ""
    updated_at: Optional[float] = None

    @property
    def is_usable(self) -> bool:
        """Determines if the system can safely route traffic to this feature."""
        return self.status in {FeatureStatus.AVAILABLE, FeatureStatus.DEGRADED}

    @property
    def is_enabled(self) -> bool:
        """True if the feature is toggled on (even if not yet available)."""
        return self.status in {FeatureStatus.ENABLED, FeatureStatus.AVAILABLE,
                               FeatureStatus.DEGRADED, FeatureStatus.UNAVAILABLE}


class CapabilityModel:
    """
    RECTIFIED (P0-4): Manages individual capability states with a status model.

    Features progress through:
        INSTALLED → ENABLED (by config) → AVAILABLE (by health check) → DEGRADED/UNAVAILABLE

    Phase 10 consults the capability model before rendering UI elements.

    Usage:
        model = CapabilityModel()
        model.enable(Capability.EXPLAIN)                     # toggles ON
        model.mark_available(Capability.EXPLAIN)             # deps healthy
        if model.is_usable(Capability.EXPLAIN):
            return api.explain(claim_id)
        else:
            return CapabilityUnavailableResponse(Capability.EXPLAIN)
    """

    def __init__(self) -> None:
        self._capabilities: Dict[Capability, CapabilityState] = {
            cap: CapabilityState(capability=cap, status=FeatureStatus.INSTALLED)
            for cap in Capability
        }
        self._lock = threading.Lock()

    # ── Basic status queries ──────────────────────────────────────────────────

    def is_usable(self, capability: Capability) -> bool:
        """Return True if the feature can be used right now (AVAILABLE or DEGRADED)."""
        with self._lock:
            return self._capabilities[capability].is_usable

    def is_enabled(self, capability: Capability) -> bool:
        """Return True if the feature is toggled ON (ENABLED or higher)."""
        with self._lock:
            return self._capabilities[capability].is_enabled

    def get_status(self, capability: Capability) -> FeatureStatus:
        with self._lock:
            return self._capabilities[capability].status

    # ── State transitions ─────────────────────────────────────────────────────

    def enable(self, capability: Capability) -> None:
        """Toggle the feature ON (set to ENABLED, not yet available)."""
        with self._lock:
            state = self._capabilities[capability]
            if state.status != FeatureStatus.ENABLED:
                state.status = FeatureStatus.ENABLED
                state.reason = ""
                state.updated_at = time.monotonic()
                self._publish_change(capability, FeatureStatus.ENABLED)

    def disable(self, capability: Capability, reason: str = "") -> None:
        """
        Make the feature unavailable (set to UNAVAILABLE) while keeping it enabled.
        This does not turn the feature off; it only indicates that dependencies
        are failing or the feature is temporarily out of service.
        """
        with self._lock:
            state = self._capabilities[capability]
            if state.status != FeatureStatus.UNAVAILABLE:
                state.status = FeatureStatus.UNAVAILABLE
                state.reason = reason
                state.updated_at = time.monotonic()
                self._publish_change(capability, FeatureStatus.UNAVAILABLE)

    def mark_available(self, capability: Capability) -> None:
        """Mark the feature as fully operational (healthy dependencies)."""
        with self._lock:
            state = self._capabilities[capability]
            if state.status != FeatureStatus.AVAILABLE:
                state.status = FeatureStatus.AVAILABLE
                state.reason = ""
                state.updated_at = time.monotonic()
                self._publish_change(capability, FeatureStatus.AVAILABLE)

    def degrade(self, capability: Capability, reason: str = "") -> None:
        """Mark the feature as degraded (still usable but in fallback mode)."""
        with self._lock:
            state = self._capabilities[capability]
            if state.status != FeatureStatus.DEGRADED:
                state.status = FeatureStatus.DEGRADED
                state.reason = reason
                state.updated_at = time.monotonic()
                self._publish_change(capability, FeatureStatus.DEGRADED)

    def mark_unavailable(self, capability: Capability, reason: str = "") -> None:
        """Mark the feature as unavailable (enabled but dependencies failing)."""
        with self._lock:
            state = self._capabilities[capability]
            if state.status != FeatureStatus.UNAVAILABLE:
                state.status = FeatureStatus.UNAVAILABLE
                state.reason = reason
                state.updated_at = time.monotonic()
                self._publish_change(capability, FeatureStatus.UNAVAILABLE)

    # ── Synchronisation with dependency graph (NEW) ──────────────────────────

    def sync_with_graph(self, graph: DependencyGraph) -> None:
        """
        Refresh capability states based on dependency health.

        Example mapping:
            If 'faiss_index' is UNAVAILABLE → mark SEARCH as DEGRADED.
            If 'embedding_model' is SLOW → mark SEARCH as DEGRADED.
            If all dependencies healthy → mark relevant capabilities AVAILABLE.
        """
        # Define capability-to-dependency mapping
        capability_deps = {
            Capability.SEARCH: {"faiss_index", "embedding_model"},
            Capability.QUERY: {"knowledge_graph", "read_store"},
            Capability.EXPLAIN: {"scoring_service"},
            Capability.EXPORT: {"export_encoder"},
            # Add more mappings as subsystems are integrated
        }

        with self._lock:
            for cap, dep_names in capability_deps.items():
                all_healthy = True
                any_unavailable = False
                any_slow = False
                dep_unavailable = None
                dep_slow = None

                for dep in dep_names:
                    health = graph.get_health(dep)
                    if health is None:
                        # Node not in graph → assume healthy
                        continue
                    if health == DependencyHealth.UNAVAILABLE:
                        any_unavailable = True
                        dep_unavailable = dep
                        break
                    if health == DependencyHealth.SLOW:
                        any_slow = True
                        dep_slow = dep
                    if health != DependencyHealth.HEALTHY:
                        all_healthy = False

                state = self._capabilities[cap]

                if any_unavailable:
                    # Dependency is down → mark UNAVAILABLE
                    if state.status != FeatureStatus.UNAVAILABLE:
                        state.status = FeatureStatus.UNAVAILABLE
                        state.reason = f"Dependency '{dep_unavailable}' unavailable"
                        state.updated_at = time.monotonic()
                        self._publish_change(cap, FeatureStatus.UNAVAILABLE)
                elif any_slow:
                    # Dependency is slow → degrade
                    if state.status not in (FeatureStatus.DEGRADED, FeatureStatus.UNAVAILABLE):
                        state.status = FeatureStatus.DEGRADED
                        state.reason = f"Dependency '{dep_slow}' slow"
                        state.updated_at = time.monotonic()
                        self._publish_change(cap, FeatureStatus.DEGRADED)
                elif all_healthy and state.is_enabled:
                    # Only mark AVAILABLE if the capability is enabled
                    if state.status != FeatureStatus.AVAILABLE:
                        state.status = FeatureStatus.AVAILABLE
                        state.reason = ""
                        state.updated_at = time.monotonic()
                        self._publish_change(cap, FeatureStatus.AVAILABLE)
                # else keep current status

    # ── Legacy compatibility methods (deprecated, but kept for smooth migration) ──

    def disable_legacy(self, capability: Capability, reason: str = "") -> None:
        """Legacy 'disable' – now maps to mark_unavailable()."""
        self.mark_unavailable(capability, reason)

    def enable_legacy(self, capability: Capability) -> None:
        """Legacy 'enable' – now maps to enable() + mark_available()? Better to keep explicit."""
        self.enable(capability)
        # Optionally automatically mark available? No, that would hide dependency health.
        # We keep them separate.

    # ── Helpers and reporting ─────────────────────────────────────────────────

    def _publish_change(self, capability: Capability, new_status: FeatureStatus) -> None:
        from smriti.runtime.events import publish, ArchitectureEventType
        publish(
            ArchitectureEventType.CAPABILITY_CHANGED,
            source="runtime.capabilities",
            capability=capability.value,
            status=new_status.value,
            reason=self._capabilities[capability].reason,
        )

    def snapshot(self) -> Dict[str, Dict]:
        """Return a read‑only snapshot of all capability states."""
        with self._lock:
            return {
                cap.value: {
                    "status":   state.status.value,
                    "reason":   state.reason,
                    "updated_at": state.updated_at,
                    "is_usable": state.is_usable,
                    "is_enabled": state.is_enabled,
                }
                for cap, state in self._capabilities.items()
            }

    def all_usable(self) -> bool:
        """Return True if all capabilities are either AVAILABLE or DEGRADED."""
        with self._lock:
            return all(state.is_usable for state in self._capabilities.values())

    def all_enabled(self) -> bool:
        """Return True if all capabilities are toggled ON (ENABLED or higher)."""
        with self._lock:
            return all(state.is_enabled for state in self._capabilities.values())

    def disabled_list(self) -> List[str]:
        """Return names of features that are currently not usable (status < AVAILABLE)."""
        with self._lock:
            return [cap.value for cap, state in self._capabilities.items()
                    if not state.is_usable]

    def status_summary(self) -> Dict[FeatureStatus, int]:
        """Count how many features are in each status."""
        counts = {s: 0 for s in FeatureStatus}
        with self._lock:
            for state in self._capabilities.values():
                counts[state.status] += 1
        return {k.value: v for k, v in counts.items()}