"""export_service.py — Knowledge export in JSON, CSV, and GraphML formats.

RECTIFIED (Method naming): execute_export renamed to execute for
consistent service interface.
"""

from __future__ import annotations

import csv
import dataclasses
import io
import json
import time
from typing import Any

import structlog
from smriti.api.domain.predicates import SortSpec
from smriti.api.domain.requests import ExportRequest
from smriti.api.domain.responses import KnowledgeResponse, make_response_meta
from smriti.api.store.read_store import ReadStore
from smriti.core.models import ExecutionContext, ExportFormat
from smriti.exceptions import ExportError

logger = structlog.get_logger(__name__)


class ExportService:
    """Exports the full knowledge base to JSON, CSV, or GraphML."""

    def __init__(self, store: ReadStore) -> None:
        self._store = store

    # ── RECTIFIED: Renamed from execute_export to execute ──────────────────
    def execute(
        self, request: ExportRequest, plan: Any, ctx: ExecutionContext
    ) -> KnowledgeResponse:
        """
        Execute an export request.

        Args:
            request: ExportRequest with format and options.
            plan:    PhysicalPlan for this request.
            ctx:     ExecutionContext.

        Returns:
            KnowledgeResponse containing the exported content.

        Raises:
            ExportError: If the export format is unsupported or fails.
        """
        t0 = time.monotonic()

        try:
            if request.export_format == ExportFormat.JSON:
                content = self._export_json(request)
            elif request.export_format == ExportFormat.CSV:
                content = self._export_csv(request)
            elif request.export_format == ExportFormat.GRAPHML:
                content = self._export_graphml(request)
            else:
                raise ExportError(f"Unsupported format: {request.export_format}")
        except Exception as e:
            raise ExportError(f"Export failed: {e}") from e

        ctx = dataclasses.replace(
            ctx,
            execution_ms=round((time.monotonic() - t0) * 1000, 2),
            rows_returned=1,
        )
        result = {
            "format": request.export_format.value,
            "content": content,
            "byte_size": len(content.encode("utf-8")),
        }
        return KnowledgeResponse(data=result, meta=make_response_meta(ctx))

    def _collect_records(self, request: ExportRequest) -> list[dict]:
        """Use ReadStore.stream() — pure primitive iteration."""
        predicates = list(request.predicates)
        if not predicates:
            return list(self._store.stream())
        # Apply predicates via scan for filtered exports
        from smriti.api.domain.predicates import Pagination

        all_records = []
        offset = 0
        page_size = 1000
        while True:
            page, total = self._store.scan(
                predicates=predicates,
                sort=SortSpec("claim_id"),
                pagination=Pagination(limit=page_size, offset=offset),
            )
            if not page:
                break
            all_records.extend(page)
            offset += page_size
            if offset >= total:
                break
        return all_records

    def _export_json(self, request: ExportRequest) -> str:
        records = self._collect_records(request)
        result: dict[str, Any] = {"run_id": request.run_id, "claims": []}
        for rec in records:
            claim_data = {
                "claim_id": rec["claim_id"],
                "claim_text": rec["claim_text"],
                "context": rec["context"],
                "document_id": rec["document_id"],
                "partition_id": rec["partition_id"],
                "semantic_role": rec["semantic_role"],
            }
            if request.include_reliability:
                claim_data.update(
                    {
                        "reliability_index": rec["reliability_index"],
                        "calibration_label": rec["calibration_label"],
                        "uncertainty_score": rec["uncertainty_score"],
                    }
                )
            result["claims"].append(claim_data)
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _export_csv(self, request: ExportRequest) -> str:
        records = self._collect_records(request)
        output = io.StringIO()
        headers = [
            "claim_id",
            "claim_text",
            "context",
            "document_id",
            "partition_id",
            "semantic_role",
        ]
        if request.include_reliability:
            headers += ["reliability_index", "calibration_label", "uncertainty_score"]
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in headers})
        return output.getvalue()

    def _export_graphml(self, request: ExportRequest) -> str:
        records = self._collect_records(request)
        edge_records = self._store.get_edge_records()
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/graphml">',
            '  <graph id="smriti_knowledge" edgedefault="directed">',
        ]
        for rec in records:
            ri = (
                f' reliability="{rec.get("reliability_index", 0)}"'
                if request.include_reliability
                else ""
            )
            text_esc = (
                rec["claim_text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            lines.append(f'    <node id="{rec["claim_id"]}"' f' label="{text_esc[:80]}"{ri}/>')
        if request.include_graph_structure:
            for er in edge_records:
                lines.append(
                    f'    <edge source="{er["source_claim_id"]}"'
                    f' target="{er["target_claim_id"]}"'
                    f' type="{er["relationship_type"]}"/>'
                )
        lines += ["  </graph>", "</graphml>"]
        return "\n".join(lines)
