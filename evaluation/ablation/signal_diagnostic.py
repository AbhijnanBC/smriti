"""
signal_diagnostic.py -- per-signal diagnostic for Phase 8 fusion (P1-5's
"conflict_pressure = 0 is not evidence the signal is unimportant" ask,
"PLEASE FIX AND SAVE ME" review round, section 17).

conflict_pressure's ablation delta is exactly 0.0 on the current
reference graph (evaluation/ablation/results.json). The review is
explicit that this is NOT by itself evidence the signal is unimportant
-- it could mean: signal unavailable, signal almost constant, signal
computed incorrectly, weight ineffective, or corpus lacks variation.
This script reports, for EVERY evidence-family and importance-family
signal (not just conflict_pressure, so the same diagnostic can be
checked for any signal going forward): availability (fraction of claims
where the signal fires at all), mean, variance, non-zero fraction, and
policy weight, reusing run_ablation.py's own graph-loading and
signal-extraction code (not reimplemented).

Run with: poetry run python evaluation/ablation/signal_diagnostic.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from smriti.pipeline.runner import PipelineRunner  # noqa: E402
from smriti.scoring.policies import load_policy, EVIDENCE_SIGNAL_NAMES, IMPORTANCE_SIGNAL_NAMES  # noqa: E402
from smriti.scoring.graph_stats import compute_global_stats  # noqa: E402
from smriti.scoring.normalization import assemble_contribution_set  # noqa: E402
from smriti.scoring.signals import signal_registry  # noqa: E402

from run_ablation import RUN_ID  # noqa: E402

RESULTS_PATH = ROOT / "evaluation" / "ablation" / "signal_diagnostic_results.json"


def main():
    class _RunIdOnly:
        run_id = RUN_ID

    graph = PipelineRunner._load_phase7_result(_RunIdOnly())
    print(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges (run_id={RUN_ID})")

    extractors = signal_registry.ordered_extractors()
    global_stats = compute_global_stats(graph)
    policy = load_policy()

    per_signal_raw = {}
    per_signal_normalized = {}
    for claim_id, node in sorted(graph.nodes.items()):
        raw_signals = [e.extract(node, graph, global_stats, policy) for e in extractors]
        contribution_set, _, _ = assemble_contribution_set(raw_signals, extractors, policy.fusion, claim_id)
        seen = set()
        for c in contribution_set.candidates:
            name = c.signal_id.value
            per_signal_raw.setdefault(name, []).append(c.raw_value)
            per_signal_normalized.setdefault(name, []).append(c.normalized_value)
            seen.add(name)

    n_claims = len(graph.nodes)
    all_signal_names = EVIDENCE_SIGNAL_NAMES | IMPORTANCE_SIGNAL_NAMES
    report = {}
    for name in sorted(all_signal_names):
        raw = per_signal_raw.get(name, [])
        availability = round(len(raw) / n_claims, 4) if n_claims else 0.0
        mean = round(sum(raw) / len(raw), 4) if raw else None
        variance = round(sum((x - mean) ** 2 for x in raw) / len(raw), 6) if raw else None
        nonzero_fraction = round(sum(1 for x in raw if x != 0.0) / len(raw), 4) if raw else None
        weight = policy.fusion.signal_weights.get(name)
        report[name] = {
            "family": "evidence" if name in EVIDENCE_SIGNAL_NAMES else "importance",
            "availability": availability,
            "n_available": len(raw),
            "mean_raw_value": mean,
            "variance_raw_value": variance,
            "non_zero_fraction": nonzero_fraction,
            "policy_weight": weight,
        }
        print(f"{name:<24} family={report[name]['family']:<11} availability={availability:.1%} "
              f"n={len(raw):>4} mean={mean} var={variance} non_zero_frac={nonzero_fraction} weight={weight}")

    RESULTS_PATH.write_text(json.dumps({"run_id": RUN_ID, "n_claims": n_claims, "signals": report},
                                        indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
