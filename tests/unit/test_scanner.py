"""
Unit tests for discovery/scanner.py.

Scanner has one job: find files.
These tests never touch hashing, validation, or manifests.
"""

import pytest
from smriti.discovery.scanner import discover_files


@pytest.fixture
def notes_dir(tmp_path):
    """Create a small realistic vault structure."""
    # Normal notes
    (tmp_path / "AI.md").write_text("AI is transforming everything.")
    (tmp_path / "Python.md").write_text("Python is great for data science.")
    (tmp_path / "Notes.txt").write_text("Some plain text notes.")

    # Subdirectory
    subdir = tmp_path / "Archive"
    subdir.mkdir()
    (subdir / "Old.md").write_text("An old note.")
    (subdir / "Report.pdf").write_bytes(b"%PDF-1.4 fake pdf content")

    # Files that must be ignored
    (tmp_path / ".hidden_file.md").write_text("Hidden — must be ignored.")
    obsidian = tmp_path / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text("{}")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main")

    return tmp_path


def test_discovers_markdown_files(notes_dir):
    """Scanner finds .md files recursively."""
    results = discover_files([notes_dir])
    md_files = [p for p in results if p.suffix.lower() == ".md"]
    assert len(md_files) == 3  # AI.md, Python.md, Archive/Old.md


def test_discovers_txt_and_pdf(notes_dir):
    """Scanner finds .txt and .pdf files."""
    results = discover_files([notes_dir])
    extensions = {p.suffix.lower() for p in results}
    assert ".txt" in extensions
    assert ".pdf" in extensions


def test_ignores_hidden_files(notes_dir):
    """Files starting with '.' must be excluded."""
    results = discover_files([notes_dir])
    names = [p.name for p in results]
    assert ".hidden_file.md" not in names


def test_ignores_obsidian_dir(notes_dir):
    """The .obsidian directory must be skipped entirely."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".obsidian" in p for p in paths_str)


def test_ignores_git_dir(notes_dir):
    """The .git directory must be skipped."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".git" in p for p in paths_str)


def test_output_is_sorted(notes_dir):
    """Discovery output must always be sorted (deterministic)."""
    results = discover_files([notes_dir])
    lower_paths = [str(p).lower() for p in results]
    assert lower_paths == sorted(lower_paths)


def test_empty_directory_returns_empty_list(tmp_path):
    """Empty directory must return [] — not crash."""
    results = discover_files([tmp_path])
    assert results == []


def test_multiple_root_dirs(tmp_path):
    """Scanner accepts multiple root directories."""
    dir_a = tmp_path / "vault_a"
    dir_b = tmp_path / "vault_b"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "note1.md").write_text("Note one.")
    (dir_b / "note2.md").write_text("Note two.")

    results = discover_files([dir_a, dir_b])
    assert len(results) == 2


def test_deeply_nested_dirs(tmp_path):
    """Recursion must be unlimited depth."""
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "deep.md").write_text("Deep nested note.")

    results = discover_files([tmp_path])
    assert any("deep.md" in str(p) for p in results)


def test_unicode_filenames(tmp_path):
    """Unicode filenames must work correctly on Windows."""
    (tmp_path / "日本語.md").write_text("Japanese filename.", encoding="utf-8")
    (tmp_path / "ñoño.md").write_text("Spanish accents.", encoding="utf-8")
    (tmp_path / "ನನ್ನ_ಟಿಪ್ಪಣಿ.md").write_text("Kannada filename.", encoding="utf-8")

    results = discover_files([tmp_path])
    assert len(results) == 3


def test_filenames_with_spaces(tmp_path):
    """Filenames with spaces are legal and must be found."""
    (tmp_path / "Machine Learning Notes.md").write_text("Notes on ML.")
    results = discover_files([tmp_path])
    assert any("Machine Learning Notes" in str(p) for p in results)
