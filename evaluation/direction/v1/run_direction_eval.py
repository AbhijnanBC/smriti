"""
run_direction_eval.py -- external directional-entailment benchmark for
SMRITI's D1-D4 direction metrics (P1-3, "PLEASE FIX AND SAVE ME" review
round).

The paper's own real-corpus direction sample (SMRITI-Reference) is a
"few dozen items" -- not enough statistical power to say much about D4
in particular (limitations.tex already discloses this and warns against
making D4 a headline number). FEVER and SciFact's SUPPORT-labeled pairs
give a much larger sample with a KNOWN, definite gold direction for
free: by each dataset's own task definition, a SUPPORT verdict means
the evidence entails the claim, never the reverse -- so gold_direction
is A_TO_B (evidence=claim_a, claim=claim_b) for every one of these pairs,
with no ambiguity or extra annotation needed.

Reuses evaluation/fever/v1/sample.json and evaluation/scifact/v1/sample.json
(already built and scored this session), restricted to gold_label ==
SUPPORT rows, re-scored here (not reusing the earlier results.json,
which recorded only the collapsed relation type, not direction) to
additionally capture RelationshipDecision.direction.

D1-D4 definitions (matching the framework already used on SMRITI-Reference,
\S\ref{sec:results-annotation}):
    D1 (availability):        fraction of ALL pairs where the resolver
                               commits to a directional call at all
                               (A_TO_B or B_TO_A), regardless of type or
                               correctness.
    D2 (unconditional dir.):  fraction of ALL pairs where predicted
                               direction == A_TO_B (the true gold
                               direction here).
    D3 (joint type+direction): fraction of ALL pairs where the predicted
                               relation type is itself a directional type
                               in the SUPPORT family (SUPPORTS or
                               REFINES) AND predicted direction == A_TO_B.
    D4 (direction | type correct): D3 count divided by the count of
                               pairs where the predicted type was
                               SUPPORTS or REFINES at all (i.e., among
                               decisions that already committed to a
                               directional SUPPORT-family type, how many
                               got the direction right). EQUIVALENT
                               predictions are excluded from this
                               denominator -- EQUIVALENT is always
                               SYMMETRIC by the ontology's own
                               construction (\S\ref{sec:system}) and does
                               not make a directional claim to be right
                               or wrong about; a pair collapsed from
                               SUPPORT to EQUIVALENT is a type
                               disagreement (already counted against D3),
                               not a direction error.

Per P1-3's explicit instruction, D4 is reported but never treated as
the headline number here -- D1/D2 (unconditional over the full sample)
are the primary results, exactly because D4's denominator is much
smaller than N.

Run with:
    poetry run python evaluation/direction/v1/run_direction_eval.py
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
    LifecycleStage, RelationshipType, RelationshipDirection, ResolutionStatus,
)
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator  # noqa: E402
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy  # noqa: E402
from smriti.evaluation.statistical.bootstrap import bootstrap_proportion_ci  # noqa: E402

FEVER_SAMPLE = ROOT / "evaluation" / "fever" / "v1" / "sample.json"
SCIFACT_SAMPLE = ROOT / "evaluation" / "scifact" / "v1" / "sample.json"
RESULTS_PATH = ROOT / "evaluation" / "direction" / "v1" / "results.json"

DIRECTIONAL_TYPES = {RelationshipType.SUPPORTS, RelationshipType.REFINES}


def load_support_pairs():
    pairs = []
    for row in json.loads(FEVER_SAMPLE.read_text(encoding="utf-8")):
        if row["gold_label"] == "SUPPORTS":
            pairs.append({"source": "fever", "evidence_text": row["evidence_text"], "claim": row["claim"],
                          "id": row["fever_id"]})
    for row in json.loads(SCIFACT_SAMPLE.read_text(encoding="utf-8")):
        if row["gold_label"] == "SUPPORT":
            pairs.append({"source": "scifact", "evidence_text": row["evidence_text"], "claim": row["claim"],
                          "id": row["claim_id"]})
    return pairs


def main():
    get_config(env="dev")
    pairs = load_support_pairs()
    print(f"Loaded {len(pairs)} gold-SUPPORT pairs (gold direction = A_TO_B for all, "
          f"{sum(1 for p in pairs if p['source']=='fever')} FEVER + "
          f"{sum(1 for p in pairs if p['source']=='scifact')} SciFact)")

    nli_gen = NLIEvidenceGenerator()
    resolver = RelationshipResolver(policy=ResolverPolicy.from_config())

    batch_size = nli_gen._batch_size
    t0 = time.monotonic()
    rows = []
    for batch_start in range(0, len(pairs), batch_size):
        batch = pairs[batch_start: batch_start + batch_size]
        text_pairs_ab = [(r["evidence_text"], r["claim"]) for r in batch]
        text_pairs_ba = [(r["claim"], r["evidence_text"]) for r in batch]
        combined = nli_gen._run_nli(text_pairs_ab + text_pairs_ba)
        n = len(batch)
        scores_ab, scores_ba = combined[:n], combined[n:]

        for r, s_ab, s_ba in zip(batch, scores_ab, scores_ba):
            nli_scores_ab = nli_gen._scores_to_nli_scores(s_ab)
            nli_scores_ba = nli_gen._scores_to_nli_scores(s_ba)
            pair = CandidatePair(
                claim_id_a=f"ev_{r['source']}_{r['id']}", claim_id_b=f"cl_{r['source']}_{r['id']}",
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
            rows.append({
                "source": r["source"], "id": r["id"],
                "status": decision.status.value,
                "relation_type": decision.relation_type.value if decision.relation_type else None,
                "direction": decision.direction.value,
            })
        print(f"  ...{batch_start + n}/{len(pairs)} scored ({time.monotonic() - t0:.1f}s)", flush=True)

    elapsed = time.monotonic() - t0
    n = len(rows)

    d1_outcomes = [r["direction"] in ("a_to_b", "b_to_a") for r in rows]
    d2_outcomes = [r["direction"] == "a_to_b" for r in rows]
    d3_outcomes = [
        r["relation_type"] in ("supports", "refines") and r["direction"] == "a_to_b"
        for r in rows
    ]
    directional_type_rows = [r for r in rows if r["relation_type"] in ("supports", "refines")]
    d4_outcomes = [r["direction"] == "a_to_b" for r in directional_type_rows]
    equivalent_count = sum(1 for r in rows if r["relation_type"] == "equivalent")

    def summarize(name, outcomes):
        if not outcomes:
            return {"n": 0, "proportion": None, "ci_lower": None, "ci_upper": None}
        ci = bootstrap_proportion_ci(outcomes)
        return {
            "n": len(outcomes),
            "proportion": round(sum(outcomes) / len(outcomes), 4),
            "ci_lower": round(ci.ci_lower, 4), "ci_upper": round(ci.ci_upper, 4),
        }

    d1 = summarize("D1", d1_outcomes)
    d2 = summarize("D2", d2_outcomes)
    d3 = summarize("D3", d3_outcomes)
    d4 = summarize("D4", d4_outcomes)

    print(f"\nN = {n}")
    print(f"D1 (availability):            {d1['proportion']:.1%}  95% CI [{d1['ci_lower']:.1%}, {d1['ci_upper']:.1%}]  n={d1['n']}")
    print(f"D2 (unconditional direction):  {d2['proportion']:.1%}  95% CI [{d2['ci_lower']:.1%}, {d2['ci_upper']:.1%}]  n={d2['n']}")
    print(f"D3 (joint type+direction):     {d3['proportion']:.1%}  95% CI [{d3['ci_lower']:.1%}, {d3['ci_upper']:.1%}]  n={d3['n']}")
    print(f"D4 (direction | type correct): {d4['proportion']:.1%}  95% CI [{d4['ci_lower']:.1%}, {d4['ci_upper']:.1%}]  n={d4['n']} "
          f"(denominator restricted to SUPPORTS/REFINES predictions; NOT the headline number)")
    print(f"EQUIVALENT-predicted (excluded from D4 denominator): {equivalent_count}/{n}")

    out = {
        "source": "FEVER + SciFact gold-SUPPORT pairs (gold direction = A_TO_B by task definition)",
        "n_total": n,
        "n_fever": sum(1 for r in rows if r["source"] == "fever"),
        "n_scifact": sum(1 for r in rows if r["source"] == "scifact"),
        "D1_availability": d1,
        "D2_unconditional_direction_accuracy": d2,
        "D3_joint_type_and_direction": d3,
        "D4_direction_given_type_correct": d4,
        "n_equivalent_predicted_excluded_from_d4": equivalent_count,
        "elapsed_seconds": elapsed,
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
