"""
Unit tests for extraction/segmenter.py.
"""

import pytest
from smriti.extraction.segmenter import SentenceSegmenter


@pytest.fixture
def segmenter():
    return SentenceSegmenter()


def test_single_sentence(segmenter):
    result = segmenter.segment("Python is great for data science.")
    assert len(result) == 1
    assert result[0].text == "Python is great for data science."


def test_two_sentences(segmenter):
    result = segmenter.segment(
        "Python is great for data science. Julia is faster for numerical computing."
    )
    assert len(result) == 2


def test_question_mark_splits(segmenter):
    result = segmenter.segment(
        "Is Python good? Yes, it is very good."
    )
    assert len(result) == 2


def test_exclamation_splits(segmenter):
    result = segmenter.segment(
        "This works! Now let's move on."
    )
    assert len(result) == 2


def test_abbreviation_dr_does_not_split(segmenter):
    """'Dr. Smith' must not split into two sentences."""
    result = segmenter.segment("Dr. Smith visited the lab.")
    assert len(result) == 1


def test_abbreviation_eg_does_not_split(segmenter):
    """'e.g. Python' must not split."""
    result = segmenter.segment("Use a high-level language, e.g. Python or Julia.")
    assert len(result) == 1


def test_abbreviation_ie_does_not_split(segmenter):
    """'i.e. that' must not split."""
    result = segmenter.segment("Use the right tool, i.e. the simplest one.")
    assert len(result) == 1


def test_decimal_number_does_not_split(segmenter):
    """'3.14' must not split."""
    result = segmenter.segment("Pi is approximately 3.14 and it is irrational.")
    assert len(result) == 1


def test_empty_prose_returns_empty(segmenter):
    result = segmenter.segment("")
    assert result == []


def test_whitespace_only_returns_empty(segmenter):
    result = segmenter.segment("   \n\n   ")
    assert result == []


def test_sentence_text_is_stripped(segmenter):
    """Sentence text must not have leading/trailing whitespace."""
    result = segmenter.segment("  Python is great.  Julia is fast.  ")
    for s in result:
        assert s.text == s.text.strip()


def test_positions_are_non_negative(segmenter):
    result = segmenter.segment("First sentence. Second sentence.")
    for s in result:
        assert s.char_start >= 0
        assert s.char_end > s.char_start


def test_three_sentences(segmenter):
    text = "First. Second. Third."
    result = segmenter.segment(text)
    assert len(result) == 3


def test_very_long_sentence_emits_warning(segmenter):
    """A sentence exceeding max_sentence_chars must emit SEG002."""
    from smriti.core.models import SegmentationWarning
    # Build text guaranteed to exceed the segmenter's actual configured
    # threshold (config/test.yaml sets max_sentence_chars=5000, higher than
    # config/default.yaml's 2000) rather than assuming the default value.
    word_count = (segmenter._max_chars // len("word ")) + 10
    long_text = "word " * word_count + "."
    result = segmenter.segment(long_text)
    assert len(result) == 1
    assert SegmentationWarning.SEG_VERY_LONG_SENTENCE in result[0].warnings