"""
scanner/table.py — Table detection and accumulation.
"""

from smriti.extraction.rules import TABLE_ROW_PATTERN, TABLE_SEPARATOR_PATTERN


def is_table_row(line: str) -> bool:
    return bool(TABLE_ROW_PATTERN.match(line))


def is_table_separator(line: str) -> bool:
    return bool(TABLE_SEPARATOR_PATTERN.match(line))


def accumulate_table(
    lines: list[str], start_char: int, current_char_pos: int
) -> tuple[str, int, int]:
    """
    Accumulate a table block.

    Returns:
        (table_text, char_start, char_end)
    """
    table_text = "\n".join(lines)
    return table_text, start_char, current_char_pos
