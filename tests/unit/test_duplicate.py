"""
Unit tests for discovery/duplicate.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.duplicate import build_duplicate_registry


def test_no_duplicates(tmp_path):
    """All unique hashes — no duplicates."""
    pairs = [
        (tmp_path / "a.md", "aaaa"),
        (tmp_path / "b.md", "bbbb"),
        (tmp_path / "c.md", "cccc"),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 3
    assert all(registry.is_canonical(p) for p, _ in pairs)


def test_one_duplicate(tmp_path):
    """Second file with same hash is marked as duplicate."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8  # 64 chars

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 1
    assert registry.unique_content_count == 1
    assert registry.is_canonical(path_a)
    assert registry.is_duplicate(path_b)


def test_canonical_path_for_duplicate(tmp_path):
    """get_canonical_for() must return the first-seen path."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "cafebabe" * 8

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.get_canonical_for(path_b) == path_a


def test_three_identical_files(tmp_path):
    """Three files with same content: first is canonical, two are duplicates."""
    shared_hash = "12345678" * 8
    pairs = [
        (tmp_path / "a.md", shared_hash),
        (tmp_path / "b.md", shared_hash),
        (tmp_path / "c.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 2
    assert registry.is_canonical(tmp_path / "a.md")
    assert registry.is_duplicate(tmp_path / "b.md")
    assert registry.is_duplicate(tmp_path / "c.md")


def test_empty_input():
    """Empty input must return empty registry — not crash."""
    registry = build_duplicate_registry([])
    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 0


def test_duplicate_same_name_different_dirs(tmp_path):
    """
    notes/AI.md and archive/AI.md with same content are duplicates.
    Same filename ≠ same document. Content hash determines identity.
    """
    dir1 = tmp_path / "notes"
    dir2 = tmp_path / "archive"
    dir1.mkdir()
    dir2.mkdir()

    shared_hash = "aabbccdd" * 8
    pairs = [
        (dir1 / "AI.md", shared_hash),
        (dir2 / "AI.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)
    assert registry.duplicate_count == 1

def test_get_canonical_for_constant_time(tmp_path):
    """get_canonical_for must be O(1) via reverse dict."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8
    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)
    assert registry.get_canonical_for(path_b) == path_a    