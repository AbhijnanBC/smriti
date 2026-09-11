"""
Integration test for Phase 1 end-to-end.

Tests the complete pipeline:
  input directories → DiscoveryResult

Uses a realistic vault fixture with:
  - Normal notes (.md, .txt, .pdf)
  - Nested subdirectories
  - Duplicate content (different filenames)
  - Invalid files (empty, wrong extension)
  - Hidden files and directories
"""

import json

import pytest
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.discovery import DiscoveryResult, run_discovery


@pytest.fixture
def realistic_vault(tmp_path):
    """
    Create a realistic Obsidian-like vault.
    """
    vault = tmp_path / "vault"
    vault.mkdir()

    # Normal notes
    ai_content = "Artificial intelligence is transforming the world."
    (vault / "AI.md").write_text(ai_content, encoding="utf-8")
    (vault / "Python.md").write_text(
        "Python is the dominant language for data science.", encoding="utf-8"
    )

    # Nested dirs
    archive = vault / "Archive"
    archive.mkdir()
    (archive / "Old_AI.md").write_text(ai_content, encoding="utf-8")  # DUPLICATE
    (archive / "Very_Old.md").write_text("Old notes about computing.", encoding="utf-8")

    research = vault / "Research" / "Papers"
    research.mkdir(parents=True)
    (research / "summary.txt").write_text("Research summary.", encoding="utf-8")
    (research / "paper.pdf").write_bytes(b"%PDF-1.4 fake content")

    # Must be ignored
    obsidian = vault / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text('{"theme": "dark"}')

    # Must be skipped
    (vault / "empty.md").write_bytes(b"")
    (vault / "unsupported.docx").write_bytes(b"PK fake docx")

    return vault


@pytest.fixture
def run_id():
    return "test_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


def test_phase1_discovers_correct_count(realistic_vault, run_id, test_managers):
    """Full discovery must find 6 documents, canonical count = 5."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert isinstance(result, DiscoveryResult)
    assert len(result.documents) == 6
    assert result.canonical_count == 5


def test_phase1_detects_one_duplicate(realistic_vault, run_id, test_managers):
    """Old_AI.md has same content as AI.md — must be detected as duplicate."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.duplicate_registry.duplicate_count == 1
    dup_paths = result.duplicate_registry.duplicate_paths
    assert any("Old_AI.md" in str(p) for p in dup_paths)


def test_phase1_skips_empty_file(realistic_vault, run_id, test_managers):
    """empty.md must appear in skipped list with appropriate reason."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("empty.md" in p for p in skipped_paths)

    skipped_reasons = {str(p): r for p, r in result.skipped}
    empty_path = next(p for p in skipped_paths if "empty.md" in p)
    assert "empty" in skipped_reasons[empty_path]


def test_phase1_skips_unsupported_extension(realistic_vault, run_id, test_managers):
    """unsupported.docx must be skipped — not crash."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("unsupported.docx" in p for p in skipped_paths)


def test_phase1_ignores_obsidian_dir(realistic_vault, run_id, test_managers):
    """No file inside .obsidian/ must appear in results."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    all_paths = [str(d.path) for d in result.documents]
    assert not any(".obsidian" in p for p in all_paths)


def test_phase1_documents_are_immutable(realistic_vault, run_id, test_managers):
    """SourceDocument must be frozen (no mutation allowed)."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_phase1_writes_manifest(realistic_vault, run_id, test_managers):
    """A manifest.json must be written after discovery."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.manifest_path is not None
    assert result.manifest_path.exists()

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 1
    assert manifest["status"] == "success"
    assert manifest["run_id"] == run_id
    assert manifest["outputs"]["canonical_documents"] == 5


def test_phase1_writes_dataset_json(realistic_vault, run_id, test_managers, tmp_path):
    """dataset.json must be written to artifacts/run_id/phase1/."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    dataset_paths = list((tmp_path / "artifacts" / f"run_{run_id}" / "phase1").glob("dataset.json"))
    assert len(dataset_paths) == 1

    dataset = json.loads(dataset_paths[0].read_text(encoding="utf-8"))
    assert len(dataset) == 5  # canonical only
    # Rectified: doc_id must equal content_hash
    for doc in dataset:
        assert "doc_id" in doc
        assert "content_hash" in doc
        assert doc["doc_id"] == doc["content_hash"]


def test_phase1_updates_pipeline_state(realistic_vault, run_id, test_managers):
    """Pipeline state must be updated to mark Phase 1 as complete."""
    manifest_mgr, state_mgr = test_managers

    run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    state = state_mgr.load()
    assert state is not None
    assert 1 in state.completed_phases


def test_phase1_is_idempotent(realistic_vault, run_id, test_managers):
    """Running Phase 1 twice on same input must produce same canonical count."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    result2 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id + "_2",
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result1.canonical_count == result2.canonical_count


def test_phase1_no_nlp_imports():
    """Phase 1 must never import NLP libraries."""
    import smriti.discovery.builder as builder_mod
    import smriti.discovery.duplicate as duplicate_mod
    import smriti.discovery.hashing as hashing_mod
    import smriti.discovery.metadata as metadata_mod
    import smriti.discovery.scanner as scanner
    import smriti.discovery.validator as validator

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [scanner, validator, metadata_mod, hashing_mod, duplicate_mod, builder_mod]:
        module_imports = set(vars(module).keys())
        assert not (
            module_imports & nlp_modules
        ), f"{module.__name__} imports NLP libraries — Phase 1 must not do NLP"
