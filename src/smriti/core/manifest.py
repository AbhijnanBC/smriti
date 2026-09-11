"""
Manifest system for tracking phase execution.
Every phase writes a manifest.json under its own run directory.

Directory layout:
  artifacts/
    run_20240715_143022/
      phase1/manifest.json
      phase2/manifest.json
      ...
    run_20240715_160500/
      phase1/manifest.json
      ...
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from smriti.constants import MANIFEST_SCHEMA_VERSION
from smriti.core.models import ManifestEntry
from smriti.core.paths import ARTIFACTS_DIR

logger = structlog.get_logger(__name__)


class ManifestManager:
    """Manages per-run, per-phase manifests."""

    def __init__(self, run_id: str, artifacts_dir: Path = ARTIFACTS_DIR):
        self.run_id = run_id
        self.artifacts_dir = Path(artifacts_dir)
        self.run_dir = self.artifacts_dir / f"run_{run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def start_phase(self, phase: int) -> float:
        """
        Mark phase as started. Returns wall-clock start time.
        Call this immediately before phase logic runs.
        """
        start_time = time.time()
        phase_dir = self.run_dir / f"phase{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        logger.info("phase started", run_id=self.run_id, phase=phase)
        return start_time

    def end_phase(
        self,
        phase: int,
        start_time: float,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        status: str = "success",
        error: str | None = None,
    ) -> Path:
        """
        Record phase completion and write manifest.json.
        Returns: path to the manifest file.
        """
        duration = time.time() - start_time

        entry = ManifestEntry(
            run_id=self.run_id,
            phase=phase,
            timestamp=datetime.now(),
            duration_seconds=duration,
            inputs=inputs,
            outputs=outputs,
            status=status,
            schema_version=MANIFEST_SCHEMA_VERSION,
            error=error,
        )

        phase_dir = self.run_dir / f"phase{phase}"
        manifest_path = phase_dir / "manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": entry.schema_version,
                    "run_id": entry.run_id,
                    "phase": entry.phase,
                    "timestamp": entry.timestamp.isoformat(),
                    "duration_seconds": round(entry.duration_seconds, 4),
                    "inputs": entry.inputs,
                    "outputs": entry.outputs,
                    "status": entry.status,
                    "error": entry.error,
                },
                f,
                indent=2,
            )

        logger.info(
            "phase completed",
            run_id=self.run_id,
            phase=phase,
            status=status,
            duration_seconds=f"{duration:.2f}",
        )
        return manifest_path

    def list_completed_phases(self) -> list:
        """Return list of phase numbers that have a manifest in this run."""
        completed = []
        for phase_dir in sorted(self.run_dir.glob("phase*")):
            if (phase_dir / "manifest.json").exists():
                completed.append(int(phase_dir.name.replace("phase", "")))
        return completed
