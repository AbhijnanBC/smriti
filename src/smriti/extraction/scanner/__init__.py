"""
scanner/__init__.py — Public interface for the structural scanner.

Exports scan_document and the BlockType enum.
"""

from smriti.extraction.scanner.scanner import BlockType, ScannerEvent, scan_document

__all__ = ["scan_document", "BlockType", "ScannerEvent"]
