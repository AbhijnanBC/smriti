"""Unit tests for classification/relatedness.py (P0-6 relatedness gate)."""

from smriti.retrieval.classification.relatedness import (
    compute_relatedness,
    passes_contradiction_relatedness_gate,
)


def test_unrelated_claims_score_zero():
    """Two claims with no shared vocabulary or entities should score 0."""
    text_a = "The mitochondria is the powerhouse of the cell."
    text_b = "Wrist spinners are more economical than finger spinners in T20."
    score = compute_relatedness(text_a, text_b)
    assert score == 0.0


def test_related_claims_via_shared_content_words():
    text_a = "Pressure cooking destroys the collagen structure of lamb."
    text_b = "Pressure cooking makes lamb tender through collagen breakdown."
    score = compute_relatedness(text_a, text_b)
    assert score > 0.0


def test_shared_entity_boosts_relatedness_even_with_different_vocabulary():
    text_a = "U-Net is the state-of-the-art architecture for segmentation."
    text_b = "Transformers have made U-Net obsolete according to recent benchmarks."
    score = compute_relatedness(text_a, text_b)
    assert score >= 0.5  # shared capitalized token "U-Net" triggers the entity bonus


def test_gate_blocks_zero_relatedness_pair():
    text_a = "Python supports generators and decorators."
    text_b = "Jupiter has 95 known moons as of the latest count."
    assert not passes_contradiction_relatedness_gate(text_a, text_b, min_relatedness=0.03)


def test_gate_allows_related_pair():
    text_a = "The pressure cooker produces tender lamb in 20 minutes."
    text_b = "The pressure cooker leaves the lamb dry and tough."
    assert passes_contradiction_relatedness_gate(text_a, text_b, min_relatedness=0.03)


def test_empty_text_scores_zero():
    assert compute_relatedness("", "Something with content here.") == 0.0
    assert compute_relatedness("Something with content here.", "") == 0.0
