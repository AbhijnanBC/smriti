"""
normalization.py — Signal assembly and ContributionSet construction.

RECTIFIED (P0-2): This module no longer builds SignalVector as the primary output
for Fusion. Instead it builds ContributionSet — a generic list of
ContributionCandidates that Fusion can process without knowing signal names.

RECTIFIED (P1-2): Normalization is now owned by each extractor. This module
assembles and validates extractor-normalized values — it never re-normalizes.

RECTIFIED (P0-4): Builds SignalManifest list from extractor.build_manifest().

SignalVector is still built for backward compatibility (serialization, tests).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple
import structlog

from smriti.core.models import (
    RawSignal, SignalVector, ContributionCandidate, ContributionSet,
    SignalManifest, SignalStatus, SignalID,
)
from smriti.scoring.policies import FusionPolicy
from smriti.scoring.signals.base import BaseSignalExtractor

logger = structlog.get_logger(__name__)


def assemble_contribution_set(
    raw_signals: List[RawSignal],
    extractors: List[BaseSignalExtractor],
    fusion_policy: FusionPolicy,
    claim_id: str,
) -> Tuple[ContributionSet, List[SignalManifest], SignalVector]:
    """
    RECTIFIED (P0-2, P0-4, P1-2): Primary assembly function.

    Validates extractor-normalized values and builds:
        - ContributionSet: for generic Fusion (signal-name-agnostic)
        - List[SignalManifest]: for derivation tracing (P0-4)
        - SignalVector: for backward-compatible serialization

    Args:
        raw_signals:    RawSignal list from all extractors.
        extractors:     The extractor instances (for manifest building).
        fusion_policy:  FusionPolicy for weights and directions.
        claim_id:       For logging and ContributionSet.

    Returns:
        (ContributionSet, manifests, signal_vector)
    """
    # FIXED: Use .value to get string keys for lookup by sig.name (a string)
    extractor_map = {e.signal_id.value: e for e in extractors}
    validated: Dict[str, RawSignal] = {}
    status_map: Dict[str, str] = {}
    manifests: List[SignalManifest] = []

    for sig in raw_signals:
        value = sig.normalized_value  # Extractor already normalized (P1-2)
        status = sig.status
        quality_flags = []

        # Validate extractor-normalized value
        if math.isnan(value):
            logger.warning("NaN normalized signal", signal=sig.name)
            value = 0.0
            status = SignalStatus.UNAVAILABLE
            quality_flags.append("nan_detected")
        elif math.isinf(value):
            logger.warning("Inf normalized signal", signal=sig.name)
            value = 0.0
            status = SignalStatus.UNAVAILABLE
            quality_flags.append("inf_detected")
        elif not (0.0 <= value <= 1.0):
            logger.warning("out-of-range normalized signal", signal=sig.name, value=value)
            value = max(0.0, min(1.0, value))
            quality_flags.append("clamped_out_of_range")

        # Build validated RawSignal (normalized_value may have been corrected)
        corrected_sig = RawSignal(
            name=sig.name,
            raw_value=sig.raw_value,
            normalized_value=value,
            status=status,
            metadata=sig.metadata,
        )
        validated[sig.name] = corrected_sig
        status_map[sig.name] = status.value

        # Build SignalManifest (P0-4) - now lookup works because keys are strings
        extractor = extractor_map.get(sig.name)
        if extractor:
            manifest = extractor.build_manifest(corrected_sig, quality_flags)
            manifests.append(manifest)

    # ── Build ContributionSet (P0-2) ────────────────────────────────────────
    candidates = []
    for signal_id_value, sig in validated.items():
        # `validated` is keyed by the raw string signal name (RawSignal.name).
        # ContributionCandidate.signal_id is typed as SignalID (see core/models.py)
        # so it must be the enum member, not the bare string key — otherwise
        # downstream consumers that call `.signal_id.value` (e.g.
        # ComponentScore.signal_name) blow up with AttributeError.
        weight = fusion_policy.get_weight(signal_id_value)
        direction = fusion_policy.get_direction(signal_id_value)
        if weight > 0:
            candidates.append(ContributionCandidate(
                signal_id=SignalID(signal_id_value),
                normalized_value=sig.normalized_value,
                policy_weight=weight,
                direction=direction,
                label=signal_id_value.replace("_", " ").title(),
                raw_value=sig.raw_value,
            ))

    evidence_completeness = _compute_completeness(status_map)

    contribution_set = ContributionSet(
        candidates=tuple(candidates),
        evidence_completeness=evidence_completeness,
        claim_id=claim_id,
    )

    # ── Build SignalVector for backward compatibility ─────────────────────────
    def get_norm(name: str) -> float:
        return validated[name].normalized_value if name in validated else 0.0

    signal_vector = SignalVector(
        evidence_strength=get_norm("evidence_strength"),
        evidence_independence=get_norm("evidence_independence"),
        source_diversity=get_norm("source_diversity"),
        topology_strength=get_norm("topology_strength"),
        conflict_pressure=get_norm("conflict_pressure"),
        temporal_stability=get_norm("temporal_stability"),
        evidence_completeness=evidence_completeness,
        statuses=status_map,
    )

    return contribution_set, manifests, signal_vector


def _compute_completeness(status_map: Dict[str, str]) -> float:
    """Fraction of signals with actual measurements."""
    total = max(1, len(status_map))
    measured = sum(
        1 for status in status_map.values()
        if status in (SignalStatus.MEASURED.value, SignalStatus.ESTIMATED.value)
    )
    return measured / total


# ── Backward-compatible wrapper for tests that use validate_and_normalize ─────

def validate_and_normalize(raw_signals: List[RawSignal]) -> SignalVector:
    """
    Backward-compatible wrapper. Tests that test normalization directly use this.
    Production code uses assemble_contribution_set().
    """
    status_map: Dict[str, str] = {}
    signal_map: Dict[str, float] = {}

    for sig in raw_signals:
        value = sig.normalized_value
        status = sig.status

        if math.isnan(value):
            value = 0.0
            status = SignalStatus.UNAVAILABLE
        elif math.isinf(value):
            value = 0.0
            status = SignalStatus.UNAVAILABLE
        elif not (0.0 <= value <= 1.0):
            value = max(0.0, min(1.0, value))

        signal_map[sig.name] = value
        status_map[sig.name] = status.value

    def get(name: str) -> float:
        return signal_map.get(name, 0.0)

    return SignalVector(
        evidence_strength=get("evidence_strength"),
        evidence_independence=get("evidence_independence"),
        source_diversity=get("source_diversity"),
        topology_strength=get("topology_strength"),
        conflict_pressure=get("conflict_pressure"),
        temporal_stability=get("temporal_stability"),
        evidence_completeness=_compute_completeness(status_map),
        statuses=status_map,
    )