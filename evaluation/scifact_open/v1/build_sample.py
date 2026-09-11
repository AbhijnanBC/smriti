"""
build_sample.py -- SciFact-Open sample: real positive evidence pairs
plus real, disclosed distractor pairs (P0-9 review round).

Unlike plain SciFact (evaluation/scifact/v1/), SciFact-Open's actual
contribution is the open-domain retrieval setting: a real IR system
surfaces many candidate documents per claim, most of which are NOT
relevant. This benchmark approximates that by pairing every one of the
206 test claims with BOTH:

  (A) its own genuine verified evidence document (SUPPORT or CONTRADICT,
      umbc-scify/scifact-open's "test" config) -- the primary label field
      is used (one evidence document per claim, not the full multi-
      document "evidences" list, for a clean 1:1 pairing matching
      SciFact/FEVER's own format), and

  (B) one document drawn from a fixed, disclosed sample of a real
      500,000-abstract distractor pool (the "distractors" config),
      assigned to that claim by a deterministic, seeded shuffle.

\textbf{Honesty caveat, disclosed here and in the paper:} bucket (B)'s
expected label is NEI (not enough info / unrelated) by construction
intent, not by verification -- nobody has confirmed each of these 206
specific (claim, random-abstract) pairs is genuinely unrelated. Random
sampling from a topically diverse 500k-abstract biomedical/scientific
pool makes a genuine, coincidental topical match with one specific claim
very unlikely, but this is a probabilistic argument, not a checked
ground truth, unlike this project's own SMRITI-ClosedWorld-v1 distractor
buckets (which ARE constructed with a guaranteed, checkable label). We
report bucket (B) results with this caveat attached, not as a certified
closed-world measurement.

Run with: poetry run python evaluation/scifact_open/v1/build_sample.py
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "evaluation" / "scifact_open" / "v1" / "raw"
OUT_PATH = ROOT / "evaluation" / "scifact_open" / "v1" / "sample.json"

SEED = 20260911915


def main():
    claims = json.loads((RAW_DIR / "test_claims.json").read_text(encoding="utf-8"))
    distractors = json.loads((RAW_DIR / "distractor_sample.json").read_text(encoding="utf-8"))
    print(f"Loaded {len(claims)} claims, {len(distractors)} candidate distractor documents")

    rng = random.Random(SEED)
    distractor_pool = distractors[:]
    rng.shuffle(distractor_pool)
    assert len(distractor_pool) >= len(claims), "not enough distractors cached"

    sample_rows = []
    for i, row in enumerate(claims):
        sample_rows.append({
            "claim_idx": i,
            "claim": row["claim"],
            "evidence_text": row["evidence"],
            "gold_label": row["label"],  # SUPPORT or CONTRADICT
            "bucket": "genuine_evidence",
        })
        distractor_doc = distractor_pool[i]
        sample_rows.append({
            "claim_idx": i,
            "claim": row["claim"],
            "evidence_text": distractor_doc["evidence"],
            "gold_label": "NEI",  # by construction intent, not verified -- see docstring
            "bucket": "unverified_random_distractor",
        })

    rng.shuffle(sample_rows)
    OUT_PATH.write_text(json.dumps(sample_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(sample_rows)} rows to {OUT_PATH}")
    from collections import Counter
    print("Bucket counts:", Counter(r["bucket"] for r in sample_rows))
    print("Label counts:", Counter(r["gold_label"] for r in sample_rows))


if __name__ == "__main__":
    main()
