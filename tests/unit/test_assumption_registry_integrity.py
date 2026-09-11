"""
Integrity checks for the assumption <-> research-claim <-> experiment
traceability graph (P0-B, "FINAL REVIEW" round).

Before this fix, affected_claims used a stale RC-00N scheme that never
matched the canonical RC1..RC5 registry, and several validation_experiment
values pointed at an experiment that runs but does not actually test the
assumption. These tests make that class of drift a build failure, not
something a reviewer has to notice by reading source line by line.
"""

from smriti.evaluation.certification.claims import (
    CANONICAL_CLAIM_IDS,
    CANONICAL_EXPERIMENT_IDS,
    RESEARCH_CLAIMS_SPEC,
)
from smriti.evaluation.statistical.assumptions import ASSUMPTION_REGISTRY, get_assumptions_for_claim


def test_every_affected_claim_is_canonical():
    for a in ASSUMPTION_REGISTRY:
        for claim_id in a.affected_claims:
            assert claim_id in CANONICAL_CLAIM_IDS, (
                f"{a.assumption_id} lists affected_claims={a.affected_claims!r}, "
                f"but {claim_id!r} is not one of {sorted(CANONICAL_CLAIM_IDS)}"
            )


def test_no_stale_rc00n_identifiers_anywhere_in_the_registry():
    """The specific historical bug: RC-001..RC-006 (with a dash and
    zero-padding) instead of RC1..RC5."""
    for a in ASSUMPTION_REGISTRY:
        for claim_id in a.affected_claims:
            assert not claim_id.startswith(
                "RC-"
            ), f"{a.assumption_id} still uses the stale RC-00N scheme: {claim_id!r}"


def test_no_stale_exp006_reference():
    for a in ASSUMPTION_REGISTRY:
        assert a.validation_experiment != "EXP-006", (
            f"{a.assumption_id} still references EXP-006, which does not exist "
            f"in the frozen 5-experiment registry."
        )


def test_validation_experiment_is_canonical_or_none():
    for a in ASSUMPTION_REGISTRY:
        if a.validation_experiment is not None:
            assert a.validation_experiment in CANONICAL_EXPERIMENT_IDS, (
                f"{a.assumption_id}.validation_experiment={a.validation_experiment!r} "
                f"is not one of {sorted(CANONICAL_EXPERIMENT_IDS)}"
            )


def test_validation_status_matches_validation_experiment_presence():
    """unvalidated <=> validation_experiment is None. A non-None
    validation_experiment must carry "validated" or "partially_validated";
    an assumption claiming "unvalidated" must not simultaneously point at
    an experiment (the exact inconsistency this fix closes)."""
    for a in ASSUMPTION_REGISTRY:
        if a.validation_status == "unvalidated":
            assert a.validation_experiment is None, (
                f"{a.assumption_id} is marked unvalidated but still points at "
                f"validation_experiment={a.validation_experiment!r}"
            )
        else:
            assert a.validation_experiment is not None, (
                f"{a.assumption_id} is marked {a.validation_status!r} but has no "
                f"validation_experiment"
            )
            assert a.validation_status in ("validated", "partially_validated"), (
                f"{a.assumption_id} has an unrecognized validation_status: "
                f"{a.validation_status!r}"
            )


def test_get_assumptions_for_claim_actually_finds_assumptions():
    """The concrete symptom of the original bug:
    get_assumptions_for_claim("RC1") returned [] because every assumption
    used "RC-001" instead of "RC1"."""
    for claim_id in CANONICAL_CLAIM_IDS:
        found = get_assumptions_for_claim(claim_id)
        # Not every claim necessarily has a registered assumption, but at
        # least RC1/RC2/RC4/RC5 (which the registry explicitly names in
        # affected_claims below) must resolve to a non-empty list.
        if any(claim_id in a.affected_claims for a in ASSUMPTION_REGISTRY):
            assert (
                found
            ), f"get_assumptions_for_claim({claim_id!r}) found nothing despite a matching record existing"


def test_claims_py_assumptions_tuples_are_reciprocated_by_the_assumption_registry():
    """If RESEARCH_CLAIMS_SPEC says claim RCn's "assumptions" include
    ASMP-x, then ASMP-x's own affected_claims must list RCn back --
    bidirectional consistency between the two independent registries,
    exactly what the review's integrity-check request asked for."""
    assumptions_by_id = {a.assumption_id: a for a in ASSUMPTION_REGISTRY}
    for spec in RESEARCH_CLAIMS_SPEC:
        claim_id = spec["claim_id"]
        for assumption_id in spec.get("assumptions", ()):
            assumption = assumptions_by_id.get(assumption_id)
            assert (
                assumption is not None
            ), f"{claim_id} cites {assumption_id!r}, which is not in ASSUMPTION_REGISTRY"
            assert claim_id in assumption.affected_claims, (
                f"{claim_id} cites {assumption_id!r} as one of its assumptions, but "
                f"{assumption_id}.affected_claims={assumption.affected_claims!r} does not include {claim_id!r}"
            )
