"""
statistics.py — Phase 3 execution statistics collector.

Responsibility:
    Collect structural metrics from one document's processing.
    Statistics are diagnostic only — they NEVER affect execution.

    Think of this as a telemetry collector.
    It observes. It never influences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import structlog

from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning

logger = structlog.get_logger(__name__)


class Phase3StatsCollector:
    """
    Mutable collector that accumulates statistics during Phase 3 processing.

    Call accumulate_event() for each ScannerEvent.
    Call record_sentence_produced() for each SemanticSentence created.
    Call record_sentence_discarded() for each discard.
    Call finalize() to get the immutable Phase3Stats result.
    """

    def __init__(self) -> None:
        self._headings = 0
        self._paragraphs = 0
        self._list_items = 0
        self._tables = 0
        self._block_quotes = 0
        self._code_blocks_skipped = 0
        self._horizontal_rules = 0
        self._front_matter_blocks = 0
        self._blank_lines = 0
        self._unknown_blocks = 0
        self._sentences_produced = 0
        self._sentences_discarded = 0
        self._warnings: List[SegmentationWarning] = []

    def accumulate_event(self, event: ScannerEvent) -> None:
        """Record a scanner event for statistics."""
        if event.block_type == BlockType.HEADING:
            self._headings += 1
        elif event.block_type == BlockType.PARAGRAPH:
            self._paragraphs += 1
        elif event.block_type in (BlockType.BULLET_ITEM, BlockType.ORDERED_ITEM):
            self._list_items += 1
        elif event.block_type == BlockType.TABLE:
            self._tables += 1
        elif event.block_type == BlockType.BLOCK_QUOTE:
            self._block_quotes += 1
        elif event.block_type == BlockType.CODE_BLOCK:
            self._code_blocks_skipped += 1
        elif event.block_type == BlockType.HORIZONTAL_RULE:
            self._horizontal_rules += 1
        elif event.block_type == BlockType.FRONT_MATTER:
            self._front_matter_blocks += 1
        elif event.block_type == BlockType.BLANK:
            self._blank_lines += 1
        else:
            self._unknown_blocks += 1

    def record_sentence_produced(self) -> None:
        self._sentences_produced += 1

    def record_sentence_discarded(self) -> None:
        self._sentences_discarded += 1

    def record_warnings(self, warnings: tuple) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase3Stats:
        """Return an immutable snapshot of accumulated statistics."""
        return Phase3Stats(
            total_headings=self._headings,
            total_paragraphs=self._paragraphs,
            total_list_items=self._list_items,
            total_tables=self._tables,
            total_block_quotes=self._block_quotes,
            total_code_blocks_skipped=self._code_blocks_skipped,
            total_horizontal_rules=self._horizontal_rules,
            total_front_matter_blocks=self._front_matter_blocks,
            total_blank_lines=self._blank_lines,
            total_unknown_blocks=self._unknown_blocks,
            sentences_produced=self._sentences_produced,
            sentences_discarded=self._sentences_discarded,
            warnings=tuple(self._warnings),
        )