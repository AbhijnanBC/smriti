"""
policies.py — Phase 8 policy definitions.

RECTIFIED (P0-3): TopologyPolicy no longer contains hub_bonus or bridge_bonus.
Those are topology implementation details. The topology extractor emits HubScore
and BridgeScore as separate registered signals. Policy only has centrality_scale.

RECTIFIED (P1-3): PolicyProfile enum added with preset profiles:
    CONSERVATIVE: High evidence bar, strong conflict penalty
    BALANCED:     Default — balanced across all signals
    RESEARCH:     Emphasizes independence and source diversity
    EVIDENCE_FIRST: Maximum weight on evidence strength

RECTIFIED (Phase 8.3): FusionPolicy.validate() now requires the active registry
set to enforce a strict 1:1 mapping between policy weights and registered signals.
This prevents silent mismatches when signals are added or removed.

Rules:
    ✅ Algorithms remain fixed; only policies change
    ✅ Changing a policy never requires changing implementation
    ✅ TopologyPolicy never knows how topology works internally
    ❌ No hard-coded weights except default policy values here
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

import structlog

from smriti.core.config import get_config
from smriti.core.models import SignalID
from smriti.exceptions import PolicyError

logger = structlog.get_logger(__name__)

POLICY_VERSION = "1.0"

# RECTIFIED (P1-4, external "reality check" review — reliability vs. graph
# importance conflation): reliability_index was previously fused from all
# 8 registered signals, silently blending "how well is this claim evidenced"
# (evidence_strength, evidence_independence, source_diversity,
# conflict_pressure, temporal_stability) with "how structurally central is
# this claim in the graph" (topology_strength, hub_score, bridge_score) into
# one number. Those are different scientific claims -- a claim can be
# well-evidenced but structurally peripheral, or highly central but resting
# on a single unverified source. This categorization is the basis for
# splitting one fused ContributionSet into two (see
# scoring.normalization.split_contribution_set_by_category), each fed
# through the SAME generic fusion engine to produce reliability_index and
# importance_index as independent, separately-explainable scores.
EVIDENCE_SIGNAL_NAMES = frozenset(
    {
        "evidence_strength",
        "evidence_independence",
        "source_diversity",
        "conflict_pressure",
        "temporal_stability",
    }
)
IMPORTANCE_SIGNAL_NAMES = frozenset(
    {
        "topology_strength",
        "hub_score",
        "bridge_score",
    }
)


class PolicyProfile(str, Enum):
    """
    RECTIFIED (P1-3): Named policy profiles for benchmarking and domain use.

    Each profile configures all weights and thresholds for a specific use case.
    Loading a profile overrides any manual configuration.

    Profiles:
        BALANCED:       Default. Balanced across evidence, topology, conflict.
        CONSERVATIVE:   High evidence requirement, strong conflict penalty.
                        Use when false positives are costly.
        RESEARCH:       Emphasizes independence and source diversity.
                        Use for academic knowledge bases.
        EVIDENCE_FIRST: Maximum weight on direct evidence strength.
                        Use when graph topology is sparse/unreliable.
    """

    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    RESEARCH = "research"
    EVIDENCE_FIRST = "evidence_first"


@dataclass(frozen=True)
class EvidencePolicy:
    """Parameters governing evidence signal extraction."""

    min_support_count: int = 1
    max_support_count: int = 20
    echo_chamber_penalty: float = 0.30
    independence_discount_threshold: float = 0.50
    # NEW (P1-1): lineage heuristics for independence detection
    lineage_depth_limit: int = 2  # How many citation hops to check
    publisher_domain_weight: float = 0.50  # Weight of publisher domain in independence
    # NEW (external review, P1-2 "evidence aggregation / double counting"):
    # weight applied to an evidence group's contribution to
    # discounted_evidence_strength/discounted_weighted_confidence,
    # keyed by the SHORTEST hop distance at which it was reached.
    # "A supports B supports C": A is real but entirely B-mediated
    # evidence for C, not independent corroboration of C -- these
    # defaults (an engineering-judgment starting point, not
    # cross-validated) discount it rather than either dropping it
    # entirely or counting it as fully independent.
    direct_evidence_weight: float = 1.0  # hop distance == 1
    derived_evidence_weight: float = 0.60  # hop distance == 2 ("one-hop derived")
    multi_hop_evidence_weight: float = 0.30  # hop distance >= 3


@dataclass(frozen=True)
class ConflictPolicy:
    """Parameters governing contradiction pressure computation."""

    max_contradiction_partners: int = 5
    conflict_saturation: float = 0.80
    contradiction_weight_multiplier: float = 1.0


@dataclass(frozen=True)
class TopologyPolicy:
    """
    Parameters governing structural importance signals.

    RECTIFIED (P0-3): hub_bonus and bridge_bonus removed.
    Those are topology implementation details — they belong in the extractor.
    The extractor emits HubScore and BridgeScore as separate signals.
    Policy only controls how centrality is scaled.
    """

    centrality_scale: float = 1.0  # Multiplier for the centrality signal


@dataclass(frozen=True)
class TemporalPolicy:
    """Parameters governing temporal stability signals."""

    default_stability: float = 0.50
    evolution_bonus: float = 0.15
    conflict_penalty: float = 0.10
    recency_window_days: float = 90.0


@dataclass(frozen=True)
class FusionPolicy:
    """
    Signal weights and fusion constraints.

    RECTIFIED (P0-2): Weights are keyed by signal_name (str → float dict).
    This means adding a new signal only requires adding it to the weights dict;
    Fusion reads weights by signal_name, not by fixed field names.

    RECTIFIED (Phase 8.3): validate() now enforces a strict 1:1 mapping
    between policy weights and the active registry of signals.
    Any registered signal missing a weight, or any weight pointing to an
    unregistered signal, raises PolicyError.

    The sum of all positive-direction weights minus negative-direction weights
    must equal 1.0 (validated on construction).
    """

    # Weights keyed by SignalID value (string) — must match the registry exactly
    signal_weights: dict[str, float] = field(
        default_factory=lambda: {
            "evidence_strength": 0.25,
            "evidence_independence": 0.15,
            "source_diversity": 0.15,
            "topology_strength": 0.10,
            "hub_score": 0.05,  # RECTIFIED (P0-3): topology sub-signals
            "bridge_score": 0.05,
            "conflict_pressure": 0.20,
            "temporal_stability": 0.05,
        }
    )

    # Signal directions: "positive" raises RI, "negative" lowers it
    signal_directions: dict[str, str] = field(
        default_factory=lambda: {
            "evidence_strength": "positive",
            "evidence_independence": "positive",
            "source_diversity": "positive",
            "topology_strength": "positive",
            "hub_score": "positive",
            "bridge_score": "positive",
            "conflict_pressure": "negative",
            "temporal_stability": "positive",
        }
    )

    # Fusion constraints
    max_reliability_without_evidence: float = 60.0
    max_reliability_with_max_conflict: float = 40.0
    max_uncertainty_discount: float = 20.0
    # RECTIFIED (P0 external review — dead config/duplicate-source-of-truth
    # sweep): min_reliability_for_high_topology was removed. No
    # FusionConstraint ever read it, and per the P1-4 evidence/importance
    # split (see EVIDENCE_SIGNAL_NAMES / IMPORTANCE_SIGNAL_NAMES above and
    # constraints.TopologyWithoutEvidenceConstraint), a topology-based floor
    # on reliability_index would reintroduce the exact reliability/importance
    # conflation P1-4 removed. IMPORTANCE_CONSTRAINT_PIPELINE is the right
    # place for a topology-native constraint if one is ever justified.

    def validate(self, active_registry_ids: set[SignalID]) -> None:
        """
        Verify weights sum to 1.0 AND match the active registry perfectly.

        Args:
            active_registry_ids: Set of SignalID enums currently registered.

        Raises:
            PolicyError: If any registered signal is missing a weight,
                         or if any weight points to an unregistered signal,
                         or if weights do not sum to 1.0.
        """
        # Convert registry to strings for comparison
        registry_strings = {s.value for s in active_registry_ids}
        policy_strings = set(self.signal_weights.keys())

        # Check for missing signals
        missing_in_policy = registry_strings - policy_strings
        if missing_in_policy:
            raise PolicyError(
                f"Registered signals missing from policy weights: {sorted(missing_in_policy)}. "
                f"Add them to scoring_policy.fusion.signal_weights."
            )

        # Check for extra signals
        missing_in_registry = policy_strings - registry_strings
        if missing_in_registry:
            raise PolicyError(
                f"Policy contains weights for unregistered signals: {sorted(missing_in_registry)}. "
                f"Either register these signals or remove them from scoring_policy.fusion.signal_weights."
            )

        # Check directions consistency (all policy keys should have a direction)
        for name in policy_strings:
            if name not in self.signal_directions:
                raise PolicyError(
                    f"Signal '{name}' has a weight but no direction defined in signal_directions."
                )

        # Sum check (existing logic)
        positive_total = sum(
            w
            for name, w in self.signal_weights.items()
            if self.signal_directions.get(name, "positive") == "positive"
        )
        negative_total = sum(
            w
            for name, w in self.signal_weights.items()
            if self.signal_directions.get(name, "positive") == "negative"
        )
        total = positive_total + negative_total
        if abs(total - 1.0) > 0.001:
            raise PolicyError(
                f"FusionPolicy signal_weights must sum to 1.0, got {total:.4f}. "
                "Adjust scoring_policy.fusion.signal_weights in config."
            )

    def get_weight(self, signal_name: str) -> float:
        """Look up weight by signal name. Returns 0.0 if not registered."""
        return self.signal_weights.get(signal_name, 0.0)

    def get_direction(self, signal_name: str) -> str:
        """Look up direction by signal name. Defaults to 'positive'."""
        return self.signal_directions.get(signal_name, "positive")


@dataclass(frozen=True)
class CalibrationPolicy:
    """Thresholds for mapping Reliability Index → CalibrationLabel."""

    very_high_threshold: float = 80.0
    high_threshold: float = 65.0
    moderate_threshold: float = 45.0
    low_threshold: float = 25.0


@dataclass(frozen=True)
class ReliabilityPolicy:
    """
    Complete policy for one scoring run.
    Loaded from config/default.yaml [scoring_policy] section.
    """

    version: str
    profile: str  # NEW (P1-3): which PolicyProfile was used
    evidence: EvidencePolicy
    conflict: ConflictPolicy
    topology: TopologyPolicy
    temporal: TemporalPolicy
    fusion: FusionPolicy
    calibration: CalibrationPolicy

    def validate(self, active_registry_ids: set[SignalID]) -> None:
        """
        Validate the entire policy against the active registry.
        Delegates to fusion.validate() for the weight-registry mapping.
        """
        self.fusion.validate(active_registry_ids)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def config_hash(self) -> str:
        material = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(material.encode()).hexdigest()[:16]


# ── Policy Profile Presets ────────────────────────────────────────────────────

_PROFILE_WEIGHTS = {
    PolicyProfile.BALANCED: {
        "evidence_strength": 0.25,
        "evidence_independence": 0.15,
        "source_diversity": 0.15,
        "topology_strength": 0.10,
        "hub_score": 0.05,
        "bridge_score": 0.05,
        "conflict_pressure": 0.20,
        "temporal_stability": 0.05,
    },
    PolicyProfile.CONSERVATIVE: {
        "evidence_strength": 0.35,
        "evidence_independence": 0.20,
        "source_diversity": 0.10,
        "topology_strength": 0.05,
        "hub_score": 0.02,
        "bridge_score": 0.03,
        "conflict_pressure": 0.25,
        "temporal_stability": 0.00,
    },
    PolicyProfile.RESEARCH: {
        "evidence_strength": 0.20,
        "evidence_independence": 0.25,
        "source_diversity": 0.25,
        "topology_strength": 0.05,
        "hub_score": 0.03,
        "bridge_score": 0.02,
        "conflict_pressure": 0.15,
        "temporal_stability": 0.05,
    },
    PolicyProfile.EVIDENCE_FIRST: {
        "evidence_strength": 0.45,
        "evidence_independence": 0.10,
        "source_diversity": 0.10,
        "topology_strength": 0.05,
        "hub_score": 0.03,
        "bridge_score": 0.02,
        "conflict_pressure": 0.20,
        "temporal_stability": 0.05,
    },
}

_PROFILE_DIRECTIONS = {
    "evidence_strength": "positive",
    "evidence_independence": "positive",
    "source_diversity": "positive",
    "topology_strength": "positive",
    "hub_score": "positive",
    "bridge_score": "positive",
    "conflict_pressure": "negative",
    "temporal_stability": "positive",
}


def load_policy(
    profile: PolicyProfile = PolicyProfile.BALANCED,
) -> ReliabilityPolicy:
    """
    Load ReliabilityPolicy from config/default.yaml [scoring_policy] section.

    Args:
        profile: Which PolicyProfile preset to apply (RECTIFIED P1-3).
                 Config can override the profile via scoring_policy.profile.

    Returns:
        ReliabilityPolicy (not yet validated against the registry).
        Caller must call policy.validate(active_registry_ids) after loading.
    """
    config = get_config()
    sp = config.get("scoring_policy", {})

    # Determine active profile
    profile_str = sp.get("profile", profile.value)
    try:
        active_profile = PolicyProfile(profile_str)
    except ValueError:
        logger.warning("unknown policy profile, using BALANCED", profile=profile_str)
        active_profile = PolicyProfile.BALANCED

    ev_cfg = sp.get("evidence", {})
    co_cfg = sp.get("conflict", {})
    to_cfg = sp.get("topology", {})
    te_cfg = sp.get("temporal", {})
    fu_cfg = sp.get("fusion", {})
    ca_cfg = sp.get("calibration", {})

    # Signal weights: start from profile preset, allow config override
    preset_weights = dict(_PROFILE_WEIGHTS[active_profile])
    config_weights = fu_cfg.get("signal_weights", {})
    preset_weights.update(config_weights)  # Config overrides preset

    fusion = FusionPolicy(
        signal_weights=preset_weights,
        signal_directions=dict(_PROFILE_DIRECTIONS),
        max_reliability_without_evidence=fu_cfg.get("max_reliability_without_evidence", 60.0),
        max_reliability_with_max_conflict=fu_cfg.get("max_reliability_with_max_conflict", 40.0),
        max_uncertainty_discount=fu_cfg.get("max_uncertainty_discount", 20.0),
    )

    policy = ReliabilityPolicy(
        version=sp.get("version", POLICY_VERSION),
        profile=active_profile.value,
        evidence=EvidencePolicy(
            min_support_count=ev_cfg.get("min_support_count", 1),
            max_support_count=ev_cfg.get("max_support_count", 20),
            echo_chamber_penalty=ev_cfg.get("echo_chamber_penalty", 0.30),
            independence_discount_threshold=ev_cfg.get("independence_discount_threshold", 0.50),
            lineage_depth_limit=ev_cfg.get("lineage_depth_limit", 2),
            publisher_domain_weight=ev_cfg.get("publisher_domain_weight", 0.50),
            direct_evidence_weight=ev_cfg.get("direct_evidence_weight", 1.0),
            derived_evidence_weight=ev_cfg.get("derived_evidence_weight", 0.60),
            multi_hop_evidence_weight=ev_cfg.get("multi_hop_evidence_weight", 0.30),
        ),
        conflict=ConflictPolicy(
            max_contradiction_partners=co_cfg.get("max_contradiction_partners", 5),
            conflict_saturation=co_cfg.get("conflict_saturation", 0.80),
            contradiction_weight_multiplier=co_cfg.get("contradiction_weight_multiplier", 1.0),
        ),
        topology=TopologyPolicy(
            centrality_scale=to_cfg.get("centrality_scale", 1.0),
        ),
        temporal=TemporalPolicy(
            default_stability=te_cfg.get("default_stability", 0.50),
            evolution_bonus=te_cfg.get("evolution_bonus", 0.15),
            conflict_penalty=te_cfg.get("conflict_penalty", 0.10),
            recency_window_days=te_cfg.get("recency_window_days", 90.0),
        ),
        fusion=fusion,
        calibration=CalibrationPolicy(
            very_high_threshold=ca_cfg.get("very_high_threshold", 80.0),
            high_threshold=ca_cfg.get("high_threshold", 65.0),
            moderate_threshold=ca_cfg.get("moderate_threshold", 45.0),
            low_threshold=ca_cfg.get("low_threshold", 25.0),
        ),
    )

    logger.info(
        "policy loaded (validation deferred to caller)",
        version=policy.version,
        profile=active_profile.value,
        config_hash=policy.config_hash(),
    )
    return policy
