"""
infrastructure/__init__.py — Public API for Phase 11 Part 2.

RECTIFIED: Exports PolicyHierarchy, StateOwnershipGraph, ServiceRegistry,
BudgetGovernor, and extended ProvenanceBuilder.
"""

from smriti.infrastructure.dependency    import DependencyMatrix, LayerBoundary, BOUNDARY_MATRIX
from smriti.infrastructure.trust         import TrustBoundary, TrustLevel, TrustModel
from smriti.infrastructure.state_taxonomy import BusinessState, RuntimeStateCategory, OperationalState
from smriti.infrastructure.state_ownership import StateOwnershipGraph, OwnershipRelation
from smriti.infrastructure.configuration import ConfigurationHierarchy, ConfigurationLevel
from smriti.infrastructure.policy_hierarchy import PolicyHierarchy, PolicyLevel
from smriti.infrastructure.resources    import ResourceGovernor, ResourceKind, BudgetGovernor, ResourceBudget
from smriti.infrastructure.provenance   import RuntimeManifest, ProvenanceBuilder
from smriti.infrastructure.ownership    import OwnershipRegistry, OWNERSHIP_TABLE
from smriti.infrastructure.service_registry import ServiceRegistry, ServiceEntry
from smriti.infrastructure.compatibility import CompatibilityMatrix, VersionContract

__all__ = [
    "DependencyMatrix", "LayerBoundary", "BOUNDARY_MATRIX",
    "TrustBoundary", "TrustLevel", "TrustModel",
    "BusinessState", "RuntimeStateCategory", "OperationalState",
    "StateOwnershipGraph", "OwnershipRelation",
    "ConfigurationHierarchy", "ConfigurationLevel",
    "PolicyHierarchy", "PolicyLevel",
    "ResourceGovernor", "ResourceKind", "BudgetGovernor", "ResourceBudget",
    "RuntimeManifest", "ProvenanceBuilder",
    "OwnershipRegistry", "OWNERSHIP_TABLE",
    "ServiceRegistry", "ServiceEntry","CompatibilityMatrix",
    "VersionContract",
]