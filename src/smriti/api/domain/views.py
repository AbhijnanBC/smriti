"""
views.py — KnowledgeView domain objects for Phase 9.

RECTIFIED (P0-5): Views are now constructed ONLY by ViewBuilders.
DTOMapper never constructs views — it only maps View → DTO.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClaimView:
    """Internal view of one scored claim. All possible fields are populated by ClaimViewBuilder."""

    claim_id: str
    claim_text: str
    context: str
    document_id: str
    source_path: str
    partition_id: str | None
    semantic_role: str

    reliability_index: float
    uncertainty_score: float
    evidence_completeness: float
    calibration_label: str
    policy_version: str

    degree: int = 0
    in_degree: int = 0
    centrality: float = 0.0
    is_hub: bool = False
    is_bridge: bool = False

    support_count: int = 0
    weighted_confidence: float = 0.0

    temporal_status: str = "unknown"
    temporal_confidence: float = 0.0
    time_delta_days: float | None = None

    evidence_strength: float = 0.0
    evidence_independence: float = 0.0
    source_diversity: float = 0.0
    topology_strength: float = 0.0
    conflict_pressure: float = 0.0
    temporal_stability: float = 0.0

    component_scores: tuple = field(default_factory=tuple)
    explanation_summary: str = ""
    explanation_dominant_signal: str = ""
    explanation_limiting_signal: str = ""
    explanation_strengths: tuple = field(default_factory=tuple)
    explanation_weaknesses: tuple = field(default_factory=tuple)
    explanation_recommendations: tuple = field(default_factory=tuple)

    audit_policy_version: str = ""
    audit_fusion_algorithm: str = ""
    audit_run_id: str = ""


@dataclass(frozen=True)
class EdgeView:
    """Internal view of one relationship edge."""

    edge_id: str
    source_claim_id: str
    target_claim_id: str
    relationship_type: str
    direction: str
    calibrated_confidence: float
    cosine_similarity: float
    candidate_rank: int


@dataclass(frozen=True)
class GraphView:
    """Internal view of a graph traversal result."""

    start_claim_id: str
    nodes: list[ClaimView]
    edges: list[EdgeView]
    depth_reached: int
    navigation_mode: str
    relationship_types_traversed: list[str]


@dataclass(frozen=True)
class ExplanationView:
    """Internal view of a complete explainability record."""

    claim_id: str
    reliability_index: float
    uncertainty_score: float
    calibration_label: str
    explainability_level: int
    summary: str = ""
    component_scores: tuple = field(default_factory=tuple)
    signal_vector: dict = field(default_factory=dict)
    signal_statuses: dict = field(default_factory=dict)
    recommendations: tuple = field(default_factory=tuple)
    policy_version: str = ""
    policy_snapshot: dict = field(default_factory=dict)
    audit_fusion_algorithm: str = ""
    audit_normalization_version: str = ""
    signal_extractor_versions: dict = field(default_factory=dict)
    run_id: str = ""


@dataclass(frozen=True)
class StatisticsView:
    """Internal view of graph-wide statistics."""

    run_id: str
    total_claims: int
    total_edges: int
    total_partitions: int
    total_contradictions: int
    avg_reliability: float
    median_reliability: float
    high_reliability_count: int
    low_reliability_count: int
    avg_uncertainty: float
    calibration_distribution: dict[str, int]
    reliability_histogram: list[tuple[str, int]]
    partition_summaries: list[dict[str, Any]]


@dataclass(frozen=True)
class ProvenanceView:
    """Internal view of the provenance chain for one claim."""

    claim_id: str
    claim_text: str
    source_path: str
    document_id: str
    sentence_context: str
    sentence_position: int
    run_id: str
    supporting_claim_ids: list[str]
    supporting_documents: list[str]
