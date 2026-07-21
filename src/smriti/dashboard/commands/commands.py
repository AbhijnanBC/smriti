"""
commands.py — Interaction Command objects for Phase 10.

Every user action is a Command. Commands are the formal interface between
the UI layer and the InteractionDispatcher.

Architecture:
    UI event
        │
        ▼
    Command (intent + payload)
        │
        ▼
    InteractionDispatcher
        │
        ├── PolicyEngine.validate()
        │
        ├── EpistemicStateManager.transition()
        │
        └── InteractionEventBus.publish()

Rules:
    ✅ Commands are immutable value objects
    ✅ Commands carry all context needed for dispatch
    ✅ Commands are typed — no stringly-typed action strings
    ❌ Commands never call state transitions directly
    ❌ Commands never access Phase 9
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from smriti.core.models import (
    EpistemicLens,
    ExplainabilityLevel,
    WorkspaceType,
)


@dataclass(frozen=True)
class BaseCommand:
    """Base for all interaction commands. Immutable."""
    session_id: str
    origin: str = "ui"   # "ui" | "system" | "test"


@dataclass(frozen=True)
class SelectClaimCommand(BaseCommand):
    """User selected a claim from a list or graph."""
    claim_id: str = ""
    source_view: str = ""    # Which view triggered this (for event tracing)


@dataclass(frozen=True)
class DeselectClaimCommand(BaseCommand):
    """User deselected the active claim."""
    pass


@dataclass(frozen=True)
class ActivateWorkspaceCommand(BaseCommand):
    """User switched to a different workspace."""
    workspace_type: WorkspaceType = WorkspaceType.RESEARCH
    lens: Optional[EpistemicLens] = None


@dataclass(frozen=True)
class ChangeLensCommand(BaseCommand):
    """User changed the active epistemic lens."""
    lens: EpistemicLens = EpistemicLens.EXPLORATION


@dataclass(frozen=True)
class ApplyFilterCommand(BaseCommand):
    """User applied a filter to the claim list."""
    field: str = ""
    value: Any = None


@dataclass(frozen=True)
class RemoveFilterCommand(BaseCommand):
    """User removed one active filter."""
    field: str = ""


@dataclass(frozen=True)
class ClearFiltersCommand(BaseCommand):
    """User cleared all active filters."""
    pass


@dataclass(frozen=True)
class SubmitSearchCommand(BaseCommand):
    """User submitted a search query."""
    query: str = ""


@dataclass(frozen=True)
class NavigateToCommand(BaseCommand):
    """User navigated to a claim via graph or breadcrumb."""
    claim_id: str = ""
    label: str = ""


@dataclass(frozen=True)
class NavigateBackCommand(BaseCommand):
    """User pressed the Back button."""
    pass


@dataclass(frozen=True)
class SetExplainabilityCommand(BaseCommand):
    """User changed the explainability depth."""
    level: int = 0   # ExplainabilityLevel value


@dataclass(frozen=True)
class CompareCommand(BaseCommand):
    """User initiated or updated a claim comparison."""
    claim_ids: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EndComparisonCommand(BaseCommand):
    """User closed the comparison panel."""
    pass


@dataclass(frozen=True)
class ExportCommand(BaseCommand):
    """User requested data export."""
    format: str = "json"      # "json" | "csv"
    scope: str = "current"    # "current" | "all"


@dataclass(frozen=True)
class SetPageCommand(BaseCommand):
    """User navigated to a different page of results."""
    page: int = 0


@dataclass(frozen=True)
class SetSortCommand(BaseCommand):
    """User changed the sort order."""
    sort_field: str = "reliability_index"
    sort_order: str = "desc"


@dataclass(frozen=True)
class SerializeWorkspaceCommand(BaseCommand):
    """System request to serialize current workspace state."""
    pass


@dataclass(frozen=True)
class RestoreWorkspaceCommand(BaseCommand):
    """System request to restore workspace from a snapshot."""
    snapshot: Dict[str, Any] = field(default_factory=dict)