from abc import ABC, abstractmethod
from typing import Tuple, Optional
from smriti.core.models import SignalVector
from smriti.scoring.policies import FusionPolicy

class FusionConstraint(ABC):
    @abstractmethod
    def apply(self, current_ri: float, sv: SignalVector, fp: FusionPolicy) -> Tuple[float, Optional[str]]:
        """Returns (new_ri, activation_log_message)."""
        pass

class NoEvidenceConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        cap = fp.max_reliability_without_evidence
        if sv.evidence_strength < 0.10 and current_ri > cap:
            return cap, f"no_evidence_cap: {cap}"
        return current_ri, None

class MaxConflictConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        cap = fp.max_reliability_with_max_conflict
        if sv.conflict_pressure >= 0.90 and current_ri > cap:
            return cap, f"max_conflict_cap: {cap}"
        return current_ri, None

class TopologyWithoutEvidenceConstraint(FusionConstraint):
    def apply(self, current_ri, sv, fp):
        if sv.evidence_strength < 0.20 and sv.topology_strength > 0.80 and current_ri > 60.0:
            return 60.0, "topology_without_evidence_cap: 60.0"
        return current_ri, None

CONSTRAINT_PIPELINE = [
    NoEvidenceConstraint(),
    MaxConflictConstraint(),
    TopologyWithoutEvidenceConstraint(),
]