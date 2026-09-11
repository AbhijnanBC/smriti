"""
Run the full SMRITI pipeline (or a phase range) against a single named vault
under data/raw/, in isolation from the other benchmark vaults.

Usage:
    poetry run python scripts/run_vault.py <vault_name> [--start N] [--stop N] [--policy PROFILE]

Example:
    poetry run python scripts/run_vault.py reference_vault --start 1 --stop 12
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import sys as _sys

from smriti.core.paths import RAW_DATA_DIR, PROJECT_ROOT, ARTIFACTS_DIR
from smriti.core.logger import setup_logging
from smriti.core.config import get_config
from smriti.pipeline.runner import PipelineRunner

_sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_run_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vault", help="Directory name under data/raw/")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--stop", type=int, default=12)
    parser.add_argument(
        "--env", default="dev",
        help=(
            "Config environment (config/{env}.yaml, deep-merged over "
            "default.yaml). Use 'eval' for evaluation runs that need every "
            "NLI-scored candidate pair retained (skip_unknown_relationships"
            "/skip_neutral_relationships disabled) for candidate-level "
            "precision/recall metrics (external review P0-9) -- production "
            "runs should keep the 'dev' default, which omits NEUTRAL/UNKNOWN "
            "to avoid graph bloat."
        ),
    )
    args = parser.parse_args()

    # RECTIFIED (external "reality check" review round 3, found while
    # re-verifying P0-9 candidate-level metrics): setup_logging() itself
    # calls get_config() internally (to read logging.level) -- when it
    # ran BEFORE this line (as it did until this fix), it silently seeded
    # the config singleton with the default "dev" env before --env's
    # value was ever read, making every `--env eval` invocation of this
    # script since config/eval.yaml was introduced a silent no-op: Phase 6
    # kept skip_unknown/skip_neutral at their production "dev" defaults
    # (true) regardless of --env, so no candidate-level precision/recall
    # run this project has produced with this script actually retained
    # every scored candidate as intended. Must seed the config singleton
    # with the requested env BEFORE any other module call, including
    # setup_logging() -- get_config()'s env argument is ignored once the
    # singleton already exists.
    get_config(env=args.env)
    setup_logging()

    vault_dir = RAW_DATA_DIR / args.vault
    if not vault_dir.exists():
        raise SystemExit(f"Vault not found: {vault_dir}")

    # The pipeline_state.json is global (not keyed by run_id), so a stale
    # state file from a previous vault run would make this run silently
    # "resume" from the wrong point. Since it is pure ephemeral run state
    # (not immutable data), reset it before each isolated benchmark run.
    state_file = ARTIFACTS_DIR / "pipeline_state.json"
    if state_file.exists():
        state_file.unlink()

    n_docs = sum(1 for p in vault_dir.rglob("*") if p.is_file() and not p.name.startswith("_"))
    print(f"=== Running pipeline on vault='{args.vault}' ({n_docs} files) start={args.start} stop={args.stop} ===")

    runner = PipelineRunner(input_dirs=[vault_dir])
    run_id = runner.run_id

    t0 = time.perf_counter()
    ok = runner.run(start_from=args.start, stop_at=args.stop)
    elapsed = time.perf_counter() - t0

    print(f"=== Pipeline {'SUCCEEDED' if ok else 'FAILED'} in {elapsed:.2f}s (run_id={run_id}) ===")

    # RECTIFIED (P1-12, "PLEASE FIX AND SAVE ME" review round): a
    # reproducibility manifest should not depend on someone remembering
    # to separately invoke scripts/generate_run_manifest.py. Generate it
    # automatically right after a successful run, and if generation
    # itself fails, the run is reported incomplete (manifest_generated =
    # False) rather than silently missing a manifest with no trace of why.
    manifest_generated = False
    manifest_error = None
    if ok:
        try:
            generate_run_manifest.main(run_id)
            manifest_generated = True
        except Exception as e:  # noqa: BLE001 -- must never crash a successful pipeline run
            manifest_error = str(e)
            print(f"WARNING: run succeeded but automatic run-manifest generation failed: {e}")

    # Record a small benchmark record alongside the run's artifacts.
    bench_path = ARTIFACTS_DIR / f"run_{run_id}" / "benchmark.json"
    bench_path.parent.mkdir(parents=True, exist_ok=True)
    bench_path.write_text(json.dumps({
        "vault": args.vault,
        "n_input_files": n_docs,
        "start_phase": args.start,
        "stop_phase": args.stop,
        "success": ok,
        "elapsed_seconds": elapsed,
        "run_id": run_id,
        "manifest_generated": manifest_generated,
        "manifest_error": manifest_error,
        "complete": ok and manifest_generated,
    }, indent=2))
    print(f"Benchmark record written to {bench_path}")
    if ok and not manifest_generated:
        print(f"=== Run {run_id}: pipeline succeeded but manifest generation failed -- "
              f"marked incomplete (complete=False in benchmark.json) ===")


if __name__ == "__main__":
    main()
