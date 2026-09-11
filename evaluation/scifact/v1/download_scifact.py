"""
download_scifact.py -- fetches SciFact's claim-verification data with
gold rationale sentences inline (P0-9, "PLEASE FIX AND SAVE ME" review
round: SciFact, following FEVER as the second public benchmark).

Source: allenai/scifact_entailment on the Hugging Face Hub -- a
re-packaging of SciFact (Wadden et al., 2020) that joins each claim to
its cited abstract (as a list of sentences) plus the specific rationale
sentence indices and verdict (SUPPORT/CONTRADICT/NEI), so no separate
corpus lookup is needed.

Downloads both the train and validation parquet files once and caches
them under evaluation/scifact/v1/raw/ -- both splits are pooled into one
labeled pool for sampling (evaluation/scifact/v1/build_sample.py); no
training happens in this project, so held-out/train distinctions carry
no leakage risk here.

Run with: poetry run python evaluation/scifact/v1/download_scifact.py
"""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "evaluation" / "scifact" / "v1" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

PARQUET_INFO_URL = "https://datasets-server.huggingface.co/parquet?dataset=allenai/scifact_entailment"


def main():
    with urllib.request.urlopen(PARQUET_INFO_URL, timeout=20) as r:
        info = json.loads(r.read().decode("utf-8"))

    for f in info["parquet_files"]:
        if f["config"] != "default":
            continue
        dest = RAW_DIR / f"{f['split']}_0000.parquet"
        if dest.exists():
            print(f"Already cached: {dest} ({dest.stat().st_size} bytes)")
        else:
            print(f"Downloading {f['url']} ...")
            urllib.request.urlretrieve(f["url"], dest)
            print(f"Wrote {dest} ({dest.stat().st_size} bytes)")
        sha256 = hashlib.sha256(dest.read_bytes()).hexdigest()
        print(f"  sha256: {sha256}")


if __name__ == "__main__":
    main()
