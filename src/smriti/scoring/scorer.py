"""scorer.py — Phase 8 entry point. Delegates to scoring/__init__.py."""
from smriti.scoring import score_knowledge_graph, ScoredKnowledgeGraph
__all__ = ["score_knowledge_graph", "ScoredKnowledgeGraph"]