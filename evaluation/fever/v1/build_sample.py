"""
build_sample.py -- stratified sample of FEVER's validation split (P0-9,
"PLEASE FIX AND SAVE ME" review round).

Samples 300 rows per label (SUPPORTS / REFUTES / NOT ENOUGH INFO) from
evaluation/fever/v1/raw/validation_0000.parquet with a fixed seed, and
writes evaluation/fever/v1/sample.json: one row per claim with its gold
label and its evidence sentence(s) concatenated into a single string
(multi-sentence evidence sets in FEVER are joint/bridging evidence --
all sentences together verify the claim, not independently -- so
concatenation, not a choice of one, is the correct reading).

NOT ENOUGH INFO's "evidence" field is NOT gold evidence in the same
sense as SUPPORTS/REFUTES -- FEVER's own construction links NEI claims
to a plausibly-related sentence for evidence-retrieval training, not a
sentence that entails or refutes the claim. This is disclosed in the
paper, not hidden: it makes the NEI arm of this benchmark a test of
"does SMRITI correctly avoid committing to SUPPORTS/REFUTES on a
sentence that doesn't settle the claim," which is still the right thing
to test, but for a different reason than genuine annotator-level
ambiguity.

Run with: poetry run python evaluation/fever/v1/build_sample.py
"""
import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW_PARQUET = ROOT / "evaluation" / "fever" / "v1" / "raw" / "validation_0000.parquet"
OUT_PATH = ROOT / "evaluation" / "fever" / "v1" / "sample.json"

N_PER_LABEL = 300
SEED = 20260911913


def main():
    df = pd.read_parquet(RAW_PARQUET)
    rng = random.Random(SEED)

    sample_rows = []
    for label in ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]:
        subset = df[df["label"] == label]
        idx = list(subset.index)
        rng.shuffle(idx)
        chosen = idx[:N_PER_LABEL]
        assert len(chosen) == N_PER_LABEL, f"{label}: only {len(chosen)} available"
        for i in chosen:
            row = subset.loc[i]
            evidence_text = " ".join(ev[2] for ev in row["evidence"])
            sample_rows.append({
                "fever_id": row["id"],
                "claim": row["claim"],
                "evidence_text": evidence_text,
                "n_evidence_sentences": len(row["evidence"]),
                "gold_label": row["label"],
                "verifiable": row["verifiable"],
            })

    rng.shuffle(sample_rows)
    OUT_PATH.write_text(json.dumps(sample_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(sample_rows)} rows to {OUT_PATH}")
    from collections import Counter
    print("Label counts:", Counter(r["gold_label"] for r in sample_rows))


if __name__ == "__main__":
    main()
