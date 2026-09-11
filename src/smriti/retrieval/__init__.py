"""
retrieval/__init__.py — Public API for Phase 6: Semantic Relationship Discovery.

External callers import ONLY from here:

    from smriti.retrieval import discover_relationships, RelationshipSet

All internal modules are hidden from external callers.

Changes from original:
    - ConfidenceCalibrator inserted between evidence generation and resolution
    - ConflictResolver applied before builder
    - ResourceGovernor enforces limits on candidate pairs
    - ReplayEngine writes replay manifest after every successful run
    - validate_all_relationships now receives triples (evidence, type, direction)
    - Phase6StatsCollector.finalize() produces DiscoveryReport (not Phase6Stats)
"""

from __future__ import annotations

import hashlib
import json

import structlog

from smriti.core.config import Config, get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    ConflictResolutionPolicy,
    EmbeddedClaim,
    RelationshipDirection,
    RelationshipSet,
    RelationshipType,
    ResolutionStatus,
)
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import FAISSNotAvailableError, IndexBuildError
from smriti.retrieval.builder import build_relationship, build_relationship_set
from smriti.retrieval.candidate_generator import CandidateGenerator
from smriti.retrieval.classification.calibration import ConfidenceCalibrator
from smriti.retrieval.classification.conflict import ConflictResolver
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator
from smriti.retrieval.classification.relatedness import passes_contradiction_relatedness_gate
from smriti.retrieval.classification.resolver import RelationshipResolver, ResolverPolicy
from smriti.retrieval.classification.specificity import is_refinement
from smriti.retrieval.classification.validator import validate_all_relationships
from smriti.retrieval.faiss_index import FAISSIndex
from smriti.retrieval.governance import ResourceGovernor
from smriti.retrieval.index import EmbeddingIndex
from smriti.retrieval.replay import ReplayEngine
from smriti.retrieval.statistics import Phase6StatsCollector
from smriti.retrieval.validator import validate_candidates

logger = structlog.get_logger(__name__)

PHASE6_VERSION = "1.0"


def _compute_config_hash(config: Config) -> str:
    """Deterministic hash of Phase 6 configuration."""
    relevant = {
        "nli_model": config.get("nli", {}).get("model_name", ""),
        "nli_threshold": config.get("nli", {}).get("nli_threshold", 0.80),
        "sim_threshold": config.get("relationship_discovery", {}).get("sim_threshold", 0.75),
        "top_k": config.get("relationship_discovery", {}).get("top_k", 50),
        "refine_threshold": config.get("relationship_discovery", {}).get("refine_threshold", 0.55),
        "calibration_strategy": config.get("calibration", {}).get("strategy", "identity"),
        "conflict_policy": config.get("relationship_discovery", {}).get(
            "conflict_resolution_policy", "highest_confidence"
        ),
    }
    material = json.dumps(relevant, sort_keys=True)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _serialize_relationship_set(relationship_set: RelationshipSet) -> str:
    """Serialize RelationshipSet to JSON for Phase 7."""
    records = []
    for rel in relationship_set.relationships:
        records.append(
            {
                "relationship_id": rel.relationship_id,
                "claim_id_a": rel.claim_id_a,
                "claim_id_b": rel.claim_id_b,
                "relationship_type": rel.relationship_type.value,
                "direction": rel.direction.value,
                "schema_version": rel.version_info.schema_version,
                "migration_version": rel.version_info.migration_version,
                "compatibility_version": rel.version_info.compatibility_version,
                "lifecycle_stage": rel.lifecycle_stage.value,
                "evidence": {
                    "cosine_similarity": rel.evidence.cosine_similarity,
                    # A -> B direction (claim_a as premise, claim_b as hypothesis)
                    "entailment_score": rel.evidence.nli_scores.entailment_score,
                    "neutral_score": rel.evidence.nli_scores.neutral_score,
                    "contradiction_score": rel.evidence.nli_scores.contradiction_score,
                    "predicted_label": rel.evidence.nli_scores.predicted_label,
                    "raw_confidence": rel.evidence.nli_scores.raw_confidence,
                    "calibrated_confidence": rel.evidence.calibrated_confidence,
                    # B -> A direction (bidirectional-NLI rewrite); None only for
                    # legacy single-direction evidence.
                    "entailment_score_b_to_a": (
                        rel.evidence.nli_scores_b_to_a.entailment_score
                        if rel.evidence.nli_scores_b_to_a
                        else None
                    ),
                    "neutral_score_b_to_a": (
                        rel.evidence.nli_scores_b_to_a.neutral_score
                        if rel.evidence.nli_scores_b_to_a
                        else None
                    ),
                    "contradiction_score_b_to_a": (
                        rel.evidence.nli_scores_b_to_a.contradiction_score
                        if rel.evidence.nli_scores_b_to_a
                        else None
                    ),
                    "predicted_label_b_to_a": (
                        rel.evidence.nli_scores_b_to_a.predicted_label
                        if rel.evidence.nli_scores_b_to_a
                        else None
                    ),
                    "model_name": rel.evidence.inference_metadata.model_name,
                    "model_version": rel.evidence.inference_metadata.model_version,
                    "latency_ms": rel.evidence.inference_metadata.latency_ms,
                },
                "quality": {
                    "cosine_above_threshold": rel.quality.cosine_above_threshold,
                    "nli_above_threshold": rel.quality.nli_above_threshold,
                    "evidence_consistent": rel.quality.evidence_consistent,
                    "calibration_applied": rel.quality.calibration_applied,
                },
                "provenance": {
                    "retrieval_backend": rel.provenance.retrieval_backend,
                    "retrieval_version": rel.provenance.retrieval_version,
                    "index_version": rel.provenance.index_version,
                    "classifier_model": rel.provenance.classifier_model,
                    "classifier_version": rel.provenance.classifier_version,
                    "resolver_version": rel.provenance.resolver_version,
                    "calibrator_version": rel.provenance.calibrator_version,
                    "cosine_similarity": rel.provenance.cosine_similarity,
                    "candidate_rank": rel.provenance.candidate_rank,
                    "raw_nli_confidence": rel.provenance.raw_nli_confidence,
                    "calibrated_confidence": rel.provenance.calibrated_confidence,
                    "config_hash": rel.provenance.config_hash,
                    "run_id": rel.provenance.run_id,
                    "replay_id": rel.provenance.replay_id,
                },
            }
        )
    return json.dumps(records, indent=2, ensure_ascii=False)


# Orchestrates the full Phase 6 pipeline (candidate generation, NLI,
# calibration, resolution, validation) as one linear, order-sensitive
# sequence; splitting it up would scatter that sequence across helper
# functions with no natural seams, trading readability for a lower
# mccabe complexity score.
def discover_relationships(  # noqa: C901
    embedded_claims: list[EmbeddedClaim],
    claims_map: dict[str, Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    index: EmbeddingIndex | None = None,
    nli_generator: NLIEvidenceGenerator | None = None,
    calibrator: ConfidenceCalibrator | None = None,
    resolver_policy: ResolverPolicy | None = None,
    conflict_policy: ConflictResolutionPolicy | None = None,
) -> RelationshipSet:
    """
    Execute the complete Phase 6 semantic relationship discovery pipeline.

    This is Phase 6's sole public function.

    Args:
        embedded_claims:   List of EmbeddedClaim from Phase 5.
        claims_map:        {claim_id: Claim} from Phase 4.
        run_id:            Current pipeline run identifier.
        manifest_manager:  For writing phase manifest.
        state_manager:     For updating pipeline state.
        index:             Optional pre-built index (for testing).
        nli_generator:     Optional pre-constructed NLI generator (for testing).
        calibrator:        Optional pre-constructed calibrator (for testing).
        resolver_policy:   Optional policy override (for testing).
        conflict_policy:   Optional conflict resolution policy override.

    Returns:
        RelationshipSet containing all discovered relationships with
        full provenance, calibration, and lifecycle tracing.
    """
    config = get_config()
    rd_cfg = config.get("relationship_discovery", {})
    nli_cfg = config.get("nli", {})

    sim_threshold: float = rd_cfg.get("sim_threshold", 0.75)
    nli_threshold: float = nli_cfg.get("nli_threshold", 0.80)
    min_confidence: float = rd_cfg.get("min_confidence", 0.50)
    skip_unknown: bool = rd_cfg.get("skip_unknown_relationships", True)
    # RECTIFIED (external review, P0-7-class defect found while re-running
    # SMRITI-Reference): this key was documented in config/default.yaml
    # but no code path ever read it before now -- NEUTRAL relationships
    # were persisted unconditionally regardless of its value.
    skip_neutral: bool = rd_cfg.get("skip_neutral_relationships", True)
    config_hash = _compute_config_hash(config)

    # Resolve conflict policy
    if conflict_policy is None:
        policy_str = rd_cfg.get("conflict_resolution_policy", "highest_confidence")
        conflict_policy = ConflictResolutionPolicy(policy_str)

    logger.info(
        "phase 6 starting",
        run_id=run_id,
        embedded_claims=len(embedded_claims),
        sim_threshold=sim_threshold,
        nli_threshold=nli_threshold,
        conflict_policy=conflict_policy.value,
    )

    start_time = manifest_manager.start_phase(phase=6)
    stats = Phase6StatsCollector()
    stats.record_embedded_claims(len(embedded_claims))

    # Resource governance
    governor = ResourceGovernor()

    # Build embeddings lookup map
    embeddings_map: dict[str, EmbeddedClaim] = {ec.claim_id: ec for ec in embedded_claims}

    # ── Stage 1: Build vector index ──────────────────────────────────────────
    if index is None:
        if not embedded_claims:
            logger.warning("no embedded claims — returning empty RelationshipSet")
            relationship_set = RelationshipSet(
                relationships=[],
                total_candidates=0,
                total_validated=0,
                total_rejected=0,
                rejected_reasons={},
                run_id=run_id,
            )
            _finalize_phase(
                relationship_set,
                stats,
                run_id,
                start_time,
                manifest_manager,
                state_manager,
                config_hash,
                config,
                phase5_path="",
                phase4_path="",
            )
            return relationship_set

        dimension = embedded_claims[0].dimension
        index = FAISSIndex(dimension=dimension)
        claim_ids = [ec.claim_id for ec in embedded_claims]
        vectors = [list(ec.values) for ec in embedded_claims]
        try:
            index.add(claim_ids, vectors)
        except (IndexBuildError, FAISSNotAvailableError) as e:
            logger.error("index build failed", error=str(e))
            raise
        logger.info("vector index built", size=index.size, dimension=dimension)

    # ── Stage 2: Generate candidate pairs ────────────────────────────────────
    stats.record_candidate_start()

    with Timer("phase6_candidate_generation"):
        generator = CandidateGenerator()
        raw_candidates = generator.generate(embedded_claims, index)

    # Resource governance: enforce pair limit
    governor.check_timeout()
    raw_candidates = governor.enforce_pair_limit(raw_candidates)
    stats.record_truncation(governor.evaluation_truncated)

    # ── Stage 3: Validate candidates ─────────────────────────────────────────
    with Timer("phase6_candidate_validation"):
        valid_candidates, rejection_counts = validate_candidates(
            candidates=raw_candidates,
            claims_map=claims_map,
            embeddings_map=embeddings_map,
            sim_threshold=sim_threshold,
        )

    stats.record_candidate_end(
        total=len(raw_candidates),
        validated=len(valid_candidates),
        rejected=sum(rejection_counts.values()),
    )
    all_rejection_reasons = dict(rejection_counts)

    # ── Stage 4: NLI evidence generation ─────────────────────────────────────
    stats.record_nli_start()
    governor.check_timeout()

    if nli_generator is None:
        nli_generator = NLIEvidenceGenerator()

    with Timer("phase6_nli_inference"):
        all_evidence = nli_generator.generate_batch(
            pairs=valid_candidates,
            claims_map=claims_map,
        )

    stats.record_nli_end(calls=len(all_evidence))
    stats.record_nli_run_stats(getattr(nli_generator, "last_run_stats", {}))

    # ── Stage 4b: Confidence calibration ─────────────────────────────────────
    if calibrator is None:
        model_name = nli_cfg.get("model_name", "cross-encoder/nli-deberta-v3-small")
        calibrator = ConfidenceCalibrator(model_name=model_name)

    with Timer("phase6_calibration"):
        all_evidence = calibrator.calibrate_batch(all_evidence)

    # ── Stage 5: Resolve relationships ───────────────────────────────────────
    # RECTIFIED (external review, P0-3 "RelationshipDecision not integrated
    # into production"): production previously called the legacy
    # resolve() -> (RelationshipType, RelationshipDirection) tuple API
    # directly, leaving resolve_as_decision() -- the conceptually correct
    # API that makes relation_type Optional and None exactly when
    # ResolutionStatus.ABSTAINED -- defined but never actually invoked by
    # any production code path. Phase 6 now computes the real
    # RelationshipDecision for every candidate first; RelationshipType.UNKNOWN
    # is still threaded through resolved_triples below as a deliberate,
    # documented compatibility sentinel for the relatedness/specificity
    # gates and validate_all_relationships (which reason over the enum,
    # not the decision object) -- but it is now DERIVED from the decision
    # (decision.relation_type or RelationshipType.UNKNOWN), not the only
    # representation ever computed, and the real ResolutionStatus is
    # tracked alongside it so abstention rate can be reported from actual
    # resolver decisions rather than reverse-inferred from the sentinel.
    policy = resolver_policy or ResolverPolicy.from_config()
    resolver = RelationshipResolver(policy=policy)
    resolved_triples = []
    abstained_count = 0

    for evidence in all_evidence:
        decision = resolver.resolve_as_decision(evidence)
        rel_type = decision.relation_type or RelationshipType.UNKNOWN
        direction = decision.direction
        if decision.status == ResolutionStatus.ABSTAINED:
            abstained_count += 1
        resolved_triples.append((evidence, rel_type, direction))

    if all_evidence:
        logger.info(
            "resolver abstention rate (ResolutionStatus.ABSTAINED, pre-gating)",
            abstained=abstained_count,
            total=len(all_evidence),
            rate=f"{abstained_count / len(all_evidence):.1%}",
        )

    # ── Stage 5b: Relatedness gate on CONTRADICTS (P0-6) ─────────────────────
    # A CONTRADICTS verdict additionally requires the two claims to share
    # some detectable topical overlap — you cannot contradict a claim you
    # are not even talking about. This does not touch SUPPORTS/REFINES/
    # NEUTRAL, since over-gating there would cost recall without addressing
    # the measured failure mode (spurious cross-domain CONTRADICTS).
    rd_cfg = config.get("relationship_discovery", {})
    min_relatedness = rd_cfg.get("min_contradiction_relatedness", 0.03)
    downgraded_count = 0
    gated_triples = []
    for evidence, rel_type, direction in resolved_triples:
        if rel_type == RelationshipType.CONTRADICTS:
            claim_a = claims_map.get(evidence.pair.claim_id_a)
            claim_b = claims_map.get(evidence.pair.claim_id_b)
            text_a = claim_a.text if claim_a else ""
            text_b = claim_b.text if claim_b else ""
            if not passes_contradiction_relatedness_gate(text_a, text_b, min_relatedness):
                rel_type = RelationshipType.UNKNOWN
                direction = RelationshipDirection.SYMMETRIC
                downgraded_count += 1
        gated_triples.append((evidence, rel_type, direction))
    resolved_triples = gated_triples
    if downgraded_count:
        logger.info(
            "relatedness gate downgraded low-overlap CONTRADICTS verdicts",
            downgraded=downgraded_count,
            min_relatedness=min_relatedness,
        )

    # ── Stage 5c: Specificity gate reclassifying SUPPORTS -> REFINES ─────────
    # RECTIFIED (external review, bidirectional-NLI rewrite): one-way
    # entailment alone (SUPPORTS's resolver rule) does not distinguish
    # "independent confirmation of the same claim" from "elaboration that
    # adds detail the other claim lacks" -- the latter should be REFINES,
    # not SUPPORTS. This mirrors the relatedness gate's own pattern (a
    # separate, model-free, text-aware stage applied here rather than
    # inside the resolver, which stays a pure function of numeric scores).
    specificity_margin = rd_cfg.get("refine_specificity_margin", 3.0)
    reclassified_count = 0
    specificity_gated_triples = []
    for evidence, rel_type, direction in resolved_triples:
        if rel_type == RelationshipType.SUPPORTS:
            claim_a = claims_map.get(evidence.pair.claim_id_a)
            claim_b = claims_map.get(evidence.pair.claim_id_b)
            text_a = claim_a.text if claim_a else ""
            text_b = claim_b.text if claim_b else ""
            if direction == RelationshipDirection.A_TO_B:
                entailing_text, entailed_text = text_a, text_b
            else:
                entailing_text, entailed_text = text_b, text_a
            if is_refinement(entailing_text, entailed_text, specificity_margin):
                rel_type = RelationshipType.REFINES
                reclassified_count += 1
        specificity_gated_triples.append((evidence, rel_type, direction))
    resolved_triples = specificity_gated_triples
    if reclassified_count:
        logger.info(
            "specificity gate reclassified SUPPORTS as REFINES",
            reclassified=reclassified_count,
            specificity_margin=specificity_margin,
        )

    # ── Stage 6: Validate resolved relationships ──────────────────────────────
    governor.check_timeout()

    valid_resolved, rel_rejection_counts = validate_all_relationships(
        evidence_with_types=resolved_triples,
        min_confidence=min_confidence,
        nli_threshold=nli_threshold,
        skip_unknown=skip_unknown,
        skip_neutral=skip_neutral,
    )
    for k, v in rel_rejection_counts.items():
        all_rejection_reasons[k] = all_rejection_reasons.get(k, 0) + v

    # ── Stage 6b: Conflict resolution ────────────────────────────────────────
    # Build preliminary relationships for conflict resolution
    preliminary_relationships = []
    for evidence, rel_type, direction in valid_resolved:
        rel = build_relationship(
            evidence=evidence,
            relationship_type=rel_type,
            direction=direction,
            nli_threshold=nli_threshold,
            config_hash=config_hash,
            run_id=run_id,
        )
        preliminary_relationships.append(rel)

    conflict_resolver = ConflictResolver(policy=conflict_policy)
    relationships = conflict_resolver.resolve_conflicts(preliminary_relationships)

    conflicts_resolved = len(preliminary_relationships) - len(relationships)
    for _ in range(conflicts_resolved):
        stats.record_conflict_resolved()

    # ── Stage 7: Record statistics ────────────────────────────────────────────
    for rel in relationships:
        calibration_applied = rel.quality.calibration_applied
        stats.record_relationship(
            rel.relationship_type,
            rel.evidence.calibrated_confidence,
            calibration_applied,
        )

    rejected_count = len(all_evidence) - len(valid_resolved)
    for _ in range(rejected_count):
        stats.record_rejected_relationship("validation_stage")

    # ── Stage 8: Build RelationshipSet ────────────────────────────────────────
    relationship_set = build_relationship_set(
        relationships=relationships,
        total_candidates=len(raw_candidates),
        total_validated=len(valid_candidates),
        total_rejected=sum(all_rejection_reasons.values()),
        rejected_reasons=all_rejection_reasons,
        run_id=run_id,
    )

    _finalize_phase(
        relationship_set,
        stats,
        run_id,
        start_time,
        manifest_manager,
        state_manager,
        config_hash,
        config,
        phase5_path="",
        phase4_path="",
    )

    logger.info(
        "phase 6 complete",
        total_relationships=relationship_set.total_relationships,
        contradictions=len(relationship_set.contradictions),
        supports=len(relationship_set.supports),
        refinements=len(relationship_set.refinements),
        conflicts_resolved=conflicts_resolved,
    )

    return relationship_set


def _finalize_phase(
    relationship_set: RelationshipSet,
    stats: Phase6StatsCollector,
    run_id: str,
    start_time: float,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    config_hash: str,
    config: Config,
    phase5_path: str,
    phase4_path: str,
) -> None:
    """Write artifacts, replay manifest, phase manifest, and update pipeline state."""
    phase_dir = (
        manifest_manager.run_dir / "phase6"
    )  # RECTIFIED: respect manifest_manager.artifacts_dir, not the global default
    phase_dir.mkdir(parents=True, exist_ok=True)

    # Write dataset artifact for Phase 7
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(_serialize_relationship_set(relationship_set), encoding="utf-8")
    relationship_set.dataset_path = dataset_path
    logger.info("dataset written", path=str(dataset_path))

    final_report = stats.finalize()

    # Write replay manifest
    replay_engine = ReplayEngine()
    replay_manifest = replay_engine.build_replay_manifest(
        run_id=run_id,
        config=config,
        config_hash=config_hash,
        total_embedded=final_report.total_embedded_claims,
        total_relationships=final_report.relationships_produced,
        phase5_path=phase5_path,
        phase4_path=phase4_path,
    )
    replay_path = replay_engine.write_replay_manifest(replay_manifest, run_id)
    relationship_set.replay_manifest_path = replay_path

    # Write phase manifest
    manifest_path = manifest_manager.end_phase(
        phase=6,
        start_time=start_time,
        inputs={
            "embedded_claims": final_report.total_embedded_claims,
            "config_hash": config_hash,
        },
        outputs={
            "total_candidates": final_report.total_candidate_pairs,
            "validated": final_report.validated_candidates,
            "relationships": final_report.relationships_produced,
            "contradictions": final_report.contradictions,
            "supports": final_report.supports,
            "refinements": final_report.refinements,
            "calibration_applied": final_report.calibration_applied_count,
            "conflicts_resolved": final_report.conflicts_resolved,
            "confidence_histogram": final_report.confidence_histogram,
            "dataset_path": str(dataset_path),
            "replay_manifest_path": str(replay_path),
        },
        status="success",
    )
    relationship_set.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=6)
