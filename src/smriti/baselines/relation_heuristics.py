"""Shared naive classification heuristic for the two similarity-based
relationship baselines (``tfidf_relations.py`` and ``sbert_relations.py``).

Both baselines only differ in *how* they turn claim text into vectors --
TF-IDF bag-of-words vs. a pretrained sentence embedding. Once either one has
produced a dense pairwise cosine-similarity matrix, the candidate selection
and SUPPORTS/CONTRADICTS/NEUTRAL labeling logic here is identical, so the
only variable being compared between the two baselines is the embedding
method itself.

This is intentionally the weakest possible classifier: no dependency
parsing, no entailment model, no scope resolution for negation -- just
similarity-band thresholds plus a surface negation-cue-word mismatch check.
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np

# A small, fixed list of negation/contrast cue words and contractions.
# Presence/absence of these is the *entire* "semantic" signal this baseline
# uses beyond raw similarity.
NEGATION_CUES = {
    "not",
    "no",
    "never",
    "none",
    "nobody",
    "nothing",
    "neither",
    "nor",
    "cannot",
    "can't",
    "won't",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "doesn't",
    "don't",
    "didn't",
    "hasn't",
    "haven't",
    "hadn't",
    "shouldn't",
    "wouldn't",
    "couldn't",
    "without",
    "lacks",
    "lacking",
    "fails",
    "failed",
    "unable",
    "incorrect",
    "false",
    "wrong",
}

_WORD_RE = re.compile(r"[A-Za-z']+")


def _has_negation_cue(text: str) -> bool:
    tokens = {m.group(0).lower() for m in _WORD_RE.finditer(text)}
    return bool(tokens & NEGATION_CUES)


def classify_pair(
    text_a: str,
    text_b: str,
    similarity: float,
    *,
    support_threshold: float,
    candidate_threshold: float,
) -> str:
    """Classify one claim pair into SUPPORTS / CONTRADICTS / NEUTRAL.

    Rule (checked in order):
    1. If exactly one of the two texts contains a negation cue word (the
       other doesn't), and they are at least similar enough to be a
       candidate pair at all, call it CONTRADICTS. This is a crude proxy
       for "same topic, opposite polarity".
    2. Otherwise, if similarity is at/above ``support_threshold``, call it
       SUPPORTS (same topic, matching polarity, high overlap).
    3. Otherwise it's a candidate pair that's neither confidently
       supportive nor contradictory: NEUTRAL.
    """
    neg_a = _has_negation_cue(text_a)
    neg_b = _has_negation_cue(text_b)

    if neg_a != neg_b and similarity >= candidate_threshold:
        return "CONTRADICTS"

    if similarity >= support_threshold:
        return "SUPPORTS"

    return "NEUTRAL"


def build_relationship_predictions(
    claim_ids: list[str],
    texts: list[str],
    similarity_matrix: np.ndarray,
    *,
    candidate_threshold: float,
    support_threshold: float,
    method: str,
) -> list[dict[str, Any]]:
    """Turn a dense pairwise similarity matrix into relationship predictions
    for every unordered pair at/above ``candidate_threshold``.

    Returns a list of plain dicts with keys: ``claim_id_a``, ``claim_id_b``,
    ``relationship_type``, ``similarity``, ``method``.
    """
    n = len(claim_ids)
    predictions: list[dict[str, Any]] = []
    for i in range(n):
        row = similarity_matrix[i]
        for j in range(i + 1, n):
            sim = float(row[j])
            if sim < candidate_threshold:
                continue
            label = classify_pair(
                texts[i],
                texts[j],
                sim,
                support_threshold=support_threshold,
                candidate_threshold=candidate_threshold,
            )
            predictions.append(
                {
                    "claim_id_a": claim_ids[i],
                    "claim_id_b": claim_ids[j],
                    "relationship_type": label,
                    "similarity": sim,
                    "method": method,
                }
            )
    return predictions
