"""
compatibility.py — Strict Version Compatibility Between Architectural Phases

Defines explicit version contracts between components. Acts as a gateway
to ensure that only compatible artifacts, APIs, and manifests can interact.

Contracts are defined as (source, target) -> VersionContract.
If no contract exists, compatibility is assumed (lenient).
If a contract exists, both minimum and maximum versions are enforced,
with support for semantic versioning and wildcard 'x' (e.g., "1.x").
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

from smriti.exceptions import GovernanceException


@dataclass(frozen=True)
class VersionContract:
    """Defines the allowed version range for a target component."""
    minimum_version: str   # e.g., "1.0", "2.0.1"
    maximum_version: str   # e.g., "3.0", "1.x" (wildcard allowed)


class CompatibilityMatrix:
    """
    Single source of truth for cross‑phase version compatibility.

    Contracts are defined as (source, target) -> VersionContract.
    Use `assert_compatibility()` to enforce.

    Raises:
        Phase11GovernanceError: if the target version falls outside the allowed range.
    """

    _CONTRACTS: Dict[Tuple[str, str], VersionContract] = {
        # Phase 11 components
        ("Phase11", "Manifest"):      VersionContract("1.0", "2.0"),
        ("Phase11", "KnowledgeAPI"):  VersionContract("1.0", "1.x"),

        # Phase 12 → Phase 11
        ("Phase12", "Phase11"):       VersionContract("11.0", "11.x"),
    }

    @classmethod
    def assert_compatibility(
        cls,
        source: str,
        target: str,
        target_version: str,
    ) -> None:
        """
        Verify that `target_version` is compatible with `source`'s contract.

        If no contract is defined for (source, target), compatibility is assumed.
        """
        contract = cls._CONTRACTS.get((source, target))
        if contract is None:
            return  # No explicit restriction

        if not cls._is_version_compatible(
            target_version,
            contract.minimum_version,
            contract.maximum_version,
        ):
            raise GovernanceException(
                f"Compatibility violation: {source} requires {target} version "
                f"between {contract.minimum_version} and {contract.maximum_version}, "
                f"but found {target_version}."
            )

    # -------------------------------------------------------------------------
    # Version parsing and comparison helpers
    # -------------------------------------------------------------------------

    @classmethod
    def _is_version_compatible(
        cls,
        actual: str,
        minimum: str,
        maximum: str,
    ) -> bool:
        """Return True if actual >= minimum and actual <= maximum (semantic)."""
        # Normalise actual version (remove leading 'v' etc.)
        actual_clean = cls._clean_version(actual)
        min_clean = cls._clean_version(minimum)
        max_clean = cls._clean_version(maximum)

        # If maximum is a wildcard, expand it to the greatest allowed version
        if max_clean.endswith(".x"):
            max_base = max_clean[:-2]  # remove ".x"
            # e.g. "1.x" -> maximum 1.999.999 (practically infinite)
            max_expanded = cls._expand_wildcard(max_base)
            max_clean = max_expanded
        else:
            max_expanded = cls._parse_version(max_clean)

        min_parsed = cls._parse_version(min_clean)
        actual_parsed = cls._parse_version(actual_clean)

        if actual_parsed is None or min_parsed is None or max_expanded is None:
            # If any parse fails, treat as incompatible (strict)
            return False

        return min_parsed <= actual_parsed <= max_expanded

    @classmethod
    def _clean_version(cls, version: str) -> str:
        """Strip leading 'v' and whitespace."""
        return version.strip().lstrip("v")

    @classmethod
    def _parse_version(cls, version: str) -> Optional[Tuple[int, ...]]:
        """
        Parse a version string into a tuple of integers.
        Returns None if the string is malformed.
        Supports:
            - "1.2.3" -> (1,2,3)
            - "1.2"   -> (1,2)
        """
        if not version:
            return None
        # Split by '.' and try to convert each part
        parts = version.split(".")
        try:
            return tuple(int(p) for p in parts if p)
        except ValueError:
            return None

    @classmethod
    def _expand_wildcard(cls, base: str) -> Tuple[int, ...]:
        """
        Expand a base version (e.g., "1.2") to a nearly infinite tuple:
        (major, minor, 999999) for up to three levels.
        This ensures any patch version is allowed.
        """
        parsed = cls._parse_version(base)
        if parsed is None:
            # Fallback: treat as (0,)
            return (0,)
        # Extend to 3 parts with 999999
        while len(parsed) < 3:
            parsed = parsed + (999999,)
        return parsed