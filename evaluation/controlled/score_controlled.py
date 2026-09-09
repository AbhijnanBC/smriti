"""
score_controlled.py — Score SMRITI against SMRITI-Controlled-v1's gold manifest.

Unlike evaluation/annotation/score.py, this needs NO annotation pass at all:
the gold_manifest.json IS the ground truth, by construction (every pair was
written to have an unambiguous, objective relationship — numeric facts,
explicit negation, named-entity attribution). This directly measures both
RETRIEVAL recall (did the intended pair even become an NLI candidate?) and
CLASSIFICATION accuracy (given it was retrieved, was it labeled correctly?)
separately, per the review's P1-13 recommendation.

Run with: poetry run python evaluation/controlled/score_controlled.py <run_id>
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from smriti.evaluation.statistical.bootstrap import bootstrap_proportion_ci

BASE = str(ROOT)
MANIFEST_PATH = os.path.join(BASE, "evaluation", "controlled", "gold_manifest.json")


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def main(run_id: str):
    art = os.path.join(BASE, "artifacts", f"run_{run_id}")
    p4 = json.load(open(os.path.join(art, "phase4", "dataset.json"), encoding="utf-8"))
    p6 = json.load(open(os.path.join(art, "phase6", "dataset.json"), encoding="utf-8"))
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    claim_of_doc = {v: k for k, v in doc_of_claim.items()}  # 1 claim per doc in this corpus

    predicted_by_pair = {}
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        key = frozenset([doc_of_claim.get(a), doc_of_claim.get(b)])
        predicted_by_pair[key] = r["relationship_type"].upper()

    # "Core" categories are the original SMRITI-Controlled-v1 design
    # (propositional CONTRADICTS/SUPPORTS, plus "easy" NEUTRAL pairs that
    # share no vocabulary at all). "neutral_hard_*" categories are a later
    # addition (external review items 3/4): NEUTRAL pairs deliberately
    # constructed to be topically/lexically related, so they test whether
    # the relatedness gate rejects a false CONTRADICTS on a genuinely-
    # related pair -- a different question from the core corpus's recall/
    # accuracy numbers, so they are reported separately and are NOT pooled
    # into "overall" (pooling them would silently change the meaning of
    # every "Overall 58.3%/78.6%"-style number already written about the
    # core corpus elsewhere).
    per_category = defaultdict(lambda: {"retrieved": 0, "total": 0, "correct": 0})
    rows = []
    for pair in manifest:
        key = frozenset([pair["doc_a"], pair["doc_b"]])
        gold = pair["gold_relationship"]
        category = pair["category"]
        predicted = predicted_by_pair.get(key)
        retrieved = predicted is not None
        correct = retrieved and predicted == gold

        per_category[category]["total"] += 1
        if retrieved:
            per_category[category]["retrieved"] += 1
        if correct:
            per_category[category]["correct"] += 1

        rows.append({
            "pair": f"{pair['doc_a']}/{pair['doc_b']}",
            "gold": gold, "category": category,
            "retrieved": retrieved, "predicted": predicted, "correct": correct,
            "is_hard_neutral": category.startswith("neutral_hard"),
        })

    print(f"{'Category':<12} {'Total':>6} {'Retrieved':>10} {'RetrievalRecall':>16} {'CorrectGivenRetrieved':>22} {'ClassAccuracy':>14}")
    overall = {"total": 0, "retrieved": 0, "correct": 0}
    for cat, d in sorted(per_category.items()):
        recall = d["retrieved"] / d["total"] if d["total"] else 0.0
        class_acc = d["correct"] / d["retrieved"] if d["retrieved"] else 0.0
        if not cat.startswith("neutral_hard"):
            overall["total"] += d["total"]
            overall["retrieved"] += d["retrieved"]
            overall["correct"] += d["correct"]
        print(f"{cat:<12} {d['total']:>6} {d['retrieved']:>10} {recall:>16.1%} {d['correct']:>10}/{d['retrieved']:<10} {class_acc:>14.1%}")

    print("-" * 90)
    overall_recall = overall["retrieved"] / overall["total"] if overall["total"] else 0.0
    overall_class_acc = overall["correct"] / overall["retrieved"] if overall["retrieved"] else 0.0
    print(f"{'TOTAL (core)':<12} {overall['total']:>6} {overall['retrieved']:>10} {overall_recall:>16.1%} "
          f"{overall['correct']:>10}/{overall['retrieved']:<10} {overall_class_acc:>14.1%}")

    # ── Bootstrap 95% CIs (P1-11): sampling uncertainty, not run-to-run noise ──
    # Core-corpus rows only, so this CI matches "overall" above exactly.
    core_rows = [r for r in rows if not r["is_hard_neutral"]]
    retrieval_outcomes = [r["retrieved"] for r in core_rows]
    classification_outcomes = [r["correct"] for r in core_rows if r["retrieved"]]
    recall_ci = bootstrap_proportion_ci(retrieval_outcomes)
    class_acc_ci = bootstrap_proportion_ci(classification_outcomes) if classification_outcomes else None
    print(f"\nRetrieval recall 95% CI:        {recall_ci.point_estimate:.1%} "
          f"[{recall_ci.ci_lower:.1%}, {recall_ci.ci_upper:.1%}] (n={recall_ci.n_items})")
    if class_acc_ci:
        print(f"Classification accuracy 95% CI: {class_acc_ci.point_estimate:.1%} "
              f"[{class_acc_ci.ci_lower:.1%}, {class_acc_ci.ci_upper:.1%}] (n={class_acc_ci.n_items})")

    out = {
        "run_id": run_id,
        "per_category": {k: dict(v) for k, v in per_category.items()},
        "overall": overall,
        "overall_retrieval_recall": round(overall_recall, 4),
        "overall_classification_accuracy_given_retrieved": round(overall_class_acc, 4),
        "retrieval_recall_bootstrap_ci": vars(recall_ci),
        "classification_accuracy_bootstrap_ci": vars(class_acc_ci) if class_acc_ci else None,
        "rows": rows,
    }
    out_path = os.path.join(BASE, "evaluation", "controlled", "results.json")
    json.dump(out, open(out_path, "w", encoding="utf-8"), indent=2)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    run_id = sys.argv[1] if len(sys.argv) > 1 else "20260909_193916"
    main(run_id)
