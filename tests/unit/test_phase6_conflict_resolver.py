"""
Unit tests for classification/conflict.py's MOST_SPECIFIC priority order,
focused on the EQUIVALENT addition (bidirectional-NLI rewrite).

Uses a minimal stand-in for Relationship (only .relationship_type is read
by the MOST_SPECIFIC branch of _apply_policy) rather than constructing the
full Relationship dataclass graph, which needs a real CandidatePair /
RelationshipEvidence / RelationshipProvenance tree unrelated to what this
policy branch actually inspects.
"""

from types import SimpleNamespace

from smriti.core.models import ConflictResolutionPolicy, RelationshipType
from smriti.retrieval.classification.conflict import ConflictResolver


def fake_rel(rel_type: RelationshipType):
    return SimpleNamespace(relationship_type=rel_type)


def test_equivalent_outranks_supports_and_refines_and_neutral():
    resolver = ConflictResolver(policy=ConflictResolutionPolicy.MOST_SPECIFIC)
    candidates = [
        fake_rel(RelationshipType.SUPPORTS),
        fake_rel(RelationshipType.EQUIVALENT),
        fake_rel(RelationshipType.REFINES),
        fake_rel(RelationshipType.NEUTRAL),
    ]
    winner = resolver._apply_policy("pair_key", candidates)
    assert winner.relationship_type == RelationshipType.EQUIVALENT


def test_contradicts_still_outranks_equivalent():
    resolver = ConflictResolver(policy=ConflictResolutionPolicy.MOST_SPECIFIC)
    candidates = [
        fake_rel(RelationshipType.EQUIVALENT),
        fake_rel(RelationshipType.CONTRADICTS),
    ]
    winner = resolver._apply_policy("pair_key", candidates)
    assert winner.relationship_type == RelationshipType.CONTRADICTS


def test_equivalent_outranks_unknown():
    resolver = ConflictResolver(policy=ConflictResolutionPolicy.MOST_SPECIFIC)
    candidates = [
        fake_rel(RelationshipType.UNKNOWN),
        fake_rel(RelationshipType.EQUIVALENT),
    ]
    winner = resolver._apply_policy("pair_key", candidates)
    assert winner.relationship_type == RelationshipType.EQUIVALENT
