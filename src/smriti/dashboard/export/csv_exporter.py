"""
csv_exporter.py — CSVExporter for Phase 10.
"""

from __future__ import annotations

from smriti.dashboard.export.models import ExportResult
from smriti.exceptions import ExportPipelineError


class CSVExporter:
    """Exports knowledge base as CSV via ServiceClient."""

    def __init__(self, client) -> None:
        self._client = client

    def export(self, run_id: str) -> ExportResult:
        content = self._client.export_data("csv")
        if content is None:
            raise ExportPipelineError("CSV export returned no content.")
        return ExportResult(
            content=content,
            mime_type="text/csv",
            filename=f"smriti_knowledge_{run_id}.csv",
            format="csv",
            byte_size=len(content.encode("utf-8")),
        )
