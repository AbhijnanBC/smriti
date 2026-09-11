"""
policies.py — Interaction policies for Phase 10.

Interaction Policies define HOW knowledge may be explored.
They influence the interaction environment ONLY.
They never influence the underlying knowledge.

RECTIFIED: Added PerformancePolicy as a hard circuit-breaker to protect
against malicious or overwhelmingly massive queries (infinite pagination,
unbounded graph traversals, etc.).
RECTIFIED: PolicyEngine now includes validate_pagination method to enforce
the performance limit on pagination offset.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class VisualizationPolicy:
    max_nodes_in_graph: int = 50
    max_edges_in_graph: int = 100
    max_traversal_depth: int = 3


@dataclass(frozen=True)
class NavigationPolicy:
    max_breadcrumb_depth: int = 8
    max_history_length: int = 20
    allow_cross_partition_navigation: bool = True


@dataclass(frozen=True)
class ComparisonPolicy:
    max_comparison_claims: int = 2
    allow_cross_workspace_comparison: bool = False


@dataclass(frozen=True)
class ExplainabilityPolicy:
    default_level: int = 0
    audit_workspace_default: int = 3
    research_workspace_default: int = 1


@dataclass(frozen=True)
class ExportPolicy:
    allow_json_export: bool = True
    allow_csv_export: bool = True
    allow_graphml_export: bool = False
    max_claims_in_export: int = 10000


@dataclass(frozen=True)
class PerformancePolicy:
    """
    Architectural invariants protecting system resources.
    Acts as a hard circuit-breaker against DOS attacks or accidental overload.
    """

    maximum_rendered_nodes: int = 500
    maximum_traversal_depth: int = 5
    maximum_pagination_offset: int = 10000  # Prevent deep pagination DOS
    lazy_loading_threshold_ms: float = 200.0
    cache_ttl_seconds: int = 3600


@dataclass(frozen=True)
class InteractionPolicy:
    """Complete policy configuration for one interaction session."""

    visualization: VisualizationPolicy = field(default_factory=VisualizationPolicy)
    navigation: NavigationPolicy = field(default_factory=NavigationPolicy)
    comparison: ComparisonPolicy = field(default_factory=ComparisonPolicy)
    explainability: ExplainabilityPolicy = field(default_factory=ExplainabilityPolicy)
    export: ExportPolicy = field(default_factory=ExportPolicy)
    performance: PerformancePolicy = field(default_factory=PerformancePolicy)


class PolicyEngine:
    """Validates interactions against InteractionPolicy. Returns (allowed, reason)."""

    def __init__(self, policy: InteractionPolicy = None) -> None:
        self._policy = policy or InteractionPolicy()

    def validate_graph_size(self, node_count: int) -> tuple:
        max_n = self._policy.visualization.max_nodes_in_graph
        if node_count > max_n:
            return False, f"Graph too large: {node_count} nodes (max {max_n})"
        return True, ""

    def validate_comparison(self, claim_count: int) -> tuple:
        max_c = self._policy.comparison.max_comparison_claims
        if claim_count > max_c:
            return False, f"Too many claims for comparison: {claim_count} (max {max_c})"
        return True, ""

    def validate_export(self, fmt: str) -> tuple:
        ep = self._policy.export
        if fmt == "json" and not ep.allow_json_export:
            return False, "JSON export not allowed"
        if fmt == "csv" and not ep.allow_csv_export:
            return False, "CSV export not allowed"
        if fmt == "graphml" and not ep.allow_graphml_export:
            return False, "GraphML export not allowed"
        return True, ""

    def validate_traversal_depth(self, depth: int) -> tuple:
        max_d = self._policy.visualization.max_traversal_depth
        if depth > max_d:
            return False, f"Traversal depth {depth} exceeds limit {max_d}"
        return True, ""

    # NEW METHOD ADDED HERE
    def validate_pagination(self, offset: int) -> tuple:
        max_offset = self._policy.performance.maximum_pagination_offset
        if offset > max_offset:
            return False, f"Pagination offset {offset} exceeds performance limit of {max_offset}"
        return True, ""

    def validate_command(self, command) -> tuple:
        """
        Generic entry point used by InteractionDispatcher._validate_policy()
        for every command type. Dispatches to the relevant specific
        validate_* method above based on the command's own payload;
        commands with no policy-relevant limit are allowed unconditionally.

        Without this method, InteractionDispatcher.dispatch() raises
        AttributeError for every command when used with a real PolicyEngine
        (previously only test doubles defined validate_command).
        """
        # Local import to avoid a hard import-time dependency from
        # policies.py (dashboard/policies/) on commands.py (dashboard/commands/).
        from smriti.dashboard.commands.commands import CompareCommand, ExportCommand, SetPageCommand

        if isinstance(command, CompareCommand):
            return self.validate_comparison(len(command.claim_ids))

        if isinstance(command, ExportCommand):
            return self.validate_export(command.format)

        if isinstance(command, SetPageCommand):
            return self.validate_pagination(command.page)

        return True, ""

    @property
    def policy(self) -> InteractionPolicy:
        return self._policy


def load_interaction_policy() -> InteractionPolicy:
    """Load interaction policy from config/default.yaml."""
    try:
        from smriti.core.config import get_config

        config = get_config()
        p10_cfg = config.get("interaction", {})

        vis_cfg = p10_cfg.get("visualization", {})
        nav_cfg = p10_cfg.get("navigation", {})
        comp_cfg = p10_cfg.get("comparison", {})
        exp_cfg = p10_cfg.get("explainability", {})
        expo_cfg = p10_cfg.get("export", {})
        perf_cfg = p10_cfg.get("performance", {})

        return InteractionPolicy(
            visualization=VisualizationPolicy(
                max_nodes_in_graph=vis_cfg.get("max_nodes_in_graph", 50),
                max_edges_in_graph=vis_cfg.get("max_edges_in_graph", 100),
                max_traversal_depth=vis_cfg.get("max_traversal_depth", 3),
            ),
            navigation=NavigationPolicy(
                max_breadcrumb_depth=nav_cfg.get("max_breadcrumb_depth", 8),
                max_history_length=nav_cfg.get("max_history_length", 20),
                allow_cross_partition_navigation=nav_cfg.get(
                    "allow_cross_partition_navigation", True
                ),
            ),
            comparison=ComparisonPolicy(
                max_comparison_claims=comp_cfg.get("max_comparison_claims", 2),
                allow_cross_workspace_comparison=comp_cfg.get(
                    "allow_cross_workspace_comparison", False
                ),
            ),
            explainability=ExplainabilityPolicy(
                default_level=exp_cfg.get("default_level", 0),
                audit_workspace_default=exp_cfg.get("audit_workspace_default", 3),
                research_workspace_default=exp_cfg.get("research_workspace_default", 1),
            ),
            export=ExportPolicy(
                allow_json_export=expo_cfg.get("allow_json_export", True),
                allow_csv_export=expo_cfg.get("allow_csv_export", True),
                allow_graphml_export=expo_cfg.get("allow_graphml_export", False),
                max_claims_in_export=expo_cfg.get("max_claims_in_export", 10000),
            ),
            performance=PerformancePolicy(
                maximum_rendered_nodes=perf_cfg.get("maximum_rendered_nodes", 500),
                maximum_traversal_depth=perf_cfg.get("maximum_traversal_depth", 5),
                maximum_pagination_offset=perf_cfg.get("maximum_pagination_offset", 10000),
                lazy_loading_threshold_ms=perf_cfg.get("lazy_loading_threshold_ms", 200.0),
                cache_ttl_seconds=perf_cfg.get("cache_ttl_seconds", 3600),
            ),
        )
    except Exception:
        return InteractionPolicy()
