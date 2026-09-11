"""
Unit tests for discovery/metadata.py.
"""

import dataclasses
from datetime import UTC

import pytest
from smriti.discovery.metadata import extract_metadata


def test_metadata_size(tmp_path):
    """size_bytes must match actual file size."""
    content = b"Hello, world! This is test content."
    f = tmp_path / "note.md"
    f.write_bytes(content)

    meta = extract_metadata(f)
    assert meta.size_bytes == len(content)


def test_metadata_extension_normalised(tmp_path):
    """Extension must be lowercase."""
    f = tmp_path / "NOTE.MD"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.extension == ".md"


def test_metadata_modified_time_is_utc(tmp_path):
    """modified_at must be UTC-aware."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.modified_at.tzinfo is not None
    assert meta.modified_at.tzinfo == UTC


def test_metadata_is_immutable(tmp_path):
    """FileMetadata is frozen — mutation must raise."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    with pytest.raises(dataclasses.FrozenInstanceError):
        meta.size_bytes = 999
