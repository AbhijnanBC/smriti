"""
Leave-one-signal-out sensitivity/ablation study for Phase 8 reliability
fusion (P1-6/P1-7), run against the real, post-fix SMRITI-Reference graph
(run_20260909_193441, 397 claims). Reuses the actual production loader
(PipelineRunner._load_phase7_result) and the actual, unmodified signal
extractors + fusion code -- no re-implementation, no new annotation, no
pipeline re-run.

For each of the 8 registered signals, zero its policy weight (without
renormalizing the rest -- standard leave-one-out: isolates exactly that
signal's own contribution) and recompute reliability_index for every
claim. Report mean shift and Pearson correlation vs. the baseline (all
signals active).

Run with: poetry run python evaluation/ablation/run_ablation.py
"""
import sys
import os
import copy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from smriti.pipeline.runner import PipelineRunner
from smriti.scoring.policies import load_policy
from smriti.scoring.graph_stats import compute_global_stats
from smriti.scoring.normalization import assemble_contribution_set
from smriti.scoring.fusion import compute_reliability
from smriti.scoring.signals import signal_registry

RUN_ID = "20260909_193441"
OUT_PATH = str(ROOT / "evaluation" / "ablation" / "results.json")


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return 1.0 if va == vb else 0.0
    return cov / math.sqrt(va * vb)


def score_all(graph, policy, extractors, global_stats):
    ri_map = {}
    for claim_id, node in sorted(graph.nodes.items()):
        raw_signals = [e.extract(node, graph, global_stats, policy) for e in extractors]
        contribution_set, _, signal_vector = assemble_contribution_set(
            raw_signals, extractors, policy.fusion, claim_id
        )
        ri, unc, _, _ = compute_reliability(contribution_set, policy, signal_vector)
        ri_map[claim_id] = ri
    return ri_map


def main():
    # Avoid PipelineRunner.__init__'s side effect (it mkdirs a fresh
    # artifacts/run_<new_id>/ directory via ManifestManager). We only need
    # its _load_phase7_result method, called unbound against a bare
    # stand-in carrying just the run_id attribute it reads.
    class _RunIdOnly:
        run_id = RUN_ID

    graph = PipelineRunner._load_phase7_result(_RunIdOnly())
    print(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    extractors = signal_registry.ordered_extractors()
    global_stats = compute_global_stats(graph)

    baseline_policy = load_policy()
    baseline_ri = score_all(graph, baseline_policy, extractors, global_stats)
    baseline_values = [baseline_ri[cid] for cid in sorted(baseline_ri)]
    baseline_mean = sum(baseline_values) / len(baseline_values)
    print(f"Baseline mean RI: {baseline_mean:.3f} (n={len(baseline_values)})")

    signal_names = list(baseline_policy.fusion.signal_weights.keys())
    results = []
    for sig in signal_names:
        policy = copy.deepcopy(baseline_policy)
        original_weight = policy.fusion.signal_weights[sig]
        policy.fusion.signal_weights[sig] = 0.0
        ablated_ri = score_all(graph, policy, extractors, global_stats)
        ablated_values = [ablated_ri[cid] for cid in sorted(baseline_ri)]
        ablated_mean = sum(ablated_values) / len(ablated_values)
        mean_abs_delta = sum(
            abs(baseline_ri[cid] - ablated_ri[cid]) for cid in baseline_ri
        ) / len(baseline_ri)
        corr = pearson(baseline_values, ablated_values)
        results.append({
            "signal": sig,
            "original_weight": original_weight,
            "baseline_mean": round(baseline_mean, 3),
            "ablated_mean": round(ablated_mean, 3),
            "mean_shift": round(ablated_mean - baseline_mean, 3),
            "mean_abs_per_claim_delta": round(mean_abs_delta, 3),
            "pearson_r_vs_baseline": round(corr, 4),
        })

    results.sort(key=lambda r: -r["mean_abs_per_claim_delta"])
    print("\nRanked by mean_abs_per_claim_delta (most to least sensitive):")
    for r in results:
        print(r)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(
            {"run_id": RUN_ID, "n_claims": len(baseline_ri), "baseline_mean_ri": round(baseline_mean, 3), "results": results},
            f, indent=2,
        )
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
