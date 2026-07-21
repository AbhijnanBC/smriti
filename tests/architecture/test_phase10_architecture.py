"""
Architecture tests for Phase 10.

These tests verify structural invariants — import boundaries, layer discipline,
presentation model enforcement. They fail fast when the architecture is violated.

Run independently:
    poetry run pytest tests/architecture/ -v

Rules validated here:
    1. No dashboard module imports from Phase 8 or below
    2. No workspace imports KnowledgeGraph directly
    3. No component imports KnowledgeAPI directly
    4. No view imports ServiceClient directly
    5. Presentation model layer enforced (views never import dict utilities)
    6. app.py remains thin (line count limit)
    7. Dependency matrix enforced (explicit forbidden imports per layer)
"""

import ast
import importlib
from pathlib import Path
import pytest


SRC = Path("src/smriti/dashboard")


def _get_imports(filepath: Path) -> set:
    """Parse a Python file and return all top-level imported module strings."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _all_dashboard_files():
    return list(SRC.rglob("*.py"))


# ── Layer boundary tests ──────────────────────────────────────────────────────

def test_no_dashboard_module_imports_knowledge_graph():
    """Dashboard must never import KnowledgeGraph or ScoredKnowledgeGraph."""
    forbidden = {"smriti.core.knowledge_graph", "smriti.knowledge_graph",
                 "smriti.graph", "ScoredKnowledgeGraph"}
    violations = []
    for f in _all_dashboard_files():
        imports = _get_imports(f)
        for imp in imports:
            if any(fb in imp for fb in forbidden):
                violations.append(f"{f.relative_to(SRC)}: imports {imp}")
    assert not violations, "Dashboard imports KnowledgeGraph:\n" + "\n".join(violations)


def test_no_dashboard_module_imports_phase8_directly():
    """Dashboard must never call Phase 8 scorers directly."""
    forbidden = {"smriti.phase8", "smriti.scoring", "smriti.reliability_scorer"}
    violations = []
    for f in _all_dashboard_files():
        imports = _get_imports(f)
        for imp in imports:
            if any(fb in imp for fb in forbidden):
                violations.append(f"{f.relative_to(SRC)}: imports {imp}")
    assert not violations, "Dashboard imports Phase 8:\n" + "\n".join(violations)


def test_views_do_not_import_service_client():
    """Views must receive data via PresentationModels, not call ServiceClient."""
    views_dir = SRC / "views"
    if not views_dir.exists():
        pytest.skip("views/ directory not yet created")
    violations = []
    for f in views_dir.rglob("*.py"):
        if f.name == "base_view.py":
            continue
        imports = _get_imports(f)
        for imp in imports:
            if "services.client" in imp or "ServiceClient" in imp:
                violations.append(f"{f.name}: imports ServiceClient")
    assert not violations, "Views import ServiceClient:\n" + "\n".join(violations)


def test_components_do_not_import_knowledge_api():
    """Components must never bypass ServiceClient."""
    components_dir = SRC / "components"
    if not components_dir.exists():
        pytest.skip("components/ directory not yet created")
    violations = []
    for f in components_dir.rglob("*.py"):
        imports = _get_imports(f)
        for imp in imports:
            if "KnowledgeAPI" in imp or "knowledge_api" in imp:
                violations.append(f"{f.name}: imports KnowledgeAPI")
    assert not violations, "Components import KnowledgeAPI:\n" + "\n".join(violations)


def test_workspaces_do_not_import_raw_dict_renderers():
    """Workspaces must use views/components, not render raw dicts via st.*."""
    # This is a static analysis proxy: workspaces should import from views/ or components/
    # and should import DTOTransformer (not bypass it).
    workspaces_dir = SRC / "workspaces"
    if not workspaces_dir.exists():
        pytest.skip("workspaces/ directory not yet created")
    # Workspaces that render raw dicts typically import json or call .items() on API resp.
    # We check that every workspace that renders imports DTOTransformer.
    excluded = {"__init__.py", "base.py", "registry.py", "manager.py",
                "serializer.py", "context.py", "view_coordinator.py"}
    violations = []
    for f in workspaces_dir.rglob("*.py"):
        if f.name in excluded:
            continue
        imports = _get_imports(f)
        has_dto = any("presentation" in imp or "DTOTransformer" in imp for imp in imports)
        if not has_dto:
            violations.append(f"{f.name}: does not import DTOTransformer or presentation")
    assert not violations, "Workspaces bypass DTOTransformer:\n" + "\n".join(violations)


# ── Structural tests ──────────────────────────────────────────────────────────

def test_app_py_is_thin():
    """app.py must remain a thin entry point (≤ 70 non-blank, non-comment lines)."""
    app_file = SRC / "app.py"
    if not app_file.exists():
        pytest.skip("app.py not yet created")
    lines = app_file.read_text(encoding="utf-8").splitlines()
    code_lines = [
        l for l in lines
        if l.strip() and not l.strip().startswith("#")
    ]
    assert len(code_lines) <= 70, (
        f"app.py has {len(code_lines)} code lines — should stay ≤ 70. "
        "Move logic to controller/."
    )


def test_service_client_does_not_contain_api_calls():
    """ServiceClient should only delegate — no direct _api.* calls beyond property access."""
    client_file = SRC / "services" / "client.py"
    if not client_file.exists():
        pytest.skip("client.py not yet created")
    source = client_file.read_text(encoding="utf-8")
    # ServiceClient delegates; only the individual service files call _api.*
    # Ensure client.py has no direct self._api.get_claim / self._api.search lines
    direct_api_calls = [
        line.strip() for line in source.splitlines()
        if "self._api.get_claim" in line
        or "self._api.search(" in line
        or "self._api.statistics(" in line
        or "self._api.traverse(" in line
        or "self._api.export(" in line
        or "self._api.explain(" in line
    ]
    assert not direct_api_calls, (
        f"ServiceClient calls Phase 9 API directly — delegate to service modules:\n"
        + "\n".join(direct_api_calls)
    )


# ── Dependency Matrix enforcement ─────────────────────────────────────────────

def test_dependency_matrix_enforcement():
    """
    Strictly enforces the Phase 10 Dependency Matrix.
    Forbidden edges result in immediate CI failure.

    Matrix:
        views:        Cannot import services, api, KnowledgeAPI, or epistemic_state.
        components:   Cannot import state, services, api, KnowledgeAPI, or workspaces.
        workspaces:   Cannot import scoring, phase8, or graph_construction.
        models:       Must be pure Python — cannot import services, api, or streamlit.
    """
    DEPENDENCY_MATRIX = {
        "views": ["services", "api", "KnowledgeAPI", "epistemic_state"],
        "components": ["state", "services", "api", "KnowledgeAPI", "workspaces"],
        "workspaces": ["scoring", "phase8", "graph_construction"],
        "models": ["services", "api", "streamlit"],
    }

    violations = []

    for layer, forbidden_imports in DEPENDENCY_MATRIX.items():
        layer_dir = SRC / layer
        if not layer_dir.exists():
            continue

        for filepath in layer_dir.rglob("*.py"):
            try:
                tree = ast.parse(filepath.read_text(encoding="utf-8"))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Get the module name (for ImportFrom, module can be None)
                    module_name = getattr(node, 'module', '') or ''
                    for alias in getattr(node, 'names', []):
                        # For relative imports (e.g., from . import x), module_name is ''
                        # We need to reconstruct the full import string.
                        full_import = f"{module_name}.{alias.name}".lstrip('.')

                        for forbidden in forbidden_imports:
                            if forbidden in full_import:
                                violations.append(
                                    f"VIOLATION in {layer}/{filepath.name}: "
                                    f"Imported '{full_import}' (Forbidden: '{forbidden}')"
                                )

    assert not violations, "Dependency Matrix Violations Found:\n" + "\n".join(violations)


# ── Determinism tests ─────────────────────────────────────────────────────────

def test_same_state_same_serialize():
    """Same EpistemicState always produces identical serialization."""
    from smriti.dashboard.state.epistemic_state import EpistemicStateManager
    from smriti.core.models import WorkspaceType

    mgr1 = EpistemicStateManager(run_id="r1")
    mgr2 = EpistemicStateManager(run_id="r1")

    for mgr in (mgr1, mgr2):
        mgr.activate_workspace(WorkspaceType.AUDIT)
        mgr.apply_filter("calibration_label", "high")
        mgr.select_claim("c001")

    snap1 = mgr1.serialize()
    snap2 = mgr2.serialize()

    # Both snapshots must agree on all deterministic fields
    assert snap1["workspace_type"] == snap2["workspace_type"]
    assert snap1["active_lens"]    == snap2["active_lens"]
    assert snap1["active_filters"] == snap2["active_filters"]
    assert snap1["selected_claim_id"] == snap2["selected_claim_id"]


# ── Workspace serializer tests ────────────────────────────────────────────────

def test_workspace_serializer_round_trip():
    """WorkspaceSerializer must survive a round-trip."""
    from smriti.dashboard.state.epistemic_state import EpistemicStateManager
    from smriti.dashboard.workspaces.serializer import WorkspaceSerializer
    from smriti.core.models import WorkspaceType

    mgr = EpistemicStateManager(run_id="r1")
    mgr.activate_workspace(WorkspaceType.RELIABILITY)
    mgr.apply_filter("calibration_label", "high")

    snapshot = mgr.serialize()
    json_str = WorkspaceSerializer.to_json(snapshot)
    restored = WorkspaceSerializer.from_json(json_str)

    assert WorkspaceSerializer.validate_snapshot(restored)
    assert restored["workspace_type"] == WorkspaceType.RELIABILITY.value


# ── Interaction pipeline tests ────────────────────────────────────────────────

def test_click_to_state_pipeline():
    """
    Full pipeline: Command → Dispatcher → State Transition → Event Log.
    Simulates a user clicking a claim, without Streamlit.
    """
    from smriti.dashboard.state.epistemic_state import EpistemicStateManager
    from smriti.dashboard.policies.policies import PolicyEngine, InteractionPolicy
    from smriti.dashboard.controller.interaction_dispatcher import InteractionDispatcher
    from smriti.dashboard.commands.commands import SelectClaimCommand
    from smriti.core.models import InteractionEventType

    mgr = EpistemicStateManager(run_id="test")
    engine = PolicyEngine(InteractionPolicy())
    dispatcher = InteractionDispatcher(state_manager=mgr, policy_engine=engine)

    # Simulate click
    dispatcher.dispatch(SelectClaimCommand(session_id="s", claim_id="c_pipeline_test"))

    # State transitioned
    assert mgr.state.selected_claim_id == "c_pipeline_test"

    # Event emitted
    events = mgr.event_log
    assert any(e.event_type == InteractionEventType.CLAIM_SELECTED for e in events)
    select_event = next(
        e for e in events if e.event_type == InteractionEventType.CLAIM_SELECTED
    )
    assert select_event.payload["claim_id"] == "c_pipeline_test"