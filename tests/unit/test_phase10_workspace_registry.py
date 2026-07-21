"""Unit tests for dashboard/workspaces/registry.py."""

import pytest
from smriti.core.models import WorkspaceType
from smriti.dashboard.workspaces.registry import WorkspaceRegistry, build_default_registry
from smriti.exceptions import WorkspaceNotFoundError


def test_default_registry_has_all_workspaces():
    registry = build_default_registry()
    expected = {
        WorkspaceType.RESEARCH, WorkspaceType.RELIABILITY,
        WorkspaceType.CONFLICT, WorkspaceType.AUDIT,
        WorkspaceType.PROVENANCE, WorkspaceType.STATISTICS,
        WorkspaceType.TOPOLOGY,
    }
    for ws_type in expected:
        assert registry.is_registered(ws_type), f"{ws_type.value} not registered"


def test_get_workspace_returns_instance():
    registry = build_default_registry()
    ws = registry.get(WorkspaceType.RESEARCH)
    assert ws is not None
    assert ws.profile.workspace_type == WorkspaceType.RESEARCH


def test_get_unregistered_raises():
    registry = WorkspaceRegistry()
    with pytest.raises(WorkspaceNotFoundError):
        registry.get(WorkspaceType.RESEARCH)


def test_workspace_profiles_have_objectives():
    registry = build_default_registry()
    for ws_type in registry.all_types():
        ws = registry.get(ws_type)
        assert ws.profile.investigative_objective, \
            f"{ws_type.value} has empty investigative_objective"


def test_workspace_profiles_have_default_lens():
    from smriti.core.models import EpistemicLens
    registry = build_default_registry()
    for ws_type in registry.all_types():
        ws = registry.get(ws_type)
        assert isinstance(ws.profile.default_lens, EpistemicLens)


def test_all_types_is_sorted():
    registry = build_default_registry()
    types = registry.all_types()
    assert types == sorted(types, key=lambda t: t.value)