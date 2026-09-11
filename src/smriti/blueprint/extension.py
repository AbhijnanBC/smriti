"""
extension.py — Extension Architecture (§11.48).

Defines how SMRITI grows without violating architectural boundaries.
Every extension must declare an entry point, contracts, validation,
lifecycle, isolation, and compatibility.

Supported extension types:
    - Document parsers (new file format support)
    - Graph algorithms (new traversal or partitioning strategies)
    - Interaction workspaces (new dashboard views)
    - Reliability models (new scoring signal)
    - Policy engines (new interaction policy)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class ExtensionType(str, Enum):
    DOCUMENT_PARSER = "document_parser"
    GRAPH_ALGORITHM = "graph_algorithm"
    INTERACTION_WORKSPACE = "interaction_workspace"
    RELIABILITY_MODEL = "reliability_model"
    POLICY_ENGINE = "policy_engine"


@dataclass
class ExtensionPoint:
    """
    Contract for a single SMRITI extension.

    An extension is a unit of optional functionality that:
        1. Declares its entry point (callable or class)
        2. Specifies its contracts (input/output types)
        3. Can be independently validated
        4. Has a defined lifecycle
        5. Is isolated from other extensions
        6. Declares its compatibility requirements
    """

    name: str
    extension_type: ExtensionType
    entry_point: str  # module.path:ClassName
    input_contract: str  # description of required input
    output_contract: str  # description of produced output
    lifecycle: str  # "request" | "session" | "runtime"
    compatibility: str  # minimum SMRITI version
    is_optional: bool = True
    validation_fn: Callable | None = None

    def validate(self) -> bool:
        """Run the optional validation function."""
        if self.validation_fn is None:
            return True
        try:
            return bool(self.validation_fn())
        except Exception:
            return False


class ExtensionRegistry:
    """
    Registry for all SMRITI extensions.

    Extensions are registered before the runtime starts.
    New extensions never bypass architectural boundaries:
        - New parsers integrate at Phase 2 (parsing layer) only
        - New workspaces integrate at Phase 10 (dashboard layer) only
        - New reliability models integrate at Phase 8 (scoring layer) only
    """

    def __init__(self) -> None:
        self._extensions: dict[str, ExtensionPoint] = {}

    def register(self, ext: ExtensionPoint) -> None:
        if ext.name in self._extensions:
            raise ValueError(f"Extension '{ext.name}' already registered.")
        self._extensions[ext.name] = ext

    def get(self, name: str) -> ExtensionPoint | None:
        return self._extensions.get(name)

    def by_type(self, ext_type: ExtensionType) -> list[ExtensionPoint]:
        return [e for e in self._extensions.values() if e.extension_type == ext_type]

    def validate_all(self) -> dict[str, bool]:
        return {name: ext.validate() for name, ext in self._extensions.items()}
