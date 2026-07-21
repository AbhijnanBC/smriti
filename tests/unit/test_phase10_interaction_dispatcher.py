"""Unit tests for dashboard/controller/interaction_dispatcher.py."""

import pytest
from smriti.core.models import WorkspaceType, ExplainabilityLevel
from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.dashboard.policies.policies import PolicyEngine, InteractionPolicy, ComparisonPolicy
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.commands.commands import (
    SelectClaimCommand,
    ActivateWorkspaceCommand,
    CompareCommand,
    SubmitSearchCommand,
    SetPageCommand,
    ApplyFilterCommand,
    ClearFiltersCommand,
)
from smriti.exceptions import CommandDispatchError


@pytest.fixture
def dispatcher():
    mgr = EpistemicStateManager(run_id="test")
    engine = PolicyEngine(InteractionPolicy())
    return InteractionDispatcher(state_manager=mgr, policy_engine=engine), mgr


def test_select_claim_command_transitions_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(SelectClaimCommand(session_id="s", claim_id="c001"))
    assert mgr.state.selected_claim_id == "c001"


def test_activate_workspace_command_transitions_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(ActivateWorkspaceCommand(session_id="s", workspace_type=WorkspaceType.AUDIT))
    assert mgr.state.workspace_type == WorkspaceType.AUDIT


def test_submit_search_command_transitions_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(SubmitSearchCommand(session_id="s", query="neural nets"))
    assert mgr.state.search_query == "neural nets"


def test_set_page_command_transitions_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(SetPageCommand(session_id="s", page=4))
    assert mgr.state.page == 4


def test_apply_filter_command_transitions_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(ApplyFilterCommand(session_id="s", field="calibration_label", value="high"))
    assert mgr.state.active_filters.get("calibration_label") == "high"


def test_clear_filters_command_clears_state(dispatcher):
    d, mgr = dispatcher
    d.dispatch(ApplyFilterCommand(session_id="s", field="calibration_label", value="high"))
    d.dispatch(ClearFiltersCommand(session_id="s"))
    assert mgr.state.active_filters == {}


def test_compare_command_within_policy_allowed(dispatcher):
    d, mgr = dispatcher
    d.dispatch(CompareCommand(session_id="s", claim_ids=("c001", "c002")))
    assert "c001" in mgr.state.comparison_claim_ids


def test_compare_command_exceeds_policy_raises(dispatcher):
    d, mgr = dispatcher
    strict_policy = PolicyEngine(InteractionPolicy(
        comparison=ComparisonPolicy(max_comparison_claims=1)
    ))
    d2 = InteractionDispatcher(state_manager=mgr, policy_engine=strict_policy)
    with pytest.raises(CommandDispatchError):
        d2.dispatch(CompareCommand(session_id="s", claim_ids=("c001", "c002", "c003")))