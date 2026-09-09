"""
Property-based tests for Phase 5 using Hypothesis.

These tests verify mathematical invariants that must hold for ALL valid inputs,
not just the specific cases covered by example-based tests.

Install: poetry add --group dev hypothesis
"""

import math
import pytest

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

pytestmark = pytest.mark.skipif(
    not HAS_HYPOTHESIS,
    reason="hypothesis not installed — run: poetry add --group dev hypothesis"
)


# ── Normalization invariants ──────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.normalization import l2_normalize

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
    def test_property_l2_normalize_always_unit_norm(values):
        """For ANY non-zero vector, L2 norm after normalization is always 1.0."""
        assume(sum(x * x for x in values) > 0)  # exclude zero vectors
        normalized = l2_normalize(values)
        norm = math.sqrt(sum(x * x for x in normalized))
        assert abs(norm - 1.0) < 1e-5, f"norm={norm} for input {values[:4]}..."


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
    def test_property_l2_normalize_does_not_mutate_input(values):
        """l2_normalize must never mutate the input list."""
        original = list(values)
        assume(sum(x * x for x in values) > 0)
        l2_normalize(values)
        assert values == original


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=200)
    def test_property_normalize_twice_is_idempotent(values):
        """Normalizing a unit vector again must yield the same unit vector."""
        assume(sum(x * x for x in values) > 0)
        once = l2_normalize(values)
        twice = l2_normalize(once)
        for a, b in zip(once, twice):
            assert abs(a - b) < 1e-5


# ── Cache key invariants ──────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.input_factory import CacheKeyFactory

    @given(
        text=st.text(min_size=1, max_size=1000),
        model_sig=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
        config_hash=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
    )
    @settings(max_examples=200)
    def test_property_cache_key_always_32_hex_chars(text, model_sig, config_hash):
        """For ANY text and signatures, cache key is always exactly 32 hex chars."""
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
        )
        import hashlib

        claim = Claim(
            claim_id="c001",
            sentence_id="s001",
            document_id="d001",
            text=text,
            context="",
            source_path=Path("test.md"),
            extraction_mode=ExtractionMode.WHOLE_SENTENCE,
            structured_assertion=None,
            assertion_metadata=AssertionMetadata(),
            provenance=ClaimProvenance(
                sentence_id="s001", document_id="d001",
                source_path=Path("test.md"), sentence_context="",
                sentence_position=0,
            ),
            schema_version="4.0",
            content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            rule_version="1.0",
        )

        factory = CacheKeyFactory(model_signature=model_sig, config_hash=config_hash)
        key = factory.build_cache_key(claim)
        assert len(key) == 32
        assert all(c in "0123456789abcdef" for c in key)


# ── Validation invariants ─────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.validation import validate_vector

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
    def test_property_valid_nonzero_vector_passes_validation(values):
        """Any non-NaN, non-Inf, non-zero-norm vector passes validation."""
        assume(any(x != 0.0 for x in values))
        is_valid, error = validate_vector(values, expected_dimension=len(values))
        assert is_valid is True, f"Expected valid but got error: {error}"


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        ),
        wrong_dim=st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=200)
    def test_property_wrong_dimension_always_fails(values, wrong_dim):
        """Validation always fails when dimension doesn't match."""
        assume(wrong_dim != len(values))
        is_valid, error = validate_vector(values, expected_dimension=wrong_dim)
        assert is_valid is False


# ── Vector domain object invariants ──────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.builders import build_vector

    @given(
        size=st.integers(min_value=1, max_value=512),
        normalized=st.booleans(),
    )
    @settings(max_examples=200)
    def test_property_build_vector_dimension_always_consistent(size, normalized):
        """build_vector.dimension must always equal len(values)."""
        values = [0.1] * size  # Non-zero, all same, valid
        vec = build_vector(values, size, normalized=normalized)
        assert vec.dimension == size
        assert len(vec.values) == size
        assert vec.normalized == normalized