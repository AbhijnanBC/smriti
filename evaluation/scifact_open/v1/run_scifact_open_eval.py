"""
run_scifact_open_eval.py -- zero-shot transfer evaluation of SMRITI's
relationship resolver against SciFact-Open (P0-9, "PLEASE FIX AND SAVE
ME" review round).

Same methodology as evaluation/fever/v1/run_fever_eval.py and
evaluation/scifact/v1/run_scifact_eval.py: each (evidence, claim) pair
goes directly to the same bidirectional NLI cross-encoder and the same
RelationshipResolver, unmodified. Results are reported per bucket
(genuine_evidence vs. unverified_random_distractor) because the two
buckets carry different evidentiary weight -- see build_sample.py's
docstring for the honesty caveat on the distractor bucket's label.

Run with:
    poetry run python evaluation/scifact_open/v1/download_scifact_open.py  # once
    poetry run python evaluation/scifact_open/v1/build_sample.py           # once
    poetry run python evaluation/scifact_open/v1/run_scifact_open_eval.py
"""
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from smriti.core.config import get_config  # noqa: E402
from smriti.core.models import (  # noqa: E402
    CandidatePair, RelationshipEvidence, InferenceMetadata,
    LifecycleStage, RelationshipType, ResolutionStatus,
)
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator  # noqa: E402
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy  # noqa: E402

SAMPLE_PATH = ROOT / "evaluation" / "scifact_open" / "v1" / "sample.json"
RESULTS_PATH = ROOT / "evaluation" / "scifact_open" / "v1" / "results.json"

SMRITI_TO_SCIFACT = {
    RelationshipType.SUPPORTS: "SUPPORT",
    RelationshipType.REFINES: "SUPPORT",
    RelationshipType.EQUIVALENT: "SUPPORT",
    RelationshipType.CONTRADICTS: "CONTRADICT",
    RelationshipType.NEUTRAL: "NEI",
}
LABELS = ["SUPPORT", "CONTRADICT", "NEI"]


def decision_to_label(status, relation_type) -> str:
    if status == ResolutionStatus.ABSTAINED:
        return "NEI"
    return SMRITI_TO_SCIFACT[relation_type]


def prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def main():
    get_config(env="dev")
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(sample)} SciFact-Open pairs")

    nli_gen = NLIEvidenceGenerator()
    resolver = RelationshipResolver(policy=ResolverPolicy.from_config())
    print(f"NLI model: {nli_gen._model_name}  device: {nli_gen._device}")

    batch_size = nli_gen._batch_size
    t0 = time.monotonic()
    rows = []
    for batch_start in range(0, len(sample), batch_size):
        batch = sample[batch_start: batch_start + batch_size]
        text_pairs_ab = [(r["evidence_text"], r["claim"]) for r in batch]
        text_pairs_ba = [(r["claim"], r["evidence_text"]) for r in batch]
        combined = nli_gen._run_nli(text_pairs_ab + text_pairs_ba)
        n = len(batch)
        scores_ab, scores_ba = combined[:n], combined[n:]

        for r, s_ab, s_ba in zip(batch, scores_ab, scores_ba):
            nli_scores_ab = nli_gen._scores_to_nli_scores(s_ab)
            nli_scores_ba = nli_gen._scores_to_nli_scores(s_ba)
            pair = CandidatePair(
                claim_id_a=f"ev_{r['claim_idx']}_{r['bucket']}",
                claim_id_b=f"cl_{r['claim_idx']}_{r['bucket']}",
                cosine_similarity=1.0, candidate_rank=1,
            )
            evidence = RelationshipEvidence(
                pair=pair, cosine_similarity=1.0,
                nli_scores=nli_scores_ab, nli_scores_b_to_a=nli_scores_ba,
                calibrated_confidence=nli_scores_ab.raw_confidence,
                calibrated_confidence_b_to_a=nli_scores_ba.raw_confidence,
                inference_metadata=InferenceMetadata(model_name=nli_gen._model_name),
                lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
            )
            decision = resolver.resolve_as_decision(evidence)
            predicted = decision_to_label(decision.status, decision.relation_type)
            rows.append({
                "claim_idx": r["claim_idx"],
                "bucket": r["bucket"],
                "gold_label": r["gold_label"],
                "smriti_status": decision.status.value,
                "smriti_relation_type": decision.relation_type.value if decision.relation_type else None,
                "predicted_label": predicted,
                "correct": predicted == r["gold_label"],
            })
        print(f"  ...{batch_start + n}/{len(sample)} scored "
              f"({time.monotonic() - t0:.1f}s elapsed)", flush=True)

    elapsed = time.monotonic() - t0
    print(f"\nScored {len(rows)} pairs in {elapsed:.1f}s")

    # ── Overall + per-bucket summary ────────────────────────────────────
    by_bucket = defaultdict(list)
    for r in rows:
        by_bucket[r["bucket"]].append(r)

    print("\nPer-bucket summary:")
    bucket_summary = {}
    for bucket, rs in by_bucket.items():
        correct = sum(1 for r in rs if r["correct"])
        bucket_summary[bucket] = {"n": len(rs), "n_correct": correct, "accuracy": round(correct / len(rs), 4)}
        print(f"  {bucket:<30} n={len(rs):>4}  accuracy={correct/len(rs):.1%}")

    # ── Genuine-evidence bucket: real 2-way SUPPORT/CONTRADICT PRF1
    #    (this bucket has no NEI examples -- SciFact-Open's "test" config
    #    only contains verified positive pairs) ─────────────────────────
    genuine = by_bucket["genuine_evidence"]
    per_class = {}
    for lbl in ["SUPPORT", "CONTRADICT"]:
        tp = sum(1 for r in genuine if r["gold_label"] == lbl and r["predicted_label"] == lbl)
        fp = sum(1 for r in genuine if r["gold_label"] != lbl and r["predicted_label"] == lbl)
        fn = sum(1 for r in genuine if r["gold_label"] == lbl and r["predicted_label"] != lbl)
        p, rec, f1 = prf1(tp, fp, fn)
        support = sum(1 for r in genuine if r["gold_label"] == lbl)
        per_class[lbl] = {"precision": p, "recall": rec, "f1": f1, "support": support, "tp": tp, "fp": fp, "fn": fn}
        print(f"  genuine_evidence/{lbl:<12} P={p:.1%}  R={rec:.1%}  F1={f1:.1%}  support={support}")

    # ── Distractor bucket: how often does SMRITI correctly call NEI
    #    (not SUPPORT/CONTRADICT) on a real, likely-unrelated abstract? ──
    distractor = by_bucket["unverified_random_distractor"]
    distractor_correct = sum(1 for r in distractor if r["predicted_label"] == "NEI")
    distractor_false_support = sum(1 for r in distractor if r["predicted_label"] == "SUPPORT")
    distractor_false_contradict = sum(1 for r in distractor if r["predicted_label"] == "CONTRADICT")
    print(f"\n  unverified_random_distractor: {distractor_correct}/{len(distractor)} correctly NEI, "
          f"{distractor_false_support} false SUPPORT, {distractor_false_contradict} false CONTRADICT")

    native_breakdown = Counter(
        (r["bucket"], r["gold_label"], r["smriti_status"], r["smriti_relation_type"]) for r in rows
    )

    out = {
        "source": "umbc-scify/scifact-open (test config + a 2000-doc sample of the distractors config)",
        "n_pairs": len(rows),
        "bucket_summary": bucket_summary,
        "genuine_evidence_per_class_prf1": per_class,
        "distractor_bucket": {
            "n": len(distractor),
            "n_correctly_nei": distractor_correct,
            "n_false_support": distractor_false_support,
            "n_false_contradict": distractor_false_contradict,
            "false_contradiction_rate": round(distractor_false_contradict / len(distractor), 4),
        },
        "native_breakdown": {f"{b}|{g}|{s}|{t}": c for (b, g, s, t), c in native_breakdown.items()},
        "elapsed_seconds": elapsed,
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
