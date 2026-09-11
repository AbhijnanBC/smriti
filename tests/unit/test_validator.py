"""
Unit tests for discovery/validator.py.

Validator has two jobs:
  1. validate_directories() — fatal check of input roots
  2. validate_file()        — per-file check, returns ValidationResult
"""

import pytest
from smriti.discovery.validator import validate_directories, validate_file
from smriti.exceptions import DiscoveryError


@pytest.fixture
def valid_md(tmp_path):
    f = tmp_path / "valid.md"
    f.write_text("Some content here.")
    return f


@pytest.fixture
def empty_file(tmp_path):
    f = tmp_path / "empty.md"
    f.write_bytes(b"")
    return f


@pytest.fixture
def unsupported_file(tmp_path):
    f = tmp_path / "document.docx"
    f.write_bytes(b"fake docx content")
    return f


# ── validate_directories ──────────────────────────────────────────────────────


def test_valid_directory_passes(tmp_path):
    """A valid existing directory must be returned."""
    result = validate_directories([tmp_path])
    assert result == [tmp_path.resolve()]


def test_nonexistent_directory_raises(tmp_path):
    """A directory that doesn't exist must raise DiscoveryError."""
    missing = tmp_path / "does_not_exist"
    with pytest.raises(DiscoveryError, match="does not exist"):
        validate_directories([missing])


def test_file_as_directory_raises(tmp_path):
    """Passing a file path as a directory must raise DiscoveryError."""
    f = tmp_path / "file.txt"
    f.write_text("not a directory")
    with pytest.raises(DiscoveryError, match="not a directory"):
        validate_directories([f])


def test_empty_list_raises():
    """Empty input list must raise DiscoveryError."""
    with pytest.raises(DiscoveryError, match="No input directories"):
        validate_directories([])


# ── validate_file ─────────────────────────────────────────────────────────────


def test_valid_markdown_passes(valid_md):
    """A valid non-empty .md file must pass validation."""
    result = validate_file(valid_md)
    assert result.is_valid is True
    assert result.rejection_reason is None


def test_nonexistent_file_fails(tmp_path):
    """A file that doesn't exist must fail with 'does not exist'."""
    missing = tmp_path / "ghost.md"
    result = validate_file(missing)
    assert result.is_valid is False
    assert "does not exist" in result.rejection_reason


def test_empty_file_fails(empty_file):
    """A zero-byte file must fail validation."""
    result = validate_file(empty_file)
    assert result.is_valid is False
    assert "empty" in result.rejection_reason


def test_unsupported_extension_fails(unsupported_file):
    """Files with unsupported extensions must be rejected."""
    result = validate_file(unsupported_file)
    assert result.is_valid is False
    assert "unsupported extension" in result.rejection_reason


def test_pdf_file_passes(tmp_path):
    """A non-empty .pdf file must pass validation."""
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake pdf content")
    result = validate_file(pdf)
    assert result.is_valid is True


def test_txt_file_passes(tmp_path):
    """A non-empty .txt file must pass validation."""
    txt = tmp_path / "notes.txt"
    txt.write_text("Some plain text.")
    result = validate_file(txt)
    assert result.is_valid is True


def test_validation_result_is_bool(valid_md):
    """ValidationResult must be usable as a boolean."""
    result = validate_file(valid_md)
    assert bool(result) is True
