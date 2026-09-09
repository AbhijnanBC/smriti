"""
explainability_audit.py — RC5 reconstruction audit (P0-13).

Answers a concrete, falsifiable question with ZERO external ground truth
needed: for every claim SMRITI scored, does replaying the exact same
deterministic fusion + constraint pipeline over that claim's OWN recorded
signal contributions reproduce the reliability_index the system actually
reported? This is a self-consistency check on the audit trail (does the
math the system claims to have done match the math it recorded?), not an
external validity claim about whether the reliability MODEL itself is
correct — that is RC4's concern, tested separately by metamorphic.py.

Previously, "faithfulness" in EXP-006 was estimated as
`min(1.0, sum(abs(contribution)) / (reliability_index * 1.5))` — an
arbitrary formula with a hard-coded 0.8 fallback when no data existed.
This replaces that with an actual recomputation of the fusion+constraint
pipeline, compared against the stored reliability_index within numerical
tolerance.
"""

from __future__ import annotations

from typing import Dict, List

from smriti.core.models import SignalVector
from smriti.scoring.fusion import _apply_constraints
from smriti.scoring.policies import load_policy

# The stored reliability_index in memory_store.py's flattened records is a
# display-rounded value (2 decimal places); the reconstruction here carries
# full float precision. 0.01 tolerance accounts for that rounding step
# without masking a genuine algorithmic inconsistency (which would produce
# deltas far larger than a rounding artifact -- typically >0.1).
_TOLERANCE = 0.01


def _rebuild_signal_vector(record: Dict) -> SignalVector:
    sv = record.get("signal_vector", {})
    statuses = record.get("signal_statuses", {})
    return SignalVector(
        evidence_strength=sv.get("evidence_strength", 0.0),
        evidence_independence=sv.get("evidence_independence", 0.0),
        source_diversity=sv.get("source_diversity", 0.0),
        topology_strength=sv.get("topology_strength", 0.0),
        conflict_pressure=sv.get("conflict_pressure", 0.0),
        temporal_stability=sv.get("temporal_stability", 0.0),
        evidence_completeness=record.get("evidence_completeness", sv.get("evidence_completeness", 0.0)),
        statuses=statuses,
    )


def run_reconstruction_audit(api) -> Dict:
    """
    Iterate every scored claim in the live KnowledgeAccessService, recompute
    raw_reliability from its own recorded component_scores, replay the
    constraint pipeline, and compare the reconstructed final value to the
    stored reliability_index.
    """
    store = getattr(api, "_store", None)
    records: Dict[str, Dict] = getattr(store, "_reliability_records", None) if store else None

    if not isinstance(records, dict) or not records:
        return {
            "exact_match_rate": 0.0,
            "n_checked": 0,
            "n_mismatched": 0,
            "note": "No reliability records accessible on this KnowledgeAccessService "
                    "(e.g. a test double rather than a live Phase 9 service).",
        }

    policy = load_policy()
    fp = policy.fusion

    n_checked = 0
    mismatches: List[Dict] = []

    for claim_id, record in records.items():
        component_scores = record.get("component_scores", [])
        if not component_scores:
            continue

        n_checked += 1
        raw_reconstructed = sum(c.get("contribution", 0.0) for c in component_scores)

        sv = _rebuild_signal_vector(record)
        constrained_log: List[str] = []
        constrained_reconstructed = _apply_constraints(raw_reconstructed, sv, fp, constrained_log)
        final_reconstructed = max(0.0, min(100.0, constrained_reconstructed))

        stored_final = record.get("reliability_index", 0.0)
        delta = abs(final_reconstructed - stored_final)
        if delta > _TOLERANCE:
            mismatches.append({
                "claim_id": claim_id,
                "stored_reliability_index": stored_final,
                "reconstructed_final": round(final_reconstructed, 4),
                "reconstructed_raw": round(raw_reconstructed, 4),
                "delta": round(delta, 4),
            })

    exact_match_rate = (n_checked - len(mismatches)) / n_checked if n_checked else 0.0

    return {
        "exact_match_rate": round(exact_match_rate, 4),
        "n_checked": n_checked,
        "n_mismatched": len(mismatches),
        "mismatches_sample": mismatches[:10],
        "fusion_policy_used": policy.fusion.version if hasattr(policy.fusion, "version") else "unknown",
    }
