"""
models.py — Export data models for Phase 10.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExportResult:
    """Result of a successful export operation."""
    content: str
    mime_type: str
    filename: str
    format: str
    byte_size: int