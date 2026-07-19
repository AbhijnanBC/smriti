"""Unit tests for evolution/validation.py."""

import pytest
from pathlib import Path
from smriti.core.models import (
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection, SemanticRole,
)
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.validation import validate_graph_structure
from smriti.exceptions import GraphValidationError


def make_node(nid):
    return ClaimNode(
        node_id=nid, claim_id=nid, claim_text=f"Claim {nid}",
        context="", source_path=Path("test.md"), document_id="d001",
    )


def make_edge(eid, src, tgt, rtype=RelationshipType.CONTRADICTS):
    return RelationshipEdge(
        edge_id=eid, source_node_id=src, target_node_id=tgt,
        relationship_type=rtype, direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=0.88, cosine_similarity=0.85,
        nli_confidence=0.88, candidate_rank=1,
    )


def test_valid_graph_passes():
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001"), "c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002")}
    backend.add_node("c001")
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "contradicts", 0.88)
    report = validate_graph_structure(nodes, edges, backend)
    assert report.is_valid is True and report.total_violations == 0


def test_orphan_edge_source_missing_raises():
    backend = NetworkXBackend()
    nodes = {"c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002")}
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "contradicts", 0.88)
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, edges, backend)


def test_unknown_type_in_edge_raises():
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001"), "c002": make_node("c002")}
    edges = {"e1": make_edge("e1", "c001", "c002", RelationshipType.UNKNOWN)}
    backend.add_node("c001")
    backend.add_node("c002")
    backend.add_edge("c001", "c002", "e1", "unknown", 0.50)
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, edges, backend)


def test_empty_claim_text_raises():
    backend = NetworkXBackend()
    bad_node = ClaimNode(
        node_id="c001", claim_id="c001", claim_text="",
        context="", source_path=Path("test.md"), document_id="d001",
    )
    nodes = {"c001": bad_node}
    backend.add_node("c001")
    with pytest.raises(GraphValidationError):
        validate_graph_structure(nodes, {}, backend)


def test_semantic_violations_detected_and_reported():
    """RECTIFIED (P2-4): SUPPORTS→CONTRADICTS→SUPPORTS chain produces semantic warning."""
    backend = NetworkXBackend()
    nodes = {
        "c001": make_node("c001"),
        "c002": make_node("c002"),
        "c003": make_node("c003"),
        "c004": make_node("c004"),
    }
    # c001 SUPPORTS c002, c002 CONTRADICTS c003, c003 SUPPORTS c004
    edges = {
        "e1": make_edge("e1", "c001", "c002", RelationshipType.SUPPORTS),
        "e2": make_edge("e2", "c002", "c003", RelationshipType.CONTRADICTS),
        "e3": make_edge("e3", "c003", "c004", RelationshipType.SUPPORTS),
    }
    for nid in nodes:
        backend.add_node(nid)
    backend.add_edge("c001", "c002", "e1", "supports", 0.88)
    backend.add_edge("c002", "c003", "e2", "contradicts", 0.88)
    backend.add_edge("c003", "c004", "e3", "supports", 0.88)

    # Should pass structurally but produce semantic warnings
    report = validate_graph_structure(nodes, edges, backend)
    assert report.is_valid is True  # Not a fatal error
    assert len(report.semantic_violations) > 0


def test_semantic_violations_field_present_on_report():
    """RECTIFIED (P2-4): ValidationReport must have semantic_violations tuple."""
    backend = NetworkXBackend()
    nodes = {"c001": make_node("c001")}
    backend.add_node("c001")
    report = validate_graph_structure(nodes, {}, backend)
    assert hasattr(report, "semantic_violations")
    assert isinstance(report.semantic_violations, tuple)