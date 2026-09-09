"""Unit tests for SignalRegistry (P0-1)."""

import pytest
from smriti.scoring.signals import signal_registry, SignalRegistry
from smriti.scoring.signals.base import BaseSignalExtractor
from smriti.core.models import (
    ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus, SignalID,
)
from smriti.scoring.policies import ReliabilityPolicy, load_policy
from smriti.exceptions import RegistryError
from pathlib import Path


class MockExtractor(BaseSignalExtractor):
    """
    Test double for BaseSignalExtractor.

    RECTIFIED (Phase 8.2): identification moved from an open `signal_name`
    string to the closed, type-safe `SignalID` enum (see
    src/smriti/scoring/signals/base.py). MockExtractor is keyed by a real
    SignalID member — it exercises registry mechanics (registration,
    idempotency, duplicate detection, ordering), not the identity space
    itself, so using canonical SignalID members is the faithful adaptation.
    """
    def __init__(self, signal_id: SignalID, ver="1.0"):
        self._signal_id = signal_id
        self._ver = ver

    @property
    def signal_id(self): return self._signal_id

    @property
    def version(self): return self._ver

    def extract(self, node, graph, global_stats, policy):
        return RawSignal(name=self._signal_id.value, raw_value=0.5, normalized_value=0.5, status=SignalStatus.MEASURED)


def test_registry_has_default_signals():
    """Default registry must have at least 6 built-in signals."""
    assert len(signal_registry) >= 6


def test_registry_ordered_extractors_deterministic():
    """ordered_extractors() must return the same order every call."""
    order1 = [e.signal_id.value for e in signal_registry.ordered_extractors()]
    order2 = [e.signal_id.value for e in signal_registry.ordered_extractors()]
    assert order1 == order2


def test_new_signal_can_be_registered():
    """Registering a new extractor must make it available via ordered_extractors()."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor(SignalID.HUB_SCORE)
    fresh_registry.register(ext, priority=99)
    names = [e.signal_id.value for e in fresh_registry.ordered_extractors()]
    assert SignalID.HUB_SCORE.value in names


def test_duplicate_registration_is_idempotent():
    """Registering the same extractor type twice must not raise."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor(SignalID.BRIDGE_SCORE)
    fresh_registry.register(ext, priority=50)
    fresh_registry.register(ext, priority=50)  # Should not raise
    assert len(fresh_registry) == 1


def test_different_extractor_same_name_raises():
    """Registering two DIFFERENT extractor types with the same signal_id must raise."""
    fresh_registry = SignalRegistry()
    ext1 = MockExtractor(SignalID.CONFLICT_PRESSURE)
    ext2 = MockExtractor(SignalID.CONFLICT_PRESSURE, ver="2.0")  # Different version — treated as different

    class AnotherExtractor(MockExtractor):
        pass

    ext3 = AnotherExtractor(SignalID.CONFLICT_PRESSURE)
    fresh_registry.register(ext1)
    with pytest.raises(RegistryError):
        fresh_registry.register(ext3)  # Different type, same signal_id → RegistryError


def test_hub_score_and_bridge_score_registered():
    """RECTIFIED (P0-3): hub_score and bridge_score must be in the default registry."""
    names = signal_registry.registered_names
    assert "hub_score" in names, "hub_score must be registered as a separate signal"
    assert "bridge_score" in names, "bridge_score must be registered as a separate signal"


def test_pipeline_never_changes_when_new_signal_registered():
    """
    RECTIFIED (P0-1): The core pipeline (__init__.py) must work identically
    whether 6 or 7 signals are registered — it reads from the registry.
    This test verifies that ordered_extractors() returns the right count.
    """
    fresh_registry = SignalRegistry()
    mock_ids = [SignalID.EVIDENCE_STRENGTH, SignalID.EVIDENCE_INDEPENDENCE, SignalID.SOURCE_DIVERSITY]
    for i, sid in enumerate(mock_ids):
        fresh_registry.register(MockExtractor(sid), priority=i)
    assert len(fresh_registry.ordered_extractors()) == 3
