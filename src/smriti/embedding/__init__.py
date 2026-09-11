"""
embedding/__init__.py — Public API for Phase 5: Semantic Embedding Layer.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.embedding import embed_claims, Phase5Result

They NEVER import from internal modules.

Public contract:
    embed_claims(claims: List[Claim], ...) → Phase5Result

That is the ONLY function that crosses the Phase 5 boundary.

Key implementation changes from original:
    - Status removed from Embedding (pure semantic artifact)
    - Internal EmbeddingResult tracks per-claim execution status
    - Failed batches retry claim-by-claim before marking anything failed
    - Post-normalization validation added (Stage 7)
    - EmbeddingQuality built per-claim (Stage 8)
    - Phase5Result includes warnings and errors lists
    - Manifest includes cache lifecycle metrics
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Phase5Stats,
    Vector,
    VectorDType,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.embedding.builders import (
    build_embedded_claim,
    build_embedding,
    build_embedding_quality,
    build_vector,
)
from smriti.embedding.cache import EmbeddingCachePolicy
from smriti.embedding.embedder import (
    PHASE5_PIPELINE_VERSION,
    PHASE5_SCHEMA_VERSION,
    BaseEmbedder,
    SentenceTransformerEmbedder,
)
from smriti.embedding.input_factory import CacheKeyFactory, EmbeddingInputFactory
from smriti.embedding.models import EmbeddingResult, EmbeddingStatus
from smriti.embedding.normalization import l2_normalize
from smriti.embedding.statistics import Phase5StatsCollector
from smriti.embedding.validation import validate_vector
from smriti.exceptions import EmbeddingInferenceError, EmbeddingModelError, Phase5Error

logger = structlog.get_logger(__name__)


# ── Public result type ────────────────────────────────────────────────────────


@dataclass
class Phase5Result:
    """
    Complete output of Phase 5 — all EmbeddedClaims produced.
    This is what Phase 6 receives.

    Fields:
        embedded_claims: All successfully embedded claims.
        stats:           Immutable execution statistics.
        run_id:          Current pipeline run identifier.
        warnings:        Non-fatal issues collected during embedding.
        errors:          Fatal per-claim errors (claim still skipped gracefully).
        manifest_path:   Path to written manifest.json.
        dataset_path:    Path to written dataset.json.
    """

    embedded_claims: list[EmbeddedClaim]
    stats: Phase5Stats
    run_id: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    manifest_path: Path | None = None
    dataset_path: Path | None = None

    @property
    def total_embedded(self) -> int:
        return len(self.embedded_claims)

    def to_dataset_json(self) -> str:
        """
        Serialize all EmbeddedClaims to JSON for Phase 6.
        Written to artifacts/run_{id}/phase5/dataset.json.

        Status field in output: derived from EmbeddingQuality (cache_used)
        since status is no longer stored on Embedding itself.
        """
        records = []
        for ec in self.embedded_claims:
            # Derive status from quality (status is not on Embedding)
            status = "cached" if ec.quality.cache_used else "success"

            records.append(
                {
                    "claim_id": ec.claim_id,
                    "vector": list(ec.values),  # Plain list of floats
                    "dimension": ec.dimension,
                    "schema_version": ec.schema_version,
                    "status": status,
                    "quality": {
                        "dimension_ok": ec.quality.dimension_ok,
                        "normalized": ec.quality.normalized,
                        "finite": ec.quality.finite,
                        "cache_used": ec.quality.cache_used,
                    },
                    "model": {
                        "provider": ec.embedding.descriptor.provider,
                        "model_name": ec.embedding.descriptor.model_name,
                        "revision": ec.embedding.descriptor.model_revision,
                        "dimension": ec.embedding.descriptor.dimension,
                        "signature": ec.embedding.descriptor.model_signature,
                        "embedding_family": ec.embedding.descriptor.embedding_family,
                    },
                    "provenance": {
                        "pipeline_version": ec.embedding.provenance.pipeline_version,
                        "normalization_mode": ec.embedding.provenance.normalization_mode,
                        "device": ec.embedding.provenance.device,
                        "config_hash": ec.embedding.provenance.config_hash,
                    },
                }
            )
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── EmbeddedClaim helper (add to EmbeddedClaim or keep as standalone) ─────────
# We monkeypatch a convenience method here so EmbeddedClaim.to_dataset_json
# doesn't need to import from __init__ (which would create a circular import).

# def _values_as_list(self) -> List[float]:
# """Return vector values as a plain Python list."""
# return list(self.embedding.vector.values)

# EmbeddedClaim.values_as_list = _values_as_list   # type: ignore[attr-defined]


# ── Config hash ───────────────────────────────────────────────────────────────


def _compute_config_hash(config: dict) -> str:
    """
    Deterministic hash of embedding configuration fields that affect output.

    Included (affect embedding values):
        model_name          — different model = different vectors
        normalize           — normalization changes the vector
        device              — should NOT affect values, but included for safety
        instruction_prefix  — changes the input text, changes the vector
        max_seq_length      — truncation changes the vector

    Excluded (do not affect embedding values):
        batch_size          — throughput only, not correctness
        cache_embeddings    — operational flag, not semantic
        pipeline_version    — pipeline version changes tracked separately
    """
    emb_cfg = config.get("embedding", {})
    relevant = {
        "model_name": emb_cfg.get("model_name", ""),
        "normalize": emb_cfg.get("normalize", True),
        "device": emb_cfg.get("device", "cpu"),
        "instruction_prefix": emb_cfg.get("instruction_prefix", ""),
        "max_seq_length": emb_cfg.get("max_seq_length", None),
    }
    material = (
        f"model:{relevant['model_name']}|"
        f"norm:{relevant['normalize']}|"
        f"dev:{relevant['device']}|"
        f"prefix:{relevant['instruction_prefix']}|"
        f"seq:{relevant['max_seq_length']}"
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


# ── Core public function ───────────────────────────────────────────────────────


def embed_claims(
    claims: list[Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    embedder: BaseEmbedder | None = None,
    force_reembed: bool = False,
) -> Phase5Result:
    """
    Transform all Claims into EmbeddedClaims.

    This is Phase 5's sole public function.
    All internal components are hidden from callers.

    Args:
        claims:           List of immutable Claims from Phase 4.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        embedder:         Optional pre-constructed embedder (for testing).
                          If None, SentenceTransformerEmbedder is used.
        force_reembed:    If True, bypass cache and re-embed all claims.

    Returns:
        Phase5Result containing EmbeddedClaims, stats, warnings, and paths.

    Raises:
        Phase5Error: If the embedding model fails to load (unrecoverable).
    """
    config = get_config()
    emb_cfg = config.get("embedding", {})
    batch_size: int = emb_cfg.get("batch_size", 32)
    normalize: bool = emb_cfg.get("normalize", True)
    cache_enabled: bool = emb_cfg.get("cache_embeddings", True) and not force_reembed
    device: str = emb_cfg.get("device", "cpu")

    logger.info(
        "phase 5 starting",
        run_id=run_id,
        claims=len(claims),
        batch_size=batch_size,
        normalize=normalize,
        cache_enabled=cache_enabled,
    )

    start_time = manifest_manager.start_phase(phase=5)

    # ── Initialize components ─────────────────────────────────────────────────
    if embedder is None:
        try:
            embedder = SentenceTransformerEmbedder(device=device)
        except EmbeddingModelError:
            raise  # Unrecoverable: bubble up as Phase5Error subclass

    config_hash = _compute_config_hash(config)
    descriptor = embedder.descriptor
    model_sig = descriptor.model_signature
    normalization_mode = "l2" if normalize else "none"

    provenance = EmbeddingProvenance(
        pipeline_version=PHASE5_PIPELINE_VERSION,
        normalization_mode=normalization_mode,
        device=device,
        config_hash=config_hash,
    )

    # Separated: EmbeddingInputFactory handles payload only
    #            CacheKeyFactory handles key generation only
    input_factory = EmbeddingInputFactory(
        instruction_prefix=emb_cfg.get("instruction_prefix", ""),
    )
    key_factory = CacheKeyFactory(
        model_signature=model_sig,
        config_hash=config_hash,
    )

    cache_policy = EmbeddingCachePolicy(enabled=cache_enabled)
    stats_collector = Phase5StatsCollector()

    # Accumulated warnings and errors for Phase5Result
    all_warnings: list[str] = []
    all_errors: list[str] = []

    # ── Process claims ─────────────────────────────────────────────────────────
    embedded_claims: list[EmbeddedClaim] = []

    with Timer("phase5_embedding"):
        # ── Stage 1 + 2: Validate claims, build payloads and cache keys ───────
        valid_claims: list[Claim] = []
        payloads: dict[str, str] = {}  # claim_id → payload text
        cache_keys: dict[str, str] = {}  # claim_id → cache key

        for claim in claims:
            if not claim.text or not claim.text.strip():
                logger.debug("skipping empty claim", claim_id=claim.claim_id[:8])
                stats_collector.record_skipped()
                continue

            payloads[claim.claim_id] = input_factory.build_payload(claim)
            cache_keys[claim.claim_id] = key_factory.build_cache_key(claim)
            valid_claims.append(claim)

        # ── Stage 3: Cache resolution ─────────────────────────────────────────
        pending_claims: list[Claim] = []
        cached_results: dict[str, list[float]] = {}  # claim_id → cached vector

        for claim in valid_claims:
            cache_key = cache_keys[claim.claim_id]
            status, vector = cache_policy.lookup(cache_key, model_sig, config_hash)

            if status == EmbeddingStatus.CACHED:
                cached_results[claim.claim_id] = vector
                stats_collector.record_cached()
            elif status == EmbeddingStatus.STALE:
                pending_claims.append(claim)
                stats_collector.record_stale()
                logger.debug("cache stale → will re-embed", claim_id=claim.claim_id[:8])
            else:
                pending_claims.append(claim)

        logger.info(
            "cache resolution complete",
            cached=len(cached_results),
            pending=len(pending_claims),
        )

        # ── Stage 3b: Build EmbeddedClaims for cached results ─────────────────
        for claim in valid_claims:
            if claim.claim_id not in cached_results:
                continue
            raw_cached = cached_results[claim.claim_id]
            try:
                vec = build_vector(
                    raw_cached,
                    descriptor.dimension,
                    dtype=VectorDType.FLOAT64,
                    normalized=True,
                )
                emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
                qual = build_embedding_quality(vec, descriptor, cache_used=True)
                ec = build_embedded_claim(claim.claim_id, emb, qual)
                embedded_claims.append(ec)
            except Exception as e:
                msg = f"claim {claim.claim_id[:8]}: cached vector build failed: {e}"
                all_errors.append(msg)
                logger.error(
                    "cached vector build failed", claim_id=claim.claim_id[:8], error=str(e)
                )
                stats_collector.record_failed()

        # ── Stages 4-9: Batch inference for pending claims ────────────────────
        if pending_claims:
            for batch_start in range(0, len(pending_claims), batch_size):
                batch_claims = pending_claims[batch_start : batch_start + batch_size]
                batch_payloads = [payloads[c.claim_id] for c in batch_claims]
                stats_collector.record_batch(len(batch_claims))

                logger.debug(
                    "embedding batch",
                    batch_num=batch_start // batch_size + 1,
                    size=len(batch_claims),
                )

                # Attempt batch inference — on failure, retry individually
                raw_vectors: list[list[float]] | None = None
                try:
                    raw_vectors = embedder.encode_batch(batch_payloads)
                except (EmbeddingInferenceError, Exception) as batch_err:
                    logger.warning(
                        "batch encoding failed — retrying individually",
                        batch_size=len(batch_claims),
                        error=str(batch_err),
                    )
                    all_warnings.append(
                        f"Batch of {len(batch_claims)} failed, retrying individually: {batch_err}"
                    )

                if raw_vectors is not None:
                    # Batch succeeded — process all at once
                    _process_batch_results(
                        batch_claims=batch_claims,
                        raw_vectors=raw_vectors,
                        descriptor=descriptor,
                        provenance=provenance,
                        cache_keys=cache_keys,
                        cache_policy=cache_policy,
                        model_sig=model_sig,
                        config_hash=config_hash,
                        normalize=normalize,
                        embedded_claims=embedded_claims,
                        stats_collector=stats_collector,
                        all_warnings=all_warnings,
                        all_errors=all_errors,
                    )
                else:
                    # Batch failed — retry each claim individually
                    for individual_claim in batch_claims:
                        individual_payload = payloads[individual_claim.claim_id]
                        try:
                            single_vectors = embedder.encode_batch([individual_payload])
                            _process_batch_results(
                                batch_claims=[individual_claim],
                                raw_vectors=single_vectors,
                                descriptor=descriptor,
                                provenance=provenance,
                                cache_keys=cache_keys,
                                cache_policy=cache_policy,
                                model_sig=model_sig,
                                config_hash=config_hash,
                                normalize=normalize,
                                embedded_claims=embedded_claims,
                                stats_collector=stats_collector,
                                all_warnings=all_warnings,
                                all_errors=all_errors,
                            )
                        except Exception as single_err:
                            msg = (
                                f"claim {individual_claim.claim_id[:8]} "
                                f"failed after individual retry: {single_err}"
                            )
                            all_errors.append(msg)
                            logger.error(
                                "individual retry failed",
                                claim_id=individual_claim.claim_id[:8],
                                error=str(single_err),
                            )
                            stats_collector.record_failed()

    stats = stats_collector.finalize()

    result = Phase5Result(
        embedded_claims=embedded_claims,
        stats=stats,
        run_id=run_id,
        warnings=all_warnings,
        errors=all_errors,
    )

    # ── Write artifacts ───────────────────────────────────────────────────────
    phase_dir = (
        manifest_manager.run_dir / "phase5"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
    result.dataset_path = dataset_path

    logger.info(
        "dataset written",
        path=str(dataset_path),
        embedded_claims=result.total_embedded,
    )

    # ── Write manifest (with cache lifecycle metrics) ─────────────────────────
    manifest_path = manifest_manager.end_phase(
        phase=5,
        start_time=start_time,
        inputs={"claims": len(claims)},
        outputs={
            "total_embedded": result.total_embedded,
            "successful": stats.successful,
            "cached": stats.cached,
            "stale": stats.stale,
            "failed": stats.failed,
            "skipped": stats.skipped,
            # Cache lifecycle metrics (high priority addition)
            "cache_entries_reused": stats.cache_entries_reused,
            "cache_entries_regenerated": stats.cache_entries_regenerated,
            "cache_entries_invalidated": stats.cache_entries_invalidated,
            # Throughput
            "vectors_per_second": f"{stats.vectors_per_second:.1f}",
            "current_memory_mb": f"{stats.current_memory_mb:.1f}",
            # Model
            "model": descriptor.model_name,
            "dimension": descriptor.dimension,
            "dataset_path": str(dataset_path),
            # Diagnostics
            "warnings": len(all_warnings),
            "errors": len(all_errors),
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # ── Update pipeline state ─────────────────────────────────────────────────
    state_manager.complete_phase(phase=5)

    logger.info(
        "phase 5 complete",
        total_embedded=result.total_embedded,
        cached=stats.cached,
        successful=stats.successful,
        failed=stats.failed,
        cache_hit_rate=f"{stats.cache_hit_rate:.1%}",
        throughput=f"{stats.vectors_per_second:.1f} vec/s",
        runtime=f"{stats.total_runtime_seconds:.2f}s",
        warnings=len(all_warnings),
    )

    return result


# ── Internal helpers ──────────────────────────────────────────────────────────


def _process_batch_results(
    batch_claims: list[Claim],
    raw_vectors: list[list[float]],
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
    cache_keys: dict[str, str],
    cache_policy: EmbeddingCachePolicy,
    model_sig: str,
    config_hash: str,
    normalize: bool,
    embedded_claims: list[EmbeddedClaim],
    stats_collector: Phase5StatsCollector,
    all_warnings: list[str],
    all_errors: list[str],
) -> None:
    """
    Process raw inference output for one batch (or single claim retry).
    Handles: validation → normalization → post-norm validation → build → cache.

    Mutates embedded_claims, stats_collector, all_warnings, all_errors in-place.
    """
    for i, claim in enumerate(batch_claims):
        raw_vector = raw_vectors[i]

        # ── Stage 5: Vector validation (pre-normalization) ────────────────────
        is_valid, error_msg = validate_vector(raw_vector, descriptor.dimension)
        if not is_valid:
            msg = f"claim {claim.claim_id[:8]} pre-norm validation: {error_msg}"
            all_warnings.append(msg)
            logger.warning("vector validation failed", claim_id=claim.claim_id[:8], error=error_msg)
            stats_collector.record_failed()
            continue

        # ── Stage 6: L2 Normalization ─────────────────────────────────────────
        final_vector_list = (
            l2_normalize(raw_vector) if normalize else [float(x) for x in raw_vector]
        )

        # ── Stage 7: Post-normalization re-validation ─────────────────────────
        is_valid_post, error_post = validate_vector(final_vector_list, descriptor.dimension)
        if not is_valid_post:
            msg = (
                f"claim {claim.claim_id[:8]} post-norm validation failed "
                f"(numerical issue after L2): {error_post}"
            )
            all_warnings.append(msg)
            logger.warning(
                "post-normalization validation failed",
                claim_id=claim.claim_id[:8],
                error=error_post,
            )
            stats_collector.record_failed()
            continue

        # ── Cache the normalized result ────────────────────────────────────────
        cache_key = cache_keys[claim.claim_id]
        cache_policy.store(cache_key, final_vector_list, model_sig, config_hash)

        # ── Stage 8: Build domain objects ──────────────────────────────────────
        try:
            vec = build_vector(
                final_vector_list,
                descriptor.dimension,
                dtype=VectorDType.FLOAT64,
                normalized=normalize,
            )
            emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
            qual = build_embedding_quality(vec, descriptor, cache_used=False)
            ec = build_embedded_claim(claim.claim_id, emb, qual)
        except AssertionError as ae:
            msg = f"claim {claim.claim_id[:8]} builder assertion: {ae}"
            all_errors.append(msg)
            logger.error("builder assertion failed", claim_id=claim.claim_id[:8], error=str(ae))
            stats_collector.record_failed()
            continue

        # ── Stage 9: Accumulate ────────────────────────────────────────────────
        embedded_claims.append(ec)
        stats_collector.record_successful()
