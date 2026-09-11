"""
classification/relatedness.py — Lightweight topical-relatedness gate (P0-6).

Problem being addressed:
    Phase 6's candidate generation admits any pair above a cosine-similarity
    threshold. Embedding-space proximity does not guarantee topical
    relatedness at the tail of the similarity distribution — two claims
    from entirely unrelated domains (e.g. a robotics claim and a cricket
    claim) can score above the cosine threshold while sharing no real
    subject matter. An off-the-shelf NLI model given such a pair has no
    reliable signal to fall back on and, empirically, over-predicts
    CONTRADICTS on exactly this population (measured false-positive rate:
    11/11 = 100% on a held-out spurious cross-domain sample; see the paper's
    error analysis).

    This module does NOT replace NLI, and does NOT filter every relation
    type — SUPPORTS/REFINES/NEUTRAL decisions are left untouched, since
    over-gating there would cost recall without addressing the actual
    failure mode. It gates ONLY the CONTRADICTS decision: you cannot
    contradict a claim you are not even talking about, so a CONTRADICTS
    verdict additionally requires some minimum topical overlap between the
    two claims. Pairs that fail the gate are downgraded to UNKNOWN, which
    Phase 6's existing validator already drops before Phase 7 (see
    RelationshipType.UNKNOWN's docstring: "never persist").

Design:
    Deliberately cheap and model-free (consistent with resolver.py's own
    "never calls any ML model" rule) — plain-text tokenization plus a
    stopword list, no spaCy pipeline load, no extra NLI calls. This is a
    coarse heuristic gate, not a relatedness classifier; its only job is
    to catch the "these two claims share literally no vocabulary or named
    entity" case that off-the-shelf NLI handles worst.
"""

from __future__ import annotations

import re

STOP_WORDS: frozenset[str] | set[str]
try:
    from spacy.lang.en.stop_words import STOP_WORDS
except ImportError:  # pragma: no cover - spaCy is a hard dependency elsewhere
    STOP_WORDS = frozenset()

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_MIN_TOKEN_LEN = 3

RELATEDNESS_VERSION = "1.0"


def _content_tokens(text: str) -> frozenset[str]:
    """Lowercased non-stopword tokens of length > _MIN_TOKEN_LEN."""
    tokens = _TOKEN_RE.findall(text.lower())
    return frozenset(t for t in tokens if len(t) > _MIN_TOKEN_LEN and t not in STOP_WORDS)


def _capitalized_words(text: str) -> frozenset[str]:
    """Capitalized tokens (cheap proxy for named entities — no NER model)."""
    return frozenset(
        t for t in _TOKEN_RE.findall(text) if t[:1].isupper() and t.lower() not in STOP_WORDS
    )


def compute_relatedness(text_a: str, text_b: str) -> float:
    """
    Jaccard overlap of content tokens, unioned with a small bonus for any
    shared capitalized word (proxy named-entity match). Returns a value in
    [0, 1]; 0.0 means no detectable shared vocabulary or entities at all.
    """
    tokens_a, tokens_b = _content_tokens(text_a), _content_tokens(text_b)
    if not tokens_a or not tokens_b:
        jaccard = 0.0
    else:
        inter = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        jaccard = inter / union if union else 0.0

    caps_a, caps_b = _capitalized_words(text_a), _capitalized_words(text_b)
    shared_entities = len(caps_a & caps_b)

    if shared_entities > 0:
        # Any shared proper noun / entity-like token is a strong relatedness
        # signal on its own, even if the surrounding vocabulary differs.
        return max(jaccard, 0.5)
    return jaccard


def passes_contradiction_relatedness_gate(
    text_a: str,
    text_b: str,
    min_relatedness: float,
) -> bool:
    """True iff (text_a, text_b) share enough vocabulary/entities to make a
    CONTRADICTS verdict between them meaningful."""
    return compute_relatedness(text_a, text_b) >= min_relatedness
