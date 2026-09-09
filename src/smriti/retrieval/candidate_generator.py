"""
candidate_generator.py — Exact FAISS-based candidate retrieval for Phase 6.

Responsibility:
    Given an EmbeddingIndex, retrieve candidate pairs worth evaluating.

    Two-stage filter:
        Stage 1 (exact retrieval): Find top-K nearest neighbors via FAISS's
            flat inner-product index (brute-force exact search, not approximate)
        Stage 2 (threshold): Keep only pairs above cosine_threshold

    Symmetric pair elimination:
        (claim_a, claim_b) and (claim_b, claim_a) → one canonical pair.
        Keep only the pair where claim_id_a < claim_id_b (lexicographic).

    Retrieval provenance is attached to every CandidatePair so
    debugging and replay are possible without re-running the pipeline.

Input:  List[EmbeddedClaim] + EmbeddingIndex
Output: List[CandidatePair]  (lifecycle: CANDIDATE)

Rules:
    ✅ Deterministic ordering (sort by pair_key after collection)
    ✅ Symmetric pair deduplication (pair_key canonicalization)
    ✅ Self-comparison elimination
    ✅ Configurable K and cosine threshold
    ✅ RetrievalSearchParameters attached to every pair (provenance)
    ✅ RetrievalQuality attached to every pair

    ❌ Never performs NLI inference
    ❌ Never modifies EmbeddedClaim objects
    ❌ Never builds Relationship objects
"""

from __future__ import annotations

from typing import List, Dict, Set
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    CandidatePair, EmbeddedClaim, LifecycleStage,
    RetrievalSearchParameters, RetrievalQuality,
)
from smriti.retrieval.index import EmbeddingIndex
from smriti.retrieval.faiss_index import RETRIEVAL_BACKEND, INDEX_VERSION

logger = structlog.get_logger(__name__)

# Threshold for "high density region" — if a claim has >N neighbors above threshold
_HIGH_DENSITY_THRESHOLD = 20
# Threshold for "isolated claim" — if a claim has 0 or 1 neighbors above threshold
_ISOLATED_THRESHOLD = 1


class CandidateGenerator:
    """
    Generates candidate pairs for NLI classification via exact
    cosine-similarity retrieval using FAISS IndexFlatIP.
    Instantiate once per pipeline run.
    """

    def __init__(self) -> None:
        config = get_config()
        retrieval_cfg = config.get("relationship_discovery", {})
        self._top_k: int = retrieval_cfg.get("top_k", 50)
        self._sim_threshold: float = retrieval_cfg.get("sim_threshold", 0.75)

    def generate(
        self,
        embedded_claims: List[EmbeddedClaim],
        index: EmbeddingIndex,
    ) -> List[CandidatePair]:
        """
        Generate candidate pairs via exact cosine-similarity retrieval
        (FAISS IndexFlatIP).

        Args:
            embedded_claims: All EmbeddedClaims from Phase 5.
            index:           Pre-built vector index.

        Returns:
            Deduplicated, sorted list of CandidatePair (lifecycle: CANDIDATE).
        """
        if not embedded_claims:
            return []

        search_parameters = RetrievalSearchParameters(
            top_k=self._top_k,
            sim_threshold=self._sim_threshold,
            index_type=RETRIEVAL_BACKEND,
            index_version=INDEX_VERSION,
        )

        # Track neighbor counts for retrieval quality assessment
        neighbor_counts: Dict[str, int] = {}
        seen_pair_keys: Set[str] = set()
        candidates: List[CandidatePair] = []

        for embedded_claim in embedded_claims:
            claim_id = embedded_claim.claim_id
            query_vector = list(embedded_claim.values)

            search_results = index.search(
                query_id=claim_id,
                query_vector=query_vector,
                k=self._top_k,
            )

            above_threshold = [r for r in search_results if r.score >= self._sim_threshold]
            neighbor_counts[claim_id] = len(above_threshold)

            for result in above_threshold:
                neighbor_id = result.claim_id

                # A claim is never its own candidate pair (e.g. an index that
                # returns the query itself as its own nearest neighbor).
                if neighbor_id == claim_id:
                    continue

                id_a, id_b = sorted([claim_id, neighbor_id])
                pair_key = f"{id_a}:{id_b}"

                if pair_key in seen_pair_keys:
                    continue
                seen_pair_keys.add(pair_key)

                candidates.append(CandidatePair(
                    claim_id_a=id_a,
                    claim_id_b=id_b,
                    cosine_similarity=result.score,
                    candidate_rank=result.rank,
                    retrieval_backend=RETRIEVAL_BACKEND,
                    index_version=INDEX_VERSION,
                    search_parameters=search_parameters,
                    retrieval_quality=None,   # Populated below after neighbor counts known
                    lifecycle_stage=LifecycleStage.CANDIDATE,
                ))

        # Now attach RetrievalQuality (requires neighbor counts for both claims)
        candidates_with_quality = []
        for pair in candidates:
            count_a = neighbor_counts.get(pair.claim_id_a, 0)
            count_b = neighbor_counts.get(pair.claim_id_b, 0)
            quality = RetrievalQuality(
                exact_match=False,   # Text-level duplicate check done in validator
                duplicate_removed=False,
                below_threshold=False,
                high_density_region=(
                    count_a > _HIGH_DENSITY_THRESHOLD or count_b > _HIGH_DENSITY_THRESHOLD
                ),
                isolated_claim=(
                    count_a <= _ISOLATED_THRESHOLD or count_b <= _ISOLATED_THRESHOLD
                ),
            )
            # Rebuild with quality (frozen dataclass — must reconstruct)
            candidates_with_quality.append(CandidatePair(
                claim_id_a=pair.claim_id_a,
                claim_id_b=pair.claim_id_b,
                cosine_similarity=pair.cosine_similarity,
                candidate_rank=pair.candidate_rank,
                retrieval_backend=pair.retrieval_backend,
                index_version=pair.index_version,
                search_parameters=pair.search_parameters,
                retrieval_quality=quality,
                lifecycle_stage=LifecycleStage.CANDIDATE,
            ))

        candidates_with_quality.sort(key=lambda c: c.pair_key())

        logger.info(
            "candidate generation complete",
            total_embedded=len(embedded_claims),
            candidates_found=len(candidates_with_quality),
            top_k=self._top_k,
            threshold=self._sim_threshold,
        )

        return candidates_with_quality