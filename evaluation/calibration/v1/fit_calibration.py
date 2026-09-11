"""
fit_calibration.py -- fits a real, frozen temperature-scaling calibrator
on SMRITI-Controlled-v2's DEV split and evaluates it on the frozen TEST
split (P1-1/"Calibration experiment" from the "PLEASE FIX AND SAVE ME"
review round).

RECTIFIED (P1-1): src/smriti/retrieval/classification/calibration.py's
ConfidenceCalibrator has always supported a real TEMPERATURE strategy,
but config/default.yaml's `calibration: {}` means every model defaults
to IDENTITY -- so `confidence_policy: "calibrated"` (the resolver's own
config key, read from every result in this paper so far) has been
selecting the IDENTITY-calibrated (i.e. uncalibrated, raw NLI softmax)
confidence value the entire time. Calling that value "calibrated
confidence" without ever having fit a calibrator is exactly the
terminology problem the review flags. This script closes that gap for
real: fit temperature scaling on DEV, freeze it, evaluate ECE/Brier/NLL
on TEST for both the raw (T=1, i.e. today's actual behavior) and the
fitted-T confidence, so the paper can report an honest before/after
rather than asserting calibration without evidence.

Calibration target: this fits temperature T using the SAME 3-class
log-softmax formula production code actually applies
(ConfidenceCalibrator._temperature_scale, imported directly here rather
than reimplemented, so the fitted T is guaranteed compatible with
config/default.yaml's `calibration:` block if it is ever deployed) --
NOT a simplified scalar-logit approximation. The three per-direction
scores (entailment/neutral/contradiction) used are the pipeline's own
A_TO_B-direction NLI scores, matching exactly what ConfidenceCalibrator.
calibrate() calibrates in production (it calibrates each direction's
raw scores independently; A_TO_B is used here as the representative
direction, a disclosed simplification, not the full bidirectional
decision-confidence combination compute_decision_confidence() performs
downstream). The calibration TARGET is binary: did the resolver's final
decision match the gold expected_relation for that pair (1) or not (0)
-- this is a correctness calibrator ("when SMRITI reports confidence q,
how often is it actually right"), not a class-membership calibrator.

Never fit on TEST -- T is chosen entirely from DEV rows; TEST is scored
once, after freezing T, and reported as-is.

Run with: poetry run python evaluation/calibration/v1/fit_calibration.py <run_id>
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from smriti.retrieval.classification.calibration import ConfidenceCalibrator  # noqa: E402

BASE = str(ROOT)
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
RESULTS_PATH = ROOT / "evaluation" / "calibration" / "v1" / "results.json"


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def temp_scale(entailment: float, neutral: float, contradiction: float, T: float) -> float:
    """The exact production formula (imported, not reimplemented) -- see
    ConfidenceCalibrator._temperature_scale for the 3-class log-softmax
    definition this calls."""
    return ConfidenceCalibrator._temperature_scale(entailment, neutral, contradiction, T)


def nll(pairs) -> float:
    total = 0.0
    for q, y in pairs:
        q = min(max(q, 1e-9), 1 - 1e-9)
        total += -(y * math.log(q) + (1 - y) * math.log(1 - q))
    return total / len(pairs) if pairs else 0.0


def brier(pairs) -> float:
    return sum((q - y) ** 2 for q, y in pairs) / len(pairs) if pairs else 0.0


def ece(pairs, n_bins: int = 10) -> float:
    bins = [[] for _ in range(n_bins)]
    for q, y in pairs:
        idx = min(int(q * n_bins), n_bins - 1)
        bins[idx].append((q, y))
    total = 0.0
    n = len(pairs)
    for b in bins:
        if not b:
            continue
        avg_conf = sum(q for q, _ in b) / len(b)
        avg_acc = sum(y for _, y in b) / len(b)
        total += (len(b) / n) * abs(avg_conf - avg_acc)
    return total


def reliability_diagram(pairs, n_bins: int = 10):
    bins = [[] for _ in range(n_bins)]
    for q, y in pairs:
        idx = min(int(q * n_bins), n_bins - 1)
        bins[idx].append((q, y))
    out = []
    for i, b in enumerate(bins):
        if not b:
            out.append({"bin": [i / n_bins, (i + 1) / n_bins], "n": 0, "avg_confidence": None, "avg_accuracy": None})
            continue
        out.append({
            "bin": [i / n_bins, (i + 1) / n_bins], "n": len(b),
            "avg_confidence": round(sum(q for q, _ in b) / len(b), 4),
            "avg_accuracy": round(sum(y for _, y in b) / len(b), 4),
        })
    return out


def fit_temperature(dev_triples) -> float:
    """Grid search T minimizing NLL on DEV. Never touches TEST."""
    raw_pairs = [(max(e, n, c), y) for e, n, c, y in dev_triples]
    best_T, best_nll = 1.0, nll(raw_pairs)
    T = 0.05
    while T <= 5.0001:
        scaled = [(temp_scale(e, n, c, T), y) for e, n, c, y in dev_triples]
        cur = nll(scaled)
        if cur < best_nll:
            best_nll, best_T = cur, T
        T += 0.02
    return best_T


def main(run_id: str):
    art = os.path.join(BASE, "artifacts", f"run_{run_id}")
    p4 = json.load(open(os.path.join(art, "phase4", "dataset.json"), encoding="utf-8"))
    p6 = json.load(open(os.path.join(art, "phase6", "dataset.json"), encoding="utf-8"))
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    manifest_by_key = {frozenset([e["doc_a"], e["doc_b"]]): e for e in manifest}

    dev_triples, test_triples = [], []
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        key = frozenset([doc_of_claim.get(a), doc_of_claim.get(b)])
        entry = manifest_by_key.get(key)
        if entry is None or entry["expected_status"] != "RESOLVED":
            continue  # not a manifest pair, or a genuinely-ambiguous pair with no single correct label
        predicted = r["relationship_type"].upper()
        correct = 1 if predicted == entry["expected_relation"] else 0
        ev = r["evidence"]
        triple = (ev["entailment_score"], ev["neutral_score"], ev["contradiction_score"], correct)
        target = dev_triples if entry["split"] == "dev" else test_triples
        target.append(triple)

    print(f"DEV pairs usable for calibration: {len(dev_triples)}")
    print(f"TEST pairs usable for calibration: {len(test_triples)}")

    T = fit_temperature(dev_triples)
    print(f"\nFitted temperature (on DEV only): T = {T:.3f}")

    dev_raw = [(max(e, n, c), y) for e, n, c, y in dev_triples]
    dev_calibrated = [(temp_scale(e, n, c, T), y) for e, n, c, y in dev_triples]
    test_raw = [(max(e, n, c), y) for e, n, c, y in test_triples]
    test_calibrated = [(temp_scale(e, n, c, T), y) for e, n, c, y in test_triples]

    def report(name, pairs):
        return {
            "n": len(pairs),
            "ece": round(ece(pairs), 4),
            "brier": round(brier(pairs), 4),
            "nll": round(nll(pairs), 4),
            "mean_confidence": round(sum(q for q, _ in pairs) / len(pairs), 4) if pairs else None,
            "accuracy": round(sum(y for _, y in pairs) / len(pairs), 4) if pairs else None,
        }

    results = {
        "run_id": run_id,
        "fitted_temperature": round(T, 4),
        "note": (
            "Scalar temperature scaling on the top-1 max-softmax NLI confidence, "
            "fit on DEV only (never TEST), target = binary decision correctness "
            "against the manifest's expected_relation."
        ),
        "dev_raw_T1": report("dev_raw", dev_raw),
        "dev_calibrated": report("dev_calibrated", dev_calibrated),
        "test_raw_T1": report("test_raw", test_raw),
        "test_calibrated": report("test_calibrated", test_calibrated),
        "reliability_diagram_test_raw": reliability_diagram(test_raw),
        "reliability_diagram_test_calibrated": reliability_diagram(test_calibrated),
    }

    for label, key in [("DEV raw (T=1)", "dev_raw_T1"), ("DEV calibrated", "dev_calibrated"),
                        ("TEST raw (T=1)", "test_raw_T1"), ("TEST calibrated", "test_calibrated")]:
        d = results[key]
        print(f"{label:<18} n={d['n']:>4}  ECE={d['ece']:.4f}  Brier={d['brier']:.4f}  "
              f"NLL={d['nll']:.4f}  mean_conf={d['mean_confidence']}  accuracy={d['accuracy']}")

    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main(sys.argv[1])
