"""
ground_truth.py — GroundTruthRepository (Section 12.25, rectified).

RECTIFIED (P0-4): Ground Truth is a REPOSITORY, not a dataset.

A GroundTruthRepository contains:
    - Dataset (actual labeled items)
    - Annotation Schema (format specification)
    - Annotation Protocol (how items were labeled)
    - Annotator Agreement (inter-annotator agreement score)
    - Version history
    - Known Limitations
    - Quality Score
    - Validity Scope (where the labels are applicable)
    - Applicable Experiments (which experiment IDs can use this)

This replaces the minimal GroundTruthDataset which only captured
task, version, provenance, item_count, annotation_agreement, checksum.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from smriti.core.models import GroundTruthRepository, ScientificDomain
from smriti.exceptions import GroundTruthError

GROUND_TRUTH_REPOSITORY: Dict[str, GroundTruthRepository] = {}


def register_ground_truth(repo: GroundTruthRepository) -> None:
    GROUND_TRUTH_REPOSITORY[repo.repository_id] = repo


def get_ground_truth(repository_id: str) -> GroundTruthRepository:
    if repository_id not in GROUND_TRUTH_REPOSITORY:
        raise GroundTruthError(
            f"Ground truth repository '{repository_id}' not registered. "
            "Register before running experiments that depend on it."
        )
    return GROUND_TRUTH_REPOSITORY[repository_id]


def build_synthetic_ground_truth_repository(domain: ScientificDomain) -> GroundTruthRepository:
    """
    RECTIFIED (P0-4): Build a full GroundTruthRepository (not just a dataset).

    Synthetic repositories are used for architectural validation when
    human-annotated data is unavailable.
    """
    item_counts = {
        ScientificDomain.KNOWLEDGE_EXTRACTION: 50,
        ScientificDomain.EMBEDDING_QUALITY:    100,
        ScientificDomain.KNOWLEDGE_GRAPH:      30,
        ScientificDomain.RETRIEVAL:            80,
        ScientificDomain.RELIABILITY_SCORING:  40,
        ScientificDomain.EXPLAINABILITY:       20,
    }
    limitation_map = {
        ScientificDomain.KNOWLEDGE_EXTRACTION: (
            "Synthetic claims do not reflect real note-taking diversity.",
            "Limited to English text only.",
        ),
        ScientificDomain.EMBEDDING_QUALITY: (
            "Synthetic pairs do not cover all semantic similarity types.",
        ),
        ScientificDomain.KNOWLEDGE_GRAPH: (
            "Contradiction labels are structurally generated, not human-verified.",
        ),
        ScientificDomain.RETRIEVAL: (
            "Relevance judgements are synthetic and do not cover ambiguous queries.",
        ),
        ScientificDomain.RELIABILITY_SCORING: (
            "Ground truth reliability labels are policy-derived, not empirically grounded.",
        ),
        ScientificDomain.EXPLAINABILITY: (
            "Faithfulness labels assume component-sum decomposability.",
        ),
    }
    repo_id = f"synthetic_{domain.value}"
    return GroundTruthRepository(
        repository_id=repo_id,
        task=domain,
        version="synthetic_1.0",
        dataset_id=f"{repo_id}_dataset",
        item_count=item_counts.get(domain, 20),
        annotation_schema="synthetic_schema_v1",
        annotation_protocol="Programmatically generated from architectural invariants",
        annotator_agreement=None,
        created_at=datetime.now(tz=timezone.utc).isoformat(),
        checksum="synthetic",
        validity_scope="Architectural smoke-test only — not suitable for publication",
        applicable_experiments=tuple([f"EXP-00{i+1}" for i in range(6)]),
        known_limitations=limitation_map.get(domain, ("No known limitations documented.",)),
        quality_score=0.50,  # Synthetic data is acknowledged as lower quality
        license="internal",
    )