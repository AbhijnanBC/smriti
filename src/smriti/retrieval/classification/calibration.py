"""
calibration.py — Confidence calibration for NLI evidence scores.

Problem being solved:
    Different NLI models have different confidence distributions.
    A raw score of 0.85 from model A may not mean the same thing
    as 0.85 from model B. For example, some models tend to produce
    scores clustered near 0.9–1.0 even for ambiguous pairs (overconfident),
    while others cluster near 0.5–0.7 (underconfident).

    Without calibration, the thresholds in ResolverPolicy become
    model-specific constants that must be manually tuned whenever
    the NLI model is changed.

Solution:
    ConfidenceCalibrator applies a model-specific transformation to
    raw confidence scores to produce calibrated_confidence values
    that are comparable across models.

Currently implemented strategies:
    IDENTITY:          No calibration (raw score passes through). Default.
    TEMPERATURE:       Divide logits by temperature T before softmax.
                       Effective when the model produces overconfident scores.
    PERCENTILE:        Map raw score to its percentile in a reference distribution.
                       Requires a reference distribution (fit on a validation set).
    ISOTONIC:          Isotonic regression calibration.
                       Requires a fitted sklearn IsotonicRegression (optional dep).

Rules:
    ✅ Pure math — never calls any ML model
    ✅ Deterministic given same parameters
    ✅ Gracefully degrades to IDENTITY if calibration data unavailable
    ❌ Never modifies NLIScores objects
    ❌ Never changes predicted_label (only calibrates confidence magnitude)
"""

from __future__ import annotations

import math
from enum import Enum
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import RelationshipEvidence, NLIScores, LifecycleStage
from smriti.core.paths import CONFIG_DIR
from smriti.exceptions import CalibrationError

logger = structlog.get_logger(__name__)

CALIBRATOR_VERSION = "1.0"


class CalibrationStrategy(str, Enum):
    IDENTITY    = "identity"
    TEMPERATURE = "temperature"
    PERCENTILE  = "percentile"
    ISOTONIC    = "isotonic"


class ConfidenceCalibrator:
    """
    Applies model-specific confidence calibration to NLI evidence.

    Instantiate once per pipeline run (per model).
    """

    def __init__(
        self,
        model_name: str,
        strategy: Optional[CalibrationStrategy] = None,
        temperature: float = 1.0,
        reference_distribution: Optional[List[float]] = None,
    ) -> None:
        """
        Args:
            model_name:              NLI model being calibrated (for logging).
            strategy:                Which calibration strategy to apply.
                                     Defaults to config or IDENTITY.
            temperature:             Temperature for TEMPERATURE strategy (T > 1 softens,
                                     T < 1 sharpens). Only used when strategy=TEMPERATURE.
            reference_distribution:  Sorted list of raw confidence scores from a
                                     representative sample (for PERCENTILE strategy).
        """
        config = get_config()
        calib_cfg = config.get("calibration", {}).get(model_name, {})

        if strategy is None:
            strategy_str = calib_cfg.get("strategy", "identity")
            strategy = CalibrationStrategy(strategy_str)

        self._model_name = model_name
        self._strategy = strategy
        self._temperature = calib_cfg.get("temperature", temperature)
        self._reference_distribution = (
            reference_distribution
            or calib_cfg.get("reference_distribution")
        )

        logger.info(
            "calibrator initialized",
            model=model_name,
            strategy=self._strategy.value,
            temperature=self._temperature,
        )

    def calibrate(self, evidence: RelationshipEvidence) -> RelationshipEvidence:
        """
        Calibrate the confidence score in a RelationshipEvidence.

        Args:
            evidence: Evidence with raw NLI scores.

        Returns:
            New RelationshipEvidence with calibrated_confidence updated.
            NLIScores (predicted_label, raw scores) are never modified.
        """
        raw = evidence.nli_scores.raw_confidence

        try:
            calibrated = self._apply_strategy(
                raw_confidence=raw,
                entailment=evidence.nli_scores.entailment_score,
                neutral=evidence.nli_scores.neutral_score,
                contradiction=evidence.nli_scores.contradiction_score,
            )
        except CalibrationError as e:
            logger.warning(
                "calibration failed, using raw confidence",
                model=self._model_name,
                error=str(e),
            )
            calibrated = raw

        # Return new RelationshipEvidence with calibrated_confidence set
        # and lifecycle advanced to CALIBRATED_EVIDENCE
        return RelationshipEvidence(
            pair=evidence.pair,
            cosine_similarity=evidence.cosine_similarity,
            nli_scores=evidence.nli_scores,
            calibrated_confidence=calibrated,
            inference_metadata=evidence.inference_metadata,
            lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
        )

    def calibrate_batch(
        self,
        evidence_list: List[RelationshipEvidence],
    ) -> List[RelationshipEvidence]:
        """Calibrate a batch of evidence objects."""
        return [self.calibrate(ev) for ev in evidence_list]

    def _apply_strategy(
        self,
        raw_confidence: float,
        entailment: float,
        neutral: float,
        contradiction: float,
    ) -> float:
        """Apply the configured calibration strategy."""
        if self._strategy == CalibrationStrategy.IDENTITY:
            return raw_confidence

        elif self._strategy == CalibrationStrategy.TEMPERATURE:
            return self._temperature_scale(
                entailment, neutral, contradiction, self._temperature
            )

        elif self._strategy == CalibrationStrategy.PERCENTILE:
            if not self._reference_distribution:
                logger.warning(
                    "PERCENTILE calibration requested but no reference distribution; "
                    "falling back to IDENTITY",
                    model=self._model_name,
                )
                return raw_confidence
            return self._percentile_calibrate(raw_confidence, self._reference_distribution)

        elif self._strategy == CalibrationStrategy.ISOTONIC:
            return self._isotonic_calibrate(raw_confidence)

        else:
            return raw_confidence

    @staticmethod
    def _temperature_scale(
        entailment: float,
        neutral: float,
        contradiction: float,
        temperature: float,
    ) -> float:
        """
        Apply temperature scaling.
        Re-compute softmax after dividing by T.
        T > 1 produces softer (lower) confidence.
        T < 1 produces sharper (higher) confidence.
        """
        if temperature <= 0:
            raise CalibrationError(f"Temperature must be > 0, got {temperature}")

        # Back-compute approximate logits (inverse softmax is not unique,
        # but log(p) is a reasonable approximation for calibration)
        eps = 1e-9
        logits = [
            math.log(max(entailment, eps)),
            math.log(max(neutral, eps)),
            math.log(max(contradiction, eps)),
        ]
        scaled = [l / temperature for l in logits]
        max_l = max(scaled)
        exps = [math.exp(s - max_l) for s in scaled]
        total = sum(exps)
        probs = [e / total for e in exps]
        return max(probs)

    @staticmethod
    def _percentile_calibrate(
        raw_confidence: float,
        reference: List[float],
    ) -> float:
        """
        Map raw_confidence to its percentile rank in the reference distribution.
        Reference must be sorted ascending.
        """
        if not reference:
            return raw_confidence

        # Binary search for position
        lo, hi = 0, len(reference)
        while lo < hi:
            mid = (lo + hi) // 2
            if reference[mid] < raw_confidence:
                lo = mid + 1
            else:
                hi = mid

        return lo / len(reference)

    def _isotonic_calibrate(self, raw_confidence: float) -> float:
        """
        Isotonic regression calibration.
        Expects a serialized sklearn IsotonicRegression model.

        The model should be placed at:
            config/calibration/{model_name}_isotonic.pkl
        where model_name has '/' replaced with '_'.
        """
        try:
            import joblib

            # Replace slashes in huggingface model names for safe filenames
            safe_name = self._model_name.replace("/", "_")
            calib_path = CONFIG_DIR / "calibration" / f"{safe_name}_isotonic.pkl"

            if calib_path.exists():
                calibrator = joblib.load(calib_path)
                # Predict returns an array, we want the float
                return float(calibrator.transform([raw_confidence])[0])
            else:
                logger.warning(
                    "Isotonic calibration artifact missing at %s, falling back to raw",
                    calib_path
                )
                return raw_confidence
        except ImportError as e:
            logger.warning(
                "scikit-learn or joblib not installed, falling back to raw: %s", e
            )
            return raw_confidence
        except Exception as e:
            logger.warning(
                "Isotonic calibration failed (%s), falling back to raw", e
            )
            return raw_confidence