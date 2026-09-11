"""
service_registry.py — ServiceRegistry (§11.18 rectified).

RECTIFIED (P2-1): DependencyGraph alone is not sufficient.
ServiceRegistry adds runtime service discovery:
    register()  — register a named service
    discover()  — find services by capability tag
    replace()   — swap an implementation (for testing / upgrades)
    retire()    — remove a service from active use

This separates "what exists" (DependencyGraph) from
"what is currently active and discoverable" (ServiceRegistry).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ServiceEntry:
    """One registered service."""

    name: str
    instance: Any
    capabilities: set[str]  # e.g. {"health", "query", "export"}
    retired: bool = False
    version: str = "1.0"
    owner: str = ""


class ServiceRegistry:
    """
    RECTIFIED (P2-1): Runtime service registry for dynamic discovery.

    Usage:
        registry = ServiceRegistry()
        registry.register("health_monitor", monitor, capabilities={"health"})
        health_services = registry.discover(capability="health")
        registry.replace("health_monitor", new_monitor)
        registry.retire("old_service")
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceEntry] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        instance: Any,
        capabilities: set[str] | None = None,
        version: str = "1.0",
        owner: str = "",
    ) -> None:
        """Register a service. Raises if name already registered and not retired."""
        with self._lock:
            existing = self._services.get(name)
            if existing and not existing.retired:
                raise ValueError(
                    f"Service '{name}' is already registered. "
                    "Call retire() first or use replace()."
                )
            self._services[name] = ServiceEntry(
                name=name,
                instance=instance,
                capabilities=capabilities or set(),
                version=version,
                owner=owner,
            )

        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.SERVICE_REGISTERED,
            source="infrastructure.service_registry",
            service_name=name,
            version=version,
        )
        logger.debug("service_registered", name=name, capabilities=list(capabilities or []))

    def discover(self, capability: str) -> list[ServiceEntry]:
        """Return all active services with the given capability tag."""
        with self._lock:
            return [
                entry
                for entry in self._services.values()
                if not entry.retired and capability in entry.capabilities
            ]

    def get(self, name: str) -> ServiceEntry | None:
        with self._lock:
            entry = self._services.get(name)
            return entry if entry and not entry.retired else None

    def replace(self, name: str, new_instance: Any, version: str = "1.0") -> None:
        """Replace an existing service's instance (e.g., for upgrades or testing)."""
        with self._lock:
            entry = self._services.get(name)
            if entry is None:
                raise ValueError(f"Service '{name}' not found.")
            entry.instance = new_instance
            entry.version = version
        logger.info("service_replaced", name=name, new_version=version)

    def retire(self, name: str) -> None:
        """Mark a service as retired (no longer discovered)."""
        with self._lock:
            entry = self._services.get(name)
            if entry:
                entry.retired = True
        from smriti.runtime.events import ArchitectureEventType, publish

        publish(
            ArchitectureEventType.SERVICE_RETIRED,
            source="infrastructure.service_registry",
            service_name=name,
        )
        logger.info("service_retired", name=name)

    def all_active(self) -> list[ServiceEntry]:
        with self._lock:
            return [e for e in self._services.values() if not e.retired]

    def snapshot(self) -> dict[str, dict]:
        with self._lock:
            return {
                name: {
                    "capabilities": list(e.capabilities),
                    "version": e.version,
                    "owner": e.owner,
                    "retired": e.retired,
                }
                for name, e in self._services.items()
            }
