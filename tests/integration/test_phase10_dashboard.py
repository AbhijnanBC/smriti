"""
Integration tests for Phase 10.
Validates EpistemicState → ServiceClient → PresentationModel consistency.
"""

import pytest
from unittest.mock import MagicMock

from smriti.core.models import (
    WorkspaceType, EpistemicLens, ExplainabilityLevel,
    ProjectionLevel, ExportFormat,
)
from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.dashboard.services.client import ServiceClient
from smriti.dashboard.workspaces.registry import build_default_registry
from smriti.dashboard.policies.policies import PolicyEngine, InteractionPolicy
from smriti.dashboard.models.presentation import DTOTransformer
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.commands.commands import SelectClaimCommand, ActivateWorkspaceCommand


# ── Test‑specific PolicyEngine with validate_command ─────────────────────────
class TestPolicyEngine(PolicyEngine):
    """Subclass that implements validate_command for testing."""
    def validate_command(self, command):
        """Enforce interaction policies for commands.
        For this test suite, we allow all commands.
        """
        # In a real implementation, you'd check command type and limits.
        # Here we just accept everything.
        return True, ""


def make_mock_api():
    api = MagicMock()
    api.run_id = "test_run_phase10"
    api.node_count = 10
    api.api_version = "1.0"

    mock_claim_dto = MagicMock()
    mock_claim_dto.claim_id = "c001"
    mock_claim_dto.claim_text = "Python supports generators."
    mock_claim_dto.reliability_index = 78.5
    mock_claim_dto.calibration_label = MagicMock()
    mock_claim_dto.calibration_label.value = "high"
    mock_claim_dto.uncertainty_score = 12.0
    mock_claim_dto.to_dict.return_value = {
        "claim_id": "c001",
        "claim_text": "Python supports generators.",
        "reliability_index": 78.5,
        "calibration_label": "high",
        "uncertainty_score": 12.0,
        "support_count": 3,
        "degree": 5,
        "centrality": 0.65,
        "context": "Python > Generators",
        "document_id": "d001",
        "source_path": "note.md",
        "semantic_role": "foundational_claim",
        "temporal_status": "static_partition",
        "evidence_strength": 0.70,
        "conflict_pressure": 0.20,
        "evidence_completeness": 1.0,
        "evidence_independence": 0.60,
        "source_diversity": 0.55,
        "topology_strength": 0.80,
        "temporal_stability": 0.90,
    }

    mock_response = MagicMock()
    mock_response.data = mock_claim_dto
    mock_response.total_count = 1

    api.get_claim.return_value = mock_response
    api.search.return_value = mock_response
    api.statistics.return_value = MagicMock(data={
        "total_claims": 10, "total_edges": 5,
        "total_partitions": 2, "total_contradictions": 1,
        "avg_reliability": 72.3, "median_reliability": 75.0,
        "avg_uncertainty": 18.5,
        "calibration_distribution": {"high": 4, "moderate": 4, "low": 2},
        "reliability_histogram": [("0-10", 0), ("10-20", 1)],
        "partition_summaries": [],
        "run_id": "test_run_phase10",
    })
    api.top_claims.return_value = mock_response

    export_resp = MagicMock()
    export_resp.data = {"format": "json", "content": '{"claims": []}', "byte_size": 15}
    api.export.return_value = export_resp

    traversal_resp = MagicMock()
    traversal_resp.data = {
        "start_claim_id": "c001", "navigation_mode": "local",
        "depth_reached": 1,
        "nodes": [mock_claim_dto.to_dict.return_value],
        "edges": [],
    }
    api.traverse.return_value = traversal_resp

    explain_resp = MagicMock()
    explain_resp.data = {
        "claim_id": "c001",
        "reliability_index": 78.5,
        "calibration_label": "high",
        "uncertainty_score": 12.0,
        "explainability_level": 3,
        "summary": "Reliable. Primary strength: Evidence strength.",
        "dominant_signal": "evidence_strength",
        "limiting_signal": "conflict_pressure",
        "component_scores": [
            {"signal_name": "evidence_strength", "contribution": 22.0,
             "direction": "positive", "explanation": "Good support.",
             "signal": "evidence_strength"}
        ],
        "signal_vector": {"evidence_strength": 0.70},
        "audit": {"policy_version": "1.0", "fusion_algorithm": "weighted_linear_v1"},
        "recommendations": [],
        "policy_snapshot": {},
    }
    api.explain.return_value = explain_resp

    return api


@pytest.fixture
def mock_api():
    return make_mock_api()


@pytest.fixture
def state_mgr(mock_api):
    return EpistemicStateManager(run_id=mock_api.run_id)


@pytest.fixture
def client(mock_api):
    return ServiceClient(api=mock_api)


@pytest.fixture
def registry():
    return build_default_registry()


@pytest.fixture
def policy_engine():
    # Use the test-specific subclass that implements validate_command
    return TestPolicyEngine(InteractionPolicy())


# ── Interaction lifecycle ─────────────────────────────────────────────────────

def test_interaction_lifecycle_completes(state_mgr):
    state_mgr.activate_workspace(WorkspaceType.RELIABILITY)
    state_mgr.apply_filter("calibration_label", "high")
    state_mgr.submit_search("machine learning")
    state_mgr.select_claim("c001")
    state_mgr.set_explainability(ExplainabilityLevel.DETAILED)
    state = state_mgr.state
    assert state.workspace_type == WorkspaceType.RELIABILITY
    assert state.active_lens == EpistemicLens.RELIABILITY
    assert state.selected_claim_id == "c001"
    assert state.explainability_level == ExplainabilityLevel.DETAILED


# ── ServiceClient ─────────────────────────────────────────────────────────────

def test_client_get_claim(client):
    result = client.get_claim("c001")
    assert result is not None
    assert result.get("claim_id") == "c001"
    assert result.get("reliability_index") == 78.5


def test_client_search_claims(client):
    result = client.search_claims(text_query="python", limit=10)
    assert "claims" in result


def test_client_get_statistics(client):
    stats = client.get_statistics()
    assert stats.get("total_claims") == 10


def test_client_get_explanation(client):
    result = client.get_explanation("c001", level=ExplainabilityLevel.FULL_AUDIT)
    assert result is not None
    assert result.get("reliability_index") == 78.5


def test_client_export_json(client):
    content = client.export_data("json")
    assert content is not None
    assert len(content) > 0


def test_client_traverse(client):
    result = client.traverse("c001", max_depth=2)
    assert result is not None
    assert "nodes" in result


# ── DTO → PresentationModel pipeline ─────────────────────────────────────────

def test_claim_dto_converts_to_pm(client):
    """ServiceClient dict must be convertible to ClaimPresentationModel."""
    dto = client.get_claim("c001")
    pm = DTOTransformer.to_claim_pm(dto)
    assert pm.claim_id == "c001"
    assert pm.label_display == "High"
    assert len(pm.signals) == 6


def test_statistics_dto_converts_to_pm(client):
    dto = client.get_statistics()
    pm = DTOTransformer.to_statistics_pm(dto)
    assert pm.total_claims == 10


def test_explanation_dto_converts_to_audit_pm(client):
    dto = client.get_explanation("c001", level=3)
    pm = DTOTransformer.to_audit_pm(dto)
    assert pm.dominant_signal == "evidence_strength"


# ── Command dispatch pipeline ─────────────────────────────────────────────────

def test_dispatcher_select_claim_command(state_mgr, policy_engine):
    dispatcher = InteractionDispatcher(state_mgr, policy_engine)
    dispatcher.dispatch(SelectClaimCommand(session_id="s", claim_id="c001"))
    assert state_mgr.state.selected_claim_id == "c001"


def test_dispatcher_activate_workspace_command(state_mgr, policy_engine):
    dispatcher = InteractionDispatcher(state_mgr, policy_engine)
    dispatcher.dispatch(ActivateWorkspaceCommand(
        session_id="s", workspace_type=WorkspaceType.AUDIT
    ))
    assert state_mgr.state.workspace_type == WorkspaceType.AUDIT


# ── WorkspaceRegistry ─────────────────────────────────────────────────────────

def test_all_workspaces_registered(registry):
    for ws_type in WorkspaceType:
        assert registry.is_registered(ws_type), f"{ws_type.value} missing"


def test_workspace_has_correct_profile(registry):
    for ws_type in WorkspaceType:
        ws = registry.get(ws_type)
        assert ws.profile.workspace_type == ws_type


# ── Policy enforcement ────────────────────────────────────────────────────────

def test_policy_rejects_large_graph(policy_engine):
    allowed, _ = policy_engine.validate_graph_size(1000)
    assert allowed is False


def test_policy_allows_normal_graph(policy_engine):
    allowed, _ = policy_engine.validate_graph_size(10)
    assert allowed is True


def test_policy_allows_json_export(policy_engine):
    allowed, _ = policy_engine.validate_export("json")
    assert allowed is True


# ── Knowledge immutability ────────────────────────────────────────────────────

def test_interaction_does_not_modify_api(mock_api, state_mgr, client):
    original_node_count = mock_api.node_count
    original_run_id = mock_api.run_id
    state_mgr.select_claim("c001")
    state_mgr.apply_filter("calibration_label", "high")
    client.get_claim("c001")
    client.search_claims(text_query="test")
    client.get_statistics()
    client.get_explanation("c001")
    assert mock_api.node_count == original_node_count
    assert mock_api.run_id == original_run_id


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_state_produces_same_requests(mock_api, state_mgr, client):
    state_mgr.select_claim("c001")
    result1 = client.get_claim("c001")
    result2 = client.get_claim("c001")
    assert result1.get("claim_id") == result2.get("claim_id")
    assert result1.get("reliability_index") == result2.get("reliability_index")


# ── Serialization ─────────────────────────────────────────────────────────────

def test_workspace_state_serializable(state_mgr):
    import json
    state_mgr.activate_workspace(WorkspaceType.AUDIT)
    state_mgr.apply_filter("calibration_label", "high")
    state_mgr.select_claim("c001")
    snapshot = state_mgr.serialize()
    json_str = json.dumps(snapshot)
    assert len(json_str) > 0
    restored = json.loads(json_str)
    assert restored.get("workspace_type") == WorkspaceType.AUDIT.value


def test_workspace_restoration(state_mgr):
    state_mgr.activate_workspace(WorkspaceType.CONFLICT)
    state_mgr.apply_filter("calibration_label", "high")
    snapshot = state_mgr.serialize()
    fresh_mgr = EpistemicStateManager(run_id="test_run_phase10")
    fresh_mgr.restore(snapshot)
    assert fresh_mgr.state.workspace_type == WorkspaceType.CONFLICT
    assert fresh_mgr.state.active_filters.get("calibration_label") == "high"