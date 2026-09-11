"""
error_taxonomy.py -- REFINES/CONTRADICTS error taxonomy on real-corpus
misses (P1-11, "FINAL REVIEW" round).

The review's ask (section 23 for REFINES, section 43 for CONTRADICTS):
rather than reporting a single collapsed recall number for a real-corpus
relation type and guessing at why it is low, categorize every MISS (a
gold-agreed pair the resolver did not predict as that relation) into a
specific failure-mode bucket, then count. This tells you whether the
bottleneck is retrieval, NLI, a specific structural mismatch, or claim
construction -- rather than leaving it as one undifferentiated number.

Categories, per the review:
    REFINES:     R1 numeric, R2 geographic, R3 temporal, R4 population,
                 R5 condition, R6 causal-mechanism, R7 qualification
                 (specificity-type missed), R8 NLI failed to establish
                 one-way entailment, R9 segmentation/claim-construction
                 error, R10 retrieval miss.
    CONTRADICTS: lexical polarity, numeric, temporal, scope, negation,
                 causal, retrieval miss, NLI miss.

Method: every miss below is a pair that already has real, cached
bidirectional NLI scores (it reached NLI scoring; see
rederive_relationship_answer_key.py) and real claim text (from the
relevant run's Phase 4 dataset), so classification is evidence-based,
not guessed:
    - "malformed claim" (truncated/list-heading fragment, e.g. ends in
      "and ." or ":") is detected by a documented regex over the claim
      text itself -- these fall outside the review's own taxonomy list
      for CONTRADICTS (which has no "segmentation" bucket) and are
      reported separately rather than force-fit into R9's REFINES-only
      slot or a CONTRADICTS category that doesn't exist.
    - "NLI miss" / "R8" is assigned when BOTH directions' relevant NLI
      score (entailment for REFINES, contradiction for CONTRADICTS) are
      low (< 0.5) on a well-formed pair -- the model simply never
      produced the signal the resolver needed, regardless of what kind
      of specificity/contradiction the gold label represents.
    - Any pair with a HIGH same-direction score that nonetheless was not
      classified as the gold relation is flagged for manual review
      rather than silently bucketed as "NLI miss" (that would misreport
      a routing/heuristic-ordering failure as a model failure) -- see
      MANUAL_OVERRIDES below, each with an inline rationale.
    - R1-R7 (REFINES specificity subtypes) and CONTRADICTS's
      lexical-polarity/numeric/temporal/scope/negation/causal
      categories are reserved for a miss where the relevant entailment/
      contradiction score IS actually high (the model correctly
      detected the core relation) but something else -- a specific
      kind of added specificity, or a specific contradiction mechanism
      -- caused the miss. If no miss meets that bar, the count is
      reported as zero, which is itself the finding (see paper
      discussion), not an argument to invent one to fill the bucket.
    - R10 / "retrieval miss": a gold pair with NO cached NLI scores at
      all (never reached NLI scoring) reports separately; none exist in
      the current 228-pair annotated sample by construction (see
      rederive_relationship_answer_key.py's docstring), so this count is
      always 0 here -- retrieval-stage misses on REFINES/CONTRADICTS
      gold pairs are a real, disclosed phenomenon but are outside this
      already-scored sample's population entirely.

Run with: poetry run python evaluation/annotation/error_taxonomy.py
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANNO = ROOT / "evaluation" / "annotation"
OUT_PATH = ANNO / "error_taxonomy_results.json"

_MALFORMED_RE = re.compile(r"(and\s*\.$)|(:$)|([,;]\s*\.$)|(\(\s*$)")

# RECTIFIED (P1-11): pairs where a same-direction score is already high
# but the resolver still did not predict the gold relation are a
# routing/heuristic-ordering issue, not an NLI failure -- reported
# individually with a rationale rather than silently folded into
# "NLI miss."
MANUAL_OVERRIDES = {
    "7d612a447c7d3f07": (
        "both_way_entailment_routes_to_equivalent_first",
        "Both directions show high entailment (A->B=0.951, B->A=0.996): "
        "the resolver's both-way-entailment rule classifies this EQUIVALENT "
        "before the specificity gate that distinguishes REFINES ever runs. "
        "Not a REFINES-specificity-subtype miss (R1-R7) and not an NLI "
        "failure (R8) -- the model succeeded at entailment in both "
        "directions; the classification-priority ordering is what misses "
        "REFINES here.",
    ),
    "3dea3b4ca700893a": (
        "comparative_scope_not_absolute_contradiction",
        "A->B entailment is high (0.736) but the claims compare against a "
        "specific reference point (\"a slow-braised dish\") rather than "
        "making an absolute claim -- closest to a scope-type CONTRADICTS "
        "miss: the comparison's scope, not a lexical/numeric/temporal "
        "marker, is what the resolver's evidence signals do not capture.",
    ),
}


def _load(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_text_map(answer_key, ids):
    source_runs = {answer_key[i]["source_run_id"] for i in ids if "source_run_id" in answer_key[i]}
    claim_text = {}
    for run_id in source_runs:
        p4_path = ROOT / "artifacts" / f"run_{run_id}" / "phase4" / "dataset.json"
        if not p4_path.exists():
            continue
        for c in json.loads(p4_path.read_text(encoding="utf-8")):
            claim_text[c["claim_id"]] = c["text"]
    return claim_text


def _is_malformed(text):
    if text is None:
        return True
    return bool(_MALFORMED_RE.search(text.strip()))


def classify_refines_miss(pair_id, entry, text_a, text_b):
    if pair_id in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[pair_id][0]
    if _is_malformed(text_a) or _is_malformed(text_b):
        return "R9_segmentation_claim_construction_error"
    if entry["nli_entailment_a_to_b"] < 0.5 and entry["nli_entailment_b_to_a"] < 0.5:
        return "R8_nli_failed_one_way_entailment"
    return "unclassified_high_entailment_not_refines"


def classify_contradicts_miss(pair_id, entry, text_a, text_b):
    if pair_id in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[pair_id][0]
    if _is_malformed(text_a) or _is_malformed(text_b):
        return "malformed_claim_not_in_review_taxonomy"
    if entry["nli_contradiction_a_to_b"] < 0.5 and entry["nli_contradiction_b_to_a"] < 0.5:
        return "nli_miss"
    return "unclassified_high_contradiction_not_contradicts"


def main():
    answer_key = _load(ANNO / "rc2_rc3_relationships_answer_key.json")
    pass1 = _load(ANNO / "pass1_relationships.json")
    pass2 = _load(ANNO / "pass2_relationships.json")

    lab1 = {k: v["label"] for k, v in pass1.items()}
    lab2 = {k: v["label"] for k, v in pass2.items()}
    agreed = {
        i: lab1[i] for i in answer_key
        if i in lab1 and i in lab2 and lab1[i] == lab2[i] and lab1[i] != "UNSURE"
    }

    results = {}
    for relation, classify_fn in (("REFINES", classify_refines_miss), ("CONTRADICTS", classify_contradicts_miss)):
        gold_ids = [i for i in agreed if agreed[i] == relation]
        claim_text = _claim_text_map(answer_key, gold_ids)
        taxonomy = {}
        misses_detail = []
        n_hit = 0
        for i in gold_ids:
            entry = answer_key[i]
            pred = entry["predicted_label"].upper()
            if pred == relation:
                n_hit += 1
                continue
            text_a = claim_text.get(entry["claim_id_a"])
            text_b = claim_text.get(entry["claim_id_b"])
            category = classify_fn(i, entry, text_a, text_b)
            taxonomy[category] = taxonomy.get(category, 0) + 1
            misses_detail.append({"id": i, "predicted": pred, "category": category})

        n_total = len(gold_ids)
        n_miss = n_total - n_hit
        results[relation] = {
            "n_gold": n_total,
            "n_hit": n_hit,
            "n_miss": n_miss,
            "recall": round(n_hit / n_total, 4) if n_total else None,
            "taxonomy_counts": taxonomy,
            "manual_override_rationales": {
                pid: rationale for pid, (cat, rationale) in MANUAL_OVERRIDES.items()
                if any(m["id"] == pid for m in misses_detail)
            },
            "misses": misses_detail,
        }

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH}\n")
    for relation, r in results.items():
        print(f"=== {relation}: {r['n_hit']}/{r['n_gold']} recall={r['recall']:.1%} ===")
        for cat, count in sorted(r["taxonomy_counts"].items(), key=lambda kv: -kv[1]):
            print(f"  {cat:<45} {count}")
        print()


if __name__ == "__main__":
    main()
