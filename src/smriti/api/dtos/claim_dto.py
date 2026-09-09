"""claim_dto.py — ClaimDTO: the external serialization contract for claims."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


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
    context: str = ""                     # RECTIFIED: default added
    reliability_index: float = 0.0
    calibration_label: str = "very_low"
    uncertainty_score: float = 100.0

    # STANDARD+
    document_id: Optional[str] = None
    source_path: Optional[str] = None
    partition_id: Optional[str] = None
    semantic_role: Optional[str] = None
    degree: Optional[int] = None
    centrality: Optional[float] = None
    support_count: Optional[int] = None

    # DETAILED+
    temporal_status: Optional[str] = None
    evidence_strength: Optional[float] = None
    conflict_pressure: Optional[float] = None
    evidence_completeness: Optional[float] = None

    # EXPLAINABILITY+
    explanation_summary: Optional[str] = None
    dominant_signal: Optional[str] = None
    limiting_signal: Optional[str] = None
    component_scores: Optional[List[ComponentScoreDTO]] = None
    recommendations: Optional[List[str]] = None

    # FULL_AUDIT
    policy_version: Optional[str] = None
    audit_run_id: Optional[str] = None
    schema_version: str = "9.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)