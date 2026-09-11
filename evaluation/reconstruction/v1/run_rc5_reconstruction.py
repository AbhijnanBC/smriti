"""
run_rc5_reconstruction.py -- RC5 exact audit-trail reconstruction test,
re-run against the current resolver (P1-4/P1-5, "PLEASE FIX AND SAVE
ME" review round: the previous artifact this paper's metamorphic
section reported (run 20260910_170759) predates this session's
resolver/corpus fixes, the same staleness class as
evaluation/partitioning/ and evaluation/ablation/, both already
re-pointed).

For every claim SMRITI actually scored in the current reference_vault
run, independently recompute reliability_index by summing that claim's
own RECORDED per-signal contributions (Phase 8's persisted
signal_manifests -- not re-extracted, not re-derived) through the real,
unmodified fusion + constraint pipeline, and compare against the value
SMRITI itself reported for that claim. This targets whether the
recorded computation is internally consistent with what was reported,
not whether the computation is scientifically correct -- it requires
zero external ground truth.

Run with: poetry run python evaluation/reconstruction/v1/run_rc5_reconstruction.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from smriti.scoring.policies import load_policy, EVIDENCE_SIGNAL_NAMES  # noqa: E402
from smriti.scoring.constraints import EVIDENCE_CONSTRAINT_PIPELINE  # noqa: E402
from smriti.scoring.fusion import compute_reliability  # noqa: E402
from smriti.scoring.normalization import split_contribution_set_by_category  # noqa: E402
from smriti.core.models import ContributionSet, ContributionCandidate, SignalID, SignalVector  # noqa: E402

RUN_ID = "20260911_125340"
RESULTS_PATH = ROOT / "evaluation" / "reconstruction" / "v1" / "results.json"


def main():
    art = ROOT / "artifacts" / f"run_{RUN_ID}" / "phase8" / "dataset.json"
    phase8 = json.loads(art.read_text(encoding="utf-8"))
    policy = load_policy()

    total = 0
    exact = 0
    max_abs_diff = 0.0
    mismatches = []

    for claim_id, rec in phase8["reliability"].items():
        total += 1
        recorded = rec["reliability_index"]

        candidates = []
        for m in rec["signal_manifests"]:
            name = m["signal_id"]
            weight = policy.fusion.signal_weights.get(name, 0.0)
            if weight <= 0:
                continue
            candidates.append(ContributionCandidate(
                signal_id=SignalID(name),
                normalized_value=m["normalized_value"],
                policy_weight=weight,
                direction=policy.fusion.get_direction(name),
                label=name,
                raw_value=m["raw_value"],
            ))
        evidence_completeness = rec["evidence_completeness"]
        full_cs = ContributionSet(candidates=tuple(candidates), evidence_completeness=evidence_completeness,
                                   claim_id=claim_id)
        # Same rescaling production actually applies (P1-4's own fix,
        # scoring/normalization.py) -- NOT run_ablation.py's deliberately
        # un-rescaled leave-one-out variant.
        evidence_cs = split_contribution_set_by_category(full_cs, EVIDENCE_SIGNAL_NAMES)
        sv = SignalVector(**rec["signal_vector"], evidence_completeness=evidence_completeness)
        recomputed, _, _, _ = compute_reliability(
            evidence_cs, policy, sv, constraint_pipeline=EVIDENCE_CONSTRAINT_PIPELINE,
        )

        diff = abs(recomputed - recorded)
        max_abs_diff = max(max_abs_diff, diff)
        if diff <= 0.01:  # 2-decimal display rounding tolerance
            exact += 1
        else:
            mismatches.append({"claim_id": claim_id, "recorded": recorded, "recomputed": round(recomputed, 4),
                                "diff": round(diff, 4)})

    print(f"RC5 reconstruction: {exact}/{total} ({exact/total:.1%}) reconstruct exactly "
          f"(within 0.01 tolerance), max_abs_diff={max_abs_diff:.4f}")
    if mismatches:
        print(f"Mismatches ({len(mismatches)}):")
        for m in mismatches[:10]:
            print(" ", m)

    out = {
        "run_id": RUN_ID, "total": total, "exact": exact,
        "exact_rate": round(exact / total, 4) if total else None,
        "max_abs_diff": round(max_abs_diff, 4),
        "mismatches": mismatches,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
