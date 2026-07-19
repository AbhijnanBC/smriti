"""
structural.py — Topology signal extractors.

RECTIFIED (P0-3): hub_bonus and bridge_bonus have been removed from TopologyPolicy.
Instead, HubScore and BridgeScore are now SEPARATE registered signals with their
own policy weights in FusionPolicy.signal_weights.

This means:
    - TopologyPolicy never knows what "hub" or "bridge" means internally
    - Fusion simply weights hub_score and bridge_score as independent signals
    - Adding a new topology sub-signal only requires a new extractor + registration
    - Policies adjust weights, not bonuses

Three extractors in this file:
    1. TopologyStrengthExtractor  — centrality-based topology signal
    2. HubScoreExtractor          — binary hub signal (is_hub → 1.0, else 0.0)
    3. BridgeScoreExtractor       — binary bridge signal (is_bridge → 1.0, else 0.0)
"""

from __future__ import annotations

from typing import List
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats,
    SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy
from smriti.scoring.signals.base import BaseSignalExtractor


class TopologyStrengthExtractor(BaseSignalExtractor):
    """Measures centrality-based structural importance."""

    @property
    def signal_id(self) -> SignalID:
        return SignalID.TOPOLOGY_STRENGTH

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "linear_centrality_scale"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.centrality", "topology.degree"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        topo = node.topology
        # RECTIFIED: only centrality × scale — no hub/bridge bonus here
        raw_value = topo.centrality * policy.topology.centrality_scale
        normalized = self.normalize(raw_value, global_stats)

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=normalized,
            status=SignalStatus.MEASURED,
            metadata={
                "centrality": topo.centrality,
                "degree": topo.degree,
                "centrality_scale": policy.topology.centrality_scale,
            },
        )


class HubScoreExtractor(BaseSignalExtractor):
    """
    RECTIFIED (P0-3): Emits HubScore as a separate signal.

    hub_bonus was a policy detail bleeding into topology measurement.
    Instead: hub_score = 1.0 if is_hub else 0.0.
    The FusionPolicy.signal_weights["hub_score"] controls importance.
    Policy never needs to know what "hub" means structurally.
    """

    @property
    def signal_id(self) -> SignalID:
        return SignalID.HUB_SCORE

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "binary"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.is_hub"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        raw_value = 1.0 if node.topology.is_hub else 0.0

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=raw_value,
            status=SignalStatus.MEASURED,
            metadata={"is_hub": node.topology.is_hub},
        )


class BridgeScoreExtractor(BaseSignalExtractor):
    """
    RECTIFIED (P0-3): Emits BridgeScore as a separate signal.

    bridge_bonus was a policy detail bleeding into topology measurement.
    Instead: bridge_score = 1.0 if is_bridge else 0.0.
    The FusionPolicy.signal_weights["bridge_score"] controls importance.
    """

    @property
    def signal_id(self) -> SignalID:
        return SignalID.BRIDGE_SCORE

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def normalization_strategy(self) -> str:
        return "binary"

    @property
    def dependency_list(self) -> List[str]:
        return ["topology.is_bridge"]

    def normalize(self, raw: float, global_stats: ScoringGlobalStats) -> float:
        return max(0.0, min(1.0, raw))

    def extract(
        self, node: ClaimNode, graph: KnowledgeGraph,
        global_stats: ScoringGlobalStats, policy: ReliabilityPolicy,
    ) -> RawSignal:
        if node.topology is None:
            return RawSignal(
                name=self.signal_id.value,
                raw_value=0.0,
                normalized_value=0.0,
                status=SignalStatus.UNAVAILABLE,
                metadata={"reason": "no_topology_metrics"},
            )

        raw_value = 1.0 if node.topology.is_bridge else 0.0

        return RawSignal(
            name=self.signal_id.value,
            raw_value=raw_value,
            normalized_value=raw_value,
            status=SignalStatus.MEASURED,
            metadata={"is_bridge": node.topology.is_bridge},
        )