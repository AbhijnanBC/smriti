"""
evolution.py — Evolution Strategy (§11.36) & Interface Governance (§11.37).

Defines how the SMRITI architecture evolves predictably:
    - Backward compatibility policy
    - Deprecation lifecycle
    - Breaking change policy
    - Interface stability levels

Decorators bind stability guarantees directly to runtime objects,
complementing the declarative InterfaceContract registry.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, TypeVar, Callable, Any

# Type variable for decorator return
F = TypeVar("F", bound=Callable[..., Any])


class CompatibilityPolicy(str, Enum):
    BACKWARD_COMPATIBLE = "backward_compatible"  # Old clients still work
    DEPRECATION_PERIOD  = "deprecation_period"   # Old API works but logs warnings
    BREAKING_CHANGE     = "breaking_change"       # Requires migration (new ADR required)


class StabilityLevel(str, Enum):
    STABLE      = "stable"       # No breaking changes without ADR
    EXPERIMENTAL = "experimental" # May change without notice
    INTERNAL    = "internal"     # Not a public interface — not governed
    DEPRECATED  = "deprecated"   # Scheduled for removal; replacement provided


# ── Decorators for runtime stability metadata ────────────────────────────────

def stable(version: str) -> Callable[[F], F]:
    """
    Decorator marking an interface as STABLE.
    Breaking changes require an ADR and a deprecation period.
    """
    def decorator(cls_or_func: F) -> F:
        cls_or_func.__stability__ = StabilityLevel.STABLE
        cls_or_func.__stability_version__ = version
        return cls_or_func
    return decorator


def experimental(version: str) -> Callable[[F], F]:
    """
    Decorator marking an interface as EXPERIMENTAL.
    May change without notice; early adopters use at their own risk.
    """
    def decorator(cls_or_func: F) -> F:
        cls_or_func.__stability__ = StabilityLevel.EXPERIMENTAL
        cls_or_func.__stability_version__ = version
        return cls_or_func
    return decorator


def internal() -> Callable[[F], F]:
    """
    Decorator marking an interface as INTERNAL.
    Not for public use; may change or disappear at any time.
    """
    def decorator(cls_or_func: F) -> F:
        cls_or_func.__stability__ = StabilityLevel.INTERNAL
        return cls_or_func
    return decorator


def deprecated(removal_in: str, replacement: str) -> Callable[[F], F]:
    """
    Decorator marking an interface as DEPRECATED.
    The interface will be removed in the specified version; use `replacement` instead.
    """
    def decorator(cls_or_func: F) -> F:
        cls_or_func.__stability__ = StabilityLevel.DEPRECATED
        cls_or_func.__removal_in__ = removal_in
        cls_or_func.__replacement__ = replacement
        return cls_or_func
    return decorator


# ── Governance data structures ──────────────────────────────────────────────

@dataclass
class DeprecationRecord:
    """Records the deprecation lifecycle of an interface or module."""
    target:          str
    deprecated_in:   str         # Version or phase
    removal_in:      str         # Version or phase
    replacement:     str
    reason:          str
    deprecated_at:   float = field(default_factory=time.time)


@dataclass(frozen=True)
class InterfaceContract:
    """Formal contract for a single public interface."""
    name:            str
    module:          str
    owner:           str
    stability:       StabilityLevel
    version:         str
    compatibility:   CompatibilityPolicy
    deprecations:    tuple[str, ...]  # List of deprecated features in this interface


class EvolutionStrategy:
    """
    Governs how SMRITI evolves while preserving architectural integrity.

    Key policies:
        1. Breaking changes require an ADR before implementation
        2. Deprecation period is at least one minor version
        3. Internal interfaces may change without notice
        4. Stable interfaces need two-phase migration (deprecate, then remove)
    """

    BREAKING_CHANGE_POLICY = (
        "Breaking changes to STABLE interfaces require: "
        "(1) an accepted ADR explaining the rationale, "
        "(2) a deprecation release with backward compatibility, "
        "(3) a migration guide in /docs/migration/, "
        "(4) removal only after the deprecation period."
    )

    INTERFACE_CONTRACTS: Dict[str, InterfaceContract] = {
        "KnowledgeAccessService": InterfaceContract(
            name="KnowledgeAccessService",
            module="smriti.api",
            owner="api",
            stability=StabilityLevel.STABLE,
            version="1.0",
            compatibility=CompatibilityPolicy.BACKWARD_COMPATIBLE,
            deprecations=(),
        ),
        "PipelineRunner": InterfaceContract(
            name="PipelineRunner",
            module="smriti.pipeline.runner",
            owner="pipeline",
            stability=StabilityLevel.STABLE,
            version="1.0",
            compatibility=CompatibilityPolicy.BACKWARD_COMPATIBLE,
            deprecations=(),
        ),
        "RuntimeCoordinator": InterfaceContract(
            name="RuntimeCoordinator",
            module="smriti.runtime.coordinator",
            owner="runtime",
            stability=StabilityLevel.STABLE,
            version="1.0",
            compatibility=CompatibilityPolicy.BACKWARD_COMPATIBLE,
            deprecations=(),
        ),
        "TelemetryCollector": InterfaceContract(
            name="TelemetryCollector",
            module="smriti.observability.telemetry",
            owner="observability",
            stability=StabilityLevel.EXPERIMENTAL,
            version="0.1",
            compatibility=CompatibilityPolicy.DEPRECATION_PERIOD,
            deprecations=(),
        ),
    }


__all__ = [
    "CompatibilityPolicy",
    "StabilityLevel",
    "DeprecationRecord",
    "InterfaceContract",
    "EvolutionStrategy",
    "stable",
    "experimental",
    "internal",
    "deprecated",
]