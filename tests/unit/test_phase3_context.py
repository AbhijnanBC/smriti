"""
Unit tests for extraction/context.py.
"""

import pytest
from smriti.extraction.context import ContextStack


def test_empty_stack_returns_empty_context():
    stack = ContextStack()
    assert stack.current_context() == ""


def test_push_one_heading():
    stack = ContextStack()
    stack.push("Python", level=1)
    assert stack.current_context() == "Python"


def test_push_nested_headings():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    assert stack.current_context() == "Python > Generators"


def test_push_deeper_nesting():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Yield", level=3)
    assert stack.current_context() == "Python > Generators > Yield"


def test_same_level_heading_replaces():
    """A new H2 heading replaces the previous H2."""
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Decorators", level=2)  # Replaces Generators
    assert stack.current_context() == "Python > Decorators"


def test_shallower_heading_pops_deeper():
    """A new H1 heading pops H2 and H3."""
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.push("Advanced", level=1)  # Should pop Generators then push Advanced
    assert stack.current_context() == "Advanced"


def test_clear_resets_stack():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    stack.clear()
    assert stack.current_context() == ""
    assert stack.depth() == 0


def test_depth_tracking():
    stack = ContextStack()
    assert stack.depth() == 0
    stack.push("A", level=1)
    assert stack.depth() == 1
    stack.push("B", level=2)
    assert stack.depth() == 2
    stack.push("C", level=1)  # Replaces A and B
    assert stack.depth() == 1


def test_peek_returns_top_heading():
    stack = ContextStack()
    stack.push("Python", level=1)
    stack.push("Generators", level=2)
    assert stack.peek() == "Generators"


def test_peek_empty_returns_none():
    stack = ContextStack()
    assert stack.peek() is None


def test_context_separator_is_correct():
    stack = ContextStack()
    stack.push("A", level=1)
    stack.push("B", level=2)
    assert " > " in stack.current_context()