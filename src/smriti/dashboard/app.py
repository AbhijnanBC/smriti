"""
app.py — SMRITI Phase 10: Human Knowledge Interaction Layer.

THIN ENTRY POINT. All logic lives in dashboard/controller/.

Architecture role:
    ✅ Streamlit page configuration (must be first call)
    ✅ Calls SessionBootstrap.bootstrap()
    ✅ Calls SidebarController.render()
    ✅ Calls RenderCoordinator.render()
    ❌ Zero business logic
    ❌ Zero Phase 9 access
    ❌ Zero workspace rendering

Entry point:
    poetry run streamlit run src/smriti/dashboard/app.py
"""

from __future__ import annotations

import streamlit as st

# ── Page configuration (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title="SMRITI — Knowledge Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Controller imports ────────────────────────────────────────────────────────
from smriti.dashboard.controller.session_bootstrap import (
    bootstrap,
    get_registry,
    get_policy_engine,
    get_export_pipeline,
)
from smriti.dashboard.controller.sidebar_controller import SidebarController
from smriti.dashboard.controller.render_coordinator import RenderCoordinator
from smriti.dashboard.state.session import (
    get_state_manager,
    get_client,
    get_notification_center,
)

# ── Controllers (stateless — created each cycle, cheap) ───────────────────────
_sidebar    = SidebarController()
_renderer   = RenderCoordinator()


def main() -> None:
    """
    Phase 10 interaction loop.
    Streamlit re-executes this on every user interaction.
    """
    # Step 1: Bootstrap (no-op after first call)
    ok = bootstrap()
    if not ok:
        st.error(
            "⚠️ No knowledge base loaded. "
            "Run the SMRITI pipeline first:\n"
            "`poetry run python -m smriti.main`"
        )
        st.info(
            "Then launch:\n"
            "`poetry run streamlit run src/smriti/dashboard/app.py`"
        )
        return

    # Step 2: Retrieve session subsystems
    state_manager      = get_state_manager()
    client             = get_client()
    policy_engine      = get_policy_engine()
    notification_center = get_notification_center()
    registry           = get_registry()
    export_pipeline    = get_export_pipeline()

    # Step 3: Render sidebar
    _sidebar.render(state_manager, policy_engine, export_pipeline)

    # Step 4: Render active workspace
    _renderer.render(
        registry=registry,
        state_manager=state_manager,
        client=client,
        policy_engine=policy_engine,
        notification_center=notification_center,
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()