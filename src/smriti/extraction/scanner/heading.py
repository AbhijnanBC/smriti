"""
scanner/heading.py — Heading detection logic.
"""

from typing import Optional
from smriti.extraction.rules import HEADING_PATTERN, SETEXT_H1_PATTERN, SETEXT_H2_PATTERN


def detect_heading(line: str, next_line: Optional[str] = None):
    """
    Detect ATX or setext heading.

    Returns:
        (level, title, consumed_lines) or (None, None, 0) if not a heading.
    """
    # ATX
    match = HEADING_PATTERN.match(line)
    if match:
        level = len(match.group(1))
        title = match.group(2).strip()
        return level, title, 1

    # Setext H1 (line followed by ===)
    if next_line and SETEXT_H1_PATTERN.match(next_line):
        return 1, line.strip(), 2

    # Setext H2 (line followed by ---)
    if next_line and SETEXT_H2_PATTERN.match(next_line):
        return 2, line.strip(), 2

    return None, None, 0