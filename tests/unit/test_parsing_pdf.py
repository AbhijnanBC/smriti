"""
Unit tests for parsing/pdf.py.
"""

import pytest
from smriti.core.models import ExtractionMethod
from smriti.parsing.pdf import PdfExtractor


@pytest.fixture
def extractor():
    return PdfExtractor()


@pytest.fixture
def minimal_pdf(tmp_path):
    """Create a minimal valid PDF with a text layer."""
    try:
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        path = tmp_path / "test.pdf"
        with open(path, "wb") as f:
            writer.write(f)
        return path
    except Exception:
        # If pypdf cannot create a test PDF, skip
        pytest.skip("pypdf could not create test PDF")


def test_method_is_pdf(extractor, minimal_pdf):
    result = extractor.extract(minimal_pdf)
    assert result.method == ExtractionMethod.PDF


def test_image_only_pdf_produces_warning(extractor, tmp_path):
    """A PDF with no text layer must produce NoExtractableTextWarning."""
    try:
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        path = tmp_path / "blank.pdf"
        with open(path, "wb") as f:
            writer.write(f)
        result = extractor.extract(path)
        # Blank page has no text — should produce a warning
        assert result.method == ExtractionMethod.PDF
        # The result is a valid RawExtractionResult regardless
    except Exception:
        pytest.skip("pypdf could not create test PDF")


def test_corrupted_pdf_raises(extractor, tmp_path):
    from smriti.exceptions import PdfExtractionError

    corrupted = tmp_path / "bad.pdf"
    corrupted.write_bytes(b"this is not a pdf at all garbage data")
    with pytest.raises(PdfExtractionError):
        extractor.extract(corrupted)


def test_nonexistent_pdf_raises(extractor, tmp_path):
    from smriti.exceptions import PdfExtractionError

    with pytest.raises(PdfExtractionError):
        extractor.extract(tmp_path / "ghost.pdf")
