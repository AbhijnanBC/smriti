"""
Unit tests for governance.py's ResourceGovernor.evaluation_truncated flag
and statistics.py's DiscoveryReport carrying it (P1-J, "FINAL REVIEW"
round): a truncated evaluation run must not be able to report headline
metrics without a visible signal that truncation happened.
"""

import pytest
from smriti.core.models import CandidatePair
from smriti.exceptions import ResourceLimitExceeded
from smriti.retrieval.governance import ResourceGovernor, ResourceLimits
from smriti.retrieval.statistics import Phase6StatsCollector


def make_limits(max_pairs: int, cancel_on_limit: bool) -> ResourceLimits:
    limits = ResourceLimits.__new__(ResourceLimits)
    limits.max_pairs = max_pairs
    limits.max_gpu_memory_gb = 0.0
    limits.max_batch_size = 64
    limits.timeout_seconds = 3600.0
    limits.cancel_on_limit = cancel_on_limit
    return limits


def make_candidates(n: int):
    return [
        CandidatePair(
            claim_id_a=f"a{i}",
            claim_id_b=f"b{i}",
            cosine_similarity=1.0 - i * 0.001,
            candidate_rank=1,
        )
        for i in range(n)
    ]


def test_truncation_sets_evaluation_truncated_flag_when_not_cancel_on_limit():
    governor = ResourceGovernor(limits=make_limits(max_pairs=5, cancel_on_limit=False))
    assert governor.evaluation_truncated is False
    result = governor.enforce_pair_limit(make_candidates(10))
    assert len(result) == 5
    assert governor.evaluation_truncated is True


def test_no_truncation_leaves_flag_false():
    governor = ResourceGovernor(limits=make_limits(max_pairs=10, cancel_on_limit=False))
    result = governor.enforce_pair_limit(make_candidates(5))
    assert len(result) == 5
    assert governor.evaluation_truncated is False


def test_cancel_on_limit_raises_instead_of_truncating():
    governor = ResourceGovernor(limits=make_limits(max_pairs=5, cancel_on_limit=True))
    with pytest.raises(ResourceLimitExceeded):
        governor.enforce_pair_limit(make_candidates(10))


def test_discovery_report_carries_truncation_and_nli_failure_stats():
    stats = Phase6StatsCollector()
    stats.record_truncation(True)
    stats.record_nli_run_stats(
        {
            "n_candidates_attempted": 100,
            "n_candidates_scored": 80,
            "n_batch_failures": 2,
            "n_retries": 3,
        }
    )
    report = stats.finalize()
    assert report.evaluation_truncated is True
    assert report.nli_candidates_attempted == 100
    assert report.nli_candidates_scored == 80
    assert report.nli_batch_failures == 2
    assert report.nli_retries == 3


def test_discovery_report_defaults_to_not_truncated():
    stats = Phase6StatsCollector()
    report = stats.finalize()
    assert report.evaluation_truncated is False
    assert report.nli_batch_failures == 0
