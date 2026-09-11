"""
Unit tests for embedding/input_factory.py.

Tests both EmbeddingInputFactory (payload) and CacheKeyFactory (keys).
These are now separate classes with separate responsibilities.
"""

from pathlib import Path

import pytest
from smriti.core.models import (
    AssertionMetadata,
    Claim,
    ClaimProvenance,
    ExtractionMode,
)
from smriti.embedding.input_factory import CacheKeyFactory, EmbeddingInputFactory


def make_claim(
    claim_id: str = "c001",
    text: str = "Python supports generators.",
    context: str = "",
    content_hash: str = "abc123",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id="d001",
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001",
            document_id="d001",
            source_path=Path("test.md"),
            sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=content_hash,
        rule_version="1.0",
    )


@pytest.fixture
def payload_factory():
    return EmbeddingInputFactory()


@pytest.fixture
def key_factory():
    return CacheKeyFactory(model_signature="test_model_sig_abc", config_hash="test_config_xyz")


# ── EmbeddingInputFactory tests ───────────────────────────────────────────────


def test_payload_without_context(payload_factory):
    """Claim without context → payload is just claim.text."""
    claim = make_claim(text="Python is fast.", context="")
    assert payload_factory.build_payload(claim) == "Python is fast."


def test_payload_with_context(payload_factory):
    """Claim with context → payload is 'context\\ntext'."""
    claim = make_claim(text="It supports yield statements.", context="Python > Generators")
    assert (
        payload_factory.build_payload(claim) == "Python > Generators\nIt supports yield statements."
    )


def test_payload_does_not_modify_claim(payload_factory):
    """Claim.text must remain unchanged — only the model input is enriched."""
    claim = make_claim(text="It supports yield.", context="Python > Generators")
    payload_factory.build_payload(claim)
    assert claim.text == "It supports yield."


def test_payload_is_deterministic(payload_factory):
    """Same claim → same payload every time."""
    claim = make_claim(text="Python is fast.", context="Programming")
    assert payload_factory.build_payload(claim) == payload_factory.build_payload(claim)


def test_instruction_prefix_applied():
    """Instruction prefix is prepended to payload when provided."""
    factory = EmbeddingInputFactory(instruction_prefix="Represent this claim: ")
    claim = make_claim(text="Python is fast.", context="")
    payload = factory.build_payload(claim)
    assert payload.startswith("Represent this claim: ")
    assert "Python is fast." in payload


def test_instruction_prefix_with_context():
    """Instruction prefix is prepended to the full context+text payload."""
    factory = EmbeddingInputFactory(instruction_prefix="Query: ")
    claim = make_claim(text="It yields values.", context="Generators")
    payload = factory.build_payload(claim)
    assert payload == "Query: Generators\nIt yields values."


# ── CacheKeyFactory tests ─────────────────────────────────────────────────────


def test_cache_key_is_32_chars(key_factory):
    """Cache key must be exactly 32 hex characters."""
    claim = make_claim()
    key = key_factory.build_cache_key(claim)
    assert len(key) == 32
    assert all(c in "0123456789abcdef" for c in key)


def test_cache_key_is_deterministic(key_factory):
    """Same claim → same cache key every time."""
    claim = make_claim(content_hash="abc123")
    assert key_factory.build_cache_key(claim) == key_factory.build_cache_key(claim)


def test_cache_key_changes_with_model_sig():
    """Different model signature → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_B", "hash_X")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_cache_key_changes_with_config_hash():
    """Different config hash → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_A", "hash_Y")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_payload_factory_and_key_factory_are_independent():
    """Changing instruction_prefix (EmbeddingInputFactory) does not affect cache keys."""
    claim = make_claim()
    factory_no_prefix = EmbeddingInputFactory()
    factory_with_prefix = EmbeddingInputFactory(instruction_prefix="Query: ")
    key_factory_shared = CacheKeyFactory("sig_A", "hash_X")

    payload_plain = factory_no_prefix.build_payload(claim)
    payload_with = factory_with_prefix.build_payload(claim)
    key = key_factory_shared.build_cache_key(claim)

    # Payloads differ but keys are the same — cache key depends on content, not enriched input
    assert payload_plain != payload_with
    assert key == key_factory_shared.build_cache_key(claim)  # Key is stable
