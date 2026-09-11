"""
classifier.py — Assertion-type classification for Phase 4.

Responsibility:
    Classify a SemanticSentence into one of the AssertionType categories
    BEFORE any Claim object is constructed.

    Only AssertionType.DECLARATIVE_ASSERTION proceeds into the claim
    construction pipeline (boundary detection → structure extraction →
    annotation → degradation → Claim). Everything else is recorded as a
    DiscardedCandidate by the caller (claims/__init__.py) so that no
    information about the source document is ever silently dropped.

Design:
    Deterministic, rule/heuristic-based classification. No ML model.
    Uses, in priority order:
        1. origin_block_type from Phase 3 (free, already-computed structural
           signal — e.g. "table", "block_quote", "code_block").
        2. Regex patterns for common non-assertion markdown idioms
           (bold-label metadata lines, leaked heading markers).
        3. Surface punctuation (trailing "?").
        4. spaCy dependency structure (root POS/tag, presence of a subject)
           to distinguish declarative assertions, imperative instructions,
           bare noun-phrase list items / headings, and incoherent fragments.

Rules:
    ✅ NEVER modifies sentence text.
    ✅ NEVER raises — always returns a classification and a reason string.
    ❌ NEVER performs semantic inference beyond surface grammar.
"""

from __future__ import annotations

import structlog

from smriti.claims.models import ParsedSentence
from smriti.claims.rules import (
    HEADING_ATX_LEAK_PATTERN,
    HEADING_BARE_BOLD_PATTERN,
    HEADING_LIKE_MAX_WORDS,
    METADATA_BOLD_LABEL_PATTERN,
    NOUN_LIKE_ROOT_POS_TAGS,
    SUBJECT_DEP_LABELS,
    VERB_POS_TAGS,
)
from smriti.core.models import AssertionType, SemanticSentence

logger = structlog.get_logger(__name__)

# origin_block_type values (from smriti.extraction.scanner.BlockType) that map
# directly onto an AssertionType, independent of the text content. Stored as
# plain strings here (rather than importing BlockType) to keep Phase 4
# decoupled from Phase 3's internal scanner module, per the existing
# architecture boundary (SemanticSentence.origin_block_type is already a str).
_ORIGIN_BLOCK_TYPE_OVERRIDES = {
    "table": AssertionType.TABLE_CELL,
    "block_quote": AssertionType.QUOTE,
    "code_block": AssertionType.CODE,
}

# List-shaped origin blocks: a verbless span from one of these is a LIST_ITEM,
# not a HEADING or FRAGMENT.
_LIST_ORIGIN_BLOCK_TYPES = frozenset(["bullet_item", "ordered_item"])


class AssertionClassifier:
    """
    Stateless rule-based classifier. Safe to share across all sentences in a
    Phase 4 run (instantiate once, call classify() per sentence).
    """

    # Walks the full rule-based AssertionType decision table (question,
    # negation, hedge, imperative, etc.); each rule is a simple, independent
    # check, but the table itself is long enough to trip mccabe's threshold.
    def classify(  # noqa: C901
        self,
        sentence: SemanticSentence,
        parsed: ParsedSentence,
    ) -> tuple[AssertionType, str]:
        """
        Classify a SemanticSentence.

        Args:
            sentence: The SemanticSentence from Phase 3.
            parsed:   The already-computed ParsedSentence (Stage 1 output) —
                      re-used here so classification never triggers a second
                      spaCy parse.

        Returns:
            (AssertionType, reason) — reason is a short machine-readable
            code, useful for logging and for DiscardedCandidate.reason.
        """
        text = sentence.text.strip()
        origin = sentence.origin_block_type

        if not text:
            return AssertionType.FRAGMENT, "empty_text"

        # ── 1. Structural override from Phase 3 block type ──────────────────
        override = _ORIGIN_BLOCK_TYPE_OVERRIDES.get(origin)
        if override is not None:
            return override, f"origin_block_type_{origin}"

        # ── 2. Markdown idioms that are never assertions ─────────────────────
        if METADATA_BOLD_LABEL_PATTERN.match(text):
            return AssertionType.METADATA, "regex_bold_label_colon"

        if HEADING_ATX_LEAK_PATTERN.match(text):
            return AssertionType.HEADING, "regex_atx_heading_leak"

        if HEADING_BARE_BOLD_PATTERN.match(text):
            return AssertionType.HEADING, "regex_bare_bold_no_colon"

        # ── 3. Surface punctuation ───────────────────────────────────────────
        if text.endswith("?"):
            return AssertionType.QUESTION, "ends_with_question_mark"

        # ── 4. Dependency-structure classification ───────────────────────────
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return AssertionType.FRAGMENT, "parse_failed"

        doc = parsed.spacy_doc
        roots = [t for t in doc if t.dep_ == "ROOT"]
        if not roots:
            return AssertionType.FRAGMENT, "no_root_token"

        root = roots[0]
        has_direct_subject = any(t.dep_ in SUBJECT_DEP_LABELS for t in root.children)
        # Fallback: some constructions (e.g. spaCy mis-tokenizing a hyphenated
        # passive participle like "pre-trained" into "pre" / "-" / "trained",
        # which detaches the subject from the nominal ROOT it should attach
        # to) leave a genuine subject in the sentence that just isn't a
        # direct child of ROOT. Search the whole doc as a second signal so a
        # real assertion isn't misclassified as a FRAGMENT purely because of
        # a tokenizer/parser quirk on an unrelated word.
        has_subject_anywhere = has_direct_subject or any(t.dep_ in SUBJECT_DEP_LABELS for t in doc)

        if root.pos_ in VERB_POS_TAGS:
            is_imperative = root.tag_ == "VB" and not has_subject_anywhere
            if is_imperative:
                return (
                    AssertionType.PROCEDURAL_INSTRUCTION,
                    "imperative_base_form_verb_no_subject",
                )
            if has_subject_anywhere:
                return AssertionType.DECLARATIVE_ASSERTION, "finite_verb_with_subject"
            if root.tag_ == "VBG":
                # Bare gerund phrase with no subject: "Preparing the Dough" —
                # a common recipe/instructional section title, not an
                # assertion about anything.
                return AssertionType.HEADING, "bare_gerund_no_subject"
            return AssertionType.FRAGMENT, "verb_root_no_subject_not_imperative"

        # Root is not a verb/aux — bare phrase, no predication.
        if root.pos_ not in NOUN_LIKE_ROOT_POS_TAGS:
            # Root is something unexpected for a coherent phrase (e.g. an
            # adposition or determiner left dangling) — treat as garbled.
            return AssertionType.FRAGMENT, "root_not_noun_like_no_verb"

        if origin in _LIST_ORIGIN_BLOCK_TYPES:
            return AssertionType.LIST_ITEM, "no_verb_root_list_item_block"

        if self._looks_like_heading(text):
            return AssertionType.HEADING, "short_titlecase_no_verb_phrase"

        return AssertionType.LIST_ITEM, "no_verb_root_bare_noun_phrase"

    @staticmethod
    def _looks_like_heading(text: str) -> bool:
        """
        Heuristic: a short, fully title-cased/capitalized phrase with no
        verb and no terminal sentence punctuation reads as a heading/title
        rather than a list item, e.g. "Ingredients" or "Weekly Meal Plan".
        """
        stripped = text.rstrip(".!").strip()
        if not stripped or stripped.endswith("?"):
            return False
        words = stripped.split()
        if not words or len(words) > HEADING_LIKE_MAX_WORDS:
            return False
        # Require every word to start with an uppercase letter (allow
        # all-caps acronyms too) — a genuine title-case heading, not just a
        # capitalized proper noun leading an otherwise lowercase phrase.
        return all(w[:1].isupper() for w in words if w[:1].isalpha())
