"""
builder.py — Immutable Claim construction for Phase 4.

Responsibility:
    Construct the final immutable Claim object from a ValidatedAssertion.

    This is the ONLY place where Claim is instantiated.
    That enforces a single, consistent construction path.

Builder performs:
    1. Deterministic claim_id generation (SHA256, never random)
    2. Content hash computation (SHA256 of exact text)
    3. Provenance chain construction
    4. Object construction with schema and rule versioning

    Builder NEVER modifies text.
    Builder NEVER applies logic or heuristics.
    Builder NEVER performs validation.
    Pure object construction only.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import structlog

from smriti.core.models import (
    Claim,
    ClaimProvenance,
    ExtractionMode,
    AssertionMetadata,  # <-- ADDED
)
from smriti.claims.models import ValidatedAssertion
from smriti.claims.rules import CLAIM_SCHEMA_VERSION, RULE_VERSION

logger = structlog.get_logger(__name__)


def build_claim(validated: ValidatedAssertion) -> Claim:
    """
    Construct a single immutable Claim from a ValidatedAssertion.

    Args:
        validated: ValidatedAssertion from degradation.py.

    Returns:
        Immutable Claim with deterministic ID and complete provenance.
    """
    sentence = validated.source_sentence
    text = validated.text
    span_start = validated.span_start

    # Deterministic claim_id
    claim_id = _compute_claim_id(
        sentence_id=sentence.sentence_id,
        text=text,
        span_start=span_start,
    )

    # Content hash (SHA256 of exact claim text)
    content_hash = _compute_content_hash(text)

    # Complete provenance chain, including exact source-token provenance
    # (Part 2): which contiguous character spans / spaCy token ids in the
    # ORIGINAL sentence text actually produced this claim, and by which
    # deterministic rule (mirrors BoundaryReason).
    provenance = ClaimProvenance(
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        source_path=sentence.source_path,
        sentence_context=sentence.context,
        sentence_position=sentence.position,
        source_char_spans=validated.source_char_spans,
        source_token_ids=validated.source_token_ids,
        reconstruction_rule=validated.reconstruction_rule,
    )

    # <-- NEW: Merge internal split metadata into the final public contract
    merged_metadata = AssertionMetadata(
        is_negated=validated.linguistic_metadata.is_negated,
        modality=validated.linguistic_metadata.modality,
        is_conditional=validated.semantic_metadata.is_conditional,
        is_comparative=validated.semantic_metadata.is_comparative,
        is_attributed=validated.semantic_metadata.is_attributed,
        attributed_to=validated.semantic_metadata.attributed_to,
        is_quoted=validated.linguistic_metadata.is_quoted,
    )

    claim = Claim(
        claim_id=claim_id,
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        text=text,
        content_hash=content_hash,
        context=sentence.context,
        source_path=sentence.source_path,
        extraction_mode=validated.extraction_mode,
        structured_assertion=validated.structured_assertion,
        assertion_metadata=merged_metadata,  # <-- REPLACED
        provenance=provenance,
        schema_version=CLAIM_SCHEMA_VERSION,
        rule_version=RULE_VERSION,
    )

    logger.debug(
        "claim built",
        claim_id=claim_id[:8],
        mode=validated.extraction_mode.value,
        is_svo=claim.is_svo,
        negated=claim.is_negated,
        hash_prefix=content_hash[:8],
        rule_version=RULE_VERSION,
    )

    return claim


def _compute_claim_id(sentence_id: str, text: str, span_start: int) -> str:
    """
    Compute a deterministic 16-character claim ID.

    Input:  sentence_id + claim text + span_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs → same ID (deterministic)
        - No timestamps, no random values
        - span_start disambiguates identical text at different positions
          within the same sentence
    """
    id_material = f"{sentence_id}:{text}:{span_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]


def _compute_content_hash(text: str) -> str:
    """
    Compute SHA256 hash of the exact claim text.

    Important: This preserves case and all characters exactly as they appear.
    Lowercasing is NOT applied because case can carry semantic meaning
    (e.g., proper nouns, acronyms).

    Returns:
        16-character hex digest (first 16 chars of full SHA256).
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]