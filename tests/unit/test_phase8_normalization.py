"""Unit tests for scoring/normalization.py."""

from smriti.core.models import RawSignal, SignalStatus, SignalVector
from smriti.scoring.normalization import (
    assemble_contribution_set,
    split_contribution_set_by_category,
    validate_and_normalize,
)
from smriti.scoring.policies import EVIDENCE_SIGNAL_NAMES, IMPORTANCE_SIGNAL_NAMES, load_policy
from smriti.scoring.signals import signal_registry


def make_raw(name: str, value: float, status=SignalStatus.MEASURED, raw_value=None) -> RawSignal:
    return RawSignal(
        name=name,
        raw_value=raw_value if raw_value is not None else value,
        normalized_value=value,
        status=status,
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

    evidence_manifest = next((m for m in manifests if m.signal_id == "evidence_strength"), None)
    assert evidence_manifest is not None
    assert evidence_manifest.normalization_strategy != ""


# ── P1-4: reliability vs. graph importance split (external "reality check" review) ──


def _make_full_contribution_set():
    policy = load_policy()
    extractors = signal_registry.ordered_extractors()
    signals = [
        make_raw("evidence_strength", 0.80, raw_value=0.72),
        make_raw("evidence_independence", 0.70),
        make_raw("source_diversity", 0.60),
        make_raw("topology_strength", 0.50),
        make_raw("hub_score", 0.30),
        make_raw("bridge_score", 0.20),
        make_raw("conflict_pressure", 0.20),
        make_raw("temporal_stability", 0.75),
    ]
    cs, _, _ = assemble_contribution_set(signals, extractors, policy.fusion, "c001")
    return cs, policy


def test_split_by_evidence_category_keeps_only_evidence_signals():
    cs, _ = _make_full_contribution_set()
    evidence_cs = split_contribution_set_by_category(cs, EVIDENCE_SIGNAL_NAMES)
    names = {c.signal_id.value for c in evidence_cs.candidates}
    assert names <= EVIDENCE_SIGNAL_NAMES
    assert names  # non-empty for this fixture


def test_split_by_importance_category_keeps_only_importance_signals():
    cs, _ = _make_full_contribution_set()
    importance_cs = split_contribution_set_by_category(cs, IMPORTANCE_SIGNAL_NAMES)
    names = {c.signal_id.value for c in importance_cs.candidates}
    assert names <= IMPORTANCE_SIGNAL_NAMES
    assert names  # non-empty for this fixture


def test_split_evidence_and_importance_partition_the_full_set():
    """Every candidate in the full set must land in exactly one of the
    two category splits -- no signal silently dropped, none double-counted."""
    cs, _ = _make_full_contribution_set()
    evidence_cs = split_contribution_set_by_category(cs, EVIDENCE_SIGNAL_NAMES)
    importance_cs = split_contribution_set_by_category(cs, IMPORTANCE_SIGNAL_NAMES)
    evidence_names = {c.signal_id.value for c in evidence_cs.candidates}
    importance_names = {c.signal_id.value for c in importance_cs.candidates}
    all_names = {c.signal_id.value for c in cs.candidates}
    assert not (evidence_names & importance_names)
    assert evidence_names | importance_names == all_names


def test_split_rescales_weights_to_sum_to_one_within_category():
    """RECTIFIED (P1-4): a category whose raw policy weights only sum to a
    fraction of the original 1.0 budget must be rescaled so it can produce
    a genuine [0,100] index on its own, not one capped at that fraction."""
    cs, _ = _make_full_contribution_set()
    evidence_cs = split_contribution_set_by_category(cs, EVIDENCE_SIGNAL_NAMES)
    importance_cs = split_contribution_set_by_category(cs, IMPORTANCE_SIGNAL_NAMES)
    assert abs(sum(c.policy_weight for c in evidence_cs.candidates) - 1.0) < 1e-6
    assert abs(sum(c.policy_weight for c in importance_cs.candidates) - 1.0) < 1e-6


def test_split_preserves_normalized_values_and_directions():
    cs, _ = _make_full_contribution_set()
    original = {c.signal_id.value: c for c in cs.candidates}
    evidence_cs = split_contribution_set_by_category(cs, EVIDENCE_SIGNAL_NAMES)
    for c in evidence_cs.candidates:
        assert c.normalized_value == original[c.signal_id.value].normalized_value
        assert c.direction == original[c.signal_id.value].direction


def test_split_of_empty_category_returns_empty_candidates_without_crash():
    cs, _ = _make_full_contribution_set()
    result = split_contribution_set_by_category(cs, frozenset({"nonexistent_signal"}))
    assert result.candidates == ()
