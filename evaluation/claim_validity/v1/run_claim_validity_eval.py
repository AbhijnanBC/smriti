"""
run_claim_validity_eval.py -- scores Phase 4's real, unmodified
AssertionClassifier against SMRITI-ClaimValidity-v1 (P1-7, "PLEASE FIX
AND SAVE ME" review round).

Uses the actual production classifier (claims/classifier.py) and the
actual production parser (claims/parser.py, real spaCy model, same
model config/default.yaml names) -- no re-implementation, no mocked
parse output. DECLARATIVE_CLAIM/NON_CLAIM spans are scored right/wrong
against the benchmark's construction-defined gold label; AMBIGUOUS spans
are reported as a resolution distribution only (P0-4/P0-12's selective-
prediction framing: there is no single correct label for a genuinely
ambiguous span, so scoring it right/wrong would be the "UNKNOWN
classification accuracy" mistake this paper elsewhere corrects).

RECTIFIED (P1-F, "FINAL REVIEW" round): also reports (a) the diversity
metrics (unique_text_count/template_count/instances_per_template) the
review asked for, per NON_CLAIM subtype, so the benchmark's own
diversity is checkable from the results artifact and not just from
build_benchmark.py's console output, and (b) accuracy/F1 computed
separately on the `train` vs `template_heldout` template split. Because
AssertionClassifier is a fixed rule-based gate, not a model trained on
this benchmark, template-held-out here is a DIVERSITY/ROBUSTNESS check
("does the classifier perform consistently across templates it happens
to see more or less often," not "did it memorize training templates"),
not an ML train/test generalization claim -- and it is reported as such.

Run with:
    poetry run python evaluation/claim_validity/v1/build_benchmark.py   # once
    poetry run python evaluation/claim_validity/v1/run_claim_validity_eval.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from smriti.core.models import AssertionType, SemanticSentence  # noqa: E402
from smriti.claims.classifier import AssertionClassifier  # noqa: E402
from smriti.claims.parser import SpaCyParser  # noqa: E402

BENCHMARK_PATH = ROOT / "evaluation" / "claim_validity" / "v1" / "benchmark.json"
RESULTS_PATH = ROOT / "evaluation" / "claim_validity" / "v1" / "results.json"


def prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def main():
    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    parser = SpaCyParser()
    classifier = AssertionClassifier()

    rows = []
    for e in benchmark:
        sentence = SemanticSentence(
            sentence_id=e["id"], document_id="benchmark", text=e["text"], context="",
            position=0, char_start=0, char_end=len(e["text"]),
            source_path=Path("benchmark.md"), origin_block_type=e["origin_block_type"],
        )
        parsed = parser.parse(sentence)
        predicted_type, reason = classifier.classify(sentence, parsed)
        predicted_binary = "DECLARATIVE_CLAIM" if predicted_type == AssertionType.DECLARATIVE_ASSERTION else "NON_CLAIM"
        rows.append({
            "id": e["id"], "text": e["text"], "gold_label": e["gold_label"],
            "category": e["category"], "predicted_assertion_type": predicted_type.value,
            "predicted_binary": predicted_binary, "reason": reason,
            "template_id": e.get("template_id"), "split": e.get("split"),
        })

    scoreable = [r for r in rows if r["gold_label"] != "AMBIGUOUS"]
    ambiguous = [r for r in rows if r["gold_label"] == "AMBIGUOUS"]

    tp = sum(1 for r in scoreable if r["gold_label"] == "DECLARATIVE_CLAIM" and r["predicted_binary"] == "DECLARATIVE_CLAIM")
    fp = sum(1 for r in scoreable if r["gold_label"] == "NON_CLAIM" and r["predicted_binary"] == "DECLARATIVE_CLAIM")
    fn = sum(1 for r in scoreable if r["gold_label"] == "DECLARATIVE_CLAIM" and r["predicted_binary"] == "NON_CLAIM")
    tn = sum(1 for r in scoreable if r["gold_label"] == "NON_CLAIM" and r["predicted_binary"] == "NON_CLAIM")
    p, rec, f1 = prf1(tp, fp, fn)
    accuracy = round((tp + tn) / len(scoreable), 4)
    macro_f1 = round((f1 + prf1(tn, fn, fp)[2]) / 2, 4)

    print(f"N scoreable (DECLARATIVE_CLAIM + NON_CLAIM) = {len(scoreable)}")
    print(f"TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"DECLARATIVE_CLAIM: precision={p:.1%} recall={rec:.1%} F1={f1:.1%}")
    print(f"Overall accuracy={accuracy:.1%}  macro-F1={macro_f1:.1%}")

    # Per-NON_CLAIM-subtype recall (does the classifier correctly reject
    # each specific non-claim category, or does it leak into DECLARATIVE_ASSERTION?)
    per_category = defaultdict(lambda: {"n": 0, "correctly_rejected": 0, "leaked_as_claim": 0})
    for r in scoreable:
        if r["gold_label"] != "NON_CLAIM":
            continue
        c = per_category[r["category"]]
        c["n"] += 1
        if r["predicted_binary"] == "NON_CLAIM":
            c["correctly_rejected"] += 1
        else:
            c["leaked_as_claim"] += 1
    print("\nPer NON_CLAIM subtype:")
    for cat, c in sorted(per_category.items()):
        print(f"  {cat:<24} n={c['n']:>3}  correctly_rejected={c['correctly_rejected']:>3} "
              f"leaked_as_claim={c['leaked_as_claim']:>3}")

    # Ambiguous: resolution distribution only, never scored right/wrong.
    ambiguous_dist = Counter(r["predicted_binary"] for r in ambiguous)
    print(f"\nAMBIGUOUS (n={len(ambiguous)}, resolution distribution, not scored right/wrong):")
    print(f"  {dict(ambiguous_dist)}")

    # RECTIFIED (P1-F, "FINAL REVIEW" round): diversity metrics per
    # category, computed from this run's own benchmark, not re-derived
    # from build_benchmark.py's console output.
    diversity_by_category = {}
    by_cat_all = defaultdict(list)
    for e in benchmark:
        by_cat_all[e["category"]].append(e)
    for cat, es in by_cat_all.items():
        templates_used = {e.get("template_id") for e in es}
        diversity_by_category[cat] = {
            "n": len(es),
            "unique_text_count": len({e["text"] for e in es}),
            "template_count": len(templates_used),
            "instances_per_template": round(len(es) / len(templates_used), 4) if templates_used else None,
        }
    print("\nDiversity per category (P1-F):")
    for cat, d in sorted(diversity_by_category.items()):
        print(f"  {cat:<22} n={d['n']:>3}  unique_text_count={d['unique_text_count']:>3}  "
              f"template_count={d['template_count']:>3}  instances_per_template={d['instances_per_template']}")

    # RECTIFIED (P1-F): template-held-out evaluation. AssertionClassifier
    # is a fixed rule-based gate not trained on this benchmark, so this
    # is a robustness/diversity check (does accuracy hold up on
    # templates this run treats as "held out"), not an ML
    # train/test-generalization claim.
    train_rows = [r for r in scoreable if r["split"] == "train"]
    heldout_rows = [r for r in scoreable if r["split"] == "template_heldout"]

    def _binary_accuracy(rs):
        if not rs:
            return None
        correct = sum(1 for r in rs if r["predicted_binary"] == r["gold_label"])
        return round(correct / len(rs), 4)

    template_heldout_eval = {
        "note": "AssertionClassifier is a fixed rule-based gate, not trained on this "
                "benchmark -- this is a template-diversity/robustness check, not an ML "
                "train/test generalization result.",
        "train_n": len(train_rows), "train_accuracy": _binary_accuracy(train_rows),
        "template_heldout_n": len(heldout_rows), "template_heldout_accuracy": _binary_accuracy(heldout_rows),
    }
    print(f"\nTemplate-held-out check: train accuracy={template_heldout_eval['train_accuracy']} "
          f"(n={template_heldout_eval['train_n']}), "
          f"template_heldout accuracy={template_heldout_eval['template_heldout_accuracy']} "
          f"(n={template_heldout_eval['template_heldout_n']})")

    out = {
        "n_scoreable": len(scoreable),
        "n_ambiguous": len(ambiguous),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "declarative_claim_precision": p, "declarative_claim_recall": rec, "declarative_claim_f1": f1,
        "overall_accuracy": accuracy, "macro_f1": macro_f1,
        "per_non_claim_subtype": {k: dict(v) for k, v in per_category.items()},
        "ambiguous_resolution_distribution": dict(ambiguous_dist),
        "diversity_by_category": diversity_by_category,
        "template_heldout_eval": template_heldout_eval,
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
