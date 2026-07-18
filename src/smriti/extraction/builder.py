"""
builder.py — SemanticSentence constructor for Phase 3.

Responsibility:
    Construct immutable SemanticSentence objects from SentenceCandidate
    and context information.

    This is the ONLY place where SemanticSentence is instantiated.
    That enforces a single, consistent construction path.

    Builder performs:
        1. Deterministic sentence_id generation (SHA256, never random)
        2. Position assignment (0-based, strictly increasing)
        3. Context association (heading path from ContextStack)
        4. Final object construction with provenance and version

    Builder NEVER modifies text.
    Builder NEVER modifies the context stack.
    Builder NEVER validates (that is validator.py's job).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional
import structlog

from smriti.core.models import SemanticSentence
from smriti.extraction.scanner import BlockType

logger = structlog.get_logger(__name__)


def build_sentence(
    text: str,
    document_id: str,
    source_path: Path,
    context: str,
    position: int,
    char_start: int,
    char_end: int,
    origin_block_type: BlockType,
) -> SemanticSentence:
    """
    Construct a single immutable SemanticSentence.

    Args:
        text:          The sentence text (stripped, non-empty).
        document_id:   The doc_id of the source Document.
        source_path:   Path to the original file (for traceability).
        context:       Current heading context (e.g. "Python > Generators").
        position:      0-based index within this document.
        char_start:    Character start in Document.normalized_text.
        char_end:      Character end in Document.normalized_text.
        origin_block_type: The BlockType that produced this sentence.

    Returns:
        Immutable SemanticSentence.
    """
    sentence_id = _compute_sentence_id(document_id, text, char_start)

    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=document_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=source_path,
        origin_block_type=origin_block_type.value,
        schema_version="3.0",
    )

    logger.debug(
        "sentence built",
        sentence_id=sentence_id[:8],
        position=position,
        context=context[:40] if context else "(root)",
        origin=origin_block_type.value,
        text_preview=text[:40],
    )

    return sentence


def _compute_sentence_id(document_id: str, text: str, char_start: int) -> str:
    """
    Compute a deterministic 16-character sentence ID.

    Input: document_id + canonical text (as stored) + char_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs always produce same ID (deterministic)
        - No timestamps
        - No random values
        - char_start disambiguates identical text at different positions
    """
    # Use the exact text that will be stored; this ensures stability across
    # future normalisation changes that might affect whitespace.
    id_material = f"{document_id}:{text}:{char_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]