"""
faiss_index.py — FAISS implementation of EmbeddingIndex.

This is the ONLY module in Phase 6 that imports faiss.
All other modules see only the EmbeddingIndex interface.

Rules:
    ✅ Convert numpy arrays → plain Python lists before returning
    ✅ Convert Python lists → numpy arrays before passing to FAISS
    ✅ Handle faiss not installed gracefully
    ❌ Never return numpy arrays or tensors
    ❌ Never expose FAISS types outside this module
"""

from __future__ import annotations

import structlog

from smriti.exceptions import FAISSNotAvailableError, IndexBuildError
from smriti.retrieval.index import EmbeddingIndex, SearchResult

logger = structlog.get_logger(__name__)

RETRIEVAL_BACKEND = "faiss_flat_ip"
RETRIEVAL_VERSION = "1.0"
INDEX_VERSION = "1.0"


class FAISSIndex(EmbeddingIndex):
    """
    FAISS IndexFlatIP — exact inner product search on L2-normalized vectors.
    Cosine similarity == dot product when both vectors are L2-normalized.
    """

    def __init__(self, dimension: int) -> None:
        self._dimension = dimension
        self._claim_ids: list[str] = []
        self._id_to_idx: dict[str, int] = {}
        self._index = self._create_index(dimension)

    def _create_index(self, dimension: int):
        try:
            import faiss

            index = faiss.IndexFlatIP(dimension)
            logger.info("faiss index created", dimension=dimension)
            return index
        except ImportError as e:
            raise FAISSNotAvailableError(
                f"faiss-cpu is not installed. Run: poetry add faiss-cpu\nError: {e}"
            ) from e

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def size(self) -> int:
        return len(self._claim_ids)

    def add(self, claim_ids: list[str], vectors: list[list[float]]) -> None:
        import numpy as np

        if not vectors:
            return

        for i, v in enumerate(vectors):
            if len(v) != self._dimension:
                raise IndexBuildError(
                    f"Vector at position {i} has dimension {len(v)}, " f"expected {self._dimension}"
                )

        try:
            matrix = np.array(vectors, dtype=np.float32)
            self._index.add(matrix)
            start_idx = len(self._claim_ids)
            for i, cid in enumerate(claim_ids):
                self._claim_ids.append(cid)
                self._id_to_idx[cid] = start_idx + i

            logger.info("vectors added to index", count=len(vectors), total=self.size)
        except Exception as e:
            raise IndexBuildError(f"FAISS add failed: {e}") from e

    def search(
        self,
        query_id: str,
        query_vector: list[float],
        k: int,
        exclude_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        import numpy as np

        if self.size == 0:
            return []

        excluded = {query_id}
        if exclude_ids:
            excluded.update(exclude_ids)

        k_request = min(k + len(excluded) + 1, self.size)

        try:
            query_np = np.array([query_vector], dtype=np.float32)
            scores_np, indices_np = self._index.search(query_np, k_request)
            scores = scores_np[0].tolist()
            indices = indices_np[0].tolist()
        except Exception as e:
            logger.warning("faiss search failed", query_id=query_id[:8], error=str(e))
            return []

        results = []
        rank = 1
        for score, idx in zip(scores, indices, strict=False):
            if idx < 0 or idx >= len(self._claim_ids):
                continue
            neighbor_id = self._claim_ids[idx]
            if neighbor_id in excluded:
                continue
            results.append(SearchResult(claim_id=neighbor_id, score=float(score), rank=rank))
            rank += 1
            if len(results) >= k:
                break

        return results
