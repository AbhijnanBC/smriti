"""
cache.py — Embedding cache policy for Phase 5.

Responsibility:
    Manage when embeddings should be reused vs regenerated.
    Separate cache POLICY from cache PERSISTENCE.

    Policy (here):   "Should this embedding be reused?"
    Persistence:     core/cache.py CacheManager handles actual file I/O

Cache entry validity rules:
    An embedding cache entry is VALID if and only if:
        1. The entry exists
        2. The schema_version matches the current Phase 5 schema    ← NEW
        3. The model signature matches the current model
        4. The config hash matches the current configuration

    If ANY condition fails → STALE → regenerate.

    Schema version check comes FIRST because a schema mismatch means
    the entry might not even deserialize correctly with newer code.

Cache key:
    SHA256(claim.content_hash : model_signature : config_hash)[:32]

Notes:
    - Cache stores vectors as List[float] (Python native, portable)
    - Cache never stores framework tensors
    - Stale entries are overwritten (not deleted first)
    - All stored vectors are assumed to be already normalized
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.paths import EMBEDDINGS_CACHE_DIR
from smriti.embedding.models import EmbeddingStatus

logger = structlog.get_logger(__name__)

# Must match PHASE5_SCHEMA_VERSION in embedder.py
# Increment this constant whenever the cache entry format changes
CACHE_SCHEMA_VERSION = "5.0"


class EmbeddingCachePolicy:
    """
    Manages embedding cache reads and writes.

    Storage format: one .pkl file per cache key.
    File content:
        {
            "vector":         [float, ...],
            "model_sig":      str,
            "config_hash":    str,
            "schema_version": str,     ← validates format compatibility
        }
    """

    def __init__(
        self,
        cache_dir: Path = EMBEDDINGS_CACHE_DIR,
        enabled: bool = True,
    ) -> None:
        self._cache_dir = Path(cache_dir)
        self._enabled = enabled

        if self._enabled:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def lookup(
        self,
        cache_key: str,
        model_signature: str,
        config_hash: str,
    ) -> Tuple[EmbeddingStatus, Optional[List[float]]]:
        """
        Look up a vector in the cache.

        Validation order:
            1. schema_version — format compatibility (checked first)
            2. model_signature — model identity
            3. config_hash — pipeline configuration

        Returns:
            (EmbeddingStatus.CACHED, vector) if fully valid hit
            (EmbeddingStatus.STALE, None)   if any condition fails
            (EmbeddingStatus.FAILED, None)  if key not found or cache disabled
        """
        if not self._enabled:
            return EmbeddingStatus.FAILED, None

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return EmbeddingStatus.FAILED, None

        try:
            with open(cache_file, "rb") as f:
                entry = pickle.load(f)

            # Check 1: Schema version — catches incompatible cache format changes
            if entry.get("schema_version") != CACHE_SCHEMA_VERSION:
                logger.debug(
                    "cache schema mismatch — stale",
                    cache_key=cache_key[:8],
                    stored=entry.get("schema_version"),
                    expected=CACHE_SCHEMA_VERSION,
                )
                return EmbeddingStatus.STALE, None

            # Check 2 + 3: Model identity and configuration
            if (entry.get("model_sig") != model_signature or
                    entry.get("config_hash") != config_hash):
                logger.debug(
                    "cache model/config mismatch — stale",
                    cache_key=cache_key[:8],
                )
                return EmbeddingStatus.STALE, None

            vector = entry.get("vector")
            if vector is None:
                return EmbeddingStatus.FAILED, None

            logger.debug("cache hit", cache_key=cache_key[:8])
            return EmbeddingStatus.CACHED, vector

        except Exception as e:
            logger.warning("cache read failed", cache_key=cache_key[:8], error=str(e))
            return EmbeddingStatus.FAILED, None

    def store(
        self,
        cache_key: str,
        vector: List[float],
        model_signature: str,
        config_hash: str,
    ) -> bool:
        """
        Store a normalized vector in the cache.

        Returns:
            True if stored successfully, False on error.
        """
        if not self._enabled:
            return False

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        try:
            entry = {
                "vector":         vector,
                "model_sig":      model_signature,
                "config_hash":    config_hash,
                "schema_version": CACHE_SCHEMA_VERSION,   # Always write current version
            }
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
            logger.debug("cache stored", cache_key=cache_key[:8])
            return True
        except Exception as e:
            logger.warning("cache write failed", cache_key=cache_key[:8], error=str(e))
            return False

    def invalidate(self, cache_key: str) -> bool:
        """
        Remove a specific cache entry.

        Returns:
            True if file existed and was removed.
        """
        cache_file = self._cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
            logger.debug("cache invalidated", cache_key=cache_key[:8])
            return True
        return False

    def clear_all(self) -> int:
        """Clear all cached embeddings. Returns count of files removed."""
        if not self._cache_dir.exists():
            return 0
        count = 0
        for f in self._cache_dir.glob("*.pkl"):
            f.unlink()
            count += 1
        logger.info("embedding cache cleared", files_removed=count)
        return count