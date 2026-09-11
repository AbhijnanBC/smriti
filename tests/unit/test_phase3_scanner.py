"""
Unit tests for extraction/scanner.py.
The scanner has one job: identify structural events.
These tests never touch context, segmentation, or building.
"""

from smriti.extraction.scanner import BlockType, scan_document


def test_empty_document_returns_empty():
    """Empty text must return [] — not crash."""
    assert scan_document("") == []
    assert scan_document("   \n\n   ") == []


def test_atx_heading_detected():
    """# Title must be detected as HEADING level 1."""
    events = scan_document("# Hello World")
    headings = [e for e in events if e.block_type == BlockType.HEADING]
    assert len(headings) == 1
    assert headings[0].heading_level == 1
    assert headings[0].text == "Hello World"


def test_h2_heading_level():
    """## Subtitle must be HEADING level 2."""
    events = scan_document("## Subtitle")
    headings = [e for e in events if e.block_type == BlockType.HEADING]
    assert headings[0].heading_level == 2


def test_paragraph_detected():
    """Plain prose must be detected as PARAGRAPH."""
    events = scan_document("Python is the best language for data science.")
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert len(paragraphs) == 1


def test_bullet_item_detected():
    """'- item' must be detected as BULLET_ITEM."""
    events = scan_document("- This is a list item")
    bullets = [e for e in events if e.block_type == BlockType.BULLET_ITEM]
    assert len(bullets) == 1
    assert bullets[0].text == "This is a list item"


def test_ordered_item_detected():
    """'1. item' must be detected as ORDERED_ITEM."""
    events = scan_document("1. Install dependencies")
    ordered = [e for e in events if e.block_type == BlockType.ORDERED_ITEM]
    assert len(ordered) == 1
    assert ordered[0].text == "Install dependencies"


def test_block_quote_detected():
    """> quote must be detected as BLOCK_QUOTE."""
    events = scan_document("> Reliability is critical.")
    quotes = [e for e in events if e.block_type == BlockType.BLOCK_QUOTE]
    assert len(quotes) == 1
    assert quotes[0].text == "Reliability is critical."


def test_fenced_code_block_detected():
    """```code``` must be detected as CODE_BLOCK."""
    text = "```python\nprint('hello')\n```"
    events = scan_document(text)
    code = [e for e in events if e.block_type == BlockType.CODE_BLOCK]
    assert len(code) == 1


def test_table_detected():
    """Markdown table must be detected as TABLE."""
    text = "| Model | Accuracy |\n|-------|----------|\n| GPT-4 | 85% |"
    events = scan_document(text)
    tables = [e for e in events if e.block_type == BlockType.TABLE]
    assert len(tables) == 1


def test_heading_not_in_paragraph():
    """A heading must NOT be a PARAGRAPH event."""
    events = scan_document("# Title\n\nSome text.")
    types = [e.block_type for e in events]
    assert BlockType.HEADING in types
    assert BlockType.PARAGRAPH in types
    # The heading text must not appear in a paragraph event
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert not any("Title" in p.text for p in paragraphs)


def test_events_are_in_document_order():
    """Events must appear in the same order as the document."""
    text = "# H1\n\nParagraph.\n\n- item\n\n## H2"
    events = scan_document(text)
    # H1 heading must come before paragraph, paragraph before bullet
    h1_idx = next(
        i
        for i, e in enumerate(events)
        if e.block_type == BlockType.HEADING and e.heading_level == 1
    )
    para_idx = next(i for i, e in enumerate(events) if e.block_type == BlockType.PARAGRAPH)
    bullet_idx = next(i for i, e in enumerate(events) if e.block_type == BlockType.BULLET_ITEM)
    assert h1_idx < para_idx < bullet_idx


def test_code_does_not_contaminate_paragraph():
    """Text inside a code block must not become a PARAGRAPH event."""
    text = "Before.\n\n```\nsome code\n```\n\nAfter."
    events = scan_document(text)
    paragraphs = [e for e in events if e.block_type == BlockType.PARAGRAPH]
    assert not any("some code" in p.text for p in paragraphs)


def test_horizontal_rule_detected():
    """--- must be detected as HORIZONTAL_RULE."""
    events = scan_document("---")
    hr = [e for e in events if e.block_type == BlockType.HORIZONTAL_RULE]
    assert len(hr) == 1


def test_multiple_bullet_items():
    """Three bullet items must produce three BULLET_ITEM events."""
    text = "- First\n- Second\n- Third"
    events = scan_document(text)
    bullets = [e for e in events if e.block_type == BlockType.BULLET_ITEM]
    assert len(bullets) == 3


def test_mixed_content():
    """Complex document with mixed structure produces correct event count."""
    text = """# Title

Introduction paragraph.

## Section

- item one
- item two

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    events = scan_document(text)
    types = [e.block_type for e in events]
    assert BlockType.HEADING in types
    assert BlockType.PARAGRAPH in types
    assert BlockType.BULLET_ITEM in types
    assert BlockType.TABLE in types
