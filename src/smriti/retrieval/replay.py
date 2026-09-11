"""
replay.py — Deterministic replay of Phase 6 discovery runs.

Given a run_id, the ReplayEngine can reconstruct exactly the same
RelationshipSet that was produced in the original run, provided:
    - The same EmbeddedClaims are available
    - The same NLI model is available
    - The replay manifest is intact

A replay manifest is written after every successful Phase 6 run.
It records all parameters needed to exactly reproduce the run.

Rules:
    ✅ Replay is bit-identical to the original (same config, same model)
    ✅ Replay manifest written atomically after every successful run
    ✅ Replays are labeled with replay_id in provenance
    ❌ Replay never modifies existing artifacts
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import structlog

from smriti.core.paths import ARTIFACTS_DIR

logger = structlog.get_logger(__name__)


@dataclass
class ReplayManifest:
    """
    Everything needed to replay a Phase 6 run identically.
    Written to artifacts/run_{id}/phase6/replay_manifest.json.
    """

    run_id: str
    schema_version: str
    nli_model: str
    nli_threshold: float
    sim_threshold: float
    top_k: int
    min_confidence: float
    refine_threshold: float
    high_sim_threshold: float
    neutrality_threshold: float
    contradiction_margin: float
    entailment_margin: float
    calibration_strategy: str
    calibration_temperature: float
    conflict_resolution_policy: str
    deduplication_policy: str
    skip_unknown_relationships: bool
    config_hash: str
    total_embedded_claims: int
    total_relationships: int
    phase5_dataset_path: str
    phase4_dataset_path: str
    # RECTIFIED (external review, P0-7-class defect): skip_neutral_relationships
    # was documented in config but never actually consumed anywhere until
    # this fix. Appended at the end with a default so replay manifests
    # written before this fix (which implicitly always retained NEUTRAL,
    # i.e. behaved as skip_neutral_relationships=False) still deserialize.
    skip_neutral_relationships: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, text: str) -> ReplayManifest:
        data = json.loads(text)
        return cls(**data)


class ReplayEngine:
    """
    Writes and reads replay manifests for deterministic replay.
    """

    def write_replay_manifest(
        self,
        manifest: ReplayManifest,
        run_id: str,
    ) -> Path:
        """Write the replay manifest after a successful run."""
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase6"
        phase_dir.mkdir(parents=True, exist_ok=True)
        replay_path = phase_dir / "replay_manifest.json"
        replay_path.write_text(manifest.to_json(), encoding="utf-8")
        logger.info(
            "replay manifest written",
            path=str(replay_path),
            run_id=run_id,
        )
        return replay_path

    def load_replay_manifest(self, run_id: str) -> ReplayManifest:
        """Load the replay manifest for a given run_id."""
        from smriti.exceptions import ReplayError

        replay_path = ARTIFACTS_DIR / f"run_{run_id}" / "phase6" / "replay_manifest.json"
        if not replay_path.exists():
            raise ReplayError(f"Replay manifest not found for run_id={run_id}: {replay_path}")
        return ReplayManifest.from_json(replay_path.read_text(encoding="utf-8"))

    def build_replay_manifest(
        self,
        run_id: str,
        config: dict,
        config_hash: str,
        total_embedded: int,
        total_relationships: int,
        phase5_path: str,
        phase4_path: str,
    ) -> ReplayManifest:
        """Build a ReplayManifest from the current run's parameters."""
        nli_cfg = config.get("nli", {})
        rd_cfg = config.get("relationship_discovery", {})
        policy_cfg = config.get("resolver_policy", {})
        calib_cfg = config.get("calibration", {}).get(nli_cfg.get("model_name", ""), {})

        return ReplayManifest(
            run_id=run_id,
            schema_version="7.0",  # kept in sync with builder.CURRENT_SCHEMA_VERSION
            nli_model=nli_cfg.get("model_name", "cross-encoder/nli-deberta-v3-small"),
            nli_threshold=nli_cfg.get("nli_threshold", 0.80),
            sim_threshold=rd_cfg.get("sim_threshold", 0.75),
            top_k=rd_cfg.get("top_k", 50),
            min_confidence=rd_cfg.get("min_confidence", 0.50),
            refine_threshold=rd_cfg.get("refine_threshold", 0.55),
            high_sim_threshold=rd_cfg.get("high_sim_threshold", 0.88),
            neutrality_threshold=rd_cfg.get("neutrality_threshold", 0.60),
            contradiction_margin=policy_cfg.get("contradiction_margin", 0.0),
            entailment_margin=policy_cfg.get("entailment_margin", 0.0),
            calibration_strategy=calib_cfg.get("strategy", "identity"),
            calibration_temperature=calib_cfg.get("temperature", 1.0),
            conflict_resolution_policy=rd_cfg.get(
                "conflict_resolution_policy", "highest_confidence"
            ),
            deduplication_policy=rd_cfg.get("deduplication_policy", "keep_highest_confidence"),
            skip_unknown_relationships=rd_cfg.get("skip_unknown_relationships", True),
            skip_neutral_relationships=rd_cfg.get("skip_neutral_relationships", True),
            config_hash=config_hash,
            total_embedded_claims=total_embedded,
            total_relationships=total_relationships,
            phase5_dataset_path=phase5_path,
            phase4_dataset_path=phase4_path,
        )
