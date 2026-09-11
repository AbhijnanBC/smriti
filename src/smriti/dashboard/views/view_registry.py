"""
view_registry.py — ViewRegistry and ViewFactory for Phase 10.

Instead of hardcoded imports, workspaces request views by name.
ViewFactory instantiates them with correct context.
This makes view composition dynamic and testable.
"""

from __future__ import annotations

from smriti.dashboard.views.base_view import BaseView
from smriti.exceptions import ViewRegistryError


class ViewRegistry:
    """
    Registry of all available view types.
    Register once during bootstrap; instantiate via ViewFactory.
    """

    def __init__(self) -> None:
        self._registry: dict[str, type[BaseView]] = {}

    def register(self, name: str, view_cls: type[BaseView]) -> None:
        """Register a view class under a name."""
        self._registry[name] = view_cls

    def is_registered(self, name: str) -> bool:
        return name in self._registry

    def all_names(self) -> list:
        return list(self._registry.keys())

    def get_class(self, name: str) -> type[BaseView]:
        if name not in self._registry:
            raise ViewRegistryError(f"View '{name}' not registered.")
        return self._registry[name]


class ViewFactory:
    """
    Creates view instances from the registry with injected context.
    """

    def __init__(self, registry: ViewRegistry) -> None:
        self._registry = registry

    def create(self, name: str, **kwargs) -> BaseView:
        """Instantiate a view by name, passing kwargs to its constructor."""
        view_cls = self._registry.get_class(name)
        return view_cls(**kwargs)


def build_default_view_registry() -> ViewRegistry:
    """Register all Phase 10 views."""
    from smriti.dashboard.views.audit_view import AuditView
    from smriti.dashboard.views.conflict_view import ConflictView
    from smriti.dashboard.views.inspector_view import InspectorView
    from smriti.dashboard.views.navigation_view import NavigationView
    from smriti.dashboard.views.reliability_view import ReliabilityView
    from smriti.dashboard.views.result_list_view import ResultListView
    from smriti.dashboard.views.search_view import SearchView
    from smriti.dashboard.views.statistics_view import StatisticsView

    registry = ViewRegistry()
    registry.register("search", SearchView)
    registry.register("result_list", ResultListView)
    registry.register("inspector", InspectorView)
    registry.register("navigation", NavigationView)
    registry.register("reliability", ReliabilityView)
    registry.register("conflict", ConflictView)
    registry.register("audit", AuditView)
    registry.register("statistics", StatisticsView)
    return registry
