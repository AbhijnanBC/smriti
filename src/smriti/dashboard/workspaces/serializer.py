"""
serializer.py — WorkspaceSerializer for Phase 10.

Extracted from EpistemicStateManager. Serialization concerns
belong here, not in the state domain object.
"""

from __future__ import annotations

import json
from typing import Any

from smriti.exceptions import WorkspaceSerializationError


class WorkspaceSerializer:
    """
    Serializes and deserializes EpistemicStateManager snapshots.
    Decoupled from EpistemicStateManager — pure I/O concern.
    """

    @staticmethod
    def to_json(snapshot: dict[str, Any]) -> str:
        """Serialize a state snapshot to JSON string."""
        try:
            return json.dumps(snapshot, indent=2, default=str)
        except Exception as e:
            raise WorkspaceSerializationError(f"Serialization failed: {e}") from e

    @staticmethod
    def from_json(json_str: str) -> dict[str, Any]:
        """Deserialize a JSON string to a state snapshot dict."""
        try:
            return json.loads(json_str)
        except Exception as e:
            raise WorkspaceSerializationError(f"Deserialization failed: {e}") from e

    @staticmethod
    def validate_snapshot(snapshot: dict[str, Any]) -> bool:
        """Check that a snapshot has the required keys for restoration."""
        required = {"workspace_type", "active_lens", "run_id"}
        return required.issubset(snapshot.keys())
