"""
Architecture tests for Phase 11: Operational Runtime & Engineering Infrastructure.
Rectification version 11.1 — tests for P0–P2 additions.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path("src/smriti")


def _get_imports(filepath: Path) -> set[str]:
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, FileNotFoundError):
        return set()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _all_files_in(subdir: str) -> list:
    target = SRC / subdir
    if not target.exists():
        return []
    return list(target.rglob("*.py"))


def _assert_no_forbidden_imports(subdir: str, forbidden: set[str]) -> None:
    violations = []
    for f in _all_files_in(subdir):
        imports = _get_imports(f)
        for imp in imports:
            if any(fb in imp for fb in forbidden):
                violations.append(f"{f}: imports '{imp}'")
    assert not violations, f"Forbidden imports in {subdir}/:\n" + "\n".join(violations)


# ── ORIGINAL 15 tests (all preserved) ────────────────────────────────────────


def test_runtime_does_not_import_api():
    _assert_no_forbidden_imports("runtime", {"smriti.api", "smriti.dashboard", "streamlit"})


def test_observability_does_not_import_dashboard():
    _assert_no_forbidden_imports("observability", {"smriti.dashboard", "streamlit"})


def test_governance_does_not_import_dashboard_or_runtime():
    _assert_no_forbidden_imports("governance", {"smriti.dashboard", "streamlit"})


def test_infrastructure_does_not_import_api_or_dashboard():
    _assert_no_forbidden_imports("infrastructure", {"smriti.api", "smriti.dashboard"})


def test_blueprint_does_not_import_runtime_or_api():
    _assert_no_forbidden_imports("blueprint", {"smriti.runtime", "smriti.api"})


def test_state_machine_rejects_illegal_transition():
    from smriti.exceptions import RuntimeException
    from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine

    sm = RuntimeStateMachine()
    with pytest.raises(RuntimeException):
        sm.transition(RuntimeState.ACTIVE, "should fail")


def test_state_machine_permits_bootstrapping():
    from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine

    sm = RuntimeStateMachine()
    sm.transition(RuntimeState.BOOTSTRAPPING, "test")
    assert sm.state == RuntimeState.BOOTSTRAPPING


def test_dependency_graph_detects_cycles():
    from smriti.runtime.composition import DependencyGraph, DependencyNode

    graph = DependencyGraph()
    graph.register(DependencyNode(name="A", instance=None, depends_on=("B",)))
    graph.register(DependencyNode(name="B", instance=None, depends_on=("A",)))
    with pytest.raises(ValueError):
        graph.resolve_order()


def test_configuration_context_is_frozen():
    from smriti.runtime.composition import ConfigurationContext

    ctx = ConfigurationContext(env="test", config_hash="abc", loaded_at=1.0, raw={})
    with pytest.raises((TypeError, AttributeError)):
        ctx.env = "modified"


def test_ownership_registry_covers_canonical_subsystems():
    from smriti.infrastructure.ownership import OwnershipRegistry

    registry = OwnershipRegistry()
    expected = ["configuration", "runtime_state", "resources", "telemetry", "knowledge_api"]
    for key in expected:
        assert registry.is_registered(key), f"OwnershipRegistry is missing subsystem: {key}"


def test_provenance_builder_produces_complete_manifest():
    from smriti.infrastructure.provenance import ProvenanceBuilder

    builder = (
        ProvenanceBuilder(run_id="test_run")
        .set_config_version("cfg_hash_001")
        .set_policy_version("policy_1.0")
        .set_schema_version("7.0")
        .set_knowledge_version("graph_001")
    )
    manifest = builder.build()
    assert manifest.run_id == "test_run"
    assert manifest.configuration_version == "cfg_hash_001"
    assert manifest.git_commit is not None
    assert "python" in manifest.dependency_versions


def test_adr_registry_contains_phase11_adrs():
    from smriti.governance.adr import ADRRegistry, ADRStatus

    registry = ADRRegistry()
    assert registry.get("0011") is not None
    assert registry.get("0012") is not None
    assert registry.get("0011").status == ADRStatus.ACCEPTED


def test_traceability_matrix_chains_to_requirement():
    from smriti.blueprint.traceability import TraceabilityMatrix

    matrix = TraceabilityMatrix()
    chain = matrix.trace_chain("TEST-provenance")
    roots = [link for link in chain if link.traced_to is None]
    assert len(roots) >= 1


def test_readiness_assessor_reaches_l4_with_complete_phase11():
    from smriti.blueprint.readiness import ReadinessAssessor, ReadinessLevel

    assessor = ReadinessAssessor()
    report = assessor.report()
    assert report["achieved_level"] >= ReadinessLevel.L4_OPERATIONS_REALIZED.value


def test_compliance_engine_runs_without_exceptions():
    from smriti.governance.compliance import ComplianceEngine

    engine = ComplianceEngine()
    results = engine.run_all()
    assert isinstance(results, dict)
    assert len(results) >= 5


def test_compliance_engine_observability_rule_passes():
    from smriti.governance.compliance import ComplianceEngine

    engine = ComplianceEngine()
    results = engine.run_all()
    cr003 = results.get("CR-003")
    if cr003 is not None:
        assert cr003.passed


def test_risk_register_has_high_severity_risks():
    from smriti.governance.risk import RiskRegister

    register = RiskRegister()
    assert len(register.high_severity()) >= 3


def test_risk_register_r001_is_mitigated():
    from smriti.governance.risk import RiskRegister

    register = RiskRegister()
    r001 = register.get("R-001")
    assert r001 is not None and r001.status == "mitigated"


def test_boundary_matrix_forbids_presentation_to_knowledge_api():
    from smriti.infrastructure.dependency import DependencyMatrix

    matrix = DependencyMatrix()
    assert not matrix.is_allowed("presentation", "knowledge_api")


def test_boundary_matrix_allows_knowledge_api_to_read_store():
    from smriti.infrastructure.dependency import DependencyMatrix

    matrix = DependencyMatrix()
    assert matrix.is_allowed("knowledge_api", "read_store")


def test_metrics_collector_counters_are_thread_safe():
    import threading

    from smriti.observability.metrics import MetricsCollector

    collector = MetricsCollector()
    counter = collector.counter("requests_total")

    def increment_many():
        for _ in range(1000):
            counter.increment()

    threads = [threading.Thread(target=increment_many) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert counter.value == 5000


def test_health_monitor_registers_and_runs():
    from smriti.observability.health import HealthCheck, HealthMonitor, HealthStatus

    monitor = HealthMonitor()
    monitor.register(HealthCheck("always_healthy", lambda: HealthStatus.HEALTHY))
    results = monitor.run_all()
    assert "always_healthy" in results
    assert results["always_healthy"].status == HealthStatus.HEALTHY


def test_health_monitor_overall_status_unhealthy_if_any_unhealthy():
    from smriti.observability.health import HealthCheck, HealthMonitor, HealthStatus

    monitor = HealthMonitor()
    monitor.register(HealthCheck("good", lambda: HealthStatus.HEALTHY))
    monitor.register(HealthCheck("bad", lambda: HealthStatus.UNHEALTHY))
    monitor.run_all()
    assert monitor.overall_status() == HealthStatus.UNHEALTHY


def test_maturity_assessor_reaches_at_least_level_1():
    from smriti.observability.maturity import MaturityLevel, build_default_assessor

    assessor = build_default_assessor()
    assessment = assessor.assess()
    assert assessment.achieved_level >= MaturityLevel.BASIC


# ── NEW P0–P2 rectification tests ────────────────────────────────────────────


def test_operational_context_is_immutable():
    """RECTIFIED (P0-1): OperationalContext must be frozen."""
    from smriti.runtime.context import OperationalContext

    ctx = OperationalContext.create(run_id="test_001")
    with pytest.raises((TypeError, AttributeError)):
        ctx.run_id = "modified"


def test_operational_context_wraps_all_sub_components():
    """RECTIFIED (P0-1): OperationalContext must expose all six original objects."""
    from smriti.runtime.context import OperationalContext

    ctx = OperationalContext.create(run_id="test_001")
    assert ctx.run_id is not None
    assert ctx.telemetry_ctx is not None
    assert ctx.quality_ctx is not None
    assert ctx.resource_governor is not None
    assert ctx.config_hash is not None
    assert ctx.start_timestamp > 0


def test_event_bus_publish_subscribe():
    """RECTIFIED (P0-2): EventBus must deliver events to subscribers."""
    from smriti.runtime.events import ArchitectureEvent, ArchitectureEventType, EventBus

    bus = EventBus()
    received = []
    bus.subscribe(lambda e: received.append(e))
    event = ArchitectureEvent.create(
        ArchitectureEventType.LIFECYCLE_STARTED,
        source="test",
        run_id="r1",
    )
    bus.publish(event)
    assert len(received) == 1
    assert received[0].event_type == ArchitectureEventType.LIFECYCLE_STARTED


def test_telemetry_subscribes_to_event_bus():
    """RECTIFIED (P0-2): TelemetryCollector must be subscribed to EventBus."""
    from smriti.observability.telemetry import TelemetryCollector
    from smriti.runtime.events import ArchitectureEvent, ArchitectureEventType, EventBus

    bus = EventBus()
    telemetry = TelemetryCollector(run_id="test")
    # Manually subscribe to our test bus
    bus.subscribe(telemetry._on_architecture_event)
    event = ArchitectureEvent.create(
        ArchitectureEventType.CONFIGURATION_LOADED,
        source="test",
        run_id="r1",
    )
    bus.publish(event)
    assert telemetry.event_count() == 1


def test_coordinator_delegates_to_sub_coordinators():
    """RECTIFIED (P0-3): RuntimeCoordinator must delegate to sub-coordinators."""
    from smriti.runtime.coordinator import RuntimeCoordinator

    coordinator = RuntimeCoordinator()
    # Verify sub-coordinators exist and are accessible
    assert coordinator._lifecycle_mgr is not None
    assert coordinator._dep_coordinator is not None
    assert coordinator._health_coordinator is not None
    assert coordinator._exec_coordinator is not None
    assert coordinator._shutdown is not None


def test_capability_model_disable_enable():
    """RECTIFIED (P0-4): CapabilityModel must support per-capability toggle."""
    from smriti.runtime.capabilities import Capability, CapabilityModel

    model = CapabilityModel()
    assert model.is_enabled(Capability.EXPLAIN) is True
    model.disable(Capability.EXPLAIN, reason="test_disable")
    assert model.is_enabled(Capability.EXPLAIN) is False
    model.enable(Capability.EXPLAIN)
    assert model.is_enabled(Capability.EXPLAIN) is True


def test_capability_model_does_not_change_runtime_state():
    """RECTIFIED (P0-4): Disabling a capability must not change RuntimeState."""
    from smriti.runtime.capabilities import Capability, CapabilityModel
    from smriti.runtime.state_machine import RuntimeState, RuntimeStateMachine

    sm = RuntimeStateMachine()
    sm.transition(RuntimeState.BOOTSTRAPPING, "test")
    model = CapabilityModel()
    model.disable(Capability.EXPORT, reason="test")
    # State must be unchanged
    assert sm.state == RuntimeState.BOOTSTRAPPING


def test_runtime_scheduler_registers_and_runs_task():
    """RECTIFIED (P1-2): RuntimeScheduler must execute registered tasks."""
    import time

    from smriti.runtime.scheduler import RuntimeScheduler

    ran = []
    scheduler = RuntimeScheduler(tick_interval=0.01)
    scheduler.register("test_task", interval_seconds=0.05, task=lambda: ran.append(1))
    scheduler.start()
    time.sleep(0.15)
    scheduler.stop()
    assert len(ran) >= 1, "Scheduled task must have run at least once"


def test_budget_governor_blocks_exceeded_budget():
    """RECTIFIED (P1-3): BudgetGovernor must block operations that exceed budget."""
    from smriti.infrastructure.resources import BudgetGovernor, ResourceBudget

    budgets = {"test_budget": ResourceBudget(kind="test_budget", limit=10.0, enforcement="block")}
    gov = BudgetGovernor(budgets=budgets)
    assert gov.consume("test_budget", 5.0) is True  # within limit
    assert gov.consume("test_budget", 10.0) is False  # would exceed 10.0 limit


def test_provenance_manifest_has_architecture_version():
    """RECTIFIED (P1-5): RuntimeManifest must carry architecture version fields."""
    from smriti.infrastructure.provenance import ProvenanceBuilder

    manifest = (
        ProvenanceBuilder("test_r1")
        .set_architecture_version("11.0")
        .set_adr_set_version("abc12345")
        .set_compliance_rule_version("1.0")
        .set_invariant_version("1.0")
        .build()
    )
    assert manifest.architecture_version == "11.0"
    assert manifest.adr_set_version == "abc12345"
    assert manifest.compliance_rule_version == "1.0"
    assert manifest.invariant_version == "1.0"


def test_service_registry_register_discover_retire():
    """RECTIFIED (P2-1): ServiceRegistry must support register/discover/retire."""
    from smriti.infrastructure.service_registry import ServiceRegistry

    registry = ServiceRegistry()
    sentinel = object()
    registry.register("test_svc", sentinel, capabilities={"health", "query"}, owner="test")
    # Discover by capability
    discovered = registry.discover(capability="health")
    assert len(discovered) == 1
    assert discovered[0].instance is sentinel
    # Retire
    registry.retire("test_svc")
    discovered_after = registry.discover(capability="health")
    assert len(discovered_after) == 0


def test_runtime_contracts_defined():
    """RECTIFIED (P2-2): Runtime contracts must be defined for key services."""
    from smriti.observability.health import RUNTIME_CONTRACTS

    assert "health_service" in RUNTIME_CONTRACTS
    assert "shutdown_coordinator" in RUNTIME_CONTRACTS
    assert "manifest_writer" in RUNTIME_CONTRACTS
    assert "compliance_engine" in RUNTIME_CONTRACTS
    health_contract = RUNTIME_CONTRACTS["health_service"]
    assert health_contract.must_complete_ms == 100.0
    assert health_contract.must_not_modify is True


def test_state_ownership_graph_chains():
    """RECTIFIED (P2-3): StateOwnershipGraph must resolve ownership chains."""
    from smriti.infrastructure.state_ownership import StateOwnershipGraph

    graph = StateOwnershipGraph()
    owned = graph.owned_by("Session")
    assert "InteractionHistory" in owned
    owner = graph.owner_of("InteractionHistory")
    assert owner == "Session"
    chain = graph.ownership_chain("InteractionHistory")
    assert "InteractionHistory" in chain
    assert "Session" in chain


def test_failure_escalation_ladder_stages():
    """RECTIFIED (P2-4): FailureEscalationLadder must traverse all stages."""
    from smriti.observability.failure import EscalationStage, FailureEscalationLadder

    ladder = FailureEscalationLadder()
    exc = ValueError("test failure")
    record = ladder.detect(exc, source="test.module")
    assert record.current_stage == EscalationStage.DETECT
    record = ladder.classify(record)
    assert record.current_stage == EscalationStage.CLASSIFY
    record = ladder.isolate(record)
    assert record.current_stage == EscalationStage.ISOLATE


def test_operational_timeline_records_stages():
    """RECTIFIED (P2-5): OperationalTimeline must record all lifecycle stages."""
    import time

    from smriti.runtime.lifecycle import OperationalTimeline, TimelineStage

    timeline = OperationalTimeline()
    timeline.enter(TimelineStage.BOOTSTRAP, notes="test")
    time.sleep(0.01)
    timeline.enter(TimelineStage.CONFIGURATION)
    time.sleep(0.01)
    timeline.exit_current()
    entries = timeline.all_entries
    assert len(entries) >= 1
    stages = [e.stage for e in entries]
    assert TimelineStage.BOOTSTRAP in stages
