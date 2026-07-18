"""
input_factory.py — Contextual payload construction and cache key generation.

Two focused classes with separate responsibilities:

    EmbeddingInputFactory
        Knows HOW to construct the model input text from a Claim.
        Does not know anything about caching.

    CacheKeyFactory
        Knows HOW to generate a deterministic cache key for a Claim.
        Does not know anything about text enrichment.

Separating these means:
    - Changing context enrichment strategy → only EmbeddingInputFactory changes
    - Changing cache key composition → only CacheKeyFactory changes
    - Neither class bleeds into the other's concern

CRITICAL DESIGN: The Claim itself remains UNCHANGED.
Only the MODEL INPUT is enriched. The cache key depends on content,
not on the enriched payload.

Rules:
    ✅ EmbeddingInputFactory: deterministic payload from Claim
    ✅ CacheKeyFactory: deterministic key from claim.content_hash + model + config
    ✅ Neither class performs inference or accesses the embedding model
    ✅ Neither class modifies the Claim

    ❌ Never perform inference
    ❌ Never access the embedding model
    ❌ Never modify claim.text
"""

from __future__ import annotations

import hashlib
from typing import Optional
import structlog

from smriti.core.models import Claim

logger = structlog.get_logger(__name__)


class EmbeddingInputFactory:
    """
    Constructs contextual text payloads from Claims.

    Responsibility: What text does the model receive for this Claim?

    Construction strategy:
        If claim.context is non-empty:
            payload = f"{claim.context}\\n{claim.text}"
        Else:
            payload = claim.text

        With optional instruction prefix (for BGE, Instructor, E5):
            payload = f"{instruction_prefix}{payload}"

    Instantiate once per pipeline run.
    """

    def __init__(self, instruction_prefix: Optional[str] = None) -> None:
        self._instruction_prefix = instruction_prefix or ""
        logger.debug(
            "EmbeddingInputFactory initialized",
            has_instruction=bool(instruction_prefix),
        )

    def build_payload(self, claim: Claim) -> str:
        """
        Build the model-ready text payload for a Claim.

        Args:
            claim: An immutable Claim from Phase 4.

        Returns:
            Model-ready string. Never empty for valid claims.
        """
        if claim.context:
            payload = f"{claim.context}\n{claim.text}"
        else:
            payload = claim.text

        if self._instruction_prefix:
            payload = f"{self._instruction_prefix}{payload}"

        return payload


class CacheKeyFactory:
    """
    Constructs deterministic cache keys for Claims.

    Responsibility: What is the stable identity of this Claim's embedding?

    Cache key components:
        - claim.content_hash: content identity of the claim text
        - model_signature:    which model is producing the embedding
        - config_hash:        normalization mode, instruction prefix, etc.

    If ANY component changes, the key changes → embedding regenerated.
    This factory is intentionally separate from EmbeddingInputFactory
    so that changing payload enrichment strategy doesn't break cache keys.

    Instantiate once per pipeline run (after model + config are resolved).
    """

    def __init__(self, model_signature: str, config_hash: str) -> None:
        self._model_signature = model_signature
        self._config_hash = config_hash
        logger.debug(
            "CacheKeyFactory initialized",
            model_sig_prefix=model_signature[:8],
            config_hash_prefix=config_hash[:8],
        )

    def build_cache_key(self, claim: Claim) -> str:
        """
        Build a deterministic cache key for a Claim's embedding.

        Returns:
            32-character lowercase hex string.
        """
        if not hasattr(claim, "content_hash") or not claim.content_hash:
            # Fallback: compute hash from text content
            text_hash = hashlib.sha256(claim.text.encode("utf-8")).hexdigest()[:16]
        else:
            text_hash = claim.content_hash

        material = f"{text_hash}:{self._model_signature}:{self._config_hash}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]