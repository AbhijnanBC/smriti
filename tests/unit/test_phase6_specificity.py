"""Unit tests for classification/specificity.py (SUPPORTS/REFINES disambiguation)."""

from smriti.retrieval.classification.specificity import (
    compute_specificity,
    is_refinement,
    specificity_delta,
)


def test_more_detailed_text_has_higher_specificity():
    generic = "Transformers outperform U-Net on benchmark X."
    detailed = "Transformers outperform U-Net on benchmark X for medical segmentation in 2023."
    assert compute_specificity(detailed) > compute_specificity(generic)


def test_numeric_content_increases_specificity():
    with_number = "The Aurora server uses 8 GB of RAM."
    without_number = "The Aurora server uses a lot of RAM."
    assert compute_specificity(with_number) > compute_specificity(without_number)


def test_date_content_increases_specificity():
    with_date = "As of January 2024, the Vantage API is deprecated."
    without_date = "The Vantage API is deprecated."
    assert compute_specificity(with_date) > compute_specificity(without_date)


def test_specificity_delta_is_antisymmetric():
    a = "The Norwich scheduler reduces average job latency."
    b = "Independent benchmarks confirm the Norwich scheduler significantly lowers job latency in 2023."
    assert specificity_delta(a, b) == -specificity_delta(b, a)


def test_is_refinement_true_when_entailing_claim_much_more_specific():
    entailing = "Transformers outperform U-Net on benchmark X for medical segmentation in 2023."
    entailed = "Transformers outperform U-Net."
    assert is_refinement(entailing, entailed, margin=3.0)


def test_is_refinement_false_when_claims_are_similarly_specific():
    """Independent confirmation of the same claim at roughly the same
    level of detail should NOT be classified as a refinement."""
    entailing = "Tests confirm the Norwich scheduler reduces job latency."
    entailed = "The Norwich scheduler reduces job latency."
    assert not is_refinement(entailing, entailed, margin=3.0)


def test_attribution_cue_words_never_count_as_added_specificity():
    """RECTIFIED (external "reality check" review round 3, P0-B.5):
    previously, "independent benchmarks confirm that X" WAS classified as
    a refinement of "X" purely because the attribution wrapper words
    ("independent", "benchmarks", "confirm") inflated the raw content-
    token count past the default margin -- a real, measured bug (the
    exact case this test file's own prior docstring called a "documented
    ambiguity" rather than a bug). Evidentiary attribution is SUPPORTS,
    never REFINES: it adds no semantic content about the claim, only
    provenance for it. This is no longer ambiguous; it must be False."""
    entailed = "The Aurora Engine reduces average job latency."
    for entailing in [
        "Independent benchmarks confirm that the Aurora Engine reduces average job latency.",
        "An internal review independently confirmed that the Aurora Engine reduces average job latency.",
        "A separate audit found that the Aurora Engine reduces average job latency.",
        "External testing verified that the Aurora Engine reduces average job latency.",
    ]:
        assert not is_refinement(
            entailing, entailed, margin=3.0
        ), f"attribution wrapper wrongly counted as refinement: {entailing!r}"


def test_genuine_refinement_still_detected_alongside_attribution_language():
    """The attribution-cue exclusion must not blind the heuristic to a
    REAL refinement that happens to also use a reporting verb."""
    entailed = "The Aurora Engine improves compilation speed."
    entailing = "A benchmark study found the Aurora Engine improves compilation speed for large projects exceeding 50 files, measured across three independent test suites in 2024."
    assert is_refinement(entailing, entailed, margin=3.0)


def test_is_refinement_false_when_entailed_claim_is_more_specific():
    """If the ENTAILED claim is the more specific one, this is not a
    refinement in the entailing direction."""
    entailing = "GPUs are used in the Aurora server."
    entailed = "The Aurora server uses 8 GB of RAM on its NVIDIA A100 GPUs as of 2024."
    assert not is_refinement(entailing, entailed, margin=3.0)


def test_specificity_is_deterministic():
    text = "The Falcon model supports GPU execution as of 2024."
    assert compute_specificity(text) == compute_specificity(text) == compute_specificity(text)
