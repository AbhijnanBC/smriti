"""
builders.py — Immutable domain object construction for Phase 5.

Responsibility:
    Construct immutable Vector, Embedding, EmbeddingQuality, and EmbeddedClaim objects.
    This is the ONLY place where these objects are instantiated.

    Like Phase 4's builder.py — pure object construction, no logic.

Builders:
    build_vector()              → Vector            (from raw float list)
    build_embedding()           → Embedding         (pure semantic, no status)
    build_embedding_quality()   → EmbeddingQuality  (diagnostic snapshot)
    build_embedded_claim()      → EmbeddedClaim     (public phase boundary object)

Rules:
    ✅ Construct immutable domain objects
    ✅ Attach all required metadata (descriptor, provenance)
    ✅ Convert List[float] → tuple inside Vector
    ✅ Assert dimension invariant before constructing Vector (defensive safeguard)

    ❌ Never perform inference
    ❌ Never normalize
    ❌ Never validate (validation.py's responsibility)
    ❌ No logic or heuristics beyond construction
"""

from __future__ import annotations

import math
from typing import List
import structlog

from smriti.core.models import (
    Embedding,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Vector,
    VectorDType,
)

logger = structlog.get_logger(__name__)


def build_vector(
    values: List[float],
    expected_dimension: int,
    dtype: VectorDType = VectorDType.FLOAT64,
    normalized: bool = False,
) -> Vector:
    """
    Construct an immutable Vector domain object from a validated float list.

    Includes a defensive assertion that dimension matches before constructing.
    This is cheap and protects against descriptor/vector mismatches that
    might slip through validation in unusual code paths.

    Args:
        values:             Validated (and optionally normalized) float list.
        expected_dimension: Dimension from EmbeddingModelDescriptor.
        dtype:              "float64" or "float32" — recorded for downstream use.
        normalized:         True if L2 normalization was applied.

    Returns:
        Immutable Vector.

    Raises:
        AssertionError: If len(values) != expected_dimension (defensive safeguard).
    """
    # Defensive assertion — cheap, catches any latent dimension mismatch
    assert expected_dimension == len(values), (
        f"build_vector: descriptor.dimension={expected_dimension} "
        f"!= len(values)={len(values)}"
    )

    vector = Vector(
        values=tuple(float(v) for v in values),
        dimension=len(values),
        dtype=dtype,
        normalized=normalized,
    )

    logger.debug(
        "vector built",
        dimension=vector.dimension,
        dtype=dtype,
        normalized=normalized,
    )

    return vector


def build_embedding(
    claim_id: str,
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
) -> Embedding:
    """
    Construct an immutable Embedding from a validated, normalized Vector.

    Note: Embedding carries NO status field.
          Status belongs to the internal EmbeddingResult.
          This is a pure, timeless semantic artifact.

    Args:
        claim_id:    The originating Claim's ID.
        vector:      Validated (and optionally normalized) Vector domain object.
        descriptor:  Which model produced this vector.
        provenance:  How/where inference was run.

    Returns:
        Immutable Embedding.
    """
    embedding = Embedding(
        claim_id=claim_id,
        vector=vector,
        descriptor=descriptor,
        provenance=provenance,
    )

    logger.debug(
        "embedding built",
        claim_id=claim_id[:8],
        dimension=vector.dimension,
        normalized=vector.normalized,
    )

    return embedding


def build_embedding_quality(
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    cache_used: bool,
) -> EmbeddingQuality:
    """
    Construct an EmbeddingQuality diagnostic snapshot.

    Phase 6 reads this and never recomputes it.
    Calling this once here prevents redundant computation downstream.

    Args:
        vector:      The built Vector (already the final, stored vector).
        descriptor:  The model descriptor to compare dimension against.
        cache_used:  True if the vector came from cache (not fresh inference).

    Returns:
        Immutable EmbeddingQuality.
    """
    # Check finiteness — redundant after validation but useful as a diagnostic fact
    finite = all(
        math.isfinite(v) for v in vector.values
    )

    quality = EmbeddingQuality(
        dimension_ok=(vector.dimension == descriptor.dimension),
        normalized=vector.normalized,
        finite=finite,
        cache_used=cache_used,
    )

    logger.debug(
        "embedding quality built",
        dimension_ok=quality.dimension_ok,
        normalized=quality.normalized,
        finite=quality.finite,
        cache_used=quality.cache_used,
    )

    return quality


def build_embedded_claim(
    claim_id: str,
    embedding: Embedding,
    quality: EmbeddingQuality,
) -> EmbeddedClaim:
    """
    Construct an immutable EmbeddedClaim.

    Args:
        claim_id:   The Claim's ID (referential, not the Claim object itself).
        embedding:  The completed Embedding (pure semantic artifact).
        quality:    The EmbeddingQuality diagnostic snapshot.

    Returns:
        Immutable EmbeddedClaim.
    """
    embedded_claim = EmbeddedClaim(
        claim_id=claim_id,
        embedding=embedding,
        quality=quality,
        schema_version="5.0",
    )

    logger.debug(
        "embedded claim built",
        claim_id=claim_id[:8],
        dimension=embedding.dimension,
        cache_used=quality.cache_used,
    )

    return embedded_claim