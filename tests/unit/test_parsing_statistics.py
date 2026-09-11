"""
Unit tests for parsing/statistics.py.

Every statistic is verified for correctness and internal consistency.
"""

import dataclasses

import pytest
from smriti.parsing.statistics import compute_statistics


def test_empty_string_returns_zeros():
    stats = compute_statistics("")
    assert stats.character_count == 0
    assert stats.word_count == 0
    assert stats.line_count == 0
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 0


def test_whitespace_only_returns_zeros():
    stats = compute_statistics("   \n\t\n  ")
    assert stats.word_count == 0
    assert stats.paragraph_count == 0


def test_single_line():
    stats = compute_statistics("Hello world")
    assert stats.character_count == 11
    assert stats.word_count == 2
    assert stats.line_count == 1
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 1


def test_two_paragraphs_with_blank_line():
    text = "First paragraph.\n\nSecond paragraph."
    stats = compute_statistics(text)
    assert stats.paragraph_count == 2
    assert stats.blank_line_count == 1
    assert stats.line_count == 3


def test_three_paragraphs():
    text = "Para 1\n\nPara 2\n\nPara 3"
    stats = compute_statistics(text)
    assert stats.paragraph_count == 3


def test_blank_line_count_never_exceeds_line_count():
    text = "\n\n\nsome text\n\n"
    stats = compute_statistics(text)
    assert stats.blank_line_count <= stats.line_count


def test_word_count_multiline():
    text = "one two\nthree four\nfive"
    stats = compute_statistics(text)
    assert stats.word_count == 5


def test_character_count_includes_whitespace():
    text = "ab cd"
    stats = compute_statistics(text)
    assert stats.character_count == 5


def test_multiline_blank_lines():
    text = "line1\n\n\n\nline2"
    stats = compute_statistics(text)
    assert stats.blank_line_count == 3  # 3 empty lines between line1 and line2
    assert stats.line_count == 5


def test_returns_frozen_dataclass():
    stats = compute_statistics("hello")
    with pytest.raises(dataclasses.FrozenInstanceError):
        stats.word_count = 999  # frozen dataclass — mutation must raise


def test_non_string_raises():
    from smriti.exceptions import StatisticsError

    with pytest.raises(StatisticsError):
        compute_statistics(123)  # type: ignore
