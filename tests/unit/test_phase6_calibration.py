"""Unit tests for classification/calibration.py."""

from smriti.core.models import (
    CandidatePair,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    RelationshipEvidence,
)
from smriti.retrieval.classification.calibration import (
    CalibrationStrategy,
    ConfidenceCalibrator,
)


def make_evidence(entailment=0.1, neutral=0.05, contradiction=0.85, cosine=0.80):
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=cosine, candidate_rank=1
    )
    nli_scores = NLIScores(
        entailment_score=entailment,
        neutral_score=neutral,
        contradiction_score=contradiction,
        predicted_label="contradiction",
        raw_confidence=max(entailment, neutral, contradiction),
    )
    metadata = InferenceMetadata(model_name="test-nli")
    return RelationshipEvidence(
        pair=pair,
        cosine_similarity=cosine,
        nli_scores=nli_scores,
        calibrated_confidence=nli_scores.raw_confidence,
        inference_metadata=metadata,
        lifecycle_stage=LifecycleStage.EVIDENCE,
    )


def test_identity_calibration_preserves_confidence():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidence = make_evidence(contradiction=0.85)
    result = calibrator.calibrate(evidence)
    assert abs(result.calibrated_confidence - 0.85) < 1e-6


def test_temperature_calibration_softens_high_confidence():
    calibrator = ConfidenceCalibrator(
        model_name="test",
        strategy=CalibrationStrategy.TEMPERATURE,
        temperature=2.0,  # Higher temperature → softer distribution
    )
    evidence = make_evidence(contradiction=0.95, entailment=0.03, neutral=0.02)
    result = calibrator.calibrate(evidence)
    # Temperature > 1 should reduce the max confidence
    assert result.calibrated_confidence < evidence.nli_scores.raw_confidence


def test_calibration_advances_lifecycle_to_calibrated():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidence = make_evidence()
    result = calibrator.calibrate(evidence)
    assert result.lifecycle_stage == LifecycleStage.CALIBRATED_EVIDENCE


def test_nli_scores_unchanged_after_calibration():
    calibrator = ConfidenceCalibrator(
        model_name="test",
        strategy=CalibrationStrategy.TEMPERATURE,
        temperature=2.0,
    )
    evidence = make_evidence(contradiction=0.90)
    result = calibrator.calibrate(evidence)
    assert result.nli_scores.contradiction_score == 0.90  # Raw scores untouched
    assert result.nli_scores.predicted_label == "contradiction"


def test_calibrate_batch_processes_all():
    calibrator = ConfidenceCalibrator(model_name="test", strategy=CalibrationStrategy.IDENTITY)
    evidences = [make_evidence() for _ in range(5)]
    results = calibrator.calibrate_batch(evidences)
    assert len(results) == 5
