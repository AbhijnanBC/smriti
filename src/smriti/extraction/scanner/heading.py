"""
scanner/heading.py — Heading detection logic.
"""

from smriti.extraction.rules import HEADING_PATTERN, SETEXT_H1_PATTERN, SETEXT_H2_PATTERN


def _is_valid_heading_title(title: str) -> bool:
    """
    Return True if the title contains at least one alphanumeric character.
    Rejects titles like '#', '---', '***', '===', etc.
    """
    return any(c.isalnum() for c in title)


def detect_heading(line: str, next_line: str | None = None):
    """
    Detect ATX or setext heading.

    Returns:
        (level, title, consumed_lines) or (None, None, 0) if not a heading.
    """
    # ── ATX heading ──────────────────────────────────────────────────────────
    match = HEADING_PATTERN.match(line)
    if match:
        level = len(match.group(1))
        title = match.group(2).strip()
        if not _is_valid_heading_title(title):
            return None, None, 0
        return level, title, 1

    # ── Setext H1 (line followed by ===) ──────────────────────────────────
    if next_line and SETEXT_H1_PATTERN.match(next_line):
        title = line.strip()
        if not _is_valid_heading_title(title):
            return None, None, 0
        return 1, title, 2

    # ── Setext H2 (line followed by ---) ──────────────────────────────────
    if next_line and SETEXT_H2_PATTERN.match(next_line):
        title = line.strip()
        if not _is_valid_heading_title(title):
            return None, None, 0
        return 2, title, 2

    return None, None, 0
