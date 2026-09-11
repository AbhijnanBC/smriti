"""Unit tests for evaluation/philosophy/principles.py."""

import pytest
from smriti.evaluation.philosophy.principles import VALIDATION_PRINCIPLES, get_principle


def test_eight_principles_defined():
    assert len(VALIDATION_PRINCIPLES) == 8


def test_principles_numbered_1_through_8():
    numbers = [p.number for p in VALIDATION_PRINCIPLES]
    assert sorted(numbers) == list(range(1, 9))


def test_each_principle_has_name_and_statement():
    for p in VALIDATION_PRINCIPLES:
        assert p.name, f"Principle {p.number} has empty name"
        assert p.statement, f"Principle {p.number} has empty statement"


def test_get_principle_by_number():
    p1 = get_principle(1)
    assert "Evidence" in p1.name


def test_get_invalid_principle_raises():
    with pytest.raises(KeyError):
        get_principle(99)


def test_all_principles_are_frozen():
    p = get_principle(1)
    with pytest.raises(Exception):
        p.name = "Modified"
