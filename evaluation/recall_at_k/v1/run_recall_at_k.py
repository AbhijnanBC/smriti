"""
run_recall_at_k.py -- retrieval Recall@K / cosine-threshold tradeoff
curves (P1-8, "PLEASE FIX AND SAVE ME" review round).

Reuses SMRITI-Controlled-v2's cached Phase 5 embeddings (real
sentence-embedding vectors already computed by the frozen run; no
re-embedding, no NLI re-run -- this is pure retrieval-stage analysis)
to sweep top-k and cosine similarity threshold INDEPENDENTLY, exactly as
requested, and report Recall@K (fraction of the 668 non-abstention gold
manifest pairs whose partner claim is retrieved) and mean candidates/claim
(the real cost driver for NLI latency, reported as a volume proxy rather
than a separately-measured latency, which would require an actual NLI
run per parameter setting).

A gold pair (A, B) counts as "retrieved" at (top_k, threshold) if B is
among A's top-k nearest neighbors by cosine similarity over ALL other
claims in the corpus AND cosine(A, B) >= threshold, OR the symmetric
condition from B's side -- this matches production's actual candidate
generation, which queries from every claim's own perspective (Phase 6's
FAISS IndexFlatIP top-k search), so a pair becomes a candidate if EITHER
side's search surfaces it.

Run with: poetry run python evaluation/recall_at_k/v1/run_recall_at_k.py
"""
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RUN_ID = "20260911_081039"
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
RESULTS_PATH = ROOT / "evaluation" / "recall_at_k" / "v1" / "results.json"

PRODUCTION_TOP_K = 50
PRODUCTION_THRESHOLD = 0.75
TOP_K_SWEEP = [10, 25, 50, 100]
THRESHOLD_SWEEP = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]


def doc_id_from_path(path: str) -> str:
    return os.path.basename(path).replace(".md", "")


def main():
    art = ROOT / "artifacts" / f"run_{RUN_ID}"
    p4 = json.loads((art / "phase4" / "dataset.json").read_text(encoding="utf-8"))
    p5 = json.loads((art / "phase5" / "dataset.json").read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    doc_of_claim = {c["claim_id"]: doc_id_from_path(c["source_path"]) for c in p4}
    claim_of_doc = {v: k for k, v in doc_of_claim.items()}
    vectors = {r["claim_id"]: r["vector"] for r in p5}
    n_claims = len(vectors)
    print(f"Loaded {n_claims} embedding vectors, {len(p4)} claims")

    gold_pairs = [
        (claim_of_doc[e["doc_a"]], claim_of_doc[e["doc_b"]])
        for e in manifest if e["expected_status"] == "RESOLVED"
        and e["doc_a"] in claim_of_doc and e["doc_b"] in claim_of_doc
    ]
    print(f"Gold non-abstention pairs usable: {len(gold_pairs)} of {len(manifest)} manifest entries")

    claim_ids = list(vectors.keys())
    idx_of = {cid: i for i, cid in enumerate(claim_ids)}
    # Single vectorized all-pairs cosine similarity matrix (one pass);
    # the sweep below is pure filtering over this matrix, not repeated
    # O(n^2) recomputation per (top_k, threshold) setting.
    print("Computing all-pairs cosine similarity matrix (vectorized)...")
    mat = np.array([vectors[cid] for cid in claim_ids], dtype=np.float64)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    unit = mat / norms
    sim_matrix = unit @ unit.T  # (n_claims, n_claims), cosine similarity
    np.fill_diagonal(sim_matrix, -1.0)  # never a claim's own neighbor

    # Rank matrix: rank_matrix[i, j] = j's rank among i's neighbors (0 = nearest)
    order = np.argsort(-sim_matrix, axis=1)
    rank_of = np.empty_like(order)
    rows = np.arange(sim_matrix.shape[0])[:, None]
    rank_of[rows, order] = np.arange(sim_matrix.shape[1])[None, :]

    def retrieved_at(top_k, threshold):
        found = 0
        for cid_a, cid_b in gold_pairs:
            ia, ib = idx_of[cid_a], idx_of[cid_b]
            a_side = rank_of[ia, ib] < top_k and sim_matrix[ia, ib] >= threshold
            b_side = rank_of[ib, ia] < top_k and sim_matrix[ib, ia] >= threshold
            if a_side or b_side:
                found += 1
        candidate_mask = (rank_of < top_k) & (sim_matrix >= threshold)
        mean_candidates_per_claim = candidate_mask.sum(axis=1).mean()
        return round(found / len(gold_pairs), 4), round(float(mean_candidates_per_claim), 3)

    top_k_curve = []
    for k in TOP_K_SWEEP:
        recall, mean_cand = retrieved_at(k, PRODUCTION_THRESHOLD)
        top_k_curve.append({"top_k": k, "threshold": PRODUCTION_THRESHOLD,
                             "recall": recall, "mean_candidates_per_claim": mean_cand})
        print(f"top_k={k:>4} threshold={PRODUCTION_THRESHOLD} -> recall={recall:.1%} "
              f"mean_candidates/claim={mean_cand}")

    threshold_curve = []
    for t in THRESHOLD_SWEEP:
        recall, mean_cand = retrieved_at(PRODUCTION_TOP_K, t)
        threshold_curve.append({"top_k": PRODUCTION_TOP_K, "threshold": t,
                                 "recall": recall, "mean_candidates_per_claim": mean_cand})
        print(f"top_k={PRODUCTION_TOP_K} threshold={t} -> recall={recall:.1%} "
              f"mean_candidates/claim={mean_cand}")

    out = {
        "run_id": RUN_ID,
        "n_gold_pairs": len(gold_pairs),
        "n_claims": n_claims,
        "production_top_k": PRODUCTION_TOP_K,
        "production_threshold": PRODUCTION_THRESHOLD,
        "top_k_sweep_at_fixed_threshold": top_k_curve,
        "threshold_sweep_at_fixed_top_k": threshold_curve,
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
