"""Baseline 2: spaCy-tokenized TF-IDF + cosine similarity relationship
baseline.

Claim texts are tokenized with spaCy (tokenization only -- no dependency
parse, no NER, no lemmatizer, no SVO structure) and vectorized with
scikit-learn's ``TfidfVectorizer``. Pairwise cosine similarity at/above a
threshold is treated as a candidate relationship; SUPPORTS vs. CONTRADICTS
vs. NEUTRAL is then decided by the shared naive heuristic in
``relation_heuristics.py``.

This baseline is self-contained: it takes a list of claim dicts
(``claim_id`` + ``text``) and returns plain dict predictions. It does not
depend on SMRITI's Phase 4/6 dataclasses or candidate-generation pipeline.
"""

from __future__ import annotations

from typing import Any

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from smriti.baselines.relation_heuristics import build_relationship_predictions

_NLP = None


def _get_tokenizer_pipeline():
    """Load spaCy with everything but the tokenizer disabled. Loaded lazily
    and cached at module level so repeated calls don't reload the model.
    """
    global _NLP
    if _NLP is None:
        _NLP = spacy.load(
            "en_core_web_sm",
            disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"],
        )
    return _NLP


def _spacy_tokenize_all(texts: list[str]) -> list[list[str]]:
    """Batch-tokenize with spaCy's nlp.pipe for speed; returns lowercase
    tokens with whitespace/punctuation dropped. Pure tokenization, no other
    linguistic signal.
    """
    nlp = _get_tokenizer_pipeline()
    tokenized: list[list[str]] = []
    for doc in nlp.pipe(texts):
        tokenized.append([tok.text.lower() for tok in doc if not tok.is_space and not tok.is_punct])
    return tokenized


def predict_relationships_tfidf(
    claims: list[dict[str, Any]],
    *,
    candidate_threshold: float = 0.20,
    support_threshold: float = 0.55,
) -> list[dict[str, Any]]:
    """Predict SUPPORTS/CONTRADICTS/NEUTRAL relationships for all claim
    pairs whose TF-IDF cosine similarity is at/above ``candidate_threshold``.

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

    tokenized_texts = _spacy_tokenize_all(texts)
    # TfidfVectorizer normally tokenizes raw strings itself; since spaCy
    # already produced token lists above, pass them straight through with
    # an identity analyzer instead of re-tokenizing with a regex.
    vectorizer = TfidfVectorizer(analyzer=lambda tokens: tokens)
    tfidf_matrix = vectorizer.fit_transform(tokenized_texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    return build_relationship_predictions(
        claim_ids,
        texts,
        similarity_matrix,
        candidate_threshold=candidate_threshold,
        support_threshold=support_threshold,
        method="tfidf_cosine_baseline",
    )
