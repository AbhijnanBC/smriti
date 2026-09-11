"""
Integration test for Phase 6 end-to-end.
Uses mock NLI generator and mock FAISS index to avoid model downloads.
"""

from pathlib import Path

import pytest
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    AssertionMetadata,
    Claim,
    ClaimProvenance,
    EmbeddedClaim,
    Embedding,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    ExtractionMode,
    InferenceMetadata,
    LifecycleStage,
    NLIScores,
    RelationshipDirection,
    RelationshipEvidence,
    RelationshipSet,
    RelationshipType,
    Vector,
    VectorDType,
)
from smriti.core.state import StateManager
from smriti.retrieval import discover_relationships
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator
from smriti.retrieval.index import EmbeddingIndex, SearchResult


class MockNLIGenerator(NLIEvidenceGenerator):
    """
    Mock NLI generator — returns configurable evidence scores.

    RECTIFIED (bidirectional-NLI rewrite): also populates nli_scores_b_to_a
    so integration tests can exercise the resolver's bidirectional path
    (EQUIVALENT, direction-aware SUPPORTS/REFINES). Defaults
    (b_to_a_entailment_score=None) mirror the a_to_b scores exactly, which
    preserves every pre-existing test's behavior (a single-direction-style
    symmetric score triple resolves the same way whichever direction is
    checked) while still exercising the new dual-direction code path
    end-to-end, unlike leaving nli_scores_b_to_a unset entirely (which
    would silently keep hitting the legacy single-direction resolver
    branch and never test the rewrite at all).
    """

    def __init__(
        self,
        contradiction_score: float = 0.90,
        entailment_score: float = 0.05,
        b_to_a_contradiction_score: float | None = None,
        b_to_a_entailment_score: float | None = None,
    ):
        self._model_name = "mock-nli"
        self._batch_size = 16
        self._contradiction_score = contradiction_score
        self._entailment_score = entailment_score
        self._b_to_a_contradiction_score = (
            b_to_a_contradiction_score
            if b_to_a_contradiction_score is not None
            else contradiction_score
        )
        self._b_to_a_entailment_score = (
            b_to_a_entailment_score if b_to_a_entailment_score is not None else entailment_score
        )

    def _load_model(self):
        return None

    @staticmethod
    def _build_nli_scores(contradiction: float, entailment: float) -> NLIScores:
        neutral = max(0.0, 1.0 - contradiction - entailment)
        scores = [contradiction, entailment, neutral]
        predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
        return NLIScores(
            entailment_score=entailment,
            neutral_score=neutral,
            contradiction_score=contradiction,
            predicted_label=predicted,
            raw_confidence=max(scores),
        )

    def generate_batch(self, pairs, claims_map):
        results = []
        for pair in pairs:
            nli_scores = self._build_nli_scores(self._contradiction_score, self._entailment_score)
            nli_scores_b_to_a = self._build_nli_scores(
                self._b_to_a_contradiction_score, self._b_to_a_entailment_score
            )
            metadata = InferenceMetadata(model_name="mock-nli")
            results.append(
                RelationshipEvidence(
                    pair=pair,
                    cosine_similarity=pair.cosine_similarity,
                    nli_scores=nli_scores,
                    nli_scores_b_to_a=nli_scores_b_to_a,
                    calibrated_confidence=nli_scores.raw_confidence,
                    inference_metadata=metadata,
                    lifecycle_stage=LifecycleStage.EVIDENCE,
                )
            )
        return results


def make_claim(claim_id: str, text: str, context: str = "") -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id="d001",
        text=text,
        content_hash=claim_id[:16],
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001",
            document_id="d001",
            source_path=Path("test.md"),
            sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        rule_version="1.0",
    )


def make_embedded_claim(claim_id: str, values: tuple = (0.5, 0.5, 0.5, 0.5)) -> EmbeddedClaim:
    vec = Vector(values=values, dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test",
        model_name="test",
        model_revision="0",
        dimension=4,
        model_signature="test_sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0",
        normalization_mode="l2",
        device="cpu",
        config_hash="test",
    )
    embedding = Embedding(
        claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance
    )
    quality = EmbeddingQuality(dimension_ok=True, normalized=True, finite=True, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


class MockFAISSIndex(EmbeddingIndex):
    def __init__(self, results: dict[str, list[SearchResult]]):
        self._results = results
        self._dimension = 4
        self._size = 0

    @property
    def dimension(self):
        return self._dimension

    @property
    def size(self):
        return self._size

    def add(self, claim_ids, vectors):
        self._size += len(claim_ids)

    def search(self, query_id, query_vector, k, exclude_ids=None):
        results = self._results.get(query_id, [])
        if exclude_ids:
            results = [r for r in results if r.claim_id not in exclude_ids]
        return results[:k]


@pytest.fixture
def run_id():
    return "test_phase6_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Original 10 tests (preserved) ────────────────────────────────────────────


def test_empty_claims_returns_empty_relationship_set(run_id, test_managers):
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[],
        claims_map={},
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        nli_generator=MockNLIGenerator(),
    )
    assert isinstance(result, RelationshipSet)
    assert result.total_relationships == 0


def test_contradiction_is_discovered(run_id, test_managers):
    ec_a = make_embedded_claim("c001", (0.9, 0.1, 0.0, 0.0))
    ec_b = make_embedded_claim("c002", (-0.9, -0.1, 0.0, 0.0))
    claims_map = {
        "c001": make_claim("c001", "Python always normalizes features before PCA."),
        "c002": make_claim("c002", "Normalization before PCA is often unnecessary."),
    }
    mock_index = MockFAISSIndex(
        {
            "c001": [SearchResult("c002", 0.85, 1)],
            "c002": [SearchResult("c001", 0.85, 1)],
        }
    )
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.92),
    )
    assert result.total_relationships >= 1
    assert len(result.contradictions) >= 1


def test_all_relationships_are_immutable(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    for rel in result.relationships:
        with pytest.raises(Exception):
            rel.claim_id_a = "modified"


def test_relationship_ids_are_unique(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    ec_c = make_embedded_claim("c003")
    claims_map = {
        "c001": make_claim("c001", "Python is fast."),
        "c002": make_claim("c002", "Python is slow."),
        "c003": make_claim("c003", "Julia is fastest."),
    }
    mock_index = MockFAISSIndex(
        {
            "c001": [SearchResult("c002", 0.85, 1), SearchResult("c003", 0.82, 2)],
            "c002": [SearchResult("c003", 0.80, 1)],
            "c003": [],
        }
    )
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b, ec_c],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    rel_ids = [r.relationship_id for r in result.relationships]
    assert len(rel_ids) == len(set(rel_ids))


def test_all_relationships_have_complete_provenance(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.provenance is not None
        assert rel.provenance.run_id == run_id
        assert rel.provenance.classifier_model != ""
        assert rel.provenance.config_hash != ""


def test_schema_version_is_60(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.schema_version == "7.0"


def test_dataset_json_written(run_id, test_managers, tmp_path):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    assert result.dataset_path is not None
    assert result.dataset_path.exists()


def test_manifest_written(run_id, test_managers):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    import json

    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 6
    assert manifest["status"] == "success"


def test_pipeline_state_updated(run_id, test_managers):
    _, state_mgr = test_managers
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, _ = test_managers
    discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    state = state_mgr.load()
    assert state is not None
    assert 6 in state.completed_phases


def test_no_nli_model_imports_in_candidate_modules():
    import smriti.retrieval.builder as cb
    import smriti.retrieval.candidate_generator as cg
    import smriti.retrieval.validator as cv

    nli_modules = {"sentence_transformers", "transformers", "torch"}
    for module in [cg, cv, cb]:
        keys = set(vars(module).keys())
        assert not (keys & nli_modules)


# ── Rectified 3 new tests ─────────────────────────────────────────────────────


def test_replay_manifest_written(run_id, test_managers):
    """RECTIFIED: replay manifest must be written after every successful run."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    assert result.replay_manifest_path is not None
    assert result.replay_manifest_path.exists()


def test_all_relationships_have_schema_version_info(run_id, test_managers):
    """RECTIFIED: every relationship must carry SchemaVersionInfo."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.version_info is not None
        assert rel.version_info.schema_version == "7.0"
        assert rel.version_info.migration_version is not None
        assert rel.version_info.compatibility_version is not None


def test_calibrated_confidence_in_provenance(run_id, test_managers):
    """RECTIFIED: provenance must record both raw and calibrated confidence."""
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    for rel in result.relationships:
        assert rel.provenance.raw_nli_confidence > 0
        assert rel.provenance.calibrated_confidence > 0
        assert rel.provenance.calibrator_version != ""


# ── Bidirectional-NLI rewrite: EQUIVALENT and directional SUPPORTS ──────────


def test_bidirectional_entailment_both_ways_discovers_equivalent(run_id, test_managers):
    """When the mock NLI reports strong entailment in BOTH directions, the
    full Phase 6 pipeline (resolver + relatedness gate + specificity gate)
    must produce an EQUIVALENT relationship, not SUPPORTS."""
    ec_a = make_embedded_claim("c001", (0.9, 0.1, 0.0, 0.0))
    ec_b = make_embedded_claim("c002", (0.85, 0.15, 0.0, 0.0))
    claims_map = {
        "c001": make_claim("c001", "The Aurora server uses 8 GB of RAM."),
        "c002": make_claim("c002", "The Aurora server has 8 GB of RAM installed."),
    }
    mock_index = MockFAISSIndex(
        {
            "c001": [SearchResult("c002", 0.85, 1)],
            "c002": [SearchResult("c001", 0.85, 1)],
        }
    )
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(
            contradiction_score=0.02,
            entailment_score=0.93,
            b_to_a_contradiction_score=0.03,
            b_to_a_entailment_score=0.90,
        ),
    )
    assert len(result.equivalents) >= 1
    assert len(result.supports) == 0


def test_one_way_entailment_discovers_directional_supports(run_id, test_managers):
    """Entailment in only ONE direction must produce SUPPORTS with the
    direction NLI actually found, not EQUIVALENT and not a hardcoded
    A_TO_B regardless of which claim entails the other."""
    ec_a = make_embedded_claim("c001", (0.9, 0.1, 0.0, 0.0))
    ec_b = make_embedded_claim("c002", (0.85, 0.15, 0.0, 0.0))
    claims_map = {
        "c001": make_claim("c001", "The Norwich scheduler reduces average job latency."),
        "c002": make_claim("c002", "Job latency dropped after adopting the Norwich scheduler."),
    }
    mock_index = MockFAISSIndex(
        {
            "c001": [SearchResult("c002", 0.85, 1)],
            "c002": [SearchResult("c001", 0.85, 1)],
        }
    )
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(
            contradiction_score=0.02,
            entailment_score=0.93,  # A -> B: strong entailment
            b_to_a_contradiction_score=0.05,
            b_to_a_entailment_score=0.15,  # B -> A: not entailment
        ),
    )
    assert len(result.equivalents) == 0
    # Resolved as either SUPPORTS or REFINES (specificity gate may
    # reclassify), but never EQUIVALENT, and always A_TO_B given the
    # scripted evidence only supports that direction.
    directional = [
        r
        for r in result.relationships
        if r.relationship_type in (RelationshipType.SUPPORTS, RelationshipType.REFINES)
    ]
    assert len(directional) >= 1
    for rel in directional:
        assert rel.direction == RelationshipDirection.A_TO_B


def test_specificity_gate_reclassifies_supports_as_refines(run_id, test_managers):
    """A one-way-entailing claim that is meaningfully more specific/
    detailed than the claim it entails must be reclassified REFINES by
    the Stage 5c specificity gate, not left as SUPPORTS."""
    ec_a = make_embedded_claim("c001", (0.9, 0.1, 0.0, 0.0))
    ec_b = make_embedded_claim("c002", (0.85, 0.15, 0.0, 0.0))
    claims_map = {
        "c001": make_claim(
            "c001",
            "Transformers outperform U-Net on benchmark X for medical segmentation in 2023.",
        ),
        "c002": make_claim("c002", "Transformers outperform U-Net."),
    }
    mock_index = MockFAISSIndex(
        {
            "c001": [SearchResult("c002", 0.85, 1)],
            "c002": [SearchResult("c001", 0.85, 1)],
        }
    )
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b],
        claims_map=claims_map,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        index=mock_index,
        nli_generator=MockNLIGenerator(
            contradiction_score=0.02,
            entailment_score=0.93,  # A -> B: strong entailment
            b_to_a_contradiction_score=0.05,
            b_to_a_entailment_score=0.15,  # B -> A: no entailment
        ),
    )
    assert len(result.relationships) >= 1
    rel = result.relationships[0]
    assert rel.relationship_type == RelationshipType.REFINES
    assert rel.direction == RelationshipDirection.A_TO_B
