"""
duplicate.py — Content-based duplicate detection.

Responsibility: Given a sequence of (path, hash) pairs, identify which
paths have identical content to a path seen earlier.

Input:  List of (path, hash) tuples — processed in discovery order
Output: DuplicateRegistry — maps each hash to its canonical path and alternates,
        plus a reverse dict for O(1) canonical lookup.

Complexity: O(n) — dictionary lookup, not pairwise comparison.

Rules:
  - "Duplicate" means identical SHA256 hash. Nothing else.
  - Same filename in different folders is NOT a duplicate.
  - First file encountered with a given hash becomes the canonical document.
  - Subsequent files with the same hash are recorded as alternate locations.
  - Duplicates are never silently discarded — always recorded.
  - This module has no filesystem access. It only compares strings.
"""

from dataclasses import dataclass, field
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DuplicateEntry:
    """
    Records a hash and all paths that share it.
    canonical_path: First file discovered with this hash.
    alternate_paths: All subsequent files with the same hash.
    """

    hash: str
    canonical_path: Path
    alternate_paths: list[Path] = field(default_factory=list)

    @property
    def is_duplicate(self) -> bool:
        """True if at least one other file shares this content."""
        return len(self.alternate_paths) > 0

    @property
    def all_paths(self) -> list[Path]:
        """All paths sharing this content, canonical first."""
        return [self.canonical_path] + self.alternate_paths


@dataclass
class DuplicateRegistry:
    """
    Complete result of duplicate detection for one discovery run.

    Attributes:
        entries:          hash → DuplicateEntry
        canonical_paths:  set of paths that are canonical (one per unique hash)
        duplicate_paths:  set of paths that are duplicates
        _duplicate_to_canonical: dict for O(1) reverse lookup
    """

    entries: dict[str, DuplicateEntry] = field(default_factory=dict)
    canonical_paths: set = field(default_factory=set)
    duplicate_paths: set = field(default_factory=set)
    _duplicate_to_canonical: dict[Path, Path] = field(default_factory=dict)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicate_paths)

    @property
    def unique_content_count(self) -> int:
        return len(self.entries)

    def is_canonical(self, path: Path) -> bool:
        return path in self.canonical_paths

    def is_duplicate(self, path: Path) -> bool:
        return path in self.duplicate_paths

    def get_canonical_for(self, path: Path) -> Path | None:
        """Given a duplicate path, return the canonical path for its content (O(1))."""
        return self._duplicate_to_canonical.get(path)


def build_duplicate_registry(path_hash_pairs: list[tuple[Path, str]]) -> DuplicateRegistry:
    """
    Build a complete duplicate registry from path-hash pairs.

    Args:
        path_hash_pairs: [(path, sha256_hex_digest), ...]
                         Must be in sorted discovery order.

    Returns:
        DuplicateRegistry with canonical and duplicate classifications.
    """
    registry = DuplicateRegistry()

    for path, content_hash in path_hash_pairs:
        if content_hash not in registry.entries:
            # First file with this hash — it is canonical
            entry = DuplicateEntry(hash=content_hash, canonical_path=path)
            registry.entries[content_hash] = entry
            registry.canonical_paths.add(path)
        else:
            # A file with identical content exists — this is a duplicate
            registry.entries[content_hash].alternate_paths.append(path)
            registry.duplicate_paths.add(path)
            registry._duplicate_to_canonical[path] = registry.entries[content_hash].canonical_path
            canonical = registry.entries[content_hash].canonical_path
            logger.warning(
                "duplicate content detected",
                duplicate_path=str(path),
                canonical_path=str(canonical),
                hash_prefix=content_hash[:8],
            )

    if registry.duplicate_count > 0:
        logger.info(
            "duplicate detection complete",
            unique_contents=registry.unique_content_count,
            duplicates=registry.duplicate_count,
        )

    return registry
