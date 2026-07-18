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
from typing import List
import structlog

logger = structlog.get_logger(__name__)


def l2_normalize(vector: List[float]) -> List[float]:
    """
    Apply L2 normalization to a vector.

    Precondition: vector has been validated (non-empty, finite, non-zero norm).

    Args:
        vector: Raw float list (pre-validated).

    Returns:
        New float list with unit L2 norm. Input is never mutated.
    """
    sum_sq = sum(float(x) * float(x) for x in vector)

    # Warn if vector is extremely close to zero (should be caught by validation)
    if sum_sq <= 1e-15:
        logger.warning(
            "near-zero norm vector in normalization, using epsilon",
            sum_sq=sum_sq,
        )

    # Compute norm with a tiny epsilon to prevent division by zero
    # even if validation had a very small margin.
    norm = math.sqrt(sum_sq) + 1e-12

    return [float(x) / norm for x in vector]


def normalize_batch(
    vectors: List[List[float]],
    enabled: bool = True,
) -> List[List[float]]:
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