"""Unit tests for workspace lifecycle methods."""

from smriti.core.models import WorkspaceStatus, WorkspaceType
from smriti.dashboard.workspaces.registry import build_default_registry


def test_all_workspaces_support_full_lifecycle():
    """Every workspace must survive create→activate→suspend→resume→dispose."""
    registry = build_default_registry()
    for ws_type in WorkspaceType:
        ws = registry.get(ws_type)
        assert (
            ws.status == WorkspaceStatus.CREATED
        ), f"{ws_type.value}: expected CREATED after construction"

        ws.on_suspend()
        assert ws.status == WorkspaceStatus.SUSPENDED

        # on_resume with no context arg (default no-op)
        ws.on_resume(context=None)
        assert ws.status == WorkspaceStatus.ACTIVE

        ws.on_dispose()
        assert ws.status == WorkspaceStatus.DISPOSED


def test_workspace_profile_has_capabilities():
    """WorkspaceProfile must include capabilities."""
    from smriti.core.models import WorkspaceCapabilities

    registry = build_default_registry()
    for ws_type in WorkspaceType:
        ws = registry.get(ws_type)
        assert isinstance(
            ws.profile.capabilities, WorkspaceCapabilities
        ), f"{ws_type.value} missing capabilities"


def test_workspace_profile_has_version():
    """WorkspaceProfile must include version."""
    from smriti.core.models import WorkspaceVersion

    registry = build_default_registry()
    for ws_type in WorkspaceType:
        ws = registry.get(ws_type)
        assert isinstance(ws.profile.version, WorkspaceVersion), f"{ws_type.value} missing version"
