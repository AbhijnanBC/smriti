"""
scanner/scanner.py — Structural scanner orchestrator.

Responsibility:
    Read a Document's normalized_text line by line and emit ScannerEvents
    describing the structural elements found.

    This file orchestrates the detection logic from submodules.

Input:  str (normalized_text from Document)
Output: List[ScannerEvent]

Complexity: O(n) — one linear pass through the text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
import structlog

from smriti.extraction.rules import (
    YAML_FRONT_MATTER_DELIMITER,
    HORIZONTAL_RULE_PATTERN,
    BLOCK_QUOTE_PATTERN,
    BULLET_PATTERN,
    ORDERED_PATTERN,
)
from smriti.extraction.scanner.heading import detect_heading
from smriti.extraction.scanner.paragraph import accumulate_paragraph
from smriti.extraction.scanner.table import is_table_row, is_table_separator, accumulate_table
from smriti.extraction.scanner.code import (
    detect_fenced_code_start,
    is_fenced_code_end,
    is_indented_code_line,
)

logger = structlog.get_logger(__name__)


class BlockType(str, Enum):
    """The structural type of a scanner event."""
    HEADING          = "heading"
    PARAGRAPH        = "paragraph"
    BULLET_ITEM      = "bullet_item"
    ORDERED_ITEM     = "ordered_item"
    BLOCK_QUOTE      = "block_quote"
    TABLE            = "table"
    CODE_BLOCK       = "code_block"       # Ignored in V1
    FRONT_MATTER     = "front_matter"     # Ignored
    HORIZONTAL_RULE  = "horizontal_rule"  # Ignored
    BLANK            = "blank"            # Ignored


@dataclass(frozen=True)
class ScannerEvent:
    """
    An immutable structural event emitted by the scanner.

    Fields:
        block_type:    What kind of structural element this is
        text:          The meaningful text content (stripped of markers)
        heading_level: 1–6 for headings, None for everything else
        char_start:    Character offset of the FIRST character of this block
        char_end:      Character offset just after the LAST character of this block
        lines:         All lines that make up this block (for multi‑line blocks)
    """
    block_type: BlockType
    text: str
    heading_level: Optional[int]
    char_start: int
    char_end: int
    lines: tuple = field(default_factory=tuple)


def scan_document(normalized_text: str) -> List[ScannerEvent]:
    """
    Perform one linear pass through normalized_text and emit structural events.

    Args:
        normalized_text: The fully normalized text from Phase 2 (Document.normalized_text).

    Returns:
        List of ScannerEvent in document order. Never empty for non‑empty text.

    Complexity: O(n) — single pass, no recursion.
    """
    if not normalized_text.strip():
        return []

    events: List[ScannerEvent] = []
    lines = normalized_text.split("\n")
    num_lines = len(lines)

    # State flags for multi‑line blocks
    in_fenced_code = False
    fenced_code_char = ""      # ` or ~
    in_front_matter = False
    front_matter_seen = False
    in_table = False

    # Accumulation buffers
    paragraph_lines: List[str] = []
    paragraph_start: int = 0
    table_lines: List[str] = []
    table_start: int = 0
    code_lines: List[str] = []
    code_start: int = 0

    char_pos = 0  # Running character position in the full string

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, paragraph_start
        if paragraph_lines:
            para_text, p_start, p_end = accumulate_paragraph(
                paragraph_lines, paragraph_start, char_pos
            )
            if para_text:
                events.append(ScannerEvent(
                    block_type=BlockType.PARAGRAPH,
                    text=para_text,
                    heading_level=None,
                    char_start=p_start,
                    char_end=p_end,
                    lines=tuple(paragraph_lines),
                ))
            paragraph_lines = []

    def flush_table() -> None:
        nonlocal table_lines, table_start, in_table
        if table_lines:
            table_text, t_start, t_end = accumulate_table(
                table_lines, table_start, char_pos
            )
            events.append(ScannerEvent(
                block_type=BlockType.TABLE,
                text=table_text,
                heading_level=None,
                char_start=t_start,
                char_end=t_end,
                lines=tuple(table_lines),
            ))
            table_lines = []
            in_table = False

    def flush_code_block() -> None:
        nonlocal code_lines, code_start, in_fenced_code
        if code_lines:
            code_text = "\n".join(code_lines)
            events.append(ScannerEvent(
                block_type=BlockType.CODE_BLOCK,
                text=code_text,
                heading_level=None,
                char_start=code_start,
                char_end=char_pos,
                lines=tuple(code_lines),
            ))
            code_lines = []
            in_fenced_code = False

    i = 0
    while i < num_lines:
        line = lines[i]
        line_end = char_pos + len(line)

        # ── Front matter handling ─────────────────────────────────────────────
        if i == 0 and YAML_FRONT_MATTER_DELIMITER.match(line):
            in_front_matter = True
            char_pos = line_end + 1
            i += 1
            continue

        if in_front_matter:
            if YAML_FRONT_MATTER_DELIMITER.match(line) and i > 0:
                in_front_matter = False
                front_matter_seen = True
            char_pos = line_end + 1
            i += 1
            continue

        # ── Fenced code block handling ────────────────────────────────────────
        if not in_fenced_code:
            fence_char = detect_fenced_code_start(line)
            if fence_char:
                flush_paragraph()
                flush_table()
                in_fenced_code = True
                fenced_code_char = fence_char
                code_start = char_pos
                char_pos = line_end + 1
                i += 1
                continue
        else:
            if is_fenced_code_end(line, fenced_code_char):
                flush_code_block()
            else:
                code_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if not line.strip():
            flush_paragraph()
            flush_table()
            # Record blank line for statistics (we'll count later)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────────
        if HORIZONTAL_RULE_PATTERN.match(line):
            flush_paragraph()
            flush_table()
            events.append(ScannerEvent(
                block_type=BlockType.HORIZONTAL_RULE,
                text="",
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── ATX Heading (# Title) ─────────────────────────────────────────────
        heading_level, heading_title, consumed = detect_heading(line, lines[i+1] if i+1 < num_lines else None)
        if heading_level is not None:
            flush_paragraph()
            flush_table()
            # For setext, we need to skip the underline line
            end_pos = line_end
            if consumed == 2:
                # Skip the underline line as well
                # We already used next line; we'll advance i by 2
                # But we need to compute end position including the underline
                underline_line = lines[i+1]
                end_pos = line_end + 1 + len(underline_line) + 1  # include newline
                # We'll handle the skip after appending event
            events.append(ScannerEvent(
                block_type=BlockType.HEADING,
                text=heading_title,
                heading_level=heading_level,
                char_start=char_pos,
                char_end=end_pos,
                lines=(line, lines[i+1] if consumed == 2 else line),
            ))
            # Move char_pos and i
            char_pos = end_pos
            i += consumed
            continue

        # ── Block quote ───────────────────────────────────────────────────────
        quote_match = BLOCK_QUOTE_PATTERN.match(line)
        if quote_match:
            flush_paragraph()
            flush_table()
            quote_text = quote_match.group(1).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BLOCK_QUOTE,
                text=quote_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Table row ─────────────────────────────────────────────────────────
        if is_table_row(line):
            flush_paragraph()
            if not in_table:
                in_table = True
                table_start = char_pos
            table_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # ── Bullet list item ──────────────────────────────────────────────────
        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            flush_paragraph()
            flush_table()
            item_text = bullet_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BULLET_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Ordered list item ─────────────────────────────────────────────────
        ordered_match = ORDERED_PATTERN.match(line)
        if ordered_match:
            flush_paragraph()
            flush_table()
            item_text = ordered_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.ORDERED_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Paragraph accumulation ────────────────────────────────────────────
        if not paragraph_lines:
            paragraph_start = char_pos
        paragraph_lines.append(line)
        char_pos = line_end + 1
        i += 1

    # Flush any remaining state
    flush_paragraph()
    flush_table()
    flush_code_block()

    logger.debug(
        "scan complete",
        events=len(events),
        lines=len(lines),
    )

    return events