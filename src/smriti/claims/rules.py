"""
rules.py — All deterministic extraction rules for Phase 4.

This file contains ONLY data and patterns.
Zero execution logic lives here.

Every constant is configurable via config/default.yaml [claim_extraction].
These are the hard-coded defaults for those config values.
"""

from typing import FrozenSet

# ── Coordinating conjunctions that split claims ───────────────────────────────
# "Python supports X and Y" → two claims if Y is a noun phrase with no predicate
# "Python is fast and Java is slow" → two claims (each has own predicate)
COORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset(["and", "but", "or", "nor"])

# ── Subordinating conjunctions that signal boundary candidates ─────────────
SUBORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset([
    "although", "because", "since", "while", "whereas", "though",
    "even though", "as long as", "unless", "until",
])

# ── Negation markers ──────────────────────────────────────────────────────────
NEGATION_MARKERS: FrozenSet[str] = frozenset([
    "not", "no", "never", "neither", "nor", "without",
    "n't", "cannot", "can't", "won't", "doesn't", "don't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
    "hadn't", "wouldn't", "couldn't", "shouldn't",
])

# ── Modality markers and their classifications ────────────────────────────────
MODALITY_POSSIBLE: FrozenSet[str] = frozenset([
    "may", "might", "could", "can",
])

MODALITY_PROBABLE: FrozenSet[str] = frozenset([
    "probably", "likely", "should", "ought",
])

MODALITY_REQUIRED: FrozenSet[str] = frozenset([
    "must", "will", "shall", "need", "have to", "has to",
])

MODALITY_IMPOSSIBLE: FrozenSet[str] = frozenset([
    "cannot", "can't", "impossible",
])

# ── Attribution verbs (X says Y / X believes Y) ───────────────────────────────
ATTRIBUTION_VERBS: FrozenSet[str] = frozenset([
    "say", "says", "said", "claim", "claims", "claimed",
    "argue", "argues", "argued", "believe", "believes", "believed",
    "state", "states", "stated", "report", "reports", "reported",
    "suggest", "suggests", "suggested", "note", "notes", "noted",
    "assert", "asserts", "asserted", "propose", "proposes", "proposed",
    "write", "writes", "wrote", "show", "shows", "showed", "shown",
    "find", "finds", "found",
])

# ── Comparison markers ────────────────────────────────────────────────────────
COMPARISON_MARKERS: FrozenSet[str] = frozenset([
    "faster", "slower", "better", "worse", "more", "less",
    "higher", "lower", "greater", "smaller", "stronger", "weaker",
    "outperforms", "underperforms", "exceeds", "beats",
    "superior", "inferior", "compared", "than",
])

# ── POS dependency labels for SVO extraction ─────────────────────────────────
# spaCy dependency labels for subject identification
SUBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "nsubj",     # Nominal subject: "Python supports X"
    "nsubjpass", # Passive nominal subject: "X is supported by Python"
    "csubj",     # Clausal subject
    "expl",      # Expletive: "There is X"
])

# spaCy dependency labels for object identification
OBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "dobj",  # Direct object: "Python supports generators"
    "pobj",  # Object of preposition: "runs on GPU"
    "attr",  # Attribute: "Python is a language"
    "acomp", # Adjectival complement: "Python is fast"
])

# spaCy POS tags for verb/predicate identification
VERB_POS_TAGS: FrozenSet[str] = frozenset(["VERB", "AUX"])

# ── Schema ────────────────────────────────────────────────────────────────────
CLAIM_SCHEMA_VERSION = "4.0"
RULE_VERSION = "1.0"          # NEW (Priority 1)
PHASE4_PIPELINE_VERSION = "1.0"

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_CLAIMS_PER_SENTENCE_DEFAULT = 10
MIN_CLAIM_CHARS_DEFAULT = 3