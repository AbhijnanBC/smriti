"""
builder.py — Immutable Relationship and RelationshipSet construction.

Changes from original:
    - Populates SchemaVersionInfo (schema_version, migration_version, compatibility_version)
    - Populates RelationshipProvenance with new fields (index_version, search_parameters,
      calibrator_version, classifier_version, raw_nli_confidence, calibrated_confidence)
    - Populates RelationshipQuality with calibration_applied and retrieval_quality
    - Sets lifecycle_stage to RELATIONSHIP on all constructed objects
    - relationship_id includes schema_version to guarantee ID change when ontology changes

Rules:
    ✅ Pure object construction
    ✅ Deterministic relationship_id generation
    ✅ Full provenance including calibration info
    ❌ Never perform NLI inference
    ❌ Never validate
    ❌ No heuristics or logic beyond construction
"""

from __future__ import annotations

import hashlib
from typing import List, Dict, Optional
import structlog

from smriti.core.models import (
    Relationship, RelationshipSet, RelationshipEvidence,
    RelationshipProvenance, RelationshipQuality, SchemaVersionInfo,
    RelationshipType, RelationshipDirection, LifecycleStage,
)
from smriti.retrieval.faiss_index import RETRIEVAL_BACKEND, RETRIEVAL_VERSION, INDEX_VERSION
from smriti.retrieval.classification.resolver import RESOLVER_VERSION
from smriti.retrieval.classification.calibration import CALIBRATOR_VERSION

logger = structlog.get_logger(__name__)

CURRENT_SCHEMA_VERSION = "6.0"
CURRENT_MIGRATION_VERSION = "6.0"
CURRENT_COMPATIBILITY_VERSION = "6.0"


def _compute_relationship_id(
    claim_id_a: str,
    claim_id_b: str,
    relationship_type: str,
    schema_version: str = CURRENT_SCHEMA_VERSION,
) -> str:
    """
    Deterministic 16-char SHA256 relationship ID including schema version.

    Injecting the schema version into the hash ensures that if the relationship
    ontology changes (e.g., the definition of SUPPORTS or CONTRADICTS evolves),
    the ID of every relationship changes automatically, preventing accidental
    cross-version mixing.
    """
    material = f"{claim_id_a}:{claim_id_b}:{relationship_type}:{schema_version}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def build_relationship(
    evidence: RelationshipEvidence,
    relationship_type: RelationshipType,
    direction: RelationshipDirection,
    nli_threshold: float,
    config_hash: str,
    run_id: str,
) -> Relationship:
    """
    Construct one immutable Relationship.

    Args:
        evidence:           NLI evidence for the pair (post-calibration).
        relationship_type:  Resolved type from resolver.
        direction:          Resolved direction.
        nli_threshold:      NLI confidence threshold (for quality diagnostics).
        config_hash:        SHA256 of relevant config.
        run_id:             Current pipeline run identifier.

    Returns:
        Immutable Relationship with full provenance, quality, and version info.
    """
    claim_id_a = evidence.pair.claim_id_a
    claim_id_b = evidence.pair.claim_id_b

    relationship_id = _compute_relationship_id(
        claim_id_a=claim_id_a,
        claim_id_b=claim_id_b,
        relationship_type=relationship_type.value,
        schema_version=CURRENT_SCHEMA_VERSION,
    )

    provenance = RelationshipProvenance(
        retrieval_backend=RETRIEVAL_BACKEND,
        retrieval_version=RETRIEVAL_VERSION,
        index_version=INDEX_VERSION,
        search_parameters=evidence.pair.search_parameters,
        classifier_model=evidence.inference_metadata.model_name,
        classifier_version=evidence.inference_metadata.model_version,
        resolver_version=RESOLVER_VERSION,
        calibrator_version=CALIBRATOR_VERSION,
        cosine_similarity=evidence.cosine_similarity,
        candidate_rank=evidence.pair.candidate_rank,
        raw_nli_confidence=evidence.nli_scores.raw_confidence,
        calibrated_confidence=evidence.calibrated_confidence,
        config_hash=config_hash,
        run_id=run_id,
        replay_id=None,
    )

    calibration_applied = (
        abs(evidence.nli_scores.raw_confidence - evidence.calibrated_confidence) > 1e-6
    )

    quality = RelationshipQuality(
        cosine_above_threshold=True,   # Guaranteed by candidate validator
        nli_above_threshold=evidence.calibrated_confidence >= nli_threshold,
        evidence_consistent=not (
            evidence.nli_scores.entailment_score >= nli_threshold
            and evidence.nli_scores.contradiction_score >= nli_threshold
        ),
        calibration_applied=calibration_applied,
        retrieval_quality=evidence.pair.retrieval_quality,
    )

    version_info = SchemaVersionInfo(
        schema_version=CURRENT_SCHEMA_VERSION,
        migration_version=CURRENT_MIGRATION_VERSION,
        compatibility_version=CURRENT_COMPATIBILITY_VERSION,
    )

    relationship = Relationship(
        relationship_id=relationship_id,
        claim_id_a=claim_id_a,
        claim_id_b=claim_id_b,
        relationship_type=relationship_type,
        direction=direction,
        evidence=evidence,
        quality=quality,
        provenance=provenance,
        version_info=version_info,
        lifecycle_stage=LifecycleStage.RELATIONSHIP,
    )

    logger.debug(
        "relationship built",
        rel_id=relationship_id[:8],
        type=relationship_type.value,
        calibrated_confidence=f"{evidence.calibrated_confidence:.3f}",
        calibration_applied=calibration_applied,
    )

    return relationship


def build_relationship_set(
    relationships: List[Relationship],
    total_candidates: int,
    total_validated: int,
    total_rejected: int,
    rejected_reasons: Dict[str, int],
    run_id: str,
) -> RelationshipSet:
    """Build the final RelationshipSet."""
    return RelationshipSet(
        relationships=relationships,
        total_candidates=total_candidates,
        total_validated=total_validated,
        total_rejected=total_rejected,
        rejected_reasons=rejected_reasons,
        run_id=run_id,
        version_info=SchemaVersionInfo(
            schema_version=CURRENT_SCHEMA_VERSION,
            migration_version=CURRENT_MIGRATION_VERSION,
            compatibility_version=CURRENT_COMPATIBILITY_VERSION,
        ),
    )