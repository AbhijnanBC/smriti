"""
scanner.py — Recursive file discovery (iterative).

Responsibility: Given a list of validated root directories, return a
sorted list of candidate file paths. Nothing more.

Input:  List[Path]  — validated root directories
Output: List[Path]  — candidate files, sorted deterministically

Rules:
  - Traversal is recursive, unlimited depth (uses stack, no recursion)
  - Output is always sorted alphabetically (full path)
  - Hidden directories and system folders are skipped
  - Broken symlinks are skipped with a warning
  - Permission errors are warned and skipped — never fatal
  - The scanner never reads file contents
  - The scanner never validates individual files (that is validator.py)
"""

from pathlib import Path

import structlog

from smriti.core.config import get_config

logger = structlog.get_logger(__name__)


# Directories that are always skipped, regardless of config.
# These are non-negotiable system directories.
_ALWAYS_IGNORE: set[str] = {
    ".git",
    ".obsidian",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
}


def discover_files(root_dirs: list[Path]) -> list[Path]:
    """
    Recursively discover all candidate files under root_dirs.

    Args:
        root_dirs: Pre-validated root directories to scan.

    Returns:
        Sorted list of candidate file paths.
        Sorting is by full absolute path (alphabetical, case-insensitive on Windows).

    Raises:
        Nothing. All errors are logged and skipped.
    """
    config = get_config()
    ignored_dirs: set[str] = _ALWAYS_IGNORE | set(config["discovery"].get("ignored_dirs", []))

    candidates: list[Path] = []

    for root_dir in root_dirs:
        logger.info("scanning directory", path=str(root_dir))
        _scan_iterative(root_dir, root_dir, ignored_dirs, candidates)

    # RULE: Output must always be sorted. Never trust OS ordering.
    candidates.sort(key=lambda p: str(p))

    logger.info(
        "discovery complete",
        total_candidates=len(candidates),
        roots_scanned=len(root_dirs),
    )

    return candidates


# Iterative (stack-based, not recursive) directory walk with several
# independent skip conditions (ignored dirs, symlinks, hidden files, size
# limits); each check is simple, but there are enough of them to trip
# mccabe's threshold.
def _scan_iterative(  # noqa: C901
    root_dir: Path,
    root_dir_original: Path,
    ignored_dirs: set[str],
    accumulator: list[Path],
) -> None:
    """
    Iterative directory walk using a stack.
    This is the only function that touches the filesystem in scanner.py.
    """
    stack = [root_dir]
    visited = {root_dir.resolve()}

    while stack:
        current_dir = stack.pop()

        try:
            # Sort directory contents for determinism within each directory.
            entries = sorted(current_dir.iterdir(), key=lambda e: e.name)
        except PermissionError:
            logger.warning("permission denied, skipping directory", path=str(current_dir))
            continue
        except OSError as e:
            logger.warning("cannot read directory", path=str(current_dir), error=str(e))
            continue

        for entry in entries:
            # Skip hidden files and directories (name starts with ".")
            if entry.name.startswith("."):
                logger.debug("skipping hidden entry", path=str(entry))
                continue

            # Skip system/ignored directories
            if entry.name in ignored_dirs:
                logger.debug("skipping ignored directory", path=str(entry))
                continue

            if entry.is_symlink():
                # Broken symlink — skip with warning
                if not entry.exists():
                    logger.warning("broken symlink, skipping", path=str(entry))
                    continue
                # Valid symlink pointing to a file — follow it
                # Valid symlink pointing to a directory — recurse
                resolved = entry.resolve()
                # Guard against symlink loops pointing outside the vault
                if resolved == root_dir_original or str(resolved).startswith(
                    str(root_dir_original)
                ):
                    pass  # within vault, safe to follow
                else:
                    logger.debug("symlink points outside vault, skipping", path=str(entry))
                    continue

            if entry.is_dir():
                resolved_dir = entry.resolve()  # <-- ADD THIS
                if resolved_dir not in visited:  # <-- ADD THIS: Cycle protection
                    visited.add(resolved_dir)
                    stack.append(entry)
                else:  # <-- ADD THIS
                    logger.debug("symlink cycle detected, skipping", path=str(entry))
            elif entry.is_file():
                accumulator.append(entry.resolve())
