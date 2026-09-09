"""
Run the three standalone baseline systems (naive keyword extraction, TF-IDF
cosine relationships, Sentence-BERT cosine relationships) and write their
predictions to evaluation/baselines/.

These baselines exist purely for the paper's "compared to what?" section.
They are intentionally NOT scored against gold labels here -- no gold
annotation exists yet at the claim/relationship level for this run. Scoring
happens later, in a separate step, once human/LLM annotation is done and can
be joined against these predictions by claim_id / claim_id_a+claim_id_b.

Usage:
    poetry run python scripts/run_baselines.py

Inputs:
    - artifacts/run_20260909_193441/phase4/dataset.json
        SMRITI's own Phase 4 claims (claim_id, text, source_path, ...) for
        the gold_vault corpus. Baselines 2 and 3 run over these SAME claim
        ids/texts so their relationship predictions can be joined 1:1
        against SMRITI's own Phase 6 predictions and future gold labels.
    - data/raw/gold_vault/*.md
        Raw markdown documents. Baseline 1 reads these directly (it does not
        depend on SMRITI's Phase 2/3 sentence segmentation) and produces its
        own independent claim list with its own claim ids.

Outputs (evaluation/baselines/):
    - naive_extraction_predictions.json
    - tfidf_relationship_predictions.json
    - sbert_relationship_predictions.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from smriti.baselines import (  # noqa: E402
    extract_claims_naive,
    predict_relationships_sbert,
    predict_relationships_tfidf,
)

PHASE4_DATASET = PROJECT_ROOT / "artifacts" / "run_20260909_193441" / "phase4" / "dataset.json"
GOLD_VAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "gold_vault"
OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "baselines"


def load_phase4_claims(path: Path) -> list[dict]:
    """Load SMRITI's own Phase 4 claim records and keep just the fields the
    baselines need: claim_id and text (source_path carried through for
    traceability, but not used by the relationship baselines).
    """
    with path.open(encoding="utf-8") as f:
        records = json.load(f)
    return [
        {
            "claim_id": r["claim_id"],
            "text": r["text"],
            "source_path": r.get("source_path"),
        }
        for r in records
    ]


def count_by_label(predictions: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in predictions:
        counts[p["relationship_type"]] = counts.get(p["relationship_type"], 0) + 1
    return counts


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SMRITI baseline systems -- prediction run (no gold scoring yet)")
    print("=" * 70)

    # --- Load SMRITI's own Phase 4 claims (shared input for baselines 2/3) ---
    phase4_claims = load_phase4_claims(PHASE4_DATASET)
    print(f"\nLoaded {len(phase4_claims)} SMRITI Phase 4 claims from:\n  {PHASE4_DATASET}")

    timings: dict[str, float] = {}
    counts: dict[str, object] = {}

    # --- Baseline 1: naive keyword extraction, run directly on raw markdown ---
    print("\n[1/3] Naive keyword claim extraction (independent of Phase 2/3)...")
    t0 = time.perf_counter()
    naive_claims = extract_claims_naive(GOLD_VAULT_RAW_DIR)
    timings["naive_extraction"] = time.perf_counter() - t0
    counts["naive_extraction"] = len(naive_claims)
    naive_out = OUTPUT_DIR / "naive_extraction_predictions.json"
    naive_out.write_text(json.dumps(naive_claims, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {len(naive_claims)} claims extracted in {timings['naive_extraction']:.2f}s")
    print(f"  -> wrote {naive_out}")

    # --- Baseline 2: TF-IDF cosine relationship baseline ---
    print("\n[2/3] TF-IDF cosine relationship baseline (over SMRITI's Phase 4 claims)...")
    t0 = time.perf_counter()
    tfidf_relationships = predict_relationships_tfidf(phase4_claims)
    timings["tfidf_relations"] = time.perf_counter() - t0
    counts["tfidf_relations"] = count_by_label(tfidf_relationships)
    tfidf_out = OUTPUT_DIR / "tfidf_relationship_predictions.json"
    tfidf_out.write_text(json.dumps(tfidf_relationships, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {len(tfidf_relationships)} candidate relationships in {timings['tfidf_relations']:.2f}s")
    print(f"     label breakdown: {counts['tfidf_relations']}")
    print(f"  -> wrote {tfidf_out}")

    # --- Baseline 3: Sentence-BERT cosine relationship baseline ---
    print("\n[3/3] Sentence-BERT cosine relationship baseline (over SMRITI's Phase 4 claims)...")
    t0 = time.perf_counter()
    sbert_relationships = predict_relationships_sbert(phase4_claims)
    timings["sbert_relations"] = time.perf_counter() - t0
    counts["sbert_relations"] = count_by_label(sbert_relationships)
    sbert_out = OUTPUT_DIR / "sbert_relationship_predictions.json"
    sbert_out.write_text(json.dumps(sbert_relationships, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {len(sbert_relationships)} candidate relationships in {timings['sbert_relations']:.2f}s")
    print(f"     label breakdown: {counts['sbert_relations']}")
    print(f"  -> wrote {sbert_out}")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Baseline':<28}{'Output count':<18}{'Wall-clock (s)':<16}")
    print(f"{'naive_extraction':<28}{counts['naive_extraction']:<18}{timings['naive_extraction']:<16.2f}")
    print(f"{'tfidf_relations':<28}{len(tfidf_relationships):<18}{timings['tfidf_relations']:<16.2f}")
    print(f"{'sbert_relations':<28}{len(sbert_relationships):<18}{timings['sbert_relations']:<16.2f}")

    print(
        f"\nVolume sanity check: naive keyword baseline extracted "
        f"{len(naive_claims)} claims from raw markdown vs. SMRITI's Phase 4 "
        f"pipeline's {len(phase4_claims)} claims (same {len(list(GOLD_VAULT_RAW_DIR.glob('*.md')))} "
        f"source documents in data/raw/gold_vault)."
    )
    print(
        "\nNo scoring against gold labels was performed -- these are "
        "predictions only. Join by claim_id (extraction) or "
        "claim_id_a/claim_id_b (relationships) once gold annotation lands."
    )

    # Persist the summary alongside the predictions for later reference.
    summary_path = OUTPUT_DIR / "run_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "phase4_claim_count": len(phase4_claims),
                "gold_vault_source_doc_count": len(list(GOLD_VAULT_RAW_DIR.glob("*.md"))),
                "naive_extraction": {
                    "claim_count": len(naive_claims),
                    "wall_clock_seconds": timings["naive_extraction"],
                },
                "tfidf_relations": {
                    "relationship_count": len(tfidf_relationships),
                    "label_breakdown": counts["tfidf_relations"],
                    "wall_clock_seconds": timings["tfidf_relations"],
                },
                "sbert_relations": {
                    "relationship_count": len(sbert_relationships),
                    "label_breakdown": counts["sbert_relations"],
                    "wall_clock_seconds": timings["sbert_relations"],
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote run summary to {summary_path}")


if __name__ == "__main__":
    main()
