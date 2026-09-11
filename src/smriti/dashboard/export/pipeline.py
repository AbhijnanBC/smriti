"""
pipeline.py — ExportPipeline for Phase 10.

Instead of ServiceClient.export_data() returning a raw string,
ExportPipeline orchestrates typed exporters.

Architecture:
    ExportCommand
        │
        ▼
    ExportPipeline.export(fmt)
        │
        ├── JSONExporter
        ├── CSVExporter
        └── (future: MarkdownExporter, ReportExporter)

Rules:
    ✅ Each exporter handles exactly one format
    ✅ ExportPipeline validates policy before exporting
    ✅ Returns (content: str, mime_type: str, filename: str)
    ❌ Exporters never access Phase 9 directly
    ❌ Exporters never call st.*
"""

from __future__ import annotations

import structlog
from smriti.dashboard.export.csv_exporter import CSVExporter
from smriti.dashboard.export.json_exporter import JSONExporter
from smriti.dashboard.export.models import ExportResult
from smriti.dashboard.policies.policies import PolicyEngine
from smriti.exceptions import ExportPipelineError

logger = structlog.get_logger(__name__)


class ExportPipeline:
    """
    Orchestrates the full export flow.
    One instance per session — held in st.session_state.
    """

    def __init__(self, service_client, policy_engine: PolicyEngine, run_id: str) -> None:
        self._client = service_client
        self._policy = policy_engine
        self._run_id = run_id
        self._json_exporter = JSONExporter(service_client)
        self._csv_exporter = CSVExporter(service_client)

    def export(self, fmt: str) -> ExportResult | None:
        """
        Run the export pipeline for a given format.
        Returns ExportResult on success, None on failure.
        """
        # Policy check first
        allowed, reason = self._policy.validate_export(fmt)
        if not allowed:
            logger.warning("export blocked by policy", fmt=fmt, reason=reason)
            raise ExportPipelineError(f"Export not allowed: {reason}")

        try:
            if fmt == "json":
                return self._json_exporter.export(self._run_id)
            elif fmt == "csv":
                return self._csv_exporter.export(self._run_id)
            else:
                raise ExportPipelineError(f"Unknown export format: {fmt}")
        except ExportPipelineError:
            raise
        except Exception as e:
            logger.error("export pipeline failed", fmt=fmt, error=str(e))
            raise ExportPipelineError(f"Export failed: {e}") from e
