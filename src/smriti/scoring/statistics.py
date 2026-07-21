"""
statistics.py — Phase 8 execution telemetry. Observes. Never influences.

RECTIFIED (Phase 8.4): Now returns Phase8Telemetry with cleanly segregated
ExecutionStats (timing and infrastructure) and KnowledgeStats (knowledge outcomes).
Calibration histogram is tracked per claim for better diagnostics.

RECTIFIED: finalize() now includes high_reliability_count and low_reliability_count
in KnowledgeStats as required by the Phase8Telemetry model.
"""

from __future__ import annotations

import time
from typing import Dict
from smriti.core.models import (
    Phase8Telemetry,
    ExecutionStats,
    KnowledgeStats,
    CalibrationLabel,
)


class Phase8StatsCollector:
    """Mutable accumulator for Phase 8 statistics."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._signal_start: float | None = None
        self._signal_end: float | None = None
        self._fusion_start: float | None = None
        self._fusion_end: float | None = None

        # Knowledge metrics
        self._scored: int = 0
        self._ri_sum: float = 0.0
        self._unc_sum: float = 0.0
        self._high_ri: int = 0
        self._low_ri: int = 0
        self._high_unc: int = 0
        self._calibration_histogram: Dict[str, int] = {
            label.value: 0 for label in CalibrationLabel
        }

        # Execution metadata
        self._policy_version: str = ""
        self._policy_profile: str = ""
        self._registered_signals: int = 0

    def record_signal_start(self) -> None:
        self._signal_start = time.monotonic()

    def record_signal_end(self) -> None:
        self._signal_end = time.monotonic()

    def record_fusion_start(self) -> None:
        self._fusion_start = time.monotonic()

    def record_fusion_end(self) -> None:
        self._fusion_end = time.monotonic()

    def record_scored(
        self,
        ri: float,
        unc: float,
        calibration_label: CalibrationLabel,
    ) -> None:
        """
        Record a scored claim's reliability index, uncertainty, and calibration label.
        """
        self._scored += 1
        self._ri_sum += ri
        self._unc_sum += unc

        if ri >= 65:
            self._high_ri += 1
        if ri < 45:
            self._low_ri += 1
        if unc >= 50:
            self._high_unc += 1

        self._calibration_histogram[calibration_label.value] = (
            self._calibration_histogram.get(calibration_label.value, 0) + 1
        )

    def set_policy_version(self, version: str, profile: str = "") -> None:
        self._policy_version = version
        self._policy_profile = profile

    def set_registered_signals(self, count: int) -> None:
        self._registered_signals = count

    def finalize(self) -> Phase8Telemetry:
        """Produce the complete Phase 8 telemetry report."""
        total = time.monotonic() - self._start

        n = max(1, self._scored)

        signal_secs = (
            (self._signal_end - self._signal_start)
            if self._signal_start and self._signal_end
            else 0.0
        )
        fusion_secs = (
            (self._fusion_end - self._fusion_start)
            if self._fusion_start and self._fusion_end
            else 0.0
        )

        execution = ExecutionStats(
            total_runtime_seconds=round(total, 4),
            signal_extraction_seconds=round(signal_secs, 4),
            fusion_seconds=round(fusion_secs, 4),
            registered_signal_count=self._registered_signals,
        )

        knowledge = KnowledgeStats(
            total_claims_scored=self._scored,
            avg_reliability_index=round(self._ri_sum / n, 2),
            avg_uncertainty_score=round(self._unc_sum / n, 2),
            calibration_histogram=dict(self._calibration_histogram),
            high_reliability_count=self._high_ri,   # RECTIFICATION: added
            low_reliability_count=self._low_ri,     # RECTIFICATION: added
        )

        return Phase8Telemetry(
            policy_version=self._policy_version,
            policy_profile=self._policy_profile,
            execution=execution,
            knowledge=knowledge,
        )