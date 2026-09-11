"""
classification/specificity.py — Lightweight SUPPORTS/REFINES disambiguation.

Problem being addressed (external review, bidirectional-NLI rewrite):
    One-way entailment (X entails Y, Y does not entail X) is not on its own
    enough to decide whether X SUPPORTS Y or X REFINES Y. "Independent
    benchmarks confirm the Norwich scheduler lowers latency" entails "The
    Norwich scheduler reduces latency" -- that is confirmation (SUPPORTS).
    "Transformers outperform U-Net on benchmark X for medical segmentation"
    entails "Transformers outperform U-Net on benchmark X" -- that is
    elaboration, X (the entailing claim) adds detail Y lacks (REFINES).
    The prior resolver had a single REFINES rule keyed on high cosine
    similarity + neutral NLI verdict + low contradiction, which fires only
    when NLI does NOT detect entailment at all -- structurally unable to
    ever fire on a pair NLI correctly recognizes as one-way entailment,
    which is exactly the population where a real SUPPORTS/REFINES
    distinction matters.

Design:
    Deliberately cheap and model-free (consistent with resolver.py's own
    "never calls any ML model" rule): the entailing claim is judged more
    SPECIFIC than the entailed claim -- and therefore a REFINES rather
    than a SUPPORTS -- if it contains meaningfully more numeric detail,
    date/temporal detail, named-entity-like tokens, or sheer content-token
    volume. This is a heuristic proxy for "adds information not present
    in the other claim," not a semantic entailment-strength measure; it
    is intentionally symmetric in implementation with relatedness.py
    (same tokenizer, same "no NER model" discipline) so the two gates are
    easy to audit side by side.
"""

from __future__ import annotations

import re

STOP_WORDS: frozenset[str] | set[str]
try:
    from spacy.lang.en.stop_words import STOP_WORDS
except ImportError:  # pragma: no cover - spaCy is a hard dependency elsewhere
    STOP_WORDS = frozenset()

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_NUMERIC_RE = re.compile(r"\d+(\.\d+)?")
_YEAR_RE = re.compile(r"\b(18|19|20)\d{2}\b")
_MONTH_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.IGNORECASE,
)
_MIN_TOKEN_LEN = 3

# RECTIFIED (external "reality check" review round 3, P0-B.5 "add an
# evidence/attribution cue detector for SUPPORTS"): a claim that merely
# ATTRIBUTES the same proposition to a source ("Independent benchmarks
# confirm that X", "An internal review independently confirmed that X")
# is SUPPORTS, not REFINES -- it adds no new semantic content about X,
# only evidentiary provenance for X. Before this fix, attribution wrapper
# words counted as ordinary content tokens, so every SUPPORTS pair built
# from an attribution template (exactly the pattern
# evaluation/controlled/generators/build_controlled_v2.py's SUPPORTS
# category uses) had its specificity artificially inflated past the
# default margin and was wrongly reclassified as REFINES: empirically,
# is_refinement("Independent benchmarks confirm that the X reduces
# latency.", "The X reduces latency.", margin=3.0) returned True before
# this fix. These cue words are now excluded from the content-token count
# on BOTH sides of a pair, exactly like stopwords -- an attribution cue is
# never evidence of added specificity, regardless of which claim it
# appears in.
_ATTRIBUTION_CUES = frozenset(
    {
        "benchmark",
        "benchmarks",
        "audit",
        "audits",
        "review",
        "reviews",
        "experiment",
        "experiments",
        "study",
        "studies",
        "test",
        "tests",
        "testing",
        "confirm",
        "confirms",
        "confirmed",
        "confirming",
        "report",
        "reports",
        "reported",
        "reporting",
        "observe",
        "observes",
        "observed",
        "observing",
        "measure",
        "measures",
        "measured",
        "measuring",
        "verify",
        "verifies",
        "verified",
        "verifying",
        "independent",
        "internal",
        "external",
    }
)

SPECIFICITY_VERSION = "2.0"  # bumped: attribution-cue exclusion (P0-B.5)


def _content_tokens(text: str) -> frozenset[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return frozenset(
        t
        for t in tokens
        if len(t) > _MIN_TOKEN_LEN and t not in STOP_WORDS and t not in _ATTRIBUTION_CUES
    )


def _capitalized_words(text: str) -> frozenset[str]:
    """
    Capitalized tokens (cheap proxy for named entities -- no NER model),
    excluding the text's own first token: sentence-initial capitalization
    is a grammatical artifact of English orthography, not an entity
    signal, and counting it would systematically -- and spuriously --
    inflate the specificity of any claim that merely starts with an
    ordinary word ("Tests confirm...", "Independent studies show...").
    """
    tokens = _TOKEN_RE.findall(text)
    return frozenset(t for t in tokens[1:] if t[:1].isupper() and t.lower() not in STOP_WORDS)


def compute_specificity(text: str) -> float:
    """
    Deterministic specificity score for one claim's text. Higher means
    more detailed/specific. Not normalized against text length across
    different pairs -- only meaningful as a relative comparison between
    the two claims of a single pair (see specificity_delta).
    """
    content_tokens = _content_tokens(text)
    numeric_hits = len(_NUMERIC_RE.findall(text))
    year_hits = len(_YEAR_RE.findall(text))
    month_hits = len(_MONTH_RE.findall(text))
    entity_hits = len(_capitalized_words(text))

    return (
        len(content_tokens)
        + 2.0 * numeric_hits
        + 2.0 * year_hits
        + 1.5 * month_hits
        + 1.5 * entity_hits
    )


def specificity_delta(entailing_text: str, entailed_text: str) -> float:
    """specificity(entailing_text) - specificity(entailed_text)."""
    return compute_specificity(entailing_text) - compute_specificity(entailed_text)


def is_refinement(entailing_text: str, entailed_text: str, margin: float) -> bool:
    """
    True iff the entailing claim (the one whose entailment of the other was
    established by NLI) is meaningfully more specific than the entailed
    claim -- i.e. this one-way entailment should be reported as REFINES
    rather than SUPPORTS. `margin` is the minimum specificity_delta required;
    at margin=0, any entailing claim that is even slightly more detailed
    counts as a refinement, so callers should pass a policy-configured
    positive margin to require a meaningful gap.
    """
    return specificity_delta(entailing_text, entailed_text) >= margin
