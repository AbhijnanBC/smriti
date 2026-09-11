"""
Configuration management for SMRITI.

Loading order:
  1. config/default.yaml     — complete baseline
  2. config/{env}.yaml       — environment overrides (deep-merged)

Deep merge: nested keys are merged recursively, not overwritten.
Model names and thresholds belong here, not in constants.py.
"""

from pathlib import Path
from typing import Any, Optional

import yaml

from smriti.core.paths import CONFIG_DIR
from smriti.exceptions import ConfigError

# Module-level singleton — call get_config() everywhere
_config: Optional["Config"] = None


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge override into base.
    Nested dicts are merged; scalars are overwritten.

    Example:
        base     = {"embedding": {"model": "MiniLM", "batch_size": 32}}
        override = {"embedding": {"batch_size": 8}}
        result   = {"embedding": {"model": "MiniLM", "batch_size": 8}}
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Load and expose layered YAML configuration."""

    def __init__(self, env: str = "dev", config_dir: Path = CONFIG_DIR):
        self.env = env
        self._data: dict[str, Any] = {}
        self._load(config_dir)

    def _load(self, config_dir: Path) -> None:
        """Load default config then deep-merge env override."""
        default_path = config_dir / "default.yaml"
        if not default_path.exists():
            raise ConfigError(f"Missing required config file: {default_path}")

        with open(default_path, encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        env_path = config_dir / f"{self.env}.yaml"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
            self._data = _deep_merge(self._data, env_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Top-level key access with optional default."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dict-style access: config["embedding"]["model"]."""
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data


def get_config(env: str = "dev") -> Config:
    """Return the module-level config singleton (lazy init)."""
    global _config
    if _config is None:
        _config = Config(env=env)
    return _config
