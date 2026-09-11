"""
Integration test for Phase 2 end-to-end.

Tests the complete pipeline:
  List[SourceDocument] → ExtractionResult

Uses a realistic vault fixture with all supported formats.
"""

import json
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
def vault_documents(tmp_path):
    """Create a realistic set of source documents for testing."""
    vault = tmp_path / "vault"
    vault.mkdir()

    docs = []

    # --- Markdown documents ---
    ai_md = vault / "AI.md"
    ai_md.write_text(
        "# Artificial Intelligence\n\n"
        "AI is transforming every industry.\n\n"
        "## Machine Learning\n\n"
        "Machine learning is a subset of AI.\n",
        encoding="utf-8",
    )
    docs.append(make_source(ai_md, FileFormat.MARKDOWN))

    python_md = vault / "Python.md"
    python_md.write_text(
        "# Python\n\nPython is the dominant language for data science.\n\n"
        "It is also used for web development.\n",
        encoding="utf-8",
    )
    docs.append(make_source(python_md, FileFormat.MARKDOWN))

    # Unicode content
    unicode_md = vault / "unicode.md"
    unicode_md.write_text(
        "# 研究ノート\n\nCafé résumé naïve.\n\nПривет мир.\n",
        encoding="utf-8",
    )
    docs.append(make_source(unicode_md, FileFormat.MARKDOWN))

    # Markdown with CRLF endings
    crlf_md = vault / "crlf.md"
    crlf_md.write_bytes(b"# Windows File\r\n\r\nWritten on Windows.\r\n")
    docs.append(make_source(crlf_md, FileFormat.MARKDOWN))

    # --- Text documents ---
    txt = vault / "notes.txt"
    txt.write_text(
        "Plain text research notes.\n\nSecond paragraph of notes.\n",
        encoding="utf-8",
    )
    docs.append(make_source(txt, FileFormat.TEXT))

    return docs


@pytest.fixture
def run_id():
    return "test_phase2_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Functional tests ──────────────────────────────────────────────────────────


def test_phase2_produces_documents(vault_documents, run_id, test_managers):
    """Phase 2 must return a Document for every valid SourceDocument."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=vault_documents,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    assert len(result.documents) == len(vault_documents)
    assert result.stats.failed == 0


def test_phase2_documents_are_frozen(vault_documents, run_id, test_managers):
    """Document must be frozen (immutable)."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.normalized_text = "mutated"


def test_phase2_doc_id_preserved(vault_documents, run_id, test_managers):
    """doc_id must equal source_document.doc_id for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert doc.doc_id == doc.source_document.doc_id


def test_phase2_crlf_normalized(vault_documents, run_id, test_managers):
    """CRLF line endings must be normalized to LF in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert "\r\n" not in doc.normalized_text
        assert "\r" not in doc.normalized_text


def test_phase2_markdown_headings_preserved(vault_documents, run_id, test_managers):
    """Markdown # headings must survive in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    md_docs = [d for d in result.documents if "AI.md" in str(d.source_document.path)]
    assert len(md_docs) == 1
    assert "# Artificial Intelligence" in md_docs[0].normalized_text


def test_phase2_unicode_preserved(vault_documents, run_id, test_managers):
    """Unicode content must be preserved correctly."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    unicode_docs = [d for d in result.documents if "unicode.md" in str(d.source_document.path)]
    assert len(unicode_docs) == 1
    assert "研究" in unicode_docs[0].normalized_text
    assert "Café" in unicode_docs[0].normalized_text


def test_phase2_statistics_consistent(vault_documents, run_id, test_managers):
    """TextStatistics invariants must hold for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        s = doc.text_statistics
        assert s.character_count >= 0
        assert s.word_count >= 0
        assert s.blank_line_count <= s.line_count
        assert s.paragraph_count <= s.line_count


def test_phase2_one_failure_does_not_stop_batch(run_id, test_managers, tmp_path):
    """A corrupted document must not stop processing of the remaining documents."""
    from smriti.core.models import SourceDocument

    vault = tmp_path / "vault"
    vault.mkdir()

    # Valid document
    good = vault / "good.md"
    good.write_text("# Good\n\nThis is fine.", encoding="utf-8")

    # Document pointing to nonexistent file
    ghost_source = SourceDocument(
        doc_id="b" * 64,
        path=tmp_path / "ghost.md",  # Does not exist
        relative_path=Path("ghost.md"),
        source_root=tmp_path,
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=0,
        modified_at=datetime.now(tz=UTC),
    )

    good_source = make_source(good, FileFormat.MARKDOWN)

    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=[good_source, ghost_source],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    # Good document succeeded, ghost failed — batch continued
    assert result.stats.successful == 1
    assert result.stats.failed == 1
    assert len(result.documents) == 1


# ── Artifact tests ────────────────────────────────────────────────────────────


def test_phase2_writes_manifest(vault_documents, run_id, test_managers):
    """A manifest.json must be written after Phase 2."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 2
    assert manifest["status"] in ("success", "partial")
    assert manifest["run_id"] == run_id


def test_phase2_writes_dataset_json(vault_documents, run_id, test_managers, tmp_path):
    """dataset.json must be written with correct structure."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()

    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    assert len(dataset) == len(result.documents)

    for record in dataset:
        assert "doc_id" in record
        assert "normalized_text" in record
        assert "text_statistics" in record
        assert "extraction_method" in record
        # raw_text must NOT be in the dataset — too large, not needed by Phase 3
        assert "raw_text" not in record


def test_phase2_dataset_has_no_raw_text(vault_documents, run_id, test_managers):
    """dataset.json must never contain raw_text — only normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    for record in dataset:
        assert "raw_text" not in record


def test_phase2_updates_pipeline_state(vault_documents, run_id, test_managers):
    """Pipeline state must mark Phase 2 as complete."""
    manifest_mgr, state_mgr = test_managers
    run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    state = state_mgr.load()
    assert state is not None
    assert 2 in state.completed_phases


# ── Architectural tests ───────────────────────────────────────────────────────


def test_phase2_no_nlp_imports():
    """Phase 2 must never import NLP libraries."""
    import smriti.parsing.builder as builder_mod
    import smriti.parsing.loader as loader_mod
    import smriti.parsing.markdown as markdown_mod
    import smriti.parsing.normalize as normalize_mod
    import smriti.parsing.statistics as statistics_mod
    import smriti.parsing.text as text_mod

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [markdown_mod, text_mod, normalize_mod, statistics_mod, builder_mod, loader_mod]:
        module_imports = set(vars(module).keys())
        assert not (
            module_imports & nlp_modules
        ), f"{module.__name__} imports NLP libraries — Phase 2 must not do NLP"


def test_phase2_is_deterministic(vault_documents, test_managers, tmp_path):
    """Running Phase 2 twice on same input must produce identical normalized_text."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_extraction(vault_documents, "run1", manifest_mgr, state_mgr)
    result2 = run_extraction(vault_documents, "run2", manifest_mgr, state_mgr)

    texts1 = {d.doc_id: d.normalized_text for d in result1.documents}
    texts2 = {d.doc_id: d.normalized_text for d in result2.documents}

    assert texts1 == texts2
