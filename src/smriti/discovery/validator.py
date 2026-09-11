"""
validator.py — Two-level validation.

Level 1: validate_directory()  — validates root input directories.
Level 2: validate_file()       — validates individual discovered files.

Responsibility:
  - Answer the binary question: "Can this path enter the pipeline?"
  - Return a ValidationResult (not raise exceptions) for files.
  - Raise DiscoveryError immediately for invalid root directories
    because the pipeline cannot proceed without valid roots.

Input:  Path
Output: ValidationResult (for files) | raises DiscoveryError (for dirs)

Design:
  - Validation is a pure predicate. No side effects.
  - The validator never reads file contents (no readability check).
  - The validator never computes hashes.
  - Every rejection reason is recorded explicitly.
"""

from dataclasses import dataclass
from pathlib import Path

import structlog

from smriti.constants import MAX_FILE_SIZE_BYTES
from smriti.core.config import get_config
from smriti.exceptions import DiscoveryError

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single file path."""

    path: Path
    is_valid: bool
    rejection_reason: str | None = None

    def __bool__(self) -> bool:
        return self.is_valid


def validate_directories(directories: list[Path]) -> list[Path]:
    """
    Validate that all input directories exist and are readable.

    Args:
        directories: Root directories to validate.

    Returns:
        List of valid, absolute, resolved directories.

    Raises:
        DiscoveryError: If any directory is invalid.
                        (Fatal — cannot start without valid roots.)
    """
    if not directories:
        raise DiscoveryError("No input directories provided.")

    validated: list[Path] = []

    for raw_path in directories:
        path = Path(raw_path).resolve()

        if not path.exists():
            raise DiscoveryError(f"Input directory does not exist: {path}")

        if not path.is_dir():
            raise DiscoveryError(f"Input path is not a directory: {path}")

        try:
            # Attempt to list — checks read permission without reading contents
            list(path.iterdir())
        except PermissionError as e:
            raise DiscoveryError(f"Input directory is not readable: {path}") from e

        validated.append(path)
        logger.info("directory validated", path=str(path))

    return validated


def validate_file(path: Path) -> ValidationResult:
    """
    Validate a single file for pipeline inclusion.

    Args:
        path: The candidate file path.

    Returns:
        ValidationResult — never raises exceptions for individual files.

    Checks (in order, cheapest first):
        1. Path exists
        2. Is a regular file (not a directory, device, etc.)
        3. Extension is in whitelist
        4. File size is non-zero
        5. File size is within maximum limit
    (Readability is tested by the hasher; no separate open/read here.)
    """
    config = get_config()
    allowed_extensions: set = set(
        config["discovery"].get("supported_extensions", [".md", ".pdf", ".txt"])
    )
    max_file_size: int = config["discovery"].get("max_file_size_bytes", MAX_FILE_SIZE_BYTES)

    # Check 1: Exists
    if not path.exists():
        return ValidationResult(path=path, is_valid=False, rejection_reason="does not exist")

    # Check 2: Regular file
    if not path.is_file():
        return ValidationResult(path=path, is_valid=False, rejection_reason="not a regular file")

    # Check 3: Extension whitelist
    extension = path.suffix.lower()
    if extension not in allowed_extensions:
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"unsupported extension '{extension}'",
        )

    # Check 4: Non-zero size
    try:
        size = path.stat().st_size
    except OSError as e:
        return ValidationResult(path=path, is_valid=False, rejection_reason=f"stat failed: {e}")

    if size == 0:
        return ValidationResult(path=path, is_valid=False, rejection_reason="empty file (0 bytes)")

    # Check 5: Size limit
    if size > max_file_size:
        size_mb = size / (1024 * 1024)
        limit_mb = max_file_size / (1024 * 1024)
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"file too large ({size_mb:.1f} MB > {limit_mb:.0f} MB limit)",
        )

    return ValidationResult(path=path, is_valid=True)
