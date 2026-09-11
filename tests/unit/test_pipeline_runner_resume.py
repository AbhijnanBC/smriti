"""
Regression test for PipelineRunner._load_phase2_result.

Bug: this method read JSON keys ("source_root", "content_hash",
"size_bytes", "stats", "raw_text") that ExtractionResult.to_dataset_json()
(smriti/parsing/__init__.py) never writes -- it writes "path"/"relative_path"/
"format"/"text_statistics"/"extraction_warnings" and explicitly never writes
raw_text ("too large, not needed by Phase 3"). Resuming a real pipeline run
at Phase 3 from a real phase2/dataset.json artifact raised a KeyError at
runtime. This round-trips a genuine ExtractionResult through
to_dataset_json() and back through the fixed loader.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from smriti.core.manifest import ManifestManager
from smriti.core.models import FileFormat, SourceDocument
from smriti.core.state import StateManager
from smriti.parsing import run_extraction


def make_source(path: Path, fmt: FileFormat) -> SourceDocument:
    content_hash = "a" * 64
    return SourceDocument(
        doc_id=content_hash,
        path=path,
        relative_path=Path(path.name),
        source_root=path.parent,
        format=fmt,
        content_hash=content_hash,
        size_bytes=path.stat().st_size,
        modified_at=datetime.now(tz=UTC),
    )


@pytest.fixture
def real_phase2_artifact(tmp_path, monkeypatch):
    """
    Run real Phase 2 extraction to produce a genuine phase2/dataset.json
    artifact (via the real serializer, not a hand-built stand-in), and
    point PipelineRunner's ARTIFACTS_DIR at the isolated tmp_path so the
    loader under test reads it.
    """
    vault = tmp_path / "vault"
    vault.mkdir()
    doc_path = vault / "note.md"
    doc_path.write_text(
        "# Note\n\nSMRITI resumes from real artifacts, not fixtures.\n"
        "It must not depend on fields the serializer never writes.\n",
        encoding="utf-8",
    )
    source = make_source(doc_path, FileFormat.MARKDOWN)

    run_id = "test_resume_20240101_000000"
    artifacts_dir = tmp_path / "artifacts"
    manifest_mgr = ManifestManager(run_id=run_id, artifacts_dir=artifacts_dir)
    state_mgr = StateManager(state_file=tmp_path / "state.json")

    extraction_result = run_extraction(
        source_documents=[source],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    assert extraction_result.stats.failed == 0

    monkeypatch.setattr("smriti.pipeline.runner.ARTIFACTS_DIR", artifacts_dir)

    return run_id, extraction_result


def test_load_phase2_result_round_trips_real_artifact(real_phase2_artifact):
    """
    _load_phase2_result must reconstruct Document objects from a genuine
    to_dataset_json() artifact without KeyError, preserving every field the
    serializer actually persisted.
    """
    from smriti.pipeline.runner import PipelineRunner

    run_id, extraction_result = real_phase2_artifact
    original = extraction_result.documents[0]

    runner = PipelineRunner.__new__(PipelineRunner)
    runner.run_id = run_id

    loaded = runner._load_phase2_result()

    assert len(loaded.documents) == 1
    doc = loaded.documents[0]

    assert doc.doc_id == original.doc_id
    assert doc.normalized_text == original.normalized_text
    assert doc.extraction_method == original.extraction_method
    assert doc.extraction_warnings == original.extraction_warnings
    assert doc.encoding_used == original.encoding_used
    assert doc.text_statistics == original.text_statistics
    assert doc.source_document.path == original.source_document.path
    assert doc.source_document.relative_path == original.source_document.relative_path
    assert doc.source_document.format == original.source_document.format

    # source_root is not persisted but must be recoverable from
    # path/relative_path (path == source_root / relative_path).
    assert (
        doc.source_document.source_root / doc.source_document.relative_path
        == doc.source_document.path
    )

    # raw_text is genuinely absent from the artifact -- loading it must not
    # KeyError, and the placeholder must never masquerade as real text.
    assert isinstance(doc.raw_text, str)
    assert doc.raw_text != original.raw_text


def test_load_phase2_result_missing_artifact_raises(tmp_path, monkeypatch):
    """No phase2 dataset.json anywhere must raise a clear PipelineError, not KeyError."""
    from smriti.exceptions import PipelineError
    from smriti.pipeline.runner import PipelineRunner

    monkeypatch.setattr("smriti.pipeline.runner.ARTIFACTS_DIR", tmp_path / "artifacts")

    runner = PipelineRunner.__new__(PipelineRunner)
    runner.run_id = "nonexistent_run"

    with pytest.raises(PipelineError):
        runner._load_phase2_result()
