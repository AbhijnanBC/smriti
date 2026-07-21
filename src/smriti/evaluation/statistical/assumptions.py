"""
assumptions.py — AssumptionRegistry for Phase 12 (P1-3).

RECTIFIED (P1-3): Every major assumption underlying SMRITI's outputs
is now a first-class registered object.

Without this, reviewers will ask:
    "What assumptions underlie this conclusion?"
and the answer would require reading the source code rather than
consulting a structured, queryable registry.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from smriti.core.models import AssumptionRecord

ASSUMPTION_REGISTRY: List[AssumptionRecord] = [
    AssumptionRecord(
        assumption_id="ASMP-001",
        description="spaCy en_core_web_sm correctly identifies clause boundaries in Obsidian markdown notes",
        affected_modules=("smriti.extraction.segmenter", "smriti.claims.constructor"),
        affected_claims=("RC-001",),
        phase=3,
        risk_if_violated="high",
        validation_experiment="EXP-001",
    ),
    AssumptionRecord(
        assumption_id="ASMP-002",
        description="Sentence-transformers contextual embeddings capture semantic similarity relevant to knowledge relationships",
        affected_modules=("smriti.embedding.embedder",),
        affected_claims=("RC-002", "RC-004"),
        phase=5,
        risk_if_violated="high",
        validation_experiment="EXP-002",
    ),
    AssumptionRecord(
        assumption_id="ASMP-003",
        description="FAISS flat inner product search is a sufficiently accurate approximation of true cosine similarity for relationship discovery",
        affected_modules=("smriti.retrieval.faiss_index", "smriti.retrieval.candidate_generator"),
        affected_claims=("RC-004",),
        phase=6,
        risk_if_violated="medium",
        validation_experiment="EXP-004",
    ),
    AssumptionRecord(
        assumption_id="ASMP-004",
        description="The NLI cross-encoder correctly classifies contradiction, entailment, and neutral at the configured threshold (0.75)",
        affected_modules=("smriti.retrieval.classification.evidence", "smriti.retrieval.classification.resolver"),
        affected_claims=("RC-003",),
        phase=6,
        risk_if_violated="high",
        validation_experiment="EXP-003",
    ),
    AssumptionRecord(
        assumption_id="ASMP-005",
        description="Reliability Index policy weights (evidence_strength=0.25, etc.) reflect the epistemological importance of each signal",
        affected_modules=("smriti.scoring.policies", "smriti.scoring.fusion"),
        affected_claims=("RC-005",),
        phase=8,
        risk_if_violated="medium",
        validation_experiment="EXP-005",
    ),
    AssumptionRecord(
        assumption_id="ASMP-006",
        description="Component contribution sum decomposability is a valid faithfulness criterion for explanation evaluation",
        affected_modules=("smriti.scoring.explanation", "smriti.api.services.explain_service"),
        affected_claims=("RC-006",),
        phase=8,
        risk_if_violated="low",
        validation_experiment="EXP-006",
    ),
    AssumptionRecord(
        assumption_id="ASMP-007",
        description="L2-normalized embedding vectors enable cosine similarity via dot product in FAISS IndexFlatIP",
        affected_modules=("smriti.embedding.normalizer", "smriti.retrieval.faiss_index"),
        affected_claims=("RC-002", "RC-004"),
        phase=5,
        risk_if_violated="high",
        validation_experiment="EXP-002",
    ),
    # ── RECTIFIED (P1-3 addition): Evidence conflict penalty assumption ─────────
    AssumptionRecord(
        assumption_id="ASMP-008",
        description="A static 10% confidence penalty is a sufficient V1 proxy for modeling the epistemic degradation caused by conflicting scientific evidence.",
        affected_modules=("smriti.evaluation.scientific.conflict",),
        affected_claims=("RC-005",),
        phase=12,
        risk_if_violated="medium",
        validation_experiment=None,
    ),
]


def get_assumption(assumption_id: str) -> Optional[AssumptionRecord]:
    for a in ASSUMPTION_REGISTRY:
        if a.assumption_id == assumption_id:
            return a
    return None


def get_assumptions_for_claim(claim_id: str) -> List[AssumptionRecord]:
    return [a for a in ASSUMPTION_REGISTRY if claim_id in a.affected_claims]


def get_high_risk_assumptions() -> List[AssumptionRecord]:
    return [a for a in ASSUMPTION_REGISTRY if a.risk_if_violated == "high"]