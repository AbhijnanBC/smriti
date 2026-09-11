"""
normalizer.py — Structured content normaliser for Phase 3.

Responsibility:
    Convert structured content (tables, lists, etc.) into canonical prose strings.
    Pass paragraph and list text through unchanged.
    Emit warnings for malformed structures.

Input:  ScannerEvent
Output: NormalizedBlock

Design:
    Each normaliser strategy handles one BlockType.
    Adding support for a new format = adding one strategy.
    No if/elif chains allowed.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from smriti.core.models import SegmentationWarning
from smriti.extraction.rules import TABLE_KV_TEMPLATE, TABLE_SEPARATOR_PATTERN
from smriti.extraction.scanner import BlockType, ScannerEvent

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class NormalizedBlock:
    """
    Result of normalising a single ScannerEvent into prose.

    Fields:
        prose:       The normalised text ready for sentence segmentation.
                     For headings: empty (headings become context only).
        block_type:  The original block type (for statistics and provenance).
        char_start:  Character start from original event.
        char_end:    Character end from original event.
        warnings:    Any warnings emitted during normalisation.
        skip:        If True, this block produces no sentences (headings, code, etc.)
    """

    prose: str
    block_type: BlockType
    char_start: int
    char_end: int
    warnings: tuple
    skip: bool = False  # True for headings, code blocks, etc.


def normalize_event(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a ScannerEvent into a NormalizedBlock.

    Dispatches to the appropriate strategy based on block_type.
    """
    strategy = _NORMALIZERS.get(event.block_type, _normalize_unknown)
    return strategy(event)


# ── Strategy implementations ──────────────────────────────────────────────────


def _normalize_paragraph(event: ScannerEvent) -> NormalizedBlock:
    """Paragraphs pass through unchanged."""
    return NormalizedBlock(
        prose=event.text.strip(),
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_heading(event: ScannerEvent) -> NormalizedBlock:
    """
    Headings become context only — they produce no sentences.
    The caller (orchestrator) updates the context stack.
    """
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,  # Headings do NOT produce sentences
    )


def _normalize_bullet_item(event: ScannerEvent) -> NormalizedBlock:
    """Bullet list items become single prose sentences."""
    text = event.text.strip()
    if text and text[-1] not in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_ordered_item(event: ScannerEvent) -> NormalizedBlock:
    """Ordered list items are treated identically to bullet items."""
    return _normalize_bullet_item(event)


def _normalize_block_quote(event: ScannerEvent) -> NormalizedBlock:
    """Block quotes pass through as prose."""
    text = event.text.strip()
    if text and text[-1] not in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_table(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a Markdown table into canonical prose.

    Strategy:
        | Model | Accuracy |      →   "Model: GPT-4. Accuracy: 85%."
        |-------|----------|
        | GPT-4 | 85%      |

    Each data row becomes one prose sentence.
    Headers become the keys.
    The separator row is discarded.

    If parsing fails, emit SEG_MALFORMED_TABLE and return empty prose.
    """
    warnings = []
    lines = list(event.lines)

    content_lines = [line for line in lines if not TABLE_SEPARATOR_PATTERN.match(line)]

    if not content_lines:
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        return NormalizedBlock(
            prose="",
            block_type=event.block_type,
            char_start=event.char_start,
            char_end=event.char_end,
            warnings=tuple(warnings),
            skip=True,
        )

    def parse_row(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    try:
        header_row = parse_row(content_lines[0])
        data_rows = content_lines[1:]

        if not header_row:
            raise ValueError("Empty header row")

        prose_sentences = []
        for data_line in data_rows:
            cells = parse_row(data_line)
            pairs = []
            for idx, header in enumerate(header_row):
                value = cells[idx] if idx < len(cells) else ""
                if header and value:
                    pairs.append(TABLE_KV_TEMPLATE.format(key=header, value=value))

            if pairs:
                prose_sentences.append(" ".join(pairs))

        combined_prose = " ".join(prose_sentences)

    except Exception as e:
        logger.warning("table normalisation failed", error=str(e))
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        combined_prose = ""

    return NormalizedBlock(
        prose=combined_prose,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=tuple(warnings),
        skip=not combined_prose,
    )


def _normalize_code_block(event: ScannerEvent) -> NormalizedBlock:
    """Code blocks are skipped in V1."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,),
        skip=True,
    )


def _normalize_skip(event: ScannerEvent) -> NormalizedBlock:
    """Blocks that produce nothing (horizontal rules, front matter, etc.)."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,
    )


def _normalize_unknown(event: ScannerEvent) -> NormalizedBlock:
    """Unrecognised structure — emit warning and skip."""
    logger.warning("unknown block type encountered", block_type=event.block_type)
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_UNKNOWN_STRUCTURE,),
        skip=True,
    )


# Strategy dispatch table — extend here for new formats
_NORMALIZERS = {
    BlockType.PARAGRAPH: _normalize_paragraph,
    BlockType.HEADING: _normalize_heading,
    BlockType.BULLET_ITEM: _normalize_bullet_item,
    BlockType.ORDERED_ITEM: _normalize_ordered_item,
    BlockType.BLOCK_QUOTE: _normalize_block_quote,
    BlockType.TABLE: _normalize_table,
    BlockType.CODE_BLOCK: _normalize_code_block,
    BlockType.FRONT_MATTER: _normalize_skip,
    BlockType.HORIZONTAL_RULE: _normalize_skip,
    BlockType.BLANK: _normalize_skip,
}
