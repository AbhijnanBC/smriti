"""
manifest.py — EvaluationManifest for Phase 12 (P2-1).

RECTIFIED (P2-1): Evaluation-specific reproducibility manifest.

Phase 11 has RuntimeManifest (infrastructure provenance).
Phase 12 adds EvaluationManifest (evaluation provenance):
    - Which experiments were run
    - Which ground truth versions were used
    - Which policy version was active
    - Random seeds per experiment
    - Software and hardware configuration
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from typing import Dict, List
from smriti.core.models import EvaluationManifest, ExperimentDesign


def build_evaluation_manifest(
    run_id: str,
    experiments: List[ExperimentDesign],
    policy_version: str,
) -> EvaluationManifest:
    """Build an EvaluationManifest for one Phase 12 run."""
    import hashlib, uuid

    manifest_id = hashlib.sha256(
        f"{run_id}:{datetime.now(tz=timezone.utc).isoformat()}".encode()
    ).hexdigest()[:12]

    experiment_ids = tuple(e.experiment_id for e in experiments)
    ground_truth_versions = {e.experiment_id: e.ground_truth_version for e in experiments}
    random_seeds = {e.experiment_id: e.random_seed for e in experiments}

    # Collect all acceptance criteria
    acceptance_criteria: Dict[str, float] = {}
    for e in experiments:
        for metric, threshold in e.acceptance_criteria.items():
            acceptance_criteria[f"{e.experiment_id}.{metric}"] = threshold

    # Software versions
    software_versions: Dict[str, str] = {"python": sys.version.split()[0]}
    for pkg in ["structlog", "spacy", "sentence_transformers", "networkx", "numpy"]:
        try:
            import importlib.metadata
            software_versions[pkg] = importlib.metadata.version(pkg)
        except Exception:
            software_versions[pkg] = "unknown"

    return EvaluationManifest(
        manifest_id=manifest_id,
        run_id=run_id,
        experiment_ids=experiment_ids,
        ground_truth_versions=ground_truth_versions,
        policy_version=policy_version,
        random_seeds=random_seeds,
        metrics_evaluated=tuple(acceptance_criteria.keys()),
        acceptance_criteria=acceptance_criteria,
        software_versions=software_versions,
        hardware_description=f"Windows 11 / Python {sys.version.split()[0]} (platform: {sys.platform})",
        created_at=datetime.now(tz=timezone.utc).isoformat(),
    )