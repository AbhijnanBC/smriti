"""
segmenter.py — Rule-based sentence segmenter for Phase 3.

Responsibility:
    Split normalised prose into sentence candidates using deterministic rules.

    CRITICAL DESIGN CONSTRAINT:
        No statistical models.
        No spaCy sentence boundaries.
        No ML of any kind.
        Must be 100% reproducible across all runs.

Philosophy:
    Prefer false MERGE over false SPLIT.
    "Dr. Smith visited" → one sentence (NOT "Dr." + "Smith visited")
    This is safer for downstream claim extraction.

Algorithm:
    1. Split on terminal punctuation (. ? !) followed by space + uppercase
    2. Guard against abbreviations using the abbreviation dictionary
    3. Guard against decimal numbers (3.14 should not split)
    4. Guard against ellipsis (... should not split)

Input:  NormalizedBlock.prose (str)
Output: List[SentenceCandidate]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, FrozenSet
import structlog

from smriti.core.config import get_config
from smriti.extraction.rules import (
    DEFAULT_ABBREVIATIONS,
    SENTENCE_ENDING_CHARS,
    MIN_SENTENCE_CHARS_DEFAULT,
    MAX_SENTENCE_CHARS_DEFAULT,
)
from smriti.core.models import SegmentationWarning

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class SentenceCandidate:
    """
    A candidate sentence extracted from a NormalizedBlock.

    Fields:
        text:       The sentence text (stripped)
        char_start: Approximate character start within the NormalizedBlock's prose
        char_end:   Approximate character end
        warnings:   Any per-candidate warnings
    """
    text: str
    char_start: int
    char_end: int
    warnings: tuple = ()


class SentenceSegmenter:
    """
    Rule-based sentence segmenter.

    Instantiate once, call segment() per NormalizedBlock.
    Configuration is loaded once from config/default.yaml.
    """

    def __init__(self) -> None:
        cfg = get_config()
        extraction_cfg = cfg.get("extraction", {})
        segmentation_cfg = cfg.get("segmentation", {})

        custom_abbrevs = frozenset(
            a.lower() for a in extraction_cfg.get("abbreviations", [])
        )
        self._abbreviations: FrozenSet[str] = DEFAULT_ABBREVIATIONS | custom_abbrevs

        self._min_chars: int = segmentation_cfg.get(
            "min_sentence_chars", MIN_SENTENCE_CHARS_DEFAULT
        )
        self._max_chars: int = segmentation_cfg.get(
            "max_sentence_chars", MAX_SENTENCE_CHARS_DEFAULT
        )

    def segment(self, prose: str, block_char_start: int = 0) -> List[SentenceCandidate]:
        """
        Split prose into sentence candidates.

        Args:
            prose:             The normalised prose from NormalizedBlock.
            block_char_start:  Character offset of this prose in the full document.

        Returns:
            List[SentenceCandidate], may be empty if prose is empty or all candidates
            are too short.
        """
        if not prose.strip():
            return []

        raw_candidates = self._split_into_candidates(prose)
        result: List[SentenceCandidate] = []
        running_offset = block_char_start

        for raw_text in raw_candidates:
            text = raw_text.strip()
            if not text:
                running_offset += len(raw_text)
                continue

            warnings = []

            if len(text) < self._min_chars:
                logger.debug(
                    "sentence discarded (too short)",
                    length=len(text),
                    text=text[:30],
                )
                running_offset += len(raw_text)
                continue

            if len(text) > self._max_chars:
                warnings.append(SegmentationWarning.SEG_VERY_LONG_SENTENCE)
                logger.debug("very long sentence", length=len(text))

            char_start = running_offset + (len(raw_text) - len(raw_text.lstrip()))
            char_end = char_start + len(text)

            result.append(SentenceCandidate(
                text=text,
                char_start=char_start,
                char_end=char_end,
                warnings=tuple(warnings),
            ))
            running_offset += len(raw_text)

        return result

    def _split_into_candidates(self, prose: str) -> List[str]:
        """
        Split prose string into sentence candidate strings.

        Algorithm:
          - Scan character by character
          - When we hit . ? ! followed by whitespace + uppercase (or end of string),
            check if it's actually an abbreviation or decimal
          - If not, split here
        """
        candidates: List[str] = []
        current_start = 0
        i = 0
        length = len(prose)

        while i < length:
            char = prose[i]

            if char in SENTENCE_ENDING_CHARS:
                # Ellipsis (...) — never a sentence boundary
                if char == "." and i + 1 < length and prose[i + 1] == ".":
                    i += 1
                    continue

                # Decimal numbers: "3.14" — no split
                if char == "." and i > 0 and prose[i - 1].isdigit():
                    if i + 1 < length and prose[i + 1].isdigit():
                        i += 1
                        continue

                # Check if this is an abbreviation: "Dr.", "e.g.", etc.
                if char == "." and self._is_abbreviation(prose, i):
                    i += 1
                    continue

                # Check: followed by whitespace then uppercase (or end of string)
                j = i + 1
                while j < length and prose[j] in '"\')\]':
                    j += 1

                if j >= length:
                    i += 1
                    continue

                if prose[j] == " ":
                    k = j + 1
                    while k < length and prose[k] == " ":
                        k += 1
                    if k < length and (prose[k].isupper() or prose[k].isdigit()):
                        candidates.append(prose[current_start : i + 1])
                        current_start = k
                        i = k
                        continue

            i += 1

        remaining = prose[current_start:].strip()
        if remaining:
            candidates.append(remaining)

        return candidates

    def _is_abbreviation(self, text: str, dot_pos: int) -> bool:
        """
        Check if the period at dot_pos is part of a known abbreviation.

        Looks backwards from the period to find the preceding word.
        """
        if dot_pos == 0:
            return False

        word_end = dot_pos
        word_start = dot_pos - 1
        while word_start > 0 and text[word_start - 1].isalpha():
            word_start -= 1

        preceding_word = text[word_start:word_end].lower()
        return preceding_word in self._abbreviations