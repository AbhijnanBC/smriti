"""
pipeline/runner.py — PipelineRunner with Phases 1, 2, 3, and 4 registered.

Phases 5–13 will be added as they are built.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from unittest import result
from smriti.core.models import RelationshipSet, KnowledgeGraph, ScoredKnowledgeGraph, CertificationReport
from smriti.retrieval import discover_relationships
import structlog

from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.exceptions import PipelineError, Phase5Error
from smriti.api import KnowledgeAccessService, run_api_initialization
from smriti.governance import stable

logger = structlog.get_logger(__name__)


def _make_run_id() -> str:
    """Produce a timestamp-based run_id. Unique per execution."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

@stable("1.0")
class PipelineRunner:
    """
    Orchestrates pipeline phases.

    Usage:
        runner = PipelineRunner(input_dirs=[Path("data/raw")])
        runner.run()
    """

    def __init__(self, input_dirs: List[Path]):
        self.input_dirs = [Path(d) for d in input_dirs]
        self.run_id = _make_run_id()
        self.manifest_manager = ManifestManager(
            run_id=self.run_id,
            artifacts_dir=ARTIFACTS_DIR,
        )
        self.state_manager = StateManager()
        logger.info("pipeline runner initialized", run_id=self.run_id)

    def run(
        self,
        start_from: int = 1,
        stop_at: Optional[int] = None,
        force_full: bool = False,
    ) -> bool:
        """
        Run pipeline phases start_from through stop_at.

        Args:
            start_from:  First phase to run (default 1).
            stop_at:     Last phase to run (default: run all registered).
            force_full:  Ignore caches and re-process everything.

        Returns:
            True if all phases succeeded.
        """
        logger.info(
            "pipeline run starting",
            run_id=self.run_id,
            start_from=start_from,
            stop_at=stop_at,
        )

        # Check for resumable state
        state = self.state_manager.load()
        if state and not force_full:
            completed = state.completed_phases
            if completed:
                resume_from = max(completed) + 1
                if resume_from > start_from:
                    logger.info(
                        "resuming from checkpoint",
                        completed_phases=completed,
                        resuming_at=resume_from,
                    )
                    start_from = resume_from

        try:
            # ── Phase 1: Input Discovery ───────────────────────────────────────
            phase1_result = None
            if start_from <= 1 and (stop_at is None or stop_at >= 1):
                phase1_result = self._run_phase_1(force_full=force_full)

            # ── Phase 2: Text Extraction ───────────────────────────────────────
            phase2_result = None
            if start_from <= 2 and (stop_at is None or stop_at >= 2):
                if phase1_result is None:
                    # Resuming from Phase 2 — load Phase 1 dataset from artifact
                    phase1_result = self._load_phase1_result()

                phase2_result = self._run_phase_2(phase1_result)

            # ── Phase 3: Semantic Sentence Construction ──────────────────────
            phase3_result = None
            if start_from <= 3 and (stop_at is None or stop_at >= 3):
                if phase2_result is None:
                    phase2_result = self._load_phase2_result()
                phase3_result = self._run_phase_3(phase2_result)

            # ── Phase 4: Claim Construction ────────────────────────────────────
            phase4_result = None
            if start_from <= 4 and (stop_at is None or stop_at >= 4):
                if phase3_result is None:
                    phase3_result = self._load_phase3_result()
                phase4_result = self._run_phase_4(phase3_result)


            phase5_result = None
            if start_from <= 5 and (stop_at is None or stop_at >= 5):
                if phase4_result is None:
                    phase4_result = self._load_phase4_result()
                phase5_result = self._run_phase_5(phase4_result)

            phase6_result = None
            if start_from <= 6 and (stop_at is None or stop_at >= 6):
                if phase5_result is None:
                    phase5_result = self._load_phase5_result()
                phase4_claims = self._load_phase4_result_as_map()
                phase6_result = self._run_phase_6(phase5_result, phase4_claims) 

            phase7_result = None
            if start_from <= 7 and (stop_at is None or stop_at >= 7):
                if phase6_result is None:
                    phase6_result = self._load_phase6_result()
                if phase4_claims is None:
                    phase4_claims = self._load_phase4_result_as_map()
            phase7_result = self._run_phase_7(phase6_result, phase4_claims)  

            phase8_result = None
            if start_from <= 8 and (stop_at is None or stop_at >= 8):
                if phase7_result is None:
                    phase7_result = self._load_phase7_result()
                phase8_result = self._run_phase_8(phase7_result) 

            phase9_api = None
            if start_from <= 9 and (stop_at is None or stop_at >= 9):
                if phase8_result is None:
                    phase8_result = self._load_phase8_result()
                phase9_api = self._run_phase_9(phase8_result)   

            if start_from <= 10 and (stop_at is None or stop_at >= 10):
                 self._run_phase_10(phase9_api)

            if start_from <= 11 and (stop_at is None or stop_at >= 11):
                self._run_phase_11()     

            if start_from <= 12 and (stop_at is None or stop_at >= 12):
                if phase9_api is None:
                    phase8_result = self._load_phase8_result()
                    from smriti.api import build_knowledge_api
                    phase9_api = build_knowledge_api(phase8_result)
                self._run_phase_12(phase9_api)
            

        except Exception as e:
            logger.error("pipeline failed", error=str(e), exc_info=True)
            return False

        logger.info("pipeline run complete", run_id=self.run_id)
        return True

    # ── Phase 1 implementation ────────────────────────────────────────────────

    def _run_phase_1(self, force_full: bool = False):
        """Execute Phase 1: Input Discovery."""
        from smriti.discovery import run_discovery, DiscoveryResult

        logger.info("running phase 1")
        result = run_discovery(
            input_dirs=self.input_dirs,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            force_full=force_full,
        )
        logger.info(
            "phase 1 complete",
            canonical_docs=result.canonical_count,
            duplicates=len(result.duplicate_documents),
            skipped=len(result.skipped),
        )
        return result

    def _load_phase1_result(self):
        """
        Load Phase 1 dataset from artifact when resuming at Phase 2.
        Reconstructs SourceDocument list from dataset.json.
        """
        import json
        from datetime import datetime, timezone
        from smriti.core.models import FileFormat, SourceDocument
        from smriti.discovery import DiscoveryResult, DiscoveryStats, DuplicateRegistry

        # Find the most recent run's phase1 dataset
        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase1" / "dataset.json"
        if not dataset_path.exists():
            # Try to find any existing phase1 artifact
            phase1_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase1/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase1_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 2: no Phase 1 dataset.json found. "
                    "Run from Phase 1 first."
                )
            dataset_path = phase1_dirs[0]
            logger.info("loading phase1 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        source_documents = []
        for r in records:
            source_documents.append(
                SourceDocument(
                    doc_id=r["doc_id"],
                    path=Path(r["path"]),
                    relative_path=Path(r["relative_path"]),
                    source_root=Path(r["source_root"]),
                    format=FileFormat(r["format"]),
                    content_hash=r["content_hash"],
                    size_bytes=r["size_bytes"],
                    modified_at=datetime.fromisoformat(r["modified_at"]),
                )
            )

        # Reconstruct a minimal DiscoveryResult for Phase 2
        return type("DiscoveryResult", (), {
            "canonical_documents": source_documents,
        })()

    # ── Phase 2 implementation ────────────────────────────────────────────────

    def _run_phase_2(self, phase1_result):
        """
        Execute Phase 2: Text Extraction.
        Returns the extraction result so it can be used by later phases.
        """
        from smriti.parsing import run_extraction

        logger.info("running phase 2")
        result = run_extraction(
            source_documents=phase1_result.canonical_documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 2 complete",
            successful=result.stats.successful,
            failed=result.stats.failed,
            total_chars=result.stats.total_characters,
        )
        return result   # <-- return the result so Phase 3 can consume it

    # ── Phase 3 implementation ────────────────────────────────────────────────

    def _load_phase2_result(self):
        """Load Phase 2 dataset from artifact when resuming at Phase 3."""
        import json
        from smriti.core.models import (
            Document, SourceDocument, FileFormat, ExtractionMethod,
            TextStatistics, WarningCode, RawExtractionResult,
        )
        from datetime import datetime, timezone

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase2" / "dataset.json"
        if not dataset_path.exists():
            phase2_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase2/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase2_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 3: no Phase 2 dataset.json found. "
                    "Run from Phase 2 first."
                )
            dataset_path = phase2_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        documents = []
        for r in records:
            source_doc = SourceDocument(
                doc_id=r["doc_id"],
                path=Path(r["path"]),
                relative_path=Path(r["relative_path"]),
                source_root=Path(r["source_root"]),
                format=FileFormat(r["format"]),
                content_hash=r["content_hash"],
                size_bytes=r["size_bytes"],
                modified_at=datetime.fromisoformat(r["modified_at"]),
            )
            stats = TextStatistics(
                character_count=r["stats"]["character_count"],
                word_count=r["stats"]["word_count"],
                line_count=r["stats"]["line_count"],
                blank_line_count=r["stats"]["blank_line_count"],
                paragraph_count=r["stats"]["paragraph_count"],
            )
            documents.append(Document(
                doc_id=r["doc_id"],
                source_document=source_doc,
                raw_text=r["raw_text"],
                normalized_text=r["normalized_text"],
                extraction_method=ExtractionMethod(r["extraction_method"]),
                extraction_warnings=tuple(WarningCode(w) for w in r.get("warnings", [])),
                text_statistics=stats,
                encoding_used=r.get("encoding_used", "utf-8"),
            ))
        return type("Phase2Result", (), {"documents": documents})()

    def _run_phase_3(self, phase2_result):
        """Execute Phase 3: Semantic Sentence Construction."""
        from smriti.extraction import run_extraction

        logger.info("running phase 3")
        result = run_extraction(
            documents=phase2_result.documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 3 complete",
            total_sentences=result.total_sentences,
            docs_ok=result.successful_documents,
            docs_failed=result.failed_documents,
        )
        return result   # return for future phases if needed

    # ── Phase 4 implementation ────────────────────────────────────────────────

    def _load_phase3_result(self):
        """Load Phase 3 dataset from artifact when resuming at Phase 4."""
        import json
        from smriti.core.models import SemanticSentence
        from pathlib import Path

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase3" / "dataset.json"
        if not dataset_path.exists():
            phase3_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase3/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase3_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 4: no Phase 3 dataset.json found. "
                    "Run from Phase 3 first."
                )
            dataset_path = phase3_dirs[0]
            logger.info("loading phase3 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        sentences = []
        for r in records:
            sentences.append(SemanticSentence(
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r["context"],
                position=r["position"],
                char_start=r["char_start"],
                char_end=r["char_end"],
                source_path=Path(r["source_path"]),
                origin_block_type=r.get("origin_block_type", "paragraph"),
                schema_version=r.get("schema_version", "3.0"),
            ))

        return type("Phase3Result", (), {"all_sentences": sentences})()

    def _run_phase_4(self, phase3_result):
        """Execute Phase 4: Claim Construction."""
        from smriti.claims import extract_claims
        from smriti.claims import Phase4Result

        logger.info("running phase 4")
        result = extract_claims(
            semantic_sentences=phase3_result.all_sentences,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 4 complete",
            total_claims=result.total_claims,
            structured=result.stats.structured_claims,
            parser_failures=result.stats.parser_failures,
        )
        return result
    
        # ── Phase 5 implementation ────────────────────────────────────────────────

    def _load_phase4_result(self):
        """
        Load Phase 4 dataset from artifact when resuming at Phase 5.

        Validates schema_version before deserializing to avoid silently
        processing data from an incompatible Phase 4 implementation.
        """
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        SUPPORTED_PHASE4_SCHEMA = "4.0"

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 5: no Phase 4 dataset.json found. "
                    "Run from Phase 4 first."
                )
            dataset_path = phase4_dirs[0]
            logger.info("loading phase4 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))

        # Validate schema_version before deserializing.
        schema_versions = {r.get("schema_version", "unknown") for r in records if records}
        unsupported = schema_versions - {SUPPORTED_PHASE4_SCHEMA}
        if unsupported:
            logger.warning(
                "unexpected schema_version in phase4 dataset",
                found=sorted(unsupported),
                expected=SUPPORTED_PHASE4_SCHEMA,
            )

        claims = []
        for r in records:
            prov_data = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov_data.get("sentence_id", ""),
                document_id=prov_data.get("document_id", ""),
                source_path=Path(prov_data.get("source_path", "unknown")),
                sentence_context=prov_data.get("sentence_context", ""),
                sentence_position=prov_data.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claims.append(Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                content_hash=r.get("content_hash", ""),
                rule_version=r.get("rule_version", "1.0"),
            ))

        return type("Phase4Result", (), {"all_claims": claims})()

    def _run_phase_5(self, phase4_result):
        """Execute Phase 5: Semantic Embedding."""
        from smriti.embedding import embed_claims
        from smriti.exceptions import Phase5Error

        logger.info("running phase 5")
        try:
            result = embed_claims(
                claims=phase4_result.all_claims,
                run_id=self.run_id,
                manifest_manager=self.manifest_manager,
                state_manager=self.state_manager,
            )
        except Phase5Error as e:
            logger.error("phase 5 failed with Phase5Error", error=str(e))
            raise  # Let the runner handle it cleanly

        if result.warnings:
            logger.warning(
                "phase 5 completed with warnings",
                warning_count=len(result.warnings),
                first_warning=result.warnings[0],
            )
        if result.errors:
            logger.error(
                "phase 5 completed with errors",
                error_count=len(result.errors),
            )

        logger.info(
            "phase 5 complete",
            total_embedded=result.total_embedded,
            cached=result.stats.cached,
            failed=result.stats.failed,
            cache_hit_rate=f"{result.stats.cache_hit_rate:.1%}",
            throughput=f"{result.stats.vectors_per_second:.1f} vec/s",
        )
        return result    
    

    def _run_phase_6(self, phase5_result, claims_map) -> "RelationshipSet":
        """Execute Phase 6: Semantic Relationship Discovery."""
        from smriti.retrieval import discover_relationships

        logger.info("running phase 6")
        result = discover_relationships(
            embedded_claims=phase5_result.embedded_claims,
            claims_map=claims_map,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 6 complete",
            total_relationships=result.total_relationships,
            contradictions=len(result.contradictions),
        )
        return result


    def _load_phase5_result(self):
        """Load Phase 5 dataset from artifact when resuming at Phase 6."""
        import json, math
        from smriti.core.models import (
            EmbeddedClaim, Embedding, EmbeddingModelDescriptor,
            EmbeddingProvenance, EmbeddingQuality, Vector, VectorDType,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase5" / "dataset.json"
        if not dataset_path.exists():
            phase5_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase5/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase5_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 6: no Phase 5 dataset.json found."
                )
            dataset_path = phase5_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        embedded_claims = []

        for r in records:
            vector_vals = r["vector"]
            dim = r["dimension"]
            vec = Vector(
                values=tuple(float(v) for v in vector_vals),
                dimension=dim,
                dtype=VectorDType.FLOAT64,
                normalized=True,
            )
            prov_data = r["provenance"]
            provenance = EmbeddingProvenance(
                pipeline_version=prov_data.get("pipeline_version", "1.0"),
                normalization_mode=prov_data.get("normalization_mode", "l2"),
                device=prov_data.get("device", "cpu"),
                config_hash=prov_data.get("config_hash", ""),
            )
            model_data = r["model"]
            descriptor = EmbeddingModelDescriptor(
                provider=model_data.get("provider", ""),
                model_name=model_data.get("model_name", ""),
                model_revision=model_data.get("revision", ""),
                dimension=model_data.get("dimension", dim),
                model_signature=model_data.get("signature", ""),
            )
            embedding = Embedding(
                claim_id=r["claim_id"],
                vector=vec,
                descriptor=descriptor,
                provenance=provenance,
            )
            quality = EmbeddingQuality(
                dimension_ok=True,
                normalized=True,
                finite=all(math.isfinite(v) for v in vector_vals[:5]),
                cache_used=r.get("status") == "cached",
            )
            ec = EmbeddedClaim(
                claim_id=r["claim_id"],
                embedding=embedding,
                quality=quality,
                schema_version=r.get("schema_version", "5.0"),
            )
            embedded_claims.append(ec)

        return type("Phase5Result", (), {"embedded_claims": embedded_claims})()


    def _load_phase4_result_as_map(self):
        """Load Phase 4 claims as a {claim_id: Claim} dict for Phase 6 text lookup."""
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError("No Phase 4 dataset.json found for claim text lookup.")
            dataset_path = phase4_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        claims_map = {}

        for r in records:
            prov = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov.get("sentence_id", ""),
                document_id=prov.get("document_id", ""),
                source_path=Path(prov.get("source_path", "unknown")),
                sentence_context=prov.get("sentence_context", ""),
                sentence_position=prov.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claim = Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                content_hash=r.get("content_hash", ""),
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                rule_version=r.get("rule_version", "1.0"),
            )
            claims_map[claim.claim_id] = claim

        return claims_map
    

    def _run_phase_7(self, phase6_result, claims_map) -> "KnowledgeGraph":
        """Execute Phase 7: Knowledge Graph Construction."""
        from smriti.evolution import build_knowledge_graph

        logger.info("running phase 7")
        result = build_knowledge_graph(
            relationship_set=phase6_result,
            claims_map=claims_map,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 7 complete",
            nodes=result.node_count,
            edges=result.edge_count,
            partitions=result.partition_count,
            contradictions=result.statistics.contradiction_count,
            evolution_chains=result.statistics.evolution_chains,
            bridge_nodes=result.statistics.bridge_nodes,
        )
        return result


    def _load_phase6_result(self):
        """Load Phase 6 dataset from artifact when resuming at Phase 7."""
        import json
        from smriti.core.models import (
            RelationshipSet, Relationship, RelationshipType, RelationshipDirection,
            RelationshipEvidence, RelationshipProvenance, RelationshipQuality,
            NLIScores, InferenceMetadata, CandidatePair, SchemaVersionInfo,
            LifecycleStage,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase6" / "dataset.json"
        if not dataset_path.exists():
            phase6_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase6/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase6_dirs:
                raise PipelineError("Cannot resume at Phase 7: no Phase 6 dataset.json found.")
            dataset_path = phase6_dirs[0]
            logger.info("loading phase6 dataset", path=str(dataset_path))

        data = json.loads(dataset_path.read_text(encoding="utf-8"))
        relationships = []

        for r in data:
            ev_data = r["evidence"]
            prov_data = r["provenance"]

            pair = CandidatePair(
                claim_id_a=r["claim_id_a"],
                claim_id_b=r["claim_id_b"],
                cosine_similarity=ev_data["cosine_similarity"],
                candidate_rank=prov_data.get("candidate_rank", 1),
            )
            nli_scores = NLIScores(
                entailment_score=ev_data.get("entailment_score", 0.0),
                neutral_score=ev_data.get("neutral_score", 0.0),
                contradiction_score=ev_data.get("contradiction_score", 0.0),
                predicted_label=ev_data.get("predicted_label", "neutral"),
                raw_confidence=ev_data.get("raw_confidence", ev_data.get("confidence", 0.0)),
            )
            inference_meta = InferenceMetadata(
                model_name=ev_data.get("model_name", ""),
                model_version=ev_data.get("model_version", "unknown"),
            )
            evidence = RelationshipEvidence(
                pair=pair,
                cosine_similarity=ev_data["cosine_similarity"],
                nli_scores=nli_scores,
                calibrated_confidence=ev_data.get("calibrated_confidence", ev_data.get("confidence", 0.0)),
                inference_metadata=inference_meta,
                lifecycle_stage=LifecycleStage.RELATIONSHIP,
            )
            provenance = RelationshipProvenance(
                retrieval_backend=prov_data.get("retrieval_backend", "faiss_flat_ip"),
                retrieval_version=prov_data.get("retrieval_version", "1.0"),
                index_version=prov_data.get("index_version", "1.0"),
                search_parameters=None,
                classifier_model=prov_data.get("classifier_model", ""),
                classifier_version=prov_data.get("classifier_version", "unknown"),
                resolver_version=prov_data.get("resolver_version", "1.0"),
                calibrator_version=prov_data.get("calibrator_version", "1.0"),
                cosine_similarity=prov_data.get("cosine_similarity", 0.0),
                candidate_rank=prov_data.get("candidate_rank", 1),
                raw_nli_confidence=prov_data.get("raw_nli_confidence", prov_data.get("nli_confidence", 0.0)),
                calibrated_confidence=prov_data.get("calibrated_confidence", 0.0),
                config_hash=prov_data.get("config_hash", ""),
                run_id=prov_data.get("run_id", self.run_id),
            )
            quality = RelationshipQuality(
                cosine_above_threshold=True, nli_above_threshold=True,
                evidence_consistent=True, calibration_applied=False,
            )
            version_info = SchemaVersionInfo(
                schema_version=r.get("schema_version", "6.0"),
                migration_version="6.0", compatibility_version="6.0",
            )
            relationships.append(Relationship(
                relationship_id=r["relationship_id"],
                claim_id_a=r["claim_id_a"], claim_id_b=r["claim_id_b"],
                relationship_type=RelationshipType(r["relationship_type"]),
                direction=RelationshipDirection(r["direction"]),
                evidence=evidence, quality=quality, provenance=provenance, version_info=version_info,
            ))

        return RelationshipSet(
            relationships=relationships,
            total_candidates=len(relationships),
            total_validated=len(relationships),
            total_rejected=0,
            rejected_reasons={},
            run_id=self.run_id,
        )


    def _run_phase_8(
        self,
        phase7_result: "KnowledgeGraph",
        policy_profile: str = "balanced",
    ) -> "ScoredKnowledgeGraph":
        """Execute Phase 8: Reliability Evaluation."""
        from smriti.scoring import score_knowledge_graph
        from smriti.scoring.policies import PolicyProfile

        try:
            profile = PolicyProfile(policy_profile)
        except ValueError:
            logger.warning("unknown policy profile, using BALANCED", profile=policy_profile)
            profile = PolicyProfile.BALANCED

        logger.info("running phase 8", profile=profile.value)
        result = score_knowledge_graph(
            graph=phase7_result,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            policy_profile=profile,
        )
        logger.info(
            "phase 8 complete",
            claims_scored=result.total_scored,
            avg_reliability=f"{result.avg_reliability:.2f}",
            profile=result.policy_profile,
        )
        return result


    def _load_phase7_result(self):
        """Load Phase 7 KnowledgeGraph from artifact when resuming at Phase 8."""
        import json
        from pathlib import Path
        from smriti.core.models import (
            KnowledgeGraph, ClaimNode, RelationshipEdge, KnowledgePartition,
            RelationshipType, RelationshipDirection, GraphStatistics, ValidationReport,
            SemanticRole, TopologyMetrics, SupportAggregate, TemporalMetadata,
            TemporalStatus, NodeAnnotations,
        )

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase7" / "dataset.json"
        if not dataset_path.exists():
            phase7_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase7/dataset.json"),
                key=lambda p: p.parent.parent.name, reverse=True,
            )
            if not phase7_dirs:
                raise PipelineError("Cannot resume at Phase 8: no Phase 7 dataset.json found.")
            dataset_path = phase7_dirs[0]
            logger.info("loading phase7 dataset", path=str(dataset_path))

        data = json.loads(dataset_path.read_text(encoding="utf-8"))
        nodes = {}
        for claim_id, nd in data.get("nodes", {}).items():
            topo_data = nd.get("topology")
            topology = None
            if topo_data:
                topology = TopologyMetrics(
                    degree=topo_data.get("degree", 0),
                    in_degree=topo_data.get("in_degree", 0),
                    out_degree=topo_data.get("out_degree", 0),
                    is_bridge=topo_data.get("is_bridge", False),
                    is_hub=topo_data.get("is_hub", False),
                    partition_id=nd.get("partition_id", ""),
                    centrality=topo_data.get("centrality", 0.0),
                )
            support_data = nd.get("support")
            support = None
            if support_data:
                support = SupportAggregate(
                    support_count=support_data.get("count", 0),
                    weighted_confidence=support_data.get("weighted_confidence", 0.0),
                    supporting_claim_ids=tuple(support_data.get("supporting_claims", [])),
                    evidence_summary=f"{support_data.get('count', 0)} supporting claims",
                )
            temp_data = nd.get("temporal")
            temporal = None
            if temp_data:
                temporal = TemporalMetadata(
                    status=TemporalStatus(temp_data.get("status", "static_partition")),
                    earlier_claim_id=temp_data.get("earlier_claim_id"),
                    later_claim_id=temp_data.get("later_claim_id"),
                    time_delta_days=temp_data.get("time_delta_days"),
                    temporal_confidence=temp_data.get("temporal_confidence", 0.0),
                )
            # Reconstruct NodeAnnotations (RECTIFIED for Phase 7 compatibility)
            annotations = NodeAnnotations(
                semantic_role=SemanticRole(nd.get("semantic_role", "unclassified")),
                topology=topology,
                support_aggregate=support,
                temporal_metadata=temporal,
                partition_id=nd.get("partition_id"),
            )
            nodes[claim_id] = ClaimNode(
                node_id=claim_id, claim_id=claim_id,
                claim_text=nd.get("claim_text", ""),
                context=nd.get("context", ""),
                source_path=Path(nd.get("source_path", "unknown")),
                document_id=nd.get("document_id", ""),
                annotations=annotations,
                schema_version=nd.get("schema_version", "7.0"),
            )

        edges = {}
        for edge_id, ed in data.get("edges", {}).items():
            edges[edge_id] = RelationshipEdge(
                edge_id=edge_id,
                source_node_id=ed.get("source", ""),
                target_node_id=ed.get("target", ""),
                relationship_type=RelationshipType(ed.get("relationship_type", "supports")),
                direction=RelationshipDirection(ed.get("direction", "symmetric")),
                calibrated_confidence=ed.get("calibrated_confidence", 0.0),
                cosine_similarity=ed.get("cosine_similarity", 0.0),
                nli_confidence=ed.get("nli_confidence", ed.get("calibrated_confidence", 0.0)),
                candidate_rank=ed.get("candidate_rank", 1),
            )

        partitions = {}
        for pid, pd in data.get("partitions", {}).items():
            partitions[pid] = KnowledgePartition(
                partition_id=pid,
                stable_partition_label=pd.get("stable_partition_label", ""),
                node_ids=frozenset(pd.get("node_ids", [])),
                internal_edge_ids=frozenset(),
                node_count=pd.get("node_count", 0),
                edge_count=pd.get("edge_count", 0),
                supports_count=pd.get("supports_count", 0),
                refines_count=pd.get("refines_count", 0),
                density=pd.get("density", 0.0),
                longest_support_chain=pd.get("longest_support_chain", 0),
            )

        stats_data = data.get("statistics", {})
        stats = GraphStatistics(
            node_count=stats_data.get("node_count", len(nodes)),
            edge_count=stats_data.get("edge_count", len(edges)),
            partition_count=stats_data.get("partition_count", len(partitions)),
            contradiction_count=stats_data.get("contradiction_count", 0),
            supports_count=stats_data.get("supports_count", 0),
            refines_count=stats_data.get("refines_count", 0),
            isolated_nodes=0, bridge_nodes=0, hub_nodes=0,
            evolution_chains=stats_data.get("evolution_chains", 0),
            unresolved_conflicts=stats_data.get("unresolved_conflicts", 0),
            construction_time_seconds=0.0, enrichment_time_seconds=0.0,
        )
        val_data = data.get("validation", {})
        validation = ValidationReport(
            is_valid=val_data.get("is_valid", True),
            node_violations=(), edge_violations=(), graph_violations=(),
            semantic_warnings=(),
            validation_time_seconds=0.0,
        )
        return KnowledgeGraph(
            graph_id=data.get("graph_id", ""), nodes=nodes, edges=edges, partitions=partitions,
            statistics=stats, validation_report=validation,
            run_id=data.get("run_id", self.run_id),
            config_hash=data.get("config_hash", ""),
            schema_version=data.get("schema_version", "7.0"),
        )
    
    def _run_phase_9(self, phase8_result: "ScoredKnowledgeGraph") -> "KnowledgeAccessService":
        """Execute Phase 9: Knowledge Access Layer initialization."""
        from smriti.api import run_api_initialization

        logger.info("running phase 9")
        api = run_api_initialization(
            scored_graph=phase8_result,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 9 complete",
            nodes_indexed=api.node_count,
            api_version=api.api_version,
        )
        return api
    
    def _run_phase_10(self, knowledge_api) -> None:
        """
        Phase 10: Prepare and register the Streamlit dashboard.

        Writes phase10/dashboard_info.json and phase10/manifest.json.
        Dashboard is launched separately (blocking Streamlit inside runner is wrong).
        """
        import json

        logger.info("phase 10 starting — registering dashboard")
        start_time = self.manifest_manager.start_phase(phase=10)

        phase_dir = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase10"
        phase_dir.mkdir(parents=True, exist_ok=True)

        dashboard_info = {
            "run_id":          self.run_id,
            "api_version":     getattr(knowledge_api, "api_version", "1.0"),
            "nodes_indexed":   getattr(knowledge_api, "node_count", 0),
            "dashboard_entry": "src/smriti/dashboard/app.py",
            "command":         "poetry run streamlit run src/smriti/dashboard/app.py",
        }
        info_path = phase_dir / "dashboard_info.json"
        info_path.write_text(json.dumps(dashboard_info, indent=2))

        self.manifest_manager.end_phase(
            phase=10,
            start_time=start_time,
            inputs={"knowledge_api_nodes": getattr(knowledge_api, "node_count", 0)},
            outputs={
                "dashboard_info": str(info_path),
                "command":        dashboard_info["command"],
            },
            status="success",
        )
        self.state_manager.complete_phase(phase=10)

        logger.info("phase 10 complete", dashboard_command=dashboard_info["command"])
        print("\n" + "=" * 60)
        print("SMRITI Dashboard Ready")
        print("=" * 60)
        print(f"Run ID: {self.run_id}")
        print(f"Nodes indexed: {getattr(knowledge_api, 'node_count', 0)}")
        print(f"\nTo launch the dashboard:")
        print(f"  {dashboard_info['command']}")
        print("=" * 60 + "\n")


    def _run_phase_11(self) -> None:
        """
        Execute Phase 11: Operational Runtime & Engineering Infrastructure.

        RECTIFIED: Now uses OperationalContext + EventBus + CapabilityModel + RuntimeScheduler.
        Fully integrates DependencyGraph with HealthCoordinator and CapabilityModel.

        Steps:
            1. Build OperationalContext (P0-1)
            2. Subscribe TelemetryCollector to EventBus (P0-2)
            3. Activate RuntimeCoordinator (split via sub-coordinators, P0-3)
            4. Enable CapabilityModel (P0-4)
            5. Wire DependencyGraph to HealthCoordinator and CapabilityModel
            6. Start RuntimeScheduler for periodic tasks (P1-2)
            7. Assert system invariants
            8. Write RuntimeManifest with architecture version (P1-5)
            9. Register shutdown handler
        """
        from smriti.runtime import get_runtime, OperationalContext
        from smriti.runtime.events import get_event_bus
        from smriti.runtime.scheduler import RuntimeScheduler
        from smriti.runtime.health_coordinator import HealthCoordinator
        from smriti.infrastructure.provenance import ProvenanceBuilder
        from smriti.governance.invariants import assert_all_invariants
        from smriti.observability.telemetry import TelemetryCollector
        from smriti.core.paths import ARTIFACTS_DIR
        from smriti.core.config import get_config
        from smriti.observability.health import HealthStatus  # for check return types
        import hashlib

        logger.info("running phase 11")
        config = get_config()
        cfg11 = config.get("feature_flags", {})

        # ── Step 1: Build OperationalContext (P0-1) ───────────────────────────────
        ctx = OperationalContext.create(
            run_id=self.run_id,
            config_hash="",  # populated after coordinator starts
            env=config.env,
        )

        # ── Step 2: Subscribe TelemetryCollector to EventBus (P0-2) ──────────────
        if cfg11.get("enable_event_bus", True):
            telemetry = TelemetryCollector(run_id=self.run_id)
            telemetry.subscribe_to_event_bus()

        # ── Step 3: Activate RuntimeCoordinator ───────────────────────────────────
        coordinator = get_runtime()
        coordinator.start(run_id=self.run_id)

        # ── Step 4: Get the dependency graph and wire it ─────────────────────────
        dep_graph = coordinator.dependency_graph

        # ── Step 5: Wire HealthCoordinator with the graph ────────────────────────
        # Get the HealthCoordinator from the runtime coordinator.
        # (We access the private attribute; consider adding a public property later.)
        health_coordinator = coordinator._health_coordinator
        health_coordinator.bind_graph(dep_graph)

        # Register default health checks with node mappings
        from smriti.core.paths import ARTIFACTS_DIR

        def check_config() -> bool:
            try:
                cfg = get_config()
                return bool(cfg)
            except Exception:
                return False

        def check_artifacts_dir() -> bool:
            try:
                return ARTIFACTS_DIR.exists()
            except Exception:
                return False

        def check_memory() -> bool:
            try:
                import psutil
                mem = psutil.virtual_memory()
                # Consider healthy if memory usage < 90%
                return mem.percent < 90
            except Exception:
                return False

        # Register checks with the coordinator, mapping to dependency nodes
        health_coordinator.register(
            "configuration",
            check_config,
            dependency_node="config"      # assume a node named "config" exists
        )
        health_coordinator.register(
            "artifacts_directory",
            check_artifacts_dir,
            dependency_node="artifacts"   # node named "artifacts"
        )
        health_coordinator.register(
            "memory_pressure",
            check_memory,
            dependency_node=None          # no node mapping; purely informational
        )

        # ── Step 6: Capability Model (P0-4) with graph sync ──────────────────────
        if cfg11.get("enable_capability_model", True):
            capabilities = coordinator.capabilities
            # Initial sync with the graph
            capabilities.sync_with_graph(dep_graph)
            logger.info("capability_model_active", capabilities=capabilities.snapshot())

        # ── Step 7: Start RuntimeScheduler (P1-2) with health coordinator task ──
        if cfg11.get("enable_scheduler", True):
            scheduler = RuntimeScheduler(tick_interval=1.0)
            sched_cfg = config.get("runtime", {}).get("scheduler", {})
            # Register a task that runs the health coordinator's checks
            scheduler.register(
                "health_check",
                interval_seconds=sched_cfg.get("tasks", {}).get("health_check", {}).get("interval_seconds", 30.0),
                task=lambda: health_coordinator.run_all(),  # runs checks and updates graph
            )
            # Optionally register a task to sync capabilities from the graph
            scheduler.register(
                "capability_sync",
                interval_seconds=60.0,
                task=lambda: capabilities.sync_with_graph(dep_graph),
            )
            coordinator._shutdown.register(
                "scheduler_stop",
                handler=scheduler.stop,
                priority=10,
            )
            scheduler.start()

        # ── Step 8: Assert invariants ─────────────────────────────────────────────
        if config.get("runtime", {}).get("assert_invariants_on_startup", True):
            try:
                assert_all_invariants()
            except Exception as exc:
                logger.error("invariant_assertion_failed", error=str(exc))

        # ── Step 9: Write RuntimeManifest with architecture version (P1-5) ────────
        if config.get("runtime", {}).get("write_runtime_manifest", True):
            cfg_ctx = coordinator.config_context
            # Compute ADR set version from accepted ADRs
            from smriti.governance.adr import ADRRegistry
            adr_registry = ADRRegistry()
            accepted_ids = "|".join(sorted(a.adr_id for a in adr_registry.all_accepted()))
            adr_version = hashlib.sha256(accepted_ids.encode()).hexdigest()[:8]

            builder = (
                ProvenanceBuilder(run_id=self.run_id)
                .set_config_version(cfg_ctx.config_hash if cfg_ctx else "unknown")
                .set_schema_version("1.0")
                .set_knowledge_version(self.run_id)
                .set_architecture_version("11.0")
                .set_adr_set_version(adr_version)
                .set_compliance_rule_version("1.0")
                .set_invariant_version("1.0")
            )
            manifest = builder.build()
            manifest.write_artifact(ARTIFACTS_DIR)

        # ── Step 10: Register shutdown handler ──────────────────────────────────
        coordinator._shutdown.register(
            name="pipeline_runner_shutdown",
            handler=lambda: logger.info("pipeline_runner_shutdown_handler_called"),
            priority=90,
        )

        self.state_manager.complete_phase(phase=11)
        logger.info("phase 11 complete", run_id=self.run_id)  

    def _run_phase_12(self, knowledge_api) -> "CertificationReport":
        from smriti.evaluation import run_evaluation
        from smriti.reporting.exporter import write_certification_artifacts, export_text_summary
        from smriti.core.paths import ARTIFACTS_DIR

        logger.info("running phase 12 — scientific validation framework (gate-based)")
        report = run_evaluation(
            knowledge_api=knowledge_api,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        artifacts_dir = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase12"
        write_certification_artifacts(report, artifacts_dir)
        logger.info("phase 12 complete",
                    certification_level=report.certification_level.name,
                    pub_readiness=report.publication_readiness.readiness_level.value)
        print(export_text_summary(report))
        return report    