"""Baseline 1: naive keyword-based claim extraction.

This is the simplest possible strawman for claim extraction: no dependency
parsing, no SVO/predicate structure, no modality/negation/attribution
analysis. A sentence "becomes a claim" if it contains at least one
non-stopword content token. Essentially every non-trivial sentence in a
document is emitted as a claim.

It is intentionally independent of SMRITI's Phase 2 (parsing) and Phase 3
(sentence segmentation) machinery -- it reads the raw markdown files itself,
strips a handful of common markdown decorations, and splits into sentences
with plain regexes. That independence is deliberate: it lets us report a
volume comparison (how many "claims" a naive rule finds vs. how many
SMRITI's linguistically-informed pipeline finds) without inheriting any of
SMRITI's own segmentation choices.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from spacy.lang.en.stop_words import STOP_WORDS

# Tokens: simple alphabetic runs (with an optional internal apostrophe, e.g.
# "isn't"). No lemmatization, no POS tagging.
_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

# Split on whitespace that follows a sentence-terminal punctuation mark.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# A handful of common markdown decorations we strip before sentence
# splitting, purely so headers/bullets/links don't get mangled into
# nonsense "sentences". This is text cleanup, not linguistic analysis.
_MD_HEADER_RE = re.compile(r"^#{1,6}\s*")
_MD_LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_MD_EMPHASIS_RE = re.compile(r"[*_`]{1,3}")
_MD_CODE_FENCE_RE = re.compile(r"^```")
_MD_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")


def _strip_markdown_line(line: str) -> str:
    """Strip the most common markdown decorations from a single line."""
    line = _MD_LINK_RE.sub(r"\1", line)
    line = _MD_HEADER_RE.sub("", line)
    line = _MD_LIST_RE.sub("", line)
    line = _MD_EMPHASIS_RE.sub("", line)
    line = line.replace("|", " ")
    return line.strip()


def _split_sentences(text: str) -> list[str]:
    """Very naive sentence splitter: strip markdown noise line-by-line, then
    split each remaining line on terminal punctuation. No abbreviation
    handling, no clause-boundary detection -- deliberately naive.
    """
    sentences: list[str] = []
    in_code_fence = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if _MD_CODE_FENCE_RE.match(stripped):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if not stripped or _MD_TABLE_SEP_RE.match(stripped):
            continue
        line = _strip_markdown_line(raw_line)
        if not line:
            continue
        for chunk in _SENTENCE_SPLIT_RE.split(line):
            chunk = chunk.strip()
            if chunk:
                sentences.append(chunk)
    return sentences


def _has_content_token(sentence: str) -> bool:
    """A sentence qualifies as a naive "claim" if it has at least one token
    that is not a stopword and not a single character.
    """
    for match in _WORD_RE.finditer(sentence):
        token = match.group(0).lower()
        if len(token) > 1 and token not in STOP_WORDS:
            return True
    return False


def _claim_id(source_path: str, sentence_index: int, text: str) -> str:
    """Deterministic id so re-running the baseline is reproducible."""
    digest = hashlib.sha256(f"{source_path}|{sentence_index}|{text}".encode())
    return digest.hexdigest()[:16]


def extract_claims_naive(doc_dir: str | Path) -> list[dict[str, Any]]:
    """Run the naive keyword-extraction baseline over every ``*.md`` file in
    ``doc_dir``.

    Rule: split each document into sentences (regex-based, after stripping
    common markdown decorations), then keep a sentence as a "claim" iff it
    contains at least one non-stopword content token. No structural or
    semantic filtering beyond that.

    Returns a list of plain dicts, one per extracted claim, with keys:
    ``claim_id``, ``text``, ``source_path``, ``document_id``,
    ``sentence_index``, ``method``.
    """
    doc_dir = Path(doc_dir)
    claims: list[dict[str, Any]] = []
    for md_path in sorted(doc_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8", errors="replace")
        sentences = _split_sentences(text)
        for idx, sentence in enumerate(sentences):
            if not _has_content_token(sentence):
                continue
            claims.append(
                {
                    "claim_id": _claim_id(str(md_path), idx, sentence),
                    "text": sentence,
                    "source_path": str(md_path),
                    "document_id": md_path.stem,
                    "sentence_index": idx,
                    "method": "naive_keyword_baseline",
                }
            )
    return claims
