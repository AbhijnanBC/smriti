"""
Run the full SMRITI pipeline (or a phase range) against a single named vault
under data/raw/, in isolation from the other benchmark vaults.

Usage:
    poetry run python scripts/run_vault.py <vault_name> [--start N] [--stop N] [--policy PROFILE]

Example:
    poetry run python scripts/run_vault.py gold_vault --start 1 --stop 12
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from smriti.core.paths import RAW_DATA_DIR, PROJECT_ROOT, ARTIFACTS_DIR
from smriti.core.logger import setup_logging
from smriti.pipeline.runner import PipelineRunner


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("vault", help="Directory name under data/raw/")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--stop", type=int, default=12)
    args = parser.parse_args()

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
    }, indent=2))
    print(f"Benchmark record written to {bench_path}")


if __name__ == "__main__":
    main()
