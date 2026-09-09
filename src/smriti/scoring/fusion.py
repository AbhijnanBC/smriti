"""
fusion.py — Generic Reliability Fusion Engine for Phase 8.

RECTIFIED (P0-2): Fusion receives ContributionSet, NOT SignalVector.
Fusion never references any signal by name — it processes whatever
ContributionCandidates are registered, with their weights and directions.

This means:
    - Adding a new signal (e.g., NoveltySignal) requires ZERO changes here
    - Fusion works on any set of signals
    - Policy interactions that reference specific signals are documented
      in _apply_policy_interactions() and flagged in ReliabilityDecisionRecord

RECTIFIED (P0-5): Every call to compute_reliability() produces a
ReliabilityDecisionRecord documenting:
    - Which policy interactions fired
    - Which constraints were activated
    - The contribution order
    - Raw vs constrained vs final reliability

Architectural invariants:
    ✅ Deterministic: same ContributionSet + same policy → same RI
    ✅ Generic: Fusion never contains signal names (except in interactions)
    ✅ Every contribution traceable (ComponentScore)
    ✅ Every decision recorded (ReliabilityDecisionRecord)
    ❌ Fusion never reads the graph directly
    ❌ Fusion never imports signal extractors
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import (
    ContributionSet, ContributionCandidate, ComponentScore,
    ReliabilityDecisionRecord, SignalVector,
)
from smriti.scoring.policies import FusionPolicy, ReliabilityPolicy

logger = structlog.get_logger(__name__)

FUSION_ALGORITHM_VERSION = "weighted_linear_v2"   # Bumped for generic fusion


def compute_reliability(
    contribution_set: ContributionSet,
    policy: ReliabilityPolicy,
    signal_vector: SignalVector,        # Still needed for constraint checks
) -> Tuple[float, float, List[ComponentScore], ReliabilityDecisionRecord]:
    """
    Compute Reliability Index, Uncertainty Score, ComponentScores, and DecisionRecord.

    RECTIFIED (P0-2): Receives ContributionSet (generic), not SignalVector (named).
    RECTIFIED (P0-5): Returns ReliabilityDecisionRecord alongside the scores.

    Args:
        contribution_set:  Generic set of ContributionCandidates from normalization.
        policy:            Active ReliabilityPolicy.
        signal_vector:     For constraint evaluation and uncertainty (backward compat).

    Returns:
        (reliability_index, uncertainty_score, component_scores, decision_record)
    """
    fp = policy.fusion
    policy_interactions: List[str] = []
    constraints_activated: List[str] = []

    # ── Step 1: Policy interactions (before contribution building) ────────────
    # Interactions are documented but do not use signal names directly in Fusion.
    # They work by looking up candidates by name (only place signal names appear here).
    adjusted_candidates = _apply_policy_interactions(
        list(contribution_set.candidates), policy, policy_interactions
    )

    # ── Step 2: Build ComponentScores (generic — no signal name references) ───
    component_scores: List[ComponentScore] = []
    for candidate in adjusted_candidates:
        if candidate.direction == "positive":
            contribution = candidate.normalized_value * candidate.policy_weight * 100
        else:
            contribution = -(candidate.normalized_value * candidate.policy_weight * 100)

        component_scores.append(ComponentScore(
            signal_id=candidate.signal_id,
            normalized_value=candidate.normalized_value,
            policy_weight=candidate.policy_weight,
            adjusted_value=candidate.normalized_value,
            contribution=contribution,
            direction=candidate.direction,
            explanation=_build_signal_explanation(candidate.signal_id, candidate.normalized_value, candidate.direction),
        ))

    # ── Step 3: Raw fusion ────────────────────────────────────────────────────
    raw_reliability = sum(c.contribution for c in component_scores)

    # ── Step 4: Constraint validation ─────────────────────────────────────────
    constrained_reliability = _apply_constraints(
        raw_reliability, signal_vector, fp, constraints_activated
    )

    # ── Step 5: Clamp ─────────────────────────────────────────────────────────
    reliability_index = max(0.0, min(100.0, constrained_reliability))

    # ── Step 6: Uncertainty Score ─────────────────────────────────────────────
    uncertainty_score, uncertainty_components = _compute_uncertainty(signal_vector, fp)

    # ── Step 7: Build contribution order (descending |contribution|) ──────────
    contribution_order = tuple(
        c.signal_id
        for c in sorted(component_scores, key=lambda c: abs(c.contribution), reverse=True)
    )

    # ── Step 8: Build ReliabilityDecisionRecord (P0-5) ────────────────────────
    dominant_adj = policy_interactions[0] if policy_interactions else "none"
    decision_record = ReliabilityDecisionRecord(
        claim_id=contribution_set.claim_id,
        policy_interactions=tuple(policy_interactions),
        constraints_activated=tuple(constraints_activated),
        contribution_order=contribution_order,
        raw_reliability=round(raw_reliability, 4),
        constrained_reliability=round(constrained_reliability, 4),
        final_reliability=round(reliability_index, 4),
        uncertainty_components=tuple(uncertainty_components),
        dominant_adjustment=dominant_adj,
    )

    logger.debug(
        "reliability computed",
        claim_id=contribution_set.claim_id[:8],
        raw=f"{raw_reliability:.2f}",
        constrained=f"{constrained_reliability:.2f}",
        final=f"{reliability_index:.2f}",
        uncertainty=f"{uncertainty_score:.2f}",
        interactions=len(policy_interactions),
        constraints=len(constraints_activated),
    )

    return reliability_index, uncertainty_score, component_scores, decision_record


def _apply_policy_interactions(
    candidates: List[ContributionCandidate],
    policy: ReliabilityPolicy,
    interactions_log: List[str],
) -> List[ContributionCandidate]:
    """
    Apply policy interactions to adjust candidate values before fusion.

    NOTE: This is the ONLY place in Fusion where signal names may appear,
    because interactions are inherently signal-aware (e.g., echo chamber
    connects evidence_independence to evidence_strength). These are documented
    and localized here to minimize coupling.

    Any interaction that fires is logged to interactions_log.
    """
    candidates_map = {c.signal_id: c for c in candidates}

    # Interaction 1: Echo chamber discount
    # If evidence_independence is low, discount evidence_strength
    independence = candidates_map.get("evidence_independence")
    evidence = candidates_map.get("evidence_strength")
    if (independence and evidence
            and independence.normalized_value < policy.evidence.independence_discount_threshold):
        discount = policy.evidence.echo_chamber_penalty
        new_value = evidence.normalized_value * (1.0 - discount)
        new_candidate = ContributionCandidate(
            signal_id=evidence.signal_id,
            normalized_value=new_value,
            policy_weight=evidence.policy_weight,
            direction=evidence.direction,
            label=evidence.label,
            raw_value=evidence.raw_value,
        )
        candidates_map["evidence_strength"] = new_candidate
        interactions_log.append(
            f"echo_chamber_discount_applied: evidence_strength {evidence.normalized_value:.3f}"
            f" → {new_value:.3f} (independence={independence.normalized_value:.3f})"
        )

    return list(candidates_map.values())


def _apply_constraints(
    raw_ri: float,
    sv: SignalVector,
    fp: FusionPolicy,
    constraints_log: List[str],
) -> float:
    """Execute the ConstraintPipeline."""
    from smriti.scoring.constraints import CONSTRAINT_PIPELINE
    
    result = raw_ri
    for constraint in CONSTRAINT_PIPELINE:
        result, log_msg = constraint.apply(result, sv, fp)
        if log_msg:
            constraints_log.append(log_msg)
            
    return result


def _compute_uncertainty(
    sv: SignalVector,
    fp: FusionPolicy,
) -> Tuple[float, List[Tuple[str, float]]]:
    """
    Compute uncertainty score and decompose into named components.

    RECTIFIED (P0-12): a claim under active dispute (high conflict_pressure)
    was previously only penalized in reliability_index, never in
    uncertainty_score -- the two are distinct published metrics, and a
    heavily-contested claim is definitionally MORE uncertain, not merely
    less reliable. conflict_pressure is already a [0,1] "how contested is
    this claim" signal (see signals/conflict.py), so it is added directly
    (not inverted, unlike the evidence-sufficiency components below) as a
    fourth weighted component.
    """
    incompleteness = 1.0 - sv.evidence_completeness
    low_diversity = 1.0 - sv.source_diversity
    low_independence = 1.0 - sv.evidence_independence
    contested = sv.conflict_pressure

    components = [
        ("evidence_incompleteness", incompleteness * 0.35),
        ("low_source_diversity", low_diversity * 0.20),
        ("low_independence", low_independence * 0.20),
        ("conflict_pressure", contested * 0.25),
    ]

    raw_uncertainty = sum(v for _, v in components) * 100.0
    uncertainty_score = min(100.0, max(0.0, raw_uncertainty))
    return uncertainty_score, components


def _build_signal_explanation(
    signal_id: str,
    value: float,
    direction: str,
) -> str:
    """Generic explanation for a signal contribution."""
    label = signal_id.replace("_", " ").capitalize()
    if direction == "positive":
        if value >= 0.80:
            return f"{label}: very high ({value:.2f}). Strong positive contribution."
        elif value >= 0.50:
            return f"{label}: moderate ({value:.2f}). Positive contribution."
        elif value > 0.10:
            return f"{label}: low ({value:.2f}). Limited positive contribution."
        else:
            return f"{label}: negligible ({value:.2f}). Minimal contribution."
    else:
        if value >= 0.80:
            return f"{label}: very high ({value:.2f}). Strong negative pressure."
        elif value >= 0.50:
            return f"{label}: moderate ({value:.2f}). Notable negative pressure."
        elif value > 0.10:
            return f"{label}: low ({value:.2f}). Weak negative pressure."
        else:
            return f"{label}: negligible ({value:.2f}). No significant pressure."


# ── Backward-compatible wrapper for tests that use old signature ───────────────

def compute_reliability_from_signal_vector(
    signal_vector: SignalVector,
    policy: ReliabilityPolicy,
) -> Tuple[float, float, List[ComponentScore]]:
    """
    Backward-compatible wrapper for existing tests.
    Converts SignalVector to ContributionSet and calls the generic fusion.
    """
    from smriti.core.models import ContributionCandidate, ContributionSet

    fp = policy.fusion
    candidates = []
    for signal_id, weight in fp.signal_weights.items():
        direction = fp.get_direction(signal_id)
        # Get value from signal_vector by signal_id
        value = getattr(signal_vector, signal_id, 0.0)
        if weight > 0:
            candidates.append(ContributionCandidate(
                signal_id=signal_id,
                normalized_value=value,
                policy_weight=weight,
                direction=direction,
                label=signal_id.replace("_", " ").title(),
                raw_value=value,
            ))

    cs = ContributionSet(
        candidates=tuple(candidates),
        evidence_completeness=signal_vector.evidence_completeness,
        claim_id="test",
    )

    ri, unc, comps, _ = compute_reliability(cs, policy, signal_vector)
    return ri, unc, comps