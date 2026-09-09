"""
Unit tests for NavigationView and ResultListView after the P0 fix that
removed their direct import of EpistemicStateManager (Dependency Matrix
violation, tests/architecture/test_phase10_architecture.py) and their direct
calls to state-mutating methods (navigate_back/select_claim/set_page),
replacing both with Command dispatch through InteractionDispatcher — the
same pattern SearchView already used.

Streamlit widgets (st.button etc.) require a live ScriptRunContext and are
not exercised here; these tests instead verify the piece that changed
behaviorally: that dispatching the relevant Command through the view's
dispatcher produces the correct state transition, exactly as a real button
click inside render() would.
"""
import pytest

from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.dashboard.policies.policies import PolicyEngine, InteractionPolicy
from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
from smriti.dashboard.commands.commands import (
    NavigateBackCommand,
    NavigateToCommand,
    SelectClaimCommand,
    SetPageCommand,
)
from smriti.dashboard.views.navigation_view import NavigationView
from smriti.dashboard.views.result_list_view import ResultListView


@pytest.fixture
def dispatcher():
    mgr = EpistemicStateManager(run_id="test")
    engine = PolicyEngine(InteractionPolicy())
    return InteractionDispatcher(state_manager=mgr, policy_engine=engine), mgr


def test_navigation_view_accepts_state_manager_without_importing_it(dispatcher):
    """Constructing via state_manager= must work without NavigationView
    importing the concrete EpistemicStateManager class (Dependency Matrix)."""
    _, mgr = dispatcher
    view = NavigationView(state_manager=mgr)
    assert view._dispatcher._sm is mgr


def test_navigation_view_accepts_dispatcher_directly(dispatcher):
    d, _ = dispatcher
    view = NavigationView(dispatcher=d)
    assert view._dispatcher is d


def test_navigation_view_requires_one_of_dispatcher_or_state_manager():
    with pytest.raises(ValueError):
        NavigationView()


def test_navigation_view_supports_reflects_breadcrumbs(dispatcher):
    d, mgr = dispatcher
    view = NavigationView(dispatcher=d)
    assert view.supports(None) is False
    d.dispatch(NavigateToCommand(session_id="s", claim_id="c001", label="Claim 1"))
    assert bool(mgr.state.breadcrumbs) is True
    assert view.supports(None) is True


def test_navigation_back_command_dispatch_matches_button_behavior(dispatcher):
    """Simulates what render()'s '<- Back' button does when clicked:
    dispatching NavigateBackCommand through the view's own dispatcher."""
    d, mgr = dispatcher
    view = NavigationView(dispatcher=d)
    d.dispatch(NavigateToCommand(session_id="s", claim_id="c001", label="Claim 1"))
    d.dispatch(NavigateToCommand(session_id="s", claim_id="c002", label="Claim 2"))
    before = len(mgr.state.breadcrumbs)

    view._dispatcher.dispatch(NavigateBackCommand(session_id=mgr._session_id))

    assert len(mgr.state.breadcrumbs) < before


def test_result_list_view_accepts_state_manager_without_importing_it(dispatcher):
    _, mgr = dispatcher
    view = ResultListView(state_manager=mgr, claims=[], total=0)
    assert view._dispatcher._sm is mgr


def test_result_list_view_requires_one_of_dispatcher_or_state_manager():
    with pytest.raises(ValueError):
        ResultListView(claims=[], total=0)


def test_result_list_select_claim_command_matches_button_behavior(dispatcher):
    """Simulates what render()'s claim-row button does when clicked."""
    d, mgr = dispatcher
    view = ResultListView(dispatcher=d, claims=[], total=1)

    view._dispatcher.dispatch(
        SelectClaimCommand(session_id=mgr._session_id, claim_id="c001", source_view=view.view_name)
    )

    assert mgr.state.selected_claim_id == "c001"


def test_result_list_set_page_command_matches_button_behavior(dispatcher):
    """Simulates what render()'s pagination buttons do when clicked."""
    d, mgr = dispatcher
    view = ResultListView(dispatcher=d, claims=[], total=100)
    start_page = mgr.state.page

    view._dispatcher.dispatch(SetPageCommand(session_id=mgr._session_id, page=start_page + 1))

    assert mgr.state.page == start_page + 1
