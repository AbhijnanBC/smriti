"""
Unit tests for classification/evidence.py's bidirectional NLI generation
(NLIEvidenceGenerator._process_batch), added for the external-review-driven
rewrite that runs the cross-encoder on both (claim_a, claim_b) and
(claim_b, claim_a) orderings instead of one fixed direction.

Constructs NLIEvidenceGenerator without calling __init__ (which loads a
real HuggingFace model) and injects a fake ._model with a scripted
.predict() so no model download or GPU/CPU inference is needed.
"""

from pathlib import Path

import pytest
from smriti.core.models import (
    AssertionMetadata,
    CandidatePair,
    Claim,
    ClaimProvenance,
    ExtractionMode,
)
from smriti.exceptions import NLIEvaluationInferenceFailureError
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator


class _FakeSoftmaxScores:
    """Mimics the numpy array .tolist() interface CrossEncoder.predict returns."""

    def __init__(self, rows: list[list]):
        self._rows = rows

    def tolist(self):
        return self._rows


class _FakeCrossEncoder:
    """Records every call's text_pairs and returns pre-scripted rows in order."""

    def __init__(self, scripted_rows: list[list]):
        self._scripted_rows = scripted_rows
        self.calls: list[list] = []

    def predict(self, text_pairs, apply_softmax=True, show_progress_bar=False):
        self.calls.append(list(text_pairs))
        assert len(text_pairs) == len(self._scripted_rows), (
            "test fixture mismatch: scripted_rows must match the batch size "
            "of the single combined predict() call"
        )
        return _FakeSoftmaxScores(self._scripted_rows)


def make_claim(claim_id: str, text: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id="d001",
        text=text,
        content_hash=claim_id[:16],
        context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001",
            document_id="d001",
            source_path=Path("test.md"),
            sentence_context="",
            sentence_position=0,
        ),
        schema_version="4.0",
        rule_version="1.0",
    )


def make_generator(scripted_rows: list[list]) -> NLIEvidenceGenerator:
    """Build an NLIEvidenceGenerator instance bypassing __init__ (no real
    model load), with a fake CrossEncoder returning scripted_rows."""
    gen = NLIEvidenceGenerator.__new__(NLIEvidenceGenerator)
    gen._model_name = "fake-nli"
    gen._batch_size = 16
    gen._model = _FakeCrossEncoder(scripted_rows)
    gen._model_revision = "fake-rev"
    gen._device = "cpu"
    gen._is_eval_env = False
    gen._allow_inference_failures = False
    gen.last_run_stats = {}
    return gen


# _LABEL_INDEX order is ["contradiction", "entailment", "neutral"]


def test_generates_both_directions_for_one_pair():
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.85, candidate_rank=1
    )
    claims_map = {
        "c001": make_claim("c001", "The Aurora server uses 8 GB of RAM."),
        "c002": make_claim("c002", "The Aurora server has 8 GB of RAM installed."),
    }
    # Row 0 = AB direction (a premise, b hypothesis); row 1 = BA direction.
    scripted = [
        [0.02, 0.95, 0.03],  # AB: strong entailment
        [0.03, 0.90, 0.07],  # BA: strong entailment (both directions -> would resolve EQUIVALENT)
    ]
    gen = make_generator(scripted)
    evidence_list = gen._process_batch([pair], claims_map)

    assert len(evidence_list) == 1
    evidence = evidence_list[0]
    assert evidence.nli_scores_b_to_a is not None
    assert evidence.nli_scores.entailment_score == pytest.approx(0.95)
    assert evidence.nli_scores_b_to_a.entailment_score == pytest.approx(0.90)


def test_directions_are_not_swapped():
    """AB and BA must map to the correct halves of the combined batch, not
    be accidentally transposed."""
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.85, candidate_rank=1
    )
    claims_map = {
        "c001": make_claim("c001", "A entails B but not vice versa."),
        "c002": make_claim("c002", "B does not entail A."),
    }
    scripted = [
        [0.01, 0.97, 0.02],  # AB: strong entailment
        [0.05, 0.10, 0.85],  # BA: neutral-dominant, no entailment
    ]
    gen = make_generator(scripted)
    evidence = gen._process_batch([pair], claims_map)[0]

    assert evidence.nli_scores.predicted_label == "entailment"
    assert evidence.nli_scores_b_to_a.predicted_label == "neutral"
    assert evidence.nli_scores.entailment_score == pytest.approx(0.97)
    assert evidence.nli_scores_b_to_a.neutral_score == pytest.approx(0.85)


def test_batch_makes_one_combined_predict_call_not_two():
    """Both directions for every pair in the batch must be sent to the
    model in a SINGLE predict() call (ab half then ba half), preserving
    batching throughput rather than doubling Python-level round trips."""
    pair_1 = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.85, candidate_rank=1
    )
    pair_2 = CandidatePair(
        claim_id_a="c003", claim_id_b="c004", cosine_similarity=0.80, candidate_rank=1
    )
    claims_map = {
        "c001": make_claim("c001", "text a1"),
        "c002": make_claim("c002", "text b1"),
        "c003": make_claim("c003", "text a2"),
        "c004": make_claim("c004", "text b2"),
    }
    scripted = [[0.1, 0.1, 0.8]] * 4  # 2 pairs x 2 directions = 4 rows
    gen = make_generator(scripted)
    gen._process_batch([pair_1, pair_2], claims_map)

    assert len(gen._model.calls) == 1, "expected exactly one combined predict() call"
    combined = gen._model.calls[0]
    assert len(combined) == 4
    # First half is AB order, second half is BA order, same pair order throughout.
    assert combined[0] == ("text a1", "text b1")
    assert combined[1] == ("text a2", "text b2")
    assert combined[2] == ("text b1", "text a1")
    assert combined[3] == ("text b2", "text a2")


def test_missing_claim_is_skipped_for_both_directions():
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="missing", cosine_similarity=0.85, candidate_rank=1
    )
    claims_map = {"c001": make_claim("c001", "text a")}
    gen = make_generator([])
    evidence_list = gen._process_batch([pair], claims_map)
    assert evidence_list == []


# ── P1-I regression tests ("FINAL REVIEW" round): NLI batch-failure
#    accounting must not silently disappear -- generate_batch() must
#    report real attempted/scored/failure counts and, in an evaluation
#    run, fail loudly on any inference failure unless explicitly
#    permitted. ─────────────────────────────────────────────────────────


class _AlwaysFailingCrossEncoder:
    def predict(self, text_pairs, apply_softmax=True, show_progress_bar=False):
        raise RuntimeError("simulated NLI inference failure")


def make_failing_generator(is_eval_env: bool, allow_failures: bool = False) -> NLIEvidenceGenerator:
    gen = NLIEvidenceGenerator.__new__(NLIEvidenceGenerator)
    gen._model_name = "fake-nli"
    gen._batch_size = 16
    gen._model = _AlwaysFailingCrossEncoder()
    gen._model_revision = "fake-rev"
    gen._device = "cpu"
    gen._is_eval_env = is_eval_env
    gen._allow_inference_failures = allow_failures
    gen.last_run_stats = {}
    return gen


def _one_pair_and_claims():
    pair = CandidatePair(
        claim_id_a="c001", claim_id_b="c002", cosine_similarity=0.85, candidate_rank=1
    )
    claims_map = {"c001": make_claim("c001", "text a"), "c002": make_claim("c002", "text b")}
    return [pair], claims_map


def test_production_env_skips_failed_batch_without_raising(monkeypatch):
    monkeypatch.setattr("smriti.retrieval.classification.evidence.time.sleep", lambda s: None)
    gen = make_failing_generator(is_eval_env=False)
    pairs, claims_map = _one_pair_and_claims()
    results = gen.generate_batch(pairs, claims_map)
    assert results == []
    assert gen.last_run_stats["n_candidates_attempted"] == 1
    assert gen.last_run_stats["n_candidates_scored"] == 0
    assert gen.last_run_stats["n_batch_failures"] == 1


def test_eval_env_raises_on_batch_failure_by_default(monkeypatch):
    monkeypatch.setattr("smriti.retrieval.classification.evidence.time.sleep", lambda s: None)
    gen = make_failing_generator(is_eval_env=True, allow_failures=False)
    pairs, claims_map = _one_pair_and_claims()
    with pytest.raises(NLIEvaluationInferenceFailureError):
        gen.generate_batch(pairs, claims_map)


def test_eval_env_permits_failure_when_explicitly_allowed(monkeypatch):
    monkeypatch.setattr("smriti.retrieval.classification.evidence.time.sleep", lambda s: None)
    gen = make_failing_generator(is_eval_env=True, allow_failures=True)
    pairs, claims_map = _one_pair_and_claims()
    results = gen.generate_batch(pairs, claims_map)
    assert results == []
    assert gen.last_run_stats["n_batch_failures"] == 1


def test_successful_batch_reports_retries_and_scored_count(monkeypatch):
    monkeypatch.setattr("smriti.retrieval.classification.evidence.time.sleep", lambda s: None)
    gen = make_generator([[0.1, 0.8, 0.1], [0.1, 0.8, 0.1]])
    pairs, claims_map = _one_pair_and_claims()
    results = gen.generate_batch(pairs, claims_map)
    assert len(results) == 1
    assert gen.last_run_stats["n_candidates_attempted"] == 1
    assert gen.last_run_stats["n_candidates_scored"] == 1
    assert gen.last_run_stats["n_batch_failures"] == 0
    assert gen.last_run_stats["n_retries"] == 0
