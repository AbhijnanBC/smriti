"""
limitations.py — LimitationRegistry for Phase 12 (P1-4).

RECTIFIED (P1-4): Limitations are known architectural boundaries,
NOT risks. They describe what SMRITI CANNOT do by design.

A limitation is:
    "SMRITI does not support multi-language corpora (by design)."

A threat is:
    "The single-vault evaluation may not generalize to multi-vault use."

These are fundamentally different and must be kept separate.
"""

from __future__ import annotations

from typing import List, Optional
from smriti.core.models import LimitationRecord

LIMITATION_REGISTRY: List[LimitationRecord] = [
    LimitationRecord(
        limitation_id="LIM-001",
        description="SMRITI processes only English-language documents. Multi-language support would require multilingual NLP models throughout Phases 3–6.",
        affected_module="smriti.extraction.segmenter",
        affected_claims=("RC-001",),
        severity="significant",
        possible_future_work="Replace spaCy en_core_web_sm with multilingual model; update NLI cross-encoder.",
    ),
    LimitationRecord(
        limitation_id="LIM-002",
        description="Reliability Index is policy-driven, not empirically calibrated. Different policy weights produce different rankings for the same claim.",
        affected_module="smriti.scoring.policies",
        affected_claims=("RC-005",),
        severity="moderate",
        possible_future_work="Empirically calibrate weights against human reliability judgements.",
    ),
    LimitationRecord(
        limitation_id="LIM-003",
        description="FAISS IndexFlatIP provides exact inner product search but does not support dynamic document addition without index rebuild.",
        affected_module="smriti.retrieval.faiss_index",
        affected_claims=("RC-004",),
        severity="moderate",
        possible_future_work="Switch to IndexIVF or HNSW for incremental indexing.",
    ),
    LimitationRecord(
        limitation_id="LIM-004",
        description="Phase 12 scientific evaluation uses structural proxies (all claims have text, all embeddings exist) rather than true human-labeled semantic accuracy.",
        affected_module="smriti.evaluation.scientific.experiment",
        affected_claims=("RC-001", "RC-002", "RC-003", "RC-004", "RC-005", "RC-006"),
        severity="significant",
        possible_future_work="Commission human annotation study for each scientific domain.",
    ),
    LimitationRecord(
        limitation_id="LIM-005",
        description="NLI threshold (0.75) was set by engineering judgment, not cross-validated on domain-specific data.",
        affected_module="smriti.retrieval.classification.resolver",
        affected_claims=("RC-003",),
        severity="moderate",
        possible_future_work="Cross-validate threshold on domain-specific contradiction pairs.",
    ),
    LimitationRecord(
        limitation_id="LIM-006",
        description="Temporal reasoning requires Claim.timestamp populated from document metadata. If Phase 2 does not extract timestamps, temporal analysis is disabled.",
        affected_module="smriti.evolution.temporal",
        affected_claims=(),
        severity="minor",
        possible_future_work="Add timestamp extraction from YAML front matter in Phase 2.",
    ),
    # ── RECTIFIED (P1-4 addition): Structural proxies limitation ──────────────
    LimitationRecord(
        limitation_id="LIM-007",
        description="Phase 12 currently utilizes structural proxies (e.g., non-empty string checks, vector presence) rather than semantic empirical evaluation due to the lack of domain-specific, human-annotated ground truth.",
        affected_module="smriti.evaluation.scientific.experiment",
        affected_claims=("RC-001", "RC-002", "RC-003", "RC-004"),
        severity="significant",
        possible_future_work="Commission human-annotated datasets and update GroundTruthRepository to replace structural proxies with true semantic evaluation metrics.",
    ),
    # ── RECTIFIED (P1-4 addition): Evidence conflict heuristic limitation ──────
    LimitationRecord(
        limitation_id="LIM-008",
        description="Evidence conflict resolution currently uses a heuristic static penalty (-0.10) rather than a formal probabilistic framework.",
        affected_module="smriti.evaluation.scientific.conflict",
        affected_claims=("RC-005",),
        severity="moderate",
        possible_future_work="Implement Bayesian belief updating or Dempster-Shafer evidence theory inside apply_conflict_adjustments().",
    ),
]


def get_limitation(limitation_id: str) -> Optional[LimitationRecord]:
    for lim in LIMITATION_REGISTRY:
        if lim.limitation_id == limitation_id:
            return lim
    return None


def get_significant_limitations() -> List[LimitationRecord]:
    return [lim for lim in LIMITATION_REGISTRY if lim.severity == "significant"]