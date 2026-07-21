"""
schema_registry.py — SchemaRegistry for DTO versioning.

RECTIFIED (P1-3): DTOs no longer hardcode schema_version.
The SchemaRegistry provides the current version for each DTO type.
When schema evolves (e.g., 9.0 → 9.1), only this file changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SchemaVersion:
    """Version metadata for one DTO type."""
    major: int
    minor: int
    description: str

    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}"


class SchemaRegistry:
    """
    Central registry for DTO schema versions.
    Single source of truth for all versioning decisions.
    """

    _VERSIONS: Dict[str, SchemaVersion] = {
        "ClaimDTO":        SchemaVersion(9, 0, "Phase 9.0 claim projection schema"),
        "ExplanationDTO":  SchemaVersion(9, 0, "Phase 9.0 explainability schema"),
        "StatisticsDTO":   SchemaVersion(9, 0, "Phase 9.0 statistics schema"),
        "GraphDTO":        SchemaVersion(9, 0, "Phase 9.0 traversal result schema"),
        "ResponseMeta":    SchemaVersion(9, 0, "Phase 9.0 response metadata schema"),
    }

    @classmethod
    def get_version(cls, dto_type: str) -> SchemaVersion:
        """Get schema version for a DTO type."""
        return cls._VERSIONS.get(dto_type, SchemaVersion(9, 0, "unknown"))

    @classmethod
    def get_version_string(cls, dto_type: str) -> str:
        return cls.get_version(dto_type).version_string

    @classmethod
    def all_versions(cls) -> Dict[str, str]:
        return {k: v.version_string for k, v in cls._VERSIONS.items()}


# Singleton
schema_registry = SchemaRegistry()