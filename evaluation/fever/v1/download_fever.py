"""
download_fever.py -- fetches the FEVER shared-task validation split with
gold evidence sentences inline (P0-9, "PLEASE FIX AND SAVE ME" review
round: FEVER is the minimum-bar public benchmark).

Source: copenlu/fever_gold_evidence on the Hugging Face Hub, a
community re-packaging of the original FEVER shared-task data
(Thorne et al., 2018) that joins each claim to its own gold evidence
sentence text inline, so no separate Wikipedia dump lookup is needed --
exactly the "claim verification given gold evidence" sub-task, not full
open-domain retrieval (SMRITI's own retrieval stage is evaluated
separately, on SMRITI's own corpora; this benchmark tests entailment/
contradiction classification specifically).

This script downloads validation/0000.parquet once and caches it under
evaluation/fever/v1/raw/ -- re-run only if the cache is missing or you
want to re-verify the source hasn't changed.

Run with: poetry run python evaluation/fever/v1/download_fever.py
"""
import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "evaluation" / "fever" / "v1" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_URL = (
    "https://huggingface.co/datasets/copenlu/fever_gold_evidence/"
    "resolve/refs%2Fconvert%2Fparquet/default/validation/0000.parquet"
)
DEST = RAW_DIR / "validation_0000.parquet"


def main():
    if DEST.exists():
        print(f"Already cached: {DEST} ({DEST.stat().st_size} bytes)")
    else:
        print(f"Downloading {SOURCE_URL} ...")
        urllib.request.urlretrieve(SOURCE_URL, DEST)
        print(f"Wrote {DEST} ({DEST.stat().st_size} bytes)")

    sha256 = hashlib.sha256(DEST.read_bytes()).hexdigest()
    print(f"sha256: {sha256}")


if __name__ == "__main__":
    main()
