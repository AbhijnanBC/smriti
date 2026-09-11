"""claim_dto.py — ClaimDTO: the external serialization contract for claims."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ComponentScoreDTO:
    signal_name: str
    contribution: float
    direction: str
    explanation: str


@dataclass(frozen=True)
class ClaimDTO:
    """External representation of one scored claim. Schema version: 9.0."""

    # ── Core fields – all have defaults so projection policies can omit them ──
    claim_id: str = ""
    claim_text: str = ""
    context: str = ""  # RECTIFIED: default added
    reliability_index: float = 0.0
    calibration_label: str = "very_low"
    uncertainty_score: float = 100.0

    # STANDARD+
    document_id: str | None = None
    source_path: str | None = None
    partition_id: str | None = None
    semantic_role: str | None = None
    degree: int | None = None
    centrality: float | None = None
    support_count: int | None = None

    # DETAILED+
    temporal_status: str | None = None
    evidence_strength: float | None = None
    conflict_pressure: float | None = None
    evidence_completeness: float | None = None

    # EXPLAINABILITY+
    explanation_summary: str | None = None
    dominant_signal: str | None = None
    limiting_signal: str | None = None
    component_scores: list[ComponentScoreDTO] | None = None
    recommendations: list[str] | None = None

    # FULL_AUDIT
    policy_version: str | None = None
    audit_run_id: str | None = None
    schema_version: str = "9.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
