"""
presentation.py — PresentationModel hierarchy for Phase 10.

PresentationModels are the ONLY objects that views may receive.
No view ever receives a raw dict directly from ServiceClient.

Architecture contract:
    ServiceClient → dict (DTO boundary)
        │
        ▼
    DTOTransformer.to_claim_pm()
        │
        ▼
    ClaimPresentationModel
        │
        ▼
    View (render method)
        │
        ▼
    Streamlit

Rules:
    ✅ Every view parameter is typed as a PresentationModel
    ✅ DTOTransformer handles all dict → PM conversions
    ✅ PresentationModels carry display-ready values (formatted strings, colors, icons)
    ❌ PresentationModels never call ServiceClient
    ❌ Views never receive raw dicts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ── Calibration label display helpers ─────────────────────────────────────────

LABEL_ICON = {
    "very_high": "🟢",
    "high":      "🔵",
    "moderate":  "🟡",
    "low":       "🟠",
    "very_low":  "🔴",
}

LABEL_COLOR = {
    "very_high": "#27ae60",
    "high":      "#2980b9",
    "moderate":  "#f39c12",
    "low":       "#e67e22",
    "very_low":  "#c0392b",
}


# ── Presentation Models ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SignalPresentationModel:
    """A single reliability signal ready for display."""
    key: str
    label: str
    value: float
    color: str
    formatted: str      # e.g. "0.712"


@dataclass(frozen=True)
class ComponentScorePresentationModel:
    """One component contribution ready for display."""
    signal_name: str
    display_name: str
    contribution: float
    direction: str      # "positive" | "negative"
    explanation: str
    icon: str           # "🟢" or "🔴"
    formatted_contribution: str   # "+22.00" or "−3.50"


@dataclass(frozen=True)
class ClaimPresentationModel:
    """
    A claim ready for display. All values are display-ready.
    Created by DTOTransformer from a ServiceClient dict.
    """
    claim_id: str
    text: str
    context: str
    reliability_index: float
    calibration_label: str
    uncertainty_score: float
    document_id: str
    source_path: str
    semantic_role: str
    temporal_status: str
    support_count: int
    degree: int
    centrality: float

    # Signal fields
    evidence_strength: float
    evidence_independence: float
    source_diversity: float
    topology_strength: float
    conflict_pressure: float
    temporal_stability: float

    # Display helpers (pre-computed)
    label_icon: str
    label_color: str
    label_display: str           # "Very High", "High", …
    ri_formatted: str            # "78.5"
    uncertainty_formatted: str   # "12.0"
    role_display: str            # "Foundational Claim"
    short_id: str                # First 8 chars

    # Explanation (populated at SUMMARY level+)
    explanation_summary: Optional[str] = None
    dominant_signal: Optional[str] = None
    limiting_signal: Optional[str] = None

    # Signal vector (populated at DETAILED level+)
    signals: List[SignalPresentationModel] = field(default_factory=list)
    component_scores: List[ComponentScorePresentationModel] = field(default_factory=list)


@dataclass(frozen=True)
class EvidencePresentationModel:
    """Evidence chain for a claim — used in ProvenanceWorkspace."""
    claim_id: str
    source_path: str
    document_id: str
    context: str
    support_count: int
    reachable_in_2_hops: int
    neighbor_ids: List[str]
    neighbor_texts: List[str]


@dataclass(frozen=True)
class RelationshipPresentationModel:
    """A graph edge ready for display — used in TopologyWorkspace."""
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    source_text: str
    target_text: str


@dataclass(frozen=True)
class AuditPresentationModel:
    """Full audit record for a claim — used in AuditWorkspace."""
    claim_id: str
    reliability_index: float
    calibration_label: str
    uncertainty_score: float
    explainability_level: int
    summary: str
    dominant_signal: str
    limiting_signal: str
    signals: List[SignalPresentationModel]
    component_scores: List[ComponentScorePresentationModel]
    audit_trail: Dict[str, Any]
    recommendations: List[str]
    policy_snapshot: Dict[str, Any]
    label_icon: str
    label_color: str


@dataclass(frozen=True)
class StatisticsPresentationModel:
    """Global knowledge base statistics ready for display."""
    total_claims: int
    total_edges: int
    total_partitions: int
    total_contradictions: int
    avg_reliability: float
    median_reliability: float
    avg_uncertainty: float
    calibration_distribution: Dict[str, int]
    reliability_histogram: List[tuple]
    partition_summaries: List[Dict[str, Any]]
    run_id: str


@dataclass(frozen=True)
class ContradictionPresentationModel:
    """A pair of contradicting claims for side-by-side display."""
    claim_a: ClaimPresentationModel
    claim_b: ClaimPresentationModel
    conflict_delta: float   # abs(ri_a - ri_b)


# ── DTO Transformer ───────────────────────────────────────────────────────────

SIGNAL_LABELS = {
    "evidence_strength":     "Evidence Strength",
    "evidence_independence": "Evidence Independence",
    "source_diversity":      "Source Diversity",
    "topology_strength":     "Topology Strength",
    "conflict_pressure":     "Conflict Pressure (↑ = worse)",
    "temporal_stability":    "Temporal Stability",
}

SIGNAL_COLORS = {
    "evidence_strength":     "#27ae60",
    "evidence_independence": "#2980b9",
    "source_diversity":      "#8e44ad",
    "topology_strength":     "#16a085",
    "conflict_pressure":     "#c0392b",
    "temporal_stability":    "#d35400",
}


class DTOTransformer:
    """
    Converts ServiceClient dicts (DTO boundary) into typed PresentationModels.

    This is the ONLY place where raw dicts are consumed.
    After this point, all view code works with PresentationModels.
    """

    @staticmethod
    def to_claim_pm(dto: Dict[str, Any]) -> ClaimPresentationModel:
        """Convert a claim dict from ServiceClient to ClaimPresentationModel."""
        label = dto.get("calibration_label", "very_low")
        role = dto.get("semantic_role", "")

        signals = []
        for key, sig_label in SIGNAL_LABELS.items():
            val = float(dto.get(key, 0.0) or 0.0)
            signals.append(SignalPresentationModel(
                key=key,
                label=sig_label,
                value=val,
                color=SIGNAL_COLORS.get(key, "#888"),
                formatted=f"{val:.3f}",
            ))

        comp_scores = []
        for comp in (dto.get("component_scores") or []):
            direction = comp.get("direction", "positive")
            contrib = float(comp.get("contribution", 0.0))
            comp_scores.append(ComponentScorePresentationModel(
                signal_name=comp.get("signal_name", ""),
                display_name=comp.get("signal_name", "").replace("_", " ").title(),
                contribution=contrib,
                direction=direction,
                explanation=comp.get("explanation", ""),
                icon="🟢" if direction == "positive" else "🔴",
                formatted_contribution=f"+{contrib:.2f}" if contrib >= 0 else f"−{abs(contrib):.2f}",
            ))

        ri = float(dto.get("reliability_index", 0.0) or 0.0)
        unc = float(dto.get("uncertainty_score", 100.0) or 100.0)

        return ClaimPresentationModel(
            claim_id=dto.get("claim_id", ""),
            text=dto.get("claim_text", ""),
            context=dto.get("context", ""),
            reliability_index=ri,
            calibration_label=label,
            uncertainty_score=unc,
            document_id=dto.get("document_id", ""),
            source_path=dto.get("source_path", ""),
            semantic_role=role,
            temporal_status=dto.get("temporal_status", ""),
            support_count=int(dto.get("support_count", 0) or 0),
            degree=int(dto.get("degree", 0) or 0),
            centrality=float(dto.get("centrality", 0.0) or 0.0),
            evidence_strength=float(dto.get("evidence_strength", 0.0) or 0.0),
            evidence_independence=float(dto.get("evidence_independence", 0.0) or 0.0),
            source_diversity=float(dto.get("source_diversity", 0.0) or 0.0),
            topology_strength=float(dto.get("topology_strength", 0.0) or 0.0),
            conflict_pressure=float(dto.get("conflict_pressure", 0.0) or 0.0),
            temporal_stability=float(dto.get("temporal_stability", 0.0) or 0.0),
            label_icon=LABEL_ICON.get(label, "⚪"),
            label_color=LABEL_COLOR.get(label, "#95a5a6"),
            label_display=label.replace("_", " ").title(),
            ri_formatted=f"{ri:.1f}",
            uncertainty_formatted=f"{unc:.1f}",
            role_display=role.replace("_", " ").title(),
            short_id=dto.get("claim_id", "")[:8],
            explanation_summary=dto.get("explanation_summary"),
            dominant_signal=dto.get("dominant_signal"),
            limiting_signal=dto.get("limiting_signal"),
            signals=signals,
            component_scores=comp_scores,
        )

    @staticmethod
    def to_audit_pm(dto: Dict[str, Any]) -> AuditPresentationModel:
        """Convert an explanation dict to AuditPresentationModel."""
        label = dto.get("calibration_label", "very_low")
        ri = float(dto.get("reliability_index", 0.0) or 0.0)
        unc = float(dto.get("uncertainty_score", 100.0) or 100.0)

        signals = []
        sv = dto.get("signal_vector") or {}
        for key, sig_label in SIGNAL_LABELS.items():
            val = float(sv.get(key, 0.0) or 0.0)
            signals.append(SignalPresentationModel(
                key=key, label=sig_label, value=val,
                color=SIGNAL_COLORS.get(key, "#888"),
                formatted=f"{val:.3f}",
            ))

        comp_scores = []
        for comp in (dto.get("component_scores") or []):
            direction = comp.get("direction", "positive")
            contrib = float(comp.get("contribution", 0.0))
            comp_scores.append(ComponentScorePresentationModel(
                signal_name=comp.get("signal_name", ""),
                display_name=comp.get("signal_name", "").replace("_", " ").title(),
                contribution=contrib,
                direction=direction,
                explanation=comp.get("explanation", ""),
                icon="🟢" if direction == "positive" else "🔴",
                formatted_contribution=f"+{contrib:.2f}" if contrib >= 0 else f"−{abs(contrib):.2f}",
            ))

        return AuditPresentationModel(
            claim_id=dto.get("claim_id", ""),
            reliability_index=ri,
            calibration_label=label,
            uncertainty_score=unc,
            explainability_level=int(dto.get("explainability_level", 0)),
            summary=dto.get("summary", ""),
            dominant_signal=dto.get("dominant_signal", ""),
            limiting_signal=dto.get("limiting_signal", ""),
            signals=signals,
            component_scores=comp_scores,
            audit_trail=dto.get("audit", {}),
            recommendations=dto.get("recommendations", []),
            policy_snapshot=dto.get("policy_snapshot", {}),
            label_icon=LABEL_ICON.get(label, "⚪"),
            label_color=LABEL_COLOR.get(label, "#95a5a6"),
        )

    @staticmethod
    def to_statistics_pm(dto: Dict[str, Any]) -> StatisticsPresentationModel:
        """Convert a statistics dict to StatisticsPresentationModel."""
        return StatisticsPresentationModel(
            total_claims=int(dto.get("total_claims", 0)),
            total_edges=int(dto.get("total_edges", 0)),
            total_partitions=int(dto.get("total_partitions", 0)),
            total_contradictions=int(dto.get("total_contradictions", 0)),
            avg_reliability=float(dto.get("avg_reliability", 0.0)),
            median_reliability=float(dto.get("median_reliability", 0.0)),
            avg_uncertainty=float(dto.get("avg_uncertainty", 0.0)),
            calibration_distribution=dto.get("calibration_distribution", {}),
            reliability_histogram=dto.get("reliability_histogram", []),
            partition_summaries=dto.get("partition_summaries", []),
            run_id=dto.get("run_id", ""),
        )

    @staticmethod
    def to_claims_list(dtos: list) -> List[ClaimPresentationModel]:
        """Batch-convert a list of claim dicts. Returns empty list if input is None."""
        if dtos is None:
            return []
        return [DTOTransformer.to_claim_pm(d) for d in dtos if d]