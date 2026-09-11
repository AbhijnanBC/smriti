"""
blueprint/__init__.py — Public API for Phase 11 Part 5.

The blueprint is not a coding guide. It is the architectural translation
layer between design and implementation.
"""

from smriti.blueprint.contracts import ContractRegistry, InterfaceDescriptor
from smriti.blueprint.extension import ExtensionPoint, ExtensionRegistry
from smriti.blueprint.module_spec import ModuleRegistry, ModuleSpecification
from smriti.blueprint.readiness import ReadinessAssessor, ReadinessLevel
from smriti.blueprint.traceability import TraceabilityLink, TraceabilityMatrix

__all__ = [
    "ModuleSpecification",
    "ModuleRegistry",
    "ContractRegistry",
    "InterfaceDescriptor",
    "ExtensionPoint",
    "ExtensionRegistry",
    "TraceabilityMatrix",
    "TraceabilityLink",
    "ReadinessLevel",
    "ReadinessAssessor",
]
