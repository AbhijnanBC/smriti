"""
signals/__init__.py — SignalRegistry for Phase 8.

RECTIFIED (P0-1): Replaces the static SIGNAL_EXTRACTORS list with a
dynamic SignalRegistry that supports:
    - register(extractor): Register a new extractor (any module can call this)
    - discover(): Return all registered extractors in priority order
    - ordered_extractors(): Return extractors sorted by priority
    - deregister(signal_name): Remove an extractor (for testing)

Open/Closed compliance:
    Adding a new signal extractor ONLY requires:
        1. Creating the extractor class
        2. Calling SignalRegistry.register() (typically in the extractor's module)
    The __init__.py pipeline, Fusion engine, and all other modules NEVER change.

Priority ordering:
    Lower priority number = extracted first.
    Extractors with the same priority are ordered alphabetically by signal_id.
    Default priority = 100. Negative priorities are reserved for system signals.

RECTIFIED (Phase 8.2): Uses signal_id (SignalID enum) instead of string signal_name.
Enforces API version compatibility at registration time.
"""

from __future__ import annotations

import structlog

from smriti.exceptions import RegistryError
from smriti.scoring.signals.base import SIGNAL_API_VERSION, BaseSignalExtractor
from smriti.scoring.signals.conflict import ConflictPressureExtractor
from smriti.scoring.signals.evidence import EvidenceStrengthExtractor
from smriti.scoring.signals.independence import EvidenceIndependenceExtractor
from smriti.scoring.signals.provenance import SourceDiversityExtractor
from smriti.scoring.signals.structural import (
    BridgeScoreExtractor,
    HubScoreExtractor,
    TopologyStrengthExtractor,
)
from smriti.scoring.signals.temporal import TemporalStabilityExtractor

logger = structlog.get_logger(__name__)


class SignalRegistry:
    """
    Central registry for all signal extractors.

    Usage:
        # In an extractor module (e.g., novelty.py):
        from smriti.scoring.signals import signal_registry
        signal_registry.register(NoveltySignalExtractor(), priority=90)

        # In the pipeline:
        extractors = signal_registry.ordered_extractors()
        # That's it. Pipeline never changes.
    """

    def __init__(self) -> None:
        self._extractors: dict[str, BaseSignalExtractor] = {}
        self._priorities: dict[str, int] = {}

    def register(
        self,
        extractor: BaseSignalExtractor,
        priority: int = 100,
    ) -> None:
        """
        Register a signal extractor.

        Args:
            extractor: The extractor instance.
            priority:  Execution priority (lower = runs first). Default = 100.

        Raises:
            RegistryError: If a different extractor is already registered
                           with the same signal_id, or if the extractor's
                           API version does not match SIGNAL_API_VERSION.
        """
        # ── API version check ─────────────────────────────────────────────────────
        if extractor.api_version != SIGNAL_API_VERSION:
            raise RegistryError(
                f"Extractor {extractor.__class__.__name__} uses API version "
                f"{extractor.api_version}, but registry expects {SIGNAL_API_VERSION}. "
                f"Update the extractor to comply with the current API."
            )

        signal_id = extractor.signal_id
        key = signal_id.value

        if key in self._extractors:
            existing = self._extractors[key]
            if type(existing) is not type(extractor):
                raise RegistryError(
                    f"Signal '{key}' is already registered with a different extractor type "
                    f"({type(existing).__name__}). Deregister first if you intend to replace it."
                )
            logger.debug("signal already registered, skipping", signal=key)
            return

        self._extractors[key] = extractor
        self._priorities[key] = priority
        logger.debug(
            "signal registered",
            signal=key,
            priority=priority,
            version=extractor.version,
            api_version=extractor.api_version,
        )

    def deregister(self, signal_id_value: str) -> None:
        """Remove an extractor by its SignalID value. Primarily for testing."""
        self._extractors.pop(signal_id_value, None)
        self._priorities.pop(signal_id_value, None)

    def discover(self) -> dict[str, BaseSignalExtractor]:
        """Return all registered extractors keyed by SignalID value."""
        return dict(self._extractors)

    def ordered_extractors(self) -> list[BaseSignalExtractor]:
        """Return extractors sorted by (priority, signal_id.value) for determinism."""
        return sorted(
            self._extractors.values(),
            key=lambda e: (self._priorities.get(e.signal_id.value, 100), e.signal_id.value),
        )

    def get(self, signal_id_value: str) -> BaseSignalExtractor | None:
        """Get a specific extractor by its SignalID value."""
        return self._extractors.get(signal_id_value)

    @property
    def registered_names(self) -> list[str]:
        """Sorted list of all registered SignalID values."""
        return sorted(self._extractors.keys())

    def __len__(self) -> int:
        return len(self._extractors)


# ── Singleton registry instance ───────────────────────────────────────────────
signal_registry = SignalRegistry()

# ── Register all built-in extractors ─────────────────────────────────────────
# Priority values control execution order.

# Register with explicit priorities (lower = runs first)
signal_registry.register(EvidenceStrengthExtractor(), priority=10)
signal_registry.register(EvidenceIndependenceExtractor(), priority=20)
signal_registry.register(SourceDiversityExtractor(), priority=30)
signal_registry.register(TopologyStrengthExtractor(), priority=40)
signal_registry.register(HubScoreExtractor(), priority=41)  # RECTIFIED (P0-3)
signal_registry.register(BridgeScoreExtractor(), priority=42)  # RECTIFIED (P0-3)
signal_registry.register(ConflictPressureExtractor(), priority=50)
signal_registry.register(TemporalStabilityExtractor(), priority=60)

# Backward-compatible alias for external callers that used SIGNAL_EXTRACTORS
# (Maintained for compatibility but should be considered deprecated)
SIGNAL_EXTRACTORS = signal_registry.ordered_extractors()

__all__ = [
    "BaseSignalExtractor",
    "SignalRegistry",
    "signal_registry",
    "SIGNAL_EXTRACTORS",
    "EvidenceStrengthExtractor",
    "EvidenceIndependenceExtractor",
    "SourceDiversityExtractor",
    "TopologyStrengthExtractor",
    "HubScoreExtractor",
    "BridgeScoreExtractor",
    "ConflictPressureExtractor",
    "TemporalStabilityExtractor",
]
