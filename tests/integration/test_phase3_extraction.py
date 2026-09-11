"""
Integration test for Phase 3 end-to-end.

Tests the complete pipeline:
  Document → build_semantic_sentences() → List[SemanticSentence]

Uses Documents with realistic note content.
"""

from datetime import UTC, datetime
from pathlib import Path

from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    SourceDocument,
    TextStatistics,
)
from smriti.extraction import build_semantic_sentences
from smriti.extraction.scanner import BlockType


def make_document(doc_id: str, normalized_text: str, path_str: str = "note.md") -> Document:
    """Create a test Document from normalized_text."""
    source = SourceDocument(
        doc_id=doc_id,
        path=Path(path_str),
        relative_path=Path(path_str),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash=doc_id,
        size_bytes=len(normalized_text),
        modified_at=datetime.now(tz=UTC),
    )
    stats = TextStatistics(
        character_count=len(normalized_text),
        word_count=len(normalized_text.split()),
        line_count=normalized_text.count("\n"),
        blank_line_count=0,
        paragraph_count=1,
    )
    return Document(
        doc_id=doc_id,
        source_document=source,
        raw_text=normalized_text,
        normalized_text=normalized_text,
        extraction_method=ExtractionMethod.MARKDOWN,
        extraction_warnings=(),
        text_statistics=stats,
        encoding_used="utf-8",
    )


# ── Basic sentence production ─────────────────────────────────────────────────


def test_simple_paragraph_produces_sentences():
    doc = make_document(
        "doc1", "Python is great for data science. Julia is faster for numerical computing."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 2
    assert result.error is None


def test_empty_document_produces_no_sentences():
    doc = make_document("doc2", "")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 0
    assert result.error is None


def test_sentences_have_correct_document_id():
    doc = make_document("myid123", "Python is great.")
    result = build_semantic_sentences(doc)
    assert all(s.document_id == "myid123" for s in result.sentences)


# ── Context preservation ──────────────────────────────────────────────────────


def test_context_captured_from_heading():
    doc = make_document("doc3", "# Python\n\nPython is great for data science.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1
    sentence = result.sentences[0]
    assert "Python" in sentence.context


def test_nested_context():
    doc = make_document("doc4", "# Programming\n\n## Python\n\nPython is great.")
    result = build_semantic_sentences(doc)
    sentence = result.sentences[0]
    assert "Programming" in sentence.context
    assert "Python" in sentence.context


def test_heading_is_not_a_sentence():
    doc = make_document("doc5", "# This Is A Heading\n\nActual sentence here.")
    result = build_semantic_sentences(doc)
    sentence_texts = [s.text for s in result.sentences]
    assert not any("This Is A Heading" in t for t in sentence_texts)


def test_context_resets_at_new_h1():
    doc = make_document("doc6", "# Section A\n\nSentence in A.\n\n# Section B\n\nSentence in B.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 2
    assert "Section A" in result.sentences[0].context
    assert "Section B" in result.sentences[1].context
    assert "Section A" not in result.sentences[1].context


# ── Structural elements ───────────────────────────────────────────────────────


def test_bullet_items_become_sentences():
    doc = make_document("doc7", "- First item\n- Second item\n- Third item")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_ordered_list_becomes_sentences():
    doc = make_document("doc8", "1. Install Poetry\n2. Install dependencies\n3. Run tests")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_block_quote_becomes_sentence():
    doc = make_document("doc9", "> Reliability is critical.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1
    assert "Reliability" in result.sentences[0].text


def test_code_block_produces_no_sentences():
    doc = make_document("doc10", "Before code.\n\n```python\nprint('hello')\n```\n\nAfter code.")
    result = build_semantic_sentences(doc)
    texts = [s.text for s in result.sentences]
    assert not any("print" in t for t in texts)


def test_table_produces_prose_sentences():
    doc = make_document("doc11", "| Model | Accuracy |\n|-------|----------|\n| GPT-4 | 85% |")
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1


# ── Determinism ───────────────────────────────────────────────────────────────


def test_same_document_same_sentence_ids():
    doc = make_document(
        "doc12", "# AI\n\nAI is transforming everything. Machine learning is a subset of AI."
    )
    result1 = build_semantic_sentences(doc)
    result2 = build_semantic_sentences(doc)

    ids1 = [s.sentence_id for s in result1.sentences]
    ids2 = [s.sentence_id for s in result2.sentences]
    assert ids1 == ids2


def test_positions_are_strictly_increasing():
    doc = make_document("doc13", "First. Second. Third. Fourth.")
    result = build_semantic_sentences(doc)
    positions = [s.position for s in result.sentences]
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))


def test_sentence_ids_are_unique():
    doc = make_document(
        "doc14", "# Section\n\nSentence A. Sentence B. Sentence C.\n\n## Sub\n\nSentence D."
    )
    result = build_semantic_sentences(doc)
    ids = [s.sentence_id for s in result.sentences]
    assert len(ids) == len(set(ids))


# ── Context separation ────────────────────────────────────────────────────────


def test_context_never_fused_into_text():
    doc = make_document("doc15", "# CUDA\n\nSupports tensors.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1
    sentence = result.sentences[0]
    assert sentence.text == "Supports tensors."
    assert "CUDA" in sentence.context
    assert "CUDA" not in sentence.text


# ── Abbreviation handling ─────────────────────────────────────────────────────


def test_abbreviation_dr_not_split():
    doc = make_document("doc16", "Dr. Smith discovered this principle.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1


def test_decimal_not_split():
    doc = make_document("doc17", "Pi equals approximately 3.14 in most calculations.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1


# ── NEW: Check origin_block_type and schema_version ──────────────────────────


def test_sentences_have_origin_block_type():
    """Each SemanticSentence must record its origin block type."""
    doc = make_document("doc18", "- First bullet\n\n> A quote.\n\nPlain paragraph.")
    result = build_semantic_sentences(doc)

    # The order of events from scanner: bullet_item, block_quote, paragraph
    # (depending on how the scanner processes)
    # We'll check that each sentence's origin_block_type is set correctly.
    origins = [s.origin_block_type for s in result.sentences]
    assert BlockType.BULLET_ITEM in origins
    assert BlockType.BLOCK_QUOTE in origins
    assert BlockType.PARAGRAPH in origins
    # SemanticSentence.origin_block_type is documented (core/models.py) as
    # "BlockType that produced this sentence (stored as string)" — builder.py
    # explicitly stores origin_block_type.value, a plain str, not the enum
    # instance, so the field round-trips cleanly through JSON. BlockType is a
    # str Enum, so equality/membership checks above still work; isinstance
    # against BlockType would not.
    assert all(isinstance(o, str) for o in origins)
    assert all(o in set(BlockType) for o in origins)


def test_sentences_have_schema_version():
    """Every SemanticSentence must carry schema_version='3.0'."""
    doc = make_document("doc19", "Simple text.")
    result = build_semantic_sentences(doc)
    for s in result.sentences:
        assert s.schema_version == "3.0"


# ── Realistic vault note ──────────────────────────────────────────────────────


def test_realistic_obsidian_note():
    note = """# Machine Learning

## Supervised Learning

Supervised learning uses labeled training data. The model learns to map inputs to outputs.

Key algorithms:
- Linear Regression
- Decision Trees
- Random Forests

## Unsupervised Learning

Unsupervised learning finds patterns without labeled data. Clustering is the most common technique.

> The choice of algorithm depends heavily on the data structure.

| Algorithm | Use Case     |
|-----------|--------------|
| K-Means   | Clustering   |
| PCA       | Dimensionality |
"""
    doc = make_document("realistic", note)
    result = build_semantic_sentences(doc)

    assert result.sentence_count > 0
    assert result.error is None
    assert all(s.document_id == "realistic" for s in result.sentences)
    contexts = [s.context for s in result.sentences]
    assert any("Machine Learning" in c for c in contexts)
    assert any("Supervised" in c for c in contexts)
    positions = [s.position for s in result.sentences]
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))
    ids = [s.sentence_id for s in result.sentences]
    assert len(ids) == len(set(ids))
