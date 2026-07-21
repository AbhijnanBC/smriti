"""
session_bootstrap.py — SessionBootstrap for Phase 10.

Handles all one-time session initialization.
app.py calls bootstrap() and then controller.run().
Everything else is decoupled from the entry point.

Responsibilities:
    ✅ Locate or load KnowledgeAPI
    ✅ Initialize all session subsystems exactly once
    ✅ Build ExportPipeline
    ✅ Build WorkspaceRegistry
    ✅ Return False if initialization fails (app.py shows error and stops)
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
from typing import Optional

from smriti.dashboard.state.session import initialize_session, SESSION_KEY_INITIALIZED
from smriti.dashboard.workspaces.registry import build_default_registry
from smriti.dashboard.policies.policies import load_interaction_policy, PolicyEngine
from smriti.dashboard.policies.policy_registry import PolicyRegistry

SESSION_KEY_REGISTRY       = "smriti_registry"
SESSION_KEY_POLICY_ENGINE  = "smriti_policy_engine"
SESSION_KEY_POLICY_REGISTRY = "smriti_policy_registry"
SESSION_KEY_EXPORT_PIPELINE = "smriti_export_pipeline"


def get_or_load_api():
    """
    Retrieve the KnowledgeAPI.

    In pipeline mode: reads from st.session_state["smriti_api"].
    In standalone mode: builds from the most recent Phase 8 artifact.
    """
    if "smriti_api" in st.session_state:
        return st.session_state["smriti_api"]

    try:
        from smriti.core.paths import ARTIFACTS_DIR
        from smriti.api import build_knowledge_api

        phase8_files = sorted(
            ARTIFACTS_DIR.glob("run_*/phase8/dataset.json"),
            key=lambda p: p.parent.parent.name,
            reverse=True,
        )
        if not phase8_files:
            return None

        dataset_path = phase8_files[0]
        run_id = dataset_path.parent.parent.name.replace("run_", "")

        from smriti.pipeline.runner import PipelineRunner
        runner = PipelineRunner.__new__(PipelineRunner)
        runner.run_id = run_id

        scored_graph = runner._load_phase8_result()
        api = build_knowledge_api(scored_graph)
        st.session_state["smriti_api"] = api
        return api

    except Exception as e:
        st.error(f"Failed to load knowledge base: {e}")
        return None


def bootstrap(api=None) -> bool:
    """
    Full one-time session bootstrap.
    Returns True if successful, False if initialization failed.
    """
    # Locate API
    if api is None:
        api = get_or_load_api()

    if api is None:
        return False

    # Initialize session subsystems (idempotent)
    initialize_session(api)

    # Build registry (idempotent)
    if SESSION_KEY_REGISTRY not in st.session_state:
        st.session_state[SESSION_KEY_REGISTRY] = build_default_registry()

    # Build policy engine (idempotent)
    if SESSION_KEY_POLICY_ENGINE not in st.session_state:
        policy = load_interaction_policy()
        st.session_state[SESSION_KEY_POLICY_ENGINE] = PolicyEngine(policy)

    # Build policy registry (idempotent)
    if SESSION_KEY_POLICY_REGISTRY not in st.session_state:
        pr = PolicyRegistry()
        st.session_state[SESSION_KEY_POLICY_REGISTRY] = pr

    # Build export pipeline (idempotent)
    if SESSION_KEY_EXPORT_PIPELINE not in st.session_state:
        from smriti.dashboard.state.session import get_client
        from smriti.dashboard.export.pipeline import ExportPipeline
        client = get_client()
        policy_engine = st.session_state[SESSION_KEY_POLICY_ENGINE]
        st.session_state[SESSION_KEY_EXPORT_PIPELINE] = ExportPipeline(
            service_client=client,
            policy_engine=policy_engine,
            run_id=api.run_id,
        )

    return True


def get_registry():
    return st.session_state[SESSION_KEY_REGISTRY]

def get_policy_engine() -> PolicyEngine:
    return st.session_state[SESSION_KEY_POLICY_ENGINE]

def get_export_pipeline():
    return st.session_state[SESSION_KEY_EXPORT_PIPELINE]