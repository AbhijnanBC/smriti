"""
json_exporter.py — JSONExporter for Phase 10.
"""

from __future__ import annotations

from smriti.dashboard.export.pipeline import ExportResult
from smriti.exceptions import ExportPipelineError


class JSONExporter:
    """Exports knowledge base as JSON via ServiceClient."""

    def __init__(self, client) -> None:
        self._client = client

    def export(self, run_id: str) -> ExportResult:
        content = self._client.export_data("json")
        if content is None:
            raise ExportPipelineError("JSON export returned no content.")
        return ExportResult(
            content=content,
            mime_type="application/json",
            filename=f"smriti_knowledge_{run_id}.json",
            format="json",
            byte_size=len(content.encode("utf-8")),
        )