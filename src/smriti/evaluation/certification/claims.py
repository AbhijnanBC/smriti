"""
claims.py — Research Claims Matrix (rectified P0-3).

RECTIFIED (P0-3): ResearchClaim now includes research_question, null_hypothesis,
assumptions, threats, supporting_limitations, and applicability.

These fields make claims genuine scientific objects, not just metadata tags.
Reviewers can ask "What would falsify this?" and get a documented answer.
"""

from __future__ import annotations

from typing import Dict, List
from smriti.core.models import (
    ResearchClaim, ScienceEvidence, EvidenceGrade,
    ScientificDomain, VerificationStatus, ExperimentResult,
)

# RECTIFIED (P0-3): Enriched claim specifications
RESEARCH_CLAIMS_SPEC = [
    {
        "claim_id": "RC-001",
        "statement": "SMRITI's claim extraction is structurally precise: every extracted claim has non-empty text and valid provenance",
        "scientific_domain": ScientificDomain.KNOWLEDGE_EXTRACTION,
        "supporting_experiment_ids": ["EXP-001"],
        "acceptance_metric": "precision",
        "acceptance_threshold": 0.70,
        # RECTIFIED (P0-3) enrichment:
        "research_question": "Does the extraction pipeline reliably produce structurally valid claims from Obsidian markdown notes?",
        "null_hypothesis": "H₀: Extraction precision < 0.70 (no significant structural validity)",
        "assumptions": ("ASMP-001",),   # spaCy correctly identifies clause boundaries
        "threats": ("THR-001",),        # Synthetic ground truth
        "supporting_limitations": ("LIM-001", "LIM-004"),  # English only; structural proxy
        "applicability": "English-language Obsidian notes processed by SMRITI v2",
    },
    {
        "claim_id": "RC-002",
        "statement": "Contextual embedding payload produces valid L2-normalized vectors for all claims",
        "scientific_domain": ScientificDomain.EMBEDDING_QUALITY,
        "supporting_experiment_ids": ["EXP-002"],
        "acceptance_metric": "embedding_stability",
        "acceptance_threshold": 0.90,
        "research_question": "Are all embedded claims represented as valid, stable, L2-normalized vectors?",
        "null_hypothesis": "H₀: Embedding stability < 0.90 (non-determinism present)",
        "assumptions": ("ASMP-002", "ASMP-007"),
        "threats": ("THR-001",),
        "supporting_limitations": ("LIM-004",),
        "applicability": "SMRITI v2 with fixed sentence-transformers model version",
    },
    {
        "claim_id": "RC-003",
        "statement": "Contradiction partitioning correctly assigns claims to distinct partitions",
        "scientific_domain": ScientificDomain.KNOWLEDGE_GRAPH,
        "supporting_experiment_ids": ["EXP-003"],
        "acceptance_metric": "partition_purity",
        "acceptance_threshold": 0.80,
        "research_question": "Does the Phase 7 partitioning algorithm correctly separate contradictory claims?",
        "null_hypothesis": "H₀: Partition purity < 0.80 (contradictions co-occur within partitions)",
        "assumptions": ("ASMP-004",),  # NLI threshold correctly classifies contradictions
        "threats": ("THR-003", "THR-006"),
        "supporting_limitations": ("LIM-004", "LIM-005"),
        "applicability": "Knowledge graphs built with SMRITI v2 Phase 7 constraint-based partitioning",
    },
    {
        "claim_id": "RC-004",
        "statement": "Knowledge retrieval returns valid, non-trivial results with all reliability data populated",
        "scientific_domain": ScientificDomain.RETRIEVAL,
        "supporting_experiment_ids": ["EXP-004"],
        "acceptance_metric": "recall_at_k",
        "acceptance_threshold": 0.85,
        "research_question": "Does Phase 9 search() return structurally valid, reliability-populated claims?",
        "null_hypothesis": "H₀: Recall@K < 0.85 (significant fraction of results are invalid)",
        "assumptions": ("ASMP-002", "ASMP-003"),
        "threats": ("THR-002",),
        "supporting_limitations": ("LIM-003", "LIM-004"),
        "applicability": "Phase 9 KnowledgeAccessService on fully processed SMRITI vault",
    },
    {
        "claim_id": "RC-005",
        "statement": "Reliability scores are calibrated [0,100] and ranking is stable across identical runs",
        "scientific_domain": ScientificDomain.RELIABILITY_SCORING,
        "supporting_experiment_ids": ["EXP-005"],
        "acceptance_metric": "ranking_stability",
        "acceptance_threshold": 0.85,
        "research_question": "Are Phase 8 reliability scores consistent and properly bounded?",
        "null_hypothesis": "H₀: Ranking stability < 0.85 (non-determinism in scoring)",
        "assumptions": ("ASMP-005",),  # Policy weights reflect epistemological importance
        "threats": ("THR-003",),       # Reliability Index is policy-driven
        "supporting_limitations": ("LIM-002",),
        "applicability": "SMRITI v2 Phase 8 with BALANCED policy profile",
    },
    {
        "claim_id": "RC-006",
        "statement": "Every reliability score is fully explainable: decomposable to component contributions with complete audit trail",
        "scientific_domain": ScientificDomain.EXPLAINABILITY,
        "supporting_experiment_ids": ["EXP-006"],
        "acceptance_metric": "completeness",
        "acceptance_threshold": 1.0,
        "research_question": "Does every reliability score have a complete, faithful, traceable explanation?",
        "null_hypothesis": "H₀: Completeness < 1.0 (some claims lack full explanation)",
        "assumptions": ("ASMP-006",),  # Component sum = valid faithfulness proxy
        "threats": ("THR-001",),
        "supporting_limitations": ("LIM-004",),
        "applicability": "SMRITI v2 Phase 9 explain() at FULL_AUDIT level",
    },
]


def assess_research_claims(
    experiment_results: List[ExperimentResult],
) -> List[ResearchClaim]:
    """Assess enriched research claims against experimental evidence."""
    result_map: Dict[str, ExperimentResult] = {r.experiment_id: r for r in experiment_results}
    assessed = []

    for spec in RESEARCH_CLAIMS_SPEC:
        exp_ids = spec["supporting_experiment_ids"]
        metric = spec["acceptance_metric"]
        threshold = spec["acceptance_threshold"]

        supporting_values = []
        evidence_ids = []

        for exp_id in exp_ids:
            result = result_map.get(exp_id)
            if result and metric in result.metrics:
                value = result.metrics[metric]
                supporting_values.append(value)
                evidence_ids.append(f"EV-{exp_id}-{metric}")

        n = len(supporting_values)
        if n >= 3:      grade = EvidenceGrade.A
        elif n == 2:    grade = EvidenceGrade.B
        elif n == 1:    grade = EvidenceGrade.C
        else:           grade = EvidenceGrade.E

        if not supporting_values:
            is_supported, confidence = False, 0.0
        else:
            avg = sum(supporting_values) / len(supporting_values)
            is_supported = avg >= threshold
            confidence = min(1.0, avg / max(threshold, 0.01))

        # RECTIFIED (P0-3): Construct enriched ResearchClaim
        assessed.append(ResearchClaim(
            claim_id=spec["claim_id"],
            statement=spec["statement"],
            scientific_domain=spec["scientific_domain"],
            evidence_ids=tuple(evidence_ids),
            evidence_grade=grade,
            is_supported=is_supported,
            confidence_score=round(confidence, 4),
            research_question=spec.get("research_question", ""),
            null_hypothesis=spec.get("null_hypothesis", ""),
            assumptions=spec.get("assumptions", ()),
            threats=spec.get("threats", ()),
            supporting_limitations=spec.get("supporting_limitations", ()),
            applicability=spec.get("applicability", ""),
        ))

    return assessed