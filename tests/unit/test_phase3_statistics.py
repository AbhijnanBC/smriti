"""
Unit tests for extraction/statistics.py.
"""

import pytest
from smriti.extraction.statistics import Phase3StatsCollector
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning


def make_event(block_type: BlockType, text: str = "", heading_level: int = None) -> ScannerEvent:
    return ScannerEvent(
        block_type=block_type,
        text=text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=(text,),
    )


def test_stats_collector_counts_all_block_types():
    collector = Phase3StatsCollector()

    # Generate one of each block type
    events = [
        make_event(BlockType.HEADING, "H1", heading_level=1),
        make_event(BlockType.PARAGRAPH, "paragraph"),
        make_event(BlockType.BULLET_ITEM, "bullet"),
        make_event(BlockType.ORDERED_ITEM, "ordered"),
        make_event(BlockType.TABLE, "table"),
        make_event(BlockType.BLOCK_QUOTE, "quote"),
        make_event(BlockType.CODE_BLOCK, "code"),
        make_event(BlockType.HORIZONTAL_RULE, "---"),
        make_event(BlockType.FRONT_MATTER, "---"),
        make_event(BlockType.BLANK, ""),
        make_event(BlockType.UNKNOWN, "unknown"),  # This should be counted as unknown
    ]

    for event in events:
        collector.accumulate_event(event)

    # Record some sentences
    for _ in range(5):
        collector.record_sentence_produced()
    for _ in range(2):
        collector.record_sentence_discarded()

    # Record a warning
    collector.record_warnings((SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,))

    stats = collector.finalize()

    assert isinstance(stats, Phase3Stats)
    assert stats.total_headings == 1
    assert stats.total_paragraphs == 1
    assert stats.total_list_items == 2  # bullet + ordered
    assert stats.total_tables == 1
    assert stats.total_block_quotes == 1
    assert stats.total_code_blocks_skipped == 1
    assert stats.total_horizontal_rules == 1
    assert stats.total_front_matter_blocks == 1
    assert stats.total_blank_lines == 1
    assert stats.total_unknown_blocks == 1  # the UNKNOWN event
    assert stats.sentences_produced == 5
    assert stats.sentences_discarded == 2
    assert len(stats.warnings) == 1
    assert stats.warnings[0] == SegmentationWarning.SEG_CODE_BLOCK_SKIPPED


def test_stats_collector_empty_document():
    collector = Phase3StatsCollector()
    stats = collector.finalize()

    assert stats.total_headings == 0
    assert stats.total_paragraphs == 0
    assert stats.total_list_items == 0
    assert stats.total_tables == 0
    assert stats.total_block_quotes == 0
    assert stats.total_code_blocks_skipped == 0
    assert stats.total_horizontal_rules == 0
    assert stats.total_front_matter_blocks == 0
    assert stats.total_blank_lines == 0
    assert stats.total_unknown_blocks == 0
    assert stats.sentences_produced == 0
    assert stats.sentences_discarded == 0
    assert len(stats.warnings) == 0