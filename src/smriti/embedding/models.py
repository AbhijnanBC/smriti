"""
embedding/models.py — Internal temporary objects for Phase 5.

These objects are NEVER exported from the embedding package.
They exist only as intermediate stages in the semantic encoding pipeline.

List[Claim]
    ↓
ValidatedClaim[]      (claim passed structural check)
    ↓
EmbeddingInput[]      (contextual text payload ready for the model)
    ↓
EmbeddingResult[]     (mutable result per claim, carries status + warnings)
    ↓
Embedding[]           (public domain object — crosses phase boundary, NO status)
    ↓
EmbeddingQuality[]    (public diagnostic — crosses phase boundary)
    ↓
EmbeddedClaim[]       (public domain object — crosses phase boundary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from enum import Enum

from smriti.core.models import Claim, Embedding

class EmbeddingStatus(str, Enum):
    """Terminal status for one Claim's embedding attempt (internal use only)."""
    SUCCESS  = "success"
    CACHED   = "cached"
    STALE    = "stale"
    FAILED   = "failed"
    SKIPPED  = "skipped"


@dataclass(frozen=True)
class ValidatedClaim:
    """
    A Claim that has passed pre-inference structural validation.

    This is the entry ticket to embedding inference.
    Only ValidatedClaims are passed to the embedder.
    """
    claim: Claim
    embedding_text: str   # Pre-computed canonical text



@dataclass(frozen=True)
class EmbeddingInput:
    """
    A validated claim paired with its contextual embedding payload.

    The payload is constructed by EmbeddingInputFactory:
        context heading + claim text (if context exists)
        OR just claim text (if no context)

    This is what actually gets passed to BaseEmbedder.encode_batch().
    The cache_key is managed separately by CacheKeyFactory.
    """
    claim_id: str
    payload: str        # Model-ready text (context-enriched)
    original_text: str  # Claim.text (kept for traceability)
    cache_key: str      # Deterministic cache key from CacheKeyFactory


@dataclass
class EmbeddingResult:
    """
    Internal mutable execution result for one Claim's embedding attempt.

    This object is created by the orchestrator, populated across pipeline stages,
    then either discarded (on failure) or used to construct the public
    EmbeddedClaim (on success).

    NEVER crosses the phase boundary. Not included in Phase5Result.

    Fields:
        claim_id:     The originating Claim's ID.
        status:       Current execution status (mutable during pipeline).
        embedding:    The completed Embedding (None until Stage 8 succeeds).
        warnings:     Non-fatal issues encountered for this claim.
        errors:       Fatal issues that prevented embedding.
        elapsed_time: Time spent embedding this specific claim (seconds).
        from_cache:   Whether the vector came from cache.
    """
    claim_id: str
    status: EmbeddingStatus
    embedding: Optional[Embedding] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0
    from_cache: bool = False

    @property
    def succeeded(self) -> bool:
        return (
            self.embedding is not None
            and self.status in (
                EmbeddingStatus.SUCCESS,
                EmbeddingStatus.CACHED,
                EmbeddingStatus.STALE,
            )
        )