"""Test data models."""

import pytest
from datetime import datetime
from pathlib import Path

from smriti.core.models import (
    Claim, Contradiction, ContradictionType,
    Document, FileFormat, Sentence, Embedding,
    Topic, ManifestEntry,
)


def test_claim_creation():
    claim = Claim(
        text="Python is great",
        document_path=Path("note.md"),
        sentence_position=0,
        extracted_at=datetime.now(),
    )
    assert claim.text == "Python is great"
    assert claim.unique_id() == "note:0"


def test_claim_unique_id_is_deterministic():
    path = Path("my_note.md")
    c1 = Claim("text", path, 3, datetime.now())
    c2 = Claim("other text", path, 3, datetime.now())
    assert c1.unique_id() == c2.unique_id()  # same doc + position = same id


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
    doc = Document(
        path=Path("note.md"),
        format=FileFormat.MARKDOWN,
        raw_text="Hello world",
        discovered_at=datetime.now(),
    )
    assert doc.size_bytes > 0


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