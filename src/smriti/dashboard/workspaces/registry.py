"""registry.py — WorkspaceRegistry."""

from __future__ import annotations
from typing import Dict, Type
from smriti.core.models import WorkspaceType
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.exceptions import WorkspaceNotFoundError


class WorkspaceRegistry:
    def __init__(self) -> None:
        self._registry: Dict[WorkspaceType, Type[BaseWorkspace]] = {}

    def register(self, workspace_cls: Type[BaseWorkspace]) -> None:
        instance = workspace_cls()
        self._registry[instance.profile.workspace_type] = workspace_cls

    def get(self, workspace_type: WorkspaceType) -> BaseWorkspace:
        if workspace_type not in self._registry:
            raise WorkspaceNotFoundError(
                f"Workspace '{workspace_type.value}' is not registered."
            )
        return self._registry[workspace_type]()

    def all_types(self) -> list:
        return sorted(self._registry.keys(), key=lambda t: t.value)

    def is_registered(self, workspace_type: WorkspaceType) -> bool:
        return workspace_type in self._registry


def build_default_registry() -> WorkspaceRegistry:
    from smriti.dashboard.workspaces.research    import ResearchWorkspace
    from smriti.dashboard.workspaces.reliability import ReliabilityWorkspace
    from smriti.dashboard.workspaces.conflict    import ConflictWorkspace
    from smriti.dashboard.workspaces.audit       import AuditWorkspace
    from smriti.dashboard.workspaces.provenance  import ProvenanceWorkspace
    from smriti.dashboard.workspaces.statistics  import StatisticsWorkspace
    from smriti.dashboard.workspaces.topology    import TopologyWorkspace

    registry = WorkspaceRegistry()
    for cls in [ResearchWorkspace, ReliabilityWorkspace, ConflictWorkspace,
                AuditWorkspace, ProvenanceWorkspace, StatisticsWorkspace, TopologyWorkspace]:
        registry.register(cls)
    return registry