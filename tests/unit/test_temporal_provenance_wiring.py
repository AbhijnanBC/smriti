"""
Unit tests for PipelineRunner._enrich_claims_with_timestamps (external
review, P1-3 "temporal metadata").

RECTIFIED: evolution/temporal.py has read Claim.timestamp (falling back
to NO_TIMESTAMP when absent) since before that field existed on Claim at
all -- every claim in every corpus this project has ever run therefore
got NO_TIMESTAMP, never genuine EVOLUTION_CHAIN reasoning. This test
proves the enrichment step that finally populates it from disclosed
document provenance (never filesystem mtime).
"""

from datetime import datetime
from pathlib import Path

from smriti.core.models import (
    AssertionMetadata,
    Claim,
    ClaimProvenance,
    DocumentProvenance,
    ExtractionMode,
)
from smriti.pipeline.runner import PipelineRunner


def make_claim(claim_id: str, document_id: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id=f"s_{claim_id}",
        document_id=document_id,
        text="Some claim text.",
        content_hash="hash",
        context="",
        source_path=Path(f"{document_id}.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id=f"s_{claim_id}",
            document_id=document_id,
            source_path=Path(f"{document_id}.md"),
            sentence_context="",
            sentence_position=0,
        ),
    )


def make_runner() -> PipelineRunner:
    return PipelineRunner(input_dirs=[Path(".")])


def test_claim_timestamp_populated_from_document_provenance():
    claim = make_claim("c1", "doc1")
    provenance = {
        "doc1": DocumentProvenance(
            publication_date=datetime(2024, 7, 1), extraction_method="yaml_frontmatter"
        ),
    }
    enriched = make_runner()._enrich_claims_with_timestamps({"c1": claim}, provenance)
    assert enriched["c1"].timestamp == datetime(2024, 7, 1)


def test_claim_validity_interval_fields_default_to_none():
    """
    RECTIFIED (P1-11, "PLEASE FIX AND SAVE ME" review round): schema-level
    extension distinct from timestamp/claim_assertion_time -- no
    extractor populates these yet, so every claim must default to None
    on all four, never inferred from timestamp or any other field.
    """
    claim = make_claim("c1", "doc1")
    assert claim.claim_valid_from is None
    assert claim.claim_valid_to is None
    assert claim.temporal_expression is None
    assert claim.temporal_confidence is None


def test_claim_validity_interval_fields_are_settable_independent_of_timestamp():
    """The four new fields are genuinely independent dataclass fields, not
    derived from timestamp -- setting timestamp must never implicitly
    populate them, and setting them must never require timestamp."""
    claim = make_claim("c1", "doc1")
    enriched_timestamp_only = make_runner()._enrich_claims_with_timestamps(
        {"c1": claim},
        {
            "doc1": DocumentProvenance(
                publication_date=datetime(2024, 7, 1), extraction_method="yaml_frontmatter"
            )
        },
    )["c1"]
    assert enriched_timestamp_only.timestamp == datetime(2024, 7, 1)
    assert enriched_timestamp_only.claim_valid_from is None

    from dataclasses import replace

    claim_with_validity = replace(
        claim,
        claim_valid_from=datetime(2023, 1, 1),
        claim_valid_to=datetime(2023, 12, 31),
        temporal_expression="in 2023",
        temporal_confidence=0.8,
    )
    assert claim_with_validity.timestamp is None
    assert claim_with_validity.claim_valid_from == datetime(2023, 1, 1)
    assert claim_with_validity.temporal_confidence == 0.8


def test_claim_timestamp_stays_none_when_document_discloses_no_date():
    claim = make_claim("c1", "doc1")
    enriched = make_runner()._enrich_claims_with_timestamps({"c1": claim}, {})
    assert enriched["c1"].timestamp is None


def test_claim_timestamp_stays_none_when_provenance_present_but_no_date():
    claim = make_claim("c1", "doc1")
    provenance = {
        "doc1": DocumentProvenance(publisher="Reuters", extraction_method="inline_source_line")
    }
    enriched = make_runner()._enrich_claims_with_timestamps({"c1": claim}, provenance)
    assert enriched["c1"].timestamp is None


def test_enrichment_never_touches_filesystem_mtime():
    """The whole point of this rectification: timestamp must come ONLY
    from disclosed provenance, never from any filesystem attribute of
    the claim/document (source_path has no mtime info attached at all
    at this layer, which is itself the guarantee -- there is nothing
    here to fall back to)."""
    claim = make_claim("c1", "doc1")
    enriched = make_runner()._enrich_claims_with_timestamps({"c1": claim}, {})
    assert enriched["c1"].timestamp is None
    assert not hasattr(claim, "modified_at")


def test_temporal_resolver_reads_the_enriched_timestamp():
    """End-to-end check one layer up: evolution/temporal.py's own
    _get_semantic_timestamp must return the enriched value, proving the
    two modules are actually wired together, not just independently
    correct in isolation."""
    from smriti.evolution.temporal import _get_semantic_timestamp

    claim = make_claim("c1", "doc1")
    provenance = {
        "doc1": DocumentProvenance(
            publication_date=datetime(2024, 7, 1), extraction_method="yaml_frontmatter"
        )
    }
    enriched = make_runner()._enrich_claims_with_timestamps({"c1": claim}, provenance)
    assert _get_semantic_timestamp(enriched["c1"]) == datetime(2024, 7, 1)
    # Un-enriched claim (no provenance) must resolve to None -> NO_TIMESTAMP.
    assert _get_semantic_timestamp(claim) is None
