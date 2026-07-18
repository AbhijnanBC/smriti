"""Shared pytest fixtures."""

import pytest
from pathlib import Path
from smriti.core.config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(tmp_path_factory):
    """Point config to test.yaml for the whole test session."""
    import smriti.core.config as cfg_module
    cfg_module._config = Config(env="test")


@pytest.fixture
def tmp_artifacts(tmp_path):
    """Temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


@pytest.fixture
def test_config():
    """Return a test Config instance."""
    return Config(env="test")


@pytest.fixture
def tmp_notes(tmp_path):
    """Create temporary markdown note files."""
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()

    (notes_dir / "note1.md").write_text(
        "# Note 1\n\nPython is the best language for data science.\n"
    )
    (notes_dir / "note2.md").write_text(
        "# Note 2\n\nRust is better than Python for performance.\n"
    )
    return notes_dir


@pytest.fixture
def sample_markdown(tmp_path):
    """Single sample markdown note."""
    note = tmp_path / "note.md"
    note.write_text(
        "# Test Note\n\nCreated: 2024-01-15\n\n"
        "Python is great for data science.\n\n"
        "But for some tasks, Julia is faster.\n"
    )
    return note