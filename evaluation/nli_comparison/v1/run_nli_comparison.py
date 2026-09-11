"""
run_nli_comparison.py -- NLI-model comparison matrix (P1-9, "PLEASE FIX
AND SAVE ME" review round).

The current real-corpus failure (SMRITI-Reference's low CONTRADICTS
precision and widespread under-commitment, and the same pattern
reproduced on FEVER/SciFact in this paper) suggests model-task mismatch,
but nothing in this paper so far isolates whether SMRITI's own
architecture or the specific NLI cross-encoder it wraps is responsible.
This script re-scores the SAME frozen FEVER sample (900 pairs,
\S\ref{sec:fever}) with a second, larger NLI cross-encoder from the same
model family (cross-encoder/nli-deberta-v3-base, ~184M parameters, vs.\
the production small variant's ~140M) through the exact same resolver
and label-collapse logic, so any difference in outcome is attributable
to the base NLI model, not to a different architecture or evaluation
methodology.

This is a genuine but SCOPED instance of the review's fuller ask
(stronger NLI model vs.\ stance model vs.\ LLM classifier, on possibly
more than one benchmark): a second cross-encoder within the same model
family and the same benchmark, not the full four-way matrix across
multiple model classes and corpora the review describes as ideal. We
report this scope honestly rather than claiming the fuller comparison.

Run with: poetry run python evaluation/nli_comparison/v1/run_nli_comparison.py
"""
import json
import sys
import time
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

FEVER_SAMPLE = ROOT / "evaluation" / "fever" / "v1" / "sample.json"
RESULTS_PATH = ROOT / "evaluation" / "nli_comparison" / "v1" / "results.json"

PRODUCTION_MODEL = "cross-encoder/nli-deberta-v3-small"
COMPARISON_MODEL = "cross-encoder/nli-deberta-v3-base"

SMRITI_TO_FEVER = {
    RelationshipType.SUPPORTS: "SUPPORTS",
    RelationshipType.REFINES: "SUPPORTS",
    RelationshipType.EQUIVALENT: "SUPPORTS",
    RelationshipType.CONTRADICTS: "REFUTES",
    RelationshipType.NEUTRAL: "NOT ENOUGH INFO",
}
FEVER_LABELS = ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]


def decision_to_fever_label(status, relation_type) -> str:
    if status == ResolutionStatus.ABSTAINED:
        return "NOT ENOUGH INFO"
    return SMRITI_TO_FEVER[relation_type]


def prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def score_with_model(model_name: str, sample: list) -> dict:
    nli_gen = NLIEvidenceGenerator(model_name=model_name)
    resolver = RelationshipResolver(policy=ResolverPolicy.from_config())
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
            pair = CandidatePair(claim_id_a=f"ev_{r['fever_id']}", claim_id_b=f"cl_{r['fever_id']}",
                                  cosine_similarity=1.0, candidate_rank=1)
            evidence = RelationshipEvidence(
                pair=pair, cosine_similarity=1.0,
                nli_scores=nli_scores_ab, nli_scores_b_to_a=nli_scores_ba,
                calibrated_confidence=nli_scores_ab.raw_confidence,
                calibrated_confidence_b_to_a=nli_scores_ba.raw_confidence,
                inference_metadata=InferenceMetadata(model_name=model_name),
                lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
            )
            decision = resolver.resolve_as_decision(evidence)
            predicted = decision_to_fever_label(decision.status, decision.relation_type)
            rows.append({"fever_id": r["fever_id"], "gold_label": r["gold_label"],
                         "predicted_fever_label": predicted, "correct": predicted == r["gold_label"]})
        print(f"  [{model_name}] ...{batch_start + n}/{len(sample)} scored "
              f"({time.monotonic() - t0:.1f}s)", flush=True)
    elapsed = time.monotonic() - t0

    accuracy = round(sum(1 for r in rows if r["correct"]) / len(rows), 4)
    per_class = {}
    for lbl in FEVER_LABELS:
        tp = sum(1 for r in rows if r["gold_label"] == lbl and r["predicted_fever_label"] == lbl)
        fp = sum(1 for r in rows if r["gold_label"] != lbl and r["predicted_fever_label"] == lbl)
        fn = sum(1 for r in rows if r["gold_label"] == lbl and r["predicted_fever_label"] != lbl)
        p, rec, f1 = prf1(tp, fp, fn)
        per_class[lbl] = {"precision": p, "recall": rec, "f1": f1,
                           "support": sum(1 for r in rows if r["gold_label"] == lbl)}
    macro_f1 = round(sum(c["f1"] for c in per_class.values()) / len(per_class), 4)
    return {"model": model_name, "n": len(rows), "elapsed_seconds": elapsed,
            "accuracy": accuracy, "per_class_prf1": per_class, "macro_f1": macro_f1}


def main():
    get_config(env="dev")
    sample = json.loads(FEVER_SAMPLE.read_text(encoding="utf-8"))
    print(f"Loaded {len(sample)} FEVER pairs (reusing the frozen \\S sec:fever sample)")

    results = {}
    for model_name in (PRODUCTION_MODEL, COMPARISON_MODEL):
        print(f"\n=== Scoring with {model_name} ===")
        results[model_name] = score_with_model(model_name, sample)
        r = results[model_name]
        print(f"  accuracy={r['accuracy']:.1%}  macro-F1={r['macro_f1']:.1%}  "
              f"elapsed={r['elapsed_seconds']:.1f}s")

    out = {
        "source": "FEVER validation sample (900 pairs, evaluation/fever/v1/sample.json)",
        "production_model": PRODUCTION_MODEL,
        "comparison_model": COMPARISON_MODEL,
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
