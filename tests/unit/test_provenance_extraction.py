"""
Unit tests for parsing/provenance.py (external review P1-1).

Uses the exact two real patterns found in this project's own corpora:
YAML frontmatter dates (data/raw/stress_vault/*.md) and inline
``**Source:**`` attribution lines (data/raw/reference_vault/*.md).
"""

from datetime import datetime

from smriti.parsing.provenance import extract_document_provenance


def test_no_provenance_signal_returns_all_none():
    text = "# A Note\n\nJust some ordinary text with no metadata at all.\n"
    prov = extract_document_provenance(text)
    assert prov.extraction_method == "none"
    assert not prov.is_available
    assert prov.author is None
    assert prov.publication_date is None


def test_lineage_fields_default_to_none_regardless_of_other_provenance():
    """
    RECTIFIED (P1-6, "PLEASE FIX AND SAVE ME" review round): publisher_id/
    canonical_url/lineage_id/evidence_origin_id are schema-level additions
    with no extraction or normalization logic implemented yet -- they
    must default to None even when OTHER provenance fields (author,
    publication_date, publisher) are successfully extracted, never
    silently derived from those fields.
    """
    text = (
        "---\nauthor: Jane Doe\ndate: 2024-07-01\npublisher: Reuters\n---\n"
        "# An Article\n\nSome disclosed, well-provenanced text.\n"
    )
    prov = extract_document_provenance(text)
    assert prov.is_available
    assert prov.author == "Jane Doe"
    assert prov.publisher_id is None
    assert prov.canonical_url is None
    assert prov.lineage_id is None
    assert prov.evidence_origin_id is None


def test_yaml_frontmatter_date_matching_stress_vault_pattern():
    text = "---\ndate: 2024-07-01\n---\n# HDFS Storage Layer\n\nHDFS divides datasets into 128MB blocks.\n"
    prov = extract_document_provenance(text)
    assert prov.extraction_method == "yaml_frontmatter"
    assert prov.is_available
    assert prov.publication_date == datetime(2024, 7, 1)


def test_yaml_frontmatter_full_fields():
    text = (
        "---\n"
        "source_id: reuters-2024-001\n"
        "author: Jane Doe\n"
        "publisher: Reuters\n"
        "url: https://reuters.example/article\n"
        "date: 2024-03-15\n"
        "derived_from: original-wire-report-42\n"
        "---\n"
        "# Some Article\n\nBody text.\n"
    )
    prov = extract_document_provenance(text)
    assert prov.source_id == "reuters-2024-001"
    assert prov.author == "Jane Doe"
    assert prov.publisher == "Reuters"
    assert prov.url == "https://reuters.example/article"
    assert prov.publication_date == datetime(2024, 3, 15)
    assert prov.parent_source_id == "original-wire-report-42"


def test_inline_source_line_matching_reference_vault_pattern():
    text = (
        "# A4. HDFS Block Storage Architecture\n\n"
        "**Source:** Apache Hadoop Documentation\n\n"
        "The Hadoop Distributed File System (HDFS) is designed to store very large data sets.\n"
    )
    prov = extract_document_provenance(text)
    assert prov.extraction_method == "inline_source_line"
    assert prov.is_available
    assert prov.publisher == "Apache Hadoop Documentation"
    assert prov.publication_date is None


def test_frontmatter_takes_precedence_over_inline_source_line():
    text = (
        "---\n"
        "publisher: Frontmatter Publisher\n"
        "---\n"
        "# Title\n\n"
        "**Source:** Inline Publisher\n\n"
        "Body.\n"
    )
    prov = extract_document_provenance(text)
    assert prov.extraction_method == "yaml_frontmatter"
    assert prov.publisher == "Frontmatter Publisher"


def test_malformed_frontmatter_falls_back_to_no_signal_not_a_crash():
    text = "---\nthis: is: not: valid: yaml: [\n---\n# Title\n\nBody.\n"
    prov = extract_document_provenance(text)
    # Must not raise; either falls back cleanly or extracts nothing useful.
    assert prov is not None


def test_frontmatter_with_no_recognized_keys_is_not_available():
    text = "---\nunrelated_key: some_value\n---\n# Title\n\nBody.\n"
    prov = extract_document_provenance(text)
    assert prov.extraction_method == "none"
    assert not prov.is_available
