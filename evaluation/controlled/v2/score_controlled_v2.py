"""
score_controlled_v2.py — Score SMRITI against SMRITI-Controlled-v2's
gold manifest, sanitized and re-scoped per the external "reality check"
review.

RECTIFIED relative to evaluation/controlled/score_controlled.py:

  P0-8 three aggregates, not one ambiguous "overall": this script reports
    (A) core semantic relations (CONTRADICTS/SUPPORTS/REFINES/EQUIVALENT/
    easy-NEUTRAL), (B) the challenge suite (hard-NEUTRAL subtypes +
    ambiguous/abstention), and (C) the full benchmark (A + B). Macro-F1
    and micro-F1 are reported for (A) instead of a single pooled
    recall/accuracy pair that conflated retrieval and classification.

  P0-9 candidate-level precision/recall, not just gold-pair retrieval
    recall: this requires the run to have been produced with
    `--env eval` (config/eval.yaml, skip_unknown_relationships=false,
    skip_neutral_relationships=false) so Phase 6's output contains EVERY
    NLI-scored candidate pair, not only the ones that survive the
    production skip-filters. If the run was NOT produced this way, the
    candidate-precision section is reported as null with an explicit
    reason rather than a silently wrong number.

  P1 template-family-clustered bootstrap: 707+ generated pairs are not
    707 independent linguistic samples -- many share a template family.
    Bootstrap CIs here resample by template_family_id, not by pair, as
    the primary CI; the per-pair CI is also reported, labeled as an
    optimistic lower bound on the true uncertainty.

  dev/test split: every metric is reported separately for dev and test.
    The frozen test set (config/eval.yaml is unaffected by this; the
    split lives in the manifest itself, assigned by template family) is
    the number that should be quoted as "the" result; dev is for
    threshold-tuning and is reported for transparency, not as the
    headline number.

  Selective prediction (P0-12): the ambiguous_abstention category is
    reported as abstention rate / coverage, never as "classification
    accuracy" against a semantic label -- UNKNOWN is a resolution
    status, not a competing relation type, and pretending otherwise is
    exactly the P0-4 confusion this rewrite avoids in its own reporting
    even where the resolver's own type system has not yet been split.

Run with:
    poetry run python scripts/run_vault.py controlled_v2 --start 1 --stop 6 --env eval
    poetry run python evaluation/controlled/v2/score_controlled_v2.py <run_id>
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from smriti.evaluation.statistical.bootstrap import bootstrap_proportion_ci, bootstrap_proportion_ci_clustered

BASE = str(ROOT)
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"

CORE_CATEGORIES = {"direct", "negated", "numeric", "temporal", "entity", "attribute", "supports", "refinement", "equivalent", "neutral"}
CONTRADICTS_CATEGORIES = {"direct", "negated", "numeric", "temporal", "entity", "attribute"}
CHALLENGE_CATEGORIES = {
    "neutral_hard_same_topic", "neutral_hard_lexical_collision",
    "neutral_hard_multi_attribute", "neutral_hard_adjacent_non_conflicting",
    "ambiguous_abstention",
}
LABELS = ["CONTRADICTS", "SUPPORTS", "REFINES", "EQUIVALENT", "NEUTRAL"]


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
    run_manifest_path = Path(art) / "run_manifest.json"

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}

    predicted_by_pair = {}
    for r in p6:
        a, b = r["claim_id_a"], r["claim_id_b"]
        key = frozenset([doc_of_claim.get(a), doc_of_claim.get(b)])
        predicted_by_pair[key] = r["relationship_type"].upper()

    gold_pair_keys = {frozenset([p["doc_a"], p["doc_b"]]) for p in manifest}

    # ── Row-level scoring against the manifest (same as v1's approach) ──
    rows = []
    for pair in manifest:
        key = frozenset([pair["doc_a"], pair["doc_b"]])
        # RECTIFIED (P0-3, "PLEASE FIX AND SAVE ME" review round): the
        # manifest no longer stores "gold_relationship": "UNKNOWN" for
        # ambiguous pairs -- expected_status is the resolution-status
        # field (RESOLVED/ABSTAINED), and expected_relation is the actual
        # semantic label, None iff expected_status is ABSTAINED. `gold`
        # below is kept as the local variable name (still means "the
        # expected relation label for RESOLVED pairs") to minimize churn
        # in the rest of this function.
        gold = pair["expected_relation"]
        is_abstention_pair = pair["expected_status"] == "ABSTAINED"
        predicted = predicted_by_pair.get(key)
        retrieved = predicted is not None
        # Ambiguous/abstention pairs are NOT scored as "predicted == UNKNOWN"
        # (P0-4/P0-12): a resolver that commits to some other label instead
        # of abstaining is not "wrong" in the classification sense, it is
        # "did not abstain when it should have" -- a selective-prediction
        # failure, scored separately below, not folded into correct/incorrect.
        correct = retrieved and predicted == gold if not is_abstention_pair else None
        abstained = retrieved and predicted == "UNKNOWN" if is_abstention_pair else None
        rows.append({
            "pair": f"{pair['doc_a']}/{pair['doc_b']}",
            "gold": gold, "category": pair["category"],
            "template_family_id": pair.get("template_family_id"),
            "split": pair.get("split", "dev"),
            "retrieved": retrieved, "predicted": predicted,
            "correct": correct, "abstained": abstained,
            "is_challenge": pair["category"] in CHALLENGE_CATEGORIES,
            "is_abstention_pair": is_abstention_pair,
        })

    def summarize(rows_subset, label):
        print(f"\n=== {label} (n={len(rows_subset)}) ===")
        per_cat = defaultdict(lambda: {"retrieved": 0, "total": 0, "correct": 0})
        for r in rows_subset:
            c = per_cat[r["category"]]
            c["total"] += 1
            if r["retrieved"]:
                c["retrieved"] += 1
            if r["correct"]:
                c["correct"] += 1
        for cat, d in sorted(per_cat.items()):
            recall = d["retrieved"] / d["total"] if d["total"] else 0.0
            acc = d["correct"] / d["retrieved"] if d["retrieved"] else 0.0
            print(f"  {cat:<38} n={d['total']:>4}  retrieval_recall={recall:>6.1%}  class_acc_given_retrieved={acc:>6.1%}")
        return per_cat

    # ── (A) Core semantic relations: macro/micro F1 ─────────────────────
    def core_prf1(rows_subset):
        core_rows = [r for r in rows_subset if r["category"] in CORE_CATEGORIES]
        per_class = {}
        for lbl in LABELS:
            tp = sum(1 for r in core_rows if r["gold"] == lbl and r["predicted"] == lbl)
            fp = sum(1 for r in core_rows if r["gold"] != lbl and r["predicted"] == lbl)
            fn = sum(1 for r in core_rows if r["gold"] == lbl and r["predicted"] != lbl)
            p, r_, f1 = prf1(tp, fp, fn)
            per_class[lbl] = {"precision": p, "recall": r_, "f1": f1, "support": sum(1 for r in core_rows if r["gold"] == lbl)}
        macro_f1 = round(sum(c["f1"] for c in per_class.values()) / len(per_class), 4)
        total_tp = sum(1 for r in core_rows if r["predicted"] == r["gold"])
        micro_f1 = round(total_tp / len(core_rows), 4) if core_rows else 0.0  # micro-F1 == accuracy when every item has exactly one gold label
        retrieval_recall = sum(1 for r in core_rows if r["retrieved"]) / len(core_rows) if core_rows else 0.0
        return {
            "n": len(core_rows), "per_class_prf1": per_class,
            "macro_f1": macro_f1, "micro_f1_accuracy": micro_f1,
            "retrieval_recall": round(retrieval_recall, 4),
        }

    # ── (B) Challenge suite: hard-neutral (still binary correct/incorrect
    #    against NEUTRAL) + ambiguous/abstention (selective prediction) ──
    def challenge_summary(rows_subset):
        hard_neutral_rows = [r for r in rows_subset if r["category"] in CHALLENGE_CATEGORIES and not r["is_abstention_pair"]]
        abstention_rows = [r for r in rows_subset if r["is_abstention_pair"]]
        hn_by_cat = defaultdict(lambda: {"retrieved": 0, "total": 0, "correct": 0})
        for r in hard_neutral_rows:
            d = hn_by_cat[r["category"]]
            d["total"] += 1
            if r["retrieved"]:
                d["retrieved"] += 1
            if r["correct"]:
                d["correct"] += 1

        n_abstention = len(abstention_rows)
        n_retrieved = sum(1 for r in abstention_rows if r["retrieved"])
        n_abstained = sum(1 for r in abstention_rows if r["abstained"])
        # Selective-prediction framing (P0-12): coverage = fraction of
        # retrieved ambiguous candidates the resolver COMMITTED a label on
        # (did not abstain); abstention_rate = the complement. This is
        # deliberately NOT called "accuracy" -- there is no single correct
        # label for a pair constructed to be genuinely ambiguous, only a
        # correct DECISION about whether to commit at all.
        coverage = round((n_retrieved - n_abstained) / n_retrieved, 4) if n_retrieved else None
        abstention_rate = round(n_abstained / n_retrieved, 4) if n_retrieved else None
        committed_label_counts = defaultdict(int)
        for r in abstention_rows:
            if r["retrieved"] and not r["abstained"]:
                committed_label_counts[r["predicted"]] += 1
        return {
            "hard_neutral_by_category": {k: dict(v) for k, v in hn_by_cat.items()},
            "ambiguous_abstention": {
                "n_total": n_abstention, "n_retrieved": n_retrieved,
                "n_abstained": n_abstained,
                "coverage_selective_prediction": coverage,
                "abstention_rate": abstention_rate,
                "committed_label_distribution_when_not_abstained": dict(committed_label_counts),
            },
        }

    dev_rows = [r for r in rows if r["split"] == "dev"]
    test_rows = [r for r in rows if r["split"] == "test"]

    print(f"Manifest: {len(manifest)} pairs ({len(dev_rows)} dev / {len(test_rows)} test)")
    summarize(dev_rows, "DEV split, all categories")
    summarize(test_rows, "TEST split, all categories (frozen)")

    core_dev = core_prf1(dev_rows)
    core_test = core_prf1(test_rows)
    core_full = core_prf1(rows)
    print(f"\n(A) Core semantic relations -- TEST: macro-F1={core_test['macro_f1']:.3f} "
          f"micro-F1/accuracy={core_test['micro_f1_accuracy']:.3f} retrieval_recall={core_test['retrieval_recall']:.3f} (n={core_test['n']})")
    print(f"(A) Core semantic relations -- DEV:  macro-F1={core_dev['macro_f1']:.3f} "
          f"micro-F1/accuracy={core_dev['micro_f1_accuracy']:.3f} retrieval_recall={core_dev['retrieval_recall']:.3f} (n={core_dev['n']})")

    challenge_dev = challenge_summary(dev_rows)
    challenge_test = challenge_summary(test_rows)
    challenge_full = challenge_summary(rows)
    ab = challenge_test["ambiguous_abstention"]
    print(f"\n(B) Challenge suite -- TEST ambiguous/abstention: "
          f"{ab['n_retrieved']}/{ab['n_total']} retrieved, "
          f"abstained {ab['n_abstained']}/{ab['n_retrieved'] or 1} "
          f"(abstention_rate={ab['abstention_rate']})")

    # ── P0-9: candidate-level precision/recall (requires --env eval) ────
    candidate_metrics = None
    eval_env_used = False
    if run_manifest_path.exists():
        rm = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        # run_manifest.json doesn't record env directly; infer from whether
        # NEUTRAL relationships are present in phase6 output at all, which
        # is the observable signature of skip_neutral_relationships=false.
    neutral_present = any(r["relationship_type"].lower() == "neutral" for r in p6)
    eval_env_used = neutral_present
    if not eval_env_used:
        candidate_metrics = {
            "available": False,
            "reason": (
                "This run's Phase 6 output contains no NEUTRAL relationships, "
                "which is the observable signature of a production-profile "
                "run (skip_neutral_relationships=true). Candidate-level "
                "precision/recall requires every NLI-scored candidate to be "
                "retained -- re-run with "
                "'scripts/run_vault.py controlled_v2 --env eval'."
            ),
        }
    else:
        total_candidates = len(p6)
        gold_candidates = sum(1 for r in p6 if frozenset([doc_of_claim.get(r["claim_id_a"]), doc_of_claim.get(r["claim_id_b"])]) in gold_pair_keys)
        non_gold_candidates = total_candidates - gold_candidates
        n_claims = len(p4)
        # RECTIFIED (external "reality check" review round 3, P0-8
        # "candidate 'precision' is not actually conventional precision"):
        # a candidate pair outside the manifest is NOT automatically a
        # false positive -- SMRITI-Controlled-v2 is an OPEN-world corpus
        # (it asserts nothing about pairs it never constructed), so a
        # "non-manifest CONTRADICTS" may be a true contradiction the
        # corpus simply never labeled, not a resolver error. Renamed
        # throughout from candidate_precision/false_contradicts to
        # intended_pair_coverage/out_of_manifest_contradicts, and the
        # note below states the open-world caveat explicitly rather than
        # implying a closed-world ground truth this corpus does not have.
        out_of_manifest_contradicts = sum(
            1 for r in p6
            if r["relationship_type"].lower() == "contradicts"
            and frozenset([doc_of_claim.get(r["claim_id_a"]), doc_of_claim.get(r["claim_id_b"])]) not in gold_pair_keys
        )
        total_contradicts_calls = sum(1 for r in p6 if r["relationship_type"].lower() == "contradicts")
        candidate_metrics = {
            "available": True,
            "total_candidates_scored_by_nli": total_candidates,
            "gold_candidates_among_them": gold_candidates,
            "non_gold_candidates_among_them": non_gold_candidates,
            "intended_pair_coverage": round(gold_candidates / total_candidates, 4) if total_candidates else None,
            "n_claims": n_claims,
            "candidates_per_claim": round(total_candidates / n_claims, 3) if n_claims else None,
            "gold_pairs_in_manifest": len(gold_pair_keys),
            "out_of_manifest_contradicts_count": out_of_manifest_contradicts,
            "out_of_manifest_contradicts_rate_over_all_contradicts_calls": (
                round(out_of_manifest_contradicts / total_contradicts_calls, 4) if total_contradicts_calls else None
            ),
            "note": (
                "OPEN-WORLD CORPUS, NOT CLOSED-WORLD: 'gold' here means the "
                "candidate pair corresponds to some pair the corpus "
                "deliberately constructed (any category, any gold label), "
                "not that the predicted label matched -- this is a "
                "retrieval-volume measure (how much of what the NLI stage "
                "scores was ever intended to be tested), separate from the "
                "per-pair classification correctness reported above. "
                "'intended_pair_coverage' is NOT conventional precision: a "
                "candidate outside the manifest ('out of manifest') is NOT "
                "automatically a false positive -- it may be a genuine, "
                "true contradiction the corpus simply never constructed or "
                "labeled (this corpus asserts nothing about pairs it did "
                "not build). 'out_of_manifest_contradicts_count' should be "
                "read as exactly that -- a count of out-of-manifest "
                "CONTRADICTS calls -- not as a false-positive count, "
                "pending a genuinely closed-world candidate benchmark "
                "(explicit guaranteed-neutral/guaranteed-contradiction "
                "distractor pairs) that would make a real error rate "
                "measurable."
            ),
        }

    print(f"\n(P0-9) Candidate-level metrics: {'available' if candidate_metrics['available'] else 'NOT AVAILABLE (' + candidate_metrics['reason'] + ')'}")
    if candidate_metrics["available"]:
        print(f"  total candidates scored: {candidate_metrics['total_candidates_scored_by_nli']}")
        print(f"  intended (manifest) candidates among them: {candidate_metrics['gold_candidates_among_them']}")
        print(f"  intended-pair coverage (manifest/total): {candidate_metrics['intended_pair_coverage']:.1%}")
        print(f"  out-of-manifest CONTRADICTS calls (NOT necessarily false positives -- see note): {candidate_metrics['out_of_manifest_contradicts_count']}")

    # ── Template-family-clustered bootstrap (P1) ─────────────────────────
    def clustered_ci_for(rows_subset, outcome_key, filter_fn=None):
        filtered = [r for r in rows_subset if filter_fn(r)] if filter_fn else rows_subset
        outcomes = [bool(r[outcome_key]) for r in filtered if r[outcome_key] is not None]
        clusters = [r["template_family_id"] for r in filtered if r[outcome_key] is not None]
        if not outcomes:
            return None
        per_pair = bootstrap_proportion_ci(outcomes)
        per_family = bootstrap_proportion_ci_clustered(outcomes, clusters)
        return {"per_pair_ci": vars(per_pair), "per_template_family_ci": vars(per_family)}

    core_test_rows = [r for r in test_rows if r["category"] in CORE_CATEGORIES]
    retrieval_ci = clustered_ci_for(core_test_rows, "retrieved")
    classification_ci = clustered_ci_for(core_test_rows, "correct", filter_fn=lambda r: r["retrieved"])
    if retrieval_ci:
        pf, tf = retrieval_ci["per_pair_ci"], retrieval_ci["per_template_family_ci"]
        print(f"\nCore retrieval recall (TEST) 95% CI: per-pair [{pf['ci_lower']:.1%}, {pf['ci_upper']:.1%}] "
              f"(n={pf['n_items']}) vs. per-template-family (real uncertainty) [{tf['ci_lower']:.1%}, {tf['ci_upper']:.1%}]")

    out = {
        "run_id": run_id,
        "eval_env_used": eval_env_used,
        "n_dev": len(dev_rows), "n_test": len(test_rows),
        "core_semantic_relations": {"dev": core_dev, "test": core_test, "full": core_full},
        "challenge_suite": {"dev": challenge_dev, "test": challenge_test, "full": challenge_full},
        "candidate_metrics": candidate_metrics,
        "template_family_clustered_ci": {
            "core_retrieval_recall_test": retrieval_ci,
            "core_classification_accuracy_test": classification_ci,
        },
        "rows": rows,
    }
    out_path = ROOT / "evaluation" / "controlled" / "v2" / "results.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    run_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_id:
        raise SystemExit("Usage: score_controlled_v2.py <run_id>")
    main(run_id)
