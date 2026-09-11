r"""
generate_release_manifest.py — write evaluation/release_manifest_v1.json,
the single provenance root for every number this paper reports (P1-M,
"FINAL REVIEW" round).

The problem this closes: this project has produced many run IDs
(20260910_..., 20260911_...) across many evaluation categories
(controlled-v2, closed-world, FEVER, SciFact, SciFact-Open, calibration,
risk-coverage, partitioning, ablation, reconstruction, ...), each
self-contained and independently reproducible, but with no single
artifact tying "this release of the paper" to "exactly these run IDs,
this git commit, this dependency lockfile, these model revisions." A
reviewer currently has to reconstruct that mapping by reading each
evaluation script's own docstring. This script does that reconstruction
once, from real artifacts already on disk (every field below is read
from an existing results.json/run_manifest.json, or computed
independently and cross-checkable against one -- never invented), and
writes the answer to one file.

Exact schema per the review (section 20):
    release_id, git_commit, git_dirty, python, dependency_lock_hash,
    datasets{}, models{embedding,nli}, runs{}, paper_generation{}

Run with: poetry run python scripts/generate_release_manifest.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import generate_run_manifest as grm  # noqa: E402 -- reuse git/software-version helpers

EVAL = ROOT / "evaluation"
OUT_PATH = EVAL / "release_manifest_v1.json"


def _load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> dict:
    if not path or not path.exists():
        return {"hash": None, "path": str(path) if path else None, "reason": "file not found"}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"hash": digest, "path": str(path.relative_to(ROOT))}


def _run_id_of(results_path: Path, explicit_source: str = None) -> dict:
    """
    Most evaluation results.json files carry their own run_id (the
    pipeline run they were scored against, either top-level or under
    "_meta"); a few (FEVER, SciFact, SciFact-Open, the naive-extraction
    baselines, claim-validity) are derived from an external dataset, a
    fixed reference-corpus run referenced only in the evaluation
    script's own source code, or no pipeline run at all, and report
    that via `explicit_source` rather than a fabricated run_id.
    """
    data = _load(results_path)
    if data is None:
        return {"run_id": None, "source": explicit_source, "results_path": None,
                "reason": f"{results_path} not found"}
    run_id = None
    source = explicit_source
    if isinstance(data, dict):
        run_id = data.get("run_id") or (data.get("_meta") or {}).get("run_id")
        source = data.get("source") or explicit_source
    return {
        "run_id": run_id,
        "source": source,
        "results_path": str(results_path.relative_to(ROOT)),
    }


def main() -> None:
    git = grm._git_state()
    versions = grm._software_versions()
    lock_hash = _file_hash(ROOT / "poetry.lock")

    # ── datasets: content-hash the actual gold/sample files each
    #    evaluation category scores against, not a run_id (several
    #    categories share the SAME underlying dataset across multiple
    #    runs; the dataset's own content hash is the honest fingerprint).
    datasets = {
        "reference": _file_hash(ROOT / "artifacts" / "run_20260911_125340" / "phase4" / "dataset.json"),
        "controlled_v2": _file_hash(EVAL / "controlled" / "v2" / "construction_manifest.json"),
        "closed_world_v1": _file_hash(EVAL / "closed_world" / "v1" / "construction_manifest.json"),
        "claim_validity_v1": _file_hash(EVAL / "claim_validity" / "v1" / "benchmark.json"),
        "fever": _file_hash(EVAL / "fever" / "v1" / "sample.json"),
        "scifact": _file_hash(EVAL / "scifact" / "v1" / "sample.json"),
        "scifact_open": _file_hash(EVAL / "scifact_open" / "v1" / "sample.json"),
    }

    # ── models: read from a real run_manifest.json (embedding+NLI model
    #    name/revision are constant across runs on this branch; reading
    #    from one real run rather than re-deriving is the same
    #    cross-checkable-not-invented rule generate_run_manifest.py uses).
    reference_run_manifest = _load(ROOT / "artifacts" / "run_20260911_081039" / "run_manifest.json")
    models = {
        "embedding": (reference_run_manifest or {}).get("embedding_model"),
        "nli": (reference_run_manifest or {}).get("nli_model"),
        "source_run_manifest": "artifacts/run_20260911_081039/run_manifest.json" if reference_run_manifest else None,
    }

    # ── runs: every evaluation category's actual run_id (or external
    #    dataset source, where there is no fresh pipeline run) -----------
    runs = {
        "controlled_v2": _run_id_of(EVAL / "controlled" / "v2" / "results.json"),
        "closed_world_v1": _run_id_of(EVAL / "closed_world" / "v1" / "results.json"),
        "reference_baselines": _run_id_of(
            EVAL / "baselines" / "run_summary.json",
            explicit_source="artifacts/run_20260911_125340/phase4/dataset.json "
                             "(hardcoded PHASE4_DATASET path in scripts/run_baselines.py, "
                             "no run_id field in its own output)",
        ),
        "claim_validity_v1": _run_id_of(
            EVAL / "claim_validity" / "v1" / "results.json",
            explicit_source="pure construction-defined benchmark scored directly against "
                             "the AssertionClassifier -- no pipeline run applies",
        ),
        "fever_v1": _run_id_of(EVAL / "fever" / "v1" / "results.json"),
        "scifact_v1": _run_id_of(EVAL / "scifact" / "v1" / "results.json"),
        "scifact_open_v1": _run_id_of(EVAL / "scifact_open" / "v1" / "results.json"),
        "direction_v1": _run_id_of(EVAL / "direction" / "v1" / "results.json"),
        "nli_comparison_v1": _run_id_of(EVAL / "nli_comparison" / "v1" / "results.json"),
        "calibration_v1": _run_id_of(EVAL / "calibration" / "v1" / "results.json"),
        "risk_coverage_v1": _run_id_of(EVAL / "calibration" / "v1" / "risk_coverage_results.json"),
        "recall_at_k_v1": _run_id_of(EVAL / "recall_at_k" / "v1" / "results.json"),
        "abstention_diagnostic_v2": _run_id_of(EVAL / "controlled" / "v2" / "abstention_confidence_diagnostic_results.json"),
        "partitioning": _run_id_of(EVAL / "partitioning" / "results.json"),
        "ablation": _run_id_of(EVAL / "ablation" / "results.json"),
        "signal_diagnostic": _run_id_of(EVAL / "ablation" / "signal_diagnostic_results.json"),
        "reconstruction_v1": _run_id_of(EVAL / "reconstruction" / "v1" / "results.json"),
    }

    manifest = {
        "release_id": f"release_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "git_commit": git["commit"],
        "git_dirty": git["is_dirty"],
        "python": versions["python"],
        "dependency_lock_hash": lock_hash,
        "datasets": datasets,
        "models": models,
        "runs": runs,
        "paper_generation": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_paper_results.py",
            "source_hashes": {
                name: _file_hash(EVAL_or_none)["hash"]
                for name, EVAL_or_none in {
                    "controlled_v2_results": EVAL / "controlled" / "v2" / "results.json",
                    "closed_world_v1_results": EVAL / "closed_world" / "v1" / "results.json",
                    "claim_validity_v1_results": EVAL / "claim_validity" / "v1" / "results.json",
                    "fever_v1_results": EVAL / "fever" / "v1" / "results.json",
                    "scifact_v1_results": EVAL / "scifact" / "v1" / "results.json",
                    "scifact_open_v1_results": EVAL / "scifact_open" / "v1" / "results.json",
                    "calibration_v1_results": EVAL / "calibration" / "v1" / "results.json",
                    "risk_coverage_v1_results": EVAL / "calibration" / "v1" / "risk_coverage_results.json",
                    "partitioning_results": EVAL / "partitioning" / "results.json",
                    "ablation_results": EVAL / "ablation" / "results.json",
                    "reconstruction_v1_results": EVAL / "reconstruction" / "v1" / "results.json",
                }.items()
            },
        },
    }

    OUT_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    if git["is_dirty"]:
        print("WARNING: git working tree was dirty when this release manifest was generated.")
    for name, r in runs.items():
        if r["run_id"] is None and r.get("source") is None:
            print(f"NOTE: {name} has neither a run_id nor a declared external source "
                  f"({r.get('reason', 'results.json missing run_id/source field')}).")


if __name__ == "__main__":
    main()
