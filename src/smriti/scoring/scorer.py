"""scorer.py — Phase 8 entry point. Delegates to scoring/__init__.py."""

from smriti.scoring import ScoredKnowledgeGraph, score_knowledge_graph

__all__ = ["score_knowledge_graph", "ScoredKnowledgeGraph"]
