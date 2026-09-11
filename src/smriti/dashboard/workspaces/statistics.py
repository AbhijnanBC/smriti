"""
statistics.py — StatisticsWorkspace.

Investigative objective: Analyze global knowledge base characteristics.
Views coordinated: StatisticsView
"""

from __future__ import annotations

from smriti.core.models import EpistemicLens, WorkspaceProfile, WorkspaceType
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.views.statistics_view import StatisticsView
from smriti.dashboard.workspaces.base import BaseWorkspace
from smriti.dashboard.workspaces.context import WorkspaceContext


class StatisticsWorkspace(BaseWorkspace):
    """Global statistics and distribution analysis workspace."""

    @property
    def profile(self) -> WorkspaceProfile:
        return WorkspaceProfile(
            workspace_type=WorkspaceType.STATISTICS,
            investigative_objective="Analyze knowledge base characteristics and distributions",
            default_lens=EpistemicLens.EXPLORATION,
            default_explainability=0,
            primary_views=("statistics",),
            navigation_strategy="aggregate",
        )

    def _fetch_and_refresh(self, context: WorkspaceContext) -> None:
        stats_dto = context.client.get_statistics()
        stats_pm = DTOTransformer.to_statistics_pm(stats_dto) if stats_dto else None
        StatisticsView(stats=stats_pm).render()
