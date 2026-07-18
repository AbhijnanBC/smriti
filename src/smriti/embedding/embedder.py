"""
embedder.py — Abstract embedding interface, capability metadata, and V1 implementation.

Responsibility:
    Define EmbedderCapabilities — so the pipeline can adapt without inspecting model names.
    Define BaseEmbedder — the stable interface that shields the pipeline from frameworks.
    Provide SentenceTransformerEmbedder — the V1 implementation.

Architecture rules:
    ✅ BaseEmbedder exposes only Python native types (List[str], List[List[float]])
    ✅ EmbedderCapabilities lets the pipeline ask "can you do X?" instead of "are you model Y?"
    ✅ SentenceTransformerEmbedder is the ONLY module that imports sentence-transformers
    ✅ torch.Tensor is converted to List[float] before leaving this module
    ✅ EmbeddingModelDescriptor is constructed here and exposed to the pipeline

    ❌ No torch.Tensor, np.ndarray, or model objects ever leave this module
    ❌ No normalization inside the embedder (that belongs to normalization.py)
    ❌ No caching inside the embedder (that belongs to cache.py)
    ❌ Pipeline never branches on model name — it queries capabilities instead
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import structlog

from smriti.core.config import get_config
from smriti.core.models import EmbeddingModelDescriptor
from smriti.exceptions import EmbeddingModelError, EmbeddingInferenceError

logger = structlog.get_logger(__name__)

# Phase 5 pipeline version — increment when pipeline logic changes
PHASE5_PIPELINE_VERSION = "1.0"
PHASE5_SCHEMA_VERSION = "5.0"


def _compute_model_signature(provider: str, model_name: str, revision: str) -> str:
    """Deterministic model signature for cache key generation."""
    material = f"{provider}:{model_name}:{revision}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class EmbedderCapabilities:
    """
    Runtime capabilities advertised by an embedder implementation.

    The pipeline queries capabilities instead of branching on model name.
    This makes the pipeline unconditionally open for extension.

    Fields:
        supports_batching:           True if encode_batch() is more efficient than
                                     repeated single-item calls.
        supports_instruction_prefix: True if the model benefits from task-specific
                                     prefixes (BGE, Instructor, E5).
        supports_multilingual:       True if the model handles non-English text well.
        supports_long_context:       True if the model handles sequences > 512 tokens
                                     without truncation loss.
    """
    supports_batching: bool
    supports_instruction_prefix: bool
    supports_multilingual: bool
    supports_long_context: bool


class BaseEmbedder(ABC):
    """
    Abstract interface for all embedding backends.

    Contract:
        - encode_batch() accepts plain Python strings
        - encode_batch() returns plain Python float lists
        - descriptor() returns an EmbeddingModelDescriptor
        - capabilities() returns an EmbedderCapabilities
        - No framework types ever cross this interface

    Adding a new embedder = subclass BaseEmbedder.
    The pipeline never changes.
    """

    @property
    @abstractmethod
    def descriptor(self) -> EmbeddingModelDescriptor:
        """Return the model descriptor for this embedder."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> EmbedderCapabilities:
        """Return the capability metadata for this embedder."""
        ...

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a batch of text strings into embedding vectors.

        Args:
            texts: List of strings to encode (payload strings, not Claim objects).

        Returns:
            List of float lists, one per input text.
            All vectors must have the same dimension == descriptor.dimension.

        Raises:
            EmbeddingInferenceError: If encoding fails.
        """
        ...


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    V1 embedding backend using sentence-transformers.

    Default model: sentence-transformers/all-MiniLM-L6-v2
        - 384-dimensional embeddings
        - CPU-runnable without GPU
        - ~80MB model size
        - Strong general-purpose semantic similarity
        - Supports batching efficiently

    Design:
        - Model loaded once at construction time (eager loading)
        - encode_batch converts torch.Tensor → List[List[float]] before returning
        - No normalization performed here (normalization.py handles that)
        - No caching performed here (cache.py handles that)
        - capabilities() advertises what this model supports
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        config = get_config()
        emb_cfg = config.get("embedding", {})

        self._model_name = model_name or emb_cfg.get(
            "model_name", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._device = device or emb_cfg.get("device", "cpu")

        self._model = self._load_model()
        self._descriptor = self._build_descriptor()

        logger.info(
            "embedding model loaded",
            model=self._model_name,
            device=self._device,
            dimension=self._descriptor.dimension,
            family=self._descriptor.embedding_family,
        )

    def _load_model(self):
        """Load the sentence-transformers model. Raises EmbeddingModelError on failure."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(self._model_name, device=self._device)
            return model
        except ImportError as e:
            raise EmbeddingModelError(
                f"sentence-transformers is not installed. "
                f"Run: poetry add sentence-transformers\nError: {e}"
            ) from e
        except Exception as e:
            raise EmbeddingModelError(
                f"Failed to load embedding model '{self._model_name}': {e}"
            ) from e

    def _build_descriptor(self) -> EmbeddingModelDescriptor:
        """Build the model descriptor after model is loaded."""
        try:
            test_embedding = self._model.encode(["test"], convert_to_numpy=True)
            dimension = test_embedding.shape[1]
        except Exception:
            dimension = 384  # MiniLM default fallback

        revision = "default"  # sentence-transformers doesn't expose git revision easily

        return EmbeddingModelDescriptor(
            provider="sentence-transformers",
            model_name=self._model_name,
            model_revision=revision,
            dimension=dimension,
            model_signature=_compute_model_signature(
                "sentence-transformers", self._model_name, revision
            ),
            embedding_family="SentenceTransformer",
            checkpoint_sha="",  # Not available from sentence-transformers API
        )

    @property
    def descriptor(self) -> EmbeddingModelDescriptor:
        return self._descriptor

    @property
    def capabilities(self) -> EmbedderCapabilities:
        """
        MiniLM capabilities:
            - Supports batching (very efficiently)
            - Does NOT benefit from instruction prefixes (standard model)
            - Limited multilingual support (primarily English)
            - Short context only (256 token practical limit)
        """
        return EmbedderCapabilities(
            supports_batching=True,
            supports_instruction_prefix=False,
            supports_multilingual=False,
            supports_long_context=False,
        )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a batch of texts into embedding vectors.

        Args:
            texts: Non-empty list of non-empty strings.

        Returns:
            List of float lists. One vector per text.
            Vectors are RAW (unnormalized) — normalization.py handles that.

        Raises:
            EmbeddingInferenceError: If encoding fails.
        """
        if not texts:
            return []

        try:
            embeddings_np = self._model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=False,  # normalization is our responsibility
            )
            return embeddings_np.tolist()
        except Exception as e:
            raise EmbeddingInferenceError(
                f"Batch encoding failed for {len(texts)} texts: {e}"
            ) from e