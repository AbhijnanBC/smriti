"""
score_closed_world.py -- scores SMRITI against SMRITI-ClosedWorld-v1
(P0-8, "PLEASE FIX AND SAVE ME" review round).

Unlike evaluation/controlled/v2/score_controlled_v2.py's candidate_metrics
(open-world: an out-of-manifest candidate is a volume count, not a known
false positive), every one of this benchmark's 900 DESIGNATED pairs has
a KNOWN true label (evaluation/controlled/generators/build_closed_world.py's
three buckets: intended / guaranteed_neutral_distractor /
guaranteed_contradiction_distractor). This script computes genuine
closed LABELED-PAIR CONTRADICTS precision/recall/F1 across those 900
designated pairs, using that known ground truth -- the actual thing
P0-8 asked for, distinct from and not a replacement for controlled-v2's
own (open-world) numbers.

RECTIFIED (P0-D, "FINAL REVIEW" round): this is a closed labeled-pair
measurement, not a closed candidate-universe measurement -- see
build_closed_world.py's own docstring for the distinction. This script
itself reports (and never conflates) `candidates_scored_within_benchmark`
(the real, larger denominator Phase 6 actually scores within this
benchmark's document set) against `candidates_matching_a_manifest_pair`
(the 900 designated pairs) so a reader can see exactly how much of the
candidate universe remains unlabeled.

Run with:
    poetry run python scripts/run_vault.py closed_world_v1 --start 1 --stop 6 --env eval
    poetry run python evaluation/closed_world/v1/score_closed_world.py <run_id>
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

BASE = str(ROOT)
MANIFEST_PATH = ROOT / "evaluation" / "closed_world" / "v1" / "construction_manifest.json"


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def main(run_id: str):
    art = os.path.join(BASE, "artifacts", f"run_{run_id}")
    p4 = json.load(open(os.path.join(art, "phase4", "dataset.json"), encoding="utf-8"))
    p6 = json.load(open(os.path.join(art, "phase6", "dataset.json"), encoding="utf-8"))
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    manifest_doc_ids = {e["doc_a"] for e in manifest} | {e["doc_b"] for e in manifest}

    predicted_by_pair = {}
    all_candidate_keys_within_benchmark = set()
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        doc_a, doc_b = doc_of_claim.get(a), doc_of_claim.get(b)
        if doc_a not in manifest_doc_ids or doc_b not in manifest_doc_ids:
            continue  # candidate involves a document outside this benchmark entirely
        key = frozenset([doc_a, doc_b])
        predicted_by_pair[key] = r["relationship_type"].upper()
        all_candidate_keys_within_benchmark.add(key)

    manifest_keys = {frozenset([e["doc_a"], e["doc_b"]]) for e in manifest}

    rows = []
    for pair in manifest:
        key = frozenset([pair["doc_a"], pair["doc_b"]])
        gold = pair["expected_relation"]
        predicted = predicted_by_pair.get(key)
        retrieved = predicted is not None
        rows.append({
            "pair": f"{pair['doc_a']}/{pair['doc_b']}",
            "gold": gold, "bucket": pair["bucket"], "category": pair["category"],
            "retrieved": retrieved, "predicted": predicted,
            "correct": retrieved and predicted == gold,
        })

    print(f"Manifest: {len(manifest)} pairs, {len(manifest_doc_ids)} documents")
    print(f"Candidates scored by Phase 6 with both members inside this benchmark's "
          f"document set: {len(all_candidate_keys_within_benchmark)}")
    out_of_manifest_within_benchmark = all_candidate_keys_within_benchmark - manifest_keys
    print(f"  of which correspond to a manifest pair (bucket A/B/C): "
          f"{len(all_candidate_keys_within_benchmark & manifest_keys)}")
    print(f"  of which are cross-pair candidates outside all three buckets "
          f"(still open-world -- no known label): {len(out_of_manifest_within_benchmark)}")

    # ── Per-bucket retrieval/classification summary ─────────────────────
    print("\nPer-bucket summary:")
    by_bucket = defaultdict(list)
    for r in rows:
        by_bucket[r["bucket"]].append(r)
    for bucket, rs in sorted(by_bucket.items()):
        retrieved = sum(1 for r in rs if r["retrieved"])
        correct = sum(1 for r in rs if r["correct"])
        print(f"  {bucket:<32} n={len(rs):>4}  retrieved={retrieved:>4} "
              f"({retrieved/len(rs):.1%})  correct_given_retrieved="
              f"{correct}/{retrieved if retrieved else 1} "
              f"({(correct/retrieved if retrieved else 0):.1%})")

    # ── P1-D ("FINAL REVIEW" round): full 5-way evaluation across ALL 900
    #    labeled pairs -- accuracy, macro-F1, per-class P/R/F1, confusion
    #    matrix, and abstention rate. The benchmark's gold labels span all
    #    5 relation classes (checked directly against construction_manifest.json:
    #    CONTRADICTS=474, NEUTRAL=332, SUPPORTS=32, REFINES=31,
    #    EQUIVALENT=31), so this is a real 5-way measurement, not just the
    #    CONTRADICTS-only slice below. A pair that was not retrieved by
    #    Phase 6 at all, or that the resolver ABSTAINED on (relationship_type
    #    "unknown"), counts as an incorrect prediction for accuracy/macro-F1
    #    (never silently dropped from the denominator) and separately as
    #    an abstention for the abstention-rate figure.
    RELATION_CLASSES = ["SUPPORTS", "CONTRADICTS", "REFINES", "EQUIVALENT", "NEUTRAL"]

    def five_way_label(predicted):
        if predicted is None:
            return "NOT_RETRIEVED"
        if predicted == "UNKNOWN":
            return "ABSTAINED"
        return predicted

    n_pairs = len(rows)
    n_correct_5way = sum(1 for r in rows if five_way_label(r["predicted"]) == r["gold"])
    accuracy_5way = n_correct_5way / n_pairs if n_pairs else 0.0
    n_abstained = sum(1 for r in rows if five_way_label(r["predicted"]) == "ABSTAINED")
    n_not_retrieved = sum(1 for r in rows if five_way_label(r["predicted"]) == "NOT_RETRIEVED")
    abstention_rate = n_abstained / n_pairs if n_pairs else 0.0

    confusion_matrix = {gold: defaultdict(int) for gold in RELATION_CLASSES}
    per_class_prf1 = {}
    per_class_f1s = []
    for cls in RELATION_CLASSES:
        cls_tp = sum(1 for r in rows if r["gold"] == cls and five_way_label(r["predicted"]) == cls)
        cls_fp = sum(1 for r in rows if r["gold"] != cls and five_way_label(r["predicted"]) == cls)
        cls_fn = sum(1 for r in rows if r["gold"] == cls and five_way_label(r["predicted"]) != cls)
        cp, cr, cf1 = prf1(cls_tp, cls_fp, cls_fn)
        per_class_prf1[cls] = {
            "precision": cp, "recall": cr, "f1": cf1,
            "tp": cls_tp, "fp": cls_fp, "fn": cls_fn,
            "gold_n": sum(1 for r in rows if r["gold"] == cls),
        }
        per_class_f1s.append(cf1)
    for r in rows:
        confusion_matrix[r["gold"]][five_way_label(r["predicted"])] += 1
    confusion_matrix = {gold: dict(preds) for gold, preds in confusion_matrix.items()}
    macro_f1 = sum(per_class_f1s) / len(per_class_f1s) if per_class_f1s else 0.0

    print(f"\n=== 5-way evaluation (all {n_pairs} labeled pairs, P1-D) ===")
    print(f"  accuracy={accuracy_5way:.1%}  macro_f1={macro_f1:.4f}  "
          f"abstention_rate={abstention_rate:.1%} (n={n_abstained})  "
          f"not_retrieved={n_not_retrieved}")
    for cls in RELATION_CLASSES:
        m = per_class_prf1[cls]
        print(f"  {cls:<12} P={m['precision']:.1%}  R={m['recall']:.1%}  "
              f"F1={m['f1']:.1%}  gold_n={m['gold_n']}")
    print("  Confusion matrix (rows=gold, cols=predicted):")
    for gold in RELATION_CLASSES:
        print(f"    {gold:<12} {confusion_matrix[gold]}")

    # ── Closed-world CONTRADICTS precision/recall/F1 across ALL 900 pairs:
    #    every pair here has a KNOWN true label, so this is a real
    #    precision/recall measurement, not an open-world volume count ────
    tp = sum(1 for r in rows if r["gold"] == "CONTRADICTS" and r["predicted"] == "CONTRADICTS")
    fp = sum(1 for r in rows if r["gold"] != "CONTRADICTS" and r["predicted"] == "CONTRADICTS")
    fn = sum(1 for r in rows if r["gold"] == "CONTRADICTS" and r["predicted"] != "CONTRADICTS")
    p, rec, f1 = prf1(tp, fp, fn)
    n_gold_contradicts = sum(1 for r in rows if r["gold"] == "CONTRADICTS")
    print(f"\n=== Closed-world CONTRADICTS precision/recall/F1 (all 900 pairs, known labels) ===")
    print(f"  TP={tp}  FP={fp}  FN={fn}  gold_n={n_gold_contradicts}")
    print(f"  precision={p:.1%}  recall={rec:.1%}  F1={f1:.1%}")

    # Where do the false positives actually come from?
    fp_rows = [r for r in rows if r["gold"] != "CONTRADICTS" and r["predicted"] == "CONTRADICTS"]
    fp_by_bucket = defaultdict(int)
    for r in fp_rows:
        fp_by_bucket[r["bucket"]] += 1
    print(f"  False positives by bucket: {dict(fp_by_bucket)}")

    # Specifically: does the resolver correctly reject the guaranteed-neutral
    # distractors (same-entity, different-attribute pairs) as NOT CONTRADICTS?
    neutral_rows = by_bucket["guaranteed_neutral_distractor"]
    neutral_retrieved = [r for r in neutral_rows if r["retrieved"]]
    neutral_false_contradicts = sum(1 for r in neutral_retrieved if r["predicted"] == "CONTRADICTS")
    print(f"\n  guaranteed_neutral_distractor: {len(neutral_retrieved)}/{len(neutral_rows)} retrieved, "
          f"{neutral_false_contradicts} of the retrieved ones misclassified CONTRADICTS "
          f"({(neutral_false_contradicts/len(neutral_retrieved) if neutral_retrieved else 0):.1%} "
          f"false-CONTRADICTS rate on a definitionally-NEUTRAL, structurally-CONTRADICTS-like distractor)")

    # Specifically: does the resolver correctly accept the guaranteed-
    # contradiction distractors (same construction as validated CONTRADICTS
    # "direct" subtype, but outside the intended-pair bookkeeping)?
    contra_rows = by_bucket["guaranteed_contradiction_distractor"]
    contra_retrieved = [r for r in contra_rows if r["retrieved"]]
    contra_correct = sum(1 for r in contra_retrieved if r["predicted"] == "CONTRADICTS")
    print(f"\n  guaranteed_contradiction_distractor: {len(contra_retrieved)}/{len(contra_rows)} retrieved, "
          f"{contra_correct} of the retrieved ones correctly classified CONTRADICTS "
          f"({(contra_correct/len(contra_retrieved) if contra_retrieved else 0):.1%} -- this is the "
          f"closed-world evidence for whether open-world 'out-of-manifest CONTRADICTS calls' are "
          f"typically genuine, since these pairs are functionally identical to a validated "
          f"CONTRADICTS construction but deliberately kept outside bucket A's membership set)")

    out = {
        "run_id": run_id,
        "n_pairs": len(manifest),
        "n_documents": len(manifest_doc_ids),
        "candidates_scored_within_benchmark": len(all_candidate_keys_within_benchmark),
        "candidates_matching_a_manifest_pair": len(all_candidate_keys_within_benchmark & manifest_keys),
        "candidates_outside_all_buckets_still_open_world": len(out_of_manifest_within_benchmark),
        "five_way_evaluation": {
            "accuracy": round(accuracy_5way, 4),
            "macro_f1": round(macro_f1, 4),
            "abstention_rate": round(abstention_rate, 4),
            "n_abstained": n_abstained,
            "n_not_retrieved": n_not_retrieved,
            "per_class": per_class_prf1,
            "confusion_matrix": confusion_matrix,
        },
        "closed_world_contradicts_prf1": {
            "precision": p, "recall": rec, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "gold_n": n_gold_contradicts,
            "false_positives_by_bucket": dict(fp_by_bucket),
        },
        "guaranteed_neutral_distractor": {
            "n": len(neutral_rows), "n_retrieved": len(neutral_retrieved),
            "n_misclassified_contradicts": neutral_false_contradicts,
            "false_contradicts_rate_given_retrieved": round(
                neutral_false_contradicts / len(neutral_retrieved), 4
            ) if neutral_retrieved else None,
        },
        "guaranteed_contradiction_distractor": {
            "n": len(contra_rows), "n_retrieved": len(contra_retrieved),
            "n_correctly_classified": contra_correct,
            "accuracy_given_retrieved": round(
                contra_correct / len(contra_retrieved), 4
            ) if contra_retrieved else None,
        },
        "per_bucket_summary": {
            bucket: {
                "n": len(rs),
                "n_retrieved": sum(1 for r in rs if r["retrieved"]),
                "n_correct": sum(1 for r in rs if r["correct"]),
            }
            for bucket, rs in by_bucket.items()
        },
        "rows": rows,
    }
    out_path = ROOT / "evaluation" / "closed_world" / "v1" / "results.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1])
