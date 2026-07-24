"""
context.py — Hierarchical context stack for Phase 3.

Responsibility:
    Maintain a lightweight push/pop stack representing the current heading
    hierarchy as Phase 3 processes structural events.

    This module has FOUR operations: push, pop, peek, current_context.
    Nothing else. It is deliberately minimal.

    Memory: O(depth) — proportional to heading nesting depth, not document length.

Input:  Heading events from scanner.py
Output: Context strings like "Python > Generators > Yield"

Example:
    # Python          →  push("Python", level=1)   → stack: ["Python"]
    ## Generators     →  push("Generators", level=2) → stack: ["Python", "Generators"]
    Sentence A        →  current_context() → "Python > Generators"
    ## Decorators     →  pop to level 1, push("Decorators") → stack: ["Python", "Decorators"]
    Sentence B        →  current_context() → "Python > Decorators"

RECTIFIED (Issue 4): Added heading title validation to reject malformed contexts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import structlog

from smriti.extraction.rules import CONTEXT_SEPARATOR

logger = structlog.get_logger(__name__)


def _is_valid_heading_title(title: str) -> bool:
    """
    Return True if the title contains at least one alphanumeric character.
    Rejects titles like '#', '---', '***', '===', etc.
    Used by both scanner and context stack for consistency.
    """
    return any(c.isalnum() for c in title)


@dataclass
class _ContextFrame:
    """One entry in the context stack."""
    heading: str      # Cleaned heading text
    level: int        # 1–6


class ContextStack:
    """
    Lightweight heading context stack.

    The context stack represents the path from the document root
    to the current heading, like a breadcrumb trail.

    Invariant: stack[i].level < stack[i+1].level always.
    """

    def __init__(self) -> None:
        self._stack: List[_ContextFrame] = []

    def push(self, heading: str, level: int) -> None:
        """
        Push a new heading onto the stack.

        Before pushing, all frames at level >= this heading's level are popped.
        This handles the transition from deep to shallow headings:
            ## A        stack: [H2:A]
            ### B       stack: [H2:A, H3:B]
            ## C        stack: [H2:C]   ← B and A are both popped

        Args:
            heading: The heading text (without # markers).
            level:   Heading level (1=H1, 2=H2, ... 6=H6).

        RECTIFIED (Issue 4): Skips headings with invalid titles (no alnum).
        """
        # ── RECTIFIED: Validate heading title ──────────────────────────────────
        clean_heading = heading.strip()
        if not _is_valid_heading_title(clean_heading):
            logger.debug(
                "heading skipped (invalid title)",
                heading=clean_heading[:20],
            )
            return

        # Pop all frames at the same or deeper level
        while self._stack and self._stack[-1].level >= level:
            popped = self._stack.pop()
            logger.debug("context popped", heading=popped.heading, level=popped.level)

        self._stack.append(_ContextFrame(heading=clean_heading, level=level))
        logger.debug("context pushed", heading=clean_heading, level=level, depth=len(self._stack))

    def peek(self) -> Optional[str]:
        """Return the topmost heading text, or None if stack is empty."""
        return self._stack[-1].heading if self._stack else None

    def current_context(self) -> str:
        """
        Return the full context path as a string.

        Example: "Python > Generators > Yield"
        Returns "" if no heading has been encountered yet.
        """
        if not self._stack:
            return ""
        return CONTEXT_SEPARATOR.join(frame.heading for frame in self._stack)

    def depth(self) -> int:
        """Current stack depth (number of active headings)."""
        return len(self._stack)

    def clear(self) -> None:
        """Reset stack to empty state (use at document boundaries)."""
        self._stack.clear()

    def __repr__(self) -> str:
        return f"ContextStack({self.current_context()!r})"