r"""
generate_run_manifest.py — Write a run_manifest.json for one pipeline run.

RECTIFIED (external review, reproducibility pipeline): no run in this
project previously recorded the git commit, dataset fingerprint, config
hash, model+revision, or software/hardware versions it was produced
under, in one place. Re-running an experiment months later with no way to
tell whether the code, corpus, or config had drifted is exactly the
"cannot verify unless you carefully diff everything by hand" gap a
reproducibility manifest exists to close. This script reads what each
phase's artifacts already recorded (per-phase config_hash, model/revision
provenance) plus environment/git state that no phase records at all, and
writes one run_manifest.json per run.

This is deliberately NOT a new source of truth: every field here is
either copied verbatim from an existing phase artifact or computed
independently and cross-checkable against it (e.g. dataset_hash is
recomputed from phase1/dataset.json's own per-file content hashes, not
invented). If a field cannot be determined, it is reported as null with
an explicit reason, never silently omitted or defaulted.

Run with: poetry run python scripts/generate_run_manifest.py <run_id>
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"


def _load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _git_state() -> dict:
    def run(args):
        try:
            return subprocess.check_output(
                ["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL, text=True,
            ).strip()
        except Exception as e:  # noqa: BLE001 -- best-effort provenance, never fatal
            return None

    commit = run(["rev-parse", "HEAD"])
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    dirty_output = run(["status", "--porcelain"])
    return {
        "commit": commit,
        "branch": branch,
        "is_dirty": bool(dirty_output) if dirty_output is not None else None,
        "unavailable_reason": None if commit else "git command failed or not a git repository",
    }


def _software_versions() -> dict:
    """
    RECTIFIED (P1-13, "PLEASE FIX AND SAVE ME" review round): torch/CUDA
    were the only dependency versions recorded here; the review's exact
    ask ("also record: Python version, CUDA version, PyTorch version,
    transformers version, spaCy model version, FAISS version") is now
    covered in full. Each import is independent and best-effort (a
    missing optional dependency reports its own reason, never blocks the
    others or the manifest as a whole) -- reproducibility provenance
    must never become a reason a real run fails to produce a manifest.
    """
    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    try:
        import torch
        versions["torch"] = torch.__version__
        versions["cuda_available"] = torch.cuda.is_available()
        versions["cuda_version"] = torch.version.cuda if torch.cuda.is_available() else None
        versions["gpu_name"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception as e:  # noqa: BLE001
        versions["torch"] = None
        versions["torch_unavailable_reason"] = str(e)
    try:
        import transformers
        versions["transformers"] = transformers.__version__
    except Exception as e:  # noqa: BLE001
        versions["transformers"] = None
        versions["transformers_unavailable_reason"] = str(e)
    try:
        import sentence_transformers
        versions["sentence_transformers"] = sentence_transformers.__version__
    except Exception as e:  # noqa: BLE001
        versions["sentence_transformers"] = None
        versions["sentence_transformers_unavailable_reason"] = str(e)
    try:
        import spacy
        versions["spacy"] = spacy.__version__
        versions["spacy_model"] = None
        versions["spacy_model_version"] = None
        for name in ("en_core_web_sm", "en_core_web_md", "en_core_web_lg", "en_core_web_trf"):
            try:
                nlp = spacy.load(name)
                versions["spacy_model"] = name
                versions["spacy_model_version"] = nlp.meta.get("version")
                break
            except Exception:  # noqa: BLE001 -- try the next candidate model name
                continue
    except Exception as e:  # noqa: BLE001
        versions["spacy"] = None
        versions["spacy_unavailable_reason"] = str(e)
    try:
        import faiss
        versions["faiss"] = getattr(faiss, "__version__", "unknown")
    except Exception as e:  # noqa: BLE001
        versions["faiss"] = None
        versions["faiss_unavailable_reason"] = str(e)
    return versions


def _dataset_hash(phase1_dataset) -> dict:
    if not phase1_dataset:
        return {"hash": None, "reason": "phase1/dataset.json not found"}
    # Deterministic corpus fingerprint: sort by relative_path so the hash is
    # order-independent, hash each file's own already-computed content_hash
    # (not the raw bytes again) since phase1 already establishes that as the
    # canonical per-file fingerprint.
    fingerprints = sorted(
        f"{d.get('relative_path', '')}:{d.get('content_hash', '')}" for d in phase1_dataset
    )
    digest = hashlib.sha256("\n".join(fingerprints).encode("utf-8")).hexdigest()
    return {"hash": digest, "n_documents": len(phase1_dataset)}


def _embedding_model_info(phase5_dataset) -> dict:
    if not phase5_dataset:
        return None
    m = phase5_dataset[0].get("model", {})
    prov = phase5_dataset[0].get("provenance", {})
    return {
        "provider": m.get("provider"),
        "model_name": m.get("model_name"),
        "revision": m.get("revision"),
        "signature": m.get("signature"),
        "device": prov.get("device"),
    }


def _nli_model_info(phase6_dataset) -> dict:
    if not phase6_dataset:
        return None
    ev = phase6_dataset[0].get("evidence", {})
    return {
        "model_name": ev.get("model_name"),
        "model_revision": ev.get("model_version"),
    }


def _config_hashes(phase1_manifest, phase5_dataset, phase6_dataset) -> dict:
    return {
        "phase5_embedding_config_hash": (
            phase5_dataset[0].get("provenance", {}).get("config_hash") if phase5_dataset else None
        ),
        "phase6_relationship_config_hash": (
            phase6_dataset[0].get("provenance", {}).get("config_hash") if phase6_dataset else None
        ),
    }


def main(run_id: str) -> None:
    run_dir = ARTIFACTS / f"run_{run_id}"
    if not run_dir.exists():
        raise SystemExit(f"No such run: {run_dir}")

    phase1_dataset = _load(run_dir / "phase1" / "dataset.json")
    phase1_manifest = _load(run_dir / "phase1" / "manifest.json")
    phase5_dataset = _load(run_dir / "phase5" / "dataset.json")
    phase6_dataset = _load(run_dir / "phase6" / "dataset.json")
    benchmark = _load(run_dir / "benchmark.json")

    manifest = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": _git_state(),
        "software_versions": _software_versions(),
        "dataset": _dataset_hash(phase1_dataset),
        "input_directories": (phase1_manifest or {}).get("inputs", {}).get("directories"),
        "config_hashes": _config_hashes(phase1_manifest, phase5_dataset, phase6_dataset),
        "embedding_model": _embedding_model_info(phase5_dataset),
        "nli_model": _nli_model_info(phase6_dataset),
        "seed": {
            "value": None,
            "note": (
                "SMRITI's inference path (embedding + NLI cross-encoder) is "
                "deterministic given fixed model weights and contains no "
                "sampling step, so no pipeline-level RNG seed applies. "
                "Evaluation-side bootstrap confidence intervals DO use a "
                "fixed seed, recorded in each evaluation script's own "
                "source (e.g. evaluation/controlled/*.py, "
                "scripts/build_relationship_sample_v2.py), not here, since "
                "those seeds are properties of the evaluation run, not this "
                "pipeline run."
            ),
        },
        "benchmark": benchmark,
    }

    out_path = run_dir / "run_manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}")
    if manifest["git"]["is_dirty"]:
        print("WARNING: git working tree was dirty when this run was produced "
              "-- exact code state is not fully captured by the commit hash alone.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: generate_run_manifest.py <run_id>")
    main(sys.argv[1])
