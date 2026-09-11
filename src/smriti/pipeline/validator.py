"""
Input and output validation for pipeline phases.
Ensures data integrity at each phase boundary.
"""

from pathlib import Path

from smriti.exceptions import ValidationError


class Validator:
    """Validate pipeline inputs and outputs."""

    @staticmethod
    def validate_input_directory(path: str) -> Path:
        """Validate input directory exists and is a directory."""
        p = Path(path)
        if not p.is_dir():
            raise ValidationError(f"Input directory not found: {path}")
        return p

    @staticmethod
    def validate_markdown_files(directory: Path) -> list[Path]:
        """Find all markdown files in directory (recursive)."""
        files = list(directory.glob("**/*.md"))
        if not files:
            raise ValidationError(f"No markdown files found in {directory}")
        return files

    @staticmethod
    def validate_output_directory(path: str) -> Path:
        """Ensure output directory exists, create if needed."""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
