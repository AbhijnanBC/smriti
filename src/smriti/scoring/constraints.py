from abc import ABC, abstractmethod

from smriti.core.models import SignalVector
from smriti.scoring.policies import FusionPolicy


class FusionConstraint(ABC):
    @abstractmethod
    def apply(
        self, current_ri: float, sv: SignalVector, fp: FusionPolicy
    ) -> tuple[float, str | None]:
        """Returns (new_ri, activation_log_message)."""
        pass


class NoEvidenceConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        # The constraint is "activated" (recorded for audit/explainability)
        # whenever its triggering condition holds, regardless of whether the
        # cap actually needs to reduce current_ri — a claim with no evidence
        # is a fact worth recording even if its raw score already happens to
        # sit below the cap.
        cap = fp.max_reliability_without_evidence
        if sv.evidence_strength < 0.10:
            return min(current_ri, cap), f"no_evidence_cap: {cap}"
        return current_ri, None


class MaxConflictConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        cap = fp.max_reliability_with_max_conflict
        if sv.conflict_pressure >= 0.90:
            return min(current_ri, cap), f"max_conflict_cap: {cap}"
        return current_ri, None


class TopologyWithoutEvidenceConstraint(FusionConstraint):
    """
    RETIRED (P1-4, external "reality check" review — reliability vs. graph
    importance conflation): this constraint used a graph-structure signal
    (topology_strength) to cap an evidence-based score, which is exactly the
    conflation the review flagged -- reliability_index is now computed from
    evidence-family signals only (see policies.EVIDENCE_SIGNAL_NAMES), so it
    has nothing to gain from being told "topology is high" in the first
    place, and importance_index (computed from topology-family signals only)
    has no evidence_strength to check. Kept only so its history is not lost;
    intentionally excluded from both EVIDENCE_CONSTRAINT_PIPELINE and
    IMPORTANCE_CONSTRAINT_PIPELINE below.
    """

    def apply(self, current_ri, sv, fp):
        if sv.evidence_strength < 0.20 and sv.topology_strength > 0.80:
            return min(current_ri, 60.0), "topology_without_evidence_cap: 60.0"
        return current_ri, None


# RECTIFIED (P1-4): constraints are now split by which of the two indices
# they legitimately govern. Evidence-native constraints (no evidence,
# max conflict) apply to reliability_index; no importance-native
# constraint currently exists, so that pipeline is empty pending real
# scientific justification for one.
EVIDENCE_CONSTRAINT_PIPELINE = [
    NoEvidenceConstraint(),
    MaxConflictConstraint(),
]

IMPORTANCE_CONSTRAINT_PIPELINE = []

# Backward-compatible default used by compute_reliability() when no
# constraint_pipeline is explicitly supplied (legacy, unsplit callers).
CONSTRAINT_PIPELINE = EVIDENCE_CONSTRAINT_PIPELINE
