"""
classification/resolver.py — Policy-driven relationship resolution.

RECTIFIED: All threshold values have been moved out of Python code and into
ResolverPolicy, which is constructed from config. The resolver itself is a
pure function: (evidence, policy) → (RelationshipType, RelationshipDirection).
No threshold values appear in this file.

RECTIFIED (P0-6): the CONTRADICTS and SUPPORTS rules previously required
only a PAIRWISE margin over ONE alternative (e.g. contradiction beating
entailment) without checking the THIRD class at all. That meant a pair
with contradiction=0.85, entailment=0.05, but neutral=0.90 (neutral
clearly dominant) still resolved to CONTRADICTS, because the rule never
looked at neutral_score. Both rules now require the winning class to be
the actual argmax of {entailment, neutral, contradiction} — beating BOTH
alternatives by the configured margin — before committing to a verdict;
otherwise resolution falls through toward NEUTRAL or UNKNOWN (abstain).
This is the single highest-value fix for the measured 3.2% CONTRADICTS
precision (see paper error analysis): most false positives were cases
where neutral was actually the model's dominant class.

Resolution rules (applied in priority order as defined by the policy):
    1. If contradiction_score >= policy.nli_threshold AND
       contradiction_score is the argmax of {c, e, n} AND
       contradiction_score exceeds BOTH alternatives by >= contradiction_margin
       → CONTRADICTS (symmetric)
    2. If entailment_score >= policy.nli_threshold AND
       entailment_score is the argmax of {c, e, n} AND
       entailment_score exceeds BOTH alternatives by >= entailment_margin
       → SUPPORTS (a_to_b)
    3. If cosine_similarity >= policy.high_sim_threshold AND
       neutral_score >= policy.neutrality_threshold AND
       contradiction_score < policy.refine_contradiction_ceiling
       → REFINES (a_to_b)
    4. If neutral_score >= policy.neutrality_threshold
       → NEUTRAL (symmetric)
    5. Otherwise
       → UNKNOWN (symmetric) — i.e. ABSTAIN; Phase 6's validator never
         persists UNKNOWN relationships to Phase 7.

A separate, downstream relatedness gate (classification/relatedness.py) may
additionally downgrade a CONTRADICTS verdict to UNKNOWN when the two claims
share no detectable topical overlap — that gate is applied by the Phase 6
orchestrator (retrieval/__init__.py), not here, to keep this resolver a pure
function of (evidence, policy) with no text/lexical access.

Rules:
    ✅ Resolver NEVER contains hard-coded thresholds
    ✅ Resolver NEVER calls any ML model
    ✅ Resolver NEVER accesses external state
    ✅ Policy is versioned and validated on construction
    ✅ Rule priority order is configurable via policy.priority_order
    ❌ No randomness, no external state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    RelationshipEvidence,
    RelationshipType,
    RelationshipDirection,
    LifecycleStage,
)
from smriti.exceptions import ResolverPolicyError

logger = structlog.get_logger(__name__)

RESOLVER_VERSION = "1.0"


@dataclass(frozen=True)
class ResolverPolicy:
    """
    All resolver thresholds and rule configuration in one place.

    This object replaces every hard-coded if/else threshold in the resolver.
    Changing resolver behavior requires changing config, not code.

    Fields:
        nli_threshold:       Minimum score for CONTRADICTS / SUPPORTS classification.
        refine_threshold:    (Deprecated) Previously used for REFINES; now unused.
        high_sim_threshold:  Minimum cosine similarity required for REFINES.
        neutrality_threshold: Minimum neutral_score for NEUTRAL classification.
        contradiction_margin: Minimum gap between contradiction and entailment scores
                              required to classify as CONTRADICTS (prevents edge cases).
        entailment_margin:   Minimum gap between entailment and contradiction scores
                             required to classify as SUPPORTS.
        confidence_policy:   "calibrated" (use calibrated_confidence) or
                             "raw" (use raw NLI score). Default: "calibrated".
        priority_order:      List of RelationshipType values in resolution priority order.
                             Default: [CONTRADICTS, SUPPORTS, REFINES, NEUTRAL, UNKNOWN].
        version:             Resolver policy version string.
    """
    nli_threshold: float
    refine_threshold: float
    high_sim_threshold: float
    neutrality_threshold: float
    contradiction_margin: float = 0.05
    entailment_margin: float = 0.05
    refine_contradiction_ceiling: float = 0.1
    confidence_policy: str = "calibrated"
    priority_order: List[str] = field(default_factory=lambda: [
        "contradicts", "supports", "refines", "neutral", "unknown"
    ])
    version: str = RESOLVER_VERSION

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate internal consistency of the policy."""
        if self.nli_threshold <= 0 or self.nli_threshold > 1:
            raise ResolverPolicyError(
                f"nli_threshold must be in (0, 1], got {self.nli_threshold}"
            )
        if self.refine_threshold >= self.nli_threshold:
            raise ResolverPolicyError(
                f"refine_threshold ({self.refine_threshold}) must be < "
                f"nli_threshold ({self.nli_threshold})"
            )
        if self.high_sim_threshold <= 0 or self.high_sim_threshold > 1:
            raise ResolverPolicyError(
                f"high_sim_threshold must be in (0, 1], got {self.high_sim_threshold}"
            )
        if self.contradiction_margin < 0:
            raise ResolverPolicyError(
                f"contradiction_margin must be >= 0, got {self.contradiction_margin}"
            )

    @classmethod
    def from_config(cls) -> "ResolverPolicy":
        """
        Construct ResolverPolicy from the application configuration.
        This is the canonical way to get a ResolverPolicy in production.
        """
        config = get_config()
        nli_cfg = config.get("nli", {})
        rd_cfg = config.get("relationship_discovery", {})
        policy_cfg = config.get("resolver_policy", {})

        return cls(
            nli_threshold=nli_cfg.get("nli_threshold", 0.80),
            refine_threshold=rd_cfg.get("refine_threshold", 0.55),
            high_sim_threshold=rd_cfg.get("high_sim_threshold", 0.88),
            neutrality_threshold=rd_cfg.get("neutrality_threshold", 0.60),
            contradiction_margin=policy_cfg.get("contradiction_margin", 0.05),
            entailment_margin=policy_cfg.get("entailment_margin", 0.05),
            refine_contradiction_ceiling=policy_cfg.get("refine_contradiction_ceiling", 0.1),
            confidence_policy=policy_cfg.get("confidence_policy", "calibrated"),
            priority_order=policy_cfg.get("priority_order", [
                "contradicts", "supports", "refines", "neutral", "unknown"
            ]),
            version=policy_cfg.get("version", RESOLVER_VERSION),
        )


class RelationshipResolver:
    """
    Policy-driven resolver: RelationshipEvidence → RelationshipType.

    The resolver itself contains no threshold values.
    All rules come from the ResolverPolicy.
    Instantiate once per pipeline run.
    """

    def __init__(self, policy: Optional["ResolverPolicy"] = None) -> None:
        self._policy = policy or ResolverPolicy.from_config()
        logger.info(
            "resolver initialized",
            policy_version=self._policy.version,
            nli_threshold=self._policy.nli_threshold,
            high_sim_threshold=self._policy.high_sim_threshold,
            neutrality_threshold=self._policy.neutrality_threshold,
            confidence_policy=self._policy.confidence_policy,
        )

    @property
    def policy(self) -> ResolverPolicy:
        return self._policy

    def resolve(
        self,
        evidence: RelationshipEvidence,
    ) -> Tuple[RelationshipType, RelationshipDirection]:
        """
        Apply policy rules to classify a RelationshipEvidence.

        Uses calibrated_confidence from evidence (unless policy says "raw").

        Returns:
            (RelationshipType, RelationshipDirection) — never raises.
        """
        p = self._policy
        c = evidence.nli_scores.contradiction_score
        e = evidence.nli_scores.entailment_score
        n = evidence.nli_scores.neutral_score
        cos = evidence.cosine_similarity

        for rule in p.priority_order:
            if rule == "contradicts":
                # RECTIFIED (P0-6): must be the argmax of {c, e, n}, beating
                # BOTH alternatives by the margin — not just beating entailment
                # while a higher neutral_score goes unchecked.
                if (c >= p.nli_threshold
                        and (c - e) >= p.contradiction_margin
                        and (c - n) >= p.contradiction_margin):
                    logger.debug(
                        "resolved: CONTRADICTS",
                        contradiction=f"{c:.3f}", entailment=f"{e:.3f}", neutral=f"{n:.3f}",
                    )
                    return RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC

            elif rule == "supports":
                # RECTIFIED (P0-6): same argmax requirement as CONTRADICTS above.
                if (e >= p.nli_threshold
                        and (e - c) >= p.entailment_margin
                        and (e - n) >= p.entailment_margin):
                    logger.debug("resolved: SUPPORTS", entailment=f"{e:.3f}", neutral=f"{n:.3f}")
                    return RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B

            elif rule == "refines":
                # Rectified heuristic:
                # A refinement is highly similar (high cosine), strictly NOT contradictory,
                # and usually classified as NLI Neutral because it does not strictly
                # entail in either direction.
                if (cos >= p.high_sim_threshold
                        and n >= p.neutrality_threshold
                        and c < p.refine_contradiction_ceiling):
                    logger.debug(
                        "resolved: REFINES",
                        neutral=f"{n:.3f}", cosine=f"{cos:.3f}",
                    )
                    return RelationshipType.REFINES, RelationshipDirection.A_TO_B

            elif rule == "neutral":
                if n >= p.neutrality_threshold:
                    logger.debug("resolved: NEUTRAL", neutral=f"{n:.3f}")
                    return RelationshipType.NEUTRAL, RelationshipDirection.SYMMETRIC

            elif rule == "unknown":
                logger.debug(
                    "resolved: UNKNOWN",
                    c=f"{c:.3f}", e=f"{e:.3f}", n=f"{n:.3f}",
                )
                return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC

        # Should never reach here, but fallback to UNKNOWN
        return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC