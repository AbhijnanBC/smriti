"""
provenance.py — Operational Provenance (§11.15 rectified).

RECTIFIED (P1-5): RuntimeManifest now includes architecture version fields:
    architecture_version      — Phase 11 architecture version
    adr_set_version           — SHA256 of accepted ADR IDs
    compliance_rule_version   — ComplianceEngine rule set version
    invariant_version         — SystemInvariant catalog version

Without these, two runs with identical code but different architecture
decisions (new ADR accepted, new compliance rule) cannot be distinguished.

RECTIFIED (P0-2): Manifest writing now publishes a ManifestWritten event.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _package_versions() -> Dict[str, str]:
    packages = [
        "structlog", "pyyaml", "networkx", "sentence_transformers",
        "spacy", "numpy", "faiss", "streamlit",
    ]
    versions: Dict[str, str] = {"python": sys.version.split()[0]}
    for pkg in packages:
        try:
            import importlib.metadata
            versions[pkg] = importlib.metadata.version(pkg)
        except Exception:
            versions[pkg] = "unknown"
    return versions


@dataclass
class RuntimeManifest:
    """
    Immutable record of a single SMRITI execution.

    RECTIFIED (P1-5): Added architecture versioning fields.
    Two executions with identical manifests must produce identical outputs.
    """
    run_id:                    str
    configuration_version:     str
    policy_version:            str
    schema_version:            str
    knowledge_version:         str
    git_commit:                str
    dependency_versions:       Dict[str, str]
    runtime_timestamp:         str     # ISO 8601
    pipeline_phases:           tuple = field(default_factory=tuple)

    # RECTIFIED (P1-5): Architecture version fields
    architecture_version:      str = "11.0"
    adr_set_version:           str = "unknown"     # SHA256 of accepted ADR IDs
    compliance_rule_version:   str = "unknown"     # Compliance engine rule set version
    invariant_version:         str = "unknown"     # SystemInvariant catalog version

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def write_artifact(self, artifacts_dir: Path) -> Path:
        manifest_dir = artifacts_dir / f"run_{self.run_id}" / "phase11"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        path = manifest_dir / "runtime_manifest.json"
        path.write_text(self.to_json(), encoding="utf-8")
        logger.info("runtime_manifest_written", path=str(path))

        # Publish ArchitectureEvent (RECTIFIED P0-2)
        from smriti.runtime.events import publish, ArchitectureEventType
        publish(
            ArchitectureEventType.MANIFEST_WRITTEN,
            source="infrastructure.provenance",
            run_id=self.run_id,
            path=str(path),
        )
        return path


class ProvenanceBuilder:
    """
    Builds RuntimeManifest by collecting provenance from all subsystems.

    RECTIFIED (P1-5): Builder now accepts architecture version fields.
    """

    def __init__(self, run_id: str) -> None:
        self._run_id       = run_id
        self._cfg_ver      = "unknown"
        self._policy       = "unknown"
        self._schema       = "unknown"
        self._knowledge    = "unknown"
        self._arch_ver     = "11.0"
        self._adr_version  = "unknown"
        self._cr_version   = "unknown"
        self._inv_version  = "unknown"

    def set_config_version(self, v: str) -> "ProvenanceBuilder":
        self._cfg_ver = v; return self

    def set_policy_version(self, v: str) -> "ProvenanceBuilder":
        self._policy = v; return self

    def set_schema_version(self, v: str) -> "ProvenanceBuilder":
        self._schema = v; return self

    def set_knowledge_version(self, v: str) -> "ProvenanceBuilder":
        self._knowledge = v; return self

    def set_architecture_version(self, v: str) -> "ProvenanceBuilder":
        """RECTIFIED (P1-5): Set the architecture version."""
        self._arch_ver = v; return self

    def set_adr_set_version(self, v: str) -> "ProvenanceBuilder":
        """RECTIFIED (P1-5): Set the ADR set version (hash of accepted ADR IDs)."""
        self._adr_version = v; return self

    def set_compliance_rule_version(self, v: str) -> "ProvenanceBuilder":
        """RECTIFIED (P1-5): Set the compliance rule set version."""
        self._cr_version = v; return self

    def set_invariant_version(self, v: str) -> "ProvenanceBuilder":
        """RECTIFIED (P1-5): Set the invariant catalog version."""
        self._inv_version = v; return self

    def build(self) -> RuntimeManifest:
        import datetime
        return RuntimeManifest(
            run_id=self._run_id,
            configuration_version=self._cfg_ver,
            policy_version=self._policy,
            schema_version=self._schema,
            knowledge_version=self._knowledge,
            git_commit=_git_commit(),
            dependency_versions=_package_versions(),
            runtime_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            architecture_version=self._arch_ver,
            adr_set_version=self._adr_version,
            compliance_rule_version=self._cr_version,
            invariant_version=self._inv_version,
        )