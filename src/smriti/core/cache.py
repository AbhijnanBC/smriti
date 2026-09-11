"""
Cache manager for expensive computations.

Cache layout (all under project root cache/):
  cache/
    embeddings/   ← Phase 4: embedding vectors
    parsed/       ← Phase 2: parsed document structures
    retrieval/    ← Phase 5: FAISS index
    nli/          ← Phase 6: NLI predictions

CONTRACT: Everything under cache/ is ephemeral.
Safe to delete at any time with: .\\Makefile.ps1 clean-cache
"""

import pickle
from pathlib import Path
from typing import Any

import structlog

from smriti.core.paths import (
    EMBEDDINGS_CACHE_DIR,
    NLI_CACHE_DIR,
)

logger = structlog.get_logger(__name__)


class CacheManager:
    """
    Namespaced pickle cache for a single cache directory.
    Instantiate one per namespace: CacheManager(EMBEDDINGS_CACHE_DIR)
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Any | None:
        """Retrieve a cached object by key. Returns None on miss."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "rb") as f:
                obj = pickle.load(f)
            logger.debug("cache hit", key=key, dir=self.cache_dir.name)
            return obj
        except Exception as e:
            logger.warning("cache read failed", key=key, error=str(e))
            return None

    def set(self, key: str, obj: Any) -> None:
        """Store an object in cache."""
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(obj, f)
            logger.debug("cache write", key=key, dir=self.cache_dir.name)
        except Exception as e:
            logger.error("cache write failed", key=key, error=str(e))

    def delete(self, key: str) -> None:
        """Remove a single cache entry."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()

    def clear(self) -> None:
        """Clear this entire cache namespace."""
        import shutil

        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("cache namespace cleared", dir=self.cache_dir.name)


# ── Specialised caches ────────────────────────────────────────────────────────


class EmbeddingCache(CacheManager):
    """Cache for embedding vectors (Phase 4)."""

    def __init__(self):
        super().__init__(EMBEDDINGS_CACHE_DIR)

    def get_batch(self, claim_ids: list) -> dict[str, list]:
        """Retrieve multiple embeddings at once."""
        return {cid: v for cid in claim_ids if (v := self.get(cid)) is not None}


class NLICache(CacheManager):
    """Cache for NLI predictions (Phase 6)."""

    def __init__(self):
        super().__init__(NLI_CACHE_DIR)

    @staticmethod
    def _pair_key(claim_a_id: str, claim_b_id: str) -> str:
        """Deterministic key: (A,B) and (B,A) produce the same key."""
        a, b = sorted([claim_a_id, claim_b_id])
        return f"{a}__{b}"

    def get_pair(self, claim_a_id: str, claim_b_id: str) -> dict | None:
        return self.get(self._pair_key(claim_a_id, claim_b_id))

    def set_pair(self, claim_a_id: str, claim_b_id: str, result: dict) -> None:
        self.set(self._pair_key(claim_a_id, claim_b_id), result)
