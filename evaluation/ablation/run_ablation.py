"""
Leave-one-signal-out sensitivity/ablation study for Phase 8 reliability
fusion, run against the real, frozen SMRITI-Reference graph (run
20260911_125340, 121 claims -- re-pointed per P1-4/P1-5, "PLEASE FIX AND
SAVE ME" review round, since the prior RUN_ID predated this session's
resolver/corpus fixes; see evaluation/partitioning/run_partitioning_comparison.py
for the same fix applied to the partitioning comparison). Reuses the actual production loader
(PipelineRunner._load_phase7_result) and the actual, unmodified signal
extractors + fusion code -- no re-implementation, no new annotation, no
pipeline re-run.

RECTIFIED (P1-4, external "reality check" review -- reliability vs. graph
importance conflation): a prior version of this script ablated all 8
signals through one fused, unsplit reliability score. Production no
longer computes that number: reliability_index is now fused from the 5
evidence-family signals only, and a separate importance_index is fused
from the 3 topology-family signals (see scoring.policies.
EVIDENCE_SIGNAL_NAMES/IMPORTANCE_SIGNAL_NAMES). This script now runs TWO
leave-one-out studies, one per family, against the SAME real graph and
policy, so the paper table this produces actually describes what
production reports.

Each ablation zeros one signal's policy weight and rebuilds that
family's ContributionSet by filtering (not rescaling) to the remaining
same-family candidates -- deliberately NOT renormalizing the rest, so
the reported shift isolates exactly the zeroed signal's own contribution
(standard leave-one-out). Because of this, the "baseline mean" reported
here is NOT the same number as production's rescaled, reported
reliability_index/importance_index (which renormalizes each family's
weights to sum to 1.0) -- it is the un-rescaled within-family baseline
that leave-one-out sensitivity is measured relative to. Read this table
as relative sensitivity only, exactly as the paper's own prose already
frames it.

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
from smriti.scoring.policies import load_policy, EVIDENCE_SIGNAL_NAMES, IMPORTANCE_SIGNAL_NAMES
from smriti.scoring.graph_stats import compute_global_stats
from smriti.scoring.normalization import assemble_contribution_set
from smriti.scoring.fusion import compute_reliability
from smriti.scoring.constraints import EVIDENCE_CONSTRAINT_PIPELINE, IMPORTANCE_CONSTRAINT_PIPELINE
from smriti.scoring.signals import signal_registry
from smriti.core.models import ContributionSet

RUN_ID = "20260911_125340"  # RECTIFIED (P1-4/P1-5, "PLEASE FIX AND SAVE ME"
# review round): the previous RUN_ID predated this session's resolver/
# corpus fixes (same staleness class as evaluation/partitioning/
# run_partitioning_comparison.py's RUN_ID, fixed alongside this one).
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


def filter_contribution_set(contribution_set: ContributionSet, names: frozenset) -> ContributionSet:
    """Filter to same-family candidates WITHOUT rescaling weights -- unlike
    scoring.normalization.split_contribution_set_by_category, this
    deliberately preserves the leave-one-out design: a zeroed signal's
    weight budget is simply absent, never redistributed to its siblings."""
    selected = tuple(c for c in contribution_set.candidates if c.signal_id.value in names)
    return ContributionSet(
        candidates=selected,
        evidence_completeness=contribution_set.evidence_completeness,
        claim_id=contribution_set.claim_id,
    )


def score_all(graph, policy, extractors, global_stats):
    """Returns (reliability_map, importance_map) -- one leave-one-out pass
    can shift AT MOST one of the two, since evidence-family and
    importance-family signals never share a policy weight key."""
    ri_map, imp_map = {}, {}
    for claim_id, node in sorted(graph.nodes.items()):
        raw_signals = [e.extract(node, graph, global_stats, policy) for e in extractors]
        contribution_set, _, signal_vector = assemble_contribution_set(
            raw_signals, extractors, policy.fusion, claim_id
        )
        evidence_cs = filter_contribution_set(contribution_set, EVIDENCE_SIGNAL_NAMES)
        importance_cs = filter_contribution_set(contribution_set, IMPORTANCE_SIGNAL_NAMES)
        ri, _, _, _ = compute_reliability(
            evidence_cs, policy, signal_vector, constraint_pipeline=EVIDENCE_CONSTRAINT_PIPELINE,
        )
        imp, _, _, _ = compute_reliability(
            importance_cs, policy, signal_vector, constraint_pipeline=IMPORTANCE_CONSTRAINT_PIPELINE,
        )
        ri_map[claim_id] = ri
        imp_map[claim_id] = imp
    return ri_map, imp_map


def run_family_ablation(graph, baseline_policy, extractors, global_stats, family_names, family_label, score_index):
    """score_index: 0 for reliability_index, 1 for importance_index (index
    into the (ri_map, imp_map) tuple score_all returns)."""
    baseline_scores = score_all(graph, baseline_policy, extractors, global_stats)[score_index]
    baseline_values = [baseline_scores[cid] for cid in sorted(baseline_scores)]
    baseline_mean = sum(baseline_values) / len(baseline_values)
    print(f"[{family_label}] baseline mean: {baseline_mean:.3f} (n={len(baseline_values)}, unrescaled within-family)")

    results = []
    for sig in sorted(family_names):
        policy = copy.deepcopy(baseline_policy)
        original_weight = policy.fusion.signal_weights[sig]
        policy.fusion.signal_weights[sig] = 0.0
        ablated_scores = score_all(graph, policy, extractors, global_stats)[score_index]
        ablated_values = [ablated_scores[cid] for cid in sorted(baseline_scores)]
        ablated_mean = sum(ablated_values) / len(ablated_values)
        mean_abs_delta = sum(
            abs(baseline_scores[cid] - ablated_scores[cid]) for cid in baseline_scores
        ) / len(baseline_scores)
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
    return baseline_mean, results


def main():
    class _RunIdOnly:
        run_id = RUN_ID

    graph = PipelineRunner._load_phase7_result(_RunIdOnly())
    print(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    extractors = signal_registry.ordered_extractors()
    global_stats = compute_global_stats(graph)
    baseline_policy = load_policy()

    ev_baseline, ev_results = run_family_ablation(
        graph, baseline_policy, extractors, global_stats,
        EVIDENCE_SIGNAL_NAMES, "reliability_index (evidence family)", 0,
    )
    imp_baseline, imp_results = run_family_ablation(
        graph, baseline_policy, extractors, global_stats,
        IMPORTANCE_SIGNAL_NAMES, "importance_index (topology family)", 1,
    )

    print("\nreliability_index ablation, ranked by mean_abs_per_claim_delta:")
    for r in ev_results:
        print(r)
    print("\nimportance_index ablation, ranked by mean_abs_per_claim_delta:")
    for r in imp_results:
        print(r)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(
            {
                "run_id": RUN_ID,
                "n_claims": len(graph.nodes),
                "reliability_index_ablation": {
                    "baseline_mean_unrescaled": round(ev_baseline, 3),
                    "results": ev_results,
                },
                "importance_index_ablation": {
                    "baseline_mean_unrescaled": round(imp_baseline, 3),
                    "results": imp_results,
                },
            },
            f, indent=2,
        )
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
