"""
download_scifact_open.py -- fetches SciFact-Open's claim/evidence pairs
and a sample of its open-domain distractor corpus (P0-9, "PLEASE FIX AND
SAVE ME" review round).

Source: umbc-scify/scifact-open on the Hugging Face Hub -- a
re-packaging of SciFact-Open (Wadden et al., 2022), which extends
SciFact's verification task with a much larger, open-domain candidate
pool: a real IR system retrieves many documents per claim, most of which
are NOT relevant, and the harder, more realistic test is whether a
verification system correctly avoids committing SUPPORT/CONTRADICT on
the irrelevant majority while still finding the genuine evidence.

Two configs are used:
  "test"        (206 rows): each claim's genuine SUPPORT/CONTRADICT
                 evidence document(s), the actual verified pairs.
  "distractors" (500,000 rows): a flat pool of candidate document texts
                 with no claim association -- real, topically diverse
                 scientific abstracts. This script downloads only a
                 fixed-seed sample of this pool (not all 500k rows,
                 ~400MB and unnecessary at this benchmark's scale), used
                 by build_sample.py to construct real, disclosed
                 "almost certainly unrelated" distractor pairs (see that
                 script's docstring for the honesty caveat -- random
                 sampling from a topically diverse 500k-abstract pool
                 makes genuine topical overlap with any one specific
                 claim very unlikely but not strictly impossible).

Run with: poetry run python evaluation/scifact_open/v1/download_scifact_open.py
"""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "evaluation" / "scifact_open" / "v1" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

N_DISTRACTOR_DOCS_TO_CACHE = 2000
DISTRACTOR_SAMPLE_SEED_OFFSET = 137  # arbitrary fixed row-offset, not a random seed


def fetch_rows(ds, cfg, split, offset, length, max_retries=5):
    url = (f"https://datasets-server.huggingface.co/rows?dataset={ds}&config={cfg}"
           f"&split={split}&offset={offset}&length={length}")
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(3)


def fetch_all_rows(ds, cfg, split, total, length=50):
    rows = []
    offset = 0
    while offset < total:
        data = fetch_rows(ds, cfg, split, offset, length)
        rows.extend(x["row"] for x in data["rows"])
        offset += length
    return rows


def main():
    test_path = RAW_DIR / "test_claims.json"
    if test_path.exists():
        print(f"Already cached: {test_path}")
    else:
        print("Fetching umbc-scify/scifact-open 'test' config (206 claim/evidence pairs)...")
        rows = fetch_all_rows("umbc-scify/scifact-open", "test", "train", 206)
        test_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(rows)} rows to {test_path}")

    distractor_path = RAW_DIR / "distractor_sample.json"
    if distractor_path.exists():
        print(f"Already cached: {distractor_path}")
    else:
        print(f"Fetching a {N_DISTRACTOR_DOCS_TO_CACHE}-row fixed-offset sample of the "
              f"500,000-row 'distractors' config...")
        rows = fetch_all_rows(
            "umbc-scify/scifact-open", "distractors", "train",
            total=DISTRACTOR_SAMPLE_SEED_OFFSET + N_DISTRACTOR_DOCS_TO_CACHE,
            length=100,
        )
        rows = rows[DISTRACTOR_SAMPLE_SEED_OFFSET:]
        distractor_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(rows)} rows to {distractor_path}")

    for p in (test_path, distractor_path):
        sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{p.name}  sha256={sha256}  size={p.stat().st_size}")


if __name__ == "__main__":
    main()
