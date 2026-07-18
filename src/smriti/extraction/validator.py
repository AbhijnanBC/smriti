"""
validator.py — SemanticSentence validator for Phase 3.

Responsibility:
    Validate a collection of SemanticSentence objects before emission.
    Check per-sentence and cross-sentence invariants.

Rules:
    ✅ Text must not be empty or whitespace-only              → discard with SEG001
    ✅ Sentence IDs must be unique across the collection       → VAL001 (fatal)
    ✅ Positions must be strictly monotonically increasing     → VAL002 (fatal)
    ✅ char_start must be < char_end                           → VAL002 (fatal)
    ✅ document_id must be consistent                          → fatal
    ✅ Context strings must be plausible (non-empty, only allowed chars) → VAL003 (warning)

Design:
    NEVER modifies objects.
    ONLY reports problems.
    Fatal problems raise SentenceValidationError.
    Recoverable problems return warnings.
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.rules import CONTEXT_VALID_PATTERN
from smriti.exceptions import SentenceValidationError

logger = structlog.get_logger(__name__)


def validate_sentences(
    sentences: List[SemanticSentence],
    document_id: str,
) -> Tuple[List[SemanticSentence], List[SegmentationWarning]]:
    """
    Validate a collection of SemanticSentences.

    Args:
        sentences:    Sentences to validate.
        document_id:  Expected document_id for all sentences.

    Returns:
        (valid_sentences, warnings_list)
        valid_sentences excludes empty/whitespace-only sentences.
        Fatal violations raise SentenceValidationError instead of returning.

    Raises:
        SentenceValidationError: On duplicate IDs, non-monotonic positions,
                                  or document_id mismatch.
    """
    warnings: List[SegmentationWarning] = []
    valid: List[SemanticSentence] = []
    seen_ids = set()
    last_position = -1

    for sentence in sentences:
        # Check 1: Document identity consistency
        if sentence.document_id != document_id:
            raise SentenceValidationError(
                f"Sentence {sentence.sentence_id} has document_id "
                f"'{sentence.document_id}' but expected '{document_id}'"
            )

        # Check 2: Non-empty text
        if not sentence.text.strip():
            warnings.append(SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED)
            logger.debug("empty sentence discarded", sentence_id=sentence.sentence_id)
            continue

        # Check 3: Unique sentence ID (fatal)
        if sentence.sentence_id in seen_ids:
            raise SentenceValidationError(
                f"Duplicate sentence ID detected: {sentence.sentence_id} "
                f"in document {document_id}. This indicates a determinism bug."
            )
        seen_ids.add(sentence.sentence_id)

        # Check 4: Monotonically increasing position (fatal)
        if sentence.position <= last_position:
            raise SentenceValidationError(
                f"Non-monotonic position: sentence {sentence.sentence_id} "
                f"has position {sentence.position} after {last_position}"
            )
        last_position = sentence.position

        # Check 5: Valid character offsets (fatal)
        if sentence.char_start >= sentence.char_end and sentence.char_end > 0:
            raise SentenceValidationError(
                f"Invalid offsets for sentence {sentence.sentence_id}: "
                f"char_start={sentence.char_start} >= char_end={sentence.char_end}"
            )

        # Check 6: Context plausibility (non-fatal)
        if sentence.context:
            if not CONTEXT_VALID_PATTERN.match(sentence.context):
                warnings.append(SegmentationWarning.VAL_INVALID_CONTEXT)
                logger.warning(
                    "invalid context characters",
                    sentence_id=sentence.sentence_id,
                    context=sentence.context,
                )

        valid.append(sentence)

    return valid, warnings