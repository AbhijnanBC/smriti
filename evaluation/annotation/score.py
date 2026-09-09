"""
Score SMRITI (and the three baselines) against the two independent
LLM-derived annotation passes.

Produces:
  - evaluation/annotation/results_summary.json   (all numbers, machine-readable)
  - prints a human-readable report

Run with: poetry run python evaluation/annotation/score.py
"""
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from smriti.evaluation.statistical.bootstrap import (
    bootstrap_proportion_ci, bootstrap_proportion_ci_clustered,
)

BASE = str(ROOT)
ANNO = os.path.join(BASE, "evaluation", "annotation")
BASELINES = os.path.join(BASE, "evaluation", "baselines")
RUN_ID = "20260909_193441"


def load(name, root=ANNO):
    path = os.path.join(root, name)
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))


def load_claim_document_map(run_id: str = RUN_ID) -> dict:
    """
    RECTIFIED (external review item 40): claims and relationship pairs
    anchored on the same source document are not independent samples --
    a document-level artifact (an unusually rhetorical rogue document, a
    parsing quirk) affects every claim drawn from it together. This map
    (claim_id -> document_id) lets score() resample at the document level
    (cluster/block bootstrap) instead of treating every item as an
    independent draw.
    """
    p4_path = os.path.join(BASE, "artifacts", f"run_{run_id}", "phase4", "dataset.json")
    if not os.path.exists(p4_path):
        return {}
    p4 = json.load(open(p4_path, encoding="utf-8"))
    return {c["claim_id"]: c["document_id"] for c in p4}


def cohen_kappa_categorical(labels_a: dict, labels_b: dict, key_fn=lambda v: v):
    """Cohen's kappa for two raters over the shared id space."""
    ids = sorted(set(labels_a) & set(labels_b))
    if not ids:
        return None, 0
    a = [key_fn(labels_a[i]) for i in ids]
    b = [key_fn(labels_b[i]) for i in ids]
    n = len(ids)
    agree = sum(1 for x, y in zip(a, b) if x == y) / n
    cats = sorted(set(a) | set(b))
    pa = Counter(a)
    pb = Counter(b)
    expected = sum((pa[c] / n) * (pb[c] / n) for c in cats)
    if expected == 1.0:
        return 1.0, n
    kappa = (agree - expected) / (1 - expected)
    return round(kappa, 4), n


def mean_abs_diff_ordinal(vals_a: dict, vals_b: dict):
    ids = sorted(set(vals_a) & set(vals_b))
    diffs = [abs(vals_a[i] - vals_b[i]) for i in ids if vals_a[i] is not None and vals_b[i] is not None]
    if not diffs:
        return None, 0
    return round(sum(diffs) / len(diffs), 4), len(diffs)


def prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def main():
    report = {}
    claim_doc = load_claim_document_map()

    # ── Task 1: claim validity / quality / reliability ──────────────────────
    pass1 = load("pass1_claims.json")
    pass2 = load("pass2_claims.json")
    answer_key = load("rc1_rc4_claims_answer_key.json")

    if pass1 and pass2:
        valid1 = {k: v["valid"] for k, v in pass1.items()}
        valid2 = {k: v["valid"] for k, v in pass2.items()}
        kappa_valid, n_valid = cohen_kappa_categorical(valid1, valid2)

        rel1 = {k: v.get("reliability") for k, v in pass1.items() if v.get("reliability") is not None}
        rel2 = {k: v.get("reliability") for k, v in pass2.items() if v.get("reliability") is not None}
        mad_rel, n_rel = mean_abs_diff_ordinal(rel1, rel2)

        # Adjudicated gold: agree -> that value; disagree on validity -> excluded from precision
        ids = sorted(set(pass1) & set(pass2))
        agreed_valid = {i: valid1[i] for i in ids if valid1[i] == valid2[i]}
        disputed = [i for i in ids if valid1[i] != valid2[i]]

        n_extracted = len(answer_key) if answer_key else len(ids)
        n_valid_agreed = sum(1 for v in agreed_valid.values() if v)
        extraction_precision = round(n_valid_agreed / len(agreed_valid), 4) if agreed_valid else None
        # P1-11: bootstrap 95% CI on precision -- the real source of
        # uncertainty here is which claims happened to be sampled, not
        # run-to-run noise, so a percentile bootstrap over per-item outcomes
        # is the right tool (see evaluation/statistical/bootstrap.py).
        precision_ci = (
            bootstrap_proportion_ci(list(agreed_valid.values())) if agreed_valid else None
        )
        # Cluster bootstrap: resample by source document, not by claim, since
        # claims from the same document are not independent (item 40).
        precision_ci_clustered = None
        if agreed_valid and claim_doc:
            clustered_ids = [claim_doc.get(i, i) for i in agreed_valid]
            precision_ci_clustered = bootstrap_proportion_ci_clustered(
                list(agreed_valid.values()), clustered_ids,
            )

        # Fraction flagged as pure metadata noise (a concrete, quotable failure mode)
        n_metadata = sum(1 for k, v in (answer_key or {}).items() if v.get("is_metadata_line"))

        report["claim_annotation"] = {
            "n_sampled": len(ids),
            "n_disputed_validity": len(disputed),
            "inter_pass_kappa_validity": kappa_valid,
            "inter_pass_mean_abs_diff_reliability_1to5": mad_rel,
            "extraction_precision_on_agreed_subset": extraction_precision,
            "extraction_precision_95ci": vars(precision_ci) if precision_ci else None,
            "extraction_precision_95ci_clustered_by_document": (
                vars(precision_ci_clustered) if precision_ci_clustered else None
            ),
            "n_agreed": len(agreed_valid),
            "n_metadata_noise_in_full_phase4_output": n_metadata,
            "n_metadata_noise_total_phase4_claims": len(answer_key) if answer_key else None,
        }

    # ── Task 2: relationship classification ──────────────────────────────
    rpass1 = load("pass1_relationships.json")
    rpass2 = load("pass2_relationships.json")
    ranswer = load("rc2_rc3_relationships_answer_key.json")
    rblind = load("rc2_rc3_relationships_blind.json")

    if rpass1 and rpass2 and ranswer:
        lab1 = {k: v["label"].upper() for k, v in rpass1.items()}
        lab2 = {k: v["label"].upper() for k, v in rpass2.items()}
        kappa_rel, n_rel_pairs = cohen_kappa_categorical(lab1, lab2)

        ids = sorted(set(lab1) & set(lab2))
        agreed = {i: lab1[i] for i in ids if lab1[i] == lab2[i] and lab1[i] != "UNSURE"}
        disputed_rel = [i for i in ids if lab1[i] != lab2[i]]

        # SMRITI predictions on the agreed-gold subset
        smriti_pred = {k: v["predicted_label"].upper() for k, v in ranswer.items()}
        labels = ["SUPPORTS", "CONTRADICTS", "REFINES", "NEUTRAL"]
        per_class = {}
        for lbl in labels:
            tp = sum(1 for i in agreed if agreed[i] == lbl and smriti_pred.get(i) == lbl)
            fp = sum(1 for i in agreed if agreed[i] != lbl and smriti_pred.get(i) == lbl)
            fn = sum(1 for i in agreed if agreed[i] == lbl and smriti_pred.get(i) != lbl)
            p, r, f1 = prf1(tp, fp, fn)
            per_class[lbl] = {"precision": p, "recall": r, "f1": f1, "support": sum(1 for i in agreed if agreed[i] == lbl)}
            # P1-11: bootstrap 95% CI on precision for this class, over the
            # per-item correctness outcomes among items SMRITI predicted as lbl.
            predicted_as_lbl_ids = [i for i in agreed if smriti_pred.get(i) == lbl]
            predicted_as_lbl_outcomes = [agreed[i] == lbl for i in predicted_as_lbl_ids]
            if predicted_as_lbl_outcomes:
                per_class[lbl]["precision_95ci"] = vars(bootstrap_proportion_ci(predicted_as_lbl_outcomes))
                # Cluster bootstrap (item 40): resample by the source
                # document of claim_id_a, since multiple relationship pairs
                # anchored on the same (often adversarial) document are not
                # independent observations.
                if claim_doc:
                    pair_cluster_ids = [
                        claim_doc.get(ranswer.get(i, {}).get("claim_id_a"), i)
                        for i in predicted_as_lbl_ids
                    ]
                    per_class[lbl]["precision_95ci_clustered_by_document"] = vars(
                        bootstrap_proportion_ci_clustered(predicted_as_lbl_outcomes, pair_cluster_ids)
                    )

        # RC3/RC6-specific: recall on the deliberate hard-contradiction target pairs
        target_ids = [k for k, v in ranswer.items() if v.get("is_known_hard_contradiction_pair")]
        target_in_agreed = [i for i in target_ids if i in agreed]
        target_recall = None
        if target_in_agreed:
            correct = sum(1 for i in target_in_agreed if smriti_pred.get(i) == "CONTRADICTS")
            target_recall = round(correct / len(target_in_agreed), 4)

        report["relationship_annotation"] = {
            "n_sampled": len(ids),
            "n_disputed": len(disputed_rel),
            "inter_pass_kappa": kappa_rel,
            "n_agreed_excl_unsure": len(agreed),
            "smriti_per_class_prf1": per_class,
            "smriti_recall_on_known_hard_contradiction_pairs": target_recall,
            "n_known_hard_contradiction_pairs_in_agreed_gold": len(target_in_agreed),
        }

        # ── Baseline comparison on the SAME agreed-gold pairs (by claim ids) ──
        blind_by_id = {b["relationship_id"]: b for b in rblind} if rblind else {}

        def load_baseline_lookup(fname):
            data = load(fname, root=BASELINES)
            if not data:
                return None
            # baseline files key by claim_id_a|claim_id_b pair; build a lookup
            lookup = {}
            preds = data if isinstance(data, list) else data.get("predictions", [])
            for p in preds:
                key = tuple(sorted([p.get("claim_id_a", ""), p.get("claim_id_b", "")]))
                label = p.get("relationship_type", p.get("predicted_label", p.get("label", "NEUTRAL")))
                lookup[key] = label.upper()
            return lookup

        for bname, fname in [("tfidf", "tfidf_relationship_predictions.json"),
                              ("sbert", "sbert_relationship_predictions.json")]:
            lookup = load_baseline_lookup(fname)
            if lookup is None:
                continue
            per_class_baseline = {}
            for lbl in labels:
                tp = fp = fn = 0
                for rid in agreed:
                    item = blind_by_id.get(rid)
                    if not item:
                        continue
                    key = tuple(sorted([item.get("relationship_id", rid)]))  # fallback
                    # blind items don't carry claim_ids directly; matched via answer_key's pair if present
                    pred = "NEUTRAL"  # baseline default when pair not surfaced as a candidate at all
                    ck = ranswer.get(rid, {})
                    cid_a, cid_b = ck.get("claim_id_a"), ck.get("claim_id_b")
                    if cid_a and cid_b:
                        pair_key = tuple(sorted([cid_a, cid_b]))
                        if pair_key in lookup:
                            pred = lookup[pair_key]
                    gold = agreed[rid]
                    if gold == lbl and pred == lbl:
                        tp += 1
                    elif gold != lbl and pred == lbl:
                        fp += 1
                    elif gold == lbl and pred != lbl:
                        fn += 1
                p, r, f1 = prf1(tp, fp, fn)
                per_class_baseline[lbl] = {"precision": p, "recall": r, "f1": f1}
            report.setdefault("baseline_relationship_prf1", {})[bname] = per_class_baseline

    os.makedirs(ANNO, exist_ok=True)
    out_path = os.path.join(ANNO, "results_summary.json")
    json.dump(report, open(out_path, "w", encoding="utf-8"), indent=2)
    print(json.dumps(report, indent=2))
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
