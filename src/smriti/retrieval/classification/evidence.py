"""
classification/evidence.py — NLI cross-encoder evidence generation.

This is the ONLY module in Phase 6 that imports sentence-transformers.

Produces RelationshipEvidence objects (lifecycle: EVIDENCE).
ConfidenceCalibrator (called by __init__.py) advances to CALIBRATED_EVIDENCE.

Changes from original:
    - Evidence now populates NLIScores + InferenceMetadata (separated)
    - raw_confidence is set in NLIScores; calibrated_confidence starts equal
      to raw_confidence until ConfidenceCalibrator is applied
    - InferenceMetadata records latency per batch

Rules:
    ✅ Process in configurable batches
    ✅ Handle model failures gracefully (skip pair, record error)
    ✅ Convert numpy/torch → plain Python before returning
    ✅ Record per-batch latency in InferenceMetadata
    ❌ Never modify Claims or CandidatePairs
    ❌ Never produce Relationship objects (resolver does that)
    ❌ Never apply thresholds (resolver does that)
"""

from __future__ import annotations

import time

import structlog
from smriti.core.config import get_config
from smriti.core.model_provenance import resolve_hf_revision
from smriti.core.models import (
    CandidatePair,
    Claim,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    RelationshipEvidence,
)
from smriti.exceptions import (
    NLIEvaluationInferenceFailureError,
    NLIInferenceBatchError,
    NLIModelError,
)

logger = structlog.get_logger(__name__)

_NLI_LABELS = ["contradiction", "entailment", "neutral"]
_LABEL_INDEX = {label: i for i, label in enumerate(_NLI_LABELS)}

# Retry configuration
_NLI_MAX_RETRIES = 3
_NLI_RETRY_BACKOFF_BASE = 2  # seconds: 1, 2, 4


class NLIEvidenceGenerator:
    """
    Generates RelationshipEvidence for candidate pairs using NLI cross-encoder.
    Instantiate once per pipeline run.
    """

    def __init__(self, model_name: str | None = None) -> None:
        config = get_config()
        nli_cfg = config.get("nli", {})
        self._model_name = model_name or nli_cfg.get(
            "model_name", "cross-encoder/nli-deberta-v3-small"
        )
        self._batch_size: int = nli_cfg.get("batch_size", 16)

        # RECTIFIED (P1-I, "FINAL REVIEW" round): a failed NLI batch used
        # to just log a warning and vanish -- "1000 attempted, 100 failed,
        # 900 resolved" could look identical to "900 successfully
        # evaluated" in every downstream metric. Track the real counts
        # (exposed via last_run_stats after generate_batch()) and, in an
        # evaluation run (config env == "eval"), fail loudly on any
        # inference failure unless evaluation.allow_nli_inference_failures
        # is explicitly set true. Production keeps the previous
        # skip-and-continue behavior -- a transient failure dropping a
        # few candidates is an acceptable production degradation, not an
        # acceptable evaluation one.
        eval_cfg = config.get("evaluation", {})
        self._is_eval_env = config.get("env", "dev") == "eval"
        self._allow_inference_failures = eval_cfg.get("allow_nli_inference_failures", False)
        self.last_run_stats: dict[str, int] = {
            "n_candidates_attempted": 0,
            "n_candidates_scored": 0,
            "n_batch_failures": 0,
            "n_retries": 0,
        }

        self._model = self._load_model()

        # Resolve the real HF commit hash for the loaded NLI model, instead
        # of a hardcoded version string.
        try:
            hf_config = self._model.model.config
        except Exception:
            hf_config = None
        self._model_revision = resolve_hf_revision(hf_config, self._model_name)

        # Real runtime device (the CrossEncoder may fall back to CPU even
        # if a GPU device was requested), rather than an assumed constant.
        self._device = str(getattr(self._model, "device", "cpu"))

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(self._model_name)
            logger.info("nli model loaded", model=self._model_name)
            return model
        except ImportError as e:
            raise NLIModelError(f"sentence-transformers not installed: {e}") from e
        except Exception as e:
            raise NLIModelError(f"Failed to load NLI model '{self._model_name}': {e}") from e

    def generate_batch(
        self,
        pairs: list[CandidatePair],
        claims_map: dict[str, Claim],
    ) -> list[RelationshipEvidence]:
        """
        Generate NLI evidence for validated candidate pairs.

        Returns:
            List of RelationshipEvidence (lifecycle: EVIDENCE, pre-calibration).
        """
        if not pairs:
            return []

        results: list[RelationshipEvidence] = []
        n_batch_failures = 0
        n_pairs_in_failed_batches = 0
        self._retries_this_call = 0

        for batch_idx, batch_start in enumerate(range(0, len(pairs), self._batch_size)):
            batch = pairs[batch_start : batch_start + self._batch_size]
            try:
                batch_evidence = self._process_batch(batch, claims_map, batch_index=batch_idx)
                results.extend(batch_evidence)
            except NLIInferenceBatchError as e:
                n_batch_failures += 1
                n_pairs_in_failed_batches += len(batch)
                logger.warning(
                    "nli batch failed, skipping batch",
                    batch_index=batch_idx,
                    batch_size=len(batch),
                    error=str(e),
                )
                continue

        self.last_run_stats = {
            "n_candidates_attempted": len(pairs),
            "n_candidates_scored": len(results),
            "n_batch_failures": n_batch_failures,
            "n_candidates_in_failed_batches": n_pairs_in_failed_batches,
            "n_retries": self._retries_this_call,
        }

        logger.info(
            "nli evidence generation complete",
            pairs_processed=len(pairs),
            evidence_produced=len(results),
            batch_failures=n_batch_failures,
        )

        if n_batch_failures > 0 and self._is_eval_env and not self._allow_inference_failures:
            raise NLIEvaluationInferenceFailureError(
                f"{n_batch_failures} NLI batch(es) failed during an evaluation run "
                f"({n_pairs_in_failed_batches}/{len(pairs)} candidates never scored). "
                f"Set evaluation.allow_nli_inference_failures: true to permit a "
                f"partial evaluation run, or fix the underlying NLI inference failure."
            )

        return results

    def _run_nli(self, text_pairs: list[tuple]) -> list[list]:
        """Run the cross-encoder with retry/backoff. Returns raw softmax score rows."""
        for attempt in range(_NLI_MAX_RETRIES):
            try:
                raw_scores = self._model.predict(
                    text_pairs,
                    apply_softmax=True,
                    show_progress_bar=False,
                )
                return raw_scores.tolist()
            except Exception as e:
                if attempt == _NLI_MAX_RETRIES - 1:
                    raise NLIInferenceBatchError(
                        f"NLI batch inference failed after {_NLI_MAX_RETRIES} attempts: {e}"
                    ) from e
                self._retries_this_call = getattr(self, "_retries_this_call", 0) + 1
                wait_seconds = _NLI_RETRY_BACKOFF_BASE**attempt
                logger.warning(
                    "NLI batch inference failed, retrying",
                    attempt=attempt + 1,
                    max_retries=_NLI_MAX_RETRIES,
                    wait_seconds=wait_seconds,
                    error=str(e),
                )
                time.sleep(wait_seconds)
        raise NLIInferenceBatchError("NLI batch inference failed with no retries left")

    @staticmethod
    def _scores_to_nli_scores(scores: list) -> NLIScores:
        contradiction_score = float(scores[_LABEL_INDEX["contradiction"]])
        entailment_score = float(scores[_LABEL_INDEX["entailment"]])
        neutral_score = float(scores[_LABEL_INDEX["neutral"]])
        raw_confidence = max(contradiction_score, entailment_score, neutral_score)
        predicted_label = _NLI_LABELS[scores.index(max(scores))]
        return NLIScores(
            entailment_score=entailment_score,
            neutral_score=neutral_score,
            contradiction_score=contradiction_score,
            predicted_label=predicted_label,
            raw_confidence=raw_confidence,
        )

    def _process_batch(
        self,
        batch: list[CandidatePair],
        claims_map: dict[str, Claim],
        batch_index: int = 0,
    ) -> list[RelationshipEvidence]:
        """
        Process one batch of candidate pairs with retry logic.

        RECTIFIED (external review, bidirectional-NLI rewrite): a single
        NLI call with (claim_a.text, claim_b.text) can only ever tell you
        whether A entails B -- it says nothing about whether B entails A,
        so "which claim is the more general one" and "do the two claims
        say the same thing" (EQUIVALENT) were both structurally
        unanswerable, and SUPPORTS' direction was always A_TO_B by
        construction rather than by evidence. This now runs the
        cross-encoder on BOTH orderings for every pair, in one combined
        batch (so batching efficiency is preserved -- this doubles the
        number of forward passes, not the number of Python-level round
        trips), and stores both directions on RelationshipEvidence.
        """
        text_pairs_ab = []
        text_pairs_ba = []
        valid_pairs = []

        for pair in batch:
            claim_a = claims_map.get(pair.claim_id_a)
            claim_b = claims_map.get(pair.claim_id_b)
            if claim_a is None or claim_b is None:
                logger.warning(
                    "claim not found for nli",
                    claim_id_a=pair.claim_id_a[:8],
                    claim_id_b=pair.claim_id_b[:8],
                )
                continue
            text_pairs_ab.append((claim_a.text, claim_b.text))
            text_pairs_ba.append((claim_b.text, claim_a.text))
            valid_pairs.append(pair)

        if not text_pairs_ab:
            return []

        batch_start_time = time.monotonic()
        # One combined forward pass for both directions (ab then ba, same
        # order as valid_pairs) rather than two separate model.predict()
        # calls, so batching throughput is unaffected by the direction split.
        combined_scores = self._run_nli(text_pairs_ab + text_pairs_ba)
        n = len(valid_pairs)
        scores_ab, scores_ba = combined_scores[:n], combined_scores[n:]

        batch_elapsed = time.monotonic() - batch_start_time
        per_pair_latency_ms = (batch_elapsed / max(2 * n, 1)) * 1000.0

        evidence_list: list[RelationshipEvidence] = []

        for pair, s_ab, s_ba in zip(valid_pairs, scores_ab, scores_ba, strict=False):
            nli_scores_ab = self._scores_to_nli_scores(s_ab)
            nli_scores_ba = self._scores_to_nli_scores(s_ba)

            inference_metadata = InferenceMetadata(
                model_name=self._model_name,
                model_version=self._model_revision,
                runtime_seconds=batch_elapsed,
                device=self._device,
                batch_index=batch_index,
                latency_ms=per_pair_latency_ms,
            )

            evidence = RelationshipEvidence(
                pair=pair,
                cosine_similarity=pair.cosine_similarity,
                nli_scores=nli_scores_ab,
                nli_scores_b_to_a=nli_scores_ba,
                calibrated_confidence=nli_scores_ab.raw_confidence,  # Updated by ConfidenceCalibrator
                calibrated_confidence_b_to_a=nli_scores_ba.raw_confidence,  # Updated by ConfidenceCalibrator (P0-5)
                inference_metadata=inference_metadata,
                lifecycle_stage=LifecycleStage.EVIDENCE,
            )
            evidence_list.append(evidence)

        return evidence_list
