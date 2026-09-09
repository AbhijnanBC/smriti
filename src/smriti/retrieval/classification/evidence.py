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
from typing import List, Dict, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Claim, CandidatePair, RelationshipEvidence,
    NLIScores, InferenceMetadata, LifecycleStage,
)
from smriti.core.model_provenance import resolve_hf_revision
from smriti.exceptions import NLIModelError, NLIInferenceBatchError

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

    def __init__(self, model_name: Optional[str] = None) -> None:
        config = get_config()
        nli_cfg = config.get("nli", {})
        self._model_name = model_name or nli_cfg.get(
            "model", "cross-encoder/nli-deberta-v3-small"
        )
        self._batch_size: int = nli_cfg.get("batch_size", 16)
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
            raise NLIModelError(
                f"Failed to load NLI model '{self._model_name}': {e}"
            ) from e

    def generate_batch(
        self,
        pairs: List[CandidatePair],
        claims_map: Dict[str, Claim],
    ) -> List[RelationshipEvidence]:
        """
        Generate NLI evidence for validated candidate pairs.

        Returns:
            List of RelationshipEvidence (lifecycle: EVIDENCE, pre-calibration).
        """
        if not pairs:
            return []

        results: List[RelationshipEvidence] = []

        for batch_idx, batch_start in enumerate(range(0, len(pairs), self._batch_size)):
            batch = pairs[batch_start: batch_start + self._batch_size]
            try:
                batch_evidence = self._process_batch(batch, claims_map, batch_index=batch_idx)
                results.extend(batch_evidence)
            except NLIInferenceBatchError as e:
                logger.warning(
                    "nli batch failed, skipping batch",
                    batch_index=batch_idx,
                    batch_size=len(batch),
                    error=str(e),
                )
                continue

        logger.info(
            "nli evidence generation complete",
            pairs_processed=len(pairs),
            evidence_produced=len(results),
        )

        return results

    def _process_batch(
        self,
        batch: List[CandidatePair],
        claims_map: Dict[str, Claim],
        batch_index: int = 0,
    ) -> List[RelationshipEvidence]:
        """Process one batch of candidate pairs with retry logic."""
        text_pairs = []
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
            text_pairs.append((claim_a.text, claim_b.text))
            valid_pairs.append(pair)

        if not text_pairs:
            return []

        batch_start_time = time.monotonic()
        scores_list = None

        # Retry loop with exponential backoff
        for attempt in range(_NLI_MAX_RETRIES):
            try:
                raw_scores = self._model.predict(
                    text_pairs,
                    apply_softmax=True,
                    show_progress_bar=False,
                )
                scores_list = raw_scores.tolist()
                break  # Success, exit retry loop
            except Exception as e:
                if attempt == _NLI_MAX_RETRIES - 1:
                    # Last attempt failed, raise error
                    raise NLIInferenceBatchError(
                        f"NLI batch inference failed after {_NLI_MAX_RETRIES} attempts: {e}"
                    ) from e
                # Exponential backoff: 1s, 2s, 4s
                wait_seconds = _NLI_RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "NLI batch inference failed, retrying",
                    attempt=attempt + 1,
                    max_retries=_NLI_MAX_RETRIES,
                    wait_seconds=wait_seconds,
                    error=str(e),
                )
                time.sleep(wait_seconds)

        # Should never happen if the loop succeeded, but guard
        if scores_list is None:
            raise NLIInferenceBatchError("NLI batch inference failed with no retries left")

        batch_elapsed = time.monotonic() - batch_start_time
        per_pair_latency_ms = (batch_elapsed / max(len(text_pairs), 1)) * 1000.0

        evidence_list: List[RelationshipEvidence] = []

        for pair, scores in zip(valid_pairs, scores_list):
            contradiction_score = float(scores[_LABEL_INDEX["contradiction"]])
            entailment_score = float(scores[_LABEL_INDEX["entailment"]])
            neutral_score = float(scores[_LABEL_INDEX["neutral"]])
            raw_confidence = max(contradiction_score, entailment_score, neutral_score)
            predicted_label = _NLI_LABELS[scores.index(max(scores))]

            nli_scores = NLIScores(
                entailment_score=entailment_score,
                neutral_score=neutral_score,
                contradiction_score=contradiction_score,
                predicted_label=predicted_label,
                raw_confidence=raw_confidence,
            )

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
                nli_scores=nli_scores,
                calibrated_confidence=raw_confidence,  # Updated by ConfidenceCalibrator
                inference_metadata=inference_metadata,
                lifecycle_stage=LifecycleStage.EVIDENCE,
            )
            evidence_list.append(evidence)

        return evidence_list