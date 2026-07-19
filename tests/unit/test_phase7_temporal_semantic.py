"""
Unit tests for temporal.py semantic-timestamp fix (P0-4).

Verifies that temporal resolution uses Claim.timestamp (semantic),
never filesystem st_mtime.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    ClaimNode, RelationshipEdge, RelationshipType, RelationshipDirection,
    TemporalStatus,
)
from smriti.evolution.context import SemanticReasoningContext
from smriti.evolution.networkx_backend import NetworkXBackend
from smriti.evolution.partitioning import run_partitioning
from smriti.evolution.temporal import run_temporal_resolution, _get_semantic_timestamp


def make_claim(claim_id, timestamp=None):
    claim = Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=f"Claim {claim_id}", content_hash=claim_id[:16], context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None, assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context="", sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )
    # Inject timestamp as attribute (until Claim model has it as a field)
    object.__setattr__(claim, "timestamp", timestamp) if hasattr(claim, "__dataclass_fields__") else None
    try:
        object.__setattr__(claim, "_timestamp_override", timestamp)
    except Exception:
        pass
    return claim


def make_contradiction_ctx(node_a, node_b):
    backend = NetworkXBackend()
    nodes = {
        node_a: ClaimNode(
            node_id=node_a, claim_id=node_a, claim_text=f"Claim {node_a}",
            context="", source_path=Path("test.md"), document_id="d001",
        ),
        node_b: ClaimNode(
            node_id=node_b, claim_id=node_b, claim_text=f"Claim {node_b}",
            context="", source_path=Path("test.md"), document_id="d001",
        ),
    }
    edge = RelationshipEdge(
        edge_id="e1", source_node_id=node_a, target_node_id=node_b,
        relationship_type=RelationshipType.CONTRADICTS,
        direction=RelationshipDirection.SYMMETRIC,
        calibrated_confidence=0.88, cosine_similarity=0.85,
        nli_confidence=0.88, candidate_rank=1,
    )
    for nid in nodes:
        backend.add_node(nid)
    backend.add_edge(node_a, node_b, "e1", "contradicts", 0.88)
    backend.add_edge(node_b, node_a, "e1_rev", "contradicts", 0.88)
    return SemanticReasoningContext(
        nodes=nodes, edges={"e1": edge}, backend=backend, run_id="test", config_hash="test",
    )


def test_no_timestamp_produces_no_timestamp_status():
    """RECTIFIED (P0-4): Missing Claim.timestamp → NO_TIMESTAMP status, not filesystem fallback."""
    ctx = make_contradiction_ctx("c001", "c002")
    run_partitioning(ctx)

    claims_map = {
        "c001": make_claim("c001", timestamp=None),
        "c002": make_claim("c002", timestamp=None),
    }
    run_temporal_resolution(ctx, claims_map)

    status_c001 = ctx.nodes["c001"].temporal_metadata.status
    # Should be NO_TIMESTAMP, not a filesystem-derived value
    assert status_c001 in (TemporalStatus.NO_TIMESTAMP, TemporalStatus.STATIC_PARTITION), (
        "When Claim.timestamp is None, temporal status must be NO_TIMESTAMP "
        "or STATIC_PARTITION — never an EVOLUTION_CHAIN from filesystem metadata."
    )


def test_get_semantic_timestamp_never_reads_filesystem(monkeypatch):
    """RECTIFIED (P0-4): _get_semantic_timestamp must NEVER call stat()."""
    stat_called = []

    def mock_stat(*args, **kwargs):
        stat_called.append(True)
        raise Exception("stat() must not be called")

    monkeypatch.setattr(Path, "stat", mock_stat)

    claim = make_claim("c001", timestamp=None)
    result = _get_semantic_timestamp(claim)

    assert not stat_called, "stat() was called! Temporal resolver must not read filesystem."
    assert result is None