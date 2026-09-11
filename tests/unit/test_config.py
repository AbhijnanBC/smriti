"""Test deep-merge config loader."""

from smriti.core.config import Config, _deep_merge


def test_deep_merge_flat():
    base = {"a": 1, "b": 2}
    override = {"b": 99, "c": 3}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_deep_merge_nested_does_not_overwrite_sibling_keys():
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    result = _deep_merge(base, override)
    # model should survive; batch_size should be overridden
    assert result["embedding"]["model"] == "MiniLM"
    assert result["embedding"]["batch_size"] == 8


def test_deep_merge_shallow_update_would_fail():
    """Demonstrates why dict.update() is wrong for nested config."""
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    # shallow update — loses model key
    shallow = dict(base)
    shallow.update(override)
    assert "model" not in shallow["embedding"]  # broken
    # deep merge — keeps model key
    deep = _deep_merge(base, override)
    assert "model" in deep["embedding"]  # correct


def test_config_loads_default(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text("embedding:\n  model: MiniLM\n  batch_size: 32\n")
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"
    assert cfg["embedding"]["batch_size"] == 32


def test_config_dev_override_deep_merges(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text("embedding:\n  model: MiniLM\n  batch_size: 32\n")
    (config_dir / "dev.yaml").write_text("embedding:\n  batch_size: 8\n")
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"  # inherited
    assert cfg["embedding"]["batch_size"] == 8  # overridden
