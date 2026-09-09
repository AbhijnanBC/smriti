"""
benchmark.py — Phase 6 INFRASTRUCTURE regression suite (not a semantic benchmark).

Provides:
    SyntheticVectorCorpus: Deterministic dataset for regression testing, built from
                            vectors with known GEOMETRIC relationships (opposite-sign,
                            near-identical, perturbed, orthogonal), not real language.
    BenchmarkSuite:         Evaluates Recall@K, Precision, latency, and relationship
                            density of the retrieval/graph MACHINERY against those
                            geometrically-constructed gold labels.

What this suite actually validates:
    - Vector index correctness (dimensions, insertion, lookup)
    - Deterministic retrieval and top-k / candidate-generation behavior
    - Whether the graph-building and relationship-resolution mechanics respond
      correctly to embeddings with known, constructed geometric relationships
      (e.g. does a pair of exactly opposite-sign vectors get flagged as a
      candidate; does the pipeline plumbing/latency scale sanely with corpus size)

What this suite does NOT validate:
    - Semantic contradiction / support / refinement understanding. The claim
      TEXT in SyntheticVectorCorpus is arbitrary template text (e.g. "Synthetic
      claim 17 about topic 7.") with no real semantic content. The gold labels
      are manufactured by directly manipulating embedding vectors (e.g. for
      CONTRADICTS, `embeddings_dict[id_b] = [-v for v in embeddings_dict[id_a]]`),
      not derived from any language-understanding process. A "pass" here proves
      the MACHINERY reacts correctly to known vector geometry — it proves
      nothing about SMRITI's NLI/semantic accuracy on real language.

    ⚠️  WARNING: Do not cite results from this suite as evidence of SMRITI's
    semantic/NLI accuracy in the paper or in Phase 12 experiments — see the
    real evaluation in evaluation/annotation/ for that.

Rules:
    ✅ SyntheticVectorCorpus is fully deterministic (seeded random)
    ✅ BenchmarkSuite never modifies pipeline objects
    ✅ All metrics are computed against a gold-standard label set built on vector geometry
    ❌ Never used in production pipeline runs
    ❌ Never cited as semantic/scientific evidence (infrastructure test only)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
import structlog

from smriti.core.models import RelationshipType

logger = structlog.get_logger(__name__)


@dataclass
class GoldPair:
    """A gold-standard relationship label for evaluation."""
    claim_id_a: str
    claim_id_b: str
    expected_type: RelationshipType


@dataclass
class SyntheticVectorCorpus:
    """
    Deterministic dataset for Phase 6 INFRASTRUCTURE regression testing.

    IMPORTANT: The claim text is arbitrary synthetic template text with no
    real semantic content. Gold labels are manufactured by directly
    constructing embedding vectors with known GEOMETRIC relationships
    (opposite-sign, near-identical, perturbed, orthogonal) — not by any
    process of language understanding. This corpus is suitable for testing
    retrieval/graph mechanics (indexing, top-k, latency scaling) but must
    never be cited as evidence of semantic contradiction/support/refinement
    understanding. See the module docstring for details.

    Usage:
        corpus = SyntheticVectorCorpus.generate(seed=42, n_claims=100, n_gold_pairs=50)
        # Use corpus.claims, corpus.embeddings, corpus.gold_labels in tests
    """
    claims: List[Dict]                          # {claim_id, text}
    embeddings: List[Tuple[str, List[float]]]   # (claim_id, vector)
    gold_labels: List[GoldPair]
    dimension: int
    seed: int

    @classmethod
    def generate(
        cls,
        seed: int = 42,
        n_claims: int = 100,
        n_gold_pairs: int = 50,
        dimension: int = 8,
    ) -> "SyntheticVectorCorpus":
        """
        Generate a deterministic synthetic corpus.

        All gold pairs are created by deterministically constructing
        claim pairs that should have known relationship types:
            - CONTRADICTS: opposite-sign vectors
            - SUPPORTS:    nearly identical vectors
            - REFINES:     high cosine but slight offset
            - NEUTRAL:     orthogonal vectors
        """
        rng = random.Random(seed)

        # Generate claim texts (templates for determinism)
        claim_texts = [
            (f"c{i:04d}", f"Synthetic claim {i} about topic {i % 10}.")
            for i in range(n_claims)
        ]
        claims = [{"claim_id": cid, "text": text} for cid, text in claim_texts]

        # Generate random L2-normalized embeddings
        def rand_vector() -> List[float]:
            vec = [rng.gauss(0, 1) for _ in range(dimension)]
            norm = math.sqrt(sum(v ** 2 for v in vec))
            return [v / max(norm, 1e-9) for v in vec]

        embeddings_dict: Dict[str, List[float]] = {
            cid: rand_vector() for cid, _ in claim_texts
        }

        # Create gold pairs with controlled relationship types
        gold_labels: List[GoldPair] = []
        claim_ids = [cid for cid, _ in claim_texts]
        pairs_created: Set[str] = set()

        for i in range(n_gold_pairs):
            idx_a = rng.randint(0, n_claims - 1)
            idx_b = rng.randint(0, n_claims - 1)
            if idx_a == idx_b:
                continue

            id_a, id_b = sorted([claim_ids[idx_a], claim_ids[idx_b]])
            pair_key = f"{id_a}:{id_b}"
            if pair_key in pairs_created:
                continue
            pairs_created.add(pair_key)

            # Assign relationship type and adjust embeddings accordingly
            rel_type_idx = i % 4
            if rel_type_idx == 0:
                rel_type = RelationshipType.CONTRADICTS
                embeddings_dict[id_b] = [-v for v in embeddings_dict[id_a]]
            elif rel_type_idx == 1:
                rel_type = RelationshipType.SUPPORTS
                noise = [rng.gauss(0, 0.01) for _ in range(dimension)]
                vec = [v + n for v, n in zip(embeddings_dict[id_a], noise)]
                norm = math.sqrt(sum(v ** 2 for v in vec))
                embeddings_dict[id_b] = [v / max(norm, 1e-9) for v in vec]
            elif rel_type_idx == 2:
                rel_type = RelationshipType.REFINES
                noise = [rng.gauss(0, 0.1) for _ in range(dimension)]
                vec = [v + n for v, n in zip(embeddings_dict[id_a], noise)]
                norm = math.sqrt(sum(v ** 2 for v in vec))
                embeddings_dict[id_b] = [v / max(norm, 1e-9) for v in vec]
            else:
                rel_type = RelationshipType.NEUTRAL

            gold_labels.append(GoldPair(
                claim_id_a=id_a, claim_id_b=id_b, expected_type=rel_type,
            ))

        embeddings = list(embeddings_dict.items())

        logger.info(
            "synthetic corpus generated",
            seed=seed, n_claims=n_claims,
            n_gold_pairs=len(gold_labels),
        )

        return cls(
            claims=claims,
            embeddings=embeddings,
            gold_labels=gold_labels,
            dimension=dimension,
            seed=seed,
        )


@dataclass
class BenchmarkResult:
    """Results of running BenchmarkSuite."""
    recall_at_k: float                          # Fraction of gold pairs retrieved
    precision: float                            # Fraction of retrieved pairs that are gold
    relationship_density: float                 # relationships / claims
    nli_latency_ms_per_pair: float
    retrieval_latency_ms_per_claim: float
    memory_mb: float
    by_type: Dict[str, Dict[str, float]]        # {type: {precision, recall}}


class BenchmarkSuite:
    """
    Evaluates Phase 6 retrieval/graph MACHINERY against a gold-standard
    corpus built from vectors with known geometric relationships.

    This validates infrastructure mechanics, not semantic understanding —
    see the module docstring for the full scope/limitations statement.

    Usage:
        corpus = SyntheticVectorCorpus.generate(seed=42)
        suite = BenchmarkSuite(corpus)
        result = suite.evaluate(relationship_set, retrieval_latency, nli_latency)
    """

    def __init__(self, corpus: SyntheticVectorCorpus) -> None:
        self._corpus = corpus
        self._gold_by_pair: Dict[str, RelationshipType] = {
            f"{g.claim_id_a}:{g.claim_id_b}": g.expected_type
            for g in corpus.gold_labels
        }

    def evaluate(
        self,
        relationship_set,
        retrieval_latency_seconds: float,
        nli_latency_seconds: float,
        memory_mb: float = 0.0,
    ) -> BenchmarkResult:
        """Evaluate a RelationshipSet against the gold labels."""
        gold_keys = set(self._gold_by_pair.keys())
        predicted_keys = {
            rel.evidence.pair.pair_key()
            for rel in relationship_set.relationships
        }

        retrieved_gold = gold_keys & predicted_keys
        recall_at_k = len(retrieved_gold) / max(len(gold_keys), 1)
        precision = len(retrieved_gold) / max(len(predicted_keys), 1)

        # n_claims is the ACTUAL number of claims in the synthetic corpus —
        # never a proxy for it (e.g. the RNG seed is not a claim count).
        n_claims = len(self._corpus.claims)
        relationship_density = relationship_set.total_relationships / max(n_claims, 1)

        # total_validated = number of candidate pairs that passed pre-NLI
        # similarity validation and were then fed to NLI (see
        # retrieval/__init__.py: `valid_candidates` -> `generate_batch(pairs=valid_candidates, ...)`).
        # It is genuinely a pair count, so it is the correct denominator here.
        nli_count = max(relationship_set.total_validated, 1)
        nli_latency_ms = (nli_latency_seconds / nli_count) * 1000.0

        # retrieval_latency_ms_per_claim must be divided by the number of
        # claims that were embedded/retrieved against — NOT by the number of
        # candidate PAIRS (relationship_set.total_candidates), which is a
        # different, much larger quantity and silently mislabels the metric.
        retrieval_latency_ms = (retrieval_latency_seconds / max(n_claims, 1)) * 1000.0

        # Per-type breakdown
        by_type: Dict[str, Dict[str, float]] = {}
        for rel_type in RelationshipType:
            gold_of_type = {
                k for k, v in self._gold_by_pair.items()
                if v == rel_type
            }
            predicted_of_type = {
                rel.evidence.pair.pair_key()
                for rel in relationship_set.relationships
                if rel.relationship_type == rel_type
            }
            tp = len(gold_of_type & predicted_of_type)
            p = tp / max(len(predicted_of_type), 1)
            r = tp / max(len(gold_of_type), 1)
            by_type[rel_type.value] = {"precision": p, "recall": r, "tp": tp}

        return BenchmarkResult(
            recall_at_k=recall_at_k,
            precision=precision,
            relationship_density=relationship_density,
            nli_latency_ms_per_pair=nli_latency_ms,
            retrieval_latency_ms_per_claim=retrieval_latency_ms,
            memory_mb=memory_mb,
            by_type=by_type,
        )