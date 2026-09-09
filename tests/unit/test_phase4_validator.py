"""
Unit tests for claims/validator.py.
"""

import hashlib
import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ExtractionMode, AssertionMetadata, Modality, ClaimProvenance, ClaimWarning,
)
from smriti.claims.validator import validate_claims
from smriti.exceptions import ClaimValidationError


def make_claim(claim_id: str, text: str, doc_id: str = "doc001") -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="sent001",
        document_id=doc_id,
        text=text,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="sent001",
            document_id=doc_id,
            source_path=Path("test.md"),
            sentence_context="",
            sentence_position=0,
        ),
        schema_version="4.0",
    )


def test_valid_claims_pass():
    claims = [
        make_claim("aaa", "Python is great."),
        make_claim("bbb", "Julia is faster."),
    ]
    valid, warnings = validate_claims(claims, "doc001", {})
    assert len(valid) == 2
    assert warnings == []


def test_empty_text_discarded():
    claims = [
        make_claim("aaa", "   "),
        make_claim("bbb", "Real claim."),
    ]
    valid, warnings = validate_claims(claims, "doc001", {})
    assert len(valid) == 1
    assert ClaimWarning.CLM_EMPTY_ASSERTION in warnings


def test_duplicate_id_raises():
    """Duplicate claim_id with genuinely different content/provenance raises,
    and the message correctly flags the inconsistency (real content_hash values
    differ here, unlike the identical-content case covered separately below)."""
    claims = [
        make_claim("dup", "First claim."),
        make_claim("dup", "Second claim."),
    ]
    with pytest.raises(ClaimValidationError, match="inconsistent"):
        validate_claims(claims, "doc001", {})


def test_wrong_document_id_raises():
    claims = [make_claim("aaa", "Text.", doc_id="wrong_doc")]
    with pytest.raises(ClaimValidationError, match="document_id"):
        validate_claims(claims, "doc001", {})


def test_no_provenance_raises():
    from dataclasses import replace
    claim = make_claim("aaa", "Text.")
    # Forcefully create a claim with no provenance
    # (cannot happen in normal pipeline, but test the validator)
    import dataclasses
    bad_claim = dataclasses.replace(claim, provenance=None)
    with pytest.raises(ClaimValidationError):
        validate_claims([bad_claim], "doc001", {})


def test_empty_input_returns_empty():
    valid, warnings = validate_claims([], "doc001", {})
    assert valid == []
    assert warnings == []

def test_duplicate_id_with_same_content_raises_too():
    """Even if content_hash matches, duplicate IDs are not allowed."""
    claim1 = make_claim("dup", "Same text")
    claim2 = make_claim("dup", "Same text")  # same content, same provenance?
    # They share same sentence_id, doc_id, etc. In practice they'd be identical.
    # The validator should still raise.
    with pytest.raises(ClaimValidationError, match="Duplicate"):
        validate_claims([claim1, claim2], "doc001", {})    