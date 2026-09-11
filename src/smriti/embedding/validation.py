"""
validation.py — Mathematical vector validation for Phase 5.

Responsibility:
    Verify that a raw (or normalized) vector from the embedder satisfies
    mathematical invariants before it becomes an immutable Vector domain object.

    Called TWICE per vector:
        1. After inference — validates raw output from the model
        2. After normalization — cheap guard against numerical edge cases

Validation checks (in order):
    1. Non-empty:         vector must have at least one element
    2. Correct dimension: len(vector) == descriptor.dimension
    3. dtype check:       all elements must be strictly float (no ints, numpy scalars, etc.)
    4. Finite values:     no NaN or Inf anywhere
    5. Non-zero norm:     a zero vector cannot be normalized

Rules:
    ✅ Return (bool, Optional[str]) — callers decide what to do with failures
    ✅ Never modify the vector
    ✅ Provide clear, actionable error messages

    ❌ Never normalize (that's normalization.py's job)
    ❌ Never embed (that's embedder.py's job)
"""

from __future__ import annotations

import math

import structlog

logger = structlog.get_logger(__name__)


def validate_vector(
    vector: list[float],
    expected_dimension: int,
) -> tuple[bool, str | None]:
    """
    Validate a raw or normalized embedding vector.

    Args:
        vector:             Float list from embedder (raw) or normalization.
        expected_dimension: Expected length (from EmbeddingModelDescriptor.dimension).

    Returns:
        (True, None)             if vector passes all checks
        (False, error_message)   if any check fails
    """
    # Check 1: Non-empty
    if not vector:
        return False, "Vector is empty"

    # Check 2: Correct dimension
    actual_dim = len(vector)
    if actual_dim != expected_dimension:
        return False, (f"Dimension mismatch: expected {expected_dimension}, got {actual_dim}")

    # Check 3: dtype — all elements must be strictly float
    # This rejects ints, numpy scalars, strings, etc. to enforce type purity.
    for i, value in enumerate(vector):
        if not isinstance(value, float):
            return False, (
                f"Non-float type at index {i}: {type(value).__name__} " f"(expected float)"
            )

    # Check 4: Finite values (no NaN or Inf)
    for i, value in enumerate(vector):
        if math.isnan(value):
            return False, f"NaN detected at index {i}"
        if math.isinf(value):
            return False, f"Inf detected at index {i}"

    # Check 5: Non-zero norm
    # RECTIFIED: check the raw values directly rather than sum-of-squares.
    # For extremely small-but-nonzero floats (e.g. ~1e-178), squaring can
    # underflow to exactly 0.0 in float64 even though the vector itself is
    # clearly nonzero — that spurious underflow must not be misreported as
    # a genuine zero-norm (all-zero) vector.
    if not any(float(x) != 0.0 for x in vector):
        return False, "Zero-norm vector (all elements are zero)"

    return True, None


def validate_batch(
    vectors: list[list[float]],
    expected_dimension: int,
) -> list[tuple[bool, str | None]]:
    """
    Validate an entire batch of vectors.

    Returns:
        List of (is_valid, error_message_or_None), one per input vector.
    """
    return [validate_vector(v, expected_dimension) for v in vectors]
