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
        affected_claims=("RC1",),
        severity="significant",
        possible_future_work="Replace spaCy en_core_web_sm with multilingual model; update NLI cross-encoder.",
    ),
    LimitationRecord(
        limitation_id="LIM-002",
        description="Reliability Index is policy-driven, not empirically calibrated. Different policy weights produce different rankings for the same claim.",
        affected_module="smriti.scoring.policies",
        affected_claims=("RC4",),
        severity="moderate",
        possible_future_work="Empirically calibrate weights against human reliability judgements.",
    ),
    LimitationRecord(
        limitation_id="LIM-003",
        description="FAISS IndexFlatIP provides exact inner product search but does not support dynamic document addition without index rebuild. Retrieval is engineering/infrastructure, not one of the five frozen research claims, so this affects RC2 only indirectly (as an upstream candidate-generation constraint).",
        affected_module="smriti.retrieval.faiss_index",
        affected_claims=(),
        severity="moderate",
        possible_future_work="Switch to IndexIVF or HNSW for incremental indexing.",
    ),
    LimitationRecord(
        limitation_id="LIM-004",
        description="Every RC1-RC5 experiment measures against real, independently-produced reference data (SMRITI-Controlled's construction-time gold labels, or the disclosed LLM-derived SMRITI-Reference annotation) or reports NOT_EVALUABLE; none defaults to a fabricated passing value. The reference annotation is itself LLM-derived, not human-labeled, and is explicitly disclosed as a weaker substitute for independent human judgment (see LIM-007).",
        affected_module="smriti.evaluation.scientific.experiment",
        affected_claims=("RC1", "RC2", "RC3", "RC4", "RC5"),
        severity="significant",
        possible_future_work="Commission a human annotation study (3+ trained annotators, measured inter-annotator kappa) to replace the LLM-derived reference for RC1/RC2.",
    ),
    LimitationRecord(
        limitation_id="LIM-005",
        description="NLI threshold (0.80, config/default.yaml's retrieval.nli_threshold) was set by engineering judgment, not cross-validated on domain-specific data.",
        affected_module="smriti.retrieval.classification.resolver",
        affected_claims=("RC2",),
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
    # ── RECTIFIED (P1-4 addition): Evidence conflict heuristic limitation ──────
    LimitationRecord(
        limitation_id="LIM-008",
        description="Evidence conflict resolution currently uses a heuristic static penalty (-0.10) rather than a formal probabilistic framework. In the current architecture, where each RC has exactly one experiment, this path only fires if a future RC is backed by multiple experiments that disagree; it is inert (no ScienceEvidence conflicts to detect) under the present one-experiment-per-claim design.",
        affected_module="smriti.evaluation.scientific.conflict",
        affected_claims=(),
        severity="minor",
        possible_future_work="Implement Bayesian belief updating or Dempster-Shafer evidence theory inside apply_conflict_adjustments() if/when a claim is ever backed by multiple, potentially-disagreeing experiments.",
    ),
]


def get_limitation(limitation_id: str) -> Optional[LimitationRecord]:
    for lim in LIMITATION_REGISTRY:
        if lim.limitation_id == limitation_id:
            return lim
    return None


def get_significant_limitations() -> List[LimitationRecord]:
    return [lim for lim in LIMITATION_REGISTRY if lim.severity == "significant"]