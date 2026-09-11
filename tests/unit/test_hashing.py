"""
Unit tests for discovery/hashing.py.
"""

from smriti.discovery.hashing import compute_hash


def test_same_content_same_hash(tmp_path):
    """Identical content must always produce the same hash."""
    content = "Python is great for data science."
    f1 = tmp_path / "note1.md"
    f2 = tmp_path / "note2.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_different_content_different_hash(tmp_path):
    """Different content must produce different hashes."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Julia is faster.", encoding="utf-8")

    assert compute_hash(f1) != compute_hash(f2)


def test_rename_does_not_change_hash(tmp_path):
    """Renaming a file must produce the same hash (content-only)."""
    content = "The hash must not depend on the filename."
    f1 = tmp_path / "original.md"
    f2 = tmp_path / "renamed.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_hash_is_64_character_hex(tmp_path):
    """SHA256 hex digest must be exactly 64 lowercase hex characters."""
    f = tmp_path / "note.md"
    f.write_text("content", encoding="utf-8")
    h = compute_hash(f)

    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_one_byte_change_changes_hash(tmp_path):
    """A single character change must produce a completely different hash."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Python is greet.", encoding="utf-8")  # 'a' → 'e'

    assert compute_hash(f1) != compute_hash(f2)


def test_hash_deterministic_across_calls(tmp_path):
    """Multiple calls on the same file must return the same hash."""
    f = tmp_path / "note.md"
    f.write_text("Determinism is essential.", encoding="utf-8")

    h1 = compute_hash(f)
    h2 = compute_hash(f)
    h3 = compute_hash(f)

    assert h1 == h2 == h3
