"""Standalone baseline systems for SMRITI's research paper comparisons.

These baselines are deliberately independent of SMRITI's Phase 2-6
dataclasses, provenance model, and PipelineRunner. Each one takes raw text
in (markdown documents, or a flat list of claim texts) and returns plain
Python lists of dicts out, so they can be run, inspected, and later scored
against gold labels without touching the main pipeline.

- naive_extraction.extract_claims_naive: claim extraction strawman.
- tfidf_relations.predict_relationships_tfidf: TF-IDF cosine relationship baseline.
- sbert_relations.predict_relationships_sbert: Sentence-BERT cosine relationship baseline.
"""

from smriti.baselines.naive_extraction import extract_claims_naive
from smriti.baselines.sbert_relations import predict_relationships_sbert
from smriti.baselines.tfidf_relations import predict_relationships_tfidf

__all__ = [
    "extract_claims_naive",
    "predict_relationships_tfidf",
    "predict_relationships_sbert",
]
