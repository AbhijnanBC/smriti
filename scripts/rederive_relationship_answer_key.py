"""
rederive_relationship_answer_key.py — recompute SMRITI's predictions in
evaluation/annotation/rc2_rc3_relationships_answer_key.json using the
CURRENT resolver/specificity/relatedness code, from the SAME cached raw
NLI scores each entry already carries (no re-inference needed: the NLI
model and its inputs are unchanged, only how the scores are interpreted
has changed this round).

Why this is necessary: the external "reality check" review round 3 found
and fixed real resolver-level bugs (P0-4 retired REFINES no-entailment
heuristic, P0-5 directional confidence, an attribution-cue bug in the
specificity gate that misclassified genuine SUPPORTS pairs as REFINES).
Those fixes change what SMRITI would predict for the SAME real
SMRITI-Reference claim pairs already sampled for blind annotation. The
two annotation passes (pass1/pass2_relationships.json) are independent
human/LLM judgments of the claim pairs themselves and do not need to
change; only SMRITI's own predicted_label/direction/confidence do.

Run with: poetry run python scripts/rederive_relationship_answer_key.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from smriti.core.models import (
    RelationshipEvidence, NLIScores, InferenceMetadata, CandidatePair,
    LifecycleStage, RelationshipType, ResolutionStatus,
)
from smriti.retrieval.classification.resolver import RelationshipResolver, compute_decision_confidence
from smriti.retrieval.classification.specificity import is_refinement
from smriti.retrieval.classification.relatedness import passes_contradiction_relatedness_gate
from smriti.core.config import get_config

ANSWER_KEY_PATH = ROOT / "evaluation" / "annotation" / "rc2_rc3_relationships_answer_key.json"


def make_nli_scores(entailment, neutral, contradiction):
    scores = {"entailment": entailment, "neutral": neutral, "contradiction": contradiction}
    predicted_label = max(scores, key=scores.get)
    return NLIScores(
        entailment_score=entailment, neutral_score=neutral, contradiction_score=contradiction,
        predicted_label=predicted_label, raw_confidence=max(entailment, neutral, contradiction),
    )


def main():
    config = get_config()
    rd_cfg = config.get("relationship_discovery", {})
    min_relatedness = rd_cfg.get("min_contradiction_relatedness", 0.03)
    specificity_margin = rd_cfg.get("refine_specificity_margin", 3.0)

    answer_key = json.loads(ANSWER_KEY_PATH.read_text(encoding="utf-8"))

    # Build claim_id -> text map from every distinct source_run_id referenced.
    claim_text = {}
    source_runs = {e["source_run_id"] for e in answer_key.values() if "source_run_id" in e}
    for run_id in source_runs:
        p4_path = ROOT / "artifacts" / f"run_{run_id}" / "phase4" / "dataset.json"
        if not p4_path.exists():
            print(f"WARNING: {p4_path} not found; pairs from run {run_id} cannot be re-specificity-gated by text.")
            continue
        p4 = json.loads(p4_path.read_text(encoding="utf-8"))
        for c in p4:
            claim_text[c["claim_id"]] = c["text"]

    resolver = RelationshipResolver()
    changed = 0
    unresolved_text = 0

    for key, entry in answer_key.items():
        ab_scores = make_nli_scores(
            entry["nli_entailment_a_to_b"], entry["nli_neutral_a_to_b"], entry["nli_contradiction_a_to_b"],
        )
        ba_scores = make_nli_scores(
            entry["nli_entailment_b_to_a"], entry["nli_neutral_b_to_a"], entry["nli_contradiction_b_to_a"],
        )
        pair = CandidatePair(
            claim_id_a=entry["claim_id_a"], claim_id_b=entry["claim_id_b"],
            cosine_similarity=entry["cosine_similarity"], candidate_rank=1,
        )
        evidence = RelationshipEvidence(
            pair=pair, cosine_similarity=entry["cosine_similarity"],
            nli_scores=ab_scores, nli_scores_b_to_a=ba_scores,
            calibrated_confidence=ab_scores.raw_confidence,
            calibrated_confidence_b_to_a=ba_scores.raw_confidence,
            inference_metadata=InferenceMetadata(model_name="cross-encoder/nli-deberta-v3-small"),
            lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
        )

        # RECTIFIED (P0-6, "FINAL REVIEW" round -- finish UNKNOWN
        # migration): call the conceptually correct resolve_as_decision()
        # rather than the legacy resolve() -> (RelationshipType, Direction)
        # tuple with UNKNOWN as a hidden sixth value. This is a pure
        # call-site modernization, not a behavior change: resolve_as_decision()
        # internally calls resolve() and wraps its output, so rel_type/
        # direction below are byte-identical to what the legacy call
        # produced -- rel_type is set back to the RelationshipType.UNKNOWN
        # sentinel (rather than left as None) only because this script's
        # OWN downstream logic (the relatedness/specificity gates below,
        # and compute_decision_confidence, both written against
        # RelationshipType) predates the Decision API and still reasons
        # in those terms; that internal bookkeeping is not the
        # "evaluation/reporting code scoring UNKNOWN classification
        # accuracy" concern resolve_as_decision()'s own docstring warns
        # about -- score.py, the actual consumer of this file's output,
        # never treats UNKNOWN as a competing class (verified: it falls
        # through as a non-match against every real label, exactly the
        # correct abstention-as-a-miss behavior).
        decision = resolver.resolve_as_decision(evidence)
        rel_type = decision.relation_type if decision.relation_type is not None else RelationshipType.UNKNOWN
        direction = decision.direction

        # Relatedness gate (CONTRADICTS only) -- needs claim text.
        text_a = claim_text.get(entry["claim_id_a"])
        text_b = claim_text.get(entry["claim_id_b"])
        if rel_type == RelationshipType.CONTRADICTS and text_a and text_b:
            if not passes_contradiction_relatedness_gate(text_a, text_b, min_relatedness):
                rel_type = RelationshipType.UNKNOWN
                from smriti.core.models import RelationshipDirection
                direction = RelationshipDirection.SYMMETRIC

        # Specificity gate (SUPPORTS -> REFINES) -- needs claim text.
        if rel_type == RelationshipType.SUPPORTS:
            if text_a and text_b:
                from smriti.core.models import RelationshipDirection
                if direction == RelationshipDirection.A_TO_B:
                    entailing_text, entailed_text = text_a, text_b
                else:
                    entailing_text, entailed_text = text_b, text_a
                if is_refinement(entailing_text, entailed_text, specificity_margin):
                    rel_type = RelationshipType.REFINES
            else:
                unresolved_text += 1

        decision_confidence = compute_decision_confidence(evidence, rel_type, direction)

        new_label = rel_type.value
        new_direction = direction.value
        if entry["predicted_label"] != new_label or entry["direction"] != new_direction:
            changed += 1
        entry["predicted_label"] = new_label
        entry["direction"] = new_direction
        entry["calibrated_confidence"] = round(decision_confidence, 6)

    ANSWER_KEY_PATH.write_text(json.dumps(answer_key, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Re-derived {len(answer_key)} entries. Changed: {changed}. "
          f"Entries missing claim text (specificity gate skipped): {unresolved_text}.")
    print(f"Wrote {ANSWER_KEY_PATH}")


if __name__ == "__main__":
    main()
