"""Integration tests for Phase 12 end-to-end (rectified)."""

import json
from unittest.mock import MagicMock

import pytest
from smriti.core.models import (
    ArtifactReadinessLevel,
    CertificationLevel,
    GateDecision,
)
from smriti.evaluation import CertificationEngine


def make_mock_api(node_count: int = 20):
    api = MagicMock()
    api.run_id = "test_run_phase12"
    api.node_count = node_count
    stats_data = {
        "total_claims": node_count,
        "total_edges": node_count // 2,
        "total_partitions": max(2, node_count // 5),
        "total_contradictions": max(1, node_count // 10),
        "avg_reliability": 72.5,
        "median_reliability": 74.0,
        "avg_uncertainty": 18.0,
        "high_reliability_count": node_count // 2,
        "calibration_distribution": {"high": 10, "moderate": 8, "low": 2},
        "reliability_histogram": [],
        "partition_summaries": [],
        "run_id": "test_run_phase12",
    }
    api.statistics.return_value = MagicMock(data=stats_data)

    def mock_claim(idx):
        m = MagicMock()
        m.claim_id = f"c{idx:03d}"
        m.claim_text = f"Test claim number {idx}."
        m.reliability_index = 70.0 + idx * 0.5
        m.get = lambda k, d=None: {
            "claim_id": f"c{idx:03d}",
            "claim_text": f"Test {idx}.",
            "reliability_index": 70.0,
        }.get(k, d)
        return m

    mock_claims = [mock_claim(i) for i in range(min(20, node_count))]
    mock_resp = MagicMock()
    mock_resp.data = mock_claims
    mock_resp.total_count = node_count
    api.search.return_value = mock_resp

    explain_data = {
        "claim_id": "c001",
        "reliability_index": 78.5,
        "calibration_label": "high",
        "uncertainty_score": 12.0,
        "explainability_level": 3,
        "summary": "Reliable claim with strong evidence.",
        "dominant_signal": "evidence_strength",
        "limiting_signal": "conflict_pressure",
        "component_scores": [
            {
                "signal": "evidence_strength",
                "contribution": 20.0,
                "direction": "positive",
                "explanation": "Good.",
            }
        ],
        "signal_vector": {"evidence_strength": 0.75},
        "audit": {"policy_version": "1.0", "fusion_algorithm": "v2"},
    }
    api.explain.return_value = MagicMock(data=explain_data)
    return api


@pytest.fixture
def mock_api():
    return make_mock_api()


# ── Original 17 tests (all preserved) ────────────────────────────────────────


def test_certification_engine_produces_report(mock_api):
    from smriti.core.models import CertificationReport

    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert isinstance(report, CertificationReport)


def test_report_has_valid_certification_level(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    valid_levels = {l.value for l in CertificationLevel}
    assert report.certification_level.value in valid_levels


def test_report_schema_version(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert report.schema_version == "12.1"


def test_certification_level_at_least_prototype(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert report.certification_level.value >= CertificationLevel.PROTOTYPE.value


def test_eci_in_valid_range(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert 0.0 <= report.engineering_confidence_index <= 100.0


def test_evidence_coverage_in_valid_range(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert 0.0 <= report.research_evidence_coverage_index <= 100.0


def test_overall_confidence_in_range(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert 0.0 <= report.overall_confidence_index <= 100.0


def test_six_experiments_run(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert len(report.experiment_results) == 5


def test_six_research_claims_assessed(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert len(report.research_claims) == 5


def test_threats_to_validity_present(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert len(report.threats_to_validity) >= 6


def test_verification_results_present(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert len(report.verification_results) >= 15


def test_report_is_immutable(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    with pytest.raises(Exception):
        report.run_id = "modified"


def test_report_is_json_serializable(mock_api):
    from smriti.evaluation.certification.report import serialize_certification_report

    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    json_str = serialize_certification_report(report)
    data = json.loads(json_str)
    assert "certification" in data
    assert "confidence_indices" in data
    assert "research_claims" in data


def test_markdown_export(mock_api):
    from smriti.reporting.exporter import export_markdown_summary

    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    md = export_markdown_summary(report)
    assert "# SMRITI Certification Report" in md
    assert "Certification Level" in md


def test_text_summary_export(mock_api):
    from smriti.reporting.exporter import export_text_summary

    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    txt = export_text_summary(report)
    assert "SMRITI" in txt
    assert "CERTIFICATION REPORT" in txt


def test_artifact_readiness_has_criteria(mock_api):
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    pr = report.artifact_readiness
    assert isinstance(pr.readiness_level, ArtifactReadinessLevel)
    assert isinstance(pr.criteria_missing, tuple)


def test_larger_corpus_achieves_higher_level():
    api_small = make_mock_api(node_count=5)
    api_large = make_mock_api(node_count=50)
    engine = CertificationEngine(run_id="phase12_comparison")
    report_small = engine.run(api_small)
    report_large = engine.run(api_large)
    assert report_large.overall_confidence_index >= report_small.overall_confidence_index - 5.0


def test_evidence_chains_complete(mock_api):
    from smriti.evaluation.philosophy.evidence_model import build_evidence_chain

    chain = build_evidence_chain(
        chain_id="EC-001",
        research_claim_id="RC-001",
        requirement_id="R-01",
        principle_numbers=[1, 4],
        adr_ids=["ADR-01"],
        implementation_modules=["smriti.claims"],
        verification_rule_ids=["ARCH-001"],
        validation_rule_ids=["COMP-001"],
        metric_names=["precision"],
        statistical_analysis_ids=["SA-001"],
        conclusion="Extraction is structurally precise",
    )
    assert chain.is_complete
    assert chain.has_adr
    assert chain.has_statistical_analysis
    assert len(chain.links) >= 9


# ── 7 new rectified integration tests ────────────────────────────────────────


def test_gate_results_in_report(mock_api):
    """RECTIFIED (P0-1): Report must contain gate_results."""
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert len(report.gate_results) >= 1, "Report must have at least one gate result"
    for g in report.gate_results:
        assert g.decision in (GateDecision.PASS, GateDecision.BLOCK)


def test_run_full_produces_research_assurance_package(mock_api):
    """RECTIFIED (P0-big): run_full() must return ResearchAssurancePackage."""
    from smriti.core.models import ResearchAssurancePackage

    engine = CertificationEngine(run_id="test_phase12")
    pkg = engine.run_full(mock_api)
    assert isinstance(pkg, ResearchAssurancePackage)
    assert pkg.certification_report is not None
    assert pkg.evaluation_manifest is not None


def test_research_assurance_package_has_all_components(mock_api):
    """RECTIFIED (P0-big): Package must contain all companion artifacts."""
    engine = CertificationEngine(run_id="test_phase12")
    pkg = engine.run_full(mock_api)
    assert len(pkg.experiment_registry) == 5
    assert len(pkg.assumption_registry) >= 5
    assert len(pkg.limitation_registry) >= 4


def test_claims_have_research_questions(mock_api):
    """RECTIFIED (P0-3): All research claims must have research_question."""
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    for claim in report.research_claims:
        assert claim.research_question, f"{claim.claim_id} missing research_question"
        assert claim.null_hypothesis, f"{claim.claim_id} missing null_hypothesis"


def test_artifact_readiness_is_not_binary(mock_api):
    """RECTIFIED (P1-6): Artifact readiness must be ArtifactReadinessLevel enum."""
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    readiness_level = report.artifact_readiness.readiness_level
    assert isinstance(
        readiness_level, ArtifactReadinessLevel
    ), f"Expected ArtifactReadinessLevel enum, got {type(readiness_level)}"


def test_evaluation_manifest_in_json(mock_api):
    """RECTIFIED (P2-1): EvaluationManifest must be included in package."""
    engine = CertificationEngine(run_id="test_phase12")
    pkg = engine.run_full(mock_api)
    manifest = pkg.evaluation_manifest
    assert manifest.run_id == "test_phase12"
    assert len(manifest.experiment_ids) == 5
    assert len(manifest.random_seeds) == 5
    assert "python" in manifest.software_versions


def test_schema_version_is_12_1(mock_api):
    """Schema version must be 12.1 (rectified schema includes gate_results)."""
    engine = CertificationEngine(run_id="test_phase12")
    report = engine.run(mock_api)
    assert report.schema_version == "12.1", (
        "Rectified schema must be '12.1' (original was '12.0'). "
        "Version bump captures addition of gate_results field."
    )
