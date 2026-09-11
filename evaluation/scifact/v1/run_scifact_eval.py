"""
run_scifact_eval.py -- zero-shot transfer evaluation of SMRITI's
relationship resolver against SciFact (P0-9, "PLEASE FIX AND SAVE ME"
review round).

Identical methodology to evaluation/fever/v1/run_fever_eval.py (see that
script's docstring for the full rationale): each (evidence, claim) pair
is fed directly to the same bidirectional NLI cross-encoder and the same
RelationshipResolver used throughout this paper, no fine-tuning, no
retrieval stage (SciFact's cited abstract is given directly, exactly as
FEVER's gold evidence is).

Label mapping (SMRITI's 5-way + ABSTAINED -> SciFact's 3-way):
    SUPPORTS, REFINES, EQUIVALENT  -> SUPPORT
    CONTRADICTS                    -> CONTRADICT
    NEUTRAL, ABSTAINED             -> NEI

Run with:
    poetry run python evaluation/scifact/v1/download_scifact.py   # once
    poetry run python evaluation/scifact/v1/build_sample.py        # once
    poetry run python evaluation/scifact/v1/run_scifact_eval.py
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

SAMPLE_PATH = ROOT / "evaluation" / "scifact" / "v1" / "sample.json"
RESULTS_PATH = ROOT / "evaluation" / "scifact" / "v1" / "results.json"

SMRITI_TO_SCIFACT = {
    RelationshipType.SUPPORTS: "SUPPORT",
    RelationshipType.REFINES: "SUPPORT",
    RelationshipType.EQUIVALENT: "SUPPORT",
    RelationshipType.CONTRADICTS: "CONTRADICT",
    RelationshipType.NEUTRAL: "NEI",
}
SCIFACT_LABELS = ["SUPPORT", "CONTRADICT", "NEI"]


def decision_to_scifact_label(status, relation_type) -> str:
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
    print(f"Loaded {len(sample)} SciFact pairs")

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
                claim_id_a=f"ev_{r['claim_id']}", claim_id_b=f"cl_{r['claim_id']}",
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
            predicted = decision_to_scifact_label(decision.status, decision.relation_type)
            rows.append({
                "claim_id": r["claim_id"],
                "gold_label": r["gold_label"],
                "n_evidence_sentences": r["n_evidence_sentences"],
                "n_abstract_sentences": r["n_abstract_sentences"],
                "smriti_status": decision.status.value,
                "smriti_relation_type": decision.relation_type.value if decision.relation_type else None,
                "predicted_scifact_label": predicted,
                "correct": predicted == r["gold_label"],
            })
        print(f"  ...{batch_start + n}/{len(sample)} scored "
              f"({time.monotonic() - t0:.1f}s elapsed)", flush=True)

    elapsed = time.monotonic() - t0
    print(f"\nScored {len(rows)} pairs in {elapsed:.1f}s")

    overall_correct = sum(1 for r in rows if r["correct"])
    accuracy = round(overall_correct / len(rows), 4)
    print(f"\nOverall 3-way accuracy: {accuracy:.1%} ({overall_correct}/{len(rows)})")

    per_class = {}
    for lbl in SCIFACT_LABELS:
        tp = sum(1 for r in rows if r["gold_label"] == lbl and r["predicted_scifact_label"] == lbl)
        fp = sum(1 for r in rows if r["gold_label"] != lbl and r["predicted_scifact_label"] == lbl)
        fn = sum(1 for r in rows if r["gold_label"] == lbl and r["predicted_scifact_label"] != lbl)
        p, rec, f1 = prf1(tp, fp, fn)
        support = sum(1 for r in rows if r["gold_label"] == lbl)
        per_class[lbl] = {"precision": p, "recall": rec, "f1": f1, "support": support, "tp": tp, "fp": fp, "fn": fn}
        print(f"  {lbl:<12} P={p:.1%}  R={rec:.1%}  F1={f1:.1%}  support={support}")
    macro_f1 = round(sum(c["f1"] for c in per_class.values()) / len(per_class), 4)
    print(f"  macro-F1 = {macro_f1:.1%}")

    confusion = defaultdict(lambda: defaultdict(int))
    for r in rows:
        confusion[r["gold_label"]][r["predicted_scifact_label"]] += 1
    print("\nConfusion matrix (rows=gold, cols=predicted):")
    print(f"{'':<12}" + "".join(f"{l:<12}" for l in SCIFACT_LABELS))
    for gold in SCIFACT_LABELS:
        print(f"{gold:<12}" + "".join(f"{confusion[gold][pred]:<12}" for pred in SCIFACT_LABELS))

    native_breakdown = Counter((r["gold_label"], r["smriti_status"], r["smriti_relation_type"]) for r in rows)

    out = {
        "source": "allenai/scifact_entailment (train+validation pooled)",
        "n_pairs": len(rows),
        "n_per_label_sampled": 265,
        "overall_accuracy_3way": accuracy,
        "per_class_prf1": per_class,
        "macro_f1": macro_f1,
        "confusion_matrix": {g: dict(confusion[g]) for g in SCIFACT_LABELS},
        "native_breakdown": {f"{g}|{s}|{t}": c for (g, s, t), c in native_breakdown.items()},
        "elapsed_seconds": elapsed,
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
