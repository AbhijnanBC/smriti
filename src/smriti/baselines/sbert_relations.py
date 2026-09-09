"""Baseline 3: Sentence-BERT (all-MiniLM-L6-v2) + cosine similarity
relationship baseline.

Identical candidate-generation and SUPPORTS/CONTRADICTS/NEUTRAL heuristic to
``tfidf_relations.py`` (both delegate to ``relation_heuristics.py``) -- the
only difference is that claims are embedded with a small pretrained
sentence-transformer instead of a TF-IDF bag-of-words vector. That isolates
"does a better embedding help" as a variable, independent of SMRITI's own
NLI-based relationship classifier (Phase 6).

Uses the locally-cached ``sentence-transformers/all-MiniLM-L6-v2`` model, so
it runs fully offline once the model has been downloaded once.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from smriti.baselines.relation_heuristics import build_relationship_predictions

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Load the sentence-transformer lazily and cache it at module level so
    repeated calls within one process don't reload the model from disk.
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def predict_relationships_sbert(
    claims: list[dict[str, Any]],
    *,
    candidate_threshold: float = 0.45,
    support_threshold: float = 0.75,
) -> list[dict[str, Any]]:
    """Predict SUPPORTS/CONTRADICTS/NEUTRAL relationships for all claim
    pairs whose Sentence-BERT cosine similarity is at/above
    ``candidate_threshold``.

    Parameters
    ----------
    claims:
        List of dicts, each with at least ``claim_id`` and ``text``.
    candidate_threshold:
        Minimum cosine similarity for a pair to be considered a
        relationship candidate at all.
    support_threshold:
        Minimum cosine similarity (with matching negation polarity) to be
        labeled SUPPORTS rather than NEUTRAL.

    Returns
    -------
    List of dicts: ``claim_id_a``, ``claim_id_b``, ``relationship_type``,
    ``similarity``, ``method``.
    """
    claim_ids = [c["claim_id"] for c in claims]
    texts = [c["text"] for c in claims]

    model = _get_model()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    similarity_matrix = np.asarray(embeddings) @ np.asarray(embeddings).T

    return build_relationship_predictions(
        claim_ids,
        texts,
        similarity_matrix,
        candidate_threshold=candidate_threshold,
        support_threshold=support_threshold,
        method="sbert_cosine_baseline",
    )
