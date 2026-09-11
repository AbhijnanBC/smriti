"""Unit tests for dashboard/models/presentation.py."""

from smriti.dashboard.models.presentation import (
    AuditPresentationModel,
    ClaimPresentationModel,
    DTOTransformer,
    StatisticsPresentationModel,
)

SAMPLE_CLAIM_DTO = {
    "claim_id": "c001",
    "claim_text": "Python supports generators.",
    "reliability_index": 78.5,
    "calibration_label": "high",
    "uncertainty_score": 12.0,
    "support_count": 3,
    "degree": 5,
    "centrality": 0.65,
    "context": "Python > Generators",
    "document_id": "d001",
    "source_path": "note.md",
    "semantic_role": "foundational_claim",
    "temporal_status": "static_partition",
    "evidence_strength": 0.70,
    "evidence_independence": 0.60,
    "source_diversity": 0.55,
    "topology_strength": 0.80,
    "conflict_pressure": 0.20,
    "temporal_stability": 0.90,
    "component_scores": [
        {
            "signal_name": "evidence_strength",
            "contribution": 22.0,
            "direction": "positive",
            "explanation": "Good support.",
        }
    ],
}

SAMPLE_STATS_DTO = {
    "total_claims": 100,
    "total_edges": 250,
    "total_partitions": 5,
    "total_contradictions": 3,
    "avg_reliability": 72.3,
    "median_reliability": 75.0,
    "avg_uncertainty": 18.5,
    "calibration_distribution": {"high": 40, "moderate": 40, "low": 20},
    "reliability_histogram": [("0-10", 0), ("10-20", 5)],
    "partition_summaries": [],
    "run_id": "test_run",
}


def test_to_claim_pm_produces_correct_type():
    pm = DTOTransformer.to_claim_pm(SAMPLE_CLAIM_DTO)
    assert isinstance(pm, ClaimPresentationModel)


def test_to_claim_pm_populates_identity_fields():
    pm = DTOTransformer.to_claim_pm(SAMPLE_CLAIM_DTO)
    assert pm.claim_id == "c001"
    assert pm.text == "Python supports generators."
    assert pm.reliability_index == 78.5
    assert pm.calibration_label == "high"


def test_to_claim_pm_populates_display_helpers():
    pm = DTOTransformer.to_claim_pm(SAMPLE_CLAIM_DTO)
    assert pm.label_icon == "🔵"  # high → blue
    assert pm.label_display == "High"
    assert pm.ri_formatted == "78.5"
    assert pm.role_display == "Foundational Claim"


def test_to_claim_pm_builds_signals():
    pm = DTOTransformer.to_claim_pm(SAMPLE_CLAIM_DTO)
    assert len(pm.signals) == 6  # All 6 signal keys
    signal_keys = {s.key for s in pm.signals}
    assert "evidence_strength" in signal_keys
    assert "conflict_pressure" in signal_keys


def test_to_claim_pm_builds_component_scores():
    pm = DTOTransformer.to_claim_pm(SAMPLE_CLAIM_DTO)
    assert len(pm.component_scores) == 1
    comp = pm.component_scores[0]
    assert comp.signal_name == "evidence_strength"
    assert comp.icon == "🟢"
    assert comp.formatted_contribution == "+22.00"


def test_to_claim_pm_handles_missing_fields_gracefully():
    """DTOTransformer must not raise on partial DTOs."""
    minimal_dto = {"claim_id": "c999", "claim_text": "Minimal."}
    pm = DTOTransformer.to_claim_pm(minimal_dto)
    assert pm.claim_id == "c999"
    assert pm.reliability_index == 0.0
    assert pm.support_count == 0


def test_to_claims_list_batch_converts():
    pms = DTOTransformer.to_claims_list([SAMPLE_CLAIM_DTO, SAMPLE_CLAIM_DTO])
    assert len(pms) == 2
    assert all(isinstance(p, ClaimPresentationModel) for p in pms)


def test_to_statistics_pm_produces_correct_type():
    pm = DTOTransformer.to_statistics_pm(SAMPLE_STATS_DTO)
    assert isinstance(pm, StatisticsPresentationModel)
    assert pm.total_claims == 100
    assert pm.avg_reliability == 72.3


def test_to_audit_pm_populates_audit_trail():
    audit_dto = {
        **SAMPLE_CLAIM_DTO,
        "explainability_level": 3,
        "summary": "Good claim.",
        "dominant_signal": "evidence_strength",
        "limiting_signal": "conflict_pressure",
        "signal_vector": {"evidence_strength": 0.70},
        "component_scores": SAMPLE_CLAIM_DTO["component_scores"],
        "audit": {"policy_version": "1.0"},
        "recommendations": ["Gather more sources."],
        "policy_snapshot": {"fusion": "weighted_linear"},
    }
    pm = DTOTransformer.to_audit_pm(audit_dto)
    assert isinstance(pm, AuditPresentationModel)
    assert pm.summary == "Good claim."
    assert len(pm.recommendations) == 1
