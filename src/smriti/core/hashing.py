"""
Content hashing for incremental processing.
Detects which notes changed since last run — skip the rest.
"""

import hashlib
import json
from pathlib import Path

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE
from smriti.core.paths import HASH_CACHE_FILE


class ContentHasher:
    """Computes and persists content hashes for change detection."""

    def __init__(self, cache_file: Path = HASH_CACHE_FILE):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.hashes: dict[str, str] = self._load()

    def compute_hash(self, content: str) -> str:
        """SHA-256 hash of a string."""
        return hashlib.new(HASH_ALGORITHM, content.encode("utf-8")).hexdigest()

    def compute_file_hash(self, file_path: Path) -> str:
        """SHA-256 hash of a file (chunked for large files)."""
        h = hashlib.new(HASH_ALGORITHM)
        with open(file_path, "rb") as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()

    def has_changed(self, path: Path, content: str) -> bool:
        """True if content differs from last stored hash (or not yet seen)."""
        current = self.compute_hash(content)
        return self.hashes.get(str(path)) != current

    def update_hash(self, path: Path, content: str) -> None:
        """Store current hash for a file."""
        self.hashes[str(path)] = self.compute_hash(content)
        self._save()

    def clear(self) -> None:
        """Reset all stored hashes."""
        self.hashes = {}
        self._save()

    def _load(self) -> dict[str, str]:
        if self.cache_file.exists():
            with open(self.cache_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.hashes, f, indent=2)
