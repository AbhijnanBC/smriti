"""
normalization.py — Vector normalization for Phase 5.

Responsibility:
    Apply L2 (unit-length) normalization to validated embedding vectors.
    This is a SEPARATE step from inference — the embedder never normalizes.

Why separate?
    Normalization is a configuration-driven post-processing step.
    Different normalization methods may be added without touching the embedder.
    Inference reproducibility is preserved independently of normalization choice.

L2 normalization:
    v_normalized = v / ||v||₂
    After normalization: ||v_normalized||₂ = 1.0

    This makes cosine similarity equivalent to dot product,
    which is important for Phase 6's nearest-neighbor retrieval.

Rules:
    ✅ Return a new list (never mutate input)
    ✅ Only called on validated vectors (validation.py ensures non-zero norm)
    ✅ Configurable via config (can be disabled)

    ❌ Never validate (validation.py's responsibility)
    ❌ Never infer (embedder.py's responsibility)

Note: After normalization, validation.py is called again (post-norm check).
      This module is not aware of that — it just normalizes.
"""

from __future__ import annotations

import math

import structlog

logger = structlog.get_logger(__name__)


def l2_normalize(vector: list[float]) -> list[float]:
    """
    Apply L2 normalization to a vector.

    Precondition: vector has been validated (non-empty, finite, non-zero norm).

    Args:
        vector: Raw float list (pre-validated).

    Returns:
        New float list with unit L2 norm. Input is never mutated.
    """
    # RECTIFIED: use math.hypot for the Euclidean norm instead of
    # sqrt(sum(x*x)) — hypot avoids spurious intermediate underflow/overflow
    # for very small or very large magnitudes.
    floats = [float(x) for x in vector]
    norm = math.hypot(*floats)

    # Only fall back to an epsilon if the computed norm is a literal zero
    # (true division-by-zero guard for a very small margin that slipped
    # past validation) — do NOT unconditionally add an epsilon, since for
    # legitimately tiny but non-zero vectors (norm well below 1e-12) a flat
    # +1e-12 would dominate the real norm and corrupt the result.
    if norm == 0.0:
        logger.warning("near-zero norm vector in normalization, using epsilon")
        norm = 1e-12

    return [x / norm for x in floats]


def normalize_batch(
    vectors: list[list[float]],
    enabled: bool = True,
) -> list[list[float]]:
    """
    Normalize a batch of vectors.

    Args:
        vectors:  Pre-validated float lists.
        enabled:  If False, returns vectors unchanged (normalization disabled).

    Returns:
        List of normalized (or original) vectors. Input vectors are never mutated.
    """
    if not enabled:
        return [[float(x) for x in v] for v in vectors]
    return [l2_normalize(v) for v in vectors]
