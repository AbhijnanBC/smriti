"""
build_sample.py -- balanced sample across SciFact's three verdicts
(P0-9 review round).

Pools allenai/scifact_entailment's train + validation splits (1{,}259
claim/abstract pairs total) and takes exactly 265 pairs per label
(SUPPORT/CONTRADICT/NEI) -- 265 because CONTRADICT is the natural
bottleneck (only 265 available across both splits combined), so this is
every CONTRADICT-labeled example available, not a further-reduced
subsample of it.

For SUPPORT/CONTRADICT rows, evidence_text is the concatenation of the
abstract's specific rationale sentences (the `evidence` field's sentence
indices) -- the same "gold rationale" framing FEVER's benchmark uses.
NEI rows carry no rationale by SciFact's own construction (`evidence` is
always empty for them: the verdict is precisely that the cited abstract
does not resolve the claim), so evidence_text is the full abstract text
instead -- what a model given only the abstract actually has available
to judge from. This is disclosed here and in the paper, not hidden.

Run with: poetry run python evaluation/scifact/v1/build_sample.py
"""
import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "evaluation" / "scifact" / "v1" / "raw"
OUT_PATH = ROOT / "evaluation" / "scifact" / "v1" / "sample.json"

SEED = 20260911914


def evidence_text_for(row) -> str:
    abstract = list(row["abstract"])
    if row["verdict"] == "NEI" or not len(row["evidence"]):
        return " ".join(abstract)
    idx = sorted(int(i) for i in row["evidence"])
    return " ".join(abstract[i] for i in idx if 0 <= i < len(abstract))


def main():
    train = pd.read_parquet(RAW_DIR / "train_0000.parquet")
    val = pd.read_parquet(RAW_DIR / "validation_0000.parquet")
    df = pd.concat([train, val], ignore_index=True)
    print(f"Pooled train+validation: {len(df)} rows")
    print(df["verdict"].value_counts())

    n_per_label = int(df["verdict"].value_counts().min())
    print(f"Sampling {n_per_label} per label (bottlenecked by the smallest class)")

    rng = random.Random(SEED)
    sample_rows = []
    for label in ["SUPPORT", "CONTRADICT", "NEI"]:
        subset = df[df["verdict"] == label]
        idx = list(subset.index)
        rng.shuffle(idx)
        chosen = idx[:n_per_label]
        assert len(chosen) == n_per_label
        for i in chosen:
            row = subset.loc[i]
            sample_rows.append({
                "claim_id": int(row["claim_id"]),
                "claim": row["claim"],
                "abstract_id": int(row["abstract_id"]),
                "title": row["title"],
                "evidence_text": evidence_text_for(row),
                "n_evidence_sentences": len(row["evidence"]),
                "n_abstract_sentences": len(row["abstract"]),
                "gold_label": row["verdict"],
            })

    rng.shuffle(sample_rows)
    OUT_PATH.write_text(json.dumps(sample_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(sample_rows)} rows to {OUT_PATH}")
    from collections import Counter
    print("Label counts:", Counter(r["gold_label"] for r in sample_rows))


if __name__ == "__main__":
    main()
