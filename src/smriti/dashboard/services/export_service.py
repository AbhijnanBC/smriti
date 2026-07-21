"""
export_service.py — Export orchestration for Phase 10.

Delegates format-specific work to ExportPipeline.
"""

from __future__ import annotations

from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class ExportService:
    """Retrieves raw export content from Phase 9 for ExportPipeline."""

    def __init__(self, api) -> None:
        self._api = api

    def get_raw_export(self, fmt: str = "json") -> Optional[str]:
        """Retrieve raw export content from Phase 9 API."""
        from smriti.core.models import ExportFormat
        try:
            fmt_enum = ExportFormat(fmt)
            resp = self._api.export(fmt=fmt_enum, include_reliability=True)
            return resp.data.get("content", "")
        except Exception as e:
            logger.error("get_raw_export failed", error=str(e))
            return None