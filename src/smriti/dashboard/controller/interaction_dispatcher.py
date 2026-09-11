"""
interaction_dispatcher.py — InteractionDispatcher for Phase 10.

The formal dispatch layer that sits between the UI and EpistemicStateManager.

Every user action that can be encoded as a Command comes here first.

Dispatch chain:
    Command
        │
        ▼
    PolicyEngine.validate()   ← reject if policy violated
        │
        ▼
    EpistemicStateManager.transition()
        │
        ▼
    InteractionEvent emitted to EventBus automatically

Rules:
    ✅ All routable user actions come through the dispatcher
    ✅ Policy is checked before every state transition
    ✅ Dispatcher raises CommandDispatchError on policy violation
    ❌ Dispatcher never renders Streamlit elements
    ❌ Dispatcher never calls Phase 9
"""

from __future__ import annotations

import structlog
from smriti.dashboard.commands.commands import (
    ActivateWorkspaceCommand,
    ApplyFilterCommand,
    BaseCommand,
    ClearFiltersCommand,
    CompareCommand,
    DeselectClaimCommand,
    EndComparisonCommand,
    ExportCommand,
    NavigateBackCommand,
    NavigateToCommand,
    RemoveFilterCommand,
    RestoreWorkspaceCommand,
    SelectClaimCommand,
    SerializeWorkspaceCommand,
    SetExplainabilityCommand,
    SetPageCommand,
    SetSortCommand,
    SubmitSearchCommand,
)
from smriti.dashboard.policies.policies import PolicyEngine
from smriti.dashboard.state.epistemic_state import EpistemicStateManager
from smriti.exceptions import CommandDispatchError

logger = structlog.get_logger(__name__)


class InteractionDispatcher:
    """
    Routes Commands through PolicyEngine to EpistemicStateManager.
    One instance per session.
    """

    def __init__(
        self,
        state_manager: EpistemicStateManager,
        policy_engine: PolicyEngine,
    ) -> None:
        self._sm = state_manager
        self._policy = policy_engine

    # Dispatches on the full BaseCommand subclass table (one isinstance
    # branch per command type); flat by design so adding a command type is
    # a one-line addition, but the branch count trips mccabe's threshold.
    def dispatch(self, command: BaseCommand) -> None:  # noqa: C901
        """
        Dispatch a command. Validates policy, then applies state transition.
        Raises CommandDispatchError if policy denies the action.
        """
        logger.debug("dispatching command", command_type=type(command).__name__)

        # ── Policy validation for all commands ──────────────────────────────────
        self._validate_policy(command)

        # ── Apply state transition ──────────────────────────────────────────────
        if isinstance(command, SelectClaimCommand):
            self._sm.select_claim(command.claim_id)

        elif isinstance(command, DeselectClaimCommand):
            self._sm.deselect_claim()

        elif isinstance(command, ActivateWorkspaceCommand):
            self._sm.activate_workspace(command.workspace_type, command.lens)

        elif isinstance(command, ApplyFilterCommand):
            self._sm.apply_filter(command.field, command.value)

        elif isinstance(command, RemoveFilterCommand):
            self._sm.remove_filter(command.field)

        elif isinstance(command, ClearFiltersCommand):
            self._sm.clear_filters()

        elif isinstance(command, SubmitSearchCommand):
            self._sm.submit_search(command.query)

        elif isinstance(command, NavigateToCommand):
            self._sm.navigate_to(command.claim_id, command.label)

        elif isinstance(command, NavigateBackCommand):
            self._sm.navigate_back()

        elif isinstance(command, SetExplainabilityCommand):
            self._sm.set_explainability(command.level)

        elif isinstance(command, CompareCommand):
            self._sm.set_comparison_claims(tuple(command.claim_ids))

        elif isinstance(command, EndComparisonCommand):
            self._sm.end_comparison()

        elif isinstance(command, SetPageCommand):
            self._sm.set_page(command.page)

        elif isinstance(command, SetSortCommand):
            self._sm.set_sort(command.sort_field, command.sort_order)

        elif isinstance(command, SerializeWorkspaceCommand):
            # Serialization result is available via state_manager.serialize()
            _ = self._sm.serialize()

        elif isinstance(command, RestoreWorkspaceCommand):
            self._sm.restore(command.snapshot)

        elif isinstance(command, ExportCommand):
            # Export pipeline handles actual I/O — dispatcher only validates
            pass

        else:
            logger.warning("unknown command type", command_type=type(command).__name__)

    def _validate_policy(self, command: BaseCommand) -> None:
        """
        Validate the command against the policy engine.
        Raises CommandDispatchError if policy denies the action.
        """
        allowed, reason = self._policy.validate_command(command)
        if not allowed:
            raise CommandDispatchError(f"Policy denied command {type(command).__name__}: {reason}")
