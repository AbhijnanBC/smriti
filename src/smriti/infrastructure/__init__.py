"""
infrastructure/__init__.py — Public API for Phase 11 Part 2.

RECTIFIED: Exports PolicyHierarchy, StateOwnershipGraph, ServiceRegistry,
BudgetGovernor, and extended ProvenanceBuilder.
"""

from smriti.infrastructure.compatibility import CompatibilityMatrix, VersionContract
from smriti.infrastructure.configuration import ConfigurationHierarchy, ConfigurationLevel
from smriti.infrastructure.dependency import BOUNDARY_MATRIX, DependencyMatrix, LayerBoundary
from smriti.infrastructure.ownership import OWNERSHIP_TABLE, OwnershipRegistry
from smriti.infrastructure.policy_hierarchy import PolicyHierarchy, PolicyLevel
from smriti.infrastructure.provenance import ProvenanceBuilder, RuntimeManifest
from smriti.infrastructure.resources import (
    BudgetGovernor,
    ResourceBudget,
    ResourceGovernor,
    ResourceKind,
)
from smriti.infrastructure.service_registry import ServiceEntry, ServiceRegistry
from smriti.infrastructure.state_ownership import OwnershipRelation, StateOwnershipGraph
from smriti.infrastructure.state_taxonomy import (
    BusinessState,
    OperationalState,
    RuntimeStateCategory,
)
from smriti.infrastructure.trust import TrustBoundary, TrustLevel, TrustModel

__all__ = [
    "DependencyMatrix",
    "LayerBoundary",
    "BOUNDARY_MATRIX",
    "TrustBoundary",
    "TrustLevel",
    "TrustModel",
    "BusinessState",
    "RuntimeStateCategory",
    "OperationalState",
    "StateOwnershipGraph",
    "OwnershipRelation",
    "ConfigurationHierarchy",
    "ConfigurationLevel",
    "PolicyHierarchy",
    "PolicyLevel",
    "ResourceGovernor",
    "ResourceKind",
    "BudgetGovernor",
    "ResourceBudget",
    "RuntimeManifest",
    "ProvenanceBuilder",
    "OwnershipRegistry",
    "OWNERSHIP_TABLE",
    "ServiceRegistry",
    "ServiceEntry",
    "CompatibilityMatrix",
    "VersionContract",
]
