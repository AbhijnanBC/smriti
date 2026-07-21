"""requests.py — Domain request objects for Phase 9."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from smriti.core.models import (
    NavigationMode, ExportFormat, ExplainabilityLevel, RelationshipType,
)
from smriti.api.domain.predicates import Predicate, SortSpec, Pagination, Projection
from smriti.core.config import get_config


@dataclass(frozen=True)
class ExecutionBudget:
    """
    Hard constraints for query execution to prevent resource exhaustion.

    Injected into ExecutionContext so services can check limits without
    hardcoded constants.
    """
    max_traversal_depth: int
    max_returned_rows: int
    timeout_ms: float
    max_export_size_mb: float

    @classmethod
    def from_config(cls) -> ExecutionBudget:
        """
        Load execution budget from config/default.yaml.
        """
        config = get_config()
        api_cfg = config.get("knowledge_api", {})
        budget_cfg = api_cfg.get("execution_budget", {})

        return cls(
            max_traversal_depth=budget_cfg.get("max_traversal_depth", 5),
            max_returned_rows=budget_cfg.get("max_returned_rows", 10_000),
            timeout_ms=budget_cfg.get("timeout_ms", 30_000.0),
            max_export_size_mb=budget_cfg.get("max_export_size_mb", 100.0),
        )


@dataclass(frozen=True)
class KnowledgeRequest:
    """Abstract base for all knowledge requests."""
    run_id: str
    projection: Projection = field(default_factory=Projection)
    explainability_level: ExplainabilityLevel = ExplainabilityLevel.NONE


@dataclass(frozen=True)
class ClaimRequest(KnowledgeRequest):
    """Retrieve a single claim by ID."""
    claim_id: str = ""


@dataclass(frozen=True)
class SearchRequest(KnowledgeRequest):
    """
    Retrieve claims matching a set of predicates.

    RECTIFIED (P1-4): Replaces top_claims() and contradicted_claims() convenience methods.
    Everything goes through search with explicit predicates.
    """
    predicates: tuple = field(default_factory=tuple)   # Tuple[Predicate, ...]
    sort: SortSpec = field(default_factory=lambda: SortSpec("reliability_index"))
    pagination: Pagination = field(default_factory=Pagination)
    text_contains: Optional[str] = None


@dataclass(frozen=True)
class TraversalRequest(KnowledgeRequest):
    """Navigate the knowledge graph from a starting node."""
    start_claim_id: str = ""
    max_depth: int = 2
    relationship_types: tuple = field(default_factory=tuple)
    navigation_mode: NavigationMode = NavigationMode.LOCAL
    target_claim_id: Optional[str] = None


@dataclass(frozen=True)
class StatisticsRequest(KnowledgeRequest):
    """Request aggregated statistics about the knowledge graph."""
    include_histogram: bool = True
    include_partition_stats: bool = True
    include_signal_distribution: bool = False


@dataclass(frozen=True)
class ExplanationRequest(KnowledgeRequest):
    """Request the complete explainability record for one claim."""
    claim_id: str = ""
    explainability_level: ExplainabilityLevel = ExplainabilityLevel.FULL_AUDIT


@dataclass(frozen=True)
class ExportRequest(KnowledgeRequest):
    """Export the full scored knowledge graph to a file format."""
    export_format: ExportFormat = ExportFormat.JSON
    include_reliability: bool = True
    include_graph_structure: bool = True
    predicates: tuple = field(default_factory=tuple)