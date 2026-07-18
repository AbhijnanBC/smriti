"""
structure.py — SVO structured extraction for Phase 4.

Responsibility:
    Attempt to extract Subject–Verb–Object structure from an AssertionCandidate.
    Returns StructuredAssertionCandidate regardless of success.

    Structure is OPTIONAL.
    A Claim always exists; its SVO is a bonus, not a requirement.

    If extraction succeeds → ExtractionMode.STRUCTURED
    If partial extraction → ExtractionMode.PARTIAL
    If extraction fails → ExtractionMode.LEXICAL (text span preserved)

Rules:
    ✅ Extract subject, predicate, object from dependency tree
    ✅ Return partial results if full SVO is unavailable
    ✅ Never reject — always return something

    ❌ Never modify text
    ❌ Never invent structure
    ❌ Never perform semantic inference
"""

from __future__ import annotations

from typing import Optional
import structlog

from smriti.core.models import (
    StructuredAssertion,
    ExtractionMode,
    ClaimWarning,
    SemanticSentence,
)
from smriti.claims.models import AssertionCandidate, StructuredAssertionCandidate
from smriti.claims.parser import BaseParser
from smriti.claims.rules import SUBJECT_DEP_LABELS, OBJECT_DEP_LABELS, VERB_POS_TAGS

logger = structlog.get_logger(__name__)


class StructureExtractor:
    """
    Extracts SVO structure from AssertionCandidates.
    """

    def extract(self, candidate: AssertionCandidate, parser: BaseParser) -> StructuredAssertionCandidate:
        """
        Attempt SVO extraction.

        The candidate text is re-parsed in isolation to strictly avoid
        cross-clause contamination from the full sentence dependency tree.

        Args:
            candidate: AssertionCandidate with text and original parse.
            parser: Linguistic parser to use for re‑parsing the candidate.

        Returns:
            StructuredAssertionCandidate with extraction result.
        """
        warnings = []

        # Create an isolated mock sentence to restrict the dependency tree
        isolated_sentence = SemanticSentence(
            sentence_id=f"{candidate.source.sentence.sentence_id}_sub",
            document_id=candidate.source.sentence.document_id,
            text=candidate.text,
            source_path=candidate.source.sentence.source_path,
            context=candidate.source.sentence.context,
            position=candidate.source.sentence.position,
            char_start=0,
            char_end=len(candidate.text),
            origin_block_type=candidate.source.sentence.origin_block_type,
            schema_version=candidate.source.sentence.schema_version,
        )

        # Reparse strictly the candidate's span
        local_parse = parser.parse(isolated_sentence)

        if not local_parse.parse_ok or local_parse.spacy_doc is None:
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.WHOLE_SENTENCE,
                warnings=warnings,
            )

        # Extract SVO from the isolated doc
        svo = self._extract_svo(local_parse.spacy_doc)

        if svo is None:
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.LEXICAL,
                warnings=warnings,
            )

        # Determine extraction mode based on completeness
        if svo.is_complete:
            mode = ExtractionMode.STRUCTURED
        elif svo.is_partial:
            mode = ExtractionMode.PARTIAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
        else:
            mode = ExtractionMode.LEXICAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)

        return StructuredAssertionCandidate(
            candidate=candidate,
            structured_assertion=svo,
            extraction_mode=mode,
            warnings=warnings,
        )

    def _extract_svo(self, doc) -> Optional[StructuredAssertion]:
        """
        Extract Subject, Verb (Predicate), Object from spaCy dependency tree.

        Traversal strategy:
            1. Find ROOT token (main verb)
            2. Find subject: child of ROOT with dep_ in SUBJECT_DEP_LABELS
            3. Find object: child of ROOT with dep_ in OBJECT_DEP_LABELS
            4. Extract full noun phrase spans for subject and object

        Returns None if no structure can be identified.
        """
        subject = None
        predicate = None
        obj = None
        negation_marker = None
        modality_marker = None

        # Find root (main verb)
        roots = [t for t in doc if t.dep_ == "ROOT"]
        if not roots:
            return None

        root = roots[0]

        # Predicate = root verb text (lemma form for consistency in annotation)
        if root.pos_ in VERB_POS_TAGS:
            predicate = root.text
        else:
            # Root is not a verb — cannot extract SVO
            return None

        # Find negation attached to root
        neg_tokens = [t for t in root.children if t.dep_ == "neg"]
        if neg_tokens:
            negation_marker = neg_tokens[0].text

        # Find auxiliary/modal attached to root
        aux_tokens = [t for t in root.children if t.dep_ in ("aux", "auxpass")]
        if aux_tokens:
            modality_marker = aux_tokens[0].text

        # Find subject
        for token in root.children:
            if token.dep_ in SUBJECT_DEP_LABELS:
                # Extract full noun phrase subtree
                subject = " ".join(t.text for t in token.subtree)
                break

        # Find object
        for token in root.children:
            if token.dep_ in OBJECT_DEP_LABELS:
                obj = " ".join(t.text for t in token.subtree)
                break

        # If nothing found at all, return None
        if not any([subject, predicate, obj]):
            return None

        return StructuredAssertion(
            subject=subject,
            predicate=predicate,
            object=obj,
            negation_marker=negation_marker,
            modality_marker=modality_marker,
        )