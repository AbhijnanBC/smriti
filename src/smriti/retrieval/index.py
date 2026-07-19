

"""
index.py — Abstract vector index interface for Phase 6.

Responsibility:
    Define the contract that all vector index implementations must satisfy.
    The rest of Phase 6 depends ONLY on this interface, never on FAISS directly.
    This allows FAISS to be replaced with HNSW, Annoy, ScaNN, or any future
    ANN backend without changing any other Phase 6 code.

Public interface:
    EmbeddingIndex.add(claim_ids, vectors) → None
    EmbeddingIndex.search(query_id, k)     → List[SearchResult]
    EmbeddingIndex.dimension               → int
    EmbeddingIndex.size                    → int

Rules:
    ✅ Returns plain Python types only (no numpy, no tensors)
    ✅ Every implementation is interchangeable
    ❌ Never performs NLI inference
    ❌ Never constructs Relationship objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SearchResult:
    """A single ANN search result."""
    claim_id: str
    score: float         # Cosine similarity (dot product on L2-normalized vectors)
    rank: int            # 1 = nearest neighbor


class EmbeddingIndex(ABC):
    """
    Abstract vector index for ANN (Approximate Nearest Neighbor) search.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension expected by this index."""
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        """Number of vectors currently in the index."""
        ...

    @abstractmethod
    def add(self, claim_ids: List[str], vectors: List[List[float]]) -> None:
        """
        Add vectors to the index.

        Args:
            claim_ids: Identifiers for each vector.
            vectors:   L2-normalized float lists (len == dimension each).

        Raises:
            IndexBuildError: If vectors cannot be added.
        """
        ...

    @abstractmethod
    def search(
        self,
        query_id: str,
        query_vector: List[float],
        k: int,
        exclude_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Find the K nearest neighbors of query_vector.

        Args:
            query_id:     The claim_id of the query (to exclude from results).
            query_vector: L2-normalized float list.
            k:            Maximum neighbors to return.
            exclude_ids:  Additional IDs to exclude from results.

        Returns:
            List of SearchResult, sorted by score (highest first).
            Never includes query_id itself.
        """
        ...