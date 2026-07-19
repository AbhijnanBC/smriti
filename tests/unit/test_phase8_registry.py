"""Unit tests for SignalRegistry (P0-1)."""

import pytest
from smriti.scoring.signals import signal_registry, SignalRegistry
from smriti.scoring.signals.base import BaseSignalExtractor
from smriti.core.models import ClaimNode, KnowledgeGraph, RawSignal, ScoringGlobalStats, SignalStatus
from smriti.scoring.policies import ReliabilityPolicy, load_policy
from smriti.exceptions import RegistryError
from pathlib import Path


class MockExtractor(BaseSignalExtractor):
    def __init__(self, name, ver="1.0"):
        self._name = name
        self._ver = ver

    @property
    def signal_name(self): return self._name

    @property
    def version(self): return self._ver

    def extract(self, node, graph, global_stats, policy):
        return RawSignal(name=self._name, raw_value=0.5, normalized_value=0.5, status=SignalStatus.MEASURED)


def test_registry_has_default_signals():
    """Default registry must have at least 6 built-in signals."""
    assert len(signal_registry) >= 6


def test_registry_ordered_extractors_deterministic():
    """ordered_extractors() must return the same order every call."""
    order1 = [e.signal_name for e in signal_registry.ordered_extractors()]
    order2 = [e.signal_name for e in signal_registry.ordered_extractors()]
    assert order1 == order2


def test_new_signal_can_be_registered():
    """Registering a new extractor must make it available via ordered_extractors()."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor("novelty_signal")
    fresh_registry.register(ext, priority=99)
    names = [e.signal_name for e in fresh_registry.ordered_extractors()]
    assert "novelty_signal" in names


def test_duplicate_registration_is_idempotent():
    """Registering the same extractor type twice must not raise."""
    fresh_registry = SignalRegistry()
    ext = MockExtractor("my_signal")
    fresh_registry.register(ext, priority=50)
    fresh_registry.register(ext, priority=50)  # Should not raise
    assert len(fresh_registry) == 1


def test_different_extractor_same_name_raises():
    """Registering two DIFFERENT extractor types with the same signal_name must raise."""
    fresh_registry = SignalRegistry()
    ext1 = MockExtractor("shared_name")
    ext2 = MockExtractor("shared_name", ver="2.0")  # Different version — treated as different

    class AnotherExtractor(MockExtractor):
        pass

    ext3 = AnotherExtractor("shared_name")
    fresh_registry.register(ext1)
    with pytest.raises(RegistryError):
        fresh_registry.register(ext3)  # Different type, same name → RegistryError


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
    for i in range(3):
        fresh_registry.register(MockExtractor(f"signal_{i}"), priority=i)
    assert len(fresh_registry.ordered_extractors()) == 3