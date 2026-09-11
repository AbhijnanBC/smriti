"""Test data models."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from smriti.core.models import (
    AssertionMetadata,
    Claim,
    ClaimProvenance,
    Contradiction,
    ContradictionType,
    ExtractionMethod,
    ExtractionMode,
    FileFormat,
    ManifestEntry,
    RawExtractionResult,
    SourceDocument,
    Topic,
)
from smriti.parsing.builder import build_document
from smriti.parsing.statistics import compute_statistics


def _make_claim(
    claim_id: str, text: str, document_id: str = "note", sentence_position: int = 0
) -> Claim:
    """
    Build a Claim using the current (Phase 4) schema.

    Claim no longer computes its own id/hash — that is builder.py's job
    (see claims/builder.py::_compute_claim_id / _compute_content_hash) — so
    here we compute content_hash the same way production does: SHA256 of the
    exact text, first 16 hex chars.
    """
    return Claim(
        claim_id=claim_id,
        sentence_id=f"{document_id}:{sentence_position}",
        document_id=document_id,
        text=text,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        context="",
        source_path=Path(f"{document_id}.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id=f"{document_id}:{sentence_position}",
            document_id=document_id,
            source_path=Path(f"{document_id}.md"),
            sentence_context="",
            sentence_position=sentence_position,
        ),
    )


def test_claim_creation():
    claim = _make_claim(
        claim_id="aaa111", text="Python is great", document_id="note", sentence_position=0
    )
    assert claim.text == "Python is great"
    # Identity is now the explicit claim_id (assigned deterministically by
    # claims/builder.py from sentence_id+text+span_start), not a computed
    # unique_id() method on the dataclass itself.
    assert claim.claim_id == "aaa111"
    assert claim.provenance.document_id == "note"
    assert claim.provenance.sentence_position == 0


def test_claim_unique_id_is_deterministic():
    """Two Claims built from identical field values are equal (dataclass value
    equality) — this is the modern analogue of the old 'same doc + position
    => same id' check, since identity now lives on the explicit claim_id
    field rather than being derived inside the dataclass."""
    c1 = _make_claim(claim_id="shared_id", text="text", document_id="my_note", sentence_position=3)
    c2 = _make_claim(claim_id="shared_id", text="text", document_id="my_note", sentence_position=3)
    assert c1 == c2
    assert c1.claim_id == c2.claim_id


def test_contradiction_creation():
    contra = Contradiction(
        claim_a_id="note1:0",
        claim_b_id="note2:0",
        contradiction_type=ContradictionType.STRATEGY_SHIFT,
        nli_confidence=0.85,
        similarity_score=0.78,
        temporal_distance_days=100,
        severity_score=7.5,
    )
    assert contra.severity_score == 7.5
    assert contra.contradiction_type == ContradictionType.STRATEGY_SHIFT


def test_document_size_inferred():
    """
    Document (Phase 2) no longer infers size itself — size_bytes lives on the
    Phase 1 SourceDocument (from the actual file on disk), and the Phase 2
    Document instead carries TextStatistics derived from the real text via
    parsing/statistics.py::compute_statistics. This test exercises that
    real derivation path via build_document, the only place Document is
    constructed in production.
    """
    raw_text = "Hello world"
    source = SourceDocument(
        doc_id="a" * 64,
        path=Path("note.md"),
        relative_path=Path("note.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="a" * 64,
        size_bytes=len(raw_text.encode("utf-8")),
        modified_at=datetime.now(tz=UTC),
    )
    extraction_result = RawExtractionResult(
        raw_text=raw_text,
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
        encoding_used="utf-8",
    )
    stats = compute_statistics(raw_text)

    doc = build_document(source, extraction_result, raw_text, (), stats)

    assert doc.text_statistics.character_count == len(raw_text)
    assert doc.source_document.size_bytes > 0


def test_topic_drift_score():
    topic = Topic(name="python", claim_ids=["a", "b", "c", "d"], contradiction_count=2)
    assert topic.drift_score == pytest.approx(50.0)


def test_topic_drift_score_empty():
    topic = Topic(name="empty")
    assert topic.drift_score == 0.0


def test_manifest_entry_has_run_id():
    entry = ManifestEntry(
        run_id="20240715_143022",
        phase=1,
        timestamp=datetime.now(),
        duration_seconds=1.5,
        inputs={},
        outputs={},
        status="success",
    )
    assert entry.run_id == "20240715_143022"
    assert entry.schema_version == "1.0"
