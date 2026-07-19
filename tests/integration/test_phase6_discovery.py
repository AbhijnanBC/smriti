"""
Integration test for Phase 6 end-to-end.
Uses mock NLI generator and mock FAISS index to avoid model downloads.
"""

import pytest
from pathlib import Path
from typing import List, Dict, Optional

from smriti.core.models import (
    Claim, EmbeddedClaim, RelationshipSet, RelationshipType,
    CandidatePair, RelationshipEvidence, NLIScores, InferenceMetadata,
    ClaimProvenance, ExtractionMode, AssertionMetadata, LifecycleStage,
    Embedding, EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, VectorDType,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.retrieval import discover_relationships
from smriti.retrieval.index import EmbeddingIndex, SearchResult
from smriti.retrieval.classification.evidence import NLIEvidenceGenerator


class MockNLIGenerator(NLIEvidenceGenerator):
    """Mock NLI generator — returns configurable evidence scores."""

    def __init__(self, contradiction_score: float = 0.90, entailment_score: float = 0.05):
        self._model_name = "mock-nli"
        self._batch_size = 16
        self._contradiction_score = contradiction_score
        self._entailment_score = entailment_score

    def _load_model(self):
        return None

    def generate_batch(self, pairs, claims_map):
        results = []
        neutral = max(0.0, 1.0 - self._contradiction_score - self._entailment_score)
        for pair in pairs:
            scores = [self._contradiction_score, self._entailment_score, neutral]
            predicted = ["contradiction", "entailment", "neutral"][scores.index(max(scores))]
            nli_scores = NLIScores(
                entailment_score=self._entailment_score,
                neutral_score=neutral,
                contradiction_score=self._contradiction_score,
                predicted_label=predicted,
                raw_confidence=max(scores),
            )
            metadata = InferenceMetadata(model_name="mock-nli")
            results.append(RelationshipEvidence(
                pair=pair,
                cosine_similarity=pair.cosine_similarity,
                nli_scores=nli_scores,
                calibrated_confidence=max(scores),
                inference_metadata=metadata,
                lifecycle_stage=LifecycleStage.EVIDENCE,
            ))
        return results


def make_claim(claim_id: str, text: str, context: str = "") -> Claim:
    return Claim(
        claim_id=claim_id, sentence_id="s001", document_id="d001",
        text=text, content_hash=claim_id[:16], context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context=context, sentence_position=0,
        ),
        schema_version="4.0", rule_version="1.0",
    )


def make_embedded_claim(claim_id: str, values: tuple = (0.5, 0.5, 0.5, 0.5)) -> EmbeddedClaim:
    vec = Vector(values=values, dimension=4, dtype=VectorDType.FLOAT64, normalized=True)
    descriptor = EmbeddingModelDescriptor(
        provider="test", model_name="test", model_revision="0",
        dimension=4, model_signature="test_sig",
    )
    provenance = EmbeddingProvenance(
        pipeline_version="1.0", normalization_mode="l2", device="cpu", config_hash="test",
    )
    embedding = Embedding(claim_id=claim_id, vector=vec, descriptor=descriptor, provenance=provenance)
    quality = EmbeddingQuality(dimension_ok=True, normalized=True, finite=True, cache_used=False)
    return EmbeddedClaim(claim_id=claim_id, embedding=embedding, quality=quality)


class MockFAISSIndex(EmbeddingIndex):
    def __init__(self, results: Dict[str, List[SearchResult]]):
        self._results = results
        self._dimension = 4
        self._size = 0

    @property
    def dimension(self): return self._dimension

    @property
    def size(self): return self._size

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
        embedded_claims=[], claims_map={},
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, nli_generator=MockNLIGenerator(),
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
    mock_index = MockFAISSIndex({
        "c001": [SearchResult("c002", 0.85, 1)],
        "c002": [SearchResult("c001", 0.85, 1)],
    })
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
    mock_index = MockFAISSIndex({
        "c001": [SearchResult("c002", 0.85, 1), SearchResult("c003", 0.82, 2)],
        "c002": [SearchResult("c003", 0.80, 1)],
        "c003": [],
    })
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b, ec_c], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.schema_version == "6.0"


def test_dataset_json_written(run_id, test_managers, tmp_path):
    ec_a = make_embedded_claim("c001")
    ec_b = make_embedded_claim("c002")
    claims_map = {"c001": make_claim("c001", "A."), "c002": make_claim("c002", "B.")}
    mock_index = MockFAISSIndex({"c001": [SearchResult("c002", 0.85, 1)], "c002": []})
    manifest_mgr, state_mgr = test_managers
    result = discover_relationships(
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    state = state_mgr.load()
    assert state is not None
    assert 6 in state.completed_phases


def test_no_nli_model_imports_in_candidate_modules():
    import smriti.retrieval.candidate_generator as cg
    import smriti.retrieval.validator as cv
    import smriti.retrieval.builder as cb

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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(),
    )
    for rel in result.relationships:
        assert rel.version_info is not None
        assert rel.version_info.schema_version == "6.0"
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
        embedded_claims=[ec_a, ec_b], claims_map=claims_map,
        run_id=run_id, manifest_manager=manifest_mgr,
        state_manager=state_mgr, index=mock_index,
        nli_generator=MockNLIGenerator(contradiction_score=0.90),
    )
    for rel in result.relationships:
        assert rel.provenance.raw_nli_confidence > 0
        assert rel.provenance.calibrated_confidence > 0
        assert rel.provenance.calibrator_version != ""