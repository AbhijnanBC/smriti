"""
assumptions.py — AssumptionRegistry for Phase 12 (P1-3).

RECTIFIED (P1-3): Every major assumption underlying SMRITI's outputs
is now a first-class registered object.

Without this, reviewers will ask:
    "What assumptions underlie this conclusion?"
and the answer would require reading the source code rather than
consulting a structured, queryable registry.

RECTIFIED (P0-B, "FINAL REVIEW" round): every affected_claims entry
previously used a stale RC-00N scheme (RC-001..RC-006) that never
matched the frozen canonical claim registry (RC1..RC5,
evaluation/certification/claims.py) -- get_assumptions_for_claim("RC1")
could never find an assumption recorded as affected_claims=("RC-001",),
silently breaking the exact traceability this registry exists to
provide. Several validation_experiment values also pointed at an
experiment that exists and runs, but does not actually test the
assumption it was attached to:
    ASMP-003 (FAISS approximation accuracy) pointed at EXP-004
        (reliability metamorphic testing -- unrelated).
    ASMP-004 (NLI threshold correctness) pointed at EXP-003
        (graph partitioning -- unrelated).
    ASMP-005 (reliability weights are epistemologically appropriate)
        pointed at EXP-005 (reconstruction/explainability self-
        consistency -- tests whether the score matches its own audit
        trail, not whether the WEIGHTS are the right values).
    ASMP-006 referenced affected_claims=("RC-006",) and
        validation_experiment="EXP-006", neither of which exists in the
        frozen registry (the correct mapping, RC5/EXP-005, is exactly
        what evaluation/certification/claims.py's own RC5 spec already
        cites as its "assumptions": ("ASMP-006",) -- this file's own
        record just never matched it).

Every affected_claims tuple below is now a subset of
claims.CANONICAL_CLAIM_IDS, cross-checked against claims.py's own
per-claim "assumptions" tuples (test_assumption_registry_integrity.py
verifies this both ways, not just asserted here) rather than a second,
independently-drifting copy of the same fact.
"""

from __future__ import annotations

from smriti.core.models import AssumptionRecord

ASSUMPTION_REGISTRY: list[AssumptionRecord] = [
    AssumptionRecord(
        assumption_id="ASMP-001",
        description="spaCy en_core_web_sm correctly identifies clause boundaries in Obsidian markdown notes",
        affected_modules=("smriti.extraction.segmenter", "smriti.claims.constructor"),
        affected_claims=("RC1",),
        phase=3,
        risk_if_violated="high",
        validation_experiment="EXP-001",
        validation_status="partially_validated",
        # EXP-001 measures extraction precision end-to-end against a
        # reference annotation -- real, direct evidence for this
        # assumption, but it measures the pipeline's combined output, not
        # spaCy's clause-boundary detection in isolation from everything
        # downstream of it (assertion classification, degradation).
    ),
    AssumptionRecord(
        assumption_id="ASMP-002",
        description="Sentence-transformers contextual embeddings capture semantic similarity relevant to knowledge relationships",
        affected_modules=("smriti.embedding.embedder",),
        affected_claims=("RC2",),
        phase=5,
        risk_if_violated="high",
        validation_experiment=None,
        validation_status="unvalidated",
        # RECTIFIED (P0-B): no experiment in the current registry isolates
        # embedding quality from everything downstream of it. EXP-002's
        # macro-F1 would be affected by bad embeddings, but claims.py's
        # own RC2 "assumptions" tuple does not currently cite this
        # assumption as one EXP-002 was designed to test -- reported
        # honestly as unvalidated rather than claiming indirect credit.
    ),
    AssumptionRecord(
        assumption_id="ASMP-003",
        description="FAISS flat inner product search is a sufficiently accurate approximation of true cosine similarity for relationship discovery",
        affected_modules=("smriti.retrieval.faiss_index", "smriti.retrieval.candidate_generator"),
        affected_claims=("RC2",),
        phase=6,
        risk_if_violated="medium",
        validation_experiment=None,
        validation_status="unvalidated",
        # RECTIFIED (P0-B): previously pointed at EXP-004 (reliability
        # metamorphic testing), which does not exercise FAISS retrieval
        # accuracy at all. No current experiment isolates retrieval
        # accuracy from downstream classification; reported as unvalidated.
    ),
    AssumptionRecord(
        assumption_id="ASMP-004",
        description="The NLI cross-encoder correctly classifies contradiction, entailment, and neutral at the configured threshold (0.80)",
        affected_modules=(
            "smriti.retrieval.classification.evidence",
            "smriti.retrieval.classification.resolver",
        ),
        affected_claims=("RC2", "RC3"),
        phase=6,
        risk_if_violated="high",
        validation_experiment="EXP-002",
        validation_status="partially_validated",
        # RECTIFIED (P0-B): previously pointed at EXP-003 (graph
        # partitioning), which tests a structural invariant GIVEN whatever
        # CONTRADICTS edges already exist -- it says nothing about whether
        # those edges are semantically correct. EXP-002 (relationship
        # classification macro-F1 against reference annotation) is the
        # experiment that actually measures NLI classification
        # correctness, and is what claims.py's own RC2 and RC3 specs both
        # cite as testing this assumption. Still "partially_validated," not
        # "validated": EXP-002 measures end-to-end classification quality,
        # not the specific 0.80 threshold value in isolation from other
        # threshold choices.
    ),
    AssumptionRecord(
        assumption_id="ASMP-005",
        description="Reliability Index policy weights (evidence_strength=0.25, etc.) reflect the epistemological importance of each signal",
        affected_modules=("smriti.scoring.policies", "smriti.scoring.fusion"),
        affected_claims=("RC4",),
        phase=8,
        risk_if_violated="medium",
        validation_experiment=None,
        validation_status="unvalidated",
        # RECTIFIED (P0-B): previously pointed at EXP-005, which tests
        # reconstruction faithfulness (does the reported score match its
        # own recorded audit trail) -- a real, useful, but completely
        # different question from "are these specific weight VALUES
        # epistemologically the right ones." No current experiment
        # validates the weights themselves; reported as unvalidated. This
        # matches the review's own explicit recommended fix verbatim.
    ),
    AssumptionRecord(
        assumption_id="ASMP-006",
        description="Component contribution sum decomposability is a valid faithfulness criterion for explanation evaluation",
        affected_modules=("smriti.scoring.explanation", "smriti.api.services.explain_service"),
        affected_claims=("RC5",),
        phase=8,
        risk_if_violated="low",
        validation_experiment="EXP-005",
        validation_status="validated",
        # RECTIFIED (P0-B): affected_claims was ("RC-006",) and
        # validation_experiment was "EXP-006" -- neither exists in the
        # frozen registry. The correct mapping (RC5/EXP-005) is exactly
        # what claims.py's own RC5 spec already cites as testing this
        # assumption: EXP-005's reconstruction_exact_match_rate directly
        # and specifically tests decomposability, so "validated" (not
        # merely "partially") is the accurate status here.
    ),
    AssumptionRecord(
        assumption_id="ASMP-007",
        description="L2-normalized embedding vectors enable cosine similarity via dot product in FAISS IndexFlatIP",
        affected_modules=("smriti.embedding.normalizer", "smriti.retrieval.faiss_index"),
        affected_claims=("RC2",),
        phase=5,
        risk_if_violated="high",
        validation_experiment=None,
        validation_status="unvalidated",
        # RECTIFIED (P0-B): same reasoning as ASMP-002/ASMP-003 -- no
        # current experiment isolates this normalization-correctness
        # assumption from the end-to-end pipeline it feeds into.
    ),
    # ── RECTIFIED (P1-3 addition): Evidence conflict penalty assumption ─────────
    AssumptionRecord(
        assumption_id="ASMP-008",
        description="A static 10% confidence penalty is a sufficient V1 proxy for modeling the epistemic degradation caused by conflicting scientific evidence.",
        affected_modules=("smriti.evaluation.scientific.conflict",),
        affected_claims=("RC4",),
        phase=12,
        risk_if_violated="medium",
        validation_experiment=None,
        validation_status="unvalidated",
    ),
]


def get_assumption(assumption_id: str) -> AssumptionRecord | None:
    for a in ASSUMPTION_REGISTRY:
        if a.assumption_id == assumption_id:
            return a
    return None


def get_assumptions_for_claim(claim_id: str) -> list[AssumptionRecord]:
    return [a for a in ASSUMPTION_REGISTRY if claim_id in a.affected_claims]


def get_high_risk_assumptions() -> list[AssumptionRecord]:
    return [a for a in ASSUMPTION_REGISTRY if a.risk_if_violated == "high"]


def get_unvalidated_assumptions() -> list[AssumptionRecord]:
    """RECTIFIED (P0-B): surfaces exactly what the review asked to be able
    to see at a glance -- which assumptions have no empirical backing at
    all, as opposed to those with at least partial/indirect evidence."""
    return [a for a in ASSUMPTION_REGISTRY if a.validation_status == "unvalidated"]
