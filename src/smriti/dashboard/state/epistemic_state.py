"""
epistemic_state.py — EpistemicState domain object and transitions.

EpistemicState is the single source of truth for the current interaction session.
It represents "what the user is currently investigating."

Rules:
    ✅ All transitions are explicit (no hidden mutations)
    ✅ Every transition preserves investigation history
    ✅ Every transition publishes an event to InteractionEventBus
    ✅ State is serializable for workspace restoration
    ❌ State never computes knowledge
    ❌ State never accesses Phase 9 directly
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional

from smriti.core.models import (
    EpistemicLens,
    EpistemicState,
    ExplainabilityLevel,
    InteractionEvent,
    InteractionEventType,
    InteractionIntent,
    WorkspaceStatus,
    WorkspaceType,
)


class EpistemicStateManager:
    """
    Manages transitions of EpistemicState.

    All mutations go through this manager.
    Direct mutations to EpistemicState are forbidden.

    Every transition:
        1. Updates _state via dataclasses.replace()
        2. Emits an InteractionEvent to the event bus
    """

    def __init__(self, run_id: str, event_bus=None) -> None:
        self._session_id = str(uuid.uuid4())[:8]
        self._state = EpistemicState(
            run_id=run_id,
            session_id=self._session_id,
        )
        self._event_log: List[InteractionEvent] = []
        self._event_bus = event_bus  # Optional — injected after bootstrap

    def set_event_bus(self, event_bus) -> None:
        """Inject the event bus after construction (avoids circular init)."""
        self._event_bus = event_bus

    @property
    def state(self) -> EpistemicState:
        return self._state

    @property
    def event_log(self) -> List[InteractionEvent]:
        return list(self._event_log)

    def _emit(self, event_type: InteractionEventType, payload: Dict[str, Any]) -> None:
        """Emit, log, and publish an interaction event."""
        event = InteractionEvent(
            event_type=event_type,
            payload=payload,
            timestamp_ms=time.monotonic() * 1000,
            session_id=self._session_id,
        )
        self._event_log.append(event)
        if self._event_bus is not None:
            self._event_bus.publish(event)

    # ── Claim selection ───────────────────────────────────────────────────────

    def select_claim(self, claim_id: str) -> None:
        """Transition: user selects a claim."""
        old_id = self._state.selected_claim_id
        self._state = replace(self._state, selected_claim_id=claim_id)
        self._emit(
            InteractionEventType.CLAIM_SELECTED,
            {"claim_id": claim_id, "previous_claim_id": old_id},
        )

    def deselect_claim(self) -> None:
        """Transition: user deselects current claim."""
        self._emit(
            InteractionEventType.CLAIM_DESELECTED,
            {"claim_id": self._state.selected_claim_id},
        )
        self._state = replace(self._state, selected_claim_id=None)

    # ── Workspace activation ──────────────────────────────────────────────────

    def activate_workspace(self, workspace_type: WorkspaceType, lens: EpistemicLens = None) -> None:
        """Transition: user activates a workspace."""
        default_lens_map = {
            WorkspaceType.RESEARCH:    EpistemicLens.EXPLORATION,
            WorkspaceType.RELIABILITY: EpistemicLens.RELIABILITY,
            WorkspaceType.CONFLICT:    EpistemicLens.CONFLICT,
            WorkspaceType.AUDIT:       EpistemicLens.AUDIT,
            WorkspaceType.PROVENANCE:  EpistemicLens.PROVENANCE,
            WorkspaceType.STATISTICS:  EpistemicLens.EXPLORATION,
            WorkspaceType.TOPOLOGY:    EpistemicLens.TOPOLOGY,
        }
        active_lens = lens or default_lens_map.get(workspace_type, EpistemicLens.EXPLORATION)
        self._state = replace(
            self._state,
            workspace_type=workspace_type,
            active_lens=active_lens,
            selected_claim_id=None,    # Always clear selection on workspace switch
            page=0,
            workspace_status=WorkspaceStatus.ACTIVE,
        )
        self._emit(
            InteractionEventType.WORKSPACE_ACTIVATED,
            {"workspace_type": workspace_type.value, "lens": active_lens.value},
        )

    def suspend_workspace(self) -> None:
        """Transition: workspace suspended (another takes focus)."""
        self._state = replace(self._state, workspace_status=WorkspaceStatus.SUSPENDED)
        self._emit(InteractionEventType.WORKSPACE_SUSPENDED,
                   {"workspace_type": self._state.workspace_type.value})

    def resume_workspace(self) -> None:
        """Transition: suspended workspace resumes."""
        self._state = replace(self._state, workspace_status=WorkspaceStatus.ACTIVE)
        self._emit(InteractionEventType.WORKSPACE_RESUMED,
                   {"workspace_type": self._state.workspace_type.value})

    # ── Filters ───────────────────────────────────────────────────────────────

    def apply_filter(self, field: str, value: Any) -> None:
        """Transition: user applies a filter."""
        new_filters = dict(self._state.active_filters)
        new_filters[field] = value
        self._state = replace(self._state, active_filters=new_filters, page=0)
        self._emit(
            InteractionEventType.FILTER_APPLIED,
            {"field": field, "value": str(value)},
        )

    def remove_filter(self, field: str) -> None:
        """Transition: user removes a filter."""
        new_filters = dict(self._state.active_filters)
        new_filters.pop(field, None)
        self._state = replace(self._state, active_filters=new_filters, page=0)
        self._emit(InteractionEventType.FILTER_REMOVED, {"field": field})

    def clear_filters(self) -> None:
        """Transition: user clears all filters."""
        self._state = replace(self._state, active_filters={}, search_query="", page=0)

    # ── Search ────────────────────────────────────────────────────────────────

    def submit_search(self, query: str) -> None:
        """Transition: user submits a search."""
        self._state = replace(self._state, search_query=query, page=0)
        self._emit(InteractionEventType.SEARCH_SUBMITTED, {"query": query})

    # ── Explainability ────────────────────────────────────────────────────────

    def set_explainability(self, level: int) -> None:
        """Transition: user changes explainability depth."""
        self._state = replace(self._state, explainability_level=level)
        self._emit(InteractionEventType.EXPLAINABILITY_CHANGED, {"level": level})

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to(self, claim_id: str, label: str = "") -> None:
        """Transition: user navigates to a claim."""
        crumbs = list(self._state.breadcrumbs)
        crumbs.append({"claim_id": claim_id, "label": label or claim_id[:8]})
        if len(crumbs) > 8:
            crumbs = crumbs[-8:]

        history = list(self._state.navigation_history)
        if claim_id not in history[-3:]:
            history.append(claim_id)
        if len(history) > 20:
            history = history[-20:]

        self._state = replace(
            self._state,
            selected_claim_id=claim_id,
            breadcrumbs=crumbs,
            navigation_history=history,
        )
        self._emit(InteractionEventType.NAVIGATION_REQUESTED, {"claim_id": claim_id})

    def navigate_back(self) -> Optional[str]:
        """Navigate to previous claim. Returns claim_id or None."""
        crumbs = list(self._state.breadcrumbs)
        if len(crumbs) > 1:
            crumbs.pop()
            prev_claim_id = crumbs[-1]["claim_id"] if crumbs else None
            self._state = replace(
                self._state,
                breadcrumbs=crumbs,
                selected_claim_id=prev_claim_id,
            )
            return prev_claim_id
        return None

    # ── Pagination + sort ─────────────────────────────────────────────────────

    def set_page(self, page: int) -> None:
        self._state = replace(self._state, page=max(0, page))

    def set_sort(self, field: str, order: str) -> None:
        self._state = replace(self._state, sort_field=field, sort_order=order, page=0)

    # ── Comparison ────────────────────────────────────────────────────────────

    def set_comparison_claims(self, claim_ids: tuple) -> None:
        """Transition: comparison selection."""
        self._state = replace(self._state, comparison_claim_ids=claim_ids[:2])
        self._emit(
            InteractionEventType.COMPARISON_STARTED,
            {"claim_ids": list(claim_ids)},
        )

    def end_comparison(self) -> None:
        """Transition: comparison panel closed."""
        self._state = replace(self._state, comparison_claim_ids=tuple())
        self._emit(InteractionEventType.COMPARISON_ENDED, {})

    # ── Serialization ─────────────────────────────────────────────────────────

    def serialize(self) -> Dict[str, Any]:
        """Serialize state for workspace restoration."""
        s = self._state
        return {
            "workspace_type": s.workspace_type.value,
            "active_lens": s.active_lens.value,
            "selected_claim_id": s.selected_claim_id,
            "search_query": s.search_query,
            "active_filters": dict(s.active_filters),
            "sort_field": s.sort_field,
            "sort_order": s.sort_order,
            "page": s.page,
            "explainability_level": s.explainability_level,
            "breadcrumbs": list(s.breadcrumbs),
            "run_id": s.run_id,
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from a serialized snapshot."""
        try:
            self._state = replace(
                self._state,
                workspace_type=WorkspaceType(snapshot.get("workspace_type", "research")),
                active_lens=EpistemicLens(snapshot.get("active_lens", "exploration")),
                selected_claim_id=snapshot.get("selected_claim_id"),
                search_query=snapshot.get("search_query", ""),
                active_filters=snapshot.get("active_filters", {}),
                sort_field=snapshot.get("sort_field", "reliability_index"),
                sort_order=snapshot.get("sort_order", "desc"),
                page=snapshot.get("page", 0),
                explainability_level=snapshot.get("explainability_level", 0),
                breadcrumbs=snapshot.get("breadcrumbs", []),
            )
            self._emit(InteractionEventType.WORKSPACE_RESTORED,
                       {"source": "snapshot"})
        except Exception as e:
            import structlog
            structlog.get_logger(__name__).warning(
                "workspace restoration failed, starting fresh", error=str(e)
            )