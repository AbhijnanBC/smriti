"""
abstention_confidence_diagnostic.py -- confidence/margin/entropy
diagnostic for the ambiguous_abstention TEST category (P0-E, "FINAL
REVIEW" round).

Directly answers the review's key diagnostic question: does the
resolver fail to abstain on these 15 deliberately-hedged pairs because
its confidence is genuinely LOW (a threshold-tuning problem, Option 1 in
the review) or because it is confidently wrong about what kind of
uncertainty this is (a benchmark-design problem, Option 2)? This never
modifies the resolver or the corpus -- it only reads the frozen run's
own recorded NLI scores for the 15 pairs and reports confidence, margin
(top class vs. second class), and entropy for both directions.

Run with: poetry run python evaluation/controlled/v2/abstention_confidence_diagnostic.py <run_id>
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
RESULTS_PATH = ROOT / "evaluation" / "controlled" / "v2" / "abstention_confidence_diagnostic_results.json"


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def entropy3(p1, p2, p3):
    total = 0.0
    for p in (p1, p2, p3):
        if p > 1e-12:
            total -= p * math.log(p, 3)  # base-3 log -> normalized to [0, 1]
    return total


def main(run_id: str):
    art = ROOT / "artifacts" / f"run_{run_id}"
    p4 = json.loads((art / "phase4" / "dataset.json").read_text(encoding="utf-8"))
    p6 = json.loads((art / "phase6" / "dataset.json").read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    amb_docs = {
        frozenset([e["doc_a"], e["doc_b"]])
        for e in manifest if e["expected_status"] == "ABSTAINED" and e["split"] == "test"
    }

    rows = []
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        key = frozenset([doc_of_claim.get(a), doc_of_claim.get(b)])
        if key not in amb_docs:
            continue
        ev = r["evidence"]
        e_ab, n_ab, c_ab = ev["entailment_score"], ev["neutral_score"], ev["contradiction_score"]
        e_ba, n_ba, c_ba = ev["entailment_score_b_to_a"], ev["neutral_score_b_to_a"], ev["contradiction_score_b_to_a"]
        margin_ab = n_ab - max(e_ab, c_ab)
        margin_ba = n_ba - max(e_ba, c_ba)
        rows.append({
            "e_ab": e_ab, "n_ab": n_ab, "c_ab": c_ab, "margin_ab": round(margin_ab, 4),
            "entropy_ab": round(entropy3(e_ab, n_ab, c_ab), 4),
            "e_ba": e_ba, "n_ba": n_ba, "c_ba": c_ba, "margin_ba": round(margin_ba, 4),
            "entropy_ba": round(entropy3(e_ba, n_ba, c_ba), 4),
        })

    n = len(rows)
    mean_n_ab = sum(r["n_ab"] for r in rows) / n
    mean_n_ba = sum(r["n_ba"] for r in rows) / n
    mean_margin_ab = sum(r["margin_ab"] for r in rows) / n
    mean_margin_ba = sum(r["margin_ba"] for r in rows) / n
    mean_entropy_ab = sum(r["entropy_ab"] for r in rows) / n
    mean_entropy_ba = sum(r["entropy_ba"] for r in rows) / n
    min_n_ab = min(r["n_ab"] for r in rows)
    min_n_ba = min(r["n_ba"] for r in rows)

    print(f"N = {n}")
    print(f"mean neutral confidence: A->B={mean_n_ab:.4f}  B->A={mean_n_ba:.4f}")
    print(f"mean margin (winning class vs. runner-up): A->B={mean_margin_ab:.4f}  B->A={mean_margin_ba:.4f}")
    print(f"mean normalized entropy (0=certain, 1=maximally uncertain over 3 classes): "
          f"A->B={mean_entropy_ab:.4f}  B->A={mean_entropy_ba:.4f}")
    print(f"minimum neutral confidence observed across all 15 pairs, either direction: "
          f"{min(min_n_ab, min_n_ba):.4f}")

    out = {
        "run_id": run_id, "n": n,
        "mean_neutral_confidence_ab": round(mean_n_ab, 4), "mean_neutral_confidence_ba": round(mean_n_ba, 4),
        "mean_margin_ab": round(mean_margin_ab, 4), "mean_margin_ba": round(mean_margin_ba, 4),
        "mean_entropy_ab": round(mean_entropy_ab, 4), "mean_entropy_ba": round(mean_entropy_ba, 4),
        "min_neutral_confidence_either_direction": round(min(min_n_ab, min_n_ba), 4),
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main(sys.argv[1])
