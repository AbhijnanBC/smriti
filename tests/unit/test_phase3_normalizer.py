"""
Unit tests for extraction/normalizer.py.
"""

import pytest
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.extraction.normalizer import normalize_event
from smriti.core.models import SegmentationWarning


def make_event(block_type, text, heading_level=None, lines=None):
    return ScannerEvent(
        block_type=block_type,
        text=text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=tuple(lines or [text]),
    )


def test_paragraph_passes_through():
    event = make_event(BlockType.PARAGRAPH, "Python is great for data science.")
    block = normalize_event(event)
    assert block.prose == "Python is great for data science."
    assert block.skip is False


def test_heading_is_skipped():
    """Headings must produce no prose — they are context only."""
    event = make_event(BlockType.HEADING, "Python", heading_level=1)
    block = normalize_event(event)
    assert block.skip is True
    assert block.prose == ""


def test_bullet_item_normalized():
    event = make_event(BlockType.BULLET_ITEM, "Use Poetry for dependency management")
    block = normalize_event(event)
    assert "Use Poetry" in block.prose
    assert block.skip is False


def test_bullet_item_gets_period():
    """Bullet items without trailing period must get one added."""
    event = make_event(BlockType.BULLET_ITEM, "No trailing period")
    block = normalize_event(event)
    assert block.prose.endswith(".")


def test_block_quote_normalized():
    event = make_event(BlockType.BLOCK_QUOTE, "Reliability is critical")
    block = normalize_event(event)
    assert "Reliability" in block.prose
    assert block.skip is False


def test_code_block_skipped():
    event = make_event(BlockType.CODE_BLOCK, "print('hello')")
    block = normalize_event(event)
    assert block.skip is True
    assert SegmentationWarning.SEG_CODE_BLOCK_SKIPPED in block.warnings


def test_horizontal_rule_skipped():
    event = make_event(BlockType.HORIZONTAL_RULE, "")
    block = normalize_event(event)
    assert block.skip is True


def test_table_normalized_to_prose():
    """Table rows become key-value prose sentences."""
    lines = [
        "| Model | Accuracy |",
        "|-------|----------|",
        "| GPT-4 | 85%      |",
    ]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert not block.skip
    assert "Model" in block.prose or "GPT-4" in block.prose


def test_malformed_table_emits_warning():
    """A table with only a separator produces SEG_MALFORMED_TABLE."""
    lines = ["|------|"]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert SegmentationWarning.SEG_MALFORMED_TABLE in block.warnings