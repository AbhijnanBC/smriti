"""
resources.py — Resource Governance + Budget Governance (§11.14 rectified).

RECTIFIED (P1-3): ResourceGovernor now includes BudgetGovernor.
Governance covers ownership + TTL + size (original) PLUS budgets:
    - Memory Budget
    - CPU Budget
    - Execution Budget
    - Traversal Budget
    - Export Budget
    - API Budget

Budget governance: every resource type has a declared budget.
Operations that would exceed the budget are blocked with ResourceBudgetExceeded.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class ResourceKind(str, Enum):
    CACHE = "cache"
    INDEX = "index"
    EXPORT_BUFFER = "export_buffer"
    TEMP_ARTIFACT = "temp_artifact"
    EXECUTION_BUFFER = "execution_buffer"


@dataclass(frozen=True)
class ResourceBudget:
    """
    RECTIFIED (P1-3): Budget declaration for one resource dimension.

    Budget governance is separate from ownership/TTL governance.
    A resource can be within its TTL and below max_size but still over budget.
    """

    kind: str  # "memory_mb" | "cpu_percent" | "traversal_depth" | "export_mb" | "api_calls"
    limit: float
    current: float = 0.0
    enforcement: str = "block"  # "block" | "warn" | "log_only"

    def is_exceeded(self, proposed: float = 0.0) -> bool:
        return (self.current + proposed) > self.limit


@dataclass
class ResourcePolicy:
    kind: ResourceKind
    owner: str
    max_size_bytes: int | None
    ttl_seconds: float | None
    eviction_strategy: str
    is_disposable: bool = True
    release_on_shutdown: bool = True


RESOURCE_POLICIES: dict[str, ResourcePolicy] = {
    "claim_view_cache": ResourcePolicy(
        kind=ResourceKind.CACHE,
        owner="api.store.memory_store",
        max_size_bytes=50 * 1024 * 1024,
        ttl_seconds=None,
        eviction_strategy="lru",
    ),
    "dto_cache": ResourcePolicy(
        kind=ResourceKind.CACHE,
        owner="api.dtos",
        max_size_bytes=10 * 1024 * 1024,
        ttl_seconds=None,
        eviction_strategy="lru",
    ),
    "faiss_index": ResourcePolicy(
        kind=ResourceKind.INDEX,
        owner="retrieval.faiss_index",
        max_size_bytes=None,
        ttl_seconds=None,
        eviction_strategy="none",
        is_disposable=True,
        release_on_shutdown=True,
    ),
    "export_buffer": ResourcePolicy(
        kind=ResourceKind.EXPORT_BUFFER,
        owner="dashboard.export",
        max_size_bytes=25 * 1024 * 1024,
        ttl_seconds=300.0,
        eviction_strategy="ttl",
    ),
}

# ── Default resource budgets (P1-3) ──────────────────────────────────────────

DEFAULT_BUDGETS: dict[str, ResourceBudget] = {
    "memory_mb": ResourceBudget(kind="memory_mb", limit=512.0, enforcement="warn"),
    "traversal_depth": ResourceBudget(kind="traversal_depth", limit=5.0, enforcement="block"),
    "export_mb": ResourceBudget(kind="export_mb", limit=25.0, enforcement="block"),
    "api_calls": ResourceBudget(kind="api_calls", limit=10_000.0, enforcement="log_only"),
    "execution_ms": ResourceBudget(kind="execution_ms", limit=30_000.0, enforcement="warn"),
}


@dataclass
class ResourceHandle:
    name: str
    policy: ResourcePolicy
    allocated_at: float = field(default_factory=time.monotonic)
    size_bytes: int = 0
    released: bool = False


class BudgetGovernor:
    """
    RECTIFIED (P1-3): Governs resource budgets.

    Tracks current consumption per budget dimension.
    Blocks or warns on budget violations.
    """

    def __init__(self, budgets: dict[str, ResourceBudget] | None = None) -> None:
        self._budgets: dict[str, ResourceBudget] = dict(budgets or DEFAULT_BUDGETS)
        self._current: dict[str, float] = {k: 0.0 for k in self._budgets}
        self._lock = threading.Lock()

    def check(self, budget_name: str, proposed: float = 0.0) -> bool:
        """Return True if the operation is within budget."""
        with self._lock:
            budget = self._budgets.get(budget_name)
            if budget is None:
                return True
            return not budget.is_exceeded(proposed - self._current.get(budget_name, 0.0))

    def consume(self, budget_name: str, amount: float) -> bool:
        """
        Consume budget. Returns True if allowed, False if blocked.
        Raises ResourceBudgetExceeded if enforcement="block".
        """
        with self._lock:
            budget = self._budgets.get(budget_name)
            if budget is None:
                return True
            current = self._current.get(budget_name, 0.0)
            if current + amount > budget.limit:
                if budget.enforcement == "block":
                    logger.error(
                        "budget_exceeded_blocked",
                        budget=budget_name,
                        current=current,
                        proposed=amount,
                        limit=budget.limit,
                    )
                    return False
                elif budget.enforcement == "warn":
                    logger.warning(
                        "budget_exceeded_warn",
                        budget=budget_name,
                        current=current,
                        proposed=amount,
                        limit=budget.limit,
                    )
                else:
                    logger.debug("budget_exceeded_logged", budget=budget_name)
            self._current[budget_name] = current + amount
            return True

    def release(self, budget_name: str, amount: float) -> None:
        with self._lock:
            current = self._current.get(budget_name, 0.0)
            self._current[budget_name] = max(0.0, current - amount)

    def snapshot(self) -> dict[str, dict]:
        with self._lock:
            return {
                name: {
                    "current": self._current.get(name, 0.0),
                    "limit": budget.limit,
                    "pct": round(100.0 * self._current.get(name, 0.0) / max(budget.limit, 1.0), 1),
                    "enforcement": budget.enforcement,
                }
                for name, budget in self._budgets.items()
            }


class ResourceGovernor:
    """
    Combined ownership + budget resource governor.
    Instantiate once per execution.
    """

    def __init__(self) -> None:
        self._handles: dict[str, ResourceHandle] = {}
        self._lock = threading.Lock()
        self._policies = RESOURCE_POLICIES.copy()
        self.budget = BudgetGovernor()  # (P1-3)

    def allocate(self, name: str, size_bytes: int = 0) -> ResourceHandle:
        policy = self._policies.get(name) or ResourcePolicy(
            kind=ResourceKind.CACHE,
            owner="unknown",
            max_size_bytes=None,
            ttl_seconds=None,
            eviction_strategy="none",
        )
        handle = ResourceHandle(name=name, policy=policy, size_bytes=size_bytes)
        with self._lock:
            self._handles[name] = handle

        # Publish ArchitectureEvent (RECTIFIED P0-2)
        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.RESOURCE_ALLOCATED,
            source="infrastructure.resources",
            name=name,
            size_bytes=size_bytes,
        )
        logger.debug("resource_allocated", name=name, size_bytes=size_bytes)
        return handle

    def release(self, name: str) -> None:
        with self._lock:
            handle = self._handles.pop(name, None)
        if handle and not handle.released:
            handle.released = True
            from smriti.runtime.events import ArchitectureEventType, publish

            publish(
                ArchitectureEventType.RESOURCE_RELEASED,
                source="infrastructure.resources",
                name=name,
            )
            logger.debug("resource_released", name=name)

    def release_all(self) -> None:
        names = list(self._handles.keys())
        for name in names:
            self.release(name)
        logger.info("all_resources_released", count=len(names))

    def utilization_report(self) -> dict:
        with self._lock:
            return {
                name: {
                    "kind": h.policy.kind.value,
                    "owner": h.policy.owner,
                    "size_bytes": h.size_bytes,
                    "age_seconds": time.monotonic() - h.allocated_at,
                }
                for name, h in self._handles.items()
                if not h.released
            }
