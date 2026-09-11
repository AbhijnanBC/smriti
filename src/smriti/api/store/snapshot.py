from dataclasses import dataclass

from smriti.api.cache.knowledge_cache import KnowledgeViewCache
from smriti.api.dtos.schema_registry import SchemaRegistry
from smriti.api.index.registry import IndexRegistry
from smriti.api.store.read_store import ReadStore


@dataclass(frozen=True)
class KnowledgeSnapshot:
    """A cohesive, immutable view of the data layer for a specific run."""

    store: ReadStore
    index_registry: IndexRegistry
    cache: KnowledgeViewCache
    schema_registry: SchemaRegistry
    run_id: str
