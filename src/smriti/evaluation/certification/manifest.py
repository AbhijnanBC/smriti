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

RECTIFIED: hardware_description and software_versions are now measured
from the actual running machine/environment (platform, psutil, torch)
instead of a hardcoded "Windows 11" placeholder string, so the manifest
is a genuine reproducibility record rather than a fabricated constant.
"""

from __future__ import annotations

import hashlib
import platform
import sys
from datetime import UTC, datetime

from smriti.core.models import EvaluationManifest, ExperimentDesign

# Packages whose installed version is recorded verbatim (never hardcoded —
# always read from the package's own installed distribution metadata).
_TRACKED_PACKAGES = (
    "structlog",
    "spacy",
    "sentence_transformers",
    "torch",
    "networkx",
    "numpy",
)

# spaCy trained pipelines (e.g. en_core_web_sm) install as their own
# versioned distribution, separate from the spacy library itself.
_DEFAULT_SPACY_MODEL = "en_core_web_sm"


def _software_versions() -> dict[str, str]:
    """Real installed package versions, via importlib.metadata — never hardcoded."""
    import importlib.metadata

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    for pkg in _TRACKED_PACKAGES:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except Exception:
            versions[pkg] = "unknown"

    try:
        from smriti.core.config import get_config

        spacy_model = get_config().get("extraction", {}).get("spacy_model", _DEFAULT_SPACY_MODEL)
    except Exception:
        spacy_model = _DEFAULT_SPACY_MODEL
    try:
        versions[f"spacy_model:{spacy_model}"] = importlib.metadata.version(spacy_model)
    except Exception:
        versions[f"spacy_model:{spacy_model}"] = "unknown"

    return versions


def _hardware_description() -> str:
    """
    Real OS/CPU/RAM/GPU description, detected at run time.

    SMRITI runs CPU-only in normal operation, so no GPU info is fabricated
    when none is present — torch.cuda.is_available() is checked directly
    and reported honestly as "cpu" when it is False.
    """
    parts = [
        f"{platform.system()} {platform.release()}",
        f"Python {platform.python_version()}",
        f"CPU: {platform.processor() or platform.machine() or 'unknown'}",
    ]

    try:
        import psutil

        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        parts.append(f"RAM: {total_ram_gb:.1f}GB")
    except Exception:
        parts.append("RAM: unknown")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            parts.append(f"GPU: {gpu_name} (CUDA {torch.version.cuda})")
        else:
            parts.append("GPU: none (cpu-only)")
    except Exception:
        parts.append("GPU: unknown")

    return " | ".join(parts)


def build_evaluation_manifest(
    run_id: str,
    experiments: list[ExperimentDesign],
    policy_version: str,
) -> EvaluationManifest:
    """Build an EvaluationManifest for one Phase 12 run."""
    manifest_id = hashlib.sha256(
        f"{run_id}:{datetime.now(tz=UTC).isoformat()}".encode()
    ).hexdigest()[:12]

    experiment_ids = tuple(e.experiment_id for e in experiments)
    ground_truth_versions = {e.experiment_id: e.ground_truth_version for e in experiments}
    random_seeds = {e.experiment_id: e.random_seed for e in experiments}

    # Collect all acceptance criteria
    acceptance_criteria: dict[str, float] = {}
    for e in experiments:
        for metric, threshold in e.acceptance_criteria.items():
            acceptance_criteria[f"{e.experiment_id}.{metric}"] = threshold

    return EvaluationManifest(
        manifest_id=manifest_id,
        run_id=run_id,
        experiment_ids=experiment_ids,
        ground_truth_versions=ground_truth_versions,
        policy_version=policy_version,
        random_seeds=random_seeds,
        metrics_evaluated=tuple(acceptance_criteria.keys()),
        acceptance_criteria=acceptance_criteria,
        software_versions=_software_versions(),
        hardware_description=_hardware_description(),
        created_at=datetime.now(tz=UTC).isoformat(),
    )
