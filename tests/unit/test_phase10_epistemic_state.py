"""Unit tests for dashboard/state/epistemic_state.py."""

import pytest
from smriti.core.models import EpistemicLens, WorkspaceType
from smriti.dashboard.state.epistemic_state import EpistemicStateManager


@pytest.fixture
def mgr():
    return EpistemicStateManager(run_id="test_run_001")


def test_initial_state(mgr):
    state = mgr.state
    assert state.workspace_type == WorkspaceType.RESEARCH
    assert state.active_lens == EpistemicLens.EXPLORATION
    assert state.selected_claim_id is None
    assert state.search_query == ""


def test_select_claim(mgr):
    mgr.select_claim("claim_abc123")
    assert mgr.state.selected_claim_id == "claim_abc123"


def test_deselect_claim(mgr):
    mgr.select_claim("claim_abc123")
    mgr.deselect_claim()
    assert mgr.state.selected_claim_id is None


def test_activate_workspace_changes_lens(mgr):
    mgr.activate_workspace(WorkspaceType.RELIABILITY)
    assert mgr.state.workspace_type == WorkspaceType.RELIABILITY
    assert mgr.state.active_lens == EpistemicLens.RELIABILITY


def test_activate_workspace_clears_selection(mgr):
    mgr.select_claim("c001")
    mgr.activate_workspace(WorkspaceType.CONFLICT)
    assert mgr.state.selected_claim_id is None


def test_apply_filter(mgr):
    mgr.apply_filter("calibration_label", "high")
    assert mgr.state.active_filters.get("calibration_label") == "high"


def test_remove_filter(mgr):
    mgr.apply_filter("calibration_label", "high")
    mgr.remove_filter("calibration_label")
    assert "calibration_label" not in mgr.state.active_filters


def test_clear_filters(mgr):
    mgr.apply_filter("calibration_label", "high")
    mgr.apply_filter("semantic_role", "foundational_claim")
    mgr.clear_filters()
    assert mgr.state.active_filters == {}
    assert mgr.state.search_query == ""


def test_submit_search(mgr):
    mgr.set_page(5)
    mgr.submit_search("machine learning")
    assert mgr.state.search_query == "machine learning"
    assert mgr.state.page == 0


def test_navigate_to_adds_breadcrumb(mgr):
    mgr.navigate_to("c001", "First claim")
    mgr.navigate_to("c002", "Second claim")
    assert len(mgr.state.breadcrumbs) == 2
    assert mgr.state.breadcrumbs[-1]["claim_id"] == "c002"


def test_navigate_back(mgr):
    mgr.navigate_to("c001", "First")
    mgr.navigate_to("c002", "Second")
    prev_id = mgr.navigate_back()
    assert prev_id == "c001"
    assert len(mgr.state.breadcrumbs) == 1


def test_event_log_records_transitions(mgr):
    initial_events = len(mgr.event_log)
    mgr.select_claim("c001")
    mgr.activate_workspace(WorkspaceType.AUDIT)
    mgr.apply_filter("calibration_label", "high")
    assert len(mgr.event_log) == initial_events + 3


def test_set_explainability(mgr):
    from smriti.core.models import ExplainabilityLevel

    mgr.set_explainability(ExplainabilityLevel.FULL_AUDIT)
    assert mgr.state.explainability_level == ExplainabilityLevel.FULL_AUDIT


def test_set_comparison_claims(mgr):
    mgr.set_comparison_claims(("c001", "c002"))
    assert "c001" in mgr.state.comparison_claim_ids
    assert "c002" in mgr.state.comparison_claim_ids


def test_serialize_and_restore(mgr):
    mgr.select_claim("c001")
    mgr.apply_filter("calibration_label", "high")
    mgr.activate_workspace(WorkspaceType.AUDIT)
    snapshot = mgr.serialize()
    fresh_mgr = EpistemicStateManager(run_id="test_run_001")
    fresh_mgr.restore(snapshot)
    assert fresh_mgr.state.workspace_type == WorkspaceType.AUDIT
    assert fresh_mgr.state.active_filters.get("calibration_label") == "high"


def test_breadcrumb_depth_limit(mgr):
    for i in range(15):
        mgr.navigate_to(f"c{i:03d}", f"Claim {i}")
    assert len(mgr.state.breadcrumbs) <= 8


def test_workspace_lens_mapping():
    mgr = EpistemicStateManager(run_id="test")
    lens_map = {
        WorkspaceType.RESEARCH: EpistemicLens.EXPLORATION,
        WorkspaceType.RELIABILITY: EpistemicLens.RELIABILITY,
        WorkspaceType.CONFLICT: EpistemicLens.CONFLICT,
        WorkspaceType.AUDIT: EpistemicLens.AUDIT,
        WorkspaceType.PROVENANCE: EpistemicLens.PROVENANCE,
    }
    for ws, expected_lens in lens_map.items():
        mgr.activate_workspace(ws)
        assert (
            mgr.state.active_lens == expected_lens
        ), f"{ws.value} should default to {expected_lens.value}"
