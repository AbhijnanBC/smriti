"""
hashing.py — Content fingerprinting.

Responsibility: Compute a SHA256 hash of file contents.

Input:  Validated Path
Output: str  — hex digest (64 characters)

Rules:
  - Hash file CONTENTS only. Never filename, path, or timestamps.
  - Read in chunks to handle arbitrarily large files without OOM.
  - This module has no knowledge of caching, duplicates, or manifests.
  - One public function: compute_hash(path) → str

Why content-only hashing matters:
  - Renaming "AI.md" → "Artificial_Intelligence.md" should NOT create a new identity.
  - Moving a file to a different folder should NOT create a new identity.
  - Changing one word inside SHOULD produce a completely different identity.
"""

import hashlib
from pathlib import Path

import structlog

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE

logger = structlog.get_logger(__name__)


def compute_hash(path: Path) -> str:
    """
    Compute SHA256 hash of file contents.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        64-character lowercase hex digest.

    Raises:
        OSError: If the file cannot be read.
    """
    hasher = hashlib.new(HASH_ALGORITHM)

    with open(path, "rb") as f:
        while chunk := f.read(HASH_CHUNK_SIZE):
            hasher.update(chunk)

    digest = hasher.hexdigest()

    logger.debug("hash computed", path=str(path), hash_prefix=digest[:8])

    return digest
