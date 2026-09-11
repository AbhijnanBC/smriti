"""
Full end-to-end pipeline smoke test.

Runs all twelve phases against a small, isolated vault and verifies the
run completes successfully and produces the artifacts a real run depends
on: a RuntimeManifest (Phase 11) and a CertificationReport (Phase 12) at
at least the ARCHITECTURALLY_VERIFIED level.

Previously this file was a placeholder (`assert True`) — no test exercised
the full pipeline end-to-end, so a regression that broke phase-to-phase
wiring (as happened during this session with a Phase 7 partitioning bug
and a Phase 6/7 resume-state bug in PipelineRunner) could only be caught by
manually running the CLI against a real vault.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from smriti.core.models import CertificationLevel

DOCS = {
    "topic_a.md": (
        "# Topic A\n\n"
        "The mitochondria is the powerhouse of the cell. "
        "It produces ATP through oxidative phosphorylation.\n"
    ),
    "topic_b.md": (
        "# Topic B\n\n"
        "Water boils at 100 degrees Celsius at sea level. "
        "Ice melts at 0 degrees Celsius under the same conditions.\n"
    ),
    "topic_c.md": (
        "# Topic C\n\n"
        "Python is a dynamically typed programming language. "
        "It supports object-oriented and functional programming styles.\n"
    ),
}


@pytest.fixture
def isolated_vault(tmp_path: Path) -> Path:
    vault_dir = tmp_path / "smoke_vault"
    vault_dir.mkdir()
    for name, content in DOCS.items():
        (vault_dir / name).write_text(content, encoding="utf-8")
    return vault_dir


@pytest.fixture
def isolated_pipeline_state(tmp_path, monkeypatch):
    """
    StateManager's default state file lives under the shared ARTIFACTS_DIR
    (a single file, not keyed by run_id — see PipelineRunner.run's resume
    logic). Running this smoke test against the real state file would let
    it interfere with — or be interfered with by — any other pipeline run
    happening concurrently (manual CLI use, other test sessions). Patch
    PipelineRunner's StateManager construction to use a tmp-path-scoped
    file instead, so this test never touches shared repo state.
    """
    from smriti.core.state import StateManager

    state_path = tmp_path / "pipeline_state.json"
    monkeypatch.setattr(
        "smriti.pipeline.runner.StateManager",
        lambda: StateManager(state_file=state_path),
    )


@pytest.mark.integration
def test_full_pipeline_smoke(isolated_vault, isolated_pipeline_state):
    """Phases 1-12 must run to completion on a small real vault and certify."""
    from smriti.core.logger import setup_logging
    from smriti.pipeline.runner import PipelineRunner

    setup_logging()

    runner = PipelineRunner(input_dirs=[isolated_vault])
    success = runner.run(start_from=1, stop_at=12)

    assert success, "Full 12-phase pipeline run must succeed on a valid small vault"

    run_dir = Path("artifacts") / f"run_{runner.run_id}"

    # Phase 11: RuntimeManifest must have been written (infrastructure/provenance.py
    # writes it to artifacts/run_<id>/phase11/runtime_manifest.json).
    runtime_manifest_path = run_dir / "phase11" / "runtime_manifest.json"
    assert runtime_manifest_path.exists(), "Phase 11 must write runtime_manifest.json"

    # Phase 12: CertificationReport must exist and clear a minimum bar.
    cert_report_path = run_dir / "phase12" / "certification_report.json"
    assert cert_report_path.exists(), "Phase 12 must write a certification_report.json"

    import json

    report = json.loads(cert_report_path.read_text(encoding="utf-8"))
    level = report["certification"]["level"]
    assert level >= CertificationLevel.ARCHITECTURALLY_VERIFIED, (
        f"Expected at least ARCHITECTURALLY_VERIFIED ({CertificationLevel.ARCHITECTURALLY_VERIFIED}), "
        f"got level {level}"
    )

    # Every phase's own manifest must report success.
    for phase in range(1, 10):
        phase_manifest = run_dir / f"phase{phase}" / "manifest.json"
        assert phase_manifest.exists(), f"Phase {phase} manifest missing"
        data = json.loads(phase_manifest.read_text(encoding="utf-8"))
        assert data["status"] == "success", f"Phase {phase} did not report success: {data}"
