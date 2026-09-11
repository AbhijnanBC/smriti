"""
risk_coverage.py -- risk-coverage curve for SMRITI's selective-prediction
signal (P1-2, "PLEASE FIX AND SAVE ME" review round).

Complements P0-7 (SMRITI-Controlled-v2's ambiguous/abstention category:
0% formal abstention rate, an architecture-vs-policy gap already
disclosed in the paper) and P1-1 (calibration): this asks a related but
distinct question -- if SMRITI used its own raw confidence score to
decide "commit or abstain" (rather than the resolver's current
threshold-based ABSTAINED path), how would accuracy trade off against
coverage as the confidence bar is raised?

Uses the SAME resolved, non-abstention pairs from
SMRITI-Controlled-v2's frozen run (score/split join logic mirrors
fit_calibration.py, duplicated rather than imported per this project's
convention of self-contained evaluation scripts) and RAW confidence
(matching what production actually uses today -- config/default.yaml's
calibration is identity, so "confidence_policy: calibrated" currently
means raw confidence; see evaluation/calibration/v1/ for the fitted-but-
undeployed alternative).

Risk = error rate (1 - accuracy) among the pairs NOT abstained on.
Coverage = fraction of all pairs not abstained on.
At coverage=1.0 (commit on everything), risk = 1 - overall accuracy.
AURC = area under the risk-coverage curve (trapezoidal), a standard
single-scalar summary: lower is better, a perfectly-ranked confidence
signal drives risk to 0 quickly as coverage drops from 1.0.

RECTIFIED (P1-H, "FINAL REVIEW" round): the curve above (now labeled
CLASSIFICATION risk-coverage) only ever looks at pairs Phase 6 actually
retrieved and the resolver did not abstain on -- exactly the population
the paper already discloses this curve is restricted to, but the review
is right that this is not the full end-to-end selective-prediction
decision. A second curve, END-TO-END risk-coverage, is added: the
population is every RESOLVED-expected gold pair in the split (not just
the ones that got that far), a pair Phase 6 never retrieved as a
candidate at all is a forced, permanent error/uncovered decision at
every threshold (there is no confidence score to rank it by -- it simply
cannot be committed), an ABSTAINED pair is likewise a permanent
non-commit at every threshold, and "wrong relation" among the retrieved-
and-resolved pairs is an error exactly as before. Coverage in this curve
is `n_committed_and_kept / n_total_gold_pairs`, not `n_kept / n_committed`
-- so end-to-end coverage can never reach 1.0 unless retrieval recall and
the non-abstention rate are both already 100%, which is the point: this
is "fraction of gold decisions actually resolved correctly enough to
commit," a materially harder and more honest number than the
classification-only curve's.

Run with: poetry run python evaluation/calibration/v1/risk_coverage.py <run_id>
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = str(ROOT)
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
RESULTS_PATH = ROOT / "evaluation" / "calibration" / "v1" / "risk_coverage_results.json"


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def risk_coverage_curve(pairs, n_points: int = 20):
    """pairs: list of (confidence, correct), sorted here by confidence
    descending. Reports risk at coverage = 1/n_points, 2/n_points, ..., 1.0."""
    ranked = sorted(pairs, key=lambda t: t[0], reverse=True)
    n = len(ranked)
    curve = []
    for i in range(1, n_points + 1):
        coverage = i / n_points
        k = max(1, round(coverage * n))
        kept = ranked[:k]
        errors = sum(1 for _, y in kept if not y)
        risk = errors / len(kept)
        curve.append({"coverage": round(coverage, 3), "risk": round(risk, 4),
                      "n_kept": len(kept), "confidence_threshold": round(kept[-1][0], 4)})
    return curve


def aurc(curve) -> float:
    """Trapezoidal area under the risk-coverage curve over coverage in (0, 1]."""
    points = [(0.0, curve[0]["risk"])] + [(p["coverage"], p["risk"]) for p in curve]
    area = 0.0
    for (c0, r0), (c1, r1) in zip(points, points[1:]):
        area += (c1 - c0) * (r0 + r1) / 2
    return round(area, 4)


def end_to_end_risk_coverage_curve(committed_pairs, n_total_gold, n_points: int = 20):
    """
    RECTIFIED (P1-H, "FINAL REVIEW" round): `committed_pairs` are only the
    (confidence, correct) pairs the resolver actually retrieved AND did
    not abstain on -- the same population the classification-only curve
    ranks. `n_total_gold` is every RESOLVED-expected gold pair in the
    split, including retrieval misses and abstentions, which never
    appear in `committed_pairs` at all and therefore can never be "kept"
    at any threshold -- they permanently cap the achievable coverage
    below 1.0. Coverage here is always relative to n_total_gold, not to
    len(committed_pairs).
    """
    ranked = sorted(committed_pairs, key=lambda t: t[0], reverse=True)
    max_coverage = len(ranked) / n_total_gold if n_total_gold else 0.0
    curve = []
    for i in range(1, n_points + 1):
        target_coverage = i / n_points
        k = max(0, min(len(ranked), round(target_coverage * n_total_gold)))
        kept = ranked[:k]
        errors = sum(1 for _, y in kept if not y)
        risk = errors / len(kept) if kept else 1.0
        actual_coverage = len(kept) / n_total_gold if n_total_gold else 0.0
        curve.append({
            "target_coverage": round(target_coverage, 3),
            "coverage": round(actual_coverage, 4),
            "risk": round(risk, 4),
            "n_kept": len(kept),
        })
    return curve, round(max_coverage, 4)


def main(run_id: str):
    art = os.path.join(BASE, "artifacts", f"run_{run_id}")
    p4 = json.load(open(os.path.join(art, "phase4", "dataset.json"), encoding="utf-8"))
    p6 = json.load(open(os.path.join(art, "phase6", "dataset.json"), encoding="utf-8"))
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    manifest_by_key = {frozenset([e["doc_a"], e["doc_b"]]): e for e in manifest}

    predicted_by_key = {}
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        key = frozenset([doc_of_claim.get(a), doc_of_claim.get(b)])
        predicted_by_key[key] = r

    # RECTIFIED (P1-H): iterate the GOLD MANIFEST, not Phase 6's output,
    # so a gold pair Phase 6 never retrieved at all still appears in the
    # end-to-end population instead of silently vanishing.
    dev_pairs, test_pairs = [], []
    dev_total, test_total = 0, 0
    dev_miss, test_miss = 0, 0
    dev_abstained, test_abstained = 0, 0
    for entry in manifest:
        if entry["expected_status"] != "RESOLVED":
            continue
        key = frozenset([entry["doc_a"], entry["doc_b"]])
        is_dev = entry["split"] == "dev"
        if is_dev:
            dev_total += 1
        else:
            test_total += 1
        r = predicted_by_key.get(key)
        if r is None:
            if is_dev:
                dev_miss += 1
            else:
                test_miss += 1
            continue
        predicted = r["relationship_type"].upper()
        if predicted == "UNKNOWN":
            if is_dev:
                dev_abstained += 1
            else:
                test_abstained += 1
            continue
        correct = predicted == entry["expected_relation"]
        raw_conf = r["evidence"]["raw_confidence"]
        target = dev_pairs if is_dev else test_pairs
        target.append((raw_conf, correct))

    print(f"DEV: n_total={dev_total} committed={len(dev_pairs)} "
          f"retrieval_miss={dev_miss} abstained={dev_abstained}")
    print(f"TEST: n_total={test_total} committed={len(test_pairs)} "
          f"retrieval_miss={test_miss} abstained={test_abstained}")

    dev_curve = risk_coverage_curve(dev_pairs)
    test_curve = risk_coverage_curve(test_pairs)
    dev_aurc = aurc(dev_curve)
    test_aurc = aurc(test_curve)

    print(f"\n=== CLASSIFICATION risk-coverage (resolved, non-abstained pairs only) ===")
    print(f"DEV AURC = {dev_aurc}   TEST AURC = {test_aurc}")
    print("\nTEST classification risk-coverage curve:")
    print(f"{'coverage':>10} {'risk':>8} {'n_kept':>8} {'conf_threshold':>15}")
    for p in test_curve:
        print(f"{p['coverage']:>10.2f} {p['risk']:>8.3f} {p['n_kept']:>8} {p['confidence_threshold']:>15.4f}")

    # RECTIFIED (P1-H, "FINAL REVIEW" round): END-TO-END risk-coverage --
    # retrieval misses and abstentions permanently cap coverage below 1.0.
    dev_e2e_curve, dev_e2e_max_coverage = end_to_end_risk_coverage_curve(dev_pairs, dev_total)
    test_e2e_curve, test_e2e_max_coverage = end_to_end_risk_coverage_curve(test_pairs, test_total)
    dev_e2e_aurc = aurc(dev_e2e_curve)
    test_e2e_aurc = aurc(test_e2e_curve)

    print(f"\n=== END-TO-END risk-coverage (retrieval miss + abstention = permanent non-commit) ===")
    print(f"DEV max achievable coverage = {dev_e2e_max_coverage}   AURC = {dev_e2e_aurc}")
    print(f"TEST max achievable coverage = {test_e2e_max_coverage}   AURC = {test_e2e_aurc}")
    print("\nTEST end-to-end risk-coverage curve:")
    print(f"{'target_cov':>10} {'coverage':>10} {'risk':>8} {'n_kept':>8}")
    for p in test_e2e_curve:
        print(f"{p['target_coverage']:>10.2f} {p['coverage']:>10.4f} {p['risk']:>8.3f} {p['n_kept']:>8}")

    out = {
        "run_id": run_id,
        "dev_n": len(dev_pairs), "test_n": len(test_pairs),
        "dev_aurc": dev_aurc, "test_aurc": test_aurc,
        "dev_risk_at_full_coverage": dev_curve[-1]["risk"],
        "test_risk_at_full_coverage": test_curve[-1]["risk"],
        "dev_curve": dev_curve,
        "test_curve": test_curve,
        "end_to_end": {
            "dev_n_total": dev_total, "dev_n_committed": len(dev_pairs),
            "dev_n_retrieval_miss": dev_miss, "dev_n_abstained": dev_abstained,
            "dev_max_achievable_coverage": dev_e2e_max_coverage, "dev_aurc": dev_e2e_aurc,
            "dev_curve": dev_e2e_curve,
            "test_n_total": test_total, "test_n_committed": len(test_pairs),
            "test_n_retrieval_miss": test_miss, "test_n_abstained": test_abstained,
            "test_max_achievable_coverage": test_e2e_max_coverage, "test_aurc": test_e2e_aurc,
            "test_curve": test_e2e_curve,
        },
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main(sys.argv[1])
