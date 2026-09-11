"""
Unit tests for embedding/normalization.py.
"""

import math

from smriti.embedding.normalization import l2_normalize, normalize_batch


def l2_norm(v):
    return math.sqrt(sum(x * x for x in v))


def test_l2_normalize_produces_unit_vector():
    vector = [3.0, 4.0]  # norm = 5.0
    normalized = l2_normalize(vector)
    assert abs(l2_norm(normalized) - 1.0) < 1e-6


def test_l2_normalize_direction_preserved():
    vector = [3.0, 4.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] / normalized[1] - 3.0 / 4.0) < 1e-6


def test_l2_normalize_returns_new_list():
    vector = [1.0, 2.0, 3.0]
    original = list(vector)
    _ = l2_normalize(vector)
    assert vector == original  # Original unchanged


def test_l2_normalize_already_unit_vector():
    vector = [1.0, 0.0, 0.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] - 1.0) < 1e-6
    assert abs(normalized[1]) < 1e-6


def test_normalize_batch_applies_to_all():
    vectors = [[3.0, 4.0], [1.0, 0.0], [0.6, 0.8]]
    normalized = normalize_batch(vectors, enabled=True)
    for v in normalized:
        assert abs(l2_norm(v) - 1.0) < 1e-6


def test_normalize_batch_disabled():
    vectors = [[3.0, 4.0], [1.0, 2.0]]
    result = normalize_batch(vectors, enabled=False)
    for i, v in enumerate(result):
        assert v == [float(x) for x in vectors[i]]


def test_normalize_384_dim():
    """Must work correctly on 384-dimensional vectors (MiniLM)."""
    import random

    random.seed(42)
    vector = [random.uniform(-1, 1) for _ in range(384)]
    normalized = l2_normalize(vector)
    assert len(normalized) == 384
    assert abs(l2_norm(normalized) - 1.0) < 1e-5
