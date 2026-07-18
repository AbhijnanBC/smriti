"""
rules.py — Deterministic rules and patterns for Phase 3.

This file contains ONLY data: patterns, dictionaries, and strategy names.
Zero execution logic lives here.

Every constant here is configurable via config/default.yaml.
This file provides the hard-coded defaults for those config values.
"""

import re

# ── Heading detection ─────────────────────────────────────────────────────────

# Matches ATX-style headings: # H1, ## H2, ..., ###### H6
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# Matches setext-style headings:
#   Title       (underlined by === for H1)
#   =========
SETEXT_H1_PATTERN = re.compile(r"^={3,}\s*$")
SETEXT_H2_PATTERN = re.compile(r"^-{3,}\s*$")

# ── List detection ────────────────────────────────────────────────────────────

# Matches bullet list items: "- item", "* item", "+ item"
BULLET_PATTERN = re.compile(r"^(\s*)[*+\-]\s+(.+)$")

# Matches ordered list items: "1. item", "2) item"
ORDERED_PATTERN = re.compile(r"^(\s*)\d+[.)]\s+(.+)$")

# ── Block quote detection ─────────────────────────────────────────────────────

BLOCK_QUOTE_PATTERN = re.compile(r"^>\s*(.*)")

# ── Code block detection ──────────────────────────────────────────────────────

FENCED_CODE_START = re.compile(r"^(`{3,}|~{3,})(.*)")
FENCED_CODE_END_TRIPLE = re.compile(r"^`{3,}\s*$")
FENCED_CODE_END_TILDE = re.compile(r"^~{3,}\s*$")

# Indented code block: 4 spaces or 1 tab at start
INDENTED_CODE_PATTERN = re.compile(r"^( {4}|\t)(.+)")

# ── Table detection ───────────────────────────────────────────────────────────

TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\|[\s\-:|]+\|")

# ── Front matter ──────────────────────────────────────────────────────────────

YAML_FRONT_MATTER_DELIMITER = re.compile(r"^---\s*$")

# ── Horizontal rule ───────────────────────────────────────────────────────────

HORIZONTAL_RULE_PATTERN = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$")

# ── HTML comment ──────────────────────────────────────────────────────────────

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)

# ── Sentence boundary ─────────────────────────────────────────────────────────

# These abbreviations should NEVER trigger a sentence boundary.
# Fully configurable via config extraction.abbreviations in default.yaml.
DEFAULT_ABBREVIATIONS = frozenset([
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "rev", "gen",
    "e.g", "i.e", "vs", "etc", "fig", "no", "vol", "pt", "pp",
    "u.s", "u.k", "a.m", "p.m", "ph.d", "m.d", "b.c", "a.d",
])

# Characters that may end a sentence when followed by space + capital letter
SENTENCE_ENDING_CHARS = frozenset([".", "?", "!"])

# Minimum characters for a sentence to be kept (shorter are discarded with SEG001)
MIN_SENTENCE_CHARS_DEFAULT = 3

# Maximum sentence length before SEG002 warning is emitted
MAX_SENTENCE_CHARS_DEFAULT = 2000

# Context separator string
CONTEXT_SEPARATOR = " > "

# Table cell serialisation template: "Key: Value."
TABLE_KV_TEMPLATE = "{key}: {value}."

# Context validation: allow letters, digits, spaces, and the separator
CONTEXT_VALID_PATTERN = re.compile(r"^[a-zA-Z0-9\s" + re.escape(CONTEXT_SEPARATOR) + "]*$")