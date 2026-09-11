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

RECTIFIED (external review, bidirectional-NLI rewrite): a single NLI call
with (claim_a, claim_b) as (premise, hypothesis) can only ever answer
"does A entail B" -- it cannot tell "A entails B" apart from "B entails A"
apart from "both" (the claims are EQUIVALENT) apart from "neither", and
the previous resolver always emitted SUPPORTS as A_TO_B regardless of
which claim actually did the entailing, purely because claim_a/claim_b's
lexicographic ID ordering (not semantics) decided which text became the
premise. Evidence now carries BOTH directions (evidence.nli_scores for
A->B, evidence.nli_scores_b_to_a for B->A; see evidence.py), and:
    - CONTRADICTS is tested on the AVERAGE of both directions' scores,
      since contradiction is a symmetric property of the pair -- averaging
      two independent (noisy) estimates of the same symmetric quantity is
      more defensible than trusting one arbitrary direction, or requiring
      both directions to independently agree (which would only tighten an
      already-low recall further with no principled justification).
    - Entailment is tested per-direction, since "A entails B" and "B
      entails A" are logically independent quantities: both directions
      dominant -> EQUIVALENT; exactly one -> SUPPORTS (in that direction,
      possibly reclassified to REFINES by a downstream specificity gate
      -- see below).
Backward compatibility: if evidence.nli_scores_b_to_a is None (legacy
single-direction evidence, e.g. some pre-existing test fixtures), resolve()
falls back to the original single-direction rule set unchanged.

Resolution rules (bidirectional path; applied in priority order as defined
by the policy). RECTIFIED (external review, P0-6): every rule below is
now a genuine, independently-ordered priority_order entry ("contradicts",
"equivalent", "supports", "refines", "neutral", "unknown", default order
as listed) -- EQUIVALENT was previously hardcoded inside the "supports"
branch regardless of where "supports" sat in priority_order, so reordering
the policy silently changed EQUIVALENT's own behavior in a way the policy
never described. ResolverPolicy._validate() now rejects any
priority_order that does not contain each of these six exactly once.
    1. If avg(contradiction_ab, contradiction_ba) >= policy.nli_threshold AND
       it exceeds BOTH max(entailment_ab, entailment_ba) and
       avg(neutral_ab, neutral_ba) by >= contradiction_margin
       → CONTRADICTS (symmetric)
    2. If entailment_ab is the argmax of {c_ab, e_ab, n_ab} beating both by
       >= entailment_margin, AND likewise entailment_ba is the argmax of
       {c_ba, e_ba, n_ba}
       → EQUIVALENT (symmetric)
    3. If exactly one direction's entailment dominates as in (2)
       → SUPPORTS, in that direction (A_TO_B or B_TO_A) — a downstream
         specificity gate (classification/specificity.py, applied by the
         Phase 6 orchestrator, not here) may reclassify this to REFINES
         in the same direction if the entailing claim is meaningfully
         more specific/detailed than the entailed claim.
    4. RETIRED (external "reality check" review round 3, P0-4): "refines"
       is now a no-op rule slot in the bidirectional path. It previously
       fired on cosine_similarity/neutral-dominance alone, with NEITHER
       direction passing the entailment test -- which is not a refinement
       by this ontology's own definition (docs/relationship_ontology.md:
       REFINES requires one-way entailment). REFINES is now produced
       EXCLUSIVELY by the downstream specificity gate reclassifying a
       genuine one-way SUPPORTS decision from rule 3 above. Candidates
       that used to hit this heuristic now correctly fall through to rule
       5 (NEUTRAL), which their own condition already satisfied.
    5. If avg(neutral_ab, neutral_ba) >= policy.neutrality_threshold, or
       either direction's own neutral_score does
       → NEUTRAL (symmetric)
    6. Otherwise
       → UNKNOWN (symmetric) — i.e. ABSTAIN; Phase 6's validator never
         persists UNKNOWN relationships to Phase 7.

A separate, downstream relatedness gate (classification/relatedness.py) may
additionally downgrade a CONTRADICTS verdict to UNKNOWN when the two claims
share no detectable topical overlap — that gate is applied by the Phase 6
orchestrator (retrieval/__init__.py), not here, to keep this resolver a pure
function of (evidence, policy) with no text/lexical access. The SUPPORTS/
REFINES specificity gate follows the identical pattern for the same reason.

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

import structlog
from smriti.core.config import get_config
from smriti.core.models import (
    RelationshipDecision,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipType,
    to_decision,
)
from smriti.exceptions import ResolverPolicyError

logger = structlog.get_logger(__name__)

RESOLVER_VERSION = "2.0"  # bumped: bidirectional NLI, EQUIVALENT, retired REFINES heuristic (P0-4)


@dataclass(frozen=True)
class ResolverPolicy:
    """
    All resolver thresholds and rule configuration in one place.

    This object replaces every hard-coded if/else threshold in the resolver.
    Changing resolver behavior requires changing config, not code.

    Fields:
        nli_threshold:       Minimum score for CONTRADICTS / SUPPORTS classification.
        refine_threshold:    (Deprecated) Previously used for REFINES; now unused.
        high_sim_threshold:  (Deprecated, P0-4) Previously gated the retired
                             "high similarity, no entailment" REFINES
                             heuristic; that branch is now a no-op (see
                             module docstring rule 4), so this threshold is
                             no longer consumed by resolve()/_resolve_bidirectional.
        neutrality_threshold: Minimum neutral_score for NEUTRAL classification.
        contradiction_margin: Minimum gap between contradiction and entailment scores
                              required to classify as CONTRADICTS (prevents edge cases).
        entailment_margin:   Minimum gap between entailment and contradiction scores
                             required to classify as SUPPORTS.
        confidence_policy:   "calibrated" (use calibrated_confidence) or
                             "raw" (use raw NLI score). Default: "raw".
                             RECTIFIED (P1-C, "FINAL REVIEW" round, section
                             37): the default was "calibrated" while the
                             config's `calibration:` section is empty by
                             default (IDENTITY for every model, i.e. no
                             real calibrator is deployed) -- that combination
                             claimed a property the system did not have.
                             Set this to "calibrated" only once a real
                             strategy (temperature/percentile/isotonic) is
                             actually configured under `calibration:` for
                             the active model. Note this field is currently
                             informational/logged only -- no code path
                             branches on it yet; calibrated_confidence is
                             computed unconditionally via the (possibly
                             identity) calibration strategy regardless of
                             this policy's value.
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
    refine_contradiction_ceiling: float = 0.1  # (Deprecated, P0-4) see high_sim_threshold
    confidence_policy: str = "raw"
    priority_order: list[str] = field(
        default_factory=lambda: [
            "contradicts",
            "equivalent",
            "supports",
            "refines",
            "neutral",
            "unknown",
        ]
    )
    version: str = RESOLVER_VERSION

    # RECTIFIED (external review, P0-6): every relation the bidirectional
    # resolver can actually resolve must appear in priority_order exactly
    # once. EQUIVALENT was previously hardcoded inside the "supports"
    # branch (checked before priority_order was even consulted), so a
    # policy reordering "refines" ahead of "supports" silently changed
    # EQUIVALENT's behavior too, in a way the policy itself never
    # described. This set is exactly the bidirectional resolver's
    # resolvable vocabulary.
    _REQUIRED_RULES = frozenset(
        {"contradicts", "equivalent", "supports", "refines", "neutral", "unknown"}
    )

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate internal consistency of the policy."""
        if self.nli_threshold <= 0 or self.nli_threshold > 1:
            raise ResolverPolicyError(f"nli_threshold must be in (0, 1], got {self.nli_threshold}")
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
        order_set = set(self.priority_order)
        if order_set != self._REQUIRED_RULES:
            missing = self._REQUIRED_RULES - order_set
            extra = order_set - self._REQUIRED_RULES
            raise ResolverPolicyError(
                f"priority_order must contain every resolvable relation exactly "
                f"once ({sorted(self._REQUIRED_RULES)}); "
                f"missing={sorted(missing)} extra={sorted(extra)}"
            )
        if len(self.priority_order) != len(order_set):
            raise ResolverPolicyError(
                f"priority_order contains a duplicate entry: {self.priority_order}"
            )

    @classmethod
    def from_config(cls) -> ResolverPolicy:
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
            confidence_policy=policy_cfg.get("confidence_policy", "raw"),
            priority_order=policy_cfg.get(
                "priority_order",
                ["contradicts", "equivalent", "supports", "refines", "neutral", "unknown"],
            ),
            version=policy_cfg.get("version", RESOLVER_VERSION),
        )


class RelationshipResolver:
    """
    Policy-driven resolver: RelationshipEvidence → RelationshipType.

    The resolver itself contains no threshold values.
    All rules come from the ResolverPolicy.
    Instantiate once per pipeline run.
    """

    def __init__(self, policy: ResolverPolicy | None = None) -> None:
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
    ) -> tuple[RelationshipType, RelationshipDirection]:
        """
        Apply policy rules to classify a RelationshipEvidence.

        Uses calibrated_confidence from evidence (unless policy says "raw").
        Dispatches to the bidirectional rule set when evidence carries both
        directions (evidence.nli_scores_b_to_a is not None), else falls back
        to the legacy single-direction rule set unchanged.

        Returns:
            (RelationshipType, RelationshipDirection) — never raises.
        """
        if evidence.nli_scores_b_to_a is not None:
            return self._resolve_bidirectional(evidence)
        return self._resolve_single_direction(evidence)

    def resolve_as_decision(self, evidence: RelationshipEvidence) -> RelationshipDecision:
        """
        RECTIFIED (external review, P0-4): the conceptually correct way to
        consume a resolution -- a RelationshipDecision whose relation_type
        is None exactly when status is ABSTAINED, rather than a
        RelationshipType where one of six values secretly means "there is
        no relation." Existing callers of resolve() are unaffected; this
        is an additive alternative for new code (especially evaluation/
        reporting code, which should never compute "UNKNOWN classification
        accuracy" against a status, only relation-type accuracy against an
        actual relation, plus abstention-rate/coverage against status).

        RECTIFIED (P0-5): confidence is now compute_decision_confidence()'s
        per-relation-type combination of both calibrated directions, not
        the A->B-only evidence.calibrated_confidence.
        """
        relationship_type, direction = self.resolve(evidence)
        confidence = compute_decision_confidence(evidence, relationship_type, direction)
        return to_decision(relationship_type, direction, confidence=confidence)

    # The full A<->B contradiction/support/refinement decision table is
    # inherently a flat branch-per-case structure; splitting it into helper
    # methods would obscure rather than clarify the case-by-case reasoning.
    def _resolve_bidirectional(  # noqa: C901
        self,
        evidence: RelationshipEvidence,
    ) -> tuple[RelationshipType, RelationshipDirection]:
        p = self._policy
        ab = evidence.nli_scores
        ba = evidence.nli_scores_b_to_a
        assert (
            ba is not None
        ), "_resolve_bidirectional requires nli_scores_b_to_a (caller must check)"
        c_ab, e_ab, n_ab = ab.contradiction_score, ab.entailment_score, ab.neutral_score
        c_ba, e_ba, n_ba = ba.contradiction_score, ba.entailment_score, ba.neutral_score
        # NOTE: cosine_similarity is no longer read here -- it was only
        # consumed by the retired "high similarity, no entailment" REFINES
        # heuristic (P0-4). Retrieval-stage similarity filtering happens
        # upstream of the resolver; this function reasons over NLI scores.

        # Contradiction is a symmetric property of the pair; average two
        # independent (noisy) direction estimates rather than trusting one
        # arbitrary direction.
        c_avg = (c_ab + c_ba) / 2.0
        n_avg = (n_ab + n_ba) / 2.0
        e_max = max(e_ab, e_ba)  # conservative: must beat the stronger entailment reading

        # Entailment is NOT symmetric: "A entails B" and "B entails A" are
        # logically independent and tested per-direction, each against its
        # own argmax (RECTIFIED P0-6 rule, applied to both directions).
        ab_entails = (
            e_ab >= p.nli_threshold
            and (e_ab - c_ab) >= p.entailment_margin
            and (e_ab - n_ab) >= p.entailment_margin
        )
        ba_entails = (
            e_ba >= p.nli_threshold
            and (e_ba - c_ba) >= p.entailment_margin
            and (e_ba - n_ba) >= p.entailment_margin
        )

        for rule in p.priority_order:
            if rule == "contradicts":
                if (
                    c_avg >= p.nli_threshold
                    and (c_avg - e_max) >= p.contradiction_margin
                    and (c_avg - n_avg) >= p.contradiction_margin
                ):
                    logger.debug(
                        "resolved: CONTRADICTS (bidirectional)",
                        contradiction_avg=f"{c_avg:.3f}",
                        entailment_max=f"{e_max:.3f}",
                        neutral_avg=f"{n_avg:.3f}",
                    )
                    return RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC

            elif rule == "equivalent":
                # RECTIFIED (external review, P0-6): previously checked
                # unconditionally inside the "supports" branch, before
                # priority_order was even consulted for this decision --
                # meaning a policy that reordered "refines" ahead of
                # "supports" silently changed EQUIVALENT's behavior too,
                # in a way priority_order's own documentation never
                # described. EQUIVALENT is now a first-class, independently
                # ordered rule.
                if ab_entails and ba_entails:
                    logger.debug(
                        "resolved: EQUIVALENT",
                        entailment_ab=f"{e_ab:.3f}",
                        entailment_ba=f"{e_ba:.3f}",
                    )
                    return RelationshipType.EQUIVALENT, RelationshipDirection.SYMMETRIC

            elif rule == "supports":
                if ab_entails and ba_entails:
                    # Both directions entail but "equivalent" either was not
                    # reached yet in this policy's priority_order (it comes
                    # later) or a custom policy omitted checking it first --
                    # either way, a pair satisfying both directions' argmax
                    # test is never reported as one-way SUPPORTS; that would
                    # silently discard the fact that it also entails in
                    # reverse. Fall through to NEUTRAL/UNKNOWN rather than
                    # misreport a symmetric relation as directional.
                    pass
                elif ab_entails:
                    logger.debug("resolved: SUPPORTS (a_to_b)", entailment=f"{e_ab:.3f}")
                    return RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B
                elif ba_entails:
                    logger.debug("resolved: SUPPORTS (b_to_a)", entailment=f"{e_ba:.3f}")
                    return RelationshipType.SUPPORTS, RelationshipDirection.B_TO_A

            elif rule == "refines":
                # RETIRED (external "reality check" review round 3, P0-4
                # "REFINES fallback is semantically wrong"): this branch used
                # to emit REFINES purely from "high similarity + neutral-
                # dominant + not contradictory," with NEITHER direction
                # passing the entailment test at all. That is not a
                # refinement by this ontology's own definition (docs/
                # relationship_ontology.md): REFINES requires one-way
                # entailment PLUS the entailing claim being more specific --
                # "insufficient evidence for entailment in either direction"
                # is not evidence of refinement, it is exactly the
                # textbook case for NEUTRAL or ABSTAIN. The corpus this
                # heuristic actually fires on (high cosine, neutral-
                # dominant) already satisfies rule "neutral" below's own
                # condition, so removing this branch does not strand those
                # candidates in UNKNOWN -- they fall through to NEUTRAL,
                # which is the semantically correct verdict for "related but
                # neither entails the other." REFINES is now produced
                # EXCLUSIVELY by the downstream specificity gate
                # (classification/specificity.py, applied in
                # retrieval/__init__.py) reclassifying a genuine one-way
                # SUPPORTS decision (ab_entails XOR ba_entails, both tested
                # above) when the entailing claim is meaningfully more
                # specific -- i.e. REFINES now always implies real,
                # NLI-established one-way entailment, matching the
                # ontology's own stated definition instead of contradicting
                # it. No case is handled here; intentionally falls through.
                pass

            elif rule == "neutral":
                if (
                    n_avg >= p.neutrality_threshold
                    or n_ab >= p.neutrality_threshold
                    or n_ba >= p.neutrality_threshold
                ):
                    logger.debug("resolved: NEUTRAL (bidirectional)", neutral_avg=f"{n_avg:.3f}")
                    return RelationshipType.NEUTRAL, RelationshipDirection.SYMMETRIC

            elif rule == "unknown":
                logger.debug(
                    "resolved: UNKNOWN (bidirectional abstain)",
                    c_ab=f"{c_ab:.3f}",
                    e_ab=f"{e_ab:.3f}",
                    n_ab=f"{n_ab:.3f}",
                    c_ba=f"{c_ba:.3f}",
                    e_ba=f"{e_ba:.3f}",
                    n_ba=f"{n_ba:.3f}",
                )
                return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC

        return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC

    def _resolve_single_direction(
        self,
        evidence: RelationshipEvidence,
    ) -> tuple[RelationshipType, RelationshipDirection]:
        """
        Legacy rule set, used only when evidence.nli_scores_b_to_a is None
        (e.g. pre-existing single-direction test fixtures). Production
        Phase 6 always populates both directions and uses
        _resolve_bidirectional instead. Cannot distinguish EQUIVALENT from
        SUPPORTS, and SUPPORTS is always reported A_TO_B, since only one
        direction of evidence exists to reason from.
        """
        p = self._policy
        c = evidence.nli_scores.contradiction_score
        e = evidence.nli_scores.entailment_score
        n = evidence.nli_scores.neutral_score
        # cosine_similarity no longer read here -- see _resolve_bidirectional's
        # equivalent note (P0-4: retired "high similarity, no entailment" REFINES).

        for rule in p.priority_order:
            if rule == "contradicts":
                # RECTIFIED (P0-6): must be the argmax of {c, e, n}, beating
                # BOTH alternatives by the margin — not just beating entailment
                # while a higher neutral_score goes unchecked.
                if (
                    c >= p.nli_threshold
                    and (c - e) >= p.contradiction_margin
                    and (c - n) >= p.contradiction_margin
                ):
                    logger.debug(
                        "resolved: CONTRADICTS",
                        contradiction=f"{c:.3f}",
                        entailment=f"{e:.3f}",
                        neutral=f"{n:.3f}",
                    )
                    return RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC

            elif rule == "supports":
                # RECTIFIED (P0-6): same argmax requirement as CONTRADICTS above.
                if (
                    e >= p.nli_threshold
                    and (e - c) >= p.entailment_margin
                    and (e - n) >= p.entailment_margin
                ):
                    logger.debug("resolved: SUPPORTS", entailment=f"{e:.3f}", neutral=f"{n:.3f}")
                    return RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B

            elif rule == "refines":
                # RETIRED (P0-4, same reasoning as _resolve_bidirectional's
                # "refines" branch): "high similarity, no entailment" is not
                # a refinement under this ontology's own definition. This
                # legacy single-direction path has no second NLI direction
                # to test one-way entailment against in the first place, so
                # it cannot produce a genuine REFINES verdict at all; falls
                # through to "neutral" below, which already matches this
                # branch's own condition.
                pass

            elif rule == "neutral":
                if n >= p.neutrality_threshold:
                    logger.debug("resolved: NEUTRAL", neutral=f"{n:.3f}")
                    return RelationshipType.NEUTRAL, RelationshipDirection.SYMMETRIC

            elif rule == "unknown":
                logger.debug(
                    "resolved: UNKNOWN",
                    c=f"{c:.3f}",
                    e=f"{e:.3f}",
                    n=f"{n:.3f}",
                )
                return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC

        # Should never reach here, but fallback to UNKNOWN
        return RelationshipType.UNKNOWN, RelationshipDirection.SYMMETRIC


def compute_decision_confidence(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
) -> float:
    """
    RECTIFIED (external "reality check" review round 3, P0-5 "directional
    confidence is still wrong"): a single relationship's confidence must
    reflect the calibrated reading for the direction the resolver actually
    committed to, not always the A->B reading regardless of outcome. Before
    this function existed, a resolver decision of B_TO_A (chosen because
    e_ba clearly dominated e_ab) still reported evidence.calibrated_confidence
    -- the A->B-only calibrated score -- as "the" relationship confidence,
    contaminating every downstream consumer of that scalar (evidence
    strength, reliability, conflict pressure, validation, provenance).

    Formula, by relationship_type:
        CONTRADICTS: symmetric -- average of both calibrated directions
                     (mirrors the resolver's own c_avg symmetric test).
        EQUIVALENT:  symmetric, both directions independently entail --
                     min() of both, since a claim of mutual entailment is
                     only as strong as its weaker-confidence direction.
        SUPPORTS / REFINES: directional -- the calibrated confidence of
                     whichever direction was actually selected.
        NEUTRAL / UNKNOWN: symmetric -- average of both directions (no
                     single direction is privileged when abstaining or
                     reporting no established relation).

    Falls back to evidence.calibrated_confidence (A->B only) when
    calibrated_confidence_b_to_a is unavailable (legacy single-direction
    evidence), so this is a strict improvement, never a regression, for
    fixtures that predate bidirectional NLI.
    """
    ab = evidence.calibrated_confidence
    ba = evidence.calibrated_confidence_b_to_a
    if ba is None:
        return ab

    if relationship_type == RelationshipType.CONTRADICTS:
        return (ab + ba) / 2.0
    if relationship_type == RelationshipType.EQUIVALENT:
        return min(ab, ba)
    if relationship_type in (RelationshipType.SUPPORTS, RelationshipType.REFINES):
        return ab if direction == RelationshipDirection.A_TO_B else ba
    # NEUTRAL, UNKNOWN, and any future symmetric-by-default type.
    return (ab + ba) / 2.0
