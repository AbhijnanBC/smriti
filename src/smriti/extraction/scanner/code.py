"""
scanner/code.py — Code block detection and accumulation.
"""

from typing import Optional, Tuple
from smriti.extraction.rules import (
    FENCED_CODE_START,
    FENCED_CODE_END_TRIPLE,
    FENCED_CODE_END_TILDE,
    INDENTED_CODE_PATTERN,
)


def detect_fenced_code_start(line: str) -> Optional[str]:
    """Return fence char ('`' or '~') if line starts a fenced code block."""
    match = FENCED_CODE_START.match(line)
    if match:
        return match.group(1)[0]   # first char of the fence
    return None


def is_fenced_code_end(line: str, fence_char: str) -> bool:
    if fence_char == "`":
        return bool(FENCED_CODE_END_TRIPLE.match(line))
    else:
        return bool(FENCED_CODE_END_TILDE.match(line))


def is_indented_code_line(line: str) -> bool:
    return bool(INDENTED_CODE_PATTERN.match(line))