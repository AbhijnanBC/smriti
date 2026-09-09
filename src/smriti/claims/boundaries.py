"""
boundaries.py — Claim boundary detection for Phase 4.

Responsibility:
    Given a ParsedSentence, identify where individual semantic assertions begin
    and end within the sentence text.

    This is the most algorithmically complex module in Phase 4.

    Input:  ParsedSentence (with spaCy Doc)
    Output: List[AssertionCandidate]

Boundary Rules (deterministic, in priority order):
    1. Coordinated predicates with shared subject: split
       "Python supports generators and decorators"
       → "Python supports generators." + "Python supports decorators."

    2. Independent clauses joined by coordinator: split
       "CUDA is proprietary and AMD ROCm is open."
       → "CUDA is proprietary." + "AMD ROCm is open."

    3. Contrastive clauses (although/whereas): preserve both sides
       "Although CUDA is proprietary, it performs well."
       → "CUDA is proprietary." + "CUDA performs well."
       (relationship recorded in metadata)

    4. Conditional clauses: preserve entire conditional as one claim
       "If CUDA is installed, PyTorch uses the GPU."
       → Single claim (condition must not be severed)

    5. Relative clauses: preserve as one claim unless independent
       "Python, which was released in 1991, supports generators."
       → Single claim (relative clause is not an independent assertion)

    6. Single assertion (default): no split → one candidate

Design:
    If splitting fails or is ambiguous → fall back to whole-sentence candidate.
    Information is NEVER lost. Ambiguous → conservative (no split).
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.models import BoundaryReason
from smriti.claims.models import ParsedSentence, AssertionCandidate
from smriti.claims.rules import SUBJECT_DEP_LABELS

logger = structlog.get_logger(__name__)


class BoundaryDetector:
    """
    Applies deterministic boundary rules to find assertion boundaries.

    Instantiate once, call detect() per ParsedSentence.
    """

    def __init__(self) -> None:
        config = get_config()
        ce_cfg = config.get("claim_extraction", {})
        self._split_conjunctions: bool = ce_cfg.get("split_conjunctions", True)
        self._split_conditionals: bool = ce_cfg.get("split_conditionals", False)
        self._split_relative_clauses: bool = ce_cfg.get("split_relative_clauses", False)

    def detect(self, parsed: ParsedSentence) -> List[AssertionCandidate]:
        """
        Detect claim boundaries in a parsed sentence.

        Args:
            parsed: ParsedSentence from parser.py.

        Returns:
            List of AssertionCandidate. Always at least one (whole-sentence fallback).
        """
        # If parsing failed, return the whole sentence as one candidate
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return [self._whole_sentence_candidate(parsed, reason=BoundaryReason.PARSE_FAILED)]

        doc = parsed.spacy_doc
        candidates: List[AssertionCandidate] = []

        if self._split_conjunctions:
            candidates = self._detect_coordination_boundaries(parsed, doc)

        # If no splits were detected (or splitting disabled), use whole sentence
        if not candidates:
            candidates = [self._whole_sentence_candidate(parsed, reason=BoundaryReason.SINGLE_ASSERTION)]

        logger.debug(
            "boundaries detected",
            sentence_id=parsed.sentence.sentence_id[:8],
            candidate_count=len(candidates),
        )

        return candidates

    def _detect_coordination_boundaries(
        self,
        parsed: ParsedSentence,
        doc,
    ) -> List[AssertionCandidate]:
        """
        Detect boundaries created by coordinating conjunctions (and, but, or).

        Uses exact token spans to reconstruct clauses, preserving tense, aspect,
        and passive voice. Never uses .lemma_ for reconstruction.
        """
        try:
            # Find sentence root (usually the main verb)
            roots = [token for token in doc if token.dep_ == "ROOT"]
            if not roots:
                return []

            root = roots[0]

            # Find coordinating conjunctions attached to root
            conj_tokens = [
                t for t in doc
                if t.dep_ == "conj" and t.head == root
            ]

            if conj_tokens:
                return self._reconstruct_coordinated_clauses(
                    sent=doc,
                    root=root,
                    conjuncts=conj_tokens,
                    parsed=parsed,
                )

            # No coordination directly on the root verb. Check for
            # coordination on the root's direct object/complement instead —
            # e.g. "Python supports generators and decorators": "decorators"
            # is dep_="conj" with head=generators (the object), not
            # head=root. Subject and verb are shared by construction in this
            # case, so it is always COORDINATED_PREDICATE, and each
            # candidate is reconstructed as subject + aux + root verb + one
            # object conjunct (instead of substituting a whole conjunct verb
            # subtree for the root, as the verb-level branch above does).
            objects = [
                t for t in root.rights
                if t.dep_ in ("dobj", "obj", "attr", "dative", "oprd", "pobj")
            ]
            for obj in objects:
                obj_conjuncts = [t for t in doc if t.dep_ == "conj" and t.head == obj]
                if obj_conjuncts:
                    return self._reconstruct_coordinated_clauses(
                        sent=doc,
                        root=root,
                        conjuncts=obj_conjuncts,
                        parsed=parsed,
                        shared_root_token=root,
                    )

            return []

        except Exception as e:
            logger.debug(
                "boundary detection error (falling back)",
                error=str(e),
                sentence_id=parsed.sentence.sentence_id[:8],
            )
            return []

    def _reconstruct_coordinated_clauses(
        self,
        sent,
        root,
        conjuncts,
        parsed: ParsedSentence,
        shared_root_token=None,
    ) -> List[AssertionCandidate]:
        """
        Reconstruct clauses using exact token spans to preserve tense, aspect, and passive voice.
        NEVER uses lemmas for reconstruction.

        `shared_root_token`, when given, means `conjuncts` are coordinated
        objects/complements of the root verb (not coordinated verbs
        themselves) — e.g. "decorators" in "Python supports generators and
        decorators". Subject and verb are then always shared, so the result
        is always COORDINATED_PREDICATE, and the root verb token must be
        explicitly included when reconstructing each conjunct's candidate
        (unlike the verb-conjunction case, where each conjunct already IS a
        verb standing in for the root).
        """
        candidates = []

        # 1. Extract the exact token span for the subject
        subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass", "csubj")]
        subj_tokens = list(subjects[0].subtree) if subjects else []

        if shared_root_token is not None:
            # Object-level coordination: subject and verb are shared by
            # construction, regardless of what follows the conjunct objects.
            boundary_reason = BoundaryReason.COORDINATED_PREDICATE
        else:
            # Verb-level coordination: determine whether each conjunct
            # introduces its OWN subject (independent clause, e.g. "Python is
            # fast and Java is slow") or shares the root's subject
            # (coordinated predicate, e.g. "Python runs and compiles quickly").
            conjunct_has_own_subject = [
                any(t.dep_ in ("nsubj", "nsubjpass", "csubj") for t in conj.lefts)
                for conj in conjuncts
            ]
            if conjuncts and all(conjunct_has_own_subject):
                boundary_reason = BoundaryReason.INDEPENDENT_CLAUSE
            else:
                boundary_reason = BoundaryReason.COORDINATED_PREDICATE

        # 2. Extract the main clause (exclude conjunct subtrees and their coordinating conjunctions)
        conjunct_subtrees = set()
        for conj in conjuncts:
            conjunct_subtrees.update(conj.subtree)
            # Catch the 'and' / 'or' attached to the conjunct
            for cc in conj.lefts:
                if cc.dep_ == "cc":
                    conjunct_subtrees.add(cc)

        main_clause_tokens = [t for t in sent if t not in conjunct_subtrees]
        main_text = self._tokens_to_string(main_clause_tokens)
        main_spans, main_token_ids = self._tokens_to_spans_and_ids(main_clause_tokens)

        candidates.append(
            AssertionCandidate(
                text=main_text,
                source=parsed,
                span_start=0,
                span_end=len(main_text),  # approximate end; we keep it simple
                boundary_reason=boundary_reason,
                source_char_spans=main_spans,
                source_token_ids=main_token_ids,
            )
        )

        # 3. Reconstruct each conjunct clause by combining:
        #    Subject Tokens + Auxiliary Tokens + [Root Verb, if object-level
        #    coordination] + Conjunct Tokens
        aux_tokens = [t for t in root.lefts if t.dep_ in ("aux", "auxpass")]
        root_tokens = [shared_root_token] if shared_root_token is not None else []

        for conj in conjuncts:
            # Combine all required tokens and sort them by their original position in the sentence
            reconstructed_tokens = sorted(
                set(subj_tokens + aux_tokens + root_tokens + list(conj.subtree)),
                key=lambda x: x.i
            )
            conj_text = self._tokens_to_string(reconstructed_tokens)
            conj_spans, conj_token_ids = self._tokens_to_spans_and_ids(reconstructed_tokens)

            candidates.append(
                AssertionCandidate(
                    text=conj_text,
                    source=parsed,
                    span_start=conj.idx,
                    span_end=conj.idx + len(conj_text),
                    boundary_reason=boundary_reason,
                    source_char_spans=conj_spans,
                    source_token_ids=conj_token_ids,
                )
            )

        return candidates

    def _tokens_to_spans_and_ids(self, tokens: list) -> Tuple[tuple, tuple]:
        """
        Compute exact source-token provenance for a reconstructed candidate.

        Given the exact token list used to build a candidate's text (in
        original-sentence order), group it into contiguous runs — a run
        breaks wherever the next token's index is not exactly one more than
        the previous token's index (i.e. tokens from the "other" conjunct, or
        an intervening coordinator, were excluded). Each run becomes one
        (char_start, char_end) span into the ORIGINAL sentence text.

        Example: "Python supports generators and decorators." reconstructing
        the "decorators" conjunct combines tokens {Python(0), supports(1),
        decorators(4)} — two contiguous runs: [0,1] ("Python supports") and
        [4] ("decorators"), because token 2 ("generators") and 3 ("and") are
        not part of this candidate.

        Returns:
            (source_char_spans, source_token_ids) — source_token_ids are the
            sorted, de-duplicated Token.i values; source_char_spans are the
            (start, end) character pairs for each contiguous run.
        """
        if not tokens:
            return (), ()

        ordered = sorted(set(tokens), key=lambda t: t.i)
        token_ids = tuple(t.i for t in ordered)

        spans: List[Tuple[int, int]] = []
        run_start_token = ordered[0]
        prev_token = ordered[0]
        for tok in ordered[1:]:
            if tok.i == prev_token.i + 1:
                prev_token = tok
                continue
            spans.append((run_start_token.idx, prev_token.idx + len(prev_token.text)))
            run_start_token = tok
            prev_token = tok
        spans.append((run_start_token.idx, prev_token.idx + len(prev_token.text)))

        return tuple(spans), token_ids

    def _tokens_to_string(self, tokens: list) -> str:
        """Safely join tokens respecting spaCy's original whitespace mapping."""
        if not tokens:
            return ""
        text = tokens[0].text
        for i in range(1, len(tokens)):
            if tokens[i-1].whitespace_:
                text += " " + tokens[i].text
            else:
                # Handle punctuation spacing fallback if whitespace is lost
                if tokens[i].is_punct:
                    text += tokens[i].text
                else:
                    text += " " + tokens[i].text
        return text.strip()

    def _whole_sentence_candidate(
        self,
        parsed: ParsedSentence,
        reason: BoundaryReason = BoundaryReason.SINGLE_ASSERTION,
    ) -> AssertionCandidate:
        """Create a single whole-sentence candidate (no splitting)."""
        text = parsed.sentence.text
        # The whole sentence is used verbatim, so it is always exactly one
        # contiguous span. Token ids are only available when spaCy actually
        # parsed the sentence (SINGLE_ASSERTION); on PARSE_FAILED there is no
        # doc to draw token ids from.
        if parsed.parse_ok and parsed.spacy_doc is not None:
            token_ids = tuple(t.i for t in parsed.spacy_doc)
        else:
            token_ids = ()
        return AssertionCandidate(
            text=text,
            span_start=0,
            span_end=len(text),
            source=parsed,
            boundary_reason=reason,
            source_char_spans=((0, len(text)),),
            source_token_ids=token_ids,
        )