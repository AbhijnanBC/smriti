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

from typing import List
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

            if not conj_tokens:
                return []

            # Use the new reconstruction method
            return self._reconstruct_coordinated_clauses(
                sent=doc,
                root=root,
                conjuncts=conj_tokens,
                parsed=parsed,
            )

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
    ) -> List[AssertionCandidate]:
        """
        Reconstruct clauses using exact token spans to preserve tense, aspect, and passive voice.
        NEVER uses lemmas for reconstruction.
        """
        candidates = []

        # 1. Extract the exact token span for the subject
        subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass", "csubj")]
        subj_tokens = list(subjects[0].subtree) if subjects else []

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

        candidates.append(
            AssertionCandidate(
                text=main_text,
                source=parsed,
                span_start=0,
                span_end=len(main_text),  # approximate end; we keep it simple
                boundary_reason=BoundaryReason.COORDINATION,
            )
        )

        # 3. Reconstruct each conjunct clause by combining:
        #    Subject Tokens + Auxiliary Tokens + Conjunct Tokens
        aux_tokens = [t for t in root.lefts if t.dep_ in ("aux", "auxpass")]

        for conj in conjuncts:
            # Combine all required tokens and sort them by their original position in the sentence
            reconstructed_tokens = sorted(
                set(subj_tokens + aux_tokens + list(conj.subtree)),
                key=lambda x: x.i
            )
            conj_text = self._tokens_to_string(reconstructed_tokens)

            candidates.append(
                AssertionCandidate(
                    text=conj_text,
                    source=parsed,
                    span_start=conj.idx,
                    span_end=conj.idx + len(conj_text),
                    boundary_reason=BoundaryReason.COORDINATION,
                )
            )

        return candidates

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
        return AssertionCandidate(
            text=text,
            span_start=0,
            span_end=len(text),
            source=parsed,
            boundary_reason=reason,
        )