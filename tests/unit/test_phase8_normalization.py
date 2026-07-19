"""Unit tests for scoring/normalization.py."""

import pytest
from smriti.core.models import RawSignal, SignalStatus, SignalVector
from smriti.scoring.normalization import validate_and_normalize, assemble_contribution_set
from smriti.scoring.policies import load_policy
from smriti.scoring.signals import signal_registry


def make_raw(name: str, value: float, status=SignalStatus.MEASURED, raw_value=None) -> RawSignal:
    return RawSignal(
        name=name, raw_value=raw_value if raw_value is not None else value,
        normalized_value=value, status=status,
    )


def test_valid_signals_produce_signal_vector():
    signals = [
        make_raw("evidence_strength", 0.80),
        make_raw("evidence_independence", 0.70),
        make_raw("source_diversity", 0.60),
        make_raw("topology_strength", 0.50),
        make_raw("conflict_pressure", 0.20),
        make_raw("temporal_stability", 0.75),
    ]
    sv = validate_and_normalize(signals)
    assert isinstance(sv, SignalVector)
    assert sv.evidence_strength == 0.80


def test_nan_signal_becomes_zero():
    signals = [
        make_raw("evidence_strength", float("nan")),
        make_raw("conflict_pressure", 0.20),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 0.0


def test_inf_signal_becomes_zero():
    signals = [
        make_raw("evidence_strength", float("inf")),
        make_raw("conflict_pressure", 0.20),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 0.0


def test_out_of_range_signal_clamped():
    signals = [
        make_raw("evidence_strength", 1.5),
        make_raw("conflict_pressure", -0.3),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_strength == 1.0
    assert sv.conflict_pressure == 0.0


def test_completeness_with_all_measured():
    signals = [
        make_raw("evidence_strength", 0.8, SignalStatus.MEASURED),
        make_raw("evidence_independence", 0.7, SignalStatus.MEASURED),
        make_raw("source_diversity", 0.6, SignalStatus.MEASURED),
        make_raw("topology_strength", 0.5, SignalStatus.MEASURED),
        make_raw("conflict_pressure", 0.2, SignalStatus.MEASURED),
        make_raw("temporal_stability", 0.7, SignalStatus.MEASURED),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_completeness == 1.0


def test_completeness_with_some_unavailable():
    signals = [
        make_raw("evidence_strength", 0.0, SignalStatus.UNAVAILABLE),
        make_raw("evidence_independence", 0.7, SignalStatus.MEASURED),
        make_raw("source_diversity", 0.6, SignalStatus.MEASURED),
        make_raw("topology_strength", 0.0, SignalStatus.UNAVAILABLE),
        make_raw("conflict_pressure", 0.2, SignalStatus.MEASURED),
        make_raw("temporal_stability", 0.7, SignalStatus.DEFAULT),
    ]
    sv = validate_and_normalize(signals)
    assert sv.evidence_completeness < 1.0
    assert sv.evidence_completeness > 0.0


def test_contribution_set_produced():
    """RECTIFIED (P0-2): assemble_contribution_set must produce a ContributionSet."""
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    signals = [
        make_raw("evidence_strength", 0.80, raw_value=0.72),
        make_raw("evidence_independence", 0.70),
        make_raw("source_diversity", 0.60),
        make_raw("topology_strength", 0.50),
        make_raw("hub_score", 0.00),
        make_raw("bridge_score", 0.00),
        make_raw("conflict_pressure", 0.20),
        make_raw("temporal_stability", 0.75),
    ]
    cs, manifests, sv = assemble_contribution_set(signals, extractors, policy.fusion, "c001")
    from smriti.core.models import ContributionSet
    assert isinstance(cs, ContributionSet)
    assert cs.claim_id == "c001"
    assert len(cs.candidates) > 0


def test_signal_manifests_produced():
    """RECTIFIED (P0-4): assemble_contribution_set must produce SignalManifests."""
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    signals = [
        make_raw("evidence_strength", 0.80, raw_value=0.72),
        make_raw("conflict_pressure", 0.20),
    ]
    cs, manifests, sv = assemble_contribution_set(signals, extractors, policy.fusion, "c001")
    from smriti.core.models import SignalManifest
    evidence_manifest = next((m for m in manifests if m.signal_name == "evidence_strength"), None)
    assert evidence_manifest is not None
    assert evidence_manifest.normalization_strategy != ""
    assert isinstance(evidence_manifest.quality_flags, tuple)
    assert isinstance(evidence_manifest.dependency_list, tuple)