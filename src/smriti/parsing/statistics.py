"""
statistics.py — Structural text statistics.

Responsibility:
    Compute lightweight structural statistics from normalized text.
    All statistics are derived purely from text structure.
    No NLP. No linguistic analysis.

Statistics computed:
    character_count   — total characters in normalized text
    word_count        — whitespace-separated tokens (rough but deterministic)
    line_count        — total lines (split on LF)
    blank_line_count  — lines that are empty or whitespace-only
    paragraph_count   — blocks of text separated by one or more blank lines

Complexity: O(n) time, O(1) space (processes line by line).

Invariants verified:
    character_count >= 0
    word_count >= 0
    line_count >= blank_line_count
    line_count >= paragraph_count
"""

import structlog

from smriti.core.models import TextStatistics
from smriti.exceptions import StatisticsError

logger = structlog.get_logger(__name__)


def compute_statistics(normalized_text: str) -> TextStatistics:
    """
    Compute structural statistics from normalized text.

    Args:
        normalized_text: Text after full normalization pipeline.
                         Must be a Python str.

    Returns:
        TextStatistics (frozen dataclass) with all counts.

    Raises:
        StatisticsError: If text is not a str or statistics are inconsistent.
    """
    if not isinstance(normalized_text, str):
        raise StatisticsError(f"normalized_text must be str, got {type(normalized_text)}")

    try:
        character_count = len(normalized_text)

        if not normalized_text.strip():
            # Empty or whitespace-only document
            return TextStatistics(
                character_count=character_count,
                word_count=0,
                line_count=0,
                blank_line_count=0,
                paragraph_count=0,
            )

        lines = normalized_text.split("\n")
        line_count = len(lines)

        blank_line_count = sum(1 for line in lines if not line.strip())

        word_count = len(normalized_text.split())

        # Paragraph = one or more non-blank lines separated by blank lines
        # Iterate through lines, counting transitions from blank→non-blank
        paragraph_count = 0
        in_paragraph = False
        for line in lines:
            if line.strip():
                if not in_paragraph:
                    paragraph_count += 1
                    in_paragraph = True
            else:
                in_paragraph = False

    except StatisticsError:
        raise
    except Exception as e:
        raise StatisticsError(f"Statistics computation failed: {e}") from e

    stats = TextStatistics(
        character_count=character_count,
        word_count=word_count,
        line_count=line_count,
        blank_line_count=blank_line_count,
        paragraph_count=paragraph_count,
    )

    logger.debug(
        "statistics computed",
        chars=character_count,
        words=word_count,
        lines=line_count,
        blank_lines=blank_line_count,
        paragraphs=paragraph_count,
    )

    return stats