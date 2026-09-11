"""Unit tests for api/domain/predicates.py."""

from smriti.api.domain.predicates import Pagination, Predicate
from smriti.core.models import PredicateOperator


def test_predicate_eq():
    p = Predicate("calibration_label", PredicateOperator.EQ, "high")
    assert p.matches("high") is True and p.matches("moderate") is False


def test_predicate_gte():
    p = Predicate("reliability_index", PredicateOperator.GTE, 80.0)
    assert p.matches(85.0) is True and p.matches(80.0) is True and p.matches(79.9) is False


def test_predicate_lte():
    p = Predicate("uncertainty_score", PredicateOperator.LTE, 30.0)
    assert p.matches(25.0) is True and p.matches(30.0) is True and p.matches(30.1) is False


def test_predicate_in():
    p = Predicate("semantic_role", PredicateOperator.IN, {"foundational_claim", "bridge_claim"})
    assert p.matches("foundational_claim") is True and p.matches("peripheral_claim") is False


def test_predicate_type_error_returns_false():
    p = Predicate("reliability_index", PredicateOperator.GT, "not_a_number")
    assert p.matches(80.0) is False


def test_pagination_clamps_limit():
    p = Pagination(limit=9999)
    assert p.limit == 1000
    p2 = Pagination(limit=0)
    assert p2.limit == 1


def test_pagination_clamps_offset():
    p = Pagination(offset=-5)
    assert p.offset == 0
