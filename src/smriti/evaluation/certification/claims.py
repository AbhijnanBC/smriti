"""
claims.py — Research Claims Matrix (FROZEN v2).

FROZEN (post-review rectification): exactly five canonical research claims,
matching the paper 1:1. There is no separate "repository registry" that
disagrees with the paper anymore — this file IS the single source of truth,
and the paper must be generated from these identifiers, never the reverse.

    RC1 — Claim Extraction
    RC2 — Semantic Relationship Resolution
    RC3 — Contradiction-Safe Graph Partitioning
    RC4 — Evidence-Aware Reliability
    RC5 — Faithful Explainability

Anything not in this list (embedding determinism, retrieval index
correctness, dashboard behavior, runtime governance, ...) is engineering
validation (ECI / architectural rules), not a research claim, and must
never be reported as scientific evidence.

Each claim's supporting experiment (evaluation/scientific/experiment.py)
either measures the claim against real reference data or reports
NOT_EVALUABLE — it never fabricates a number to avoid an empty cell.
"""

from __future__ import annotations

from smriti.core.models import (
    EvidenceGrade,
    ExperimentResult,
    ResearchClaim,
    ScientificDomain,
    VerificationStatus,
)

# RECTIFIED (P0-B, "FINAL REVIEW" round): the single source of truth for
# which claim/experiment IDs are actually canonical, so other modules
# (assumptions.py, integrity checks) can validate against this instead of
# a second hardcoded copy that can drift out of sync -- exactly how the
# assumption registry's RC-00N identifiers went stale.
CANONICAL_CLAIM_IDS = frozenset({"RC1", "RC2", "RC3", "RC4", "RC5"})
CANONICAL_EXPERIMENT_IDS = frozenset({"EXP-001", "EXP-002", "EXP-003", "EXP-004", "EXP-005"})

# RECTIFIED (P1-B, "FINAL REVIEW" round): evidence grade must reflect the
# QUALITY/PROVENANCE of the evidence behind a claim, not how many
# ExperimentResult objects happen to be registered for it. Under the
# retired rule (n_supporting_values >= 3 -> A, ==2 -> B, ==1 -> C, else E),
# a claim measured by five purely synthetic self-consistency checks could
# outrank one independently-annotated external benchmark measured once --
# scientifically backwards, since it rewards experiment-registration count
# rather than evidence strength. Each claim below now declares what KIND
# of evidence actually backs it via "evidence_provenance", and its grade
# is that provenance category's grade whenever real supporting_values
# exist (E otherwise) -- never inflated by re-running the same kind of
# evidence more times.
EVIDENCE_PROVENANCE_GRADE: dict[str, EvidenceGrade] = {
    "human_labeled_benchmark": EvidenceGrade.A,
    "public_benchmark_independent_annotation": EvidenceGrade.B,
    "independent_llm_reference_annotation": EvidenceGrade.C,
    "construction_defined_synthetic_benchmark": EvidenceGrade.C,
    "self_consistency_or_reconstruction_test": EvidenceGrade.D,
    "structural_invariant_check": EvidenceGrade.D,
}

RESEARCH_CLAIMS_SPEC = [
    {
        "claim_id": "RC1",
        # RECTIFIED (external review item 19): "semantically faithful" overclaimed
        # what RC1's own metric (extraction_precision_on_agreed_subset) measures --
        # a binary valid/invalid structural judgment (is this a real declarative
        # assertion, or extraction noise), not semantic entailment from the source
        # sentence. The statement now matches the research_question below exactly.
        "statement": "SMRITI extracts structurally valid declarative claims from heterogeneous note-style text",
        "scientific_domain": ScientificDomain.KNOWLEDGE_EXTRACTION,
        "supporting_experiment_ids": ["EXP-001"],
        "acceptance_metric": "precision",
        "acceptance_threshold": 0.70,
        "research_question": "What fraction of SMRITI's extracted claims are structurally valid declarative assertions, judged against an independent reference annotation?",
        "null_hypothesis": "H0: extraction precision against the reference annotation is < 0.70",
        "assumptions": ("ASMP-001",),
        "threats": ("THR-001",),
        "supporting_limitations": ("LIM-001", "LIM-004"),
        "applicability": "SMRITI-Reference corpus, LLM-derived reference annotation (see Limitations: not a human-annotation substitute)",
        "evidence_provenance": "independent_llm_reference_annotation",
    },
    {
        "claim_id": "RC2",
        # RECTIFIED (P0-C, "FINAL REVIEW" round): the statement previously
        # named only 4 relation types (SUPPORTS/CONTRADICTS/REFINES/
        # NEUTRAL); EQUIVALENT has been a deliberate, first-class 5th
        # relation type since the bidirectional-NLI rewrite, and the
        # annotation protocol explicitly distinguishes it. ABSTAINED is a
        # resolution status the resolver can reach, not a 6th relation to
        # classify against -- it is named explicitly here so this
        # statement cannot be misread as claiming a 6-way classification.
        "statement": "SMRITI's embedding-retrieval + bidirectional-NLI pipeline distinguishes SUPPORTS, CONTRADICTS, REFINES, EQUIVALENT, and NEUTRAL relationships on the defined evaluation set, while representing unresolved cases separately as ABSTAINED",
        "scientific_domain": ScientificDomain.RELATIONSHIP_RESOLUTION,
        "supporting_experiment_ids": ["EXP-002"],
        "acceptance_metric": "macro_f1",
        "acceptance_threshold": 0.60,
        "research_question": "Does SMRITI's relationship classifier achieve acceptable macro-F1 (over all 5 relation classes) against an independent reference annotation, including on deliberately-planted hard contradiction pairs, and separately, how accurately does it recover direction on the subset of pairs with a determinate gold direction?",
        "null_hypothesis": "H0: relationship classification macro-F1 against the reference annotation is < 0.60",
        "assumptions": ("ASMP-004",),
        "threats": ("THR-003", "THR-006"),
        "supporting_limitations": ("LIM-004", "LIM-005"),
        # RECTIFIED (P0-C): frozen at the current reference-annotation
        # round's own parameters -- N=196 (228 sampled, 32 excluded as
        # either pass's UNSURE), inter-pass kappa=0.726, 5 relation
        # classes, ABSTAINED as a status not a class. Re-freeze this
        # string whenever evaluation/annotation/score.py's reference round
        # changes, rather than letting it silently describe a prior round.
        "applicability": "SMRITI-Reference corpus, LLM-derived reference annotation (N=196 agreed pairs of 228 sampled, inter-pass kappa=0.726, 5 relation classes + ABSTAINED status; direction evaluated separately on the determinate-gold-direction subset)",
        "evidence_provenance": "independent_llm_reference_annotation",
    },
    {
        "claim_id": "RC3",
        "statement": "SMRITI's constraint-based graph partitioning guarantees no two directly-contradicting claims are ever assigned to the same partition",
        "scientific_domain": ScientificDomain.KNOWLEDGE_GRAPH,
        "supporting_experiment_ids": ["EXP-003"],
        "acceptance_metric": "contradiction_violation_rate",
        "acceptance_threshold": 0.0,
        # RECTIFIED (P0-A, "FINAL REVIEW" round): acceptance for this claim
        # is INVERTED -- lower is better, and the required value is a
        # maximum, not a minimum. This is now the ONE place that fact is
        # declared (assess_research_claims() reads acceptance_direction
        # from this spec rather than hardcoding `claim_id == "RC3"`), and
        # it matches evaluation/scientific/experiment.py's EXP-003
        # acceptance_directions -- two independent declarations of the
        # SAME fact (claim-level here, experiment-level there), not one
        # hardcoded in two places by accident.
        "acceptance_direction": "lower_is_better",
        "research_question": "Does Phase 7's 2-coloring + union-find partitioning ever place two claims connected by a CONTRADICTS edge into the same partition?",
        "null_hypothesis": "H0: the contradiction-within-partition violation rate is > 0 (the structural invariant does not hold)",
        "assumptions": ("ASMP-004",),
        "threats": ("THR-006",),
        "supporting_limitations": ("LIM-005",),
        "applicability": "Any knowledge graph SMRITI's Phase 7 constructs — this claim is about the STRUCTURAL invariant, not about whether individual CONTRADICTS predictions are semantically correct (that is RC2's concern).",
        "evidence_provenance": "structural_invariant_check",
    },
    {
        "claim_id": "RC4",
        "statement": "SMRITI's evidence-aware reliability fusion responds monotonically and predictably to controlled evidence perturbations",
        "scientific_domain": ScientificDomain.RELIABILITY_SCORING,
        "supporting_experiment_ids": ["EXP-004"],
        "acceptance_metric": "monotonicity_pass_rate",
        "acceptance_threshold": 0.90,
        "research_question": "Does adding independent supporting evidence increase reliability, does adding a contradiction decrease it, and does adding a duplicate-source claim leave source-diversity/independence unchanged, as metamorphic relations require?",
        "null_hypothesis": "H0: fewer than 90% of metamorphic reliability-perturbation tests pass",
        # RECTIFIED (P0-B): ASMP-008 (the static 10% conflict-penalty
        # proxy) is a real assumption underlying this fusion and was
        # previously orphaned -- affected_claims=("RC-005",) on the
        # assumption record itself never matched any canonical claim ID,
        # so it was invisible to get_assumptions_for_claim("RC4").
        "assumptions": ("ASMP-005", "ASMP-008"),
        "threats": ("THR-003",),
        "supporting_limitations": ("LIM-002",),
        "applicability": "SMRITI Phase 8 with the BALANCED policy profile, evaluated via metamorphic testing (no external gold label required)",
        "evidence_provenance": "self_consistency_or_reconstruction_test",
    },
    {
        "claim_id": "RC5",
        "statement": "Every reliability score is exactly reconstructible from its recorded signal contributions and constraint adjustments",
        "scientific_domain": ScientificDomain.EXPLAINABILITY,
        "supporting_experiment_ids": ["EXP-005"],
        "acceptance_metric": "reconstruction_exact_match_rate",
        "acceptance_threshold": 1.0,
        "research_question": "For every scored claim, does raw_reliability = sum(component contributions), and does final_reliability follow deterministically from raw_reliability through the recorded constraint adjustments, within numerical tolerance?",
        "null_hypothesis": "H0: fewer than 100% of scored claims' final reliability values are exactly reconstructible from their own audit trail",
        "assumptions": ("ASMP-006",),
        "threats": ("THR-001",),
        "supporting_limitations": ("LIM-004",),
        "applicability": "Every claim scored by SMRITI Phase 8, regardless of policy profile — this is a self-consistency check on the audit trail, not an external validity claim",
        "evidence_provenance": "self_consistency_or_reconstruction_test",
    },
]


def assess_research_claims(
    experiment_results: list[ExperimentResult],
) -> list[ResearchClaim]:
    """Assess the five frozen research claims against experimental evidence.

    A claim whose supporting experiment(s) returned NOT_EVALUABLE is itself
    reported as NOT SUPPORTED with confidence 0.0 and evidence_grade E — it
    is never silently treated as passing, and the ResearchClaim carries the
    NOT_EVALUABLE status forward so the certification report can display it
    honestly rather than as a generic "unsupported".
    """
    result_map: dict[str, ExperimentResult] = {r.experiment_id: r for r in experiment_results}
    assessed = []

    for spec in RESEARCH_CLAIMS_SPEC:
        exp_ids = spec["supporting_experiment_ids"]
        metric = spec["acceptance_metric"]
        threshold = spec["acceptance_threshold"]
        # RECTIFIED (P0-A): read direction from the spec itself rather than
        # hardcoding a claim_id check -- see RC3's "acceptance_direction" above.
        inverted = spec.get("acceptance_direction", "higher_is_better") == "lower_is_better"

        supporting_values = []
        evidence_ids = []
        any_not_evaluable = False

        for exp_id in exp_ids:
            result = result_map.get(exp_id)
            if result is None:
                continue
            if result.status == VerificationStatus.NOT_EVALUABLE:
                any_not_evaluable = True
                continue
            if metric in result.metrics:
                value = result.metrics[metric]
                supporting_values.append(value)
                evidence_ids.append(f"EV-{exp_id}-{metric}")

        if any_not_evaluable and not supporting_values:
            # No real measurement exists at all — report plainly, do not
            # invent a confidence score.
            assessed.append(
                ResearchClaim(
                    claim_id=spec["claim_id"],
                    statement=spec["statement"],
                    scientific_domain=spec["scientific_domain"],
                    evidence_ids=(),
                    evidence_grade=EvidenceGrade.E,
                    is_supported=False,
                    confidence_score=0.0,
                    research_question=spec.get("research_question", ""),
                    null_hypothesis=spec.get("null_hypothesis", ""),
                    assumptions=spec.get("assumptions", ()),
                    threats=spec.get("threats", ()),
                    supporting_limitations=spec.get("supporting_limitations", ()),
                    applicability=spec.get("applicability", "")
                    + " [NOT_EVALUABLE: no reference data available for this run]",
                )
            )
            continue

        # RECTIFIED (P1-B): grade reflects evidence provenance/quality, not
        # how many ExperimentResult rows happened to be registered.
        grade = (
            EVIDENCE_PROVENANCE_GRADE.get(spec.get("evidence_provenance"), EvidenceGrade.E)
            if supporting_values
            else EvidenceGrade.E
        )

        if not supporting_values:
            is_supported, confidence = False, 0.0
        else:
            avg = sum(supporting_values) / len(supporting_values)
            if inverted:
                is_supported = avg <= threshold
                # Confidence for an inverted (lower-is-better) metric: 1.0 at
                # avg==0, decaying as avg grows past the threshold. Avoid
                # division by a zero threshold.
                confidence = 1.0 if avg <= threshold else max(0.0, 1.0 - avg)
            else:
                is_supported = avg >= threshold
                confidence = min(1.0, avg / max(threshold, 0.01))

        assessed.append(
            ResearchClaim(
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
            )
        )

    return assessed
