"""
signals/base.py — Abstract base for all signal extractors.

RECTIFIED (P1-2): Each extractor now owns its normalize() method.
The normalization engine calls extractor.normalize(raw_value) rather than
centralizing normalization logic.

RECTIFIED (P0-4): extract() now returns RawSignal with both raw_value and
normalized_value, plus a build_manifest() method for SignalManifest construction.

RECTIFIED (Phase 8.2): signal_name replaced by signal_id (a SignalID enum)
for type-safe signal identification across the registry and fusion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalManifest, SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy

SIGNAL_API_VERSION = 1


class BaseSignalExtractor(ABC):
    """Abstract base for all signal extractors."""

    @property
    @abstractmethod
    def signal_id(self) -> SignalID:
        """
        Unique signal identifier (replaces signal_name).

        Uses the SignalID enum for type safety and canonical registry.
        """
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Extractor version for audit trail."""
        ...

    @property
    def normalization_strategy(self) -> str:
        """
        Human-readable description of the normalization strategy.
        RECTIFIED (P1-2): Each extractor declares its strategy.
        """
        return "identity"

    @property
    def dependency_list(self) -> List[str]:
        """
        Which graph fields this extractor depends on.
        RECTIFIED (P0-4): For SignalManifest.dependency_list.
        """
        return []

    @property
    def api_version(self) -> int:
        """The interface version this extractor was built against."""
        return SIGNAL_API_VERSION

    @abstractmethod
    def extract(
        self,
        node: ClaimNode,
        graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats,
        policy: ReliabilityPolicy,
    ) -> RawSignal:
        """
        Extract and normalize the raw signal value for one ClaimNode.

        RECTIFIED (P1-2): Extractor owns normalization.
        Returns RawSignal with BOTH raw_value and normalized_value populated.
        normalized_value is always in [0, 1].

        NEVER raises — errors are captured in status and metadata.
        """
        ...

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        """
        RECTIFIED (P1-2): Extractor-owned normalization strategy.
        Default: identity (raw already in [0,1]).
        Override in subclass for log-scale, step-function, etc.
        """
        return max(0.0, min(1.0, raw))

    def build_manifest(
        self,
        signal: RawSignal,
        quality_flags: Optional[List[str]] = None,
    ) -> SignalManifest:
        """
        RECTIFIED (P0-4): Build a SignalManifest for this signal/claim.
        Called by the normalization engine after extract().
        """
        return SignalManifest(
            signal_id=self.signal_id.value,           # RECTIFIED: use signal_id (not signal_name)
            extractor_version=self.version,
            raw_value=signal.raw_value,
            normalized_value=signal.normalized_value,
            normalization_strategy=self.normalization_strategy,
            status=signal.status,
            quality_flags=tuple(quality_flags or []),
            dependency_list=tuple(self.dependency_list),
            diagnostics=dict(signal.metadata),
        )