"""
Unit tests for claims/classifier.py — AssertionClassifier.

Verifies that SemanticSentences are routed into the correct AssertionType
BEFORE any Claim is ever constructed. Only DECLARATIVE_ASSERTION is meant to
proceed into claim construction; every other category must be classified
correctly so it can be recorded as a DiscardedCandidate instead.
"""

from pathlib import Path

import pytest
from smriti.claims.classifier import AssertionClassifier
from smriti.claims.models import ParsedSentence
from smriti.claims.parser import SpaCyParser
from smriti.core.models import AssertionType, SemanticSentence


@pytest.fixture(scope="module")
def parser():
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def classifier():
    return AssertionClassifier()


def make_sentence(
    text: str,
    origin_block_type: str = "paragraph",
    sentence_id: str = "s001",
) -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("note.md"),
        origin_block_type=origin_block_type,
        schema_version="3.0",
    )


def classify(parser, classifier, text, origin_block_type="paragraph"):
    sentence = make_sentence(text, origin_block_type=origin_block_type)
    parsed = parser.parse(sentence)
    return classifier.classify(sentence, parsed)


# ── DECLARATIVE_ASSERTION ─────────────────────────────────────────────────────


def test_simple_declarative_assertion(parser, classifier):
    """'Earth orbits the Sun.' -- the canonical positive example."""
    result_type, _ = classify(parser, classifier, "Earth orbits the Sun.")
    assert result_type == AssertionType.DECLARATIVE_ASSERTION


def test_negated_declarative_assertion(parser, classifier):
    result_type, _ = classify(parser, classifier, "Python does not support this feature.")
    assert result_type == AssertionType.DECLARATIVE_ASSERTION


def test_attributed_declarative_assertion(parser, classifier):
    result_type, _ = classify(
        parser,
        classifier,
        "According to the authors, transformers are now state-of-the-art.",
    )
    assert result_type == AssertionType.DECLARATIVE_ASSERTION


def test_passive_assertion_survives_hyphen_tokenization_quirk(parser, classifier):
    """
    Regression test: spaCy's small English model sometimes splits a
    hyphenated passive participle ("pre-trained") into three tokens
    ("pre" / "-" / "trained") and makes "pre" the ROOT, detaching the real
    subject ("transformers", attached to the auxiliary "be" instead of the
    ROOT). This is still a genuine declarative assertion and must not be
    misclassified as FRAGMENT just because the subject isn't a direct child
    of ROOT.
    """
    text = (
        "Moreover, transformers can be pre-trained on large natural image "
        "datasets and fine-tuned for specific tasks."
    )
    result_type, _ = classify(parser, classifier, text)
    assert result_type == AssertionType.DECLARATIVE_ASSERTION


# ── PROCEDURAL_INSTRUCTION ────────────────────────────────────────────────────


def test_imperative_instruction(parser, classifier):
    """'Heat the oil in a pan.' -- the canonical procedural example."""
    result_type, reason = classify(parser, classifier, "Heat the oil in a pan.")
    assert result_type == AssertionType.PROCEDURAL_INSTRUCTION
    assert "imperative" in reason


def test_another_imperative_instruction(parser, classifier):
    result_type, _ = classify(parser, classifier, "Mix the flour and sugar together.")
    assert result_type == AssertionType.PROCEDURAL_INSTRUCTION


# ── QUESTION ───────────────────────────────────────────────────────────────


def test_question_mark_is_question(parser, classifier):
    result_type, _ = classify(parser, classifier, "What temperature should the oven be?")
    assert result_type == AssertionType.QUESTION


def test_simple_question(parser, classifier):
    result_type, _ = classify(parser, classifier, "Is Python faster than Java?")
    assert result_type == AssertionType.QUESTION


# ── HEADING ────────────────────────────────────────────────────────────────


def test_bare_atx_heading_leak(parser, classifier):
    """'## Ingredients' -- literal example from the annotation review."""
    result_type, reason = classify(parser, classifier, "## Ingredients")
    assert result_type == AssertionType.HEADING
    assert reason == "regex_atx_heading_leak"


def test_bare_bold_heading(parser, classifier):
    """'**Ingredients**' with no colon reads as a bare section title."""
    result_type, _ = classify(parser, classifier, "**Ingredients**")
    assert result_type == AssertionType.HEADING


def test_gerund_phrase_heading(parser, classifier):
    """A bare gerund phrase with no subject reads as a section title."""
    result_type, _ = classify(parser, classifier, "Preparing the Dough")
    assert result_type == AssertionType.HEADING


def test_titlecase_noun_phrase_heading(parser, classifier):
    result_type, _ = classify(parser, classifier, "Weekly Meal Plan")
    assert result_type == AssertionType.HEADING


# ── METADATA ───────────────────────────────────────────────────────────────


def test_source_metadata_line(parser, classifier):
    """'**Source:** Flavor Quotient' -- literal example from the annotation review."""
    result_type, reason = classify(parser, classifier, "**Source:** Flavor Quotient")
    assert result_type == AssertionType.METADATA
    assert reason == "regex_bold_label_colon"


def test_contradicts_metadata_line(parser, classifier):
    result_type, _ = classify(parser, classifier, "**Contradicts:** Some other claim about eggs.")
    assert result_type == AssertionType.METADATA


# ── LIST_ITEM ──────────────────────────────────────────────────────────────


def test_bare_noun_phrase_list_item(parser, classifier):
    """'Coconut oil.' -- literal example from the annotation review."""
    result_type, reason = classify(
        parser, classifier, "Coconut oil.", origin_block_type="bullet_item"
    )
    assert result_type == AssertionType.LIST_ITEM
    assert reason == "no_verb_root_list_item_block"


def test_quantity_list_item(parser, classifier):
    result_type, _ = classify(parser, classifier, "2 tbsp ghee", origin_block_type="bullet_item")
    assert result_type == AssertionType.LIST_ITEM


def test_ordered_list_item(parser, classifier):
    result_type, _ = classify(
        parser, classifier, "Fresh coriander leaves.", origin_block_type="ordered_item"
    )
    assert result_type == AssertionType.LIST_ITEM


# ── TABLE_CELL ─────────────────────────────────────────────────────────────


def test_table_origin_is_table_cell(parser, classifier):
    """Any sentence whose origin_block_type is 'table' is TABLE_CELL,
    regardless of its textual content."""
    result_type, reason = classify(
        parser, classifier, "Model: GPT-4. Accuracy: 85%.", origin_block_type="table"
    )
    assert result_type == AssertionType.TABLE_CELL
    assert reason == "origin_block_type_table"


def test_table_cell_overrides_metadata_pattern(parser, classifier):
    """origin_block_type=table wins even if the text also looks metadata-like."""
    result_type, _ = classify(parser, classifier, "**Source:** GPT-4.", origin_block_type="table")
    assert result_type == AssertionType.TABLE_CELL


# ── QUOTE ──────────────────────────────────────────────────────────────────


def test_block_quote_origin_is_quote(parser, classifier):
    result_type, reason = classify(
        parser, classifier, "This changes everything.", origin_block_type="block_quote"
    )
    assert result_type == AssertionType.QUOTE
    assert reason == "origin_block_type_block_quote"


# ── CODE ───────────────────────────────────────────────────────────────────


def test_code_block_origin_is_code(parser, classifier):
    result_type, reason = classify(parser, classifier, "print(x)", origin_block_type="code_block")
    assert result_type == AssertionType.CODE
    assert reason == "origin_block_type_code_block"


# ── FRAGMENT ───────────────────────────────────────────────────────────────


def test_parse_failure_is_fragment(parser, classifier):
    """When spaCy could not parse the sentence at all, classify as FRAGMENT."""
    sentence = make_sentence("some garbled text")
    fake_parsed = ParsedSentence(
        sentence=sentence, spacy_doc=None, parse_ok=False, parse_error="boom"
    )
    result_type, reason = classifier.classify(sentence, fake_parsed)
    assert result_type == AssertionType.FRAGMENT
    assert reason == "parse_failed"


def test_empty_text_is_fragment(parser, classifier):
    result_type, reason = classify(parser, classifier, "   ")
    assert result_type == AssertionType.FRAGMENT


# ── Never raises ─────────────────────────────────────────────────────────────


def test_classify_never_raises_on_odd_input(parser, classifier):
    for text in ["@@@ ### ??? weird !!!", "", "a", "1234567890"]:
        sentence = make_sentence(text if text else " ")
        parsed = parser.parse(sentence)
        result_type, reason = classifier.classify(sentence, parsed)
        assert isinstance(result_type, AssertionType)
        assert isinstance(reason, str) and reason
