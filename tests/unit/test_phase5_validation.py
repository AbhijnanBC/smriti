"""
Unit tests for embedding/validation.py.
Includes dtype validation and post-normalization scenario.
"""

import pytest
import math
from smriti.embedding.validation import validate_vector, validate_batch


def test_valid_vector_passes():
    vector = [0.1, 0.2, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True
    assert error is None


def test_empty_vector_fails():
    is_valid, error = validate_vector([], expected_dimension=4)
    assert is_valid is False
    assert "empty" in error.lower()


def test_wrong_dimension_fails():
    vector = [0.1, 0.2, 0.3]  # 3 elements, expected 4
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "dimension" in error.lower()


def test_nan_fails():
    vector = [0.1, float("nan"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "nan" in error.lower()


def test_inf_fails():
    vector = [0.1, float("inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "inf" in error.lower()


def test_negative_inf_fails():
    vector = [0.1, float("-inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_zero_norm_fails():
    vector = [0.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "zero" in error.lower()


def test_unit_vector_passes():
    vector = [1.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True


def test_dtype_string_fails():
    """Non-numeric (string) type in vector must fail."""
    vector = [0.1, "bad", 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "type" in error.lower() or "non-numeric" in error.lower()


def test_dtype_none_fails():
    """None in vector must fail."""
    vector = [0.1, None, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_validate_batch_all_valid():
    vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    results = validate_batch(vectors, expected_dimension=3)
    assert all(valid for valid, _ in results)


def test_validate_batch_mixed():
    vectors = [
        [0.1, 0.2, 0.3],
        [float("nan"), 0.2, 0.3],
    ]
    results = validate_batch(vectors, expected_dimension=3)
    assert results[0][0] is True
    assert results[1][0] is False


def test_post_normalization_valid_unit_vector():
    """A correctly normalized unit vector must pass post-norm validation."""
    import math
    vector = [1.0, 0.0, 0.0, 0.0]
    norm = math.sqrt(sum(x * x for x in vector))
    normalized = [x / norm for x in vector]
    is_valid, error = validate_vector(normalized, expected_dimension=4)
    assert is_valid is True