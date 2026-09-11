"""
Unit tests for embedding/cache.py.
Includes schema_version validation (critical fix).
"""

import pickle

import pytest
from smriti.embedding.cache import CACHE_SCHEMA_VERSION, EmbeddingCachePolicy
from smriti.embedding.models import EmbeddingStatus


@pytest.fixture
def cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=True)


@pytest.fixture
def disabled_cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=False)


def test_miss_on_empty_cache(cache):
    status, vector = cache.lookup("nonexistent_key", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_store_and_retrieve(cache):
    vector = [0.1, 0.2, 0.3]
    cache.store("key001", vector, "sig_A", "hash_X")
    status, retrieved = cache.lookup("key001", "sig_A", "hash_X")
    assert status == EmbeddingStatus.CACHED
    assert retrieved == vector


def test_stale_on_model_change(cache):
    """Different model signature → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_B", "hash_X")
    assert status == EmbeddingStatus.STALE


def test_stale_on_config_change(cache):
    """Different config hash → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_A", "hash_Y")
    assert status == EmbeddingStatus.STALE


def test_stale_on_schema_version_mismatch(cache, tmp_path):
    """
    Cache entry with an old schema_version → STALE.
    This is the critical fix: schema changes must not silently reuse old artifacts.
    """
    cache_dir = tmp_path / "emb_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Write an entry with an old schema_version directly
    old_entry = {
        "vector": [0.1, 0.2, 0.3],
        "model_sig": "sig_A",
        "config_hash": "hash_X",
        "schema_version": "4.0",  # Old schema — incompatible
    }
    cache_file = cache_dir / "key_old.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(old_entry, f)

    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    status, vector = policy.lookup("key_old", "sig_A", "hash_X")
    assert status == EmbeddingStatus.STALE
    assert vector is None


def test_stored_entry_has_current_schema_version(cache, tmp_path):
    """Stored entries must include CACHE_SCHEMA_VERSION."""
    cache_dir = tmp_path / "emb_cache2"
    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    policy.store("key001", [0.1, 0.2], "sig", "hash")
    with open(cache_dir / "key001.pkl", "rb") as f:
        entry = pickle.load(f)
    assert entry["schema_version"] == CACHE_SCHEMA_VERSION


def test_disabled_cache_returns_failed(disabled_cache):
    status, vector = disabled_cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_clear_all(cache):
    cache.store("key001", [0.1], "sig", "hash")
    cache.store("key002", [0.2], "sig", "hash")
    count = cache.clear_all()
    assert count == 2
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED


def test_invalidate_specific_key(cache):
    cache.store("key001", [0.1, 0.2], "sig", "hash")
    removed = cache.invalidate("key001")
    assert removed is True
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
