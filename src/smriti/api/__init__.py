"""
api/__init__.py — KnowledgeAccessService: Phase 9 thin public façade.

RECTIFIED (P0-big): The façade is now a THIN WRAPPER around ApplicationService.
It builds requests from kwargs and calls application_service.execute().
It contains NO business logic, NO caching, NO planning.

RECTIFIED (P1-4): Convenience methods top_claims() and contradicted_claims()
are REMOVED. Phase 10 uses search() with explicit predicates instead.

RECTIFIED (Capability Metadata): CapabilityRegistry now self-describing
with CapabilityDescriptor objects.

RECTIFIED (KnowledgeSnapshot + ExecutionEngine): Data layer grouped into
KnowledgeSnapshot; execution logic moved to QueryExecutionEngine.
ApplicationService now takes snapshot + engine (clean orchestration).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import structlog

# Application Service + all sub-components
from smriti.api.application import ApplicationService
from smriti.api.cache.knowledge_cache import KnowledgeViewCache
from smriti.api.domain.predicates import Pagination, Predicate, Projection, SortSpec
from smriti.api.domain.requests import (
    ClaimRequest,
    ExplanationRequest,
    ExportRequest,
    SearchRequest,
    StatisticsRequest,
    TraversalRequest,
)
from smriti.api.domain.responses import KnowledgeResponse
from smriti.api.dtos.mapper import DTOMapper
from smriti.api.dtos.schema_registry import schema_registry
from smriti.api.engine.execution import QueryExecutionEngine
from smriti.api.engine.resolver import ServiceResolver
from smriti.api.index.builder import IndexBuilder
from smriti.api.index.registry import IndexRegistry
from smriti.api.index.selector import IndexSelector
from smriti.api.index.statistics import IndexStatistics
from smriti.api.planner.logical_planner import LogicalPlanner
from smriti.api.planner.normalizer import QueryNormalizer
from smriti.api.planner.optimizer import QueryOptimizer
from smriti.api.services.explain_service import ExplainabilityService
from smriti.api.services.export_service import ExportService
from smriti.api.services.navigation_service import NavigationService
from smriti.api.services.query_service import QueryService
from smriti.api.services.statistics_service import StatisticsService
from smriti.api.store.memory_store import InMemoryReadStore
from smriti.api.store.snapshot import KnowledgeSnapshot
from smriti.api.validation.request_validator import RequestValidator
from smriti.api.views.claim_view_builder import ClaimViewBuilder
from smriti.api.views.statistics_view_builder import StatisticsViewBuilder
from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    ExplainabilityLevel,
    ExportFormat,
    NavigationMode,
    Phase9Stats,
    ProjectionLevel,
    ScoredKnowledgeGraph,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.exceptions import RequestValidationError
from smriti.governance import stable

logger = structlog.get_logger(__name__)

API_VERSION = "1.0"


# ── Capability Descriptor ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class CapabilityDescriptor:
    """
    Self-describing API capability metadata.

    Fields:
        name:                 Capability identifier (e.g., "graph_traversal").
        version:              Version of this capability (semantic versioning).
        supported_requests:   List of request types that use this capability.
        required_projection:  Minimum projection level required.
        cacheable:            Whether results can be cached.
        experimental:         True if this capability is experimental/under development.
        description:          Human-readable explanation.
    """

    name: str
    version: str
    supported_requests: list[str]
    required_projection: str
    cacheable: bool
    experimental: bool
    description: str = ""


# ── Capability Registry ───────────────────────────────────────────────────────


class CapabilityRegistry:
    """
    RECTIFIED: Self-discovering capability registry with structured descriptors.
    Clients can inspect what the API supports without documentation.
    """

    def __init__(self, run_id: str, node_count: int, edge_count: int) -> None:
        self.run_id = run_id
        self.node_count = node_count
        self.edge_count = edge_count
        self.api_version = API_VERSION

        # ── Build structured capability descriptors ──
        self.capabilities: list[CapabilityDescriptor] = [
            CapabilityDescriptor(
                name="point_query",
                version="1.0",
                supported_requests=["ClaimRequest"],
                required_projection="standard",
                cacheable=True,
                experimental=False,
                description="Retrieve a single claim by its ID.",
            ),
            CapabilityDescriptor(
                name="filter_query",
                version="1.0",
                supported_requests=["SearchRequest"],
                required_projection="summary",
                cacheable=True,
                experimental=False,
                description="Search and filter claims using predicates.",
            ),
            CapabilityDescriptor(
                name="graph_traversal",
                version="1.0",
                supported_requests=["TraversalRequest"],
                required_projection="summary",
                cacheable=True,
                experimental=False,
                description="Navigate the knowledge graph from a starting claim.",
            ),
            CapabilityDescriptor(
                name="statistics_aggregation",
                version="1.0",
                supported_requests=["StatisticsRequest"],
                required_projection="standard",
                cacheable=True,
                experimental=False,
                description="Aggregate graph-wide statistics.",
            ),
            CapabilityDescriptor(
                name="explainability",
                version="1.0",
                supported_requests=["ExplanationRequest"],
                required_projection="explainability",
                cacheable=False,
                experimental=False,
                description="Retrieve full explainability records for a claim.",
            ),
            CapabilityDescriptor(
                name="export",
                version="1.0",
                supported_requests=["ExportRequest"],
                required_projection="full_audit",
                cacheable=False,
                experimental=False,
                description="Export the knowledge base in various formats.",
            ),
        ]

        # ── Backward-compatible properties ──
        self.supported_query_families = [c.name for c in self.capabilities]
        self.supported_projections = [p.value for p in ProjectionLevel]
        self.supported_export_formats = [f.value for f in ExportFormat]
        self.supported_navigation_modes = [m.value for m in NavigationMode]
        self.explainability_levels = [0, 1, 2, 3]
        self.max_traversal_depth = 5
        self.supports_search = True
        self.supports_traversal = True
        self.supports_export = True
        self.supports_explain = True
        self.supports_statistics = True

    def to_dict(self) -> dict:
        """Serialize the registry including structured capability metadata."""
        return {
            "run_id": self.run_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "api_version": self.api_version,
            "capabilities": [
                {
                    "name": c.name,
                    "version": c.version,
                    "supported_requests": c.supported_requests,
                    "required_projection": c.required_projection,
                    "cacheable": c.cacheable,
                    "experimental": c.experimental,
                    "description": c.description,
                }
                for c in self.capabilities
            ],
            # Backward-compatible flat lists (deprecated, kept for transition)
            "supported_query_families": self.supported_query_families,
            "supported_projections": self.supported_projections,
            "supported_export_formats": self.supported_export_formats,
            "supported_navigation_modes": self.supported_navigation_modes,
            "explainability_levels": self.explainability_levels,
            "max_traversal_depth": self.max_traversal_depth,
            "supports_search": self.supports_search,
            "supports_traversal": self.supports_traversal,
            "supports_export": self.supports_export,
            "supports_explain": self.supports_explain,
            "supports_statistics": self.supports_statistics,
        }


# ── KnowledgeAccessService thin façade ──────────────────────────────────────
@stable("1.0")
class KnowledgeAccessService:
    """
    Phase 9 thin public façade.

    RECTIFIED: Contains NO business logic. Delegates everything to ApplicationService.
    The façade's only job is:
        1. Build typed KnowledgeRequest from caller's kwargs
        2. Call self._app.execute(request)
        3. Return KnowledgeResponse

    Properties:
        run_id:          The Run ID of the loaded snapshot
        node_count:      Number of claims available
        api_version:     API contract version
        capabilities:    CapabilityRegistry (self-discovering clients)
    """

    def __init__(
        self,
        app: ApplicationService,
        store: InMemoryReadStore,
        capabilities: CapabilityRegistry,
        stats: Phase9Stats,
        run_id: str,
    ) -> None:
        self._app = app
        self._store = store
        self._capabilities = capabilities
        self._stats = stats
        self._run_id = run_id

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def node_count(self) -> int:
        return self._store.node_count

    @property
    def api_version(self) -> str:
        return API_VERSION

    @property
    def capabilities(self) -> CapabilityRegistry:
        return self._capabilities

    @property
    def initialization_stats(self) -> Phase9Stats:
        return self._stats

    def get_claim(
        self,
        claim_id: str,
        projection: ProjectionLevel = ProjectionLevel.STANDARD,
        explain_level: ExplainabilityLevel = ExplainabilityLevel.NONE,
    ) -> KnowledgeResponse:
        """Retrieve one claim by ID."""
        request = ClaimRequest(
            run_id=self._run_id,
            claim_id=claim_id,
            projection=Projection(level=projection),
            explainability_level=explain_level,
        )
        return self._app.execute(request)

    def search(
        self,
        request: SearchRequest | None = None,
        predicates: tuple = (),
        text_contains: str | None = None,
        sort_field: str = "reliability_index",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        projection: ProjectionLevel = ProjectionLevel.SUMMARY,
    ) -> KnowledgeResponse:
        """Filter claims matching predicates. Replaces all convenience methods."""
        from smriti.core.models import SortOrder

        if request is None:
            request = SearchRequest(
                run_id=self._run_id,
                predicates=predicates,
                text_contains=text_contains,
                sort=SortSpec(sort_field, SortOrder(sort_order)),
                pagination=Pagination(limit=limit, offset=offset),
                projection=Projection(level=projection),
            )
        return self._app.execute(request)

    def traverse(
        self,
        start_claim_id: str,
        max_depth: int = 2,
        mode: NavigationMode = NavigationMode.LOCAL,
        relationship_types: tuple = (),
        projection: ProjectionLevel = ProjectionLevel.SUMMARY,
    ) -> KnowledgeResponse:
        """Navigate the knowledge graph from a starting node."""
        request = TraversalRequest(
            run_id=self._run_id,
            start_claim_id=start_claim_id,
            max_depth=max_depth,
            navigation_mode=mode,
            relationship_types=relationship_types,
            projection=Projection(level=projection),
        )
        return self._app.execute(request)

    def explain(
        self,
        claim_id: str,
        level: ExplainabilityLevel = ExplainabilityLevel.FULL_AUDIT,
    ) -> KnowledgeResponse:
        """Return the complete explainability record for one claim."""
        request = ExplanationRequest(
            run_id=self._run_id,
            claim_id=claim_id,
            explainability_level=level,
        )
        return self._app.execute(request)

    def statistics(
        self,
        include_histogram: bool = True,
        include_partition_stats: bool = True,
    ) -> KnowledgeResponse:
        """Return graph-wide statistics."""
        request = StatisticsRequest(
            run_id=self._run_id,
            include_histogram=include_histogram,
            include_partition_stats=include_partition_stats,
        )
        return self._app.execute(request)

    def export(
        self,
        fmt: ExportFormat = ExportFormat.JSON,
        include_reliability: bool = True,
    ) -> KnowledgeResponse:
        """Export the knowledge base to a file format."""
        request = ExportRequest(
            run_id=self._run_id,
            export_format=fmt,
            include_reliability=include_reliability,
        )
        return self._app.execute(request)

    def clear_cache(self) -> None:
        """Clear the knowledge view cache."""
        self._app.clear_cache()


# ── Factory function ──────────────────────────────────────────────────────────


def build_knowledge_api(
    scored_graph: ScoredKnowledgeGraph,
    cache_size: int = 256,
) -> KnowledgeAccessService:
    """
    Build a fully initialized KnowledgeAccessService from a ScoredKnowledgeGraph.

    RECTIFIED: Wires together:
        ReadStore (primitive only)
        IndexRegistry + IndexBuilder + IndexSelector + IndexStatistics
        QueryNormalizer + LogicalPlanner + QueryOptimizer
        KnowledgeViewCache (View-level)
        ViewBuilders (separated from DTOMapper)
        DTOMapper (View → DTO only)
        RequestValidator (centralized)
        Domain Services
        ServiceResolver + QueryExecutionEngine
        KnowledgeSnapshot
        ApplicationService (orchestration)
        KnowledgeAccessService (thin façade)
    """
    t0 = time.monotonic()

    config = get_config()
    api_cfg = config.get("knowledge_api", {})

    logger.info(
        "building knowledge access service",
        run_id=scored_graph.run_id,
        nodes=scored_graph.graph.node_count,
        reliability_records=scored_graph.total_scored,
    )

    # 1. ReadStore (primitive retrieval only)
    store = InMemoryReadStore(scored_graph)

    # 2. Index Manager (RECTIFIED P0-3 + Cost-Based)
    index_builder = IndexBuilder()
    index_registry = index_builder.build(store.all_claim_records())
    index_stats = IndexStatistics().compute(index_registry)
    index_selector = IndexSelector(registry=index_registry, statistics=index_stats)

    # 3. Planning pipeline (RECTIFIED P0-2)
    normalizer = QueryNormalizer()
    logical_planner = LogicalPlanner(index_selector=index_selector)
    optimizer = QueryOptimizer(index_selector=index_selector)

    # 4. View-level cache (RECTIFIED P0-4)
    cache = KnowledgeViewCache(
        max_size=api_cfg.get("cache", {}).get("max_size", cache_size),
        run_id=scored_graph.run_id,
    )

    # 5. View builders (RECTIFIED P0-5)
    claim_view_builder = ClaimViewBuilder()
    statistics_view_builder = StatisticsViewBuilder()

    # 6. DTO mapper (View → DTO only)
    mapper = DTOMapper()

    # 7. Request validator (RECTIFIED P0-big)
    validator = RequestValidator()

    # 8. Domain services
    query_svc = QueryService(store, claim_view_builder, mapper)
    nav_svc = NavigationService(store, claim_view_builder, mapper)
    stats_svc = StatisticsService(store, statistics_view_builder)
    explain_svc = ExplainabilityService(store)
    export_svc = ExportService(store)

    # ── 9. ServiceResolver + QueryExecutionEngine (NEW) ──
    resolver = ServiceResolver()
    resolver.register(ClaimRequest, query_svc)
    resolver.register(SearchRequest, query_svc)
    resolver.register(TraversalRequest, nav_svc)
    resolver.register(StatisticsRequest, stats_svc)
    resolver.register(ExplanationRequest, explain_svc)
    resolver.register(ExportRequest, export_svc)

    engine = QueryExecutionEngine(resolver=resolver, cache=cache)

    # ── 10. KnowledgeSnapshot (NEW) ──
    snapshot = KnowledgeSnapshot(
        store=store,
        index_registry=index_registry,
        cache=cache,
        schema_registry=schema_registry,
        run_id=scored_graph.run_id,
    )

    # ── 11. ApplicationService (with snapshot + engine) ──
    app = ApplicationService(
        validator=validator,
        normalizer=normalizer,
        logical_planner=logical_planner,
        optimizer=optimizer,
        snapshot=snapshot,
        engine=engine,
    )

    # 12. Capability registry (RECTIFIED P1-1)
    capabilities = CapabilityRegistry(
        run_id=scored_graph.run_id,
        node_count=store.node_count,
        edge_count=scored_graph.graph.edge_count,
    )

    elapsed = time.monotonic() - t0

    stats = Phase9Stats(
        nodes_indexed=store.node_count,
        edges_indexed=scored_graph.graph.edge_count,
        partitions_indexed=scored_graph.graph.partition_count,
        reliability_records_loaded=scored_graph.total_scored,
        index_build_seconds=round(elapsed, 4),
        run_id=scored_graph.run_id,
        api_version=API_VERSION,
        capability_count=len(capabilities.capabilities),
    )

    api = KnowledgeAccessService(
        app=app,
        store=store,
        capabilities=capabilities,
        stats=stats,
        run_id=scored_graph.run_id,
    )

    logger.info(
        "knowledge access service ready",
        run_id=scored_graph.run_id,
        nodes=store.node_count,
        indexes=len(index_registry.indexed_fields),
        build_seconds=f"{elapsed:.3f}",
    )

    return api


def run_api_initialization(
    scored_graph: ScoredKnowledgeGraph,
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> KnowledgeAccessService:
    """Initialize Phase 9 as part of the pipeline run. Writes manifest."""
    import json

    start_time = manifest_manager.start_phase(phase=9)

    api = build_knowledge_api(scored_graph)
    stats = api.initialization_stats

    phase_dir = (
        manifest_manager.run_dir / "phase9"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)

    capabilities_path = phase_dir / "capabilities.json"
    capabilities_path.write_text(json.dumps(api.capabilities.to_dict(), indent=2), encoding="utf-8")

    manifest_manager.end_phase(
        phase=9,
        start_time=start_time,
        inputs={"scored_graph_nodes": scored_graph.graph.node_count},
        outputs={
            "nodes_indexed": stats.nodes_indexed,
            "api_version": API_VERSION,
            "capabilities_path": str(capabilities_path),
            "indexed_fields": api.capabilities.supported_query_families,
        },
        status="success",
    )
    state_manager.complete_phase(phase=9)

    logger.info("phase 9 complete", nodes=stats.nodes_indexed)
    return api


# Backward-compatible alias
KnowledgeAPI = KnowledgeAccessService
