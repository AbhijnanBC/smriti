"""
parser.py — Deterministic linguistic analysis wrapper for Phase 4.
Now uses a pluggable parser abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import structlog

from smriti.claims.models import ParsedSentence
from smriti.core.config import get_config
from smriti.core.models import SemanticSentence
from smriti.exceptions import SpacyNotLoadedError

logger = structlog.get_logger(__name__)


@dataclass
class ParserCapabilities:
    """Defines the supported features of the underlying linguistic parser."""

    supports_svo: bool
    supports_negation: bool
    supports_modality: bool
    supports_dependencies: bool


class BaseParser(ABC):
    """Abstract interface for linguistic parsers."""

    @property
    @abstractmethod
    def capabilities(self) -> ParserCapabilities:
        """Return the capabilities supported by this parser."""
        ...

    @abstractmethod
    def parse(self, sentence: SemanticSentence) -> ParsedSentence:
        """Parse a SemanticSentence into a ParsedSentence."""
        ...


class SpaCyParser(BaseParser):
    """spaCy-based implementation of the linguistic parser."""

    def __init__(self, model_name: str | None = None) -> None:
        if model_name is None:
            config = get_config()
            model_name = config.get("extraction", {}).get("spacy_model", "en_core_web_sm")
        self._model_name = model_name
        self._nlp = self._load_model()

    @property
    def capabilities(self) -> ParserCapabilities:
        """spaCy supports full dependency parsing and structural extraction."""
        return ParserCapabilities(
            supports_svo=True,
            supports_negation=True,
            supports_modality=True,
            supports_dependencies=True,
        )

    def _load_model(self):
        try:
            import spacy

            return spacy.load(self._model_name)
        except OSError as e:
            raise SpacyNotLoadedError(
                f"spaCy model '{self._model_name}' not found. "
                f"Run: poetry run python -m spacy download {self._model_name}\n"
                f"Error: {e}"
            ) from e
        except ImportError as e:
            raise SpacyNotLoadedError(
                f"spaCy is not installed. Run: poetry add spacy\nError: {e}"
            ) from e

    def parse(self, sentence: SemanticSentence) -> ParsedSentence:
        """
        Parse a SemanticSentence using spaCy.

        Args:
            sentence: SemanticSentence from Phase 3.

        Returns:
            ParsedSentence with spacy_doc populated if parse succeeded,
            or with parse_ok=False and parse_error set if it failed.
            NEVER raises — failures are captured in the result.
        """
        text = sentence.text

        if not text or not text.strip():
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=None,
                parse_ok=False,
                parse_error="Empty sentence text",
            )

        try:
            doc = self._nlp(text)
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=doc,
                parse_ok=True,
            )
        except Exception as e:
            logger.warning(
                "spacy parse failed",
                sentence_id=sentence.sentence_id[:8],
                text=text[:50],
                error=str(e),
            )
            return ParsedSentence(
                sentence=sentence,
                spacy_doc=None,
                parse_ok=False,
                parse_error=str(e),
            )
