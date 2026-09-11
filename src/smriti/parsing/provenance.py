"""
provenance.py — Extract disclosed source identity from raw document text.

RECTIFIED (external review, P1-1 "provenance/source lineage"): no phase
of this pipeline previously extracted WHO wrote or published a document,
or WHEN, even when the document itself discloses it. This module reads
two concrete patterns already present in this project's own corpora:

  1. YAML frontmatter (```---\\nkey: value\\n---``` at the top of the
     file), e.g. data/raw/stress_vault/*.md's `date: 2024-07-01`.
  2. An inline ``**Source:** X`` attribution line immediately after the
     document's first heading, e.g. data/raw/reference_vault/*.md's
     ``**Source:** Apache Hadoop Documentation`` -- present in 53 real
     documents, previously extracted only as claim noise (correctly
     discarded by the assertion classifier as METADATA) with the
     attribution itself never captured anywhere.

Nothing here is inferred: a document with neither pattern gets a
DocumentProvenance with every field None (extraction_method="none"),
which is the honest, common case for most notes.

Rules:
    ✅ Every returned field is either a literal value the document itself
       states, or None.
    ✅ Never fabricate or guess author/publisher/date from filename,
       content, or filesystem metadata (that is exactly what P1-3 forbids
       for temporal metadata, and the same principle applies here).
    ❌ Never modify or strip the source text (that remains the raw_text
       Phase 2 preserves) -- this module only reads it.
"""

from __future__ import annotations

import re
from datetime import datetime

import yaml

from smriti.core.models import DocumentProvenance

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_INLINE_SOURCE_RE = re.compile(r"^\*\*Source:\*\*\s*(.+?)\s*$", re.MULTILINE)

# Frontmatter keys accepted for each provenance field. A document may use
# any one of a small set of common aliases; the first one present wins.
_FRONTMATTER_KEY_ALIASES = {
    "source_id": ["source_id", "id"],
    "author": ["author", "authors"],
    "publisher": ["publisher", "publication", "source", "outlet"],
    "domain": ["domain"],
    "url": ["url", "link"],
    "publication_date": ["date", "published", "publication_date"],
    "parent_source_id": ["parent_source_id", "derived_from", "quotes"],
}


def _parse_date(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    # yaml.safe_load already parses unquoted ISO dates (YYYY-MM-DD) into
    # datetime.date, not datetime.datetime -- normalize both.
    import datetime as _dt

    if isinstance(value, _dt.date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
    return None


def _extract_frontmatter(raw_text: str) -> dict | None:
    match = _FRONTMATTER_RE.match(raw_text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _extract_inline_source_line(raw_text: str) -> str | None:
    match = _INLINE_SOURCE_RE.search(raw_text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def extract_document_provenance(raw_text: str) -> DocumentProvenance:
    """
    Extract whatever source-identity information a document discloses
    about itself. Returns an all-None DocumentProvenance (is_available =
    False) when neither pattern is present -- the common case.
    """
    frontmatter = _extract_frontmatter(raw_text)
    if frontmatter:
        fields = {}
        for field_name, keys in _FRONTMATTER_KEY_ALIASES.items():
            for k in keys:
                if k in frontmatter and frontmatter[k] is not None:
                    fields[field_name] = frontmatter[k]
                    break
        if "publication_date" in fields:
            fields["publication_date"] = _parse_date(fields["publication_date"])
        # Coerce any non-string scalar (e.g. a YAML int/bool) to str for
        # the string-typed fields, defensively -- frontmatter is
        # user-authored free text, not a validated schema.
        for field_name in ("source_id", "author", "publisher", "domain", "url", "parent_source_id"):
            if field_name in fields and fields[field_name] is not None:
                fields[field_name] = str(fields[field_name])
        if fields:
            return DocumentProvenance(extraction_method="yaml_frontmatter", **fields)

    inline_source = _extract_inline_source_line(raw_text)
    if inline_source:
        return DocumentProvenance(publisher=inline_source, extraction_method="inline_source_line")

    return DocumentProvenance()
