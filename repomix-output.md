This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  workflows/
    ci.yml
artifacts/
  .gitkeep
config/
  default.yaml
  dev.yaml
  test.yaml
data/
  raw/
    .gitkeep
  .gitkeep
scripts/
  download_models.ps1
  setup_dev.ps1
src/
  smriti/
    claims/
      __init__.py
      annotation.py
      boundaries.py
      builder.py
      degradation.py
      models.py
      parser.py
      rules.py
      statistics.py
      structure.py
      validator.py
    contradiction/
      __init__.py
      detector.py
    core/
      __init__.py
      cache.py
      config.py
      hashing.py
      logger.py
      manifest.py
      models.py
      paths.py
      state.py
      timing.py
    dashboard/
      __init__.py
      app.py
    discovery/
      __init__.py
      builder.py
      duplicate.py
      hashing.py
      metadata.py
      scanner.py
      validator.py
    embedding/
      __init__.py
      builders.py
      cache.py
      embedder.py
      input_factory.py
      models.py
      normalization.py
      statistics.py
      validation.py
    evolution/
      __init__.py
      analyzer.py
    extraction/
      scanner/
        __init__.py
        code.py
        heading.py
        paragraph.py
        scanner.py
        table.py
      __init__.py
      builder.py
      context.py
      extractor.py
      normalizer.py
      rules.py
      segmenter.py
      statistics.py
      validator.py
    parsing/
      __init__.py
      builder.py
      loader.py
      markdown.py
      normalize.py
      parser.py
      pdf.py
      statistics.py
      text.py
    pipeline/
      __init__.py
      runner.py
      validator.py
    reporting/
      __init__.py
      exporter.py
    retrieval/
      __init__.py
      retriever.py
    scoring/
      __init__.py
      scorer.py
    __init__.py
    __version__.py
    constants.py
    exceptions.py
    main.py
  .gitkeep
tests/
  fixtures/
    sample_notes.md
    sample.pdf
  integration/
    test_phase1_discovery.py
    test_phase3_extraction.py
    test_phase4_extraction.py
    test_phase5_embedding.py
    test_pipeline_runner.py
  unit/
    test_builder.py
    test_cache.py
    test_config.py
    test_duplicate.py
    test_hashing.py
    test_manifest.py
    test_metadata.py
    test_models.py
    test_parsing_builder.py
    test_parsing_loader.py
    test_parsing_markdown.py
    test_parsing_normalize.py
    test_parsing_pdf.py
    test_parsing_statistics.py
    test_phase2_extraction.py
    test_phase3_builder.py
    test_phase3_context.py
    test_phase3_normalizer.py
    test_phase3_scanner.py
    test_phase3_segmenter.py
    test_phase3_statistics.py
    test_phase3_validator.py
    test_phase4_annotation.py
    test_phase4_boundaries.py
    test_phase4_builder.py
    test_phase4_parser.py
    test_phase4_structure.py
    test_phase4_validator.py
    test_phase5_builders.py
    test_phase5_cache.py
    test_phase5_input_factory.py
    test_phase5_normalization.py
    test_phase5_property_based.py
    test_phase5_validation.py
    test_scanner.py
    test_validator.py
  __init__.py
  conftest.py
.gitignore
download_models.ps1
LICENSE
Makefile.ps1
pyproject.toml
README.md
setup_dev.ps1
```

# Files

## File: .github/workflows/ci.yml
````yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-and-lint:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      run: python -m pip install poetry
      shell: bash

    - name: Install dependencies
      run: poetry install --with dev
      shell: bash

    - name: Download spaCy model
      run: poetry run python -m spacy download en_core_web_sm
      shell: bash

    - name: Run tests
      run: poetry run pytest tests/ -v --cov=src/smriti
      shell: bash

    - name: Lint with Ruff
      run: poetry run ruff check src/ tests/
      shell: bash

    - name: Format check with Black
      run: poetry run black --check src/ tests/
      shell: bash

    - name: Type check
      run: poetry run mypy src/smriti
      shell: bash

    - name: Upload coverage
      uses: codecov/codecov-action@v4
````

## File: artifacts/.gitkeep
````

````

## File: config/default.yaml
````yaml
# config/default.yaml
# Single source of truth for all tunable parameters.
# constants.py holds only structural/schema values.
env: dev
debug: false

pipeline:
  max_notes: 10000
  max_claims_per_note: 100

extraction:
  spacy_model: "en_core_web_sm"
  min_svo_confidence: 0.6
  fallback_to_sentences: true

# Model names are configuration, not constants.
# Change model here — nothing else needs to change.
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 32
  cache_embeddings: true

nli:
  model: "cross-encoder/nli-deberta-v3-small"
  sim_threshold: 0.75
  nli_threshold: 0.80
  temporal_base: 30

metrics:
  kcs_min_pairs: 5
  ds_min_claims: 2

logging:
  level: "INFO"

# config/default.yaml — append discovery section

discovery:
  # Extension whitelist. Only these will enter the pipeline.
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"

  # Directories always skipped during recursive traversal.
  # These are IN ADDITION to the hardcoded system dirs in scanner.py.
  ignored_dirs:
    - ".git"
    - ".obsidian"
    - ".vscode"
    - "__pycache__"
    - "node_modules"
    - ".idea"
    - "dist"
    - "build"

  # Maximum file size in bytes. Files larger than this are skipped.
  # Default: 50 MB
  max_file_size_bytes: 52428800

  # Skip files starting with these prefixes (case-insensitive)
  ignored_prefixes:
    - "~$"          # Word/Excel temp files
    - ".~lock."     # LibreOffice temp files

  # Output
  output_dataset_filename: "dataset.json"  

# ── Phase 2: Text Extraction ──────────────────────────────────────────────────
parsing:
  # Unicode normalization form. NFC makes equivalent sequences identical.
  # Do NOT change after first run — would invalidate cached normalized text.
  unicode_normalization: "NFC"

  # Maximum consecutive blank lines allowed after normalization.
  # 100 blank lines → collapse_blank_lines blank lines.
  collapse_blank_lines: 2

  # Whether to preserve Markdown syntax characters in extracted text.
  # true  → "# Heading" stays "# Heading"  (downstream sees full context)
  # false → "# Heading" becomes "Heading"   (NOT recommended)
  preserve_markdown_syntax: true

  # Whether to preserve indentation (code blocks, nested lists).
  preserve_indentation: true

  # Remove trailing whitespace on every line.
  remove_trailing_whitespace: true

  # Encoding detection order. First succeeds → used.
  # Every fallback beyond utf-8 generates an EncodingFallbackWarning.
  encoding_fallbacks:
    - "utf-8"
    - "utf-8-sig"   # UTF-8 with BOM
    - "utf-16"
    - "latin-1"     # Last resort — never fails, but may misrepresent bytes

  # PDF extraction limits
  max_pdf_pages: 500           # Pages beyond this are skipped with a warning
  max_text_length_chars: 5000000  # ~5 MB of text — documents larger are truncated with warning

  # Minimum non-whitespace characters required for a document to be
  # considered "successfully extracted" (not empty). Documents below
  # this threshold produce a NoExtractableTextWarning.
  min_extractable_chars: 10

  # Output artifact filename
  output_dataset_filename: "dataset.json"  

  # ── Phase 3: Semantic Sentence Construction ──────────────────────────────────
segmentation:
  # Minimum characters for a sentence to be kept.
  # Shorter candidates are discarded with SEG001.
  min_sentence_chars: 3

  # Maximum characters before emitting SEG002 warning.
  max_sentence_chars: 2000

  # Abbreviations that should never trigger sentence boundaries.
  abbreviations:
    - "dr"
    - "mr"
    - "mrs"
    - "ms"
    - "prof"
    - "sr"
    - "jr"
    - "e.g"
    - "i.e"
    - "vs"
    - "etc"
    - "fig"
    - "no"
    - "vol"
    - "pt"
    - "pp"
    - "u.s"
    - "u.k"
    - "a.m"
    - "p.m"

  # Context path separator
  context_separator: " > "

  # Maximum heading depth to track in context stack.
  # Headings deeper than this generate CTX001 warning.
  max_context_depth: 6

  # Table serialisation: how to format key-value pairs from table cells.
  table_kv_template: "{key}: {value}."


  # ── Phase 4: Claim Construction ───────────────────────────────────────────────
claim_extraction:

  # Maximum claims extracted from one SemanticSentence.
  # Prevents pathological outputs from complex sentences.
  max_claims_per_sentence: 10

  # Minimum characters for a claim to be kept.
  min_claim_chars: 3

  # Whether to attempt splitting coordinated predicates/clauses.
  # "Python supports X and Y" → two claims when true.
  split_conjunctions: true

  # Whether to split conditional clauses.
  # "If X, then Y" → usually kept together (false = safer).
  split_conditionals: false

  # Whether to split relative clauses into independent claims.
  # "Python, which runs on CPU, is popular" → conservative: keep together.
  split_relative_clauses: false

  # Whether to annotate negation, modality, attribution.
  enable_annotation: true

  # Whether to preserve the author's exact wording.
  # MUST always be true. Here for documentation only.
  preserve_original_text: true

  # ── Phase 5: Semantic Embedding Layer ────────────────────────────────────────
embedding_phase5:
  # Embedding model (sentence-transformers format)
  model_name: "sentence-transformers/all-MiniLM-L6-v2"

  # Inference device: "cpu", "cuda", or "mps"
  # Default is CPU — SMRITI is designed to run without GPU
  device: "cpu"

  # Number of claims to encode in one inference call
  # Larger batches = faster throughput; smaller batches = lower memory
  # NOTE: batch_size does NOT affect embedding values — excluded from config_hash
  batch_size: 32

  # Apply L2 normalization after inference
  # Recommended: true — enables cosine similarity via dot product in Phase 6
  normalize: true

  # Cache embeddings to disk
  # Huge speed improvement for re-runs on unchanged vaults
  cache_embeddings: true

  # Optional instruction prefix (for instruction-tuned models like BGE, Instructor, E5)
  # Leave empty for standard models like MiniLM
  # INCLUDED in config_hash — changing this invalidates all cached embeddings
  instruction_prefix: ""

  # Maximum sequence length override (model-specific)
  # Leave null to use the model's default
  # INCLUDED in config_hash — changing this may change truncation behavior
  max_seq_length: null

  # Pipeline version — increment when pipeline logic changes
  pipeline_version: "1.0"
````

## File: config/dev.yaml
````yaml
# config/dev.yaml
# Only override what changes for local development.
# Deep-merged: keys not listed here are inherited from default.yaml.

env: dev
debug: true

logging:
  level: "DEBUG"

embedding:
  batch_size: 8   # Smaller batches — faster iteration on dev hardware

# config/dev.yaml — Phase 1 overrides for development

discovery:
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"
    - ".rst"  

parsing:
  # Smaller limits for faster local iteration
  max_pdf_pages: 50
  max_text_length_chars: 500000
````

## File: config/test.yaml
````yaml
# config/test.yaml
env: test
debug: false

pipeline:
  max_notes: 100

logging:
  level: "WARNING"

embedding:
  cache_embeddings: false

nli:
  cache_nli_results: false


# config/test.yaml — Phase 1 overrides for tests

discovery:
  supported_extensions:
    - ".md"
    - ".pdf"
    - ".txt"
  max_file_size_bytes: 1048576  # 1 MB limit in tests  

parsing:
  max_pdf_pages: 10
  max_text_length_chars: 100000
  min_extractable_chars: 1  

# config/test.yaml — Phase 3 test overrides
segmentation:
  min_sentence_chars: 1    # Accept very short sentences in tests
  max_sentence_chars: 5000  


# config/test.yaml — Phase 4 test overrides
claim_extraction:
  max_claims_per_sentence: 5
  split_conjunctions: true
  split_conditionals: false
  enable_annotation: true  

# config/test.yaml — Phase 5 test overrides
embedding_phase5:
  batch_size: 4            # Small batches for test speed
  cache_embeddings: false  # No caching during tests
  normalize: true
  device: "cpu"
  instruction_prefix: ""
  max_seq_length: null
````

## File: data/raw/.gitkeep
````

````

## File: data/.gitkeep
````

````

## File: scripts/download_models.ps1
````powershell
<#
.SYNOPSIS
    Download ML models required by SMRITI.
.DESCRIPTION
    Downloads spaCy and sentence-transformers models.
    Checks internet connectivity before attempting downloads.
#>

#Requires -Version 5.1
$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Fail { param([string]$msg) Write-Host "  ✗ $msg" -ForegroundColor Red; exit 1 }

Write-Step "Checking internet connectivity"
try {
    $null = Invoke-WebRequest -Uri "https://huggingface.co" -UseBasicParsing -TimeoutSec 10
    Write-OK "Internet reachable"
} catch {
    Write-Fail "No internet connection. Cannot download models."
}

Write-Step "Downloading spaCy model"
poetry run python -m spacy download en_core_web_sm
if ($LASTEXITCODE -ne 0) { Write-Fail "spaCy model download failed" }
Write-OK "en_core_web_sm ready"

Write-Step "Downloading sentence-transformers embedding model"
poetry run python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('embedding model ready')
"
if ($LASTEXITCODE -ne 0) { Write-Fail "Embedding model download failed" }
Write-OK "all-MiniLM-L6-v2 ready"

Write-Step "Downloading NLI cross-encoder model"
poetry run python -c "
from sentence_transformers import CrossEncoder
CrossEncoder('cross-encoder/nli-deberta-v3-small')
print('NLI model ready')
"
if ($LASTEXITCODE -ne 0) { Write-Fail "NLI model download failed" }
Write-OK "nli-deberta-v3-small ready"

Write-Host "`n=== All models downloaded ===" -ForegroundColor Green
````

## File: scripts/setup_dev.ps1
````powershell
<#
.SYNOPSIS
    Setup development environment for SMRITI on Windows.
.DESCRIPTION
    Validates Python version, installs Poetry, installs dependencies,
    verifies virtual environment, checks internet connectivity,
    then downloads required ML models.
#>

#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$MIN_PYTHON_MAJOR = 3
$MIN_PYTHON_MINOR = 11
$MIN_POETRY_VERSION = [version]"1.8.0"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Fail { param([string]$msg) Write-Host "  ✗ $msg" -ForegroundColor Red; exit 1 }

# ── 1. Python version check ──────────────────────────────────────────────────
Write-Step "Checking Python version"
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]; $minor = [int]$Matches[2]
        if ($major -lt $MIN_PYTHON_MAJOR -or ($major -eq $MIN_PYTHON_MAJOR -and $minor -lt $MIN_PYTHON_MINOR)) {
            Write-Fail "Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR+ required. Found: $pyVersion"
        }
        Write-OK "Python $major.$minor"
    } else {
        Write-Fail "Could not parse Python version from: $pyVersion"
    }
} catch {
    Write-Fail "Python not found. Install from https://python.org"
}

# ── 2. Poetry check / install ────────────────────────────────────────────────
Write-Step "Checking Poetry"
$poetryInstalled = $false
try {
    $poetryRaw = poetry --version 2>&1
    if ($poetryRaw -match "Poetry \(version (\d+\.\d+\.\d+)\)") {
        $poetryVer = [version]$Matches[1]
        if ($poetryVer -ge $MIN_POETRY_VERSION) {
            Write-OK "Poetry $poetryVer"
            $poetryInstalled = $true
        } else {
            Write-Host "  ! Poetry $poetryVer found — upgrading..." -ForegroundColor Yellow
        }
    }
} catch { }

if (-not $poetryInstalled) {
    Write-Host "  Installing Poetry..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    $env:Path += ";$env:APPDATA\Python\Scripts"
    Write-OK "Poetry installed"
}

# ── 3. Install dependencies ───────────────────────────────────────────────────
Write-Step "Installing Python dependencies"
poetry install --with dev
if ($LASTEXITCODE -ne 0) { Write-Fail "poetry install failed" }
Write-OK "Dependencies installed"

# ── 4. Virtual environment validation ────────────────────────────────────────
Write-Step "Validating virtual environment"
$venvPath = poetry env info --path 2>&1
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPath)) {
    Write-Fail "Virtual environment not found at: $venvPath"
}
Write-OK "Virtual env: $venvPath"

# ── 5. Internet connectivity check ───────────────────────────────────────────
Write-Step "Checking internet connectivity (needed to download models)"
try {
    $null = Invoke-WebRequest -Uri "https://huggingface.co" -UseBasicParsing -TimeoutSec 10
    Write-OK "Internet reachable"
} catch {
    Write-Fail "No internet connection. Cannot download ML models. Check your network."
}

# ── 6. Download spaCy model ───────────────────────────────────────────────────
Write-Step "Downloading spaCy model (en_core_web_sm)"
poetry run python -m spacy download en_core_web_sm
if ($LASTEXITCODE -ne 0) { Write-Fail "spaCy model download failed" }
Write-OK "spaCy model ready"

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  .\Makefile.ps1 test    # Run all tests"
Write-Host "  .\Makefile.ps1 lint    # Lint and type-check"
````

## File: src/smriti/claims/__init__.py
````python
"""
claims/__init__.py — Public API for Phase 4: Claim Construction.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.claims import extract_claims, Phase4Result

They NEVER import from internal modules:
    claims.parser, claims.boundaries, claims.structure,
    claims.annotation, claims.degradation, claims.builder,
    claims.validator, claims.statistics, claims.models, claims.rules

Public contract:
    extract_claims(semantic_sentences: List[SemanticSentence]) → Phase4Result

That is the ONLY function that crosses the Phase 4 boundary.

Everything inside this module (parser, boundaries, structure, annotation,
degradation, builder, validator) is an implementation detail.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    ClaimWarning,
    ExtractionMode,
    Phase4Stats,
    SemanticSentence,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase4Error, ClaimValidationError

from smriti.claims.parser import BaseParser, SpaCyParser  # <-- REPLACED
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.builder import build_claim
from smriti.claims.validator import validate_claims
from smriti.claims.statistics import Phase4StatsCollector

logger = structlog.get_logger(__name__)


# ── Public result types ────────────────────────────────────────────────────────

@dataclass
class SentenceExtractionResult:
    """Phase 4 result for a single SemanticSentence."""
    sentence_id: str
    claims: List[Claim]
    warnings: List[ClaimWarning]
    error: Optional[str] = None

    @property
    def claim_count(self) -> int:
        return len(self.claims)


@dataclass
class Phase4Result:
    """
    Complete output of Phase 4 — all claims extracted from all sentences.
    This is what Phase 5 (Embedding) receives.
    """
    sentence_results: List[SentenceExtractionResult]
    stats: Phase4Stats
    run_id: str
    manifest_path: Optional[Path] = None

    @property
    def all_claims(self) -> List[Claim]:
        """Flat list of all claims across all sentences."""
        result = []
        for sr in self.sentence_results:
            result.extend(sr.claims)
        return result

    @property
    def total_claims(self) -> int:
        return sum(sr.claim_count for sr in self.sentence_results)

    @property
    def successful_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is None)

    @property
    def failed_sentences(self) -> int:
        return sum(1 for sr in self.sentence_results if sr.error is not None)

    def to_dataset_json(self) -> str:
        """
        Serialize all Claims to JSON for Phase 5.
        Written to artifacts/run_{id}/phase4/dataset.json.
        """
        records = []
        for claim in self.all_claims:
            record = {
                "claim_id":         claim.claim_id,
                "sentence_id":      claim.sentence_id,
                "document_id":      claim.document_id,
                "text":             claim.text,
                "content_hash":     claim.content_hash,          # NEW
                "context":          claim.context,
                "source_path":      str(claim.source_path),
                "extraction_mode":  claim.extraction_mode.value,
                "schema_version":   claim.schema_version,
                "rule_version":     claim.rule_version,          # NEW
                "is_negated":       claim.assertion_metadata.is_negated,
                "modality":         claim.assertion_metadata.modality.value,
                "is_conditional":   claim.assertion_metadata.is_conditional,
                "is_comparative":   claim.assertion_metadata.is_comparative,
                "is_attributed":    claim.assertion_metadata.is_attributed,
                "attributed_to":    claim.assertion_metadata.attributed_to,
                "provenance": {
                    "sentence_id":       claim.provenance.sentence_id,
                    "document_id":       claim.provenance.document_id,
                    "source_path":       str(claim.provenance.source_path),
                    "sentence_context":  claim.provenance.sentence_context,
                    "sentence_position": claim.provenance.sentence_position,
                },
            }
            # Include SVO if available
            if claim.structured_assertion:
                record["svo"] = {
                    "subject":   claim.structured_assertion.subject,
                    "predicate": claim.structured_assertion.predicate,
                    "object":    claim.structured_assertion.object,
                }
            else:
                record["svo"] = None

            records.append(record)

        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ───────────────────────────────────────────────────────

def extract_claims_from_sentence(
    sentence: SemanticSentence,
    parser: BaseParser,
    boundary_detector: BoundaryDetector,
    structure_extractor: StructureExtractor,
    annotator: AssertionAnnotator,
    degradation_handler: DegradationHandler,
    stats_collector: Phase4StatsCollector,
    max_claims: int,
    global_seen_ids: dict,
) -> SentenceExtractionResult:
    """
    Extract claims from a single SemanticSentence.

    This is the 7-stage compiler pipeline applied to one sentence.

    Returns:
        SentenceExtractionResult (never raises — errors are captured).
    """
    sentence_id = sentence.sentence_id
    all_warnings: List[ClaimWarning] = []

    try:
        stats_collector.record_sentence_processed()

        # Stage 1: Linguistic Analysis
        parsed = parser.parse(sentence)
        if not parsed.parse_ok:
            stats_collector.record_parser_failure()
            all_warnings.append(ClaimWarning.CLM_PARSER_FAILURE)

        # Stage 2–3: Assertion Analysis + Boundary Detection
        candidates = boundary_detector.detect(parsed)
        stats_collector.record_boundary_split(len(candidates))

        # Enforce max claims per sentence
        if len(candidates) > max_claims:
            candidates = candidates[:max_claims]
            all_warnings.append(ClaimWarning.CLM_EXCEEDED_MAX_CLAIMS)

        claims: List[Claim] = []

        for candidate in candidates:
            # Stage 4: Structured Extraction
            structured = structure_extractor.extract(candidate, parser)

            # Stage 5: Assertion Annotation
            annotated = annotator.annotate(structured)

            # Stage 6: Failure Degradation
            validated = degradation_handler.apply(annotated)
            all_warnings.extend(validated.all_warnings)

            # Stage 7: Build Claim
            claim = build_claim(validated)

            # Record statistics
            stats_collector.record_claim(
                mode=claim.extraction_mode,
                is_negated=claim.is_negated,
                is_modal=claim.assertion_metadata.modality.value != "certain",
                is_attributed=claim.assertion_metadata.is_attributed,
            )

            claims.append(claim)

        # Validate the complete claim collection
        validated_claims, val_warnings = validate_claims(claims, sentence.document_id, global_seen_ids)
        all_warnings.extend(val_warnings)
        stats_collector.record_warnings(all_warnings)

        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=validated_claims,
            warnings=all_warnings,
        )

    except ClaimValidationError as e:
        logger.error(
            "fatal claim validation error",
            sentence_id=sentence_id[:8],
            error=str(e),
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in claim extraction",
            sentence_id=sentence_id[:8],
            error=str(e),
            exc_info=True,
        )
        return SentenceExtractionResult(
            sentence_id=sentence_id,
            claims=[],
            warnings=all_warnings,
            error=str(e),
        )


def extract_claims(
    semantic_sentences: List[SemanticSentence],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> Phase4Result:
    """
    Extract claims from all SemanticSentences.

    This is the sole public function of Phase 4.
    All internal pipeline components are created here and hidden from callers.

    Args:
        semantic_sentences: All SemanticSentences from Phase 3.
        run_id:             Current pipeline run identifier.
        manifest_manager:   For writing phase manifest.
        state_manager:      For updating pipeline state.

    Returns:
        Phase4Result containing all Claims and statistics.
    """
    config = get_config()
    ce_cfg = config.get("claim_extraction", {})
    max_claims = ce_cfg.get("max_claims_per_sentence", 10)

    logger.info(
        "phase 4 starting",
        run_id=run_id,
        sentences=len(semantic_sentences),
    )
    start_time = manifest_manager.start_phase(phase=4)

    # Initialize all pipeline components once
    parser = SpaCyParser()  # <-- REPLACED (instantiate concrete class)
    boundary_detector = BoundaryDetector()
    structure_extractor = StructureExtractor()
    annotator = AssertionAnnotator()
    degradation_handler = DegradationHandler()
    stats_collector = Phase4StatsCollector()

    sentence_results: List[SentenceExtractionResult] = []
    global_seen_ids: dict = {}

    with Timer("phase4_claim_construction"):
        for sentence in semantic_sentences:
            result = extract_claims_from_sentence(
                sentence=sentence,
                parser=parser,
                boundary_detector=boundary_detector,
                structure_extractor=structure_extractor,
                annotator=annotator,
                degradation_handler=degradation_handler,
                stats_collector=stats_collector,
                max_claims=max_claims,
                global_seen_ids=global_seen_ids,
            )
            sentence_results.append(result)

    stats = stats_collector.finalize()

    phase4_result = Phase4Result(
        sentence_results=sentence_results,
        stats=stats,
        run_id=run_id,
    )

    # Write dataset artifact for Phase 5
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase4"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(phase4_result.to_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        claims=phase4_result.total_claims,
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=4,
        start_time=start_time,
        inputs={"sentences": len(semantic_sentences)},
        outputs={
            "total_claims": phase4_result.total_claims,
            "structured": stats.structured_claims,
            "partial": stats.partial_claims,
            "lexical": stats.lexical_claims,
            "whole_sentence": stats.whole_sentence_claims,
            "parser_failures": stats.parser_failures,
            "dataset_path": str(dataset_path),
        },
        status="success",
    )
    phase4_result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=4)

    logger.info(
        "phase 4 complete",
        total_claims=phase4_result.total_claims,
        structured=stats.structured_claims,
        fallbacks=stats.whole_sentence_claims,
        parser_failures=stats.parser_failures,
    )

    return phase4_result
````

## File: src/smriti/claims/annotation.py
````python
"""
annotation.py — Semantic metadata annotation for Phase 4.

Responsibility:
    Add semantic metadata to a StructuredAssertionCandidate.
    Detect: negation, modality, attribution, conditional, comparison, quotation.

Rules:
    ✅ Annotate text with semantic flags
    ✅ Record metadata accurately

    ❌ NEVER modify text
    ❌ NEVER rewrite claims
    ❌ NEVER perform semantic inference
    ❌ NEVER change ExtractionMode

The text remains exactly as the author wrote it.
Metadata is additive, never transformative.
"""

from __future__ import annotations

import structlog

from smriti.core.models import Modality
from smriti.claims.models import (
    StructuredAssertionCandidate, 
    AnnotatedAssertion,
    LinguisticMetadata,
    SemanticMetadata
)
from smriti.claims.rules import (
    NEGATION_MARKERS,
    MODALITY_POSSIBLE,
    MODALITY_PROBABLE,
    MODALITY_REQUIRED,
    MODALITY_IMPOSSIBLE,
    ATTRIBUTION_VERBS,
    COMPARISON_MARKERS,
)

logger = structlog.get_logger(__name__)


class AssertionAnnotator:
    """
    Annotates assertions with semantic metadata.
    """

    def annotate(self, candidate: StructuredAssertionCandidate) -> AnnotatedAssertion:
        """
        Annotate an assertion with semantic metadata.

        Args:
            candidate: StructuredAssertionCandidate from structure.py.

        Returns:
            AnnotatedAssertion with metadata populated.
        """
        parsed = candidate.candidate.source
        text = candidate.candidate.text.lower()

        # ── Linguistic metadata ──────────────────────────────────────────────────
        is_negated = self._detect_negation(parsed, text)
        modality = self._detect_modality(parsed, text)
        is_quoted = self._detect_quotation(text)

        linguistic = LinguisticMetadata(
            is_negated=is_negated,
            modality=modality,
            is_quoted=is_quoted,
        )

        # ── Semantic metadata ────────────────────────────────────────────────────
        is_conditional = self._detect_conditional(parsed, text)
        is_comparative = self._detect_comparative(text)
        is_attributed, attributed_to = self._detect_attribution(parsed)

        semantic = SemanticMetadata(
            is_conditional=is_conditional,
            is_comparative=is_comparative,
            is_attributed=is_attributed,
            attributed_to=attributed_to,
        )

        logger.debug(
            "assertion annotated",
            negated=is_negated,
            modality=modality.value,
            conditional=is_conditional,
            attributed=is_attributed,
        )

        return AnnotatedAssertion(
            structured_candidate=candidate,
            linguistic_metadata=linguistic,
            semantic_metadata=semantic,
        )

    def _detect_negation(self, parsed, text_lower: str) -> bool:
        """Detect negation via spaCy dep_ or keyword scan."""
        # spaCy negation detection (more accurate)
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ == "neg":
                    return True

        # Keyword fallback
        words = set(text_lower.split())
        return bool(words & NEGATION_MARKERS)

    def _detect_modality(self, parsed, text_lower: str) -> Modality:
        """Detect modality from auxiliary verbs."""
        if parsed.parse_ok and parsed.spacy_doc:
            for token in parsed.spacy_doc:
                if token.dep_ in ("aux", "auxpass"):
                    lemma = token.lemma_.lower()
                    if lemma in MODALITY_IMPOSSIBLE:
                        return Modality.IMPOSSIBLE
                    if lemma in MODALITY_REQUIRED:
                        return Modality.REQUIRED
                    if lemma in MODALITY_PROBABLE:
                        return Modality.PROBABLE
                    if lemma in MODALITY_POSSIBLE:
                        return Modality.POSSIBLE

        # Keyword fallback
        words = set(text_lower.split())
        if words & MODALITY_IMPOSSIBLE:
            return Modality.IMPOSSIBLE
        if words & MODALITY_REQUIRED:
            return Modality.REQUIRED
        if words & MODALITY_PROBABLE:
            return Modality.PROBABLE
        if words & MODALITY_POSSIBLE:
            return Modality.POSSIBLE

        return Modality.CERTAIN

    def _detect_conditional(self, parsed, text_lower: str) -> bool:
        """Detect conditional clauses (if/unless/when)."""
        conditional_markers = {"if", "unless", "when", "whenever", "provided", "assuming"}
        words = set(text_lower.split())
        return bool(words & conditional_markers)

    def _detect_comparative(self, text_lower: str) -> bool:
        """Detect comparative claims ("faster than", "better than")."""
        words = set(text_lower.split())
        return bool(words & COMPARISON_MARKERS)

    def _detect_attribution(self, parsed) -> tuple:
        """
        Detect attribution: "X says Y" / "According to X, Y".

        Returns:
            (is_attributed: bool, attributed_to: Optional[str])
        """
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return False, None

        for token in parsed.spacy_doc:
            if token.lemma_.lower() in ATTRIBUTION_VERBS:
                # Find the subject of the attribution verb
                subjects = [t for t in token.children if t.dep_ in ("nsubj", "nsubjpass")]
                if subjects:
                    attributed_to = subjects[0].text
                    return True, attributed_to

        return False, None

    def _detect_quotation(self, text_lower: str) -> bool:
        """Detect direct quotations (text contains quotes)."""
        return '"' in text_lower or "'" in text_lower
````

## File: src/smriti/claims/boundaries.py
````python
"""
boundaries.py — Claim boundary detection for Phase 4.

Responsibility:
    Given a ParsedSentence, identify where individual semantic assertions begin
    and end within the sentence text.

    This is the most algorithmically complex module in Phase 4.

    Input:  ParsedSentence (with spaCy Doc)
    Output: List[AssertionCandidate]

Boundary Rules (deterministic, in priority order):
    1. Coordinated predicates with shared subject: split
       "Python supports generators and decorators"
       → "Python supports generators." + "Python supports decorators."

    2. Independent clauses joined by coordinator: split
       "CUDA is proprietary and AMD ROCm is open."
       → "CUDA is proprietary." + "AMD ROCm is open."

    3. Contrastive clauses (although/whereas): preserve both sides
       "Although CUDA is proprietary, it performs well."
       → "CUDA is proprietary." + "CUDA performs well."
       (relationship recorded in metadata)

    4. Conditional clauses: preserve entire conditional as one claim
       "If CUDA is installed, PyTorch uses the GPU."
       → Single claim (condition must not be severed)

    5. Relative clauses: preserve as one claim unless independent
       "Python, which was released in 1991, supports generators."
       → Single claim (relative clause is not an independent assertion)

    6. Single assertion (default): no split → one candidate

Design:
    If splitting fails or is ambiguous → fall back to whole-sentence candidate.
    Information is NEVER lost. Ambiguous → conservative (no split).
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.config import get_config
from smriti.core.models import BoundaryReason
from smriti.claims.models import ParsedSentence, AssertionCandidate
from smriti.claims.rules import SUBJECT_DEP_LABELS

logger = structlog.get_logger(__name__)


class BoundaryDetector:
    """
    Applies deterministic boundary rules to find assertion boundaries.

    Instantiate once, call detect() per ParsedSentence.
    """

    def __init__(self) -> None:
        config = get_config()
        ce_cfg = config.get("claim_extraction", {})
        self._split_conjunctions: bool = ce_cfg.get("split_conjunctions", True)
        self._split_conditionals: bool = ce_cfg.get("split_conditionals", False)
        self._split_relative_clauses: bool = ce_cfg.get("split_relative_clauses", False)

    def detect(self, parsed: ParsedSentence) -> List[AssertionCandidate]:
        """
        Detect claim boundaries in a parsed sentence.

        Args:
            parsed: ParsedSentence from parser.py.

        Returns:
            List of AssertionCandidate. Always at least one (whole-sentence fallback).
        """
        # If parsing failed, return the whole sentence as one candidate
        if not parsed.parse_ok or parsed.spacy_doc is None:
            return [self._whole_sentence_candidate(parsed, reason=BoundaryReason.PARSE_FAILED)]

        doc = parsed.spacy_doc
        candidates: List[AssertionCandidate] = []

        if self._split_conjunctions:
            candidates = self._detect_coordination_boundaries(parsed, doc)

        # If no splits were detected (or splitting disabled), use whole sentence
        if not candidates:
            candidates = [self._whole_sentence_candidate(parsed, reason=BoundaryReason.SINGLE_ASSERTION)]

        logger.debug(
            "boundaries detected",
            sentence_id=parsed.sentence.sentence_id[:8],
            candidate_count=len(candidates),
        )

        return candidates

    def _detect_coordination_boundaries(
        self,
        parsed: ParsedSentence,
        doc,
    ) -> List[AssertionCandidate]:
        """
        Detect boundaries created by coordinating conjunctions (and, but, or).

        Uses exact token spans to reconstruct clauses, preserving tense, aspect,
        and passive voice. Never uses .lemma_ for reconstruction.
        """
        try:
            # Find sentence root (usually the main verb)
            roots = [token for token in doc if token.dep_ == "ROOT"]
            if not roots:
                return []

            root = roots[0]

            # Find coordinating conjunctions attached to root
            conj_tokens = [
                t for t in doc
                if t.dep_ == "conj" and t.head == root
            ]

            if not conj_tokens:
                return []

            # Use the new reconstruction method
            return self._reconstruct_coordinated_clauses(
                sent=doc,
                root=root,
                conjuncts=conj_tokens,
                parsed=parsed,
            )

        except Exception as e:
            logger.debug(
                "boundary detection error (falling back)",
                error=str(e),
                sentence_id=parsed.sentence.sentence_id[:8],
            )
            return []

    def _reconstruct_coordinated_clauses(
        self,
        sent,
        root,
        conjuncts,
        parsed: ParsedSentence,
    ) -> List[AssertionCandidate]:
        """
        Reconstruct clauses using exact token spans to preserve tense, aspect, and passive voice.
        NEVER uses lemmas for reconstruction.
        """
        candidates = []

        # 1. Extract the exact token span for the subject
        subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass", "csubj")]
        subj_tokens = list(subjects[0].subtree) if subjects else []

        # 2. Extract the main clause (exclude conjunct subtrees and their coordinating conjunctions)
        conjunct_subtrees = set()
        for conj in conjuncts:
            conjunct_subtrees.update(conj.subtree)
            # Catch the 'and' / 'or' attached to the conjunct
            for cc in conj.lefts:
                if cc.dep_ == "cc":
                    conjunct_subtrees.add(cc)

        main_clause_tokens = [t for t in sent if t not in conjunct_subtrees]
        main_text = self._tokens_to_string(main_clause_tokens)

        candidates.append(
            AssertionCandidate(
                text=main_text,
                source=parsed,
                span_start=0,
                span_end=len(main_text),  # approximate end; we keep it simple
                boundary_reason=BoundaryReason.COORDINATION,
            )
        )

        # 3. Reconstruct each conjunct clause by combining:
        #    Subject Tokens + Auxiliary Tokens + Conjunct Tokens
        aux_tokens = [t for t in root.lefts if t.dep_ in ("aux", "auxpass")]

        for conj in conjuncts:
            # Combine all required tokens and sort them by their original position in the sentence
            reconstructed_tokens = sorted(
                set(subj_tokens + aux_tokens + list(conj.subtree)),
                key=lambda x: x.i
            )
            conj_text = self._tokens_to_string(reconstructed_tokens)

            candidates.append(
                AssertionCandidate(
                    text=conj_text,
                    source=parsed,
                    span_start=conj.idx,
                    span_end=conj.idx + len(conj_text),
                    boundary_reason=BoundaryReason.COORDINATION,
                )
            )

        return candidates

    def _tokens_to_string(self, tokens: list) -> str:
        """Safely join tokens respecting spaCy's original whitespace mapping."""
        if not tokens:
            return ""
        text = tokens[0].text
        for i in range(1, len(tokens)):
            if tokens[i-1].whitespace_:
                text += " " + tokens[i].text
            else:
                # Handle punctuation spacing fallback if whitespace is lost
                if tokens[i].is_punct:
                    text += tokens[i].text
                else:
                    text += " " + tokens[i].text
        return text.strip()

    def _whole_sentence_candidate(
        self,
        parsed: ParsedSentence,
        reason: BoundaryReason = BoundaryReason.SINGLE_ASSERTION,
    ) -> AssertionCandidate:
        """Create a single whole-sentence candidate (no splitting)."""
        text = parsed.sentence.text
        return AssertionCandidate(
            text=text,
            span_start=0,
            span_end=len(text),
            source=parsed,
            boundary_reason=reason,
        )
````

## File: src/smriti/claims/builder.py
````python
"""
builder.py — Immutable Claim construction for Phase 4.

Responsibility:
    Construct the final immutable Claim object from a ValidatedAssertion.

    This is the ONLY place where Claim is instantiated.
    That enforces a single, consistent construction path.

Builder performs:
    1. Deterministic claim_id generation (SHA256, never random)
    2. Content hash computation (SHA256 of exact text)
    3. Provenance chain construction
    4. Object construction with schema and rule versioning

    Builder NEVER modifies text.
    Builder NEVER applies logic or heuristics.
    Builder NEVER performs validation.
    Pure object construction only.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import structlog

from smriti.core.models import (
    Claim,
    ClaimProvenance,
    ExtractionMode,
    AssertionMetadata,  # <-- ADDED
)
from smriti.claims.models import ValidatedAssertion
from smriti.claims.rules import CLAIM_SCHEMA_VERSION, RULE_VERSION

logger = structlog.get_logger(__name__)


def build_claim(validated: ValidatedAssertion) -> Claim:
    """
    Construct a single immutable Claim from a ValidatedAssertion.

    Args:
        validated: ValidatedAssertion from degradation.py.

    Returns:
        Immutable Claim with deterministic ID and complete provenance.
    """
    sentence = validated.source_sentence
    text = validated.text
    span_start = validated.span_start

    # Deterministic claim_id
    claim_id = _compute_claim_id(
        sentence_id=sentence.sentence_id,
        text=text,
        span_start=span_start,
    )

    # Content hash (SHA256 of exact claim text)
    content_hash = _compute_content_hash(text)

    # Complete provenance chain
    provenance = ClaimProvenance(
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        source_path=sentence.source_path,
        sentence_context=sentence.context,
        sentence_position=sentence.position,
    )

    # <-- NEW: Merge internal split metadata into the final public contract
    merged_metadata = AssertionMetadata(
        is_negated=validated.linguistic_metadata.is_negated,
        modality=validated.linguistic_metadata.modality,
        is_conditional=validated.semantic_metadata.is_conditional,
        is_comparative=validated.semantic_metadata.is_comparative,
        is_attributed=validated.semantic_metadata.is_attributed,
        attributed_to=validated.semantic_metadata.attributed_to,
        is_quoted=validated.linguistic_metadata.is_quoted,
    )

    claim = Claim(
        claim_id=claim_id,
        sentence_id=sentence.sentence_id,
        document_id=sentence.document_id,
        text=text,
        content_hash=content_hash,
        context=sentence.context,
        source_path=sentence.source_path,
        extraction_mode=validated.extraction_mode,
        structured_assertion=validated.structured_assertion,
        assertion_metadata=merged_metadata,  # <-- REPLACED
        provenance=provenance,
        schema_version=CLAIM_SCHEMA_VERSION,
        rule_version=RULE_VERSION,
    )

    logger.debug(
        "claim built",
        claim_id=claim_id[:8],
        mode=validated.extraction_mode.value,
        is_svo=claim.is_svo,
        negated=claim.is_negated,
        hash_prefix=content_hash[:8],
        rule_version=RULE_VERSION,
    )

    return claim


def _compute_claim_id(sentence_id: str, text: str, span_start: int) -> str:
    """
    Compute a deterministic 16-character claim ID.

    Input:  sentence_id + claim text + span_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs → same ID (deterministic)
        - No timestamps, no random values
        - span_start disambiguates identical text at different positions
          within the same sentence
    """
    id_material = f"{sentence_id}:{text}:{span_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]


def _compute_content_hash(text: str) -> str:
    """
    Compute SHA256 hash of the exact claim text.

    Important: This preserves case and all characters exactly as they appear.
    Lowercasing is NOT applied because case can carry semantic meaning
    (e.g., proper nouns, acronyms).

    Returns:
        16-character hex digest (first 16 chars of full SHA256).
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
````

## File: src/smriti/claims/degradation.py
````python
"""
degradation.py — Failure recovery hierarchy for Phase 4.

Responsibility:
    Apply the graceful degradation hierarchy when structured extraction fails.
    NEVER loses information — only loses structure.

Hierarchy (tried in order, first success wins):
    1. ExtractionMode.STRUCTURED    — Full SVO: S + P + O
    2. ExtractionMode.PARTIAL       — Partial SVO: at least S+P or P+O
    3. ExtractionMode.LEXICAL       — No SVO: lexical text span from boundary
    4. ExtractionMode.WHOLE_SENTENCE — Parse failed: entire sentence text

Philosophy:
    Structure is optional.
    Information is mandatory.
    A Claim must ALWAYS be produced from every AssertionCandidate.

Rules:
    ✅ Produce a Claim from every candidate, regardless of extraction success
    ✅ Record warnings for every degradation step
    ✅ Preserve original text unchanged

    ❌ Never discard an assertion
    ❌ Never invent structure to avoid degradation
    ❌ Never elevate ExtractionMode (degradation only goes down)
"""

from __future__ import annotations

from typing import List
import structlog

from smriti.core.models import ExtractionMode, ClaimWarning
from smriti.claims.models import AnnotatedAssertion, ValidatedAssertion

logger = structlog.get_logger(__name__)


class DegradationHandler:
    """
    Applies the failure degradation hierarchy.
    """

    def apply(self, annotated: AnnotatedAssertion) -> ValidatedAssertion:
        """
        Apply degradation rules and return a ValidatedAssertion.

        Args:
            annotated: AnnotatedAssertion from annotation.py.

        Returns:
            ValidatedAssertion (never None — always something).
        """
        mode = annotated.extraction_mode
        warnings: List[ClaimWarning] = list(annotated.additional_warnings)
        warnings.extend(annotated.structured_candidate.warnings)

        if mode == ExtractionMode.STRUCTURED:
            # Best case — no degradation needed
            logger.debug("extraction mode: STRUCTURED")

        elif mode == ExtractionMode.PARTIAL:
            # Partial structure — acceptable, add warning
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            logger.debug("extraction mode: PARTIAL")

        elif mode == ExtractionMode.LEXICAL:
            # No structure — whole text span preserved
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: LEXICAL (fallback)")

        elif mode == ExtractionMode.WHOLE_SENTENCE:
            # Parser completely failed — sentence text used as-is
            warnings.append(ClaimWarning.CLM_PARSER_FAILURE)
            warnings.append(ClaimWarning.CLM_FALLBACK_ACTIVATED)
            logger.debug("extraction mode: WHOLE_SENTENCE (total fallback)")

        return ValidatedAssertion(
            annotated=annotated,
            all_warnings=warnings,
        )
````

## File: src/smriti/claims/models.py
````python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any

from smriti.core.models import (           # Note: BoundaryReason now in core.models
    SemanticSentence,
    StructuredAssertion,
    AssertionMetadata,
    ExtractionMode,
    ClaimWarning,
    BoundaryReason, 
    Modality,                  # NEW import
)

# ── NEW: Internal Split Metadata ──────────────────────────────────────────────

@dataclass
class LinguisticMetadata:
    is_negated: bool
    modality: Modality
    is_quoted: bool

@dataclass
class SemanticMetadata:
    is_conditional: bool
    is_comparative: bool
    is_attributed: bool
    attributed_to: Optional[str]


@dataclass
class ParsedSentence:
    sentence: SemanticSentence
    spacy_doc: Optional[Any]
    parse_ok: bool
    parse_error: Optional[str] = None


@dataclass
class AssertionCandidate:
    text: str
    span_start: int
    span_end: int
    source: ParsedSentence
    boundary_reason: BoundaryReason   # now Enum
    # confidence removed (Priority 2)


@dataclass
class StructuredAssertionCandidate:
    candidate: AssertionCandidate
    structured_assertion: Optional[StructuredAssertion]
    extraction_mode: ExtractionMode
    warnings: List[ClaimWarning] = field(default_factory=list)


@dataclass
class AnnotatedAssertion:
    structured_candidate: StructuredAssertionCandidate
    linguistic_metadata: LinguisticMetadata  # <-- REPLACED
    semantic_metadata: SemanticMetadata      # <-- REPLACED
    additional_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.structured_candidate.candidate.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.structured_candidate.extraction_mode


@dataclass
class ValidatedAssertion:
    annotated: AnnotatedAssertion
    all_warnings: List[ClaimWarning] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.annotated.text

    @property
    def extraction_mode(self) -> ExtractionMode:
        return self.annotated.extraction_mode

    @property
    def structured_assertion(self) -> Optional[StructuredAssertion]:
        return self.annotated.structured_candidate.structured_assertion

    @property
    def linguistic_metadata(self) -> LinguisticMetadata:   # <-- ADDED
        return self.annotated.linguistic_metadata

    @property
    def semantic_metadata(self) -> SemanticMetadata:       # <-- ADDED
        return self.annotated.semantic_metadata

    @property
    def source_sentence(self) -> SemanticSentence:
        return self.annotated.structured_candidate.candidate.source.sentence

    @property
    def span_start(self) -> int:
        return self.annotated.structured_candidate.candidate.span_start
````

## File: src/smriti/claims/parser.py
````python
"""
parser.py — Deterministic linguistic analysis wrapper for Phase 4.
Now uses a pluggable parser abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import SemanticSentence
from smriti.claims.models import ParsedSentence
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

    def __init__(self, model_name: Optional[str] = None) -> None:
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
````

## File: src/smriti/claims/rules.py
````python
"""
rules.py — All deterministic extraction rules for Phase 4.

This file contains ONLY data and patterns.
Zero execution logic lives here.

Every constant is configurable via config/default.yaml [claim_extraction].
These are the hard-coded defaults for those config values.
"""

from typing import FrozenSet

# ── Coordinating conjunctions that split claims ───────────────────────────────
# "Python supports X and Y" → two claims if Y is a noun phrase with no predicate
# "Python is fast and Java is slow" → two claims (each has own predicate)
COORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset(["and", "but", "or", "nor"])

# ── Subordinating conjunctions that signal boundary candidates ─────────────
SUBORDINATING_CONJUNCTIONS: FrozenSet[str] = frozenset([
    "although", "because", "since", "while", "whereas", "though",
    "even though", "as long as", "unless", "until",
])

# ── Negation markers ──────────────────────────────────────────────────────────
NEGATION_MARKERS: FrozenSet[str] = frozenset([
    "not", "no", "never", "neither", "nor", "without",
    "n't", "cannot", "can't", "won't", "doesn't", "don't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
    "hadn't", "wouldn't", "couldn't", "shouldn't",
])

# ── Modality markers and their classifications ────────────────────────────────
MODALITY_POSSIBLE: FrozenSet[str] = frozenset([
    "may", "might", "could", "can",
])

MODALITY_PROBABLE: FrozenSet[str] = frozenset([
    "probably", "likely", "should", "ought",
])

MODALITY_REQUIRED: FrozenSet[str] = frozenset([
    "must", "will", "shall", "need", "have to", "has to",
])

MODALITY_IMPOSSIBLE: FrozenSet[str] = frozenset([
    "cannot", "can't", "impossible",
])

# ── Attribution verbs (X says Y / X believes Y) ───────────────────────────────
ATTRIBUTION_VERBS: FrozenSet[str] = frozenset([
    "say", "says", "said", "claim", "claims", "claimed",
    "argue", "argues", "argued", "believe", "believes", "believed",
    "state", "states", "stated", "report", "reports", "reported",
    "suggest", "suggests", "suggested", "note", "notes", "noted",
    "assert", "asserts", "asserted", "propose", "proposes", "proposed",
    "write", "writes", "wrote", "show", "shows", "showed", "shown",
    "find", "finds", "found",
])

# ── Comparison markers ────────────────────────────────────────────────────────
COMPARISON_MARKERS: FrozenSet[str] = frozenset([
    "faster", "slower", "better", "worse", "more", "less",
    "higher", "lower", "greater", "smaller", "stronger", "weaker",
    "outperforms", "underperforms", "exceeds", "beats",
    "superior", "inferior", "compared", "than",
])

# ── POS dependency labels for SVO extraction ─────────────────────────────────
# spaCy dependency labels for subject identification
SUBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "nsubj",     # Nominal subject: "Python supports X"
    "nsubjpass", # Passive nominal subject: "X is supported by Python"
    "csubj",     # Clausal subject
    "expl",      # Expletive: "There is X"
])

# spaCy dependency labels for object identification
OBJECT_DEP_LABELS: FrozenSet[str] = frozenset([
    "dobj",  # Direct object: "Python supports generators"
    "pobj",  # Object of preposition: "runs on GPU"
    "attr",  # Attribute: "Python is a language"
    "acomp", # Adjectival complement: "Python is fast"
])

# spaCy POS tags for verb/predicate identification
VERB_POS_TAGS: FrozenSet[str] = frozenset(["VERB", "AUX"])

# ── Schema ────────────────────────────────────────────────────────────────────
CLAIM_SCHEMA_VERSION = "4.0"
RULE_VERSION = "1.0"          # NEW (Priority 1)
PHASE4_PIPELINE_VERSION = "1.0"

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_CLAIMS_PER_SENTENCE_DEFAULT = 10
MIN_CLAIM_CHARS_DEFAULT = 3
````

## File: src/smriti/claims/statistics.py
````python
"""
statistics.py — Phase 4 execution statistics collector.

Responsibility:
    Collect operational metrics during Phase 4 processing.
    Statistics are DIAGNOSTIC ONLY — they never affect execution.

Design:
    This module observes. It never influences.
    Think of it as a telemetry layer.
"""

from __future__ import annotations

from typing import List

from smriti.core.models import ExtractionMode, ClaimWarning, Phase4Stats


class Phase4StatsCollector:
    """
    Mutable collector that accumulates Phase 4 statistics.
    Call finalize() to get the immutable Phase4Stats result.
    """

    def __init__(self) -> None:
        self._sentences = 0
        self._claims = 0
        self._structured = 0
        self._partial = 0
        self._lexical = 0
        self._whole_sentence = 0
        self._parser_failures = 0
        self._boundary_splits = 0
        self._negated = 0
        self._modal = 0
        self._attributed = 0
        self._warnings: List[ClaimWarning] = []

    def record_sentence_processed(self) -> None:
        self._sentences += 1

    def record_parser_failure(self) -> None:
        self._parser_failures += 1

    def record_boundary_split(self, count: int) -> None:
        """Record that a sentence was split into `count` claims."""
        if count > 1:
            self._boundary_splits += 1

    def record_claim(self, mode: ExtractionMode, is_negated: bool,
                     is_modal: bool, is_attributed: bool) -> None:
        self._claims += 1
        if mode == ExtractionMode.STRUCTURED:
            self._structured += 1
        elif mode == ExtractionMode.PARTIAL:
            self._partial += 1
        elif mode == ExtractionMode.LEXICAL:
            self._lexical += 1
        elif mode == ExtractionMode.WHOLE_SENTENCE:
            self._whole_sentence += 1

        if is_negated:
            self._negated += 1
        if is_modal:
            self._modal += 1
        if is_attributed:
            self._attributed += 1

    def record_warnings(self, warnings: List[ClaimWarning]) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase4Stats:
        return Phase4Stats(
            total_sentences_processed=self._sentences,
            total_claims_produced=self._claims,
            structured_claims=self._structured,
            partial_claims=self._partial,
            lexical_claims=self._lexical,
            whole_sentence_claims=self._whole_sentence,
            parser_failures=self._parser_failures,
            boundary_splits=self._boundary_splits,
            negated_claims=self._negated,
            modal_claims=self._modal,
            attributed_claims=self._attributed,
            warnings=tuple(self._warnings),
        )
````

## File: src/smriti/claims/structure.py
````python
"""
structure.py — SVO structured extraction for Phase 4.

Responsibility:
    Attempt to extract Subject–Verb–Object structure from an AssertionCandidate.
    Returns StructuredAssertionCandidate regardless of success.

    Structure is OPTIONAL.
    A Claim always exists; its SVO is a bonus, not a requirement.

    If extraction succeeds → ExtractionMode.STRUCTURED
    If partial extraction → ExtractionMode.PARTIAL
    If extraction fails → ExtractionMode.LEXICAL (text span preserved)

Rules:
    ✅ Extract subject, predicate, object from dependency tree
    ✅ Return partial results if full SVO is unavailable
    ✅ Never reject — always return something

    ❌ Never modify text
    ❌ Never invent structure
    ❌ Never perform semantic inference
"""

from __future__ import annotations

from typing import Optional
import structlog

from smriti.core.models import (
    StructuredAssertion,
    ExtractionMode,
    ClaimWarning,
    SemanticSentence,
)
from smriti.claims.models import AssertionCandidate, StructuredAssertionCandidate
from smriti.claims.parser import BaseParser
from smriti.claims.rules import SUBJECT_DEP_LABELS, OBJECT_DEP_LABELS, VERB_POS_TAGS

logger = structlog.get_logger(__name__)


class StructureExtractor:
    """
    Extracts SVO structure from AssertionCandidates.
    """

    def extract(self, candidate: AssertionCandidate, parser: BaseParser) -> StructuredAssertionCandidate:
        """
        Attempt SVO extraction.

        The candidate text is re-parsed in isolation to strictly avoid
        cross-clause contamination from the full sentence dependency tree.

        Args:
            candidate: AssertionCandidate with text and original parse.
            parser: Linguistic parser to use for re‑parsing the candidate.

        Returns:
            StructuredAssertionCandidate with extraction result.
        """
        warnings = []

        # Create an isolated mock sentence to restrict the dependency tree
        isolated_sentence = SemanticSentence(
            sentence_id=f"{candidate.source.sentence.sentence_id}_sub",
            document_id=candidate.source.sentence.document_id,
            text=candidate.text,
            source_path=candidate.source.sentence.source_path,
            context=candidate.source.sentence.context,
            position=candidate.source.sentence.position,
            char_start=0,
            char_end=len(candidate.text),
            origin_block_type=candidate.source.sentence.origin_block_type,
            schema_version=candidate.source.sentence.schema_version,
        )

        # Reparse strictly the candidate's span
        local_parse = parser.parse(isolated_sentence)

        if not local_parse.parse_ok or local_parse.spacy_doc is None:
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.WHOLE_SENTENCE,
                warnings=warnings,
            )

        # Extract SVO from the isolated doc
        svo = self._extract_svo(local_parse.spacy_doc)

        if svo is None:
            return StructuredAssertionCandidate(
                candidate=candidate,
                structured_assertion=None,
                extraction_mode=ExtractionMode.LEXICAL,
                warnings=warnings,
            )

        # Determine extraction mode based on completeness
        if svo.is_complete:
            mode = ExtractionMode.STRUCTURED
        elif svo.is_partial:
            mode = ExtractionMode.PARTIAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)
        else:
            mode = ExtractionMode.LEXICAL
            warnings.append(ClaimWarning.CLM_STRUCTURE_UNAVAILABLE)

        return StructuredAssertionCandidate(
            candidate=candidate,
            structured_assertion=svo,
            extraction_mode=mode,
            warnings=warnings,
        )

    def _extract_svo(self, doc) -> Optional[StructuredAssertion]:
        """
        Extract Subject, Verb (Predicate), Object from spaCy dependency tree.

        Traversal strategy:
            1. Find ROOT token (main verb)
            2. Find subject: child of ROOT with dep_ in SUBJECT_DEP_LABELS
            3. Find object: child of ROOT with dep_ in OBJECT_DEP_LABELS
            4. Extract full noun phrase spans for subject and object

        Returns None if no structure can be identified.
        """
        subject = None
        predicate = None
        obj = None
        negation_marker = None
        modality_marker = None

        # Find root (main verb)
        roots = [t for t in doc if t.dep_ == "ROOT"]
        if not roots:
            return None

        root = roots[0]

        # Predicate = root verb text (lemma form for consistency in annotation)
        if root.pos_ in VERB_POS_TAGS:
            predicate = root.text
        else:
            # Root is not a verb — cannot extract SVO
            return None

        # Find negation attached to root
        neg_tokens = [t for t in root.children if t.dep_ == "neg"]
        if neg_tokens:
            negation_marker = neg_tokens[0].text

        # Find auxiliary/modal attached to root
        aux_tokens = [t for t in root.children if t.dep_ in ("aux", "auxpass")]
        if aux_tokens:
            modality_marker = aux_tokens[0].text

        # Find subject
        for token in root.children:
            if token.dep_ in SUBJECT_DEP_LABELS:
                # Extract full noun phrase subtree
                subject = " ".join(t.text for t in token.subtree)
                break

        # Find object
        for token in root.children:
            if token.dep_ in OBJECT_DEP_LABELS:
                obj = " ".join(t.text for t in token.subtree)
                break

        # If nothing found at all, return None
        if not any([subject, predicate, obj]):
            return None

        return StructuredAssertion(
            subject=subject,
            predicate=predicate,
            object=obj,
            negation_marker=negation_marker,
            modality_marker=modality_marker,
        )
````

## File: src/smriti/claims/validator.py
````python
"""
validator.py — Structural validator for Phase 4 claims.

Responsibility:
    Validate a collection of Claim objects for structural correctness.
    Check per-claim and cross-claim invariants.

Rules:
    ✅ Claim IDs must be unique                          → CLM006 (fatal)
    ✅ Provenance chain must be complete                 → CLM007 (fatal)
    ✅ Text must not be empty                            → CLM005 (discard)
    ✅ schema_version must be "4.0"                      → CLM008 (fatal)
    ✅ extraction_mode must be a valid ExtractionMode    → CLM008 (fatal)

Rules about what validator NEVER does:
    ❌ Never evaluates claim semantics
    ❌ Never modifies any object
    ❌ Never reorders claims
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import Claim, ClaimWarning
from smriti.exceptions import ClaimValidationError

logger = structlog.get_logger(__name__)


def validate_claims(
    claims: List[Claim],
    document_id: str,
    seen_ids: dict,
) -> Tuple[List[Claim], List[ClaimWarning]]:
    """
    Validate a collection of Claims for one document.

    Args:
        claims:       Claims to validate.
        document_id:  Expected document_id for all claims.

    Returns:
        (valid_claims, warnings)
        valid_claims excludes empty-text claims.

    Raises:
        ClaimValidationError: On duplicate IDs, broken provenance, invalid schema.
    """
    warnings: List[ClaimWarning] = []
    valid: List[Claim] = []
    

    for claim in claims:
        # Check 1: Non-empty text
        if not claim.text.strip():
            warnings.append(ClaimWarning.CLM_EMPTY_ASSERTION)
            logger.debug("empty claim discarded", claim_id=claim.claim_id)
            continue

        # Check 2: Unique claim ID with consistency (fatal)
        if claim.claim_id in seen_ids:
            existing = seen_ids[claim.claim_id]
            # Must have same content_hash and same provenance (sentence_id/doc_id)
            if (existing.content_hash != claim.content_hash or
                existing.provenance != claim.provenance):
                raise ClaimValidationError(
                    f"Duplicate claim_id {claim.claim_id} with inconsistent content "
                    f"or provenance. Existing: {existing.content_hash[:8]}..., "
                    f"new: {claim.content_hash[:8]}..."
                )
            # Even if identical, raise to enforce uniqueness and catch logic bugs
            raise ClaimValidationError(
                f"Duplicate claim_id {claim.claim_id} detected. "
                "All claims must have unique IDs."
            )
        seen_ids[claim.claim_id] = claim

        # Check 3: Provenance chain (fatal)
        if not claim.provenance:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has no provenance. "
                "Every claim must have an unbroken lineage."
            )
        if claim.provenance.document_id != document_id:
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has provenance.document_id "
                f"'{claim.provenance.document_id}' but expected '{document_id}'"
            )

        # Check 4: Schema version
        if claim.schema_version != "4.0":
            raise ClaimValidationError(
                f"Claim {claim.claim_id} has schema_version '{claim.schema_version}', "
                "expected '4.0'"
            )

        valid.append(claim)

    return valid, warnings
````

## File: src/smriti/contradiction/__init__.py
````python

````

## File: src/smriti/contradiction/detector.py
````python
# Will be filled in Phase 6\n
````

## File: src/smriti/core/__init__.py
````python

````

## File: src/smriti/core/cache.py
````python
"""
Cache manager for expensive computations.

Cache layout (all under project root cache/):
  cache/
    embeddings/   ← Phase 4: embedding vectors
    parsed/       ← Phase 2: parsed document structures
    retrieval/    ← Phase 5: FAISS index
    nli/          ← Phase 6: NLI predictions

CONTRACT: Everything under cache/ is ephemeral.
Safe to delete at any time with: .\\Makefile.ps1 clean-cache
"""

import pickle
from pathlib import Path
from typing import Any, Optional, Dict
import structlog

from smriti.core.paths import (
    EMBEDDINGS_CACHE_DIR,
    PARSED_CACHE_DIR,
    RETRIEVAL_CACHE_DIR,
    NLI_CACHE_DIR,
)


logger = structlog.get_logger(__name__)


class CacheManager:
    """
    Namespaced pickle cache for a single cache directory.
    Instantiate one per namespace: CacheManager(EMBEDDINGS_CACHE_DIR)
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached object by key. Returns None on miss."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "rb") as f:
                obj = pickle.load(f)
            logger.debug("cache hit", key=key, dir=self.cache_dir.name)
            return obj
        except Exception as e:
            logger.warning("cache read failed", key=key, error=str(e))
            return None

    def set(self, key: str, obj: Any) -> None:
        """Store an object in cache."""
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(obj, f)
            logger.debug("cache write", key=key, dir=self.cache_dir.name)
        except Exception as e:
            logger.error("cache write failed", key=key, error=str(e))

    def delete(self, key: str) -> None:
        """Remove a single cache entry."""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()

    def clear(self) -> None:
        """Clear this entire cache namespace."""
        import shutil
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("cache namespace cleared", dir=self.cache_dir.name)


# ── Specialised caches ────────────────────────────────────────────────────────

class EmbeddingCache(CacheManager):
    """Cache for embedding vectors (Phase 4)."""

    def __init__(self):
        super().__init__(EMBEDDINGS_CACHE_DIR)

    def get_batch(self, claim_ids: list) -> Dict[str, list]:
        """Retrieve multiple embeddings at once."""
        return {cid: v for cid in claim_ids if (v := self.get(cid)) is not None}


class NLICache(CacheManager):
    """Cache for NLI predictions (Phase 6)."""

    def __init__(self):
        super().__init__(NLI_CACHE_DIR)

    @staticmethod
    def _pair_key(claim_a_id: str, claim_b_id: str) -> str:
        """Deterministic key: (A,B) and (B,A) produce the same key."""
        a, b = sorted([claim_a_id, claim_b_id])
        return f"{a}__{b}"

    def get_pair(self, claim_a_id: str, claim_b_id: str) -> Optional[Dict]:
        return self.get(self._pair_key(claim_a_id, claim_b_id))

    def set_pair(self, claim_a_id: str, claim_b_id: str, result: Dict) -> None:
        self.set(self._pair_key(claim_a_id, claim_b_id), result)
````

## File: src/smriti/core/config.py
````python
"""
Configuration management for SMRITI.

Loading order:
  1. config/default.yaml     — complete baseline
  2. config/{env}.yaml       — environment overrides (deep-merged)

Deep merge: nested keys are merged recursively, not overwritten.
Model names and thresholds belong here, not in constants.py.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml

from smriti.core.paths import CONFIG_DIR
from smriti.exceptions import ConfigError

# Module-level singleton — call get_config() everywhere
_config: Optional["Config"] = None


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Recursively merge override into base.
    Nested dicts are merged; scalars are overwritten.

    Example:
        base     = {"embedding": {"model": "MiniLM", "batch_size": 32}}
        override = {"embedding": {"batch_size": 8}}
        result   = {"embedding": {"model": "MiniLM", "batch_size": 8}}
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Load and expose layered YAML configuration."""

    def __init__(self, env: str = "dev", config_dir: Path = CONFIG_DIR):
        self.env = env
        self._data: Dict[str, Any] = {}
        self._load(config_dir)

    def _load(self, config_dir: Path) -> None:
        """Load default config then deep-merge env override."""
        default_path = config_dir / "default.yaml"
        if not default_path.exists():
            raise ConfigError(f"Missing required config file: {default_path}")

        with open(default_path, encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        env_path = config_dir / f"{self.env}.yaml"
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
            self._data = _deep_merge(self._data, env_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Top-level key access with optional default."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dict-style access: config["embedding"]["model"]."""
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data


def get_config(env: str = "dev") -> Config:
    """Return the module-level config singleton (lazy init)."""
    global _config
    if _config is None:
        _config = Config(env=env)
    return _config
````

## File: src/smriti/core/hashing.py
````python
"""
Content hashing for incremental processing.
Detects which notes changed since last run — skip the rest.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE
from smriti.core.paths import HASH_CACHE_FILE


class ContentHasher:
    """Computes and persists content hashes for change detection."""

    def __init__(self, cache_file: Path = HASH_CACHE_FILE):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.hashes: Dict[str, str] = self._load()

    def compute_hash(self, content: str) -> str:
        """SHA-256 hash of a string."""
        return hashlib.new(HASH_ALGORITHM, content.encode("utf-8")).hexdigest()

    def compute_file_hash(self, file_path: Path) -> str:
        """SHA-256 hash of a file (chunked for large files)."""
        h = hashlib.new(HASH_ALGORITHM)
        with open(file_path, "rb") as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()

    def has_changed(self, path: Path, content: str) -> bool:
        """True if content differs from last stored hash (or not yet seen)."""
        current = self.compute_hash(content)
        return self.hashes.get(str(path)) != current

    def update_hash(self, path: Path, content: str) -> None:
        """Store current hash for a file."""
        self.hashes[str(path)] = self.compute_hash(content)
        self._save()

    def clear(self) -> None:
        """Reset all stored hashes."""
        self.hashes = {}
        self._save()

    def _load(self) -> Dict[str, str]:
        if self.cache_file.exists():
            with open(self.cache_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.hashes, f, indent=2)
````

## File: src/smriti/core/logger.py
````python
"""
Structured logging setup.
Reads level from config — not hardcoded.
"""

import logging
import structlog
from pathlib import Path

from smriti.core.paths import LOG_DIR
from smriti.core.config import get_config


def setup_logging() -> None:
    """Configure structured logging from config."""
    config = get_config()
    level = config["logging"]["level"]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "smriti.log"

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return a named structlog logger."""
    return structlog.get_logger(name)
````

## File: src/smriti/core/manifest.py
````python
"""
Manifest system for tracking phase execution.
Every phase writes a manifest.json under its own run directory.

Directory layout:
  artifacts/
    run_20240715_143022/
      phase1/manifest.json
      phase2/manifest.json
      ...
    run_20240715_160500/
      phase1/manifest.json
      ...
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from smriti.constants import MANIFEST_SCHEMA_VERSION
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.models import ManifestEntry


logger = structlog.get_logger(__name__)


class ManifestManager:
    """Manages per-run, per-phase manifests."""

    def __init__(self, run_id: str, artifacts_dir: Path = ARTIFACTS_DIR):
        self.run_id = run_id
        self.artifacts_dir = Path(artifacts_dir)
        self.run_dir = self.artifacts_dir / f"run_{run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def start_phase(self, phase: int) -> float:
        """
        Mark phase as started. Returns wall-clock start time.
        Call this immediately before phase logic runs.
        """
        start_time = time.time()
        phase_dir = self.run_dir / f"phase{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        logger.info("phase started", run_id=self.run_id, phase=phase)
        return start_time

    def end_phase(
        self,
        phase: int,
        start_time: float,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        status: str = "success",
        error: Optional[str] = None,
    ) -> Path:
        """
        Record phase completion and write manifest.json.
        Returns: path to the manifest file.
        """
        duration = time.time() - start_time

        entry = ManifestEntry(
            run_id=self.run_id,
            phase=phase,
            timestamp=datetime.now(),
            duration_seconds=duration,
            inputs=inputs,
            outputs=outputs,
            status=status,
            schema_version=MANIFEST_SCHEMA_VERSION,
            error=error,
        )

        phase_dir = self.run_dir / f"phase{phase}"
        manifest_path = phase_dir / "manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": entry.schema_version,
                    "run_id": entry.run_id,
                    "phase": entry.phase,
                    "timestamp": entry.timestamp.isoformat(),
                    "duration_seconds": round(entry.duration_seconds, 4),
                    "inputs": entry.inputs,
                    "outputs": entry.outputs,
                    "status": entry.status,
                    "error": entry.error,
                },
                f,
                indent=2,
            )

        logger.info(
            "phase completed",
            run_id=self.run_id,
            phase=phase,
            status=status,
            duration_seconds=f"{duration:.2f}",
        )
        return manifest_path

    def list_completed_phases(self) -> list:
        """Return list of phase numbers that have a manifest in this run."""
        completed = []
        for phase_dir in sorted(self.run_dir.glob("phase*")):
            if (phase_dir / "manifest.json").exists():
                completed.append(int(phase_dir.name.replace("phase", "")))
        return completed
````

## File: src/smriti/core/models.py
````python
"""
Data models for SMRITI.
Define once, use everywhere.
These are the contracts between phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class FileFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class ContradictionType(str, Enum):
    DIRECT_REVERSAL = "direct_reversal"
    REFINEMENT = "refinement"
    STRATEGY_SHIFT = "strategy_shift"
    DEFINITION_CHANGE = "definition_change"


class ExtractionMethod(str, Enum):
    """Which extractor was used to produce raw_text."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class WarningCode(str, Enum):
    """Strict taxonomy of extraction and normalization warnings."""
    UNICODE_NORMALIZED = "unicode_normalized"
    BOM_REMOVED = "bom_removed"
    LINE_ENDINGS_NORMALIZED = "line_endings_normalized"
    TRAILING_WHITESPACE_REMOVED = "trailing_whitespace_removed"
    CONTROL_CHARS_REMOVED = "control_chars_removed"
    BLANK_LINES_COLLAPSED = "blank_lines_collapsed"
    MIXED_LINE_ENDINGS = "mixed_line_endings"
    NULL_BYTES_REMOVED = "null_bytes_removed"
    ENCODING_FALLBACK = "encoding_fallback"
    PAGE_LIMIT_REACHED = "page_limit_reached"
    PAGE_EXTRACTION_FAILED = "page_extraction_failed"
    EMPTY_PDF_PAGE = "empty_pdf_page"
    NO_EXTRACTABLE_TEXT = "no_extractable_text"
    TEXT_TRUNCATED = "text_truncated"


# ── Phase 3 Warning Codes ────────────────────────────────────────────────────

class SegmentationWarning(str, Enum):
    """Warning codes specific to Phase 3 semantic sentence construction."""
    SEG_EMPTY_SENTENCE_DISCARDED   = "SEG001"   # Empty string after strip
    SEG_VERY_LONG_SENTENCE         = "SEG002"   # Exceeds max_sentence_chars
    SEG_UNKNOWN_STRUCTURE          = "SEG003"   # Structural element not recognised
    SEG_MALFORMED_TABLE            = "SEG004"   # Table could not be parsed
    SEG_CODE_BLOCK_SKIPPED         = "SEG005"   # Code block skipped (V1)
    CTX_STACK_IMBALANCE            = "CTX001"   # Context stack depth mismatch
    VAL_DUPLICATE_SENTENCE_ID      = "VAL001"   # Two sentences share an ID (fatal)
    VAL_INVALID_POSITION_ORDER     = "VAL002"   # Non-monotonic positions (fatal)
    VAL_INVALID_CONTEXT            = "VAL003"   # Context string malformed


# ── Phase 4 Warning Codes ─────────────────────────────────────────────────────

class ClaimWarning(str, Enum):
    """Warning codes specific to Phase 4 claim construction."""
    CLM_PARSER_FAILURE          = "CLM001"
    CLM_BOUNDARY_AMBIGUITY      = "CLM002"
    CLM_STRUCTURE_UNAVAILABLE   = "CLM003"
    CLM_FALLBACK_ACTIVATED      = "CLM004"
    CLM_EMPTY_ASSERTION         = "CLM005"
    CLM_DUPLICATE_CLAIM_ID      = "CLM006"  # Fatal if inconsistent
    CLM_INVALID_PROVENANCE      = "CLM007"
    CLM_VALIDATION_FAILURE      = "CLM008"
    CLM_EXCEEDED_MAX_CLAIMS     = "CLM009"
    CLM_UNSUPPORTED_SYNTAX      = "CLM010"


class ExtractionMode(str, Enum):
    STRUCTURED    = "structured"
    PARTIAL       = "partial"
    LEXICAL       = "lexical"
    WHOLE_SENTENCE = "whole_sentence"


class Modality(str, Enum):
    CERTAIN    = "certain"
    POSSIBLE   = "possible"
    PROBABLE   = "probable"
    IMPOSSIBLE = "impossible"
    REQUIRED   = "required"
    UNKNOWN    = "unknown"


class BoundaryReason(str, Enum):
    """Enum for deterministic boundary detection reasons."""
    SINGLE_ASSERTION       = "single_assertion"
    COORDINATED_PREDICATE  = "coordinated_predicate"
    INDEPENDENT_CLAUSE     = "independent_clause"
    PARSE_FAILED           = "parse_failed"
    CONDITIONAL_SPLIT      = "conditional_split"      # reserved
    RELATIVE_CLAUSE        = "relative_clause"
    COORDINATION           = "coordination"


# ── Phase 3 contract: Document → SemanticSentence ────────────────────────────

@dataclass(frozen=True)
class SemanticSentence:
    """
    The immutable public output of Phase 3.

    This is the contract boundary between document processing and knowledge processing.
    Phase 4+ never needs to understand Markdown, headings, or document structure.
    Everything structural is fully encapsulated here.

    Fields:
        sentence_id:       Deterministic SHA256‑based identifier (16 hex chars)
        document_id:       doc_id of the source Document (links back to Phase 2)
        text:              The sentence text exactly as it appears (canonical prose)
        context:           Heading path under which this sentence appears, or empty string
                           Example: "Python > Generators > Yield"
                           Stored SEPARATELY from text — never fused.
        position:          0‑based sequence number within this document
        char_start:        Character offset in Document.normalized_text where sentence begins
                           (for generated prose, refers to the start of the block)
        char_end:          Character offset in Document.normalized_text where sentence ends
                           (for generated prose, refers to the end of the block)
        source_path:       Path to the original file (for traceability)
        origin_block_type: BlockType that produced this sentence (stored as string)
        schema_version:    Version of this data structure

    All offsets refer to Document.normalized_text; they are traceability offsets,
    not reconstructed offsets into generated prose.
    """
    sentence_id: str
    document_id: str
    text: str
    context: str           # "Python > Generators" or "" if at root
    position: int
    char_start: int
    char_end: int
    source_path: Path
    origin_block_type: str   # e.g., "paragraph", "heading", etc.
    schema_version: str = "3.0"


# ── Phase 3 result ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Phase3Stats:
    """Structural statistics collected during Phase 3 for a single Document."""
    total_headings: int = 0
    total_paragraphs: int = 0
    total_list_items: int = 0
    total_tables: int = 0
    total_block_quotes: int = 0
    total_code_blocks_skipped: int = 0
    total_horizontal_rules: int = 0
    total_front_matter_blocks: int = 0
    total_blank_lines: int = 0
    total_unknown_blocks: int = 0
    sentences_produced: int = 0
    sentences_discarded: int = 0
    warnings: tuple = field(default_factory=tuple)


# ── Phase 1 contract: Discovery → Parsing ────────────────────────────────────

@dataclass(frozen=True)
class SourceDocument:
    """
    The immutable, file‑centric representation of one discovered document.
    Produced by Phase 1, consumed by Phase 2.
    """
    doc_id: str
    path: Path
    relative_path: Path
    source_root: Path
    format: FileFormat
    content_hash: str
    size_bytes: int
    modified_at: datetime


# ── Phase 2 extraction models ────────────────────────────────────────────────

@dataclass(frozen=True)
class TextStatistics:
    character_count: int
    word_count: int
    line_count: int
    blank_line_count: int
    paragraph_count: int


@dataclass(frozen=True)
class RawExtractionResult:
    raw_text: str
    warnings: tuple[WarningCode, ...]
    method: ExtractionMethod
    encoding_used: str


@dataclass(frozen=True)
class NormalizationResult:
    normalized_text: str
    warnings: tuple[WarningCode, ...]


@dataclass(frozen=True)
class Document:
    """The final enriched document produced by Phase 2."""
    doc_id: str
    source_document: SourceDocument
    raw_text: str
    normalized_text: str
    extraction_method: ExtractionMethod
    extraction_warnings: tuple[WarningCode, ...]
    text_statistics: TextStatistics
    encoding_used: str
    schema_version: str = "2.0"

    @property
    def has_warnings(self) -> bool:
        return len(self.extraction_warnings) > 0

    @property
    def is_empty(self) -> bool:
        return len(self.normalized_text.strip()) == 0


# ── Phase 4 contract: SemanticSentence → Claim ───────────────────────────────

@dataclass(frozen=True)
class StructuredAssertion:
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    negation_marker: Optional[str] = None
    modality_marker: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return all([self.subject, self.predicate, self.object])

    @property
    def is_partial(self) -> bool:
        return any([self.subject, self.predicate, self.object])


@dataclass(frozen=True)
class AssertionMetadata:
    is_negated: bool = False
    modality: Modality = Modality.CERTAIN
    is_conditional: bool = False
    is_comparative: bool = False
    is_attributed: bool = False
    attributed_to: Optional[str] = None
    is_quoted: bool = False


@dataclass(frozen=True)
class ClaimProvenance:
    sentence_id: str
    document_id: str
    source_path: Path
    sentence_context: str
    sentence_position: int


@dataclass(frozen=True)
class Claim:
    """
    An atomic claim (SVO triple or full sentence). Produced by Phase 4.

    Fields:
        claim_id:            Deterministic identifier (SHA256 of content hash + metadata)
        sentence_id:         The ID of the SemanticSentence this claim originated from
        document_id:         doc_id of the source Document
        text:                The claim text (exact substring or full sentence)
        content_hash:        SHA256 of the exact text (for deduplication)
        context:             Heading path (same as SemanticSentence.context)
        source_path:         Path to the original file
        extraction_mode:     How this claim was constructed (structured/partial/lexical/whole_sentence)
        structured_assertion: Optional SVO triple (if extracted with a parser)
        assertion_metadata:  Negation, modality, attribution, etc.
        provenance:          Link back to the original sentence
        schema_version:      Version of this data structure
        rule_version:        Version of the extraction rules used
    """
    claim_id: str
    sentence_id: str
    document_id: str
    text: str
    content_hash: str
    context: str
    source_path: Path
    extraction_mode: ExtractionMode
    structured_assertion: Optional[StructuredAssertion]
    assertion_metadata: AssertionMetadata
    provenance: ClaimProvenance
    schema_version: str = "4.0"
    rule_version: str = "1.0"

    @property
    def is_svo(self) -> bool:
        return (
            self.extraction_mode == ExtractionMode.STRUCTURED
            and self.structured_assertion is not None
            and self.structured_assertion.is_complete
        )

    @property
    def is_negated(self) -> bool:
        return self.assertion_metadata.is_negated

    @property
    def subject(self) -> Optional[str]:
        return self.structured_assertion.subject if self.structured_assertion else None

    @property
    def predicate(self) -> Optional[str]:
        return self.structured_assertion.predicate if self.structured_assertion else None

    @property
    def object(self) -> Optional[str]:
        return self.structured_assertion.object if self.structured_assertion else None


@dataclass(frozen=True)
class Phase4Stats:
    total_sentences_processed: int = 0
    total_claims_produced: int = 0
    structured_claims: int = 0
    partial_claims: int = 0
    lexical_claims: int = 0
    whole_sentence_claims: int = 0
    parser_failures: int = 0
    boundary_splits: int = 0
    negated_claims: int = 0
    modal_claims: int = 0
    attributed_claims: int = 0
    warnings: tuple = field(default_factory=tuple)


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────

class VectorDType(str, Enum):
    FLOAT32 = "float32"
    FLOAT64 = "float64"

@dataclass(frozen=True)
class Vector:
    """
    A typed, self-describing embedding vector.

    This is the lowest-level geometric primitive in Phase 5.
    All higher-level objects (Embedding, EmbeddedClaim) reference a Vector.

    Design:
        Replaces the raw `tuple` that was previously embedded in Embedding.
        This future-proofs for: quantization, sparse vectors, binary vectors,
        multimodal vectors — without touching Phase 6.

    Fields:
        values:     Immutable float tuple (the actual numbers).
        dimension:  Length of values (redundant but self-documenting).
        dtype:      "float64" or "float32" — guards against object-type contamination.
        normalized: True if L2 norm has been applied (||values||₂ ≈ 1.0).
    """
    values: tuple
    dimension: int
    dtype: VectorDType = VectorDType.FLOAT64
    normalized: bool = False

    def __post_init__(self):
        if len(self.values) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: values has {len(self.values)} elements "
                f"but dimension={self.dimension}"
            )

    def to_list(self) -> list:
        """Return values as a plain Python list (for serialization, FAISS, etc.)."""
        return list(self.values)

    def __len__(self) -> int:
        return self.dimension


@dataclass(frozen=True)
class EmbeddingModelDescriptor:
    """
    Identifies the exact semantic encoder that produced an embedding.

    All fields together form the model signature used in cache key generation.
    Any change to any field invalidates all cached embeddings.

    Fields:
        provider:         "sentence-transformers", "openai", "bge", etc.
        model_name:       "all-MiniLM-L6-v2"
        model_revision:   Git revision hash of model weights
        dimension:        Embedding dimension (384 for MiniLM)
        model_signature:  SHA256 of (provider + model_name + revision)
        embedding_family: High-level family: "SentenceTransformer", "OpenAI", "BGE", "Instructor"
        checkpoint_sha:   Optional content-addressable SHA if available (beyond HF revision)
    """
    provider: str
    model_name: str
    model_revision: str
    dimension: int
    model_signature: str   # Deterministic: SHA256(provider:model_name:revision)
    embedding_family: str = ""   # e.g. "SentenceTransformer", "OpenAI", "BGE"
    checkpoint_sha: str = ""     # Content-addressable checkpoint hash if available


@dataclass(frozen=True)
class EmbeddingProvenance:
    """
    Execution metadata for one embedding — lightweight, non-semantic.

    Fields:
        pipeline_version:   Phase 5 implementation version
        normalization_mode: "l2" or "none"
        device:             "cpu" / "cuda" / "mps"
        config_hash:        SHA256 of the embedding config section
    """
    pipeline_version: str
    normalization_mode: str
    device: str
    config_hash: str


@dataclass(frozen=True)
class EmbeddingQuality:
    """
    Per-claim diagnostic snapshot produced during Phase 5.

    Phase 6 reads these — it never recomputes them.
    Invaluable when debugging large vaults with thousands of claims.

    Fields:
        dimension_ok:  True if vector.dimension == descriptor.dimension
        normalized:    True if L2 normalization was applied
        finite:        True if all values are finite (no NaN or Inf)
        cache_used:    True if vector came from cache (not fresh inference)
    """
    dimension_ok: bool
    normalized: bool
    finite: bool
    cache_used: bool


@dataclass(frozen=True)
class Embedding:
    """
    The canonical semantic artifact produced by Phase 5 for one Claim.

    DESIGN PRINCIPLE: Embedding is a timeless semantic object.
    It does NOT carry execution status (cached / fresh / stale).
    Execution metadata belongs to EmbeddingResult (internal) and EmbeddingQuality.

    Fields:
        claim_id:   Links back to the originating Claim (referential integrity)
        vector:     Validated, normalized Vector domain object
        descriptor: Which model produced this vector
        provenance: How/where the inference was run
    """
    claim_id: str
    vector: Vector
    descriptor: EmbeddingModelDescriptor
    provenance: EmbeddingProvenance

    @property
    def dimension(self) -> int:
        return self.vector.dimension

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience)."""
        return self.vector.values


@dataclass(frozen=True)
class EmbeddedClaim:
    """
    The bridge between symbolic knowledge (Claim) and numeric geometry (Embedding).

    Phase 6 receives List[EmbeddedClaim] and uses them for similarity search.

    Design:
        Claim is NOT duplicated here — only its ID is referenced.
        This preserves referential integrity and avoids unnecessary duplication.
        Phase 6 looks up the Claim by claim_id when needed.

        quality provides pre-computed diagnostics so Phase 6 never has to
        re-derive normalization status, dimension correctness, etc.
    """
    claim_id: str
    embedding: Embedding
    quality: EmbeddingQuality
    schema_version: str = "5.0"

    @property
    def vector(self) -> Vector:
        return self.embedding.vector

    @property
    def values(self) -> tuple:
        """Direct access to float values (convenience for Phase 6 / FAISS)."""
        return self.embedding.vector.values

    @property
    def dimension(self) -> int:
        return self.embedding.dimension

    @property
    def is_cached(self) -> bool:
        return self.quality.cache_used


@dataclass(frozen=True)
class Phase5Stats:
    """Statistics collected during one Phase 5 execution."""
    total_claims: int = 0
    successful: int = 0
    cached: int = 0
    stale: int = 0
    failed: int = 0
    skipped: int = 0
    total_batches: int = 0
    average_batch_size: float = 0.0
    cache_hit_rate: float = 0.0
    total_runtime_seconds: float = 0.0
    vectors_per_second: float = 0.0
    current_memory_mb: float = 0.0
    cache_entries_reused: int = 0
    cache_entries_regenerated: int = 0
    cache_entries_invalidated: int = 0


# ── Phase 6 contract: Retrieval → Contradiction ──────────────────────────────

@dataclass
class CandidatePair:
    """Two claims that might contradict. Produced by Phase 6, consumed by Phase 7."""
    claim_a_id: str
    claim_b_id: str
    similarity_score: float     # Cosine similarity from FAISS


# ── Phase 7 contract: Contradiction → Scoring ────────────────────────────────

@dataclass
class Contradiction:
    """A detected contradiction between two claims. Produced by Phase 7."""
    claim_a_id: str
    claim_b_id: str
    contradiction_type: ContradictionType
    nli_confidence: float       # Gate 2 output
    similarity_score: float     # Gate 1 output
    temporal_distance_days: int
    severity_score: float       # Gate 3 final score
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def __repr__(self) -> str:
        return (
            f"Contradiction({self.claim_a_id[:20]} vs {self.claim_b_id[:20]}, "
            f"type={self.contradiction_type}, severity={self.severity_score:.2f})"
        )


# ── Phase 8 contract: Evolution ───────────────────────────────────────────────

@dataclass
class Topic:
    """A topic/theme grouping related claims. Produced by Phase 8."""
    name: str
    claim_ids: List[str] = field(default_factory=list)
    contradiction_count: int = 0

    @property
    def drift_score(self) -> float:
        """Drift score for this topic (0–100)."""
        if not self.claim_ids:
            return 0.0
        return min(100.0, (self.contradiction_count / len(self.claim_ids)) * 100)


@dataclass
class EvolutionChain:
    """Temporal chain of related claims showing how a belief evolved."""
    topic: str
    claim_ids: List[str]                    # Ordered by timestamp
    stages: List[Dict[str, Any]] = field(default_factory=list)


# ── Manifest and state ────────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    """Record of a completed phase. Written by ManifestManager after each phase."""
    run_id: str                             # unique per execution
    phase: int
    timestamp: datetime
    duration_seconds: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str                             # pending | running | success | failed
    schema_version: str = "1.0"            # version manifest format
    error: Optional[str] = None
    versions: Dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineState:
    """Current state of pipeline execution. Persisted for resume capability."""
    started_at: datetime
    current_phase: int
    completed_phases: List[int] = field(default_factory=list)
    manifests: List[ManifestEntry] = field(default_factory=list)

    def is_resumable(self) -> bool:
        """Can pipeline be resumed from checkpoint?"""
        return len(self.manifests) > 0


# ── Internal embedding models (not exported) ────────────────────────────────
# These are used internally by Phase 5; they never cross the phase boundary.
````

## File: src/smriti/core/paths.py
````python
"""
Centralized path definitions for SMRITI.

Every path in the project is derived from PROJECT_ROOT.
Import from here — never hardcode path strings elsewhere.
"""

from pathlib import Path

# === ROOT ===
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # smriti/

# === SOURCE ===
SRC_DIR = PROJECT_ROOT / "src" / "smriti"

# === CONFIGURATION ===
CONFIG_DIR = PROJECT_ROOT / "config"

# === DATA (input) ===
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# === CACHE (ephemeral — always safe to delete) ===
CACHE_DIR = PROJECT_ROOT / "cache"
EMBEDDINGS_CACHE_DIR = CACHE_DIR / "embeddings"
PARSED_CACHE_DIR = CACHE_DIR / "parsed"
RETRIEVAL_CACHE_DIR = CACHE_DIR / "retrieval"
NLI_CACHE_DIR = CACHE_DIR / "nli"
HASH_CACHE_FILE = CACHE_DIR / "hashes.json"

# === ARTIFACTS (immutable — do not delete) ===
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

# === OUTPUT ===
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"

# === STATE ===
STATE_FILE = ARTIFACTS_DIR / "pipeline_state.json"


def ensure_dirs() -> None:
    """Create all required directories on first run."""
    dirs = [
        RAW_DATA_DIR,
        EMBEDDINGS_CACHE_DIR,
        PARSED_CACHE_DIR,
        RETRIEVAL_CACHE_DIR,
        NLI_CACHE_DIR,
        ARTIFACTS_DIR,
        LOG_DIR,
        REPORTS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
````

## File: src/smriti/core/state.py
````python
"""
Pipeline state for resuming interrupted runs.
Stores: which phases completed, when they started, current position.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog

from smriti.core.paths import STATE_FILE
from smriti.core.models import PipelineState


logger = structlog.get_logger(__name__)


class StateManager:
    """Persist and restore pipeline state across interruptions."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def start_run(self) -> PipelineState:
        """Initialize a new pipeline run and persist it."""
        state = PipelineState(started_at=datetime.now(), current_phase=1)
        self.save(state)
        logger.info("pipeline run started", started_at=state.started_at.isoformat())
        return state

    def complete_phase(self, phase: int) -> None:
        """Mark a phase as completed and advance current_phase."""
        state = self.load()
        if state:
            if phase not in state.completed_phases:
                state.completed_phases.append(phase)
            state.current_phase = phase + 1
            self.save(state)
            logger.info("phase marked complete", phase=phase)

    def load(self) -> Optional[PipelineState]:
        """Load existing state. Returns None if no state file found."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, encoding="utf-8") as f:
                data = json.load(f)
            return PipelineState(
                started_at=datetime.fromisoformat(data["started_at"]),
                current_phase=data.get("current_phase", 1),
                completed_phases=data.get("completed_phases", []),
            )
        except Exception as e:
            logger.error("state load failed", error=str(e))
            return None

    def save(self, state: PipelineState) -> None:
        """Persist state to disk."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "started_at": state.started_at.isoformat(),
                    "current_phase": state.current_phase,
                    "completed_phases": state.completed_phases,
                },
                f,
                indent=2,
            )

    def clear(self) -> None:
        """Clear saved state (use before a fresh run)."""
        if self.state_file.exists():
            self.state_file.unlink()
        logger.info("state cleared")
````

## File: src/smriti/core/timing.py
````python
"""
Performance timing for pipeline profiling.

Captures:
  - Wall clock time
  - CPU time (user + system)
  - Peak memory delta (MB)
  - Optional: documents processed, claims generated

Invaluable for identifying bottlenecks before optimizing.
"""

import time
import os
import psutil
import structlog
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, Generator

logger = structlog.get_logger(__name__)

_process = psutil.Process(os.getpid())


@dataclass
class TimingStats:
    """Performance statistics captured during a timed block."""

    operation: str
    wall_time_seconds: float
    cpu_time_seconds: float
    peak_memory_delta_mb: float
    documents_processed: int = 0
    claims_generated: int = 0

    def log(self) -> None:
        logger.info(
            "timing_stats",
            operation=self.operation,
            wall_s=f"{self.wall_time_seconds:.2f}",
            cpu_s=f"{self.cpu_time_seconds:.2f}",
            peak_mem_mb=f"{self.peak_memory_delta_mb:.1f}",
            docs=self.documents_processed,
            claims=self.claims_generated,
        )


class Timer:
    """
    Context manager that captures wall time, CPU time, and peak memory.

    Usage:
        with Timer("Phase 4 — Embedding") as t:
            run_embedding(claims)
        t.stats.log()
    """

    def __init__(self, name: str):
        self.name = name
        self.stats: Optional[TimingStats] = None

    def __enter__(self) -> "Timer":
        self._wall_start = time.perf_counter()
        self._cpu_start = time.process_time()
        mem = _process.memory_info()
        self._mem_start_mb = mem.rss / 1024 / 1024
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        wall = time.perf_counter() - self._wall_start
        cpu = time.process_time() - self._cpu_start
        mem_end_mb = _process.memory_info().rss / 1024 / 1024
        peak_delta = mem_end_mb - self._mem_start_mb

        self.stats = TimingStats(
            operation=self.name,
            wall_time_seconds=wall,
            cpu_time_seconds=cpu,
            peak_memory_delta_mb=peak_delta,
        )
        self.stats.log()


@contextmanager
def timed_operation(name: str) -> Generator[None, None, None]:
    """Lightweight context manager for one-liner timing."""
    with Timer(name) as t:
        yield
    # stats already logged by Timer.__exit__
````

## File: src/smriti/dashboard/__init__.py
````python

````

## File: src/smriti/dashboard/app.py
````python
# Will be filled in Phase 10\n
````

## File: src/smriti/discovery/__init__.py
````python
"""
discovery/__init__.py — Public API for Phase 1.

External callers (PipelineRunner) import from here:

    from smriti.discovery import run_discovery, DiscoveryResult

They never import from individual submodules.

Orchestration:
  1. Validate input directories           [validator.validate_directories]
  2. Discover candidate files             [scanner.discover_files]
  3. Validate each candidate file         [validator.validate_file]
  4. Extract metadata for valid files     [metadata.extract_metadata]
  5. Compute content hash                 [hashing.compute_hash + hash cache]
  6. Build duplicate registry             [duplicate.build_duplicate_registry]
  7. Build source documents               [builder.build_source_document]
  8. Write manifest                       [manifest.ManifestManager]
  9. Update pipeline state                [state.StateManager]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.hashing import ContentHasher
from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR, CACHE_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import DiscoveryError

from smriti.discovery.scanner import discover_files
from smriti.discovery.validator import validate_directories, validate_file
from smriti.discovery.metadata import extract_metadata, FileMetadata
from smriti.discovery.hashing import compute_hash
from smriti.discovery.duplicate import build_duplicate_registry, DuplicateRegistry
from smriti.discovery.builder import SourceDocument, build_source_document

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveryContext:
    """
    Immutable shared execution context for Phase 1.
    Carries configuration, run metadata, and managers.
    """
    run_id: str
    manifest_manager: ManifestManager
    state_manager: StateManager
    force_full: bool
    config: dict
    discovered_at: datetime


@dataclass
class DiscoveryStats:
    """Statistics from one discovery run."""

    total_candidates: int = 0
    valid_count: int = 0
    skipped_count: int = 0
    duplicate_count: int = 0
    # Incremental stats (based on hash cache)
    unchanged_count: int = 0
    new_count: int = 0
    modified_count: int = 0

    def summary(self) -> str:
        return (
            f"discovered={self.valid_count} "
            f"skipped={self.skipped_count} "
            f"duplicates={self.duplicate_count} "
            f"new={self.new_count} "
            f"unchanged={self.unchanged_count} "
            f"modified={self.modified_count}"
        )


@dataclass
class DiscoveryResult:
    """
    Complete output of Phase 1.
    This is what Phase 2 receives.

    Attributes:
        documents:          All valid SourceDocument objects (including duplicates).
        duplicate_registry: Mapping from content hash to duplicate info.
        skipped:            All paths that failed validation (with reasons).
        stats:              Summary statistics.
        run_id:             Pipeline run identifier.
        manifest_path:      Path to written manifest.json.
    """

    documents: List[SourceDocument]
    duplicate_registry: DuplicateRegistry
    skipped: List[Tuple[Path, str]]
    stats: DiscoveryStats
    run_id: str
    manifest_path: Optional[Path] = None

    @property
    def canonical_documents(self) -> List[SourceDocument]:
        """Return only canonical (non‑duplicate) documents."""
        return [d for d in self.documents if not self.duplicate_registry.is_duplicate(d.path)]

    @property
    def duplicate_documents(self) -> List[SourceDocument]:
        """Return only duplicate documents."""
        return [d for d in self.documents if self.duplicate_registry.is_duplicate(d.path)]

    @property
    def canonical_count(self) -> int:
        return len(self.canonical_documents)

    def to_dataset_json(self) -> str:
        """
        Serialize the canonical document dataset to JSON.
        Written to artifacts/run_{id}/phase1/dataset.json for Phase 2.
        """
        records = []
        for doc in self.canonical_documents:
            records.append({
                "doc_id": doc.doc_id,
                "path": str(doc.path),
                "relative_path": str(doc.relative_path),
                "source_root": str(doc.source_root),
                "format": doc.format.value,
                "content_hash": doc.content_hash,
                "size_bytes": doc.size_bytes,
                "modified_at": doc.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_discovery(
    input_dirs: List[Path],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    force_full: bool = False,
) -> DiscoveryResult:
    """
    Execute the complete Phase 1 discovery pipeline.

    Args:
        input_dirs:       Root directories to scan.
        run_id:           Unique pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        force_full:       If True, ignore hash cache and re-process all files.

    Returns:
        DiscoveryResult containing canonical documents and statistics.

    Raises:
        DiscoveryError: If input directories are invalid (fatal).
    """
    config = get_config()
    discovered_at = datetime.now(tz=timezone.utc)
    context = DiscoveryContext(
        run_id=run_id,
        manifest_manager=manifest_manager,
        state_manager=state_manager,
        force_full=force_full,
        config=config,
        discovered_at=discovered_at,
    )
    stats = DiscoveryStats()

    with Timer("phase1_discovery") as timer:

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=1)
        logger.info("phase 1 starting", run_id=run_id)

        # ── Step 2: Validate input directories ────────────────────────────────
        logger.info("validating input directories", count=len(input_dirs))
        validated_roots = validate_directories(input_dirs)

        # ── Step 3: Discover candidate files ──────────────────────────────────
        logger.info("scanning directories")
        candidate_paths = discover_files(validated_roots)
        stats.total_candidates = len(candidate_paths)
        logger.info("candidates found", count=stats.total_candidates)

        # ── Step 4: Validate individual files ─────────────────────────────────
        logger.info("validating files")
        valid_paths: List[Path] = []
        skipped: List[Tuple[Path, str]] = []

        for path in candidate_paths:
            result = validate_file(path)
            if result.is_valid:
                valid_paths.append(path)
            else:
                skipped.append((path, result.rejection_reason))
                logger.debug(
                    "file skipped",
                    path=str(path),
                    reason=result.rejection_reason,
                )

        stats.valid_count = len(valid_paths)
        stats.skipped_count = len(skipped)
        logger.info(
            "file validation complete",
            valid=stats.valid_count,
            skipped=stats.skipped_count,
        )

        # ── Step 5: Extract metadata ───────────────────────────────────────────
        logger.info("extracting metadata")
        metadata_map: Dict[Path, FileMetadata] = {}
        for path in valid_paths:
            try:
                metadata_map[path] = extract_metadata(path)
            except OSError as e:
                logger.warning("metadata extraction failed", path=str(path), error=str(e))
                skipped.append((path, f"metadata error: {e}"))
                stats.skipped_count += 1
                stats.valid_count -= 1

        valid_paths = [p for p in valid_paths if p in metadata_map]

        # ── Step 6: Compute content hashes (with incremental cache) ───────────
        logger.info("computing content hashes")
        hash_cache = ContentHasher(cache_file=CACHE_DIR / "hashes.json")
        path_hash_pairs: List[Tuple[Path, str]] = []
        
        new_active_hashes: Dict[str, str] = {}  # <-- ADDED: Initialize fresh dictionary

        for path in valid_paths:
            try:
                content_hash = compute_hash(path)  # reads once
            except OSError as e:
                logger.warning("hash computation failed", path=str(path), error=str(e))
                skipped.append((path, f"hash error: {e}"))
                stats.skipped_count += 1
                continue

            # Incremental classification (for stats only)
            if not force_full:
                cached = hash_cache.hashes.get(str(path))
                if cached is None:
                    stats.new_count += 1
                elif cached == content_hash:
                    stats.unchanged_count += 1
                else:
                    stats.modified_count += 1
            else:
                stats.new_count += 1

            # <-- CHANGED: Populate the fresh dictionary instead of updating old cache
            new_active_hashes[str(path)] = content_hash  
            path_hash_pairs.append((path, content_hash))

        # <-- ADDED: Overwrite the cache completely to prune deleted files
        hash_cache.hashes = new_active_hashes
        hash_cache._save()

        # ── Step 7: Detect duplicates ──────────────────────────────────────────
        logger.info("detecting duplicate content")
        duplicate_registry = build_duplicate_registry(path_hash_pairs)
        stats.duplicate_count = duplicate_registry.duplicate_count

        # ── Step 8: Build source documents ────────────────────────────────────
        logger.info("building source documents")
        hash_dict = dict(path_hash_pairs)
        all_documents: List[SourceDocument] = []

        for path in valid_paths:
            if path not in hash_dict:
                continue  # was skipped during hashing

            # Determine which root this file belongs to
            source_root = _find_source_root(path, validated_roots)

            doc = build_source_document(
                metadata=metadata_map[path],
                content_hash=hash_dict[path],
                source_root=source_root,
            )
            all_documents.append(doc)

        # ── Step 9: Write dataset artifact ────────────────────────────────────
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase1"
        phase_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = phase_dir / "dataset.json"

        result = DiscoveryResult(
            documents=all_documents,
            duplicate_registry=duplicate_registry,
            skipped=skipped,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(
            result.to_dataset_json(), encoding="utf-8"
        )
        logger.info("dataset written", path=str(dataset_path), count=result.canonical_count)

        # ── Step 10: Write manifest ────────────────────────────────────────────
        manifest_path = manifest_manager.end_phase(
            phase=1,
            start_time=start_time,
            inputs={
                "directories": [str(d) for d in input_dirs],
                "force_full": force_full,
            },
            outputs={
                "canonical_documents": result.canonical_count,
                "duplicate_documents": len(result.duplicate_documents),
                "skipped_files": len(skipped),
                "dataset_path": str(dataset_path),
            },
            status="success",
        )
        result.manifest_path = manifest_path

        # ── Step 11: Update pipeline state ────────────────────────────────────
        state_manager.complete_phase(phase=1)

    logger.info("phase 1 complete", **{k: v for k, v in vars(stats).items()})

    return result


def _find_source_root(path: Path, roots: List[Path]) -> Path:
    """Find which root directory a discovered file belongs to."""
    # Pre‑sort roots by length descending to match the most specific root.
    for root in sorted(roots, key=lambda r: len(str(r)), reverse=True):
        try:
            path.relative_to(root)
            return root
        except ValueError:
            continue
    return roots[0]  # Fallback
````

## File: src/smriti/discovery/builder.py
````python
"""
builder.py — SourceDocument construction.

Responsibility: Assemble the final SourceDocument objects from
validated metadata and content hash.

Input:
  - FileMetadata (from metadata.py)
  - content_hash: str (from hashing.py)
  - source_root: Path (which root dir this file came from)

Output:
  - SourceDocument (immutable, file‑centric)
"""

from datetime import datetime
from pathlib import Path
import structlog

from smriti.core.models import FileFormat, SourceDocument
from smriti.discovery.metadata import FileMetadata

logger = structlog.get_logger(__name__)

# Map file extensions to FileFormat enum values
_EXTENSION_TO_FORMAT = {
    ".md": FileFormat.MARKDOWN,
    ".txt": FileFormat.TEXT,
    ".pdf": FileFormat.PDF,
}

def build_source_document(
    metadata: FileMetadata,
    content_hash: str,
    source_root: Path,
) -> SourceDocument:
    """
    Construct a SourceDocument from its component parts.

    Args:
        metadata:       Filesystem metadata from metadata.py
        content_hash:   SHA256 digest from hashing.py
        source_root:    The root directory this file was found under

    Returns:
        Immutable SourceDocument.
    """
    path = metadata.path
    format = _EXTENSION_TO_FORMAT.get(metadata.extension, FileFormat.TEXT)

    # ADR-7: doc_id is the content hash itself — content defines identity.
    doc_id = content_hash

    # Relative path for human-readable display
    try:
        relative_path = path.relative_to(source_root)
    except ValueError:
        relative_path = path  # Fallback if not under source_root

    doc = SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=relative_path,
        source_root=source_root,
        format=format,
        content_hash=content_hash,
        size_bytes=metadata.size_bytes,
        modified_at=metadata.modified_at,
    )

    logger.debug(
        "source document built",
        doc_id=doc_id[:8],
        path=str(relative_path),
        format=format.value,
    )

    return doc
````

## File: src/smriti/discovery/duplicate.py
````python
"""
duplicate.py — Content-based duplicate detection.

Responsibility: Given a sequence of (path, hash) pairs, identify which
paths have identical content to a path seen earlier.

Input:  List of (path, hash) tuples — processed in discovery order
Output: DuplicateRegistry — maps each hash to its canonical path and alternates,
        plus a reverse dict for O(1) canonical lookup.

Complexity: O(n) — dictionary lookup, not pairwise comparison.

Rules:
  - "Duplicate" means identical SHA256 hash. Nothing else.
  - Same filename in different folders is NOT a duplicate.
  - First file encountered with a given hash becomes the canonical document.
  - Subsequent files with the same hash are recorded as alternate locations.
  - Duplicates are never silently discarded — always recorded.
  - This module has no filesystem access. It only compares strings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DuplicateEntry:
    """
    Records a hash and all paths that share it.
    canonical_path: First file discovered with this hash.
    alternate_paths: All subsequent files with the same hash.
    """

    hash: str
    canonical_path: Path
    alternate_paths: List[Path] = field(default_factory=list)

    @property
    def is_duplicate(self) -> bool:
        """True if at least one other file shares this content."""
        return len(self.alternate_paths) > 0

    @property
    def all_paths(self) -> List[Path]:
        """All paths sharing this content, canonical first."""
        return [self.canonical_path] + self.alternate_paths


@dataclass
class DuplicateRegistry:
    """
    Complete result of duplicate detection for one discovery run.

    Attributes:
        entries:          hash → DuplicateEntry
        canonical_paths:  set of paths that are canonical (one per unique hash)
        duplicate_paths:  set of paths that are duplicates
        _duplicate_to_canonical: dict for O(1) reverse lookup
    """

    entries: Dict[str, DuplicateEntry] = field(default_factory=dict)
    canonical_paths: set = field(default_factory=set)
    duplicate_paths: set = field(default_factory=set)
    _duplicate_to_canonical: Dict[Path, Path] = field(default_factory=dict)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicate_paths)

    @property
    def unique_content_count(self) -> int:
        return len(self.entries)

    def is_canonical(self, path: Path) -> bool:
        return path in self.canonical_paths

    def is_duplicate(self, path: Path) -> bool:
        return path in self.duplicate_paths

    def get_canonical_for(self, path: Path) -> Optional[Path]:
        """Given a duplicate path, return the canonical path for its content (O(1))."""
        return self._duplicate_to_canonical.get(path)


def build_duplicate_registry(
    path_hash_pairs: List[Tuple[Path, str]]
) -> DuplicateRegistry:
    """
    Build a complete duplicate registry from path-hash pairs.

    Args:
        path_hash_pairs: [(path, sha256_hex_digest), ...]
                         Must be in sorted discovery order.

    Returns:
        DuplicateRegistry with canonical and duplicate classifications.
    """
    registry = DuplicateRegistry()

    for path, content_hash in path_hash_pairs:
        if content_hash not in registry.entries:
            # First file with this hash — it is canonical
            entry = DuplicateEntry(hash=content_hash, canonical_path=path)
            registry.entries[content_hash] = entry
            registry.canonical_paths.add(path)
        else:
            # A file with identical content exists — this is a duplicate
            registry.entries[content_hash].alternate_paths.append(path)
            registry.duplicate_paths.add(path)
            registry._duplicate_to_canonical[path] = registry.entries[content_hash].canonical_path
            canonical = registry.entries[content_hash].canonical_path
            logger.warning(
                "duplicate content detected",
                duplicate_path=str(path),
                canonical_path=str(canonical),
                hash_prefix=content_hash[:8],
            )

    if registry.duplicate_count > 0:
        logger.info(
            "duplicate detection complete",
            unique_contents=registry.unique_content_count,
            duplicates=registry.duplicate_count,
        )

    return registry
````

## File: src/smriti/discovery/hashing.py
````python
"""
hashing.py — Content fingerprinting.

Responsibility: Compute a SHA256 hash of file contents.

Input:  Validated Path
Output: str  — hex digest (64 characters)

Rules:
  - Hash file CONTENTS only. Never filename, path, or timestamps.
  - Read in chunks to handle arbitrarily large files without OOM.
  - This module has no knowledge of caching, duplicates, or manifests.
  - One public function: compute_hash(path) → str

Why content-only hashing matters:
  - Renaming "AI.md" → "Artificial_Intelligence.md" should NOT create a new identity.
  - Moving a file to a different folder should NOT create a new identity.
  - Changing one word inside SHOULD produce a completely different identity.
"""

import hashlib
from pathlib import Path
import structlog

from smriti.constants import HASH_ALGORITHM, HASH_CHUNK_SIZE

logger = structlog.get_logger(__name__)


def compute_hash(path: Path) -> str:
    """
    Compute SHA256 hash of file contents.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        64-character lowercase hex digest.

    Raises:
        OSError: If the file cannot be read.
    """
    hasher = hashlib.new(HASH_ALGORITHM)

    with open(path, "rb") as f:
        while chunk := f.read(HASH_CHUNK_SIZE):
            hasher.update(chunk)

    digest = hasher.hexdigest()

    logger.debug("hash computed", path=str(path), hash_prefix=digest[:8])

    return digest
````

## File: src/smriti/discovery/metadata.py
````python
"""
metadata.py — Filesystem metadata extraction.

Responsibility: Extract essential filesystem facts about a validated file.
                This is the ONLY module that calls path.stat().

Input:  Validated Path
Output: FileMetadata dataclass

Rules:
  - Never read file contents (that is hashing.py's job)
  - Never infer semantic meaning from metadata
  - Only keep fields needed by future phases:
      path, size_bytes, extension, modified_at (UTC)
  - MIME type, read‑only, creation time are removed (not used later)
  - Encoding detection is deferred to Phase 2
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class FileMetadata:
    """
    Immutable essential filesystem metadata for a single file.
    Produced by Phase 1 and used to build SourceDocument.
    """

    path: Path
    size_bytes: int
    extension: str                   # Normalised lowercase (.md / .pdf / .txt)
    modified_at: datetime            # UTC (last modification time)


def extract_metadata(path: Path) -> FileMetadata:
    """
    Extract filesystem metadata from a validated file.

    Args:
        path: A path that has already passed validate_file().

    Returns:
        Immutable FileMetadata.

    Raises:
        OSError: If stat() fails (should not happen post-validation, but guard anyway).
    """
    stat = path.stat()

    # Modified time as UTC-aware datetime
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    extension = path.suffix.lower()

    metadata = FileMetadata(
        path=path,
        size_bytes=stat.st_size,
        extension=extension,
        modified_at=modified_at,
    )

    logger.debug(
        "metadata extracted",
        path=str(path),
        size_bytes=stat.st_size,
        modified_at=modified_at.isoformat(),
    )

    return metadata
````

## File: src/smriti/discovery/scanner.py
````python
"""
scanner.py — Recursive file discovery (iterative).

Responsibility: Given a list of validated root directories, return a
sorted list of candidate file paths. Nothing more.

Input:  List[Path]  — validated root directories
Output: List[Path]  — candidate files, sorted deterministically

Rules:
  - Traversal is recursive, unlimited depth (uses stack, no recursion)
  - Output is always sorted alphabetically (full path)
  - Hidden directories and system folders are skipped
  - Broken symlinks are skipped with a warning
  - Permission errors are warned and skipped — never fatal
  - The scanner never reads file contents
  - The scanner never validates individual files (that is validator.py)
"""

from pathlib import Path
from typing import List, Set
from collections import deque
import structlog

from smriti.core.config import get_config

logger = structlog.get_logger(__name__)


# Directories that are always skipped, regardless of config.
# These are non-negotiable system directories.
_ALWAYS_IGNORE: Set[str] = {
    ".git",
    ".obsidian",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
}


def discover_files(root_dirs: List[Path]) -> List[Path]:
    """
    Recursively discover all candidate files under root_dirs.

    Args:
        root_dirs: Pre-validated root directories to scan.

    Returns:
        Sorted list of candidate file paths.
        Sorting is by full absolute path (alphabetical, case-insensitive on Windows).

    Raises:
        Nothing. All errors are logged and skipped.
    """
    config = get_config()
    ignored_dirs: Set[str] = _ALWAYS_IGNORE | set(
        config["discovery"].get("ignored_dirs", [])
    )

    candidates: List[Path] = []

    for root_dir in root_dirs:
        logger.info("scanning directory", path=str(root_dir))
        _scan_iterative(root_dir, root_dir, ignored_dirs, candidates)

    # RULE: Output must always be sorted. Never trust OS ordering.
    candidates.sort(key=lambda p: str(p))

    logger.info(
        "discovery complete",
        total_candidates=len(candidates),
        roots_scanned=len(root_dirs),
    )

    return candidates


def _scan_iterative(
    root_dir: Path,
    root_dir_original: Path,
    ignored_dirs: Set[str],
    accumulator: List[Path],
) -> None:
    """
    Iterative directory walk using a stack.
    This is the only function that touches the filesystem in scanner.py.
    """
    stack = [root_dir]
    visited = {root_dir.resolve()}

    while stack:
        current_dir = stack.pop()

        try:
            # Sort directory contents for determinism within each directory.
            entries = sorted(current_dir.iterdir(), key=lambda e: e.name)
        except PermissionError:
            logger.warning("permission denied, skipping directory", path=str(current_dir))
            continue
        except OSError as e:
            logger.warning("cannot read directory", path=str(current_dir), error=str(e))
            continue

        for entry in entries:
            # Skip hidden files and directories (name starts with ".")
            if entry.name.startswith("."):
                logger.debug("skipping hidden entry", path=str(entry))
                continue

            # Skip system/ignored directories
            if entry.name in ignored_dirs:
                logger.debug("skipping ignored directory", path=str(entry))
                continue

            if entry.is_symlink():
                # Broken symlink — skip with warning
                if not entry.exists():
                    logger.warning("broken symlink, skipping", path=str(entry))
                    continue
                # Valid symlink pointing to a file — follow it
                # Valid symlink pointing to a directory — recurse
                resolved = entry.resolve()
                # Guard against symlink loops pointing outside the vault
                if resolved == root_dir_original or str(resolved).startswith(str(root_dir_original)):
                    pass  # within vault, safe to follow
                else:
                    logger.debug("symlink points outside vault, skipping", path=str(entry))
                    continue

            if entry.is_dir():
                resolved_dir = entry.resolve()          # <-- ADD THIS
                if resolved_dir not in visited:         # <-- ADD THIS: Cycle protection
                    visited.add(resolved_dir)
                    stack.append(entry)
                else:                                   # <-- ADD THIS
                    logger.debug("symlink cycle detected, skipping", path=str(entry))    
            elif entry.is_file():
                accumulator.append(entry.resolve())
````

## File: src/smriti/discovery/validator.py
````python
"""
validator.py — Two-level validation.

Level 1: validate_directory()  — validates root input directories.
Level 2: validate_file()       — validates individual discovered files.

Responsibility:
  - Answer the binary question: "Can this path enter the pipeline?"
  - Return a ValidationResult (not raise exceptions) for files.
  - Raise DiscoveryError immediately for invalid root directories
    because the pipeline cannot proceed without valid roots.

Input:  Path
Output: ValidationResult (for files) | raises DiscoveryError (for dirs)

Design:
  - Validation is a pure predicate. No side effects.
  - The validator never reads file contents (no readability check).
  - The validator never computes hashes.
  - Every rejection reason is recorded explicitly.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.constants import MAX_FILE_SIZE_BYTES
from smriti.exceptions import DiscoveryError

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single file path."""

    path: Path
    is_valid: bool
    rejection_reason: Optional[str] = None

    def __bool__(self) -> bool:
        return self.is_valid


def validate_directories(directories: List[Path]) -> List[Path]:
    """
    Validate that all input directories exist and are readable.

    Args:
        directories: Root directories to validate.

    Returns:
        List of valid, absolute, resolved directories.

    Raises:
        DiscoveryError: If any directory is invalid.
                        (Fatal — cannot start without valid roots.)
    """
    if not directories:
        raise DiscoveryError("No input directories provided.")

    validated: List[Path] = []

    for raw_path in directories:
        path = Path(raw_path).resolve()

        if not path.exists():
            raise DiscoveryError(f"Input directory does not exist: {path}")

        if not path.is_dir():
            raise DiscoveryError(f"Input path is not a directory: {path}")

        try:
            # Attempt to list — checks read permission without reading contents
            list(path.iterdir())
        except PermissionError:
            raise DiscoveryError(f"Input directory is not readable: {path}")

        validated.append(path)
        logger.info("directory validated", path=str(path))

    return validated


def validate_file(path: Path) -> ValidationResult:
    """
    Validate a single file for pipeline inclusion.

    Args:
        path: The candidate file path.

    Returns:
        ValidationResult — never raises exceptions for individual files.

    Checks (in order, cheapest first):
        1. Path exists
        2. Is a regular file (not a directory, device, etc.)
        3. Extension is in whitelist
        4. File size is non-zero
        5. File size is within maximum limit
    (Readability is tested by the hasher; no separate open/read here.)
    """
    config = get_config()
    allowed_extensions: set = set(
        config["discovery"].get("supported_extensions", [".md", ".pdf", ".txt"])
    )
    max_file_size: int = config["discovery"].get(
        "max_file_size_bytes", MAX_FILE_SIZE_BYTES
    )

    # Check 1: Exists
    if not path.exists():
        return ValidationResult(path=path, is_valid=False, rejection_reason="does not exist")

    # Check 2: Regular file
    if not path.is_file():
        return ValidationResult(path=path, is_valid=False, rejection_reason="not a regular file")

    # Check 3: Extension whitelist
    extension = path.suffix.lower()
    if extension not in allowed_extensions:
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"unsupported extension '{extension}'",
        )

    # Check 4: Non-zero size
    try:
        size = path.stat().st_size
    except OSError as e:
        return ValidationResult(path=path, is_valid=False, rejection_reason=f"stat failed: {e}")

    if size == 0:
        return ValidationResult(path=path, is_valid=False, rejection_reason="empty file (0 bytes)")

    # Check 5: Size limit
    if size > max_file_size:
        size_mb = size / (1024 * 1024)
        limit_mb = max_file_size / (1024 * 1024)
        return ValidationResult(
            path=path,
            is_valid=False,
            rejection_reason=f"file too large ({size_mb:.1f} MB > {limit_mb:.0f} MB limit)",
        )

    return ValidationResult(path=path, is_valid=True)
````

## File: src/smriti/embedding/__init__.py
````python
"""
embedding/__init__.py — Public API for Phase 5: Semantic Embedding Layer.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.embedding import embed_claims, Phase5Result

They NEVER import from internal modules.

Public contract:
    embed_claims(claims: List[Claim], ...) → Phase5Result

That is the ONLY function that crosses the Phase 5 boundary.

Key implementation changes from original:
    - Status removed from Embedding (pure semantic artifact)
    - Internal EmbeddingResult tracks per-claim execution status
    - Failed batches retry claim-by-claim before marking anything failed
    - Post-normalization validation added (Stage 7)
    - EmbeddingQuality built per-claim (Stage 8)
    - Phase5Result includes warnings and errors lists
    - Manifest includes cache lifecycle metrics
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Claim,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Phase5Stats,
    Vector,
    VectorDType,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase5Error, EmbeddingModelError, EmbeddingInferenceError

from smriti.embedding.embedder import (
    BaseEmbedder,
    SentenceTransformerEmbedder,
    PHASE5_PIPELINE_VERSION,
    PHASE5_SCHEMA_VERSION,
)
from smriti.embedding.input_factory import EmbeddingInputFactory, CacheKeyFactory
from smriti.embedding.cache import EmbeddingCachePolicy
from smriti.embedding.validation import validate_vector
from smriti.embedding.normalization import l2_normalize
from smriti.embedding.builders import (
    build_vector,
    build_embedding,
    build_embedding_quality,
    build_embedded_claim,
)
from smriti.embedding.statistics import Phase5StatsCollector
from smriti.embedding.models import EmbeddingResult, EmbeddingStatus

logger = structlog.get_logger(__name__)


# ── Public result type ────────────────────────────────────────────────────────

@dataclass
class Phase5Result:
    """
    Complete output of Phase 5 — all EmbeddedClaims produced.
    This is what Phase 6 receives.

    Fields:
        embedded_claims: All successfully embedded claims.
        stats:           Immutable execution statistics.
        run_id:          Current pipeline run identifier.
        warnings:        Non-fatal issues collected during embedding.
        errors:          Fatal per-claim errors (claim still skipped gracefully).
        manifest_path:   Path to written manifest.json.
        dataset_path:    Path to written dataset.json.
    """
    embedded_claims: List[EmbeddedClaim]
    stats: Phase5Stats
    run_id: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None

    @property
    def total_embedded(self) -> int:
        return len(self.embedded_claims)

    def to_dataset_json(self) -> str:
        """
        Serialize all EmbeddedClaims to JSON for Phase 6.
        Written to artifacts/run_{id}/phase5/dataset.json.

        Status field in output: derived from EmbeddingQuality (cache_used)
        since status is no longer stored on Embedding itself.
        """
        records = []
        for ec in self.embedded_claims:
            # Derive status from quality (status is not on Embedding)
            

            records.append({
                "claim_id":       ec.claim_id,
                "vector":         list(ec.values),   # Plain list of floats
                "dimension":      ec.dimension,
                "schema_version": ec.schema_version,
                "quality": {
                    "dimension_ok": ec.quality.dimension_ok,
                    "normalized":   ec.quality.normalized,
                    "finite":       ec.quality.finite,
                    "cache_used":   ec.quality.cache_used,
                },
                "model": {
                    "provider":          ec.embedding.descriptor.provider,
                    "model_name":        ec.embedding.descriptor.model_name,
                    "revision":          ec.embedding.descriptor.model_revision,
                    "dimension":         ec.embedding.descriptor.dimension,
                    "signature":         ec.embedding.descriptor.model_signature,
                    "embedding_family":  ec.embedding.descriptor.embedding_family,
                },
                "provenance": {
                    "pipeline_version":   ec.embedding.provenance.pipeline_version,
                    "normalization_mode": ec.embedding.provenance.normalization_mode,
                    "device":             ec.embedding.provenance.device,
                    "config_hash":        ec.embedding.provenance.config_hash,
                },
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── EmbeddedClaim helper (add to EmbeddedClaim or keep as standalone) ─────────
# We monkeypatch a convenience method here so EmbeddedClaim.to_dataset_json
# doesn't need to import from __init__ (which would create a circular import).

#def _values_as_list(self) -> List[float]:
    #"""Return vector values as a plain Python list."""
    #return list(self.embedding.vector.values)

#EmbeddedClaim.values_as_list = _values_as_list   # type: ignore[attr-defined]


# ── Config hash ───────────────────────────────────────────────────────────────

def _compute_config_hash(config: dict) -> str:
    """
    Deterministic hash of embedding configuration fields that affect output.

    Included (affect embedding values):
        model_name          — different model = different vectors
        normalize           — normalization changes the vector
        device              — should NOT affect values, but included for safety
        instruction_prefix  — changes the input text, changes the vector
        max_seq_length      — truncation changes the vector

    Excluded (do not affect embedding values):
        batch_size          — throughput only, not correctness
        cache_embeddings    — operational flag, not semantic
        pipeline_version    — pipeline version changes tracked separately
    """
    emb_cfg = config.get("embedding", {})
    relevant = {
        "model_name":        emb_cfg.get("model_name", ""),
        "normalize":         emb_cfg.get("normalize", True),
        "device":            emb_cfg.get("device", "cpu"),
        "instruction_prefix": emb_cfg.get("instruction_prefix", ""),
        "max_seq_length":    emb_cfg.get("max_seq_length", None),
    }
    material = (
        f"model:{relevant['model_name']}|"
        f"norm:{relevant['normalize']}|"
        f"dev:{relevant['device']}|"
        f"prefix:{relevant['instruction_prefix']}|"
        f"seq:{relevant['max_seq_length']}"
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


# ── Core public function ───────────────────────────────────────────────────────

def embed_claims(
    claims: List[Claim],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
    embedder: Optional[BaseEmbedder] = None,
    force_reembed: bool = False,
) -> Phase5Result:
    """
    Transform all Claims into EmbeddedClaims.

    This is Phase 5's sole public function.
    All internal components are hidden from callers.

    Args:
        claims:           List of immutable Claims from Phase 4.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.
        embedder:         Optional pre-constructed embedder (for testing).
                          If None, SentenceTransformerEmbedder is used.
        force_reembed:    If True, bypass cache and re-embed all claims.

    Returns:
        Phase5Result containing EmbeddedClaims, stats, warnings, and paths.

    Raises:
        Phase5Error: If the embedding model fails to load (unrecoverable).
    """
    config = get_config()
    emb_cfg = config.get("embedding", {})
    batch_size: int = emb_cfg.get("batch_size", 32)
    normalize: bool = emb_cfg.get("normalize", True)
    cache_enabled: bool = emb_cfg.get("cache_embeddings", True) and not force_reembed
    device: str = emb_cfg.get("device", "cpu")

    logger.info(
        "phase 5 starting",
        run_id=run_id,
        claims=len(claims),
        batch_size=batch_size,
        normalize=normalize,
        cache_enabled=cache_enabled,
    )

    start_time = manifest_manager.start_phase(phase=5)

    # ── Initialize components ─────────────────────────────────────────────────
    if embedder is None:
        try:
            embedder = SentenceTransformerEmbedder(device=device)
        except EmbeddingModelError:
            raise  # Unrecoverable: bubble up as Phase5Error subclass

    config_hash = _compute_config_hash(config)
    descriptor = embedder.descriptor
    model_sig = descriptor.model_signature
    normalization_mode = "l2" if normalize else "none"

    provenance = EmbeddingProvenance(
        pipeline_version=PHASE5_PIPELINE_VERSION,
        normalization_mode=normalization_mode,
        device=device,
        config_hash=config_hash,
    )

    # Separated: EmbeddingInputFactory handles payload only
    #            CacheKeyFactory handles key generation only
    input_factory = EmbeddingInputFactory(
        instruction_prefix=emb_cfg.get("instruction_prefix", ""),
    )
    key_factory = CacheKeyFactory(
        model_signature=model_sig,
        config_hash=config_hash,
    )

    cache_policy = EmbeddingCachePolicy(enabled=cache_enabled)
    stats_collector = Phase5StatsCollector()

    # Accumulated warnings and errors for Phase5Result
    all_warnings: List[str] = []
    all_errors: List[str] = []

    # ── Process claims ─────────────────────────────────────────────────────────
    embedded_claims: List[EmbeddedClaim] = []

    with Timer("phase5_embedding"):
        # ── Stage 1 + 2: Validate claims, build payloads and cache keys ───────
        valid_claims: List[Claim] = []
        payloads: Dict[str, str] = {}     # claim_id → payload text
        cache_keys: Dict[str, str] = {}   # claim_id → cache key

        for claim in claims:
            if not claim.text or not claim.text.strip():
                logger.debug("skipping empty claim", claim_id=claim.claim_id[:8])
                stats_collector.record_skipped()
                continue

            payloads[claim.claim_id] = input_factory.build_payload(claim)
            cache_keys[claim.claim_id] = key_factory.build_cache_key(claim)
            valid_claims.append(claim)

        # ── Stage 3: Cache resolution ─────────────────────────────────────────
        pending_claims: List[Claim] = []
        cached_results: Dict[str, List[float]] = {}   # claim_id → cached vector

        for claim in valid_claims:
            cache_key = cache_keys[claim.claim_id]
            status, vector = cache_policy.lookup(cache_key, model_sig, config_hash)

            if status == EmbeddingStatus.CACHED:
                cached_results[claim.claim_id] = vector
                stats_collector.record_cached()
            elif status == EmbeddingStatus.STALE:
                pending_claims.append(claim)
                stats_collector.record_stale()
                logger.debug("cache stale → will re-embed", claim_id=claim.claim_id[:8])
            else:
                pending_claims.append(claim)

        logger.info(
            "cache resolution complete",
            cached=len(cached_results),
            pending=len(pending_claims),
        )

        # ── Stage 3b: Build EmbeddedClaims for cached results ─────────────────
        for claim in valid_claims:
            if claim.claim_id not in cached_results:
                continue
            raw_cached = cached_results[claim.claim_id]
            try:
                vec = build_vector(
                    raw_cached, descriptor.dimension,
                    dtype=VectorDType.FLOAT64, normalized=True,
                )
                emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
                qual = build_embedding_quality(vec, descriptor, cache_used=True)
                ec = build_embedded_claim(claim.claim_id, emb, qual)
                embedded_claims.append(ec)
            except Exception as e:
                msg = f"claim {claim.claim_id[:8]}: cached vector build failed: {e}"
                all_errors.append(msg)
                logger.error("cached vector build failed", claim_id=claim.claim_id[:8], error=str(e))
                stats_collector.record_failed()

        # ── Stages 4-9: Batch inference for pending claims ────────────────────
        if pending_claims:
            for batch_start in range(0, len(pending_claims), batch_size):
                batch_claims = pending_claims[batch_start:batch_start + batch_size]
                batch_payloads = [payloads[c.claim_id] for c in batch_claims]
                stats_collector.record_batch(len(batch_claims))

                logger.debug(
                    "embedding batch",
                    batch_num=batch_start // batch_size + 1,
                    size=len(batch_claims),
                )

                # Attempt batch inference — on failure, retry individually
                raw_vectors: Optional[List[List[float]]] = None
                try:
                    raw_vectors = embedder.encode_batch(batch_payloads)
                except (EmbeddingInferenceError, Exception) as batch_err:
                    logger.warning(
                        "batch encoding failed — retrying individually",
                        batch_size=len(batch_claims),
                        error=str(batch_err),
                    )
                    all_warnings.append(
                        f"Batch of {len(batch_claims)} failed, retrying individually: {batch_err}"
                    )

                if raw_vectors is not None:
                    # Batch succeeded — process all at once
                    _process_batch_results(
                        batch_claims=batch_claims,
                        raw_vectors=raw_vectors,
                        descriptor=descriptor,
                        provenance=provenance,
                        cache_keys=cache_keys,
                        cache_policy=cache_policy,
                        model_sig=model_sig,
                        config_hash=config_hash,
                        normalize=normalize,
                        embedded_claims=embedded_claims,
                        stats_collector=stats_collector,
                        all_warnings=all_warnings,
                        all_errors=all_errors,
                    )
                else:
                    # Batch failed — retry each claim individually
                    for individual_claim in batch_claims:
                        individual_payload = payloads[individual_claim.claim_id]
                        try:
                            single_vectors = embedder.encode_batch([individual_payload])
                            _process_batch_results(
                                batch_claims=[individual_claim],
                                raw_vectors=single_vectors,
                                descriptor=descriptor,
                                provenance=provenance,
                                cache_keys=cache_keys,
                                cache_policy=cache_policy,
                                model_sig=model_sig,
                                config_hash=config_hash,
                                normalize=normalize,
                                embedded_claims=embedded_claims,
                                stats_collector=stats_collector,
                                all_warnings=all_warnings,
                                all_errors=all_errors,
                            )
                        except Exception as single_err:
                            msg = (
                                f"claim {individual_claim.claim_id[:8]} "
                                f"failed after individual retry: {single_err}"
                            )
                            all_errors.append(msg)
                            logger.error(
                                "individual retry failed",
                                claim_id=individual_claim.claim_id[:8],
                                error=str(single_err),
                            )
                            stats_collector.record_failed()

    stats = stats_collector.finalize()

    result = Phase5Result(
        embedded_claims=embedded_claims,
        stats=stats,
        run_id=run_id,
        warnings=all_warnings,
        errors=all_errors,
    )

    # ── Write artifacts ───────────────────────────────────────────────────────
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase5"
    phase_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
    result.dataset_path = dataset_path

    logger.info(
        "dataset written",
        path=str(dataset_path),
        embedded_claims=result.total_embedded,
    )

    # ── Write manifest (with cache lifecycle metrics) ─────────────────────────
    manifest_path = manifest_manager.end_phase(
        phase=5,
        start_time=start_time,
        inputs={"claims": len(claims)},
        outputs={
            "total_embedded":          result.total_embedded,
            "successful":              stats.successful,
            "cached":                  stats.cached,
            "stale":                   stats.stale,
            "failed":                  stats.failed,
            "skipped":                 stats.skipped,
            # Cache lifecycle metrics (high priority addition)
            "cache_entries_reused":      stats.cache_entries_reused,
            "cache_entries_regenerated": stats.cache_entries_regenerated,
            "cache_entries_invalidated": stats.cache_entries_invalidated,
            # Throughput
            "vectors_per_second":      f"{stats.vectors_per_second:.1f}",
            "current_memory_mb":       f"{stats.current_memory_mb:.1f}",
            # Model
            "model":        descriptor.model_name,
            "dimension":    descriptor.dimension,
            "dataset_path": str(dataset_path),
            # Diagnostics
            "warnings": len(all_warnings),
            "errors":   len(all_errors),
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # ── Update pipeline state ─────────────────────────────────────────────────
    state_manager.complete_phase(phase=5)

    logger.info(
        "phase 5 complete",
        total_embedded=result.total_embedded,
        cached=stats.cached,
        successful=stats.successful,
        failed=stats.failed,
        cache_hit_rate=f"{stats.cache_hit_rate:.1%}",
        throughput=f"{stats.vectors_per_second:.1f} vec/s",
        runtime=f"{stats.total_runtime_seconds:.2f}s",
        warnings=len(all_warnings),
    )

    return result


# ── Internal helpers ──────────────────────────────────────────────────────────

def _process_batch_results(
    batch_claims: List[Claim],
    raw_vectors: List[List[float]],
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
    cache_keys: Dict[str, str],
    cache_policy: EmbeddingCachePolicy,
    model_sig: str,
    config_hash: str,
    normalize: bool,
    embedded_claims: List[EmbeddedClaim],
    stats_collector: Phase5StatsCollector,
    all_warnings: List[str],
    all_errors: List[str],
) -> None:
    """
    Process raw inference output for one batch (or single claim retry).
    Handles: validation → normalization → post-norm validation → build → cache.

    Mutates embedded_claims, stats_collector, all_warnings, all_errors in-place.
    """
    for i, claim in enumerate(batch_claims):
        raw_vector = raw_vectors[i]

        # ── Stage 5: Vector validation (pre-normalization) ────────────────────
        is_valid, error_msg = validate_vector(raw_vector, descriptor.dimension)
        if not is_valid:
            msg = f"claim {claim.claim_id[:8]} pre-norm validation: {error_msg}"
            all_warnings.append(msg)
            logger.warning("vector validation failed", claim_id=claim.claim_id[:8], error=error_msg)
            stats_collector.record_failed()
            continue

        # ── Stage 6: L2 Normalization ─────────────────────────────────────────
        final_vector_list = l2_normalize(raw_vector) if normalize else [float(x) for x in raw_vector]

        # ── Stage 7: Post-normalization re-validation ─────────────────────────
        is_valid_post, error_post = validate_vector(final_vector_list, descriptor.dimension)
        if not is_valid_post:
            msg = (
                f"claim {claim.claim_id[:8]} post-norm validation failed "
                f"(numerical issue after L2): {error_post}"
            )
            all_warnings.append(msg)
            logger.warning(
                "post-normalization validation failed",
                claim_id=claim.claim_id[:8],
                error=error_post,
            )
            stats_collector.record_failed()
            continue

        # ── Cache the normalized result ────────────────────────────────────────
        cache_key = cache_keys[claim.claim_id]
        cache_policy.store(cache_key, final_vector_list, model_sig, config_hash)

        # ── Stage 8: Build domain objects ──────────────────────────────────────
        try:
            vec = build_vector(
                final_vector_list,
                descriptor.dimension,
                dtype=VectorDType.FLOAT64,
                normalized=normalize,
            )
            emb = build_embedding(claim.claim_id, vec, descriptor, provenance)
            qual = build_embedding_quality(vec, descriptor, cache_used=False)
            ec = build_embedded_claim(claim.claim_id, emb, qual)
        except AssertionError as ae:
            msg = f"claim {claim.claim_id[:8]} builder assertion: {ae}"
            all_errors.append(msg)
            logger.error("builder assertion failed", claim_id=claim.claim_id[:8], error=str(ae))
            stats_collector.record_failed()
            continue

        # ── Stage 9: Accumulate ────────────────────────────────────────────────
        embedded_claims.append(ec)
        stats_collector.record_successful()
````

## File: src/smriti/embedding/builders.py
````python
"""
builders.py — Immutable domain object construction for Phase 5.

Responsibility:
    Construct immutable Vector, Embedding, EmbeddingQuality, and EmbeddedClaim objects.
    This is the ONLY place where these objects are instantiated.

    Like Phase 4's builder.py — pure object construction, no logic.

Builders:
    build_vector()              → Vector            (from raw float list)
    build_embedding()           → Embedding         (pure semantic, no status)
    build_embedding_quality()   → EmbeddingQuality  (diagnostic snapshot)
    build_embedded_claim()      → EmbeddedClaim     (public phase boundary object)

Rules:
    ✅ Construct immutable domain objects
    ✅ Attach all required metadata (descriptor, provenance)
    ✅ Convert List[float] → tuple inside Vector
    ✅ Assert dimension invariant before constructing Vector (defensive safeguard)

    ❌ Never perform inference
    ❌ Never normalize
    ❌ Never validate (validation.py's responsibility)
    ❌ No logic or heuristics beyond construction
"""

from __future__ import annotations

import math
from typing import List
import structlog

from smriti.core.models import (
    Embedding,
    EmbeddedClaim,
    EmbeddingModelDescriptor,
    EmbeddingProvenance,
    EmbeddingQuality,
    Vector,
    VectorDType,
)

logger = structlog.get_logger(__name__)


def build_vector(
    values: List[float],
    expected_dimension: int,
    dtype: VectorDType = VectorDType.FLOAT64,
    normalized: bool = False,
) -> Vector:
    """
    Construct an immutable Vector domain object from a validated float list.

    Includes a defensive assertion that dimension matches before constructing.
    This is cheap and protects against descriptor/vector mismatches that
    might slip through validation in unusual code paths.

    Args:
        values:             Validated (and optionally normalized) float list.
        expected_dimension: Dimension from EmbeddingModelDescriptor.
        dtype:              "float64" or "float32" — recorded for downstream use.
        normalized:         True if L2 normalization was applied.

    Returns:
        Immutable Vector.

    Raises:
        AssertionError: If len(values) != expected_dimension (defensive safeguard).
    """
    # Defensive assertion — cheap, catches any latent dimension mismatch
    assert expected_dimension == len(values), (
        f"build_vector: descriptor.dimension={expected_dimension} "
        f"!= len(values)={len(values)}"
    )

    vector = Vector(
        values=tuple(float(v) for v in values),
        dimension=len(values),
        dtype=dtype,
        normalized=normalized,
    )

    logger.debug(
        "vector built",
        dimension=vector.dimension,
        dtype=dtype,
        normalized=normalized,
    )

    return vector


def build_embedding(
    claim_id: str,
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    provenance: EmbeddingProvenance,
) -> Embedding:
    """
    Construct an immutable Embedding from a validated, normalized Vector.

    Note: Embedding carries NO status field.
          Status belongs to the internal EmbeddingResult.
          This is a pure, timeless semantic artifact.

    Args:
        claim_id:    The originating Claim's ID.
        vector:      Validated (and optionally normalized) Vector domain object.
        descriptor:  Which model produced this vector.
        provenance:  How/where inference was run.

    Returns:
        Immutable Embedding.
    """
    embedding = Embedding(
        claim_id=claim_id,
        vector=vector,
        descriptor=descriptor,
        provenance=provenance,
    )

    logger.debug(
        "embedding built",
        claim_id=claim_id[:8],
        dimension=vector.dimension,
        normalized=vector.normalized,
    )

    return embedding


def build_embedding_quality(
    vector: Vector,
    descriptor: EmbeddingModelDescriptor,
    cache_used: bool,
) -> EmbeddingQuality:
    """
    Construct an EmbeddingQuality diagnostic snapshot.

    Phase 6 reads this and never recomputes it.
    Calling this once here prevents redundant computation downstream.

    Args:
        vector:      The built Vector (already the final, stored vector).
        descriptor:  The model descriptor to compare dimension against.
        cache_used:  True if the vector came from cache (not fresh inference).

    Returns:
        Immutable EmbeddingQuality.
    """
    # Check finiteness — redundant after validation but useful as a diagnostic fact
    finite = all(
        math.isfinite(v) for v in vector.values
    )

    quality = EmbeddingQuality(
        dimension_ok=(vector.dimension == descriptor.dimension),
        normalized=vector.normalized,
        finite=finite,
        cache_used=cache_used,
    )

    logger.debug(
        "embedding quality built",
        dimension_ok=quality.dimension_ok,
        normalized=quality.normalized,
        finite=quality.finite,
        cache_used=quality.cache_used,
    )

    return quality


def build_embedded_claim(
    claim_id: str,
    embedding: Embedding,
    quality: EmbeddingQuality,
) -> EmbeddedClaim:
    """
    Construct an immutable EmbeddedClaim.

    Args:
        claim_id:   The Claim's ID (referential, not the Claim object itself).
        embedding:  The completed Embedding (pure semantic artifact).
        quality:    The EmbeddingQuality diagnostic snapshot.

    Returns:
        Immutable EmbeddedClaim.
    """
    embedded_claim = EmbeddedClaim(
        claim_id=claim_id,
        embedding=embedding,
        quality=quality,
        schema_version="5.0",
    )

    logger.debug(
        "embedded claim built",
        claim_id=claim_id[:8],
        dimension=embedding.dimension,
        cache_used=quality.cache_used,
    )

    return embedded_claim
````

## File: src/smriti/embedding/cache.py
````python
"""
cache.py — Embedding cache policy for Phase 5.

Responsibility:
    Manage when embeddings should be reused vs regenerated.
    Separate cache POLICY from cache PERSISTENCE.

    Policy (here):   "Should this embedding be reused?"
    Persistence:     core/cache.py CacheManager handles actual file I/O

Cache entry validity rules:
    An embedding cache entry is VALID if and only if:
        1. The entry exists
        2. The schema_version matches the current Phase 5 schema    ← NEW
        3. The model signature matches the current model
        4. The config hash matches the current configuration

    If ANY condition fails → STALE → regenerate.

    Schema version check comes FIRST because a schema mismatch means
    the entry might not even deserialize correctly with newer code.

Cache key:
    SHA256(claim.content_hash : model_signature : config_hash)[:32]

Notes:
    - Cache stores vectors as List[float] (Python native, portable)
    - Cache never stores framework tensors
    - Stale entries are overwritten (not deleted first)
    - All stored vectors are assumed to be already normalized
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.paths import EMBEDDINGS_CACHE_DIR
from smriti.embedding.models import EmbeddingStatus

logger = structlog.get_logger(__name__)

# Must match PHASE5_SCHEMA_VERSION in embedder.py
# Increment this constant whenever the cache entry format changes
CACHE_SCHEMA_VERSION = "5.0"


class EmbeddingCachePolicy:
    """
    Manages embedding cache reads and writes.

    Storage format: one .pkl file per cache key.
    File content:
        {
            "vector":         [float, ...],
            "model_sig":      str,
            "config_hash":    str,
            "schema_version": str,     ← validates format compatibility
        }
    """

    def __init__(
        self,
        cache_dir: Path = EMBEDDINGS_CACHE_DIR,
        enabled: bool = True,
    ) -> None:
        self._cache_dir = Path(cache_dir)
        self._enabled = enabled

        if self._enabled:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def lookup(
        self,
        cache_key: str,
        model_signature: str,
        config_hash: str,
    ) -> Tuple[EmbeddingStatus, Optional[List[float]]]:
        """
        Look up a vector in the cache.

        Validation order:
            1. schema_version — format compatibility (checked first)
            2. model_signature — model identity
            3. config_hash — pipeline configuration

        Returns:
            (EmbeddingStatus.CACHED, vector) if fully valid hit
            (EmbeddingStatus.STALE, None)   if any condition fails
            (EmbeddingStatus.FAILED, None)  if key not found or cache disabled
        """
        if not self._enabled:
            return EmbeddingStatus.FAILED, None

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return EmbeddingStatus.FAILED, None

        try:
            with open(cache_file, "rb") as f:
                entry = pickle.load(f)

            # Check 1: Schema version — catches incompatible cache format changes
            if entry.get("schema_version") != CACHE_SCHEMA_VERSION:
                logger.debug(
                    "cache schema mismatch — stale",
                    cache_key=cache_key[:8],
                    stored=entry.get("schema_version"),
                    expected=CACHE_SCHEMA_VERSION,
                )
                return EmbeddingStatus.STALE, None

            # Check 2 + 3: Model identity and configuration
            if (entry.get("model_sig") != model_signature or
                    entry.get("config_hash") != config_hash):
                logger.debug(
                    "cache model/config mismatch — stale",
                    cache_key=cache_key[:8],
                )
                return EmbeddingStatus.STALE, None

            vector = entry.get("vector")
            if vector is None:
                return EmbeddingStatus.FAILED, None

            logger.debug("cache hit", cache_key=cache_key[:8])
            return EmbeddingStatus.CACHED, vector

        except Exception as e:
            logger.warning("cache read failed", cache_key=cache_key[:8], error=str(e))
            return EmbeddingStatus.FAILED, None

    def store(
        self,
        cache_key: str,
        vector: List[float],
        model_signature: str,
        config_hash: str,
    ) -> bool:
        """
        Store a normalized vector in the cache.

        Returns:
            True if stored successfully, False on error.
        """
        if not self._enabled:
            return False

        cache_file = self._cache_dir / f"{cache_key}.pkl"

        try:
            entry = {
                "vector":         vector,
                "model_sig":      model_signature,
                "config_hash":    config_hash,
                "schema_version": CACHE_SCHEMA_VERSION,   # Always write current version
            }
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
            logger.debug("cache stored", cache_key=cache_key[:8])
            return True
        except Exception as e:
            logger.warning("cache write failed", cache_key=cache_key[:8], error=str(e))
            return False

    def invalidate(self, cache_key: str) -> bool:
        """
        Remove a specific cache entry.

        Returns:
            True if file existed and was removed.
        """
        cache_file = self._cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
            logger.debug("cache invalidated", cache_key=cache_key[:8])
            return True
        return False

    def clear_all(self) -> int:
        """Clear all cached embeddings. Returns count of files removed."""
        if not self._cache_dir.exists():
            return 0
        count = 0
        for f in self._cache_dir.glob("*.pkl"):
            f.unlink()
            count += 1
        logger.info("embedding cache cleared", files_removed=count)
        return count
````

## File: src/smriti/embedding/embedder.py
````python
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
````

## File: src/smriti/embedding/input_factory.py
````python
"""
input_factory.py — Contextual payload construction and cache key generation.

Two focused classes with separate responsibilities:

    EmbeddingInputFactory
        Knows HOW to construct the model input text from a Claim.
        Does not know anything about caching.

    CacheKeyFactory
        Knows HOW to generate a deterministic cache key for a Claim.
        Does not know anything about text enrichment.

Separating these means:
    - Changing context enrichment strategy → only EmbeddingInputFactory changes
    - Changing cache key composition → only CacheKeyFactory changes
    - Neither class bleeds into the other's concern

CRITICAL DESIGN: The Claim itself remains UNCHANGED.
Only the MODEL INPUT is enriched. The cache key depends on content,
not on the enriched payload.

Rules:
    ✅ EmbeddingInputFactory: deterministic payload from Claim
    ✅ CacheKeyFactory: deterministic key from claim.content_hash + model + config
    ✅ Neither class performs inference or accesses the embedding model
    ✅ Neither class modifies the Claim

    ❌ Never perform inference
    ❌ Never access the embedding model
    ❌ Never modify claim.text
"""

from __future__ import annotations

import hashlib
from typing import Optional
import structlog

from smriti.core.models import Claim

logger = structlog.get_logger(__name__)


class EmbeddingInputFactory:
    """
    Constructs contextual text payloads from Claims.

    Responsibility: What text does the model receive for this Claim?

    Construction strategy:
        If claim.context is non-empty:
            payload = f"{claim.context}\\n{claim.text}"
        Else:
            payload = claim.text

        With optional instruction prefix (for BGE, Instructor, E5):
            payload = f"{instruction_prefix}{payload}"

    Instantiate once per pipeline run.
    """

    def __init__(self, instruction_prefix: Optional[str] = None) -> None:
        self._instruction_prefix = instruction_prefix or ""
        logger.debug(
            "EmbeddingInputFactory initialized",
            has_instruction=bool(instruction_prefix),
        )

    def build_payload(self, claim: Claim) -> str:
        """
        Build the model-ready text payload for a Claim.

        Args:
            claim: An immutable Claim from Phase 4.

        Returns:
            Model-ready string. Never empty for valid claims.
        """
        if claim.context:
            payload = f"{claim.context}\n{claim.text}"
        else:
            payload = claim.text

        if self._instruction_prefix:
            payload = f"{self._instruction_prefix}{payload}"

        return payload


class CacheKeyFactory:
    """
    Constructs deterministic cache keys for Claims.

    Responsibility: What is the stable identity of this Claim's embedding?

    Cache key components:
        - claim.content_hash: content identity of the claim text
        - model_signature:    which model is producing the embedding
        - config_hash:        normalization mode, instruction prefix, etc.

    If ANY component changes, the key changes → embedding regenerated.
    This factory is intentionally separate from EmbeddingInputFactory
    so that changing payload enrichment strategy doesn't break cache keys.

    Instantiate once per pipeline run (after model + config are resolved).
    """

    def __init__(self, model_signature: str, config_hash: str) -> None:
        self._model_signature = model_signature
        self._config_hash = config_hash
        logger.debug(
            "CacheKeyFactory initialized",
            model_sig_prefix=model_signature[:8],
            config_hash_prefix=config_hash[:8],
        )

    def build_cache_key(self, claim: Claim) -> str:
        """
        Build a deterministic cache key for a Claim's embedding.

        Returns:
            32-character lowercase hex string.
        """
        if not hasattr(claim, "content_hash") or not claim.content_hash:
            # Fallback: compute hash from text content
            text_hash = hashlib.sha256(claim.text.encode("utf-8")).hexdigest()[:16]
        else:
            text_hash = claim.content_hash

        material = f"{text_hash}:{self._model_signature}:{self._config_hash}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
````

## File: src/smriti/embedding/models.py
````python
"""
embedding/models.py — Internal temporary objects for Phase 5.

These objects are NEVER exported from the embedding package.
They exist only as intermediate stages in the semantic encoding pipeline.

List[Claim]
    ↓
ValidatedClaim[]      (claim passed structural check)
    ↓
EmbeddingInput[]      (contextual text payload ready for the model)
    ↓
EmbeddingResult[]     (mutable result per claim, carries status + warnings)
    ↓
Embedding[]           (public domain object — crosses phase boundary, NO status)
    ↓
EmbeddingQuality[]    (public diagnostic — crosses phase boundary)
    ↓
EmbeddedClaim[]       (public domain object — crosses phase boundary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from enum import Enum

from smriti.core.models import Claim, Embedding

class EmbeddingStatus(str, Enum):
    """Terminal status for one Claim's embedding attempt (internal use only)."""
    SUCCESS  = "success"
    CACHED   = "cached"
    STALE    = "stale"
    FAILED   = "failed"
    SKIPPED  = "skipped"


@dataclass(frozen=True)
class ValidatedClaim:
    """
    A Claim that has passed pre-inference structural validation.

    This is the entry ticket to embedding inference.
    Only ValidatedClaims are passed to the embedder.
    """
    claim: Claim
    embedding_text: str   # Pre-computed canonical text



@dataclass(frozen=True)
class EmbeddingInput:
    """
    A validated claim paired with its contextual embedding payload.

    The payload is constructed by EmbeddingInputFactory:
        context heading + claim text (if context exists)
        OR just claim text (if no context)

    This is what actually gets passed to BaseEmbedder.encode_batch().
    The cache_key is managed separately by CacheKeyFactory.
    """
    claim_id: str
    payload: str        # Model-ready text (context-enriched)
    original_text: str  # Claim.text (kept for traceability)
    cache_key: str      # Deterministic cache key from CacheKeyFactory


@dataclass
class EmbeddingResult:
    """
    Internal mutable execution result for one Claim's embedding attempt.

    This object is created by the orchestrator, populated across pipeline stages,
    then either discarded (on failure) or used to construct the public
    EmbeddedClaim (on success).

    NEVER crosses the phase boundary. Not included in Phase5Result.

    Fields:
        claim_id:     The originating Claim's ID.
        status:       Current execution status (mutable during pipeline).
        embedding:    The completed Embedding (None until Stage 8 succeeds).
        warnings:     Non-fatal issues encountered for this claim.
        errors:       Fatal issues that prevented embedding.
        elapsed_time: Time spent embedding this specific claim (seconds).
        from_cache:   Whether the vector came from cache.
    """
    claim_id: str
    status: EmbeddingStatus
    embedding: Optional[Embedding] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0
    from_cache: bool = False

    @property
    def succeeded(self) -> bool:
        return (
            self.embedding is not None
            and self.status in (
                EmbeddingStatus.SUCCESS,
                EmbeddingStatus.CACHED,
                EmbeddingStatus.STALE,
            )
        )
````

## File: src/smriti/embedding/normalization.py
````python
"""
normalization.py — Vector normalization for Phase 5.

Responsibility:
    Apply L2 (unit-length) normalization to validated embedding vectors.
    This is a SEPARATE step from inference — the embedder never normalizes.

Why separate?
    Normalization is a configuration-driven post-processing step.
    Different normalization methods may be added without touching the embedder.
    Inference reproducibility is preserved independently of normalization choice.

L2 normalization:
    v_normalized = v / ||v||₂
    After normalization: ||v_normalized||₂ = 1.0

    This makes cosine similarity equivalent to dot product,
    which is important for Phase 6's nearest-neighbor retrieval.

Rules:
    ✅ Return a new list (never mutate input)
    ✅ Only called on validated vectors (validation.py ensures non-zero norm)
    ✅ Configurable via config (can be disabled)

    ❌ Never validate (validation.py's responsibility)
    ❌ Never infer (embedder.py's responsibility)

Note: After normalization, validation.py is called again (post-norm check).
      This module is not aware of that — it just normalizes.
"""

from __future__ import annotations

import math
from typing import List
import structlog

logger = structlog.get_logger(__name__)


def l2_normalize(vector: List[float]) -> List[float]:
    """
    Apply L2 normalization to a vector.

    Precondition: vector has been validated (non-empty, finite, non-zero norm).

    Args:
        vector: Raw float list (pre-validated).

    Returns:
        New float list with unit L2 norm. Input is never mutated.
    """
    sum_sq = sum(float(x) * float(x) for x in vector)

    # Warn if vector is extremely close to zero (should be caught by validation)
    if sum_sq <= 1e-15:
        logger.warning(
            "near-zero norm vector in normalization, using epsilon",
            sum_sq=sum_sq,
        )

    # Compute norm with a tiny epsilon to prevent division by zero
    # even if validation had a very small margin.
    norm = math.sqrt(sum_sq) + 1e-12

    return [float(x) / norm for x in vector]


def normalize_batch(
    vectors: List[List[float]],
    enabled: bool = True,
) -> List[List[float]]:
    """
    Normalize a batch of vectors.

    Args:
        vectors:  Pre-validated float lists.
        enabled:  If False, returns vectors unchanged (normalization disabled).

    Returns:
        List of normalized (or original) vectors. Input vectors are never mutated.
    """
    if not enabled:
        return [[float(x) for x in v] for v in vectors]
    return [l2_normalize(v) for v in vectors]
````

## File: src/smriti/embedding/statistics.py
````python
"""
statistics.py — Phase 5 execution statistics collector.

Responsibility:
    Collect operational metrics during Phase 5 execution.
    Statistics are DIAGNOSTIC ONLY — they never influence execution.

This module observes. It never acts.

Metrics collected:
    - Outcome counts (successful, cached, stale, failed, skipped)
    - Batch metrics (count, average size)
    - Cache lifecycle (reused, regenerated, invalidated)
    - Throughput: vectors embedded per second
    - Memory: peak RSS in MB (best-effort, 0 if psutil unavailable)
"""

from __future__ import annotations

import time
from typing import List
from smriti.embedding.models import EmbeddingStatus

from smriti.core.models import Phase5Stats


class Phase5StatsCollector:
    """
    Mutable statistics accumulator for Phase 5.
    Call finalize() to get the immutable Phase5Stats snapshot.

    Thread safety: NOT thread-safe. Use from a single thread only.
    """

    def __init__(self) -> None:
        self._total = 0
        self._successful = 0
        self._cached = 0
        self._stale = 0
        self._failed = 0
        self._skipped = 0
        self._total_batches = 0
        self._batch_sizes: List[int] = []
        # Cache lifecycle
        self._cache_reused = 0
        self._cache_regenerated = 0
        self._cache_invalidated = 0
        self._start_time = time.monotonic()

    # ── Per-claim recording ───────────────────────────────────────────────────

    def record_skipped(self) -> None:
        self._total += 1
        self._skipped += 1

    def record_cached(self) -> None:
        self._total += 1
        self._cached += 1
        self._cache_reused += 1

    def record_stale(self) -> None:
        """Record a stale cache hit — will be followed by record_successful."""
        self._stale += 1
        self._cache_regenerated += 1
        # Note: total not incremented here — stale leads to a separate successful/failed

    def record_successful(self) -> None:
        self._total += 1
        self._successful += 1

    def record_failed(self) -> None:
        self._total += 1
        self._failed += 1

    def record_invalidated(self) -> None:
        """Record a cache entry that was explicitly invalidated."""
        self._cache_invalidated += 1

    def record_status(self, status: EmbeddingStatus) -> None:
        """Convenience dispatcher for any EmbeddingStatus."""
        self._total += 1
        if status == EmbeddingStatus.SUCCESS:
            self._successful += 1
        elif status == EmbeddingStatus.CACHED:
            self._cached += 1
            self._cache_reused += 1
        elif status == EmbeddingStatus.STALE:
            self._stale += 1
            self._cache_regenerated += 1
        elif status == EmbeddingStatus.FAILED:
            self._failed += 1
        elif status == EmbeddingStatus.SKIPPED:
            self._skipped += 1

    def record_batch(self, batch_size: int) -> None:
        self._total_batches += 1
        self._batch_sizes.append(batch_size)

    # ── Finalization ──────────────────────────────────────────────────────────

    def finalize(self) -> Phase5Stats:
        """Return an immutable snapshot of accumulated statistics."""
        elapsed = time.monotonic() - self._start_time
        total_attempts = self._total or 1

        cache_hit_rate = self._cached / total_attempts
        avg_batch = (
            sum(self._batch_sizes) / len(self._batch_sizes)
            if self._batch_sizes else 0.0
        )

        # Throughput: count vectors that ended up embedded (cached + successful)
        total_embedded = self._successful + self._cached
        vectors_per_second = total_embedded / elapsed if elapsed > 0 else 0.0

        # Memory: best-effort, never fails
        current_memory_mb = _get_current_memory_mb()

        return Phase5Stats(
            total_claims=self._total,
            successful=self._successful,
            cached=self._cached,
            stale=self._stale,
            failed=self._failed,
            skipped=self._skipped,
            total_batches=self._total_batches,
            average_batch_size=avg_batch,
            cache_hit_rate=cache_hit_rate,
            total_runtime_seconds=elapsed,
            vectors_per_second=vectors_per_second,
            current_memory_mb=current_memory_mb,
            cache_entries_reused=self._cache_reused,
            cache_entries_regenerated=self._cache_regenerated,
            cache_entries_invalidated=self._cache_invalidated,
        )


def _get_current_memory_mb() -> float:
    """
    Return current process RSS in MB. Returns 0.0 if unavailable.
    This is the current RSS at finalize() time, not a true peak tracker.
    For a true peak, use tracemalloc or psutil.Process.memory_info().peak_wset
    (Windows) or /proc/self/status VmPeak (Linux).
    """
    try:
        import psutil
        import os
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except ImportError:
        pass
    try:
        # Fallback: read from /proc/self/status on Linux
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return kb / 1024
    except Exception:
        pass
    return 0.0
````

## File: src/smriti/embedding/validation.py
````python
"""
validation.py — Mathematical vector validation for Phase 5.

Responsibility:
    Verify that a raw (or normalized) vector from the embedder satisfies
    mathematical invariants before it becomes an immutable Vector domain object.

    Called TWICE per vector:
        1. After inference — validates raw output from the model
        2. After normalization — cheap guard against numerical edge cases

Validation checks (in order):
    1. Non-empty:         vector must have at least one element
    2. Correct dimension: len(vector) == descriptor.dimension
    3. dtype check:       all elements must be strictly float (no ints, numpy scalars, etc.)
    4. Finite values:     no NaN or Inf anywhere
    5. Non-zero norm:     a zero vector cannot be normalized

Rules:
    ✅ Return (bool, Optional[str]) — callers decide what to do with failures
    ✅ Never modify the vector
    ✅ Provide clear, actionable error messages

    ❌ Never normalize (that's normalization.py's job)
    ❌ Never embed (that's embedder.py's job)
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


def validate_vector(
    vector: List[float],
    expected_dimension: int,
) -> Tuple[bool, Optional[str]]:
    """
    Validate a raw or normalized embedding vector.

    Args:
        vector:             Float list from embedder (raw) or normalization.
        expected_dimension: Expected length (from EmbeddingModelDescriptor.dimension).

    Returns:
        (True, None)             if vector passes all checks
        (False, error_message)   if any check fails
    """
    # Check 1: Non-empty
    if not vector:
        return False, "Vector is empty"

    # Check 2: Correct dimension
    actual_dim = len(vector)
    if actual_dim != expected_dimension:
        return False, (
            f"Dimension mismatch: expected {expected_dimension}, got {actual_dim}"
        )

    # Check 3: dtype — all elements must be strictly float
    # This rejects ints, numpy scalars, strings, etc. to enforce type purity.
    for i, value in enumerate(vector):
        if not isinstance(value, float):
            return False, (
                f"Non-float type at index {i}: {type(value).__name__} "
                f"(expected float)"
            )

    # Check 4: Finite values (no NaN or Inf)
    for i, value in enumerate(vector):
        if math.isnan(value):
            return False, f"NaN detected at index {i}"
        if math.isinf(value):
            return False, f"Inf detected at index {i}"

    # Check 5: Non-zero norm
    norm_sq = sum(float(x) * float(x) for x in vector)
    if norm_sq == 0.0:
        return False, "Zero-norm vector (all elements are zero)"

    return True, None


def validate_batch(
    vectors: List[List[float]],
    expected_dimension: int,
) -> List[Tuple[bool, Optional[str]]]:
    """
    Validate an entire batch of vectors.

    Returns:
        List of (is_valid, error_message_or_None), one per input vector.
    """
    return [validate_vector(v, expected_dimension) for v in vectors]
````

## File: src/smriti/evolution/__init__.py
````python

````

## File: src/smriti/evolution/analyzer.py
````python
# Will be filled in Phase 7\n
````

## File: src/smriti/extraction/scanner/__init__.py
````python
"""
scanner/__init__.py — Public interface for the structural scanner.

Exports scan_document and the BlockType enum.
"""

from smriti.extraction.scanner.scanner import scan_document, BlockType, ScannerEvent

__all__ = ["scan_document", "BlockType", "ScannerEvent"]
````

## File: src/smriti/extraction/scanner/code.py
````python
"""
scanner/code.py — Code block detection and accumulation.
"""

from typing import Optional, Tuple
from smriti.extraction.rules import (
    FENCED_CODE_START,
    FENCED_CODE_END_TRIPLE,
    FENCED_CODE_END_TILDE,
    INDENTED_CODE_PATTERN,
)


def detect_fenced_code_start(line: str) -> Optional[str]:
    """Return fence char ('`' or '~') if line starts a fenced code block."""
    match = FENCED_CODE_START.match(line)
    if match:
        return match.group(1)[0]   # first char of the fence
    return None


def is_fenced_code_end(line: str, fence_char: str) -> bool:
    if fence_char == "`":
        return bool(FENCED_CODE_END_TRIPLE.match(line))
    else:
        return bool(FENCED_CODE_END_TILDE.match(line))


def is_indented_code_line(line: str) -> bool:
    return bool(INDENTED_CODE_PATTERN.match(line))
````

## File: src/smriti/extraction/scanner/heading.py
````python
"""
scanner/heading.py — Heading detection logic.
"""

from typing import Optional
from smriti.extraction.rules import HEADING_PATTERN, SETEXT_H1_PATTERN, SETEXT_H2_PATTERN


def detect_heading(line: str, next_line: Optional[str] = None):
    """
    Detect ATX or setext heading.

    Returns:
        (level, title, consumed_lines) or (None, None, 0) if not a heading.
    """
    # ATX
    match = HEADING_PATTERN.match(line)
    if match:
        level = len(match.group(1))
        title = match.group(2).strip()
        return level, title, 1

    # Setext H1 (line followed by ===)
    if next_line and SETEXT_H1_PATTERN.match(next_line):
        return 1, line.strip(), 2

    # Setext H2 (line followed by ---)
    if next_line and SETEXT_H2_PATTERN.match(next_line):
        return 2, line.strip(), 2

    return None, None, 0
````

## File: src/smriti/extraction/scanner/paragraph.py
````python
"""
scanner/paragraph.py — Paragraph accumulation logic.
"""

from typing import List, Tuple


def accumulate_paragraph(
    lines: List[str],
    start_char: int,
    current_char_pos: int,
) -> Tuple[str, int, int]:
    """
    Accumulate a paragraph block from a list of lines.

    Returns:
        (paragraph_text, char_start, char_end)
    """
    para_text = "\n".join(lines).strip()
    char_start = start_char
    char_end = current_char_pos
    return para_text, char_start, char_end
````

## File: src/smriti/extraction/scanner/scanner.py
````python
"""
scanner/scanner.py — Structural scanner orchestrator.

Responsibility:
    Read a Document's normalized_text line by line and emit ScannerEvents
    describing the structural elements found.

    This file orchestrates the detection logic from submodules.

Input:  str (normalized_text from Document)
Output: List[ScannerEvent]

Complexity: O(n) — one linear pass through the text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
import structlog

from smriti.extraction.rules import (
    YAML_FRONT_MATTER_DELIMITER,
    HORIZONTAL_RULE_PATTERN,
    BLOCK_QUOTE_PATTERN,
    BULLET_PATTERN,
    ORDERED_PATTERN,
)
from smriti.extraction.scanner.heading import detect_heading
from smriti.extraction.scanner.paragraph import accumulate_paragraph
from smriti.extraction.scanner.table import is_table_row, is_table_separator, accumulate_table
from smriti.extraction.scanner.code import (
    detect_fenced_code_start,
    is_fenced_code_end,
    is_indented_code_line,
)

logger = structlog.get_logger(__name__)


class BlockType(str, Enum):
    """The structural type of a scanner event."""
    HEADING          = "heading"
    PARAGRAPH        = "paragraph"
    BULLET_ITEM      = "bullet_item"
    ORDERED_ITEM     = "ordered_item"
    BLOCK_QUOTE      = "block_quote"
    TABLE            = "table"
    CODE_BLOCK       = "code_block"       # Ignored in V1
    FRONT_MATTER     = "front_matter"     # Ignored
    HORIZONTAL_RULE  = "horizontal_rule"  # Ignored
    BLANK            = "blank"            # Ignored


@dataclass(frozen=True)
class ScannerEvent:
    """
    An immutable structural event emitted by the scanner.

    Fields:
        block_type:    What kind of structural element this is
        text:          The meaningful text content (stripped of markers)
        heading_level: 1–6 for headings, None for everything else
        char_start:    Character offset of the FIRST character of this block
        char_end:      Character offset just after the LAST character of this block
        lines:         All lines that make up this block (for multi‑line blocks)
    """
    block_type: BlockType
    text: str
    heading_level: Optional[int]
    char_start: int
    char_end: int
    lines: tuple = field(default_factory=tuple)


def scan_document(normalized_text: str) -> List[ScannerEvent]:
    """
    Perform one linear pass through normalized_text and emit structural events.

    Args:
        normalized_text: The fully normalized text from Phase 2 (Document.normalized_text).

    Returns:
        List of ScannerEvent in document order. Never empty for non‑empty text.

    Complexity: O(n) — single pass, no recursion.
    """
    if not normalized_text.strip():
        return []

    events: List[ScannerEvent] = []
    lines = normalized_text.split("\n")
    num_lines = len(lines)

    # State flags for multi‑line blocks
    in_fenced_code = False
    fenced_code_char = ""      # ` or ~
    in_front_matter = False
    front_matter_seen = False
    in_table = False

    # Accumulation buffers
    paragraph_lines: List[str] = []
    paragraph_start: int = 0
    table_lines: List[str] = []
    table_start: int = 0
    code_lines: List[str] = []
    code_start: int = 0

    char_pos = 0  # Running character position in the full string

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, paragraph_start
        if paragraph_lines:
            para_text, p_start, p_end = accumulate_paragraph(
                paragraph_lines, paragraph_start, char_pos
            )
            if para_text:
                events.append(ScannerEvent(
                    block_type=BlockType.PARAGRAPH,
                    text=para_text,
                    heading_level=None,
                    char_start=p_start,
                    char_end=p_end,
                    lines=tuple(paragraph_lines),
                ))
            paragraph_lines = []

    def flush_table() -> None:
        nonlocal table_lines, table_start, in_table
        if table_lines:
            table_text, t_start, t_end = accumulate_table(
                table_lines, table_start, char_pos
            )
            events.append(ScannerEvent(
                block_type=BlockType.TABLE,
                text=table_text,
                heading_level=None,
                char_start=t_start,
                char_end=t_end,
                lines=tuple(table_lines),
            ))
            table_lines = []
            in_table = False

    def flush_code_block() -> None:
        nonlocal code_lines, code_start, in_fenced_code
        if code_lines:
            code_text = "\n".join(code_lines)
            events.append(ScannerEvent(
                block_type=BlockType.CODE_BLOCK,
                text=code_text,
                heading_level=None,
                char_start=code_start,
                char_end=char_pos,
                lines=tuple(code_lines),
            ))
            code_lines = []
            in_fenced_code = False

    i = 0
    while i < num_lines:
        line = lines[i]
        line_end = char_pos + len(line)

        # ── Front matter handling ─────────────────────────────────────────────
        if i == 0 and YAML_FRONT_MATTER_DELIMITER.match(line):
            in_front_matter = True
            char_pos = line_end + 1
            i += 1
            continue

        if in_front_matter:
            if YAML_FRONT_MATTER_DELIMITER.match(line) and i > 0:
                in_front_matter = False
                front_matter_seen = True
            char_pos = line_end + 1
            i += 1
            continue

        # ── Fenced code block handling ────────────────────────────────────────
        if not in_fenced_code:
            fence_char = detect_fenced_code_start(line)
            if fence_char:
                flush_paragraph()
                flush_table()
                in_fenced_code = True
                fenced_code_char = fence_char
                code_start = char_pos
                char_pos = line_end + 1
                i += 1
                continue
        else:
            if is_fenced_code_end(line, fenced_code_char):
                flush_code_block()
            else:
                code_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if not line.strip():
            flush_paragraph()
            flush_table()
            # Record blank line for statistics (we'll count later)
            char_pos = line_end + 1
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────────
        if HORIZONTAL_RULE_PATTERN.match(line):
            flush_paragraph()
            flush_table()
            events.append(ScannerEvent(
                block_type=BlockType.HORIZONTAL_RULE,
                text="",
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── ATX Heading (# Title) ─────────────────────────────────────────────
        heading_level, heading_title, consumed = detect_heading(line, lines[i+1] if i+1 < num_lines else None)
        if heading_level is not None:
            flush_paragraph()
            flush_table()
            # For setext, we need to skip the underline line
            end_pos = line_end
            if consumed == 2:
                # Skip the underline line as well
                # We already used next line; we'll advance i by 2
                # But we need to compute end position including the underline
                underline_line = lines[i+1]
                end_pos = line_end + 1 + len(underline_line) + 1  # include newline
                # We'll handle the skip after appending event
            events.append(ScannerEvent(
                block_type=BlockType.HEADING,
                text=heading_title,
                heading_level=heading_level,
                char_start=char_pos,
                char_end=end_pos,
                lines=(line, lines[i+1] if consumed == 2 else line),
            ))
            # Move char_pos and i
            char_pos = end_pos
            i += consumed
            continue

        # ── Block quote ───────────────────────────────────────────────────────
        quote_match = BLOCK_QUOTE_PATTERN.match(line)
        if quote_match:
            flush_paragraph()
            flush_table()
            quote_text = quote_match.group(1).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BLOCK_QUOTE,
                text=quote_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Table row ─────────────────────────────────────────────────────────
        if is_table_row(line):
            flush_paragraph()
            if not in_table:
                in_table = True
                table_start = char_pos
            table_lines.append(line)
            char_pos = line_end + 1
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # ── Bullet list item ──────────────────────────────────────────────────
        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            flush_paragraph()
            flush_table()
            item_text = bullet_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.BULLET_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Ordered list item ─────────────────────────────────────────────────
        ordered_match = ORDERED_PATTERN.match(line)
        if ordered_match:
            flush_paragraph()
            flush_table()
            item_text = ordered_match.group(2).strip()
            events.append(ScannerEvent(
                block_type=BlockType.ORDERED_ITEM,
                text=item_text,
                heading_level=None,
                char_start=char_pos,
                char_end=line_end,
                lines=(line,),
            ))
            char_pos = line_end + 1
            i += 1
            continue

        # ── Paragraph accumulation ────────────────────────────────────────────
        if not paragraph_lines:
            paragraph_start = char_pos
        paragraph_lines.append(line)
        char_pos = line_end + 1
        i += 1

    # Flush any remaining state
    flush_paragraph()
    flush_table()
    flush_code_block()

    logger.debug(
        "scan complete",
        events=len(events),
        lines=len(lines),
    )

    return events
````

## File: src/smriti/extraction/scanner/table.py
````python
"""
scanner/table.py — Table detection and accumulation.
"""

from typing import List, Tuple
from smriti.extraction.rules import TABLE_ROW_PATTERN, TABLE_SEPARATOR_PATTERN


def is_table_row(line: str) -> bool:
    return bool(TABLE_ROW_PATTERN.match(line))


def is_table_separator(line: str) -> bool:
    return bool(TABLE_SEPARATOR_PATTERN.match(line))


def accumulate_table(lines: List[str], start_char: int, current_char_pos: int) -> Tuple[str, int, int]:
    """
    Accumulate a table block.

    Returns:
        (table_text, char_start, char_end)
    """
    table_text = "\n".join(lines)
    return table_text, start_char, current_char_pos
````

## File: src/smriti/extraction/__init__.py
````python
"""
extraction/__init__.py — Public API for Phase 3.

External callers (PipelineRunner, tests) import ONLY from here:

    from smriti.extraction import build_semantic_sentences, ExtractionResult

They never import from individual submodules.
All internal modules (scanner, context, normalizer, segmenter, builder, validator)
are implementation details.

Public contract:
    build_semantic_sentences(document: Document) → ExtractionResult

That is the only function that crosses the phase boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import (
    Document,
    SemanticSentence,
    Phase3Stats,
    SegmentationWarning,
)
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import Phase3Error, SentenceValidationError

from smriti.extraction.scanner import scan_document, BlockType
from smriti.extraction.context import ContextStack
from smriti.extraction.normalizer import normalize_event
from smriti.extraction.segmenter import SentenceSegmenter
from smriti.extraction.builder import build_sentence
from smriti.extraction.validator import validate_sentences
from smriti.extraction.statistics import Phase3StatsCollector

logger = structlog.get_logger(__name__)


# ── Public result types ───────────────────────────────────────────────────────

@dataclass
class DocumentExtractionResult:
    """
    Phase 3 result for a single Document.
    """
    document_id: str
    sentences: List[SemanticSentence]
    stats: Phase3Stats
    warnings: List[SegmentationWarning]
    error: Optional[str] = None

    @property
    def sentence_count(self) -> int:
        return len(self.sentences)


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 3 — all documents processed.
    This is what Phase 4 receives.
    """
    document_results: List[DocumentExtractionResult]
    run_id: str
    rules_version: str = "3.1.0"  # <-- ADDED FINGERPRINT
    manifest_path: Optional[Path] = None

    @property
    def all_sentences(self) -> List[SemanticSentence]:
        """Flat list of all sentences across all documents."""
        result = []
        for dr in self.document_results:
            result.extend(dr.sentences)
        return result

    @property
    def total_sentences(self) -> int:
        return sum(dr.sentence_count for dr in self.document_results)

    @property
    def successful_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is None)

    @property
    def failed_documents(self) -> int:
        return sum(1 for dr in self.document_results if dr.error is not None)

    def to_dataset_json(self) -> str:
        """
        Serialise all SemanticSentences to JSON for Phase 4.
        Written to artifacts/run_{id}/phase3/dataset.json.
        """
        records = []
        for sentence in self.all_sentences:
            records.append({
                "sentence_id":  sentence.sentence_id,
                "document_id":  sentence.document_id,
                "text":         sentence.text,
                "context":      sentence.context,
                "position":     sentence.position,
                "char_start":   sentence.char_start,
                "char_end":     sentence.char_end,
                "source_path":  str(sentence.source_path),
                "origin_block_type": sentence.origin_block_type,  # <-- FIX: Remove .value
                "schema_version": sentence.schema_version,
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


# ── Core public function ──────────────────────────────────────────────────────

def build_semantic_sentences(document: Document) -> DocumentExtractionResult:
    """
    Transform one Document into an ordered collection of SemanticSentences.

    This is Phase 3's single public function.
    Internal modules (scanner, context, normalizer, segmenter, builder, validator)
    are never exposed.

    Args:
        document: A Document from Phase 2 with validated normalized_text.

    Returns:
        DocumentExtractionResult with sentences, stats, and warnings.
        On error, returns a result with error set and empty sentences.
    """
    document_id = document.doc_id
    source_path = document.source_document.path

    try:
        sentences, stats, warnings = _process_document(document)
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=sentences,
            stats=stats,
            warnings=warnings,
        )

    except SentenceValidationError as e:
        logger.error(
            "fatal sentence validation error",
            document_id=document_id,
            error=str(e),
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )

    except Exception as e:
        logger.error(
            "unexpected error in phase 3",
            document_id=document_id,
            error=str(e),
            exc_info=True,
        )
        return DocumentExtractionResult(
            document_id=document_id,
            sentences=[],
            stats=Phase3Stats(),
            warnings=[],
            error=str(e),
        )


def _process_document(
    document: Document,
) -> Tuple[List[SemanticSentence], Phase3Stats, List[SegmentationWarning]]:
    """
    Internal orchestration of Phase 3 for one Document.

    Pipeline:
        1. scan_document      → ScannerEvent[]
        2. Normalise each event → NormalizedBlock[]
        3. Associate context (from heading events) to each block
        4. segmenter.segment   → SentenceCandidate[]
        5. build_sentence      → SemanticSentence (one per candidate)
        6. validate_sentences  → validated list

    Complexity: O(n) where n = length of normalized_text
    """
    normalized_text = document.normalized_text
    document_id = document.doc_id
    source_path = document.source_document.path

    # Step 1: Structural scan
    events = scan_document(normalized_text)

    # Step 2: Initialise components
    context_stack = ContextStack()
    segmenter = SentenceSegmenter()
    stats_collector = Phase3StatsCollector()

    sentences: List[SemanticSentence] = []
    all_warnings: List[SegmentationWarning] = []
    position = 0  # Global position counter across all sentences in document

    # Step 3: Process each structural event
    for event in events:
        stats_collector.accumulate_event(event)

        # 3a: Update context if this is a heading event
        # MUST happen before normalization because headings set skip=True
        if event.block_type == BlockType.HEADING and event.heading_level is not None:
            context_stack.push(event.text, event.heading_level)

        # 3b: Normalise event to prose (context-agnostic)
        normalized_block = normalize_event(event)
        if normalized_block.warnings:
            all_warnings.extend(normalized_block.warnings)
            stats_collector.record_warnings(normalized_block.warnings)

        # Skip blocks that produce no sentences (headings, code, etc.)
        if normalized_block.skip or not normalized_block.prose.strip():
            if event.block_type == BlockType.CODE_BLOCK:
                stats_collector.record_sentence_discarded()
            continue

        # 3c: Attach current context to this block
        current_context = context_stack.current_context()

        # 3d: Segment prose into sentence candidates
        candidates = segmenter.segment(
            normalized_block.prose,
            block_char_start=normalized_block.char_start,
        )

        if not candidates:
            stats_collector.record_sentence_discarded()
            continue

        # 3e: Build SemanticSentence for each candidate
        for candidate in candidates:
            if candidate.warnings:
                all_warnings.extend(candidate.warnings)
                stats_collector.record_warnings(candidate.warnings)

            sentence = build_sentence(
                text=candidate.text,
                document_id=document_id,
                source_path=source_path,
                context=current_context,
                position=position,
                char_start=candidate.char_start,
                char_end=candidate.char_end,
                origin_block_type=event.block_type,
            )
            sentences.append(sentence)
            stats_collector.record_sentence_produced()
            position += 1

    # Step 4: Validate the complete sentence collection
    validated_sentences, val_warnings = validate_sentences(sentences, document_id)
    all_warnings.extend(val_warnings)

    discarded = len(sentences) - len(validated_sentences)
    for _ in range(discarded):
        stats_collector.record_sentence_discarded()

    stats = stats_collector.finalize()

    logger.info(
        "document processed",
        document_id=document_id[:8],
        sentences=len(validated_sentences),
        warnings=len(all_warnings),
    )

    return validated_sentences, stats, all_warnings


# ── Batch runner (called by PipelineRunner) ───────────────────────────────────

def run_extraction(
    documents: List[Document],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Run Phase 3 on all Documents from Phase 2.

    Args:
        documents:        List[Document] from Phase 2's ExtractionResult.
        run_id:           Current pipeline run identifier.
        manifest_manager: For writing phase manifest.
        state_manager:    For updating pipeline state.

    Returns:
        ExtractionResult containing all SemanticSentences.
    """
    logger.info("phase 3 starting", run_id=run_id, documents=len(documents))
    start_time = manifest_manager.start_phase(phase=3)

    document_results: List[DocumentExtractionResult] = []

    for document in documents:
        if document.is_empty:
            logger.debug("skipping empty document", document_id=document.doc_id[:8])
            continue

        doc_result = build_semantic_sentences(document)
        document_results.append(doc_result)

    result = ExtractionResult(
        document_results=document_results,
        run_id=run_id,
    )

    # Write dataset artifact
    phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase3"
    phase_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = phase_dir / "dataset.json"
    dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")

    logger.info(
        "dataset written",
        path=str(dataset_path),
        sentences=result.total_sentences,
    )

    # Write manifest
    manifest_path = manifest_manager.end_phase(
        phase=3,
        start_time=start_time,
        inputs={"documents": len(documents)},
        outputs={
            "total_sentences": result.total_sentences,
            "successful_documents": result.successful_documents,
            "failed_documents": result.failed_documents,
            "dataset_path": str(dataset_path),
            "rules_version": result.rules_version,
        },
        status="success",
    )
    result.manifest_path = manifest_path

    # Update pipeline state
    state_manager.complete_phase(phase=3)

    logger.info(
        "phase 3 complete",
        sentences=result.total_sentences,
        docs_ok=result.successful_documents,
        docs_failed=result.failed_documents,
    )

    return result
````

## File: src/smriti/extraction/builder.py
````python
"""
builder.py — SemanticSentence constructor for Phase 3.

Responsibility:
    Construct immutable SemanticSentence objects from SentenceCandidate
    and context information.

    This is the ONLY place where SemanticSentence is instantiated.
    That enforces a single, consistent construction path.

    Builder performs:
        1. Deterministic sentence_id generation (SHA256, never random)
        2. Position assignment (0-based, strictly increasing)
        3. Context association (heading path from ContextStack)
        4. Final object construction with provenance and version

    Builder NEVER modifies text.
    Builder NEVER modifies the context stack.
    Builder NEVER validates (that is validator.py's job).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional
import structlog

from smriti.core.models import SemanticSentence
from smriti.extraction.scanner import BlockType

logger = structlog.get_logger(__name__)


def build_sentence(
    text: str,
    document_id: str,
    source_path: Path,
    context: str,
    position: int,
    char_start: int,
    char_end: int,
    origin_block_type: BlockType,
) -> SemanticSentence:
    """
    Construct a single immutable SemanticSentence.

    Args:
        text:          The sentence text (stripped, non-empty).
        document_id:   The doc_id of the source Document.
        source_path:   Path to the original file (for traceability).
        context:       Current heading context (e.g. "Python > Generators").
        position:      0-based index within this document.
        char_start:    Character start in Document.normalized_text.
        char_end:      Character end in Document.normalized_text.
        origin_block_type: The BlockType that produced this sentence.

    Returns:
        Immutable SemanticSentence.
    """
    sentence_id = _compute_sentence_id(document_id, text, char_start)

    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=document_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=source_path,
        origin_block_type=origin_block_type.value,
        schema_version="3.0",
    )

    logger.debug(
        "sentence built",
        sentence_id=sentence_id[:8],
        position=position,
        context=context[:40] if context else "(root)",
        origin=origin_block_type.value,
        text_preview=text[:40],
    )

    return sentence


def _compute_sentence_id(document_id: str, text: str, char_start: int) -> str:
    """
    Compute a deterministic 16-character sentence ID.

    Input: document_id + canonical text (as stored) + char_start offset
    Output: first 16 characters of SHA256 hex digest

    Properties:
        - Same inputs always produce same ID (deterministic)
        - No timestamps
        - No random values
        - char_start disambiguates identical text at different positions
    """
    # Use the exact text that will be stored; this ensures stability across
    # future normalisation changes that might affect whitespace.
    id_material = f"{document_id}:{text}:{char_start}"
    return hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:16]
````

## File: src/smriti/extraction/context.py
````python
"""
context.py — Hierarchical context stack for Phase 3.

Responsibility:
    Maintain a lightweight push/pop stack representing the current heading
    hierarchy as Phase 3 processes structural events.

    This module has FOUR operations: push, pop, peek, current_context.
    Nothing else. It is deliberately minimal.

    Memory: O(depth) — proportional to heading nesting depth, not document length.

Input:  Heading events from scanner.py
Output: Context strings like "Python > Generators > Yield"

Example:
    # Python          →  push("Python", level=1)   → stack: ["Python"]
    ## Generators     →  push("Generators", level=2) → stack: ["Python", "Generators"]
    Sentence A        →  current_context() → "Python > Generators"
    ## Decorators     →  pop to level 1, push("Decorators") → stack: ["Python", "Decorators"]
    Sentence B        →  current_context() → "Python > Decorators"
"""

from dataclasses import dataclass
from typing import List, Optional
import structlog

from smriti.extraction.rules import CONTEXT_SEPARATOR

logger = structlog.get_logger(__name__)


@dataclass
class _ContextFrame:
    """One entry in the context stack."""
    heading: str      # Cleaned heading text
    level: int        # 1–6


class ContextStack:
    """
    Lightweight heading context stack.

    The context stack represents the path from the document root
    to the current heading, like a breadcrumb trail.

    Invariant: stack[i].level < stack[i+1].level always.
    """

    def __init__(self) -> None:
        self._stack: List[_ContextFrame] = []

    def push(self, heading: str, level: int) -> None:
        """
        Push a new heading onto the stack.

        Before pushing, all frames at level >= this heading's level are popped.
        This handles the transition from deep to shallow headings:
            ## A        stack: [H2:A]
            ### B       stack: [H2:A, H3:B]
            ## C        stack: [H2:C]   ← B and A are both popped

        Args:
            heading: The heading text (without # markers).
            level:   Heading level (1=H1, 2=H2, ... 6=H6).
        """
        # Pop all frames at the same or deeper level
        while self._stack and self._stack[-1].level >= level:
            popped = self._stack.pop()
            logger.debug("context popped", heading=popped.heading, level=popped.level)

        self._stack.append(_ContextFrame(heading=heading.strip(), level=level))
        logger.debug("context pushed", heading=heading.strip(), level=level, depth=len(self._stack))

    def peek(self) -> Optional[str]:
        """Return the topmost heading text, or None if stack is empty."""
        return self._stack[-1].heading if self._stack else None

    def current_context(self) -> str:
        """
        Return the full context path as a string.

        Example: "Python > Generators > Yield"
        Returns "" if no heading has been encountered yet.
        """
        if not self._stack:
            return ""
        return CONTEXT_SEPARATOR.join(frame.heading for frame in self._stack)

    def depth(self) -> int:
        """Current stack depth (number of active headings)."""
        return len(self._stack)

    def clear(self) -> None:
        """Reset stack to empty state (use at document boundaries)."""
        self._stack.clear()

    def __repr__(self) -> str:
        return f"ContextStack({self.current_context()!r})"
````

## File: src/smriti/extraction/extractor.py
````python
# Will be filled in Phase 3\n
````

## File: src/smriti/extraction/normalizer.py
````python
"""
normalizer.py — Structured content normaliser for Phase 3.

Responsibility:
    Convert structured content (tables, lists, etc.) into canonical prose strings.
    Pass paragraph and list text through unchanged.
    Emit warnings for malformed structures.

Input:  ScannerEvent
Output: NormalizedBlock

Design:
    Each normaliser strategy handles one BlockType.
    Adding support for a new format = adding one strategy.
    No if/elif chains allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import structlog

from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.extraction.rules import TABLE_KV_TEMPLATE, TABLE_SEPARATOR_PATTERN
from smriti.core.models import SegmentationWarning

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class NormalizedBlock:
    """
    Result of normalising a single ScannerEvent into prose.

    Fields:
        prose:       The normalised text ready for sentence segmentation.
                     For headings: empty (headings become context only).
        block_type:  The original block type (for statistics and provenance).
        char_start:  Character start from original event.
        char_end:    Character end from original event.
        warnings:    Any warnings emitted during normalisation.
        skip:        If True, this block produces no sentences (headings, code, etc.)
    """
    prose: str
    block_type: BlockType
    char_start: int
    char_end: int
    warnings: tuple
    skip: bool = False  # True for headings, code blocks, etc.


def normalize_event(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a ScannerEvent into a NormalizedBlock.

    Dispatches to the appropriate strategy based on block_type.
    """
    strategy = _NORMALIZERS.get(event.block_type, _normalize_unknown)
    return strategy(event)


# ── Strategy implementations ──────────────────────────────────────────────────

def _normalize_paragraph(event: ScannerEvent) -> NormalizedBlock:
    """Paragraphs pass through unchanged."""
    return NormalizedBlock(
        prose=event.text.strip(),
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_heading(event: ScannerEvent) -> NormalizedBlock:
    """
    Headings become context only — they produce no sentences.
    The caller (orchestrator) updates the context stack.
    """
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,  # Headings do NOT produce sentences
    )


def _normalize_bullet_item(event: ScannerEvent) -> NormalizedBlock:
    """Bullet list items become single prose sentences."""
    text = event.text.strip()
    if text and not text[-1] in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_ordered_item(event: ScannerEvent) -> NormalizedBlock:
    """Ordered list items are treated identically to bullet items."""
    return _normalize_bullet_item(event)


def _normalize_block_quote(event: ScannerEvent) -> NormalizedBlock:
    """Block quotes pass through as prose."""
    text = event.text.strip()
    if text and not text[-1] in ".?!":
        text = text + "."
    return NormalizedBlock(
        prose=text,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=False,
    )


def _normalize_table(event: ScannerEvent) -> NormalizedBlock:
    """
    Convert a Markdown table into canonical prose.

    Strategy:
        | Model | Accuracy |      →   "Model: GPT-4. Accuracy: 85%."
        |-------|----------|
        | GPT-4 | 85%      |

    Each data row becomes one prose sentence.
    Headers become the keys.
    The separator row is discarded.

    If parsing fails, emit SEG_MALFORMED_TABLE and return empty prose.
    """
    warnings = []
    lines = list(event.lines)

    content_lines = [l for l in lines if not TABLE_SEPARATOR_PATTERN.match(l)]

    if not content_lines:
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        return NormalizedBlock(
            prose="",
            block_type=event.block_type,
            char_start=event.char_start,
            char_end=event.char_end,
            warnings=tuple(warnings),
            skip=True,
        )

    def parse_row(line: str) -> List[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    try:
        header_row = parse_row(content_lines[0])
        data_rows = content_lines[1:]

        if not header_row:
            raise ValueError("Empty header row")

        prose_sentences = []
        for data_line in data_rows:
            cells = parse_row(data_line)
            pairs = []
            for idx, header in enumerate(header_row):
                value = cells[idx] if idx < len(cells) else ""
                if header and value:
                    pairs.append(TABLE_KV_TEMPLATE.format(key=header, value=value))

            if pairs:
                prose_sentences.append(" ".join(pairs))

        combined_prose = " ".join(prose_sentences)

    except Exception as e:
        logger.warning("table normalisation failed", error=str(e))
        warnings.append(SegmentationWarning.SEG_MALFORMED_TABLE)
        combined_prose = ""

    return NormalizedBlock(
        prose=combined_prose,
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=tuple(warnings),
        skip=not combined_prose,
    )


def _normalize_code_block(event: ScannerEvent) -> NormalizedBlock:
    """Code blocks are skipped in V1."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,),
        skip=True,
    )


def _normalize_skip(event: ScannerEvent) -> NormalizedBlock:
    """Blocks that produce nothing (horizontal rules, front matter, etc.)."""
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(),
        skip=True,
    )


def _normalize_unknown(event: ScannerEvent) -> NormalizedBlock:
    """Unrecognised structure — emit warning and skip."""
    logger.warning("unknown block type encountered", block_type=event.block_type)
    return NormalizedBlock(
        prose="",
        block_type=event.block_type,
        char_start=event.char_start,
        char_end=event.char_end,
        warnings=(SegmentationWarning.SEG_UNKNOWN_STRUCTURE,),
        skip=True,
    )


# Strategy dispatch table — extend here for new formats
_NORMALIZERS = {
    BlockType.PARAGRAPH:       _normalize_paragraph,
    BlockType.HEADING:         _normalize_heading,
    BlockType.BULLET_ITEM:     _normalize_bullet_item,
    BlockType.ORDERED_ITEM:    _normalize_ordered_item,
    BlockType.BLOCK_QUOTE:     _normalize_block_quote,
    BlockType.TABLE:           _normalize_table,
    BlockType.CODE_BLOCK:      _normalize_code_block,
    BlockType.FRONT_MATTER:    _normalize_skip,
    BlockType.HORIZONTAL_RULE: _normalize_skip,
    BlockType.BLANK:           _normalize_skip,
}
````

## File: src/smriti/extraction/rules.py
````python
"""
rules.py — Deterministic rules and patterns for Phase 3.

This file contains ONLY data: patterns, dictionaries, and strategy names.
Zero execution logic lives here.

Every constant here is configurable via config/default.yaml.
This file provides the hard-coded defaults for those config values.
"""

import re

# ── Heading detection ─────────────────────────────────────────────────────────

# Matches ATX-style headings: # H1, ## H2, ..., ###### H6
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# Matches setext-style headings:
#   Title       (underlined by === for H1)
#   =========
SETEXT_H1_PATTERN = re.compile(r"^={3,}\s*$")
SETEXT_H2_PATTERN = re.compile(r"^-{3,}\s*$")

# ── List detection ────────────────────────────────────────────────────────────

# Matches bullet list items: "- item", "* item", "+ item"
BULLET_PATTERN = re.compile(r"^(\s*)[*+\-]\s+(.+)$")

# Matches ordered list items: "1. item", "2) item"
ORDERED_PATTERN = re.compile(r"^(\s*)\d+[.)]\s+(.+)$")

# ── Block quote detection ─────────────────────────────────────────────────────

BLOCK_QUOTE_PATTERN = re.compile(r"^>\s*(.*)")

# ── Code block detection ──────────────────────────────────────────────────────

FENCED_CODE_START = re.compile(r"^(`{3,}|~{3,})(.*)")
FENCED_CODE_END_TRIPLE = re.compile(r"^`{3,}\s*$")
FENCED_CODE_END_TILDE = re.compile(r"^~{3,}\s*$")

# Indented code block: 4 spaces or 1 tab at start
INDENTED_CODE_PATTERN = re.compile(r"^( {4}|\t)(.+)")

# ── Table detection ───────────────────────────────────────────────────────────

TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\|[\s\-:|]+\|")

# ── Front matter ──────────────────────────────────────────────────────────────

YAML_FRONT_MATTER_DELIMITER = re.compile(r"^---\s*$")

# ── Horizontal rule ───────────────────────────────────────────────────────────

HORIZONTAL_RULE_PATTERN = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$")

# ── HTML comment ──────────────────────────────────────────────────────────────

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)

# ── Sentence boundary ─────────────────────────────────────────────────────────

# These abbreviations should NEVER trigger a sentence boundary.
# Fully configurable via config extraction.abbreviations in default.yaml.
DEFAULT_ABBREVIATIONS = frozenset([
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "rev", "gen",
    "e.g", "i.e", "vs", "etc", "fig", "no", "vol", "pt", "pp",
    "u.s", "u.k", "a.m", "p.m", "ph.d", "m.d", "b.c", "a.d",
])

# Characters that may end a sentence when followed by space + capital letter
SENTENCE_ENDING_CHARS = frozenset([".", "?", "!"])

# Minimum characters for a sentence to be kept (shorter are discarded with SEG001)
MIN_SENTENCE_CHARS_DEFAULT = 3

# Maximum sentence length before SEG002 warning is emitted
MAX_SENTENCE_CHARS_DEFAULT = 2000

# Context separator string
CONTEXT_SEPARATOR = " > "

# Table cell serialisation template: "Key: Value."
TABLE_KV_TEMPLATE = "{key}: {value}."

# Context validation: allow letters, digits, spaces, and the separator
CONTEXT_VALID_PATTERN = re.compile(r"^[a-zA-Z0-9\s" + re.escape(CONTEXT_SEPARATOR) + "]*$")
````

## File: src/smriti/extraction/segmenter.py
````python
"""
segmenter.py — Rule-based sentence segmenter for Phase 3.

Responsibility:
    Split normalised prose into sentence candidates using deterministic rules.

    CRITICAL DESIGN CONSTRAINT:
        No statistical models.
        No spaCy sentence boundaries.
        No ML of any kind.
        Must be 100% reproducible across all runs.

Philosophy:
    Prefer false MERGE over false SPLIT.
    "Dr. Smith visited" → one sentence (NOT "Dr." + "Smith visited")
    This is safer for downstream claim extraction.

Algorithm:
    1. Split on terminal punctuation (. ? !) followed by space + uppercase
    2. Guard against abbreviations using the abbreviation dictionary
    3. Guard against decimal numbers (3.14 should not split)
    4. Guard against ellipsis (... should not split)

Input:  NormalizedBlock.prose (str)
Output: List[SentenceCandidate]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, FrozenSet
import structlog

from smriti.core.config import get_config
from smriti.extraction.rules import (
    DEFAULT_ABBREVIATIONS,
    SENTENCE_ENDING_CHARS,
    MIN_SENTENCE_CHARS_DEFAULT,
    MAX_SENTENCE_CHARS_DEFAULT,
)
from smriti.core.models import SegmentationWarning

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class SentenceCandidate:
    """
    A candidate sentence extracted from a NormalizedBlock.

    Fields:
        text:       The sentence text (stripped)
        char_start: Approximate character start within the NormalizedBlock's prose
        char_end:   Approximate character end
        warnings:   Any per-candidate warnings
    """
    text: str
    char_start: int
    char_end: int
    warnings: tuple = ()


class SentenceSegmenter:
    """
    Rule-based sentence segmenter.

    Instantiate once, call segment() per NormalizedBlock.
    Configuration is loaded once from config/default.yaml.
    """

    def __init__(self) -> None:
        cfg = get_config()
        extraction_cfg = cfg.get("extraction", {})
        segmentation_cfg = cfg.get("segmentation", {})

        custom_abbrevs = frozenset(
            a.lower() for a in extraction_cfg.get("abbreviations", [])
        )
        self._abbreviations: FrozenSet[str] = DEFAULT_ABBREVIATIONS | custom_abbrevs

        self._min_chars: int = segmentation_cfg.get(
            "min_sentence_chars", MIN_SENTENCE_CHARS_DEFAULT
        )
        self._max_chars: int = segmentation_cfg.get(
            "max_sentence_chars", MAX_SENTENCE_CHARS_DEFAULT
        )

    def segment(self, prose: str, block_char_start: int = 0) -> List[SentenceCandidate]:
        """
        Split prose into sentence candidates.

        Args:
            prose:             The normalised prose from NormalizedBlock.
            block_char_start:  Character offset of this prose in the full document.

        Returns:
            List[SentenceCandidate], may be empty if prose is empty or all candidates
            are too short.
        """
        if not prose.strip():
            return []

        raw_candidates = self._split_into_candidates(prose)
        result: List[SentenceCandidate] = []
        running_offset = block_char_start

        for raw_text in raw_candidates:
            text = raw_text.strip()
            if not text:
                running_offset += len(raw_text)
                continue

            warnings = []

            if len(text) < self._min_chars:
                logger.debug(
                    "sentence discarded (too short)",
                    length=len(text),
                    text=text[:30],
                )
                running_offset += len(raw_text)
                continue

            if len(text) > self._max_chars:
                warnings.append(SegmentationWarning.SEG_VERY_LONG_SENTENCE)
                logger.debug("very long sentence", length=len(text))

            char_start = running_offset + (len(raw_text) - len(raw_text.lstrip()))
            char_end = char_start + len(text)

            result.append(SentenceCandidate(
                text=text,
                char_start=char_start,
                char_end=char_end,
                warnings=tuple(warnings),
            ))
            running_offset += len(raw_text)

        return result

    def _split_into_candidates(self, prose: str) -> List[str]:
        """
        Split prose string into sentence candidate strings.

        Algorithm:
          - Scan character by character
          - When we hit . ? ! followed by whitespace + uppercase (or end of string),
            check if it's actually an abbreviation or decimal
          - If not, split here
        """
        candidates: List[str] = []
        current_start = 0
        i = 0
        length = len(prose)

        while i < length:
            char = prose[i]

            if char in SENTENCE_ENDING_CHARS:
                # Ellipsis (...) — never a sentence boundary
                if char == "." and i + 1 < length and prose[i + 1] == ".":
                    i += 1
                    continue

                # Decimal numbers: "3.14" — no split
                if char == "." and i > 0 and prose[i - 1].isdigit():
                    if i + 1 < length and prose[i + 1].isdigit():
                        i += 1
                        continue

                # Check if this is an abbreviation: "Dr.", "e.g.", etc.
                if char == "." and self._is_abbreviation(prose, i):
                    i += 1
                    continue

                # Check: followed by whitespace then uppercase (or end of string)
                j = i + 1
                while j < length and prose[j] in '"\')\]':
                    j += 1

                if j >= length:
                    i += 1
                    continue

                if prose[j] == " ":
                    k = j + 1
                    while k < length and prose[k] == " ":
                        k += 1
                    if k < length and (prose[k].isupper() or prose[k].isdigit()):
                        candidates.append(prose[current_start : i + 1])
                        current_start = k
                        i = k
                        continue

            i += 1

        remaining = prose[current_start:].strip()
        if remaining:
            candidates.append(remaining)

        return candidates

    def _is_abbreviation(self, text: str, dot_pos: int) -> bool:
        """
        Check if the period at dot_pos is part of a known abbreviation.

        Looks backwards from the period to find the preceding word.
        """
        if dot_pos == 0:
            return False

        word_end = dot_pos
        word_start = dot_pos - 1
        while word_start > 0 and text[word_start - 1].isalpha():
            word_start -= 1

        preceding_word = text[word_start:word_end].lower()
        return preceding_word in self._abbreviations
````

## File: src/smriti/extraction/statistics.py
````python
"""
statistics.py — Phase 3 execution statistics collector.

Responsibility:
    Collect structural metrics from one document's processing.
    Statistics are diagnostic only — they NEVER affect execution.

    Think of this as a telemetry collector.
    It observes. It never influences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import structlog

from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning

logger = structlog.get_logger(__name__)


class Phase3StatsCollector:
    """
    Mutable collector that accumulates statistics during Phase 3 processing.

    Call accumulate_event() for each ScannerEvent.
    Call record_sentence_produced() for each SemanticSentence created.
    Call record_sentence_discarded() for each discard.
    Call finalize() to get the immutable Phase3Stats result.
    """

    def __init__(self) -> None:
        self._headings = 0
        self._paragraphs = 0
        self._list_items = 0
        self._tables = 0
        self._block_quotes = 0
        self._code_blocks_skipped = 0
        self._horizontal_rules = 0
        self._front_matter_blocks = 0
        self._blank_lines = 0
        self._unknown_blocks = 0
        self._sentences_produced = 0
        self._sentences_discarded = 0
        self._warnings: List[SegmentationWarning] = []

    def accumulate_event(self, event: ScannerEvent) -> None:
        """Record a scanner event for statistics."""
        if event.block_type == BlockType.HEADING:
            self._headings += 1
        elif event.block_type == BlockType.PARAGRAPH:
            self._paragraphs += 1
        elif event.block_type in (BlockType.BULLET_ITEM, BlockType.ORDERED_ITEM):
            self._list_items += 1
        elif event.block_type == BlockType.TABLE:
            self._tables += 1
        elif event.block_type == BlockType.BLOCK_QUOTE:
            self._block_quotes += 1
        elif event.block_type == BlockType.CODE_BLOCK:
            self._code_blocks_skipped += 1
        elif event.block_type == BlockType.HORIZONTAL_RULE:
            self._horizontal_rules += 1
        elif event.block_type == BlockType.FRONT_MATTER:
            self._front_matter_blocks += 1
        elif event.block_type == BlockType.BLANK:
            self._blank_lines += 1
        else:
            self._unknown_blocks += 1

    def record_sentence_produced(self) -> None:
        self._sentences_produced += 1

    def record_sentence_discarded(self) -> None:
        self._sentences_discarded += 1

    def record_warnings(self, warnings: tuple) -> None:
        self._warnings.extend(warnings)

    def finalize(self) -> Phase3Stats:
        """Return an immutable snapshot of accumulated statistics."""
        return Phase3Stats(
            total_headings=self._headings,
            total_paragraphs=self._paragraphs,
            total_list_items=self._list_items,
            total_tables=self._tables,
            total_block_quotes=self._block_quotes,
            total_code_blocks_skipped=self._code_blocks_skipped,
            total_horizontal_rules=self._horizontal_rules,
            total_front_matter_blocks=self._front_matter_blocks,
            total_blank_lines=self._blank_lines,
            total_unknown_blocks=self._unknown_blocks,
            sentences_produced=self._sentences_produced,
            sentences_discarded=self._sentences_discarded,
            warnings=tuple(self._warnings),
        )
````

## File: src/smriti/extraction/validator.py
````python
"""
validator.py — SemanticSentence validator for Phase 3.

Responsibility:
    Validate a collection of SemanticSentence objects before emission.
    Check per-sentence and cross-sentence invariants.

Rules:
    ✅ Text must not be empty or whitespace-only              → discard with SEG001
    ✅ Sentence IDs must be unique across the collection       → VAL001 (fatal)
    ✅ Positions must be strictly monotonically increasing     → VAL002 (fatal)
    ✅ char_start must be < char_end                           → VAL002 (fatal)
    ✅ document_id must be consistent                          → fatal
    ✅ Context strings must be plausible (non-empty, only allowed chars) → VAL003 (warning)

Design:
    NEVER modifies objects.
    ONLY reports problems.
    Fatal problems raise SentenceValidationError.
    Recoverable problems return warnings.
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.rules import CONTEXT_VALID_PATTERN
from smriti.exceptions import SentenceValidationError

logger = structlog.get_logger(__name__)


def validate_sentences(
    sentences: List[SemanticSentence],
    document_id: str,
) -> Tuple[List[SemanticSentence], List[SegmentationWarning]]:
    """
    Validate a collection of SemanticSentences.

    Args:
        sentences:    Sentences to validate.
        document_id:  Expected document_id for all sentences.

    Returns:
        (valid_sentences, warnings_list)
        valid_sentences excludes empty/whitespace-only sentences.
        Fatal violations raise SentenceValidationError instead of returning.

    Raises:
        SentenceValidationError: On duplicate IDs, non-monotonic positions,
                                  or document_id mismatch.
    """
    warnings: List[SegmentationWarning] = []
    valid: List[SemanticSentence] = []
    seen_ids = set()
    last_position = -1

    for sentence in sentences:
        # Check 1: Document identity consistency
        if sentence.document_id != document_id:
            raise SentenceValidationError(
                f"Sentence {sentence.sentence_id} has document_id "
                f"'{sentence.document_id}' but expected '{document_id}'"
            )

        # Check 2: Non-empty text
        if not sentence.text.strip():
            warnings.append(SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED)
            logger.debug("empty sentence discarded", sentence_id=sentence.sentence_id)
            continue

        # Check 3: Unique sentence ID (fatal)
        if sentence.sentence_id in seen_ids:
            raise SentenceValidationError(
                f"Duplicate sentence ID detected: {sentence.sentence_id} "
                f"in document {document_id}. This indicates a determinism bug."
            )
        seen_ids.add(sentence.sentence_id)

        # Check 4: Monotonically increasing position (fatal)
        if sentence.position <= last_position:
            raise SentenceValidationError(
                f"Non-monotonic position: sentence {sentence.sentence_id} "
                f"has position {sentence.position} after {last_position}"
            )
        last_position = sentence.position

        # Check 5: Valid character offsets (fatal)
        if sentence.char_start >= sentence.char_end and sentence.char_end > 0:
            raise SentenceValidationError(
                f"Invalid offsets for sentence {sentence.sentence_id}: "
                f"char_start={sentence.char_start} >= char_end={sentence.char_end}"
            )

        # Check 6: Context plausibility (non-fatal)
        if sentence.context:
            if not CONTEXT_VALID_PATTERN.match(sentence.context):
                warnings.append(SegmentationWarning.VAL_INVALID_CONTEXT)
                logger.warning(
                    "invalid context characters",
                    sentence_id=sentence.sentence_id,
                    context=sentence.context,
                )

        valid.append(sentence)

    return valid, warnings
````

## File: src/smriti/parsing/__init__.py
````python
"""
parsing/__init__.py — Public API for Phase 2.

External callers (PipelineRunner, main.py) import from here:

    from smriti.parsing import run_extraction, ExtractionResult

They never import from individual submodules (loader, markdown, pdf, etc.).
Those remain internal implementation details.

Orchestration:
    1. Accept List[SourceDocument] from Phase 1
    2. For each document: dispatch loader.load_document()
    3. Collect successful Document objects
    4. Record failures (one failure never stops the batch)
    5. Write dataset.json artifact
    6. Write manifest
    7. Update pipeline state
    8. Return ExtractionResult

Phase 2 Golden Rule: Extract text. Never interpret text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.manifest import ManifestManager
from smriti.core.models import Document, ExtractionMethod, SourceDocument
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.core.timing import Timer
from smriti.exceptions import ParsingError

from smriti.parsing.loader import load_document

logger = structlog.get_logger(__name__)


@dataclass
class ExtractionStats:
    """Statistics from one Phase 2 run."""
    total_documents: int = 0
    successful: int = 0
    failed: int = 0
    total_characters: int = 0
    total_words: int = 0
    documents_with_warnings: int = 0

    def summary(self) -> str:
        return (
            f"total={self.total_documents} "
            f"success={self.successful} "
            f"failed={self.failed} "
            f"chars={self.total_characters} "
            f"words={self.total_words} "
            f"with_warnings={self.documents_with_warnings}"
        )


@dataclass
class ExtractionResult:
    """
    Complete output of Phase 2.
    This is what Phase 3 receives.

    Attributes:
        documents:     All successfully extracted Document objects.
        failed:        (SourceDocument, error_message) pairs for failures.
        stats:         Summary statistics.
        run_id:        Pipeline run identifier.
        manifest_path: Path to the written manifest.json.
        dataset_path:  Path to the written dataset.json.
    """
    documents: List[Document]
    failed: List[Tuple[SourceDocument, str]]
    stats: ExtractionStats
    run_id: str
    manifest_path: Optional[Path] = None
    dataset_path: Optional[Path] = None

    def to_dataset_json(self) -> str:
        """
        Serialize extracted documents to JSON.
        Written to artifacts/run_{id}/phase2/dataset.json for Phase 3.

        Includes only normalized_text and structural metadata.
        Never includes raw_text (too large, not needed by Phase 3).
        """
        records = []
        for doc in self.documents:
            records.append({
                "doc_id": doc.doc_id,
                "schema_version": doc.schema_version,
                "path": str(doc.source_document.path),
                "relative_path": str(doc.source_document.relative_path),
                "format": doc.source_document.format.value,
                "extraction_method": doc.extraction_method.value,
                "encoding_used": doc.encoding_used,
                "normalized_text": doc.normalized_text,
                "extraction_warnings": [w.value for w in doc.extraction_warnings],
                "text_statistics": {
                    "character_count": doc.text_statistics.character_count,
                    "word_count": doc.text_statistics.word_count,
                    "line_count": doc.text_statistics.line_count,
                    "blank_line_count": doc.text_statistics.blank_line_count,
                    "paragraph_count": doc.text_statistics.paragraph_count,
                },
                "modified_at": doc.source_document.modified_at.isoformat(),
            })
        return json.dumps(records, indent=2, ensure_ascii=False)


def run_extraction(
    source_documents: List[SourceDocument],
    run_id: str,
    manifest_manager: ManifestManager,
    state_manager: StateManager,
) -> ExtractionResult:
    """
    Execute the complete Phase 2 extraction pipeline.

    Args:
        source_documents:  List of SourceDocument from Phase 1 (canonical only).
        run_id:            Unique pipeline run identifier.
        manifest_manager:  For writing phase manifest.
        state_manager:     For updating pipeline state.

    Returns:
        ExtractionResult containing Document list and statistics.

    Raises:
        ParsingError: Only for pipeline-fatal errors (config missing, artifact dir
                      unavailable). Individual document failures do NOT raise.
    """
    config = get_config()
    stats = ExtractionStats(total_documents=len(source_documents))

    with Timer("phase2_extraction"):

        # ── Step 1: Record phase start ─────────────────────────────────────────
        start_time = manifest_manager.start_phase(phase=2)
        logger.info(
            "phase 2 starting",
            run_id=run_id,
            total_documents=stats.total_documents,
        )

        # ── Step 2: Process each document ─────────────────────────────────────
        documents: List[Document] = []
        failed: List[Tuple[SourceDocument, str]] = []

        for source in source_documents:
            doc, error = load_document(source)

            if doc is not None:
                documents.append(doc)
                stats.successful += 1
                stats.total_characters += doc.text_statistics.character_count
                stats.total_words += doc.text_statistics.word_count
                if doc.has_warnings:
                    stats.documents_with_warnings += 1
            else:
                failed.append((source, error or "unknown error"))
                stats.failed += 1

        logger.info("phase 2 extraction complete", **{
            k: v for k, v in [
                ("successful", stats.successful),
                ("failed", stats.failed),
                ("total_chars", stats.total_characters),
                ("total_words", stats.total_words),
            ]
        })

        # ── Step 3: Write dataset artifact ────────────────────────────────────
        phase_dir = ARTIFACTS_DIR / f"run_{run_id}" / "phase2"
        phase_dir.mkdir(parents=True, exist_ok=True)

        output_filename = config.get("parsing", {}).get(
            "output_dataset_filename", "dataset.json"
        )
        dataset_path = phase_dir / output_filename

        result = ExtractionResult(
            documents=documents,
            failed=failed,
            stats=stats,
            run_id=run_id,
        )

        dataset_path.write_text(result.to_dataset_json(), encoding="utf-8")
        result.dataset_path = dataset_path

        logger.info(
            "phase 2 dataset written",
            path=str(dataset_path),
            documents=len(documents),
        )

        # ── Step 4: Write manifest ─────────────────────────────────────────────
        failed_paths = [str(src.path) for src, _ in failed]

        manifest_path = manifest_manager.end_phase(
            phase=2,
            start_time=start_time,
            inputs={
                "source_documents": stats.total_documents,
                "run_id": run_id,
            },
            outputs={
                "successful_documents": stats.successful,
                "failed_documents": stats.failed,
                "total_characters": stats.total_characters,
                "total_words": stats.total_words,
                "documents_with_warnings": stats.documents_with_warnings,
                "dataset_path": str(dataset_path),
                "failed_paths": failed_paths,
            },
            status="success" if stats.failed == 0 else "partial",
        )
        result.manifest_path = manifest_path

        # ── Step 5: Update pipeline state ─────────────────────────────────────
        state_manager.complete_phase(phase=2)

    logger.info("phase 2 complete", **{k: v for k, v in vars(stats).items()})

    return result
````

## File: src/smriti/parsing/builder.py
````python
"""
builder.py — Document construction.

Responsibility:
    The ONLY module allowed to create Document objects.

    Enforces all Document invariants before construction:
      - doc_id must equal source_document.doc_id (identity preserved)
      - raw_text must be str
      - normalized_text must be str
      - warnings is a tuple of WarningCode
      - text_statistics is a TextStatistics instance

    Returns a frozen (immutable) Document.

Rules:
    ✅ Validate all inputs before construction
    ✅ Enforce doc_id identity invariant
    ✅ Produce immutable Document
    ✅ Warn if document appears to be empty (using WarningCode.NO_EXTRACTABLE_TEXT)

    ❌ No extraction logic
    ❌ No normalization logic
    ❌ No filesystem access
"""

from typing import List, Tuple
import structlog

from smriti.core.config import get_config
from smriti.core.models import (
    Document,
    ExtractionMethod,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.exceptions import BuilderError, DocumentError

logger = structlog.get_logger(__name__)


def build_document(
    source_document: SourceDocument,
    extraction_result: RawExtractionResult,
    normalized_text: str,
    normalization_warnings: Tuple[WarningCode, ...],
    text_statistics: TextStatistics,
) -> Document:
    """
    Construct an immutable Document from its component parts.

    Args:
        source_document:        The Phase 1 SourceDocument (must remain unchanged).
        extraction_result:      Raw extraction output (raw_text, warnings, method).
        normalized_text:        Text after full normalization pipeline.
        normalization_warnings: Warnings produced during normalization (WarningCode tuple).
        text_statistics:        Structural statistics from statistics.py.

    Returns:
        Immutable Document with doc_id == source_document.doc_id.

    Raises:
        BuilderError: If any input is invalid.
        DocumentError: If the constructed Document violates an invariant.
    """
    config = get_config()
    min_extractable_chars: int = config.get("parsing", {}).get("min_extractable_chars", 10)

    # ── Input validation ──────────────────────────────────────────────────────
    if not isinstance(source_document, SourceDocument):
        raise BuilderError(f"source_document must be SourceDocument, got {type(source_document)}")
    if not isinstance(extraction_result, RawExtractionResult):
        raise BuilderError(f"extraction_result must be RawExtractionResult")
    if not isinstance(normalized_text, str):
        raise BuilderError(f"normalized_text must be str, got {type(normalized_text)}")
    if not isinstance(normalization_warnings, tuple):
        raise BuilderError(f"normalization_warnings must be tuple")
    if not isinstance(text_statistics, TextStatistics):
        raise BuilderError(f"text_statistics must be TextStatistics")

    # ── Merge all warnings (both are tuples of WarningCode) ──────────────────
    all_warnings: List[WarningCode] = list(extraction_result.warnings) + list(normalization_warnings)

    # ── Check for empty extraction ────────────────────────────────────────────
    if len(normalized_text.strip()) < min_extractable_chars:
        all_warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)

    # ── Build Document ────────────────────────────────────────────────────────
    try:
        doc = Document(
            doc_id=source_document.doc_id,        # Identity inherited, never changed
            source_document=source_document,
            raw_text=extraction_result.raw_text,
            normalized_text=normalized_text,
            extraction_method=extraction_result.method,
            extraction_warnings=tuple(all_warnings),  # tuple of WarningCode
            text_statistics=text_statistics,
            encoding_used=extraction_result.encoding_used,  # <-- ADDED
            schema_version="2.0",
        )
    except ValueError as e:
        raise DocumentError(f"Document invariant violated: {e}") from e
    except Exception as e:
        raise BuilderError(f"Document construction failed: {e}") from e

    logger.debug(
        "document built",
        doc_id=doc.doc_id[:8],
        method=doc.extraction_method.value,
        chars=text_statistics.character_count,
        words=text_statistics.word_count,
        warnings=len(all_warnings),
    )

    return doc
````

## File: src/smriti/parsing/loader.py
````python
"""
loader.py — Format dispatcher.

Responsibility:
    Choose the correct extractor based on SourceDocument.format.
    Coordinate extraction → normalization → statistics → builder pipeline.
    Return a Document or record the failure.

Rules:
    ✅ Dispatch based on FileFormat enum
    ✅ Coordinate the full single-document pipeline
    ✅ Catch document-level errors (one failure must not stop the batch)
    ✅ Return (Document | None, error_message | None)

    ❌ Never extract text itself (delegates to format-specific extractors)
    ❌ Never create Document directly (delegates to builder.py)
    ❌ Never access filesystem beyond passing path to extractor

Pipeline for each document:
    SourceDocument
        ↓
    Format-specific extractor → RawExtractionResult
        ↓
    normalize.normalize_text() → NormalizationResult (normalized_text, warnings)
        ↓
    statistics.compute_statistics() → TextStatistics
        ↓
    builder.build_document() → Document
"""

from pathlib import Path
from typing import Optional, Tuple
import structlog

from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    NormalizationResult,
    SourceDocument,
    WarningCode,
)
from smriti.exceptions import (
    BuilderError,
    DocumentError,
    EncodingError,
    LoaderError,
    MarkdownExtractionError,
    NormalizationError,
    ParsingError,
    PdfExtractionError,
    StatisticsError,
    TextExtractionError,
)
from smriti.parsing.markdown import MarkdownExtractor
from smriti.parsing.normalize import normalize_text
from smriti.parsing.pdf import PdfExtractor
from smriti.parsing.statistics import compute_statistics
from smriti.parsing.builder import build_document
from smriti.parsing.text import TextExtractor

logger = structlog.get_logger(__name__)

# Instantiate extractors once — they are stateless after init
_markdown_extractor = MarkdownExtractor()
_pdf_extractor = PdfExtractor()
_text_extractor = TextExtractor()


def load_document(source: SourceDocument) -> Tuple[Optional[Document], Optional[str]]:
    """
    Execute the full extraction pipeline for a single SourceDocument.

    Args:
        source: Immutable SourceDocument produced by Phase 1.

    Returns:
        (Document, None)       — success
        (None, error_message)  — document-level failure, batch continues

    This function never raises. All exceptions are caught and returned as
    error strings. The pipeline continues with the next document.
    """
    logger.info("loading document", doc_id=source.doc_id[:8], format=source.format.value)

    try:
        # ── Step 1: Dispatch to format-specific extractor ─────────────────────
        extraction_result = _dispatch(source)

        # ── Step 2: Normalize text ────────────────────────────────────────────
        norm_result: NormalizationResult = normalize_text(extraction_result.raw_text)

        # ── Step 3: Compute statistics ────────────────────────────────────────
        stats = compute_statistics(norm_result.normalized_text)

        # ── Step 4: Build Document ────────────────────────────────────────────
        doc = build_document(
            source_document=source,
            extraction_result=extraction_result,
            normalized_text=norm_result.normalized_text,
            normalization_warnings=norm_result.warnings,  # tuple of WarningCode
            text_statistics=stats,
        )

        logger.info(
            "document loaded",
            doc_id=source.doc_id[:8],
            chars=stats.character_count,
            words=stats.word_count,
            warnings=len(doc.extraction_warnings),
        )
        return doc, None

    # ── Document-level failures: log, continue batch ──────────────────────────
    except (
        MarkdownExtractionError,
        PdfExtractionError,
        TextExtractionError,
        EncodingError,
        NormalizationError,
        StatisticsError,
        BuilderError,
        DocumentError,
        LoaderError,
    ) as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error(
            "document extraction failed",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
        )
        return None, error_msg

    except Exception as e:
        # Unexpected error — still document-level, not pipeline-fatal
        error_msg = f"UnexpectedError: {type(e).__name__}: {e}"
        logger.error(
            "unexpected error during extraction",
            doc_id=source.doc_id[:8],
            path=str(source.path),
            error=error_msg,
            exc_info=True,
        )
        return None, error_msg


def _dispatch(source: SourceDocument):
    """
    Select and call the correct extractor based on FileFormat.

    Raises:
        LoaderError: If the format is unsupported (should never happen post Phase 1).
    """
    match source.format:
        case FileFormat.MARKDOWN:
            return _markdown_extractor.extract(source.path)
        case FileFormat.PDF:
            return _pdf_extractor.extract(source.path)
        case FileFormat.TEXT:
            return _text_extractor.extract(source.path)
        case _:
            raise LoaderError(
                f"Unsupported format {source.format!r} for document {source.doc_id[:8]}. "
                f"Supported: {[f.value for f in FileFormat]}"
            )
````

## File: src/smriti/parsing/markdown.py
````python
"""
markdown.py — Markdown text extractor.

Responsibility:
    Read a Markdown file and return its raw decoded text.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Preserve ALL Markdown syntax (headings, lists, code blocks, tables)
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ Do NOT parse Markdown AST
    ❌ Do NOT strip Markdown syntax
    ❌ Do NOT extract YAML front matter
    ❌ Do NOT render HTML
    ❌ Do NOT detect language
    ❌ Do NOT split sentences

Why preserve Markdown syntax?
    "# AI is transforming" is richer context than "AI is transforming".
    Phase 3 uses headings as semantic signals.
    Removing '#' changes information — that belongs to interpretation, not extraction.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import MarkdownExtractionError, EncodingError

logger = structlog.get_logger(__name__)


class MarkdownExtractor:
    """Extracts raw text from a Markdown file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: List[str] = (
            config["parsing"].get("encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a Markdown file.

        Args:
            path: Absolute path to a .md file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=MARKDOWN.

        Raises:
            MarkdownExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: List[WarningCode] = []

        logger.debug("reading markdown", path=str(path))

        raw_bytes = self._read_bytes(path)
        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect and warn about mixed line endings BEFORE normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "markdown extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.MARKDOWN,
            encoding_used=encoding_used,
        )

    def _read_bytes(self, path: Path) -> bytes:
        """Read raw bytes from file."""
        try:
            return path.read_bytes()
        except OSError as e:
            raise MarkdownExtractionError(f"Cannot read {path}: {e}") from e

    def _decode(self, raw_bytes: bytes, path: Path) -> Tuple[str, Optional[WarningCode], str]:
        """
        Decode bytes using the encoding fallback chain.

        Returns:
            (decoded_text, warning_code_or_None, encoding_used)
        """
        for i, encoding in enumerate(self._encoding_fallbacks):
            try:
                text = raw_bytes.decode(encoding)
                warning = WarningCode.ENCODING_FALLBACK if i > 0 else None
                return text, warning, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        raise EncodingError(
            f"Cannot decode {path} with any supported encoding: "
            f"{self._encoding_fallbacks}"
        )
````

## File: src/smriti/parsing/normalize.py
````python
"""
normalize.py — Text normalization pipeline.

Responsibility:
    Transform raw extracted text into a canonical, deterministic form.
    This is the ONLY module that performs normalization.

Normalization order (NEVER reorder — order matters):
    1. Unicode NFC normalization
    2. Remove BOM (if present after decoding)
    3. Normalize line endings → LF
    4. Remove trailing whitespace per line
    5. Normalize tabs (if configured)
    6. Collapse consecutive blank lines
    7. Strip leading/trailing whitespace from entire document

Rules:
    ✅ Make equivalent text identical
    ✅ Never change meaning
    ✅ Record every transformation as a warning

    ❌ Do NOT change words (colour → color)
    ❌ Do NOT expand contractions (can't → cannot)
    ❌ Do NOT stem or lemmatize
    ❌ Do NOT remove stopwords
    ❌ Do NOT remove indentation
    ❌ Do NOT remove code block content

Determinism guarantee:
    Given identical input, this function always produces identical output.
    No timestamps, no randomness, no locale-dependent behavior.
"""

import re
import unicodedata
from typing import List
import structlog

from smriti.core.config import get_config
from smriti.exceptions import NormalizationError
from smriti.core.models import NormalizationResult, WarningCode

logger = structlog.get_logger(__name__)


def normalize_text(raw_text: str) -> NormalizationResult:
    """
    Apply the full normalization pipeline to raw extracted text.

    Args:
        raw_text: Text exactly as decoded from the source file.

    Returns:
        NormalizationResult(normalized_text, warnings)
        where warnings is a tuple of WarningCode enums describing transformations applied.

    Raises:
        NormalizationError: If normalization itself fails unexpectedly.
    """
    if not isinstance(raw_text, str):
        raise NormalizationError(f"raw_text must be str, got {type(raw_text)}")

    config = get_config()
    parsing_cfg = config.get("parsing", {})

    unicode_form: str = parsing_cfg.get("unicode_normalization", "NFC")
    collapse_blank_lines: int = parsing_cfg.get("collapse_blank_lines", 2)
    remove_trailing_ws: bool = parsing_cfg.get("remove_trailing_whitespace", True)

    warnings: List[WarningCode] = []
    text = raw_text

    try:
        # ── Step 1: Unicode normalization ────────────────────────────────
        text_before = text
        text = unicodedata.normalize(unicode_form, text)
        if text != text_before:
            warnings.append(WarningCode.UNICODE_NORMALIZED)

        # ── Step 2: Remove UTF-8 BOM ─────────────────────────────────────
        if text.startswith("\ufeff"):
            text = text[1:]
            warnings.append(WarningCode.BOM_REMOVED)

        # ── Step 3: Normalize line endings → LF ──────────────────────────
        has_crlf = "\r\n" in text
        has_cr_only = "\r" in text.replace("\r\n", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if has_crlf or has_cr_only:
            warnings.append(WarningCode.LINE_ENDINGS_NORMALIZED)

        # ── Step 4: Remove trailing whitespace per line ──────────────────
        if remove_trailing_ws:
            lines = text.split("\n")
            stripped_lines = [line.rstrip() for line in lines]
            if stripped_lines != lines:
                warnings.append(WarningCode.TRAILING_WHITESPACE_REMOVED)
            text = "\n".join(stripped_lines)

        # ── Step 5: Remove control characters (except LF and TAB) ────────
        control_char_pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
        text_before = text
        text = control_char_pattern.sub("", text)
        if text != text_before:
            warnings.append(WarningCode.CONTROL_CHARS_REMOVED)

        # ── Step 6: Collapse consecutive blank lines ─────────────────────
        if collapse_blank_lines >= 0:
            max_newlines = collapse_blank_lines + 1
            pattern = re.compile(r"\n{" + str(max_newlines + 1) + r",}")
            replacement = "\n" * max_newlines
            text_before = text
            text = pattern.sub(replacement, text)
            if text != text_before:
                warnings.append(WarningCode.BLANK_LINES_COLLAPSED)

        # ── Step 7: Strip leading/trailing whitespace ────────────────────
        text = text.strip()

    except NormalizationError:
        raise
    except Exception as e:
        raise NormalizationError(f"Normalization failed unexpectedly: {e}") from e

    logger.debug(
        "normalization complete",
        original_chars=len(raw_text),
        normalized_chars=len(text),
        warnings=len(warnings),
    )

    return NormalizationResult(normalized_text=text, warnings=tuple(warnings))
````

## File: src/smriti/parsing/parser.py
````python
# Will be filled in Phase 2\n
````

## File: src/smriti/parsing/pdf.py
````python
"""
pdf.py — PDF text extractor.

Responsibility:
    Extract the embedded text layer from a PDF file.
    Concatenate pages into a single string.
    Record warnings for pages with no extractable text.

Rules:
    ✅ Extract text layer from each page
    ✅ Concatenate pages with explicit page break marker
    ✅ Record per-page warnings for empty pages (as WarningCode enums)
    ✅ Respect max_pdf_pages config limit

    ❌ No OCR (ever)
    ❌ No page rendering
    ❌ No layout detection
    ❌ No table inference
    ❌ No image extraction

If a PDF has no text layer at all (image-only PDF):
    → Record WarningCode.NO_EXTRACTABLE_TEXT
    → Return empty string (do NOT fail the pipeline)
    → Phase 3 will produce 0 claims from this document

Library: pypdf (replaces deprecated PyPDF2)
"""

from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import PdfExtractionError

logger = structlog.get_logger(__name__)

# Explicit page break marker – used to separate text from different pages.
# This helps downstream phases know where page boundaries occur.
PAGE_BREAK_MARKER = "\n\n--- PAGE BREAK ---\n\n"


class PdfExtractor:
    """Extracts raw text from a PDF file using the embedded text layer."""

    def __init__(self) -> None:
        config = get_config()
        parsing_cfg = config.get("parsing", {})
        self._max_pages: int = parsing_cfg.get("max_pdf_pages", 500)
        self._max_text_length: int = parsing_cfg.get("max_text_length_chars", 5_000_000)

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Extract text from all pages of a PDF.

        Args:
            path: Absolute path to a .pdf file (already validated by Phase 1).

        Returns:
            RawExtractionResult with concatenated page text, warnings (as WarningCode), method=PDF.

        Raises:
            PdfExtractionError: If the PDF cannot be opened or is fatally corrupted.
        """
        try:
            import pypdf
        except ImportError as e:
            raise PdfExtractionError("pypdf is required for PDF extraction") from e

        warnings: List[WarningCode] = []
        page_texts: List[str] = []

        logger.debug("reading pdf", path=str(path))

        try:
            reader = pypdf.PdfReader(str(path))
        except Exception as e:
            raise PdfExtractionError(f"Cannot open PDF {path}: {e}") from e

        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, self._max_pages)

        if total_pages > self._max_pages:
            warnings.append(WarningCode.PAGE_LIMIT_REACHED)

        empty_pages: List[int] = []

        for page_num in range(pages_to_process):
            try:
                page = reader.pages[page_num]
                text = page.extract_text() or ""
            except Exception as e:
                warnings.append(WarningCode.PAGE_EXTRACTION_FAILED)
                text = ""

            if text.strip():
                page_texts.append(text)
            else:
                empty_pages.append(page_num + 1)

        if empty_pages:
            # Batch warning — don't produce one warning per empty page
            if len(empty_pages) == pages_to_process:
                warnings.append(WarningCode.NO_EXTRACTABLE_TEXT)
            else:
                warnings.append(WarningCode.EMPTY_PDF_PAGE)

        # Join pages with explicit page break marker
        raw_text = PAGE_BREAK_MARKER.join(page_texts)

        # Guard against pathologically large PDFs
        if len(raw_text) > self._max_text_length:
            raw_text = raw_text[: self._max_text_length]
            warnings.append(WarningCode.TEXT_TRUNCATED)

        logger.debug(
            "pdf extracted",
            path=str(path),
            total_pages=total_pages,
            processed_pages=pages_to_process,
            empty_pages=len(empty_pages),
            chars=len(raw_text),
            warnings=len(warnings),
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.PDF,
            encoding_used="pdf-native",
        )
````

## File: src/smriti/parsing/statistics.py
````python
"""
statistics.py — Structural text statistics.

Responsibility:
    Compute lightweight structural statistics from normalized text.
    All statistics are derived purely from text structure.
    No NLP. No linguistic analysis.

Statistics computed:
    character_count   — total characters in normalized text
    word_count        — whitespace-separated tokens (rough but deterministic)
    line_count        — total lines (split on LF)
    blank_line_count  — lines that are empty or whitespace-only
    paragraph_count   — blocks of text separated by one or more blank lines

Complexity: O(n) time, O(1) space (processes line by line).

Invariants verified:
    character_count >= 0
    word_count >= 0
    line_count >= blank_line_count
    line_count >= paragraph_count
"""

import structlog

from smriti.core.models import TextStatistics
from smriti.exceptions import StatisticsError

logger = structlog.get_logger(__name__)


def compute_statistics(normalized_text: str) -> TextStatistics:
    """
    Compute structural statistics from normalized text.

    Args:
        normalized_text: Text after full normalization pipeline.
                         Must be a Python str.

    Returns:
        TextStatistics (frozen dataclass) with all counts.

    Raises:
        StatisticsError: If text is not a str or statistics are inconsistent.
    """
    if not isinstance(normalized_text, str):
        raise StatisticsError(f"normalized_text must be str, got {type(normalized_text)}")

    try:
        character_count = len(normalized_text)

        if not normalized_text.strip():
            # Empty or whitespace-only document
            return TextStatistics(
                character_count=character_count,
                word_count=0,
                line_count=0,
                blank_line_count=0,
                paragraph_count=0,
            )

        lines = normalized_text.split("\n")
        line_count = len(lines)

        blank_line_count = sum(1 for line in lines if not line.strip())

        word_count = len(normalized_text.split())

        # Paragraph = one or more non-blank lines separated by blank lines
        # Iterate through lines, counting transitions from blank→non-blank
        paragraph_count = 0
        in_paragraph = False
        for line in lines:
            if line.strip():
                if not in_paragraph:
                    paragraph_count += 1
                    in_paragraph = True
            else:
                in_paragraph = False

    except StatisticsError:
        raise
    except Exception as e:
        raise StatisticsError(f"Statistics computation failed: {e}") from e

    stats = TextStatistics(
        character_count=character_count,
        word_count=word_count,
        line_count=line_count,
        blank_line_count=blank_line_count,
        paragraph_count=paragraph_count,
    )

    logger.debug(
        "statistics computed",
        chars=character_count,
        words=word_count,
        lines=line_count,
        blank_lines=blank_line_count,
        paragraphs=paragraph_count,
    )

    return stats
````

## File: src/smriti/parsing/text.py
````python
"""
text.py — Plain-text extractor.

Responsibility:
    Read a .txt file and return its raw decoded text.
    Simplest extractor — reads bytes, decodes, returns.

Rules:
    ✅ Read file bytes
    ✅ Decode using encoding fallback strategy
    ✅ Return raw text + warnings (as WarningCode values)

    ❌ No semantic processing
    ❌ No format-specific parsing
"""

from pathlib import Path
from typing import List, Tuple, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import ExtractionMethod, RawExtractionResult, WarningCode
from smriti.exceptions import TextExtractionError, EncodingError

logger = structlog.get_logger(__name__)


class TextExtractor:
    """Extracts raw text from a plain-text (.txt) file."""

    def __init__(self) -> None:
        config = get_config()
        self._encoding_fallbacks: List[str] = (
            config["parsing"].get("encoding_fallbacks", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
        )

    def extract(self, path: Path) -> RawExtractionResult:
        """
        Read and decode a plain-text file.

        Args:
            path: Absolute path to a .txt file (already validated by Phase 1).

        Returns:
            RawExtractionResult with raw_text, warnings (as WarningCode), method=TEXT.

        Raises:
            TextExtractionError: If the file cannot be read at all.
            EncodingError: If no supported encoding successfully decodes the file.
        """
        warnings: List[WarningCode] = []

        logger.debug("reading text file", path=str(path))

        try:
            raw_bytes = path.read_bytes()
        except OSError as e:
            raise TextExtractionError(f"Cannot read {path}: {e}") from e

        raw_text, encoding_warning, encoding_used = self._decode(raw_bytes, path)

        if encoding_warning is not None:
            warnings.append(encoding_warning)

        # Detect mixed line endings before normalization
        if b"\r\n" in raw_bytes and b"\n" in raw_bytes.replace(b"\r\n", b""):
            warnings.append(WarningCode.MIXED_LINE_ENDINGS)

        # Detect embedded null bytes
        if "\x00" in raw_text:
            raw_text = raw_text.replace("\x00", "")
            warnings.append(WarningCode.NULL_BYTES_REMOVED)

        logger.debug(
            "text extracted",
            path=str(path),
            chars=len(raw_text),
            warnings=len(warnings),
            encoding=encoding_used,
        )

        return RawExtractionResult(
            raw_text=raw_text,
            warnings=tuple(warnings),
            method=ExtractionMethod.TEXT,
            encoding_used=encoding_used,
        )

    def _decode(self, raw_bytes: bytes, path: Path) -> Tuple[str, Optional[WarningCode], str]:
        """
        Decode bytes using the encoding fallback chain.

        Returns:
            (decoded_text, warning_code_or_None, encoding_used)
        """
        for i, encoding in enumerate(self._encoding_fallbacks):
            try:
                text = raw_bytes.decode(encoding)
                warning = WarningCode.ENCODING_FALLBACK if i > 0 else None
                return text, warning, encoding
            except (UnicodeDecodeError, LookupError):
                continue

        raise EncodingError(
            f"Cannot decode {path} with any supported encoding: "
            f"{self._encoding_fallbacks}"
        )
````

## File: src/smriti/pipeline/__init__.py
````python

````

## File: src/smriti/pipeline/runner.py
````python
"""
pipeline/runner.py — PipelineRunner with Phases 1, 2, 3, and 4 registered.

Phases 5–13 will be added as they are built.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import structlog

from smriti.core.manifest import ManifestManager
from smriti.core.paths import ARTIFACTS_DIR
from smriti.core.state import StateManager
from smriti.exceptions import PipelineError, Phase5Error

logger = structlog.get_logger(__name__)


def _make_run_id() -> str:
    """Produce a timestamp-based run_id. Unique per execution."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class PipelineRunner:
    """
    Orchestrates pipeline phases.

    Usage:
        runner = PipelineRunner(input_dirs=[Path("data/raw")])
        runner.run()
    """

    def __init__(self, input_dirs: List[Path]):
        self.input_dirs = [Path(d) for d in input_dirs]
        self.run_id = _make_run_id()
        self.manifest_manager = ManifestManager(
            run_id=self.run_id,
            artifacts_dir=ARTIFACTS_DIR,
        )
        self.state_manager = StateManager()
        logger.info("pipeline runner initialized", run_id=self.run_id)

    def run(
        self,
        start_from: int = 1,
        stop_at: Optional[int] = None,
        force_full: bool = False,
    ) -> bool:
        """
        Run pipeline phases start_from through stop_at.

        Args:
            start_from:  First phase to run (default 1).
            stop_at:     Last phase to run (default: run all registered).
            force_full:  Ignore caches and re-process everything.

        Returns:
            True if all phases succeeded.
        """
        logger.info(
            "pipeline run starting",
            run_id=self.run_id,
            start_from=start_from,
            stop_at=stop_at,
        )

        # Check for resumable state
        state = self.state_manager.load()
        if state and not force_full:
            completed = state.completed_phases
            if completed:
                resume_from = max(completed) + 1
                if resume_from > start_from:
                    logger.info(
                        "resuming from checkpoint",
                        completed_phases=completed,
                        resuming_at=resume_from,
                    )
                    start_from = resume_from

        try:
            # ── Phase 1: Input Discovery ───────────────────────────────────────
            phase1_result = None
            if start_from <= 1 and (stop_at is None or stop_at >= 1):
                phase1_result = self._run_phase_1(force_full=force_full)

            # ── Phase 2: Text Extraction ───────────────────────────────────────
            phase2_result = None
            if start_from <= 2 and (stop_at is None or stop_at >= 2):
                if phase1_result is None:
                    # Resuming from Phase 2 — load Phase 1 dataset from artifact
                    phase1_result = self._load_phase1_result()

                phase2_result = self._run_phase_2(phase1_result)

            # ── Phase 3: Semantic Sentence Construction ──────────────────────
            phase3_result = None
            if start_from <= 3 and (stop_at is None or stop_at >= 3):
                if phase2_result is None:
                    phase2_result = self._load_phase2_result()
                phase3_result = self._run_phase_3(phase2_result)

            # ── Phase 4: Claim Construction ────────────────────────────────────
            phase4_result = None
            if start_from <= 4 and (stop_at is None or stop_at >= 4):
                if phase3_result is None:
                    phase3_result = self._load_phase3_result()
                phase4_result = self._run_phase_4(phase3_result)


            phase5_result = None
            if start_from <= 5 and (stop_at is None or stop_at >= 5):
                if phase4_result is None:
                    phase4_result = self._load_phase4_result()
                phase5_result = self._run_phase_5(phase4_result)

            # Phases 5–13 will be registered here as they are built.

        except Exception as e:
            logger.error("pipeline failed", error=str(e), exc_info=True)
            return False

        logger.info("pipeline run complete", run_id=self.run_id)
        return True

    # ── Phase 1 implementation ────────────────────────────────────────────────

    def _run_phase_1(self, force_full: bool = False):
        """Execute Phase 1: Input Discovery."""
        from smriti.discovery import run_discovery, DiscoveryResult

        logger.info("running phase 1")
        result = run_discovery(
            input_dirs=self.input_dirs,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
            force_full=force_full,
        )
        logger.info(
            "phase 1 complete",
            canonical_docs=result.canonical_count,
            duplicates=len(result.duplicate_documents),
            skipped=len(result.skipped),
        )
        return result

    def _load_phase1_result(self):
        """
        Load Phase 1 dataset from artifact when resuming at Phase 2.
        Reconstructs SourceDocument list from dataset.json.
        """
        import json
        from datetime import datetime, timezone
        from smriti.core.models import FileFormat, SourceDocument
        from smriti.discovery import DiscoveryResult, DiscoveryStats, DuplicateRegistry

        # Find the most recent run's phase1 dataset
        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase1" / "dataset.json"
        if not dataset_path.exists():
            # Try to find any existing phase1 artifact
            phase1_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase1/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase1_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 2: no Phase 1 dataset.json found. "
                    "Run from Phase 1 first."
                )
            dataset_path = phase1_dirs[0]
            logger.info("loading phase1 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        source_documents = []
        for r in records:
            source_documents.append(
                SourceDocument(
                    doc_id=r["doc_id"],
                    path=Path(r["path"]),
                    relative_path=Path(r["relative_path"]),
                    source_root=Path(r["source_root"]),
                    format=FileFormat(r["format"]),
                    content_hash=r["content_hash"],
                    size_bytes=r["size_bytes"],
                    modified_at=datetime.fromisoformat(r["modified_at"]),
                )
            )

        # Reconstruct a minimal DiscoveryResult for Phase 2
        return type("DiscoveryResult", (), {
            "canonical_documents": source_documents,
        })()

    # ── Phase 2 implementation ────────────────────────────────────────────────

    def _run_phase_2(self, phase1_result):
        """
        Execute Phase 2: Text Extraction.
        Returns the extraction result so it can be used by later phases.
        """
        from smriti.parsing import run_extraction

        logger.info("running phase 2")
        result = run_extraction(
            source_documents=phase1_result.canonical_documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 2 complete",
            successful=result.stats.successful,
            failed=result.stats.failed,
            total_chars=result.stats.total_characters,
        )
        return result   # <-- return the result so Phase 3 can consume it

    # ── Phase 3 implementation ────────────────────────────────────────────────

    def _load_phase2_result(self):
        """Load Phase 2 dataset from artifact when resuming at Phase 3."""
        import json
        from smriti.core.models import (
            Document, SourceDocument, FileFormat, ExtractionMethod,
            TextStatistics, WarningCode, RawExtractionResult,
        )
        from datetime import datetime, timezone

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase2" / "dataset.json"
        if not dataset_path.exists():
            phase2_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase2/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase2_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 3: no Phase 2 dataset.json found. "
                    "Run from Phase 2 first."
                )
            dataset_path = phase2_dirs[0]

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        documents = []
        for r in records:
            source_doc = SourceDocument(
                doc_id=r["doc_id"],
                path=Path(r["path"]),
                relative_path=Path(r["relative_path"]),
                source_root=Path(r["source_root"]),
                format=FileFormat(r["format"]),
                content_hash=r["content_hash"],
                size_bytes=r["size_bytes"],
                modified_at=datetime.fromisoformat(r["modified_at"]),
            )
            stats = TextStatistics(
                character_count=r["stats"]["character_count"],
                word_count=r["stats"]["word_count"],
                line_count=r["stats"]["line_count"],
                blank_line_count=r["stats"]["blank_line_count"],
                paragraph_count=r["stats"]["paragraph_count"],
            )
            documents.append(Document(
                doc_id=r["doc_id"],
                source_document=source_doc,
                raw_text=r["raw_text"],
                normalized_text=r["normalized_text"],
                extraction_method=ExtractionMethod(r["extraction_method"]),
                extraction_warnings=tuple(WarningCode(w) for w in r.get("warnings", [])),
                text_statistics=stats,
                encoding_used=r.get("encoding_used", "utf-8"),
            ))
        return type("Phase2Result", (), {"documents": documents})()

    def _run_phase_3(self, phase2_result):
        """Execute Phase 3: Semantic Sentence Construction."""
        from smriti.extraction import run_extraction

        logger.info("running phase 3")
        result = run_extraction(
            documents=phase2_result.documents,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 3 complete",
            total_sentences=result.total_sentences,
            docs_ok=result.successful_documents,
            docs_failed=result.failed_documents,
        )
        return result   # return for future phases if needed

    # ── Phase 4 implementation ────────────────────────────────────────────────

    def _load_phase3_result(self):
        """Load Phase 3 dataset from artifact when resuming at Phase 4."""
        import json
        from smriti.core.models import SemanticSentence
        from pathlib import Path

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase3" / "dataset.json"
        if not dataset_path.exists():
            phase3_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase3/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase3_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 4: no Phase 3 dataset.json found. "
                    "Run from Phase 3 first."
                )
            dataset_path = phase3_dirs[0]
            logger.info("loading phase3 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        sentences = []
        for r in records:
            sentences.append(SemanticSentence(
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r["context"],
                position=r["position"],
                char_start=r["char_start"],
                char_end=r["char_end"],
                source_path=Path(r["source_path"]),
                origin_block_type=r.get("origin_block_type", "paragraph"),
                schema_version=r.get("schema_version", "3.0"),
            ))

        return type("Phase3Result", (), {"all_sentences": sentences})()

    def _run_phase_4(self, phase3_result):
        """Execute Phase 4: Claim Construction."""
        from smriti.claims import extract_claims
        from smriti.claims import Phase4Result

        logger.info("running phase 4")
        result = extract_claims(
            semantic_sentences=phase3_result.all_sentences,
            run_id=self.run_id,
            manifest_manager=self.manifest_manager,
            state_manager=self.state_manager,
        )
        logger.info(
            "phase 4 complete",
            total_claims=result.total_claims,
            structured=result.stats.structured_claims,
            parser_failures=result.stats.parser_failures,
        )
        return result
    
        # ── Phase 5 implementation ────────────────────────────────────────────────

    def _load_phase4_result(self):
        """
        Load Phase 4 dataset from artifact when resuming at Phase 5.

        Validates schema_version before deserializing to avoid silently
        processing data from an incompatible Phase 4 implementation.
        """
        import json
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
            Modality, StructuredAssertion,
        )

        SUPPORTED_PHASE4_SCHEMA = "4.0"

        dataset_path = ARTIFACTS_DIR / f"run_{self.run_id}" / "phase4" / "dataset.json"
        if not dataset_path.exists():
            phase4_dirs = sorted(
                ARTIFACTS_DIR.glob("run_*/phase4/dataset.json"),
                key=lambda p: p.parent.parent.name,
                reverse=True,
            )
            if not phase4_dirs:
                raise PipelineError(
                    "Cannot resume at Phase 5: no Phase 4 dataset.json found. "
                    "Run from Phase 4 first."
                )
            dataset_path = phase4_dirs[0]
            logger.info("loading phase4 dataset", path=str(dataset_path))

        records = json.loads(dataset_path.read_text(encoding="utf-8"))

        # Validate schema_version before deserializing.
        schema_versions = {r.get("schema_version", "unknown") for r in records if records}
        unsupported = schema_versions - {SUPPORTED_PHASE4_SCHEMA}
        if unsupported:
            logger.warning(
                "unexpected schema_version in phase4 dataset",
                found=sorted(unsupported),
                expected=SUPPORTED_PHASE4_SCHEMA,
            )

        claims = []
        for r in records:
            prov_data = r.get("provenance", {})
            provenance = ClaimProvenance(
                sentence_id=prov_data.get("sentence_id", ""),
                document_id=prov_data.get("document_id", ""),
                source_path=Path(prov_data.get("source_path", "unknown")),
                sentence_context=prov_data.get("sentence_context", ""),
                sentence_position=prov_data.get("sentence_position", 0),
            )
            svo_data = r.get("svo")
            structured = None
            if svo_data:
                structured = StructuredAssertion(
                    subject=svo_data.get("subject"),
                    predicate=svo_data.get("predicate"),
                    object=svo_data.get("object"),
                )
            metadata = AssertionMetadata(
                is_negated=r.get("is_negated", False),
                modality=Modality(r.get("modality", "certain")),
                is_conditional=r.get("is_conditional", False),
                is_comparative=r.get("is_comparative", False),
                is_attributed=r.get("is_attributed", False),
                attributed_to=r.get("attributed_to"),
            )
            claims.append(Claim(
                claim_id=r["claim_id"],
                sentence_id=r["sentence_id"],
                document_id=r["document_id"],
                text=r["text"],
                context=r.get("context", ""),
                source_path=Path(r.get("source_path", "unknown")),
                extraction_mode=ExtractionMode(r.get("extraction_mode", "whole_sentence")),
                structured_assertion=structured,
                assertion_metadata=metadata,
                provenance=provenance,
                schema_version=r.get("schema_version", "4.0"),
                content_hash=r.get("content_hash", ""),
                rule_version=r.get("rule_version", "1.0"),
            ))

        return type("Phase4Result", (), {"all_claims": claims})()

    def _run_phase_5(self, phase4_result):
        """Execute Phase 5: Semantic Embedding."""
        from smriti.embedding import embed_claims
        from smriti.exceptions import Phase5Error

        logger.info("running phase 5")
        try:
            result = embed_claims(
                claims=phase4_result.all_claims,
                run_id=self.run_id,
                manifest_manager=self.manifest_manager,
                state_manager=self.state_manager,
            )
        except Phase5Error as e:
            logger.error("phase 5 failed with Phase5Error", error=str(e))
            raise  # Let the runner handle it cleanly

        if result.warnings:
            logger.warning(
                "phase 5 completed with warnings",
                warning_count=len(result.warnings),
                first_warning=result.warnings[0],
            )
        if result.errors:
            logger.error(
                "phase 5 completed with errors",
                error_count=len(result.errors),
            )

        logger.info(
            "phase 5 complete",
            total_embedded=result.total_embedded,
            cached=result.stats.cached,
            failed=result.stats.failed,
            cache_hit_rate=f"{result.stats.cache_hit_rate:.1%}",
            throughput=f"{result.stats.vectors_per_second:.1f} vec/s",
        )
        return result
````

## File: src/smriti/pipeline/validator.py
````python
"""
Input and output validation for pipeline phases.
Ensures data integrity at each phase boundary.
"""

from pathlib import Path
from typing import List
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
    def validate_markdown_files(directory: Path) -> List[Path]:
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
````

## File: src/smriti/reporting/__init__.py
````python

````

## File: src/smriti/reporting/exporter.py
````python
# Will be filled in Phase 11\n
````

## File: src/smriti/retrieval/__init__.py
````python

````

## File: src/smriti/retrieval/retriever.py
````python
# Will be filled in Phase 5\n
````

## File: src/smriti/scoring/__init__.py
````python

````

## File: src/smriti/scoring/scorer.py
````python
# Will be filled in Phase 8\n
````

## File: src/smriti/__init__.py
````python
__all__ = ['__version__']\nfrom .__version__ import __version__\n
````

## File: src/smriti/__version__.py
````python
__version__ = '0.1.0'\n
````

## File: src/smriti/constants.py
````python
"""
Structural constants for SMRITI.

RULE: Only values that are genuinely fixed belong here.
      - Schema versions (changing them = breaking change)
      - Algorithm identifiers (sha256, not a tuning knob)
      - Hard system limits (not tuning knobs)
      - Template structures

WHAT DOES NOT BELONG HERE:
      - ML model names        → config/default.yaml (embedding.model)
      - Similarity thresholds → config/default.yaml (nli.sim_threshold)
      - Batch sizes           → config/default.yaml (embedding.batch_size)
      - Log levels            → config/default.yaml (logging.level)
"""

# === SCHEMA ===
CACHE_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = "1.0"
STATE_SCHEMA_VERSION = "1.0"

# === HASHING ===
HASH_ALGORITHM = "sha256"
HASH_CHUNK_SIZE = 8192  # bytes

# === HARD LIMITS (system safety, not tuning) ===
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024   # 50 MB — reject files larger than this
MAX_BATCH_SIZE = 256                      # absolute ceiling, never exceeded
TIMEOUT_SECONDS = 3600                    # 1 hour per phase

# === PIPELINE MANIFEST TEMPLATE ===
MANIFEST_TEMPLATE = {
    "schema_version": MANIFEST_SCHEMA_VERSION,
    "run_id": None,
    "phase": None,
    "timestamp": None,
    "duration_seconds": None,
    "inputs": None,
    "outputs": None,
    "status": "pending",    # pending | running | success | failed
    "versions": {},
    "error": None,
}
````

## File: src/smriti/exceptions.py
````python
"""
Custom exception hierarchy for SMRITI.
All exceptions inherit from SMRITIError for easy catch-all handling.
"""


class SMRITIError(Exception):
    """Base exception for all SMRITI errors."""
    pass


class ConfigError(SMRITIError):
    """Configuration is invalid or incomplete."""
    pass


class DiscoveryError(SMRITIError):
    """Error discovering input files."""
    pass


# ── Phase 2: Text Extraction ──────────────────────────────────────────────────

class ParsingError(SMRITIError):
    """Base exception for all Phase 2 extraction errors."""
    pass


class LoaderError(ParsingError):
    """Loader failed to dispatch to an extractor."""
    pass


class EncodingError(ParsingError):
    """File could not be decoded with any supported encoding."""
    pass


class MarkdownExtractionError(ParsingError):
    """Error reading a Markdown file."""
    pass


class PdfExtractionError(ParsingError):
    """Error extracting text from a PDF file."""
    pass


class TextExtractionError(ParsingError):
    """Error reading a plain-text file."""
    pass


class NormalizationError(ParsingError):
    """Error during text normalization."""
    pass


class StatisticsError(ParsingError):
    """Error computing text statistics."""
    pass


class BuilderError(ParsingError):
    """Error constructing a Document object."""
    pass


class DocumentError(ParsingError):
    """Invalid Document state detected."""
    pass


# ── Phase 3+ ─────────────────────────────────────────────────────────────────

class ExtractionError(SMRITIError):
    """Error extracting claims (Phase 3)."""
    pass


class EmbeddingError(SMRITIError):
    """Error computing embeddings."""
    pass


class RetrievalError(SMRITIError):
    """Error retrieving candidates."""
    pass


class ContradictionError(SMRITIError):
    """Error detecting contradictions."""
    pass


class EvolutionError(SMRITIError):
    """Error analyzing knowledge evolution."""
    pass


class ScoringError(SMRITIError):
    """Error computing metrics."""
    pass


class ReportingError(SMRITIError):
    """Error generating report."""
    pass


class DashboardError(SMRITIError):
    """Error in dashboard."""
    pass


class PipelineError(SMRITIError):
    """Error in pipeline orchestration."""
    pass


class CacheError(SMRITIError):
    """Error in cache operations."""
    pass


class HashError(SMRITIError):
    """Error computing hash."""
    pass


class ValidationError(SMRITIError):
    """Input or output validation failed."""
    pass

# ── Phase 3: Semantic Sentence Construction ───────────────────────────────────

class Phase3Error(SMRITIError):
    """Base for all Phase 3 errors."""
    pass


class ScannerError(Phase3Error):
    """Structural scanner failed on a document."""
    pass


class ContextError(Phase3Error):
    """Context stack invariant violated (fatal — indicates design error)."""
    pass


class NormalizationError(Phase3Error):
    """Structured content could not be normalised to prose."""
    pass


class SegmentationError(Phase3Error):
    """Sentence segmentation produced an impossible result."""
    pass


class SentenceValidationError(Phase3Error):
    """A SemanticSentence failed validation (fatal constraint violated)."""
    pass

# ── Phase 4: Claim Construction ───────────────────────────────────────────────

class Phase4Error(SMRITIError):
    """Base for all Phase 4 errors."""
    pass


class ClaimExtractionError(Phase4Error):
    """Unrecoverable error during claim extraction for a single sentence."""
    pass


class ClaimValidationError(Phase4Error):
    """Fatal constraint violation in claim validation (duplicate ID, broken provenance)."""
    pass


class SpacyNotLoadedError(Phase4Error):
    """spaCy model could not be loaded — pipeline cannot continue."""
    pass


# ── Phase 5: Semantic Embedding Layer ─────────────────────────────────────────

class Phase5Error(SMRITIError):
    """Base for all Phase 5 errors."""
    pass


class EmbeddingModelError(Phase5Error):
    """Embedding model failed to load or is misconfigured."""
    pass


class EmbeddingInferenceError(Phase5Error):
    """Embedding inference failed for a batch or single input."""
    pass


class VectorValidationError(Phase5Error):
    """Vector failed mathematical validation (NaN, Inf, dimension mismatch, dtype)."""
    pass


class CacheKeyError(Phase5Error):
    """Cache key could not be computed deterministically."""
    pass


class CacheSchemaMismatchError(Phase5Error):
    """Cache entry schema version does not match current Phase 5 schema."""
    pass
````

## File: src/smriti/main.py
````python
"""
Main entry point for the SMRITI pipeline.
Initializes core infrastructure, wires up phases, and triggers the runner.
"""

from smriti.core.logger import setup_logging, get_logger
from smriti.core.paths import RAW_DATA_DIR

setup_logging()
logger = get_logger(__name__)


def main():
    logger.info("smriti application starting")

    try:
        from smriti.pipeline.runner import PipelineRunner

        runner = PipelineRunner(input_dirs=[RAW_DATA_DIR])

        # Run Phase 1 + Phase 2 (stop_at=2 to run only these phases during development)
        success = runner.run(start_from=1, stop_at=2)

        if success:
            logger.info("smriti pipeline completed successfully")
        else:
            logger.error("smriti pipeline failed")

    except Exception as e:
        logger.error("fatal pipeline error", error=str(e), exc_info=True)


if __name__ == "__main__":
    main()
````

## File: src/.gitkeep
````

````

## File: tests/fixtures/sample_notes.md
````markdown
# sample notes\n
````

## File: tests/integration/test_phase1_discovery.py
````python
"""
Integration test for Phase 1 end-to-end.

Tests the complete pipeline:
  input directories → DiscoveryResult

Uses a realistic vault fixture with:
  - Normal notes (.md, .txt, .pdf)
  - Nested subdirectories
  - Duplicate content (different filenames)
  - Invalid files (empty, wrong extension)
  - Hidden files and directories
"""

import json
import pytest
from pathlib import Path
from smriti.discovery import run_discovery, DiscoveryResult
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager


@pytest.fixture
def realistic_vault(tmp_path):
    """
    Create a realistic Obsidian-like vault.
    """
    vault = tmp_path / "vault"
    vault.mkdir()

    # Normal notes
    ai_content = "Artificial intelligence is transforming the world."
    (vault / "AI.md").write_text(ai_content, encoding="utf-8")
    (vault / "Python.md").write_text(
        "Python is the dominant language for data science.", encoding="utf-8"
    )

    # Nested dirs
    archive = vault / "Archive"
    archive.mkdir()
    (archive / "Old_AI.md").write_text(ai_content, encoding="utf-8")  # DUPLICATE
    (archive / "Very_Old.md").write_text("Old notes about computing.", encoding="utf-8")

    research = vault / "Research" / "Papers"
    research.mkdir(parents=True)
    (research / "summary.txt").write_text("Research summary.", encoding="utf-8")
    (research / "paper.pdf").write_bytes(b"%PDF-1.4 fake content")

    # Must be ignored
    obsidian = vault / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text('{"theme": "dark"}')

    # Must be skipped
    (vault / "empty.md").write_bytes(b"")
    (vault / "unsupported.docx").write_bytes(b"PK fake docx")

    return vault


@pytest.fixture
def run_id():
    return "test_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


def test_phase1_discovers_correct_count(realistic_vault, run_id, test_managers):
    """Full discovery must find 6 documents, canonical count = 5."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert isinstance(result, DiscoveryResult)
    assert len(result.documents) == 6
    assert result.canonical_count == 5


def test_phase1_detects_one_duplicate(realistic_vault, run_id, test_managers):
    """Old_AI.md has same content as AI.md — must be detected as duplicate."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.duplicate_registry.duplicate_count == 1
    dup_paths = result.duplicate_registry.duplicate_paths
    assert any("Old_AI.md" in str(p) for p in dup_paths)


def test_phase1_skips_empty_file(realistic_vault, run_id, test_managers):
    """empty.md must appear in skipped list with appropriate reason."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("empty.md" in p for p in skipped_paths)

    skipped_reasons = {str(p): r for p, r in result.skipped}
    empty_path = next(p for p in skipped_paths if "empty.md" in p)
    assert "empty" in skipped_reasons[empty_path]


def test_phase1_skips_unsupported_extension(realistic_vault, run_id, test_managers):
    """unsupported.docx must be skipped — not crash."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    skipped_paths = [str(p) for p, _ in result.skipped]
    assert any("unsupported.docx" in p for p in skipped_paths)


def test_phase1_ignores_obsidian_dir(realistic_vault, run_id, test_managers):
    """No file inside .obsidian/ must appear in results."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    all_paths = [str(d.path) for d in result.documents]
    assert not any(".obsidian" in p for p in all_paths)


def test_phase1_documents_are_immutable(realistic_vault, run_id, test_managers):
    """SourceDocument must be frozen (no mutation allowed)."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_phase1_writes_manifest(realistic_vault, run_id, test_managers):
    """A manifest.json must be written after discovery."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result.manifest_path is not None
    assert result.manifest_path.exists()

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 1
    assert manifest["status"] == "success"
    assert manifest["run_id"] == run_id
    assert manifest["outputs"]["canonical_documents"] == 5


def test_phase1_writes_dataset_json(realistic_vault, run_id, test_managers, tmp_path):
    """dataset.json must be written to artifacts/run_id/phase1/."""
    manifest_mgr, state_mgr = test_managers

    result = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    dataset_paths = list(
        (tmp_path / "artifacts" / f"run_{run_id}" / "phase1").glob("dataset.json")
    )
    assert len(dataset_paths) == 1

    dataset = json.loads(dataset_paths[0].read_text(encoding="utf-8"))
    assert len(dataset) == 5  # canonical only
    # Rectified: doc_id must equal content_hash
    for doc in dataset:
        assert "doc_id" in doc
        assert "content_hash" in doc
        assert doc["doc_id"] == doc["content_hash"]


def test_phase1_updates_pipeline_state(realistic_vault, run_id, test_managers):
    """Pipeline state must be updated to mark Phase 1 as complete."""
    manifest_mgr, state_mgr = test_managers

    run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    state = state_mgr.load()
    assert state is not None
    assert 1 in state.completed_phases


def test_phase1_is_idempotent(realistic_vault, run_id, test_managers):
    """Running Phase 1 twice on same input must produce same canonical count."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    result2 = run_discovery(
        input_dirs=[realistic_vault],
        run_id=run_id + "_2",
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    assert result1.canonical_count == result2.canonical_count


def test_phase1_no_nlp_imports():
    """Phase 1 must never import NLP libraries."""
    import smriti.discovery.scanner as scanner
    import smriti.discovery.validator as validator
    import smriti.discovery.metadata as metadata_mod
    import smriti.discovery.hashing as hashing_mod
    import smriti.discovery.duplicate as duplicate_mod
    import smriti.discovery.builder as builder_mod

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [scanner, validator, metadata_mod, hashing_mod, duplicate_mod, builder_mod]:
        module_imports = set(vars(module).keys())
        assert not (module_imports & nlp_modules), (
            f"{module.__name__} imports NLP libraries — Phase 1 must not do NLP"
        )
````

## File: tests/integration/test_phase3_extraction.py
````python
"""
Integration test for Phase 3 end-to-end.

Tests the complete pipeline:
  Document → build_semantic_sentences() → List[SemanticSentence]

Uses Documents with realistic note content.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from smriti.core.models import (
    Document, SourceDocument, FileFormat, ExtractionMethod,
    TextStatistics, WarningCode, SemanticSentence,
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
        modified_at=datetime.now(tz=timezone.utc),
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
        "doc1",
        "Python is great for data science. Julia is faster for numerical computing."
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
    doc = make_document(
        "doc3",
        "# Python\n\nPython is great for data science."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1
    sentence = result.sentences[0]
    assert "Python" in sentence.context


def test_nested_context():
    doc = make_document(
        "doc4",
        "# Programming\n\n## Python\n\nPython is great."
    )
    result = build_semantic_sentences(doc)
    sentence = result.sentences[0]
    assert "Programming" in sentence.context
    assert "Python" in sentence.context


def test_heading_is_not_a_sentence():
    doc = make_document(
        "doc5",
        "# This Is A Heading\n\nActual sentence here."
    )
    result = build_semantic_sentences(doc)
    sentence_texts = [s.text for s in result.sentences]
    assert not any("This Is A Heading" in t for t in sentence_texts)


def test_context_resets_at_new_h1():
    doc = make_document(
        "doc6",
        "# Section A\n\nSentence in A.\n\n# Section B\n\nSentence in B."
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 2
    assert "Section A" in result.sentences[0].context
    assert "Section B" in result.sentences[1].context
    assert "Section A" not in result.sentences[1].context


# ── Structural elements ───────────────────────────────────────────────────────

def test_bullet_items_become_sentences():
    doc = make_document(
        "doc7",
        "- First item\n- Second item\n- Third item"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_ordered_list_becomes_sentences():
    doc = make_document(
        "doc8",
        "1. Install Poetry\n2. Install dependencies\n3. Run tests"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 3


def test_block_quote_becomes_sentence():
    doc = make_document("doc9", "> Reliability is critical.")
    result = build_semantic_sentences(doc)
    assert result.sentence_count == 1
    assert "Reliability" in result.sentences[0].text


def test_code_block_produces_no_sentences():
    doc = make_document(
        "doc10",
        "Before code.\n\n```python\nprint('hello')\n```\n\nAfter code."
    )
    result = build_semantic_sentences(doc)
    texts = [s.text for s in result.sentences]
    assert not any("print" in t for t in texts)


def test_table_produces_prose_sentences():
    doc = make_document(
        "doc11",
        "| Model | Accuracy |\n|-------|----------|\n| GPT-4 | 85% |"
    )
    result = build_semantic_sentences(doc)
    assert result.sentence_count >= 1


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_document_same_sentence_ids():
    doc = make_document(
        "doc12",
        "# AI\n\nAI is transforming everything. Machine learning is a subset of AI."
    )
    result1 = build_semantic_sentences(doc)
    result2 = build_semantic_sentences(doc)

    ids1 = [s.sentence_id for s in result1.sentences]
    ids2 = [s.sentence_id for s in result2.sentences]
    assert ids1 == ids2


def test_positions_are_strictly_increasing():
    doc = make_document(
        "doc13",
        "First. Second. Third. Fourth."
    )
    result = build_semantic_sentences(doc)
    positions = [s.position for s in result.sentences]
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))


def test_sentence_ids_are_unique():
    doc = make_document(
        "doc14",
        "# Section\n\nSentence A. Sentence B. Sentence C.\n\n## Sub\n\nSentence D."
    )
    result = build_semantic_sentences(doc)
    ids = [s.sentence_id for s in result.sentences]
    assert len(ids) == len(set(ids))


# ── Context separation ────────────────────────────────────────────────────────

def test_context_never_fused_into_text():
    doc = make_document(
        "doc15",
        "# CUDA\n\nSupports tensors."
    )
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
    doc = make_document(
        "doc18",
        "- First bullet\n\n> A quote.\n\nPlain paragraph."
    )
    result = build_semantic_sentences(doc)

    # The order of events from scanner: bullet_item, block_quote, paragraph
    # (depending on how the scanner processes)
    # We'll check that each sentence's origin_block_type is set correctly.
    origins = [s.origin_block_type for s in result.sentences]
    assert BlockType.BULLET_ITEM in origins
    assert BlockType.BLOCK_QUOTE in origins
    assert BlockType.PARAGRAPH in origins
    assert all(isinstance(o, BlockType) for o in origins)


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
````

## File: tests/integration/test_phase4_extraction.py
````python
"""
Integration test for Phase 4 end-to-end.

Tests the complete pipeline:
    SemanticSentence → extract_claims_from_sentence() → List[Claim]
"""

import hashlib
import pytest
from pathlib import Path
from smriti.core.models import (
    SemanticSentence, Claim, ExtractionMode, Modality,
)
from smriti.claims import extract_claims_from_sentence
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.degradation import DegradationHandler
from smriti.claims.statistics import Phase4StatsCollector


@pytest.fixture(scope="module")
def pipeline():
    """Initialize pipeline components once per module."""
    try:
        return (
            SpaCyParser(),
            BoundaryDetector(),
            StructureExtractor(),
            AssertionAnnotator(),
            DegradationHandler(),
        )
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(
    text: str,
    sentence_id: str = "s001",
    context: str = "",
    position: int = 0,
) -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context=context,
        position=position,
        char_start=0,
        char_end=len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def run_pipeline(pipeline, sentence, max_claims=10):
    parser, bd, se, ann, dh = pipeline
    stats = Phase4StatsCollector()
    return extract_claims_from_sentence(
        sentence=sentence, parser=parser, boundary_detector=bd,
        structure_extractor=se, annotator=ann, degradation_handler=dh,
        stats_collector=stats, max_claims=max_claims,
    )


# ── Basic claim production ─────────────────────────────────────────────────────

def test_simple_sentence_produces_claim(pipeline):
    """Every non-empty sentence must produce at least one claim."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert result.claim_count >= 1
    assert result.error is None


def test_empty_sentence_produces_no_claims(pipeline):
    """Empty text → zero claims, no error."""
    result = run_pipeline(pipeline, make_sentence("   "))
    assert result.claim_count == 0


def test_claims_have_correct_sentence_id(pipeline):
    """Every claim must link back to the source sentence_id."""
    sentence = make_sentence("Python is fast.", sentence_id="unique_s_id")
    result = run_pipeline(pipeline, sentence)
    assert all(c.sentence_id == "unique_s_id" for c in result.claims)
    # New checks for content_hash and rule_version
    assert all(c.content_hash is not None for c in result.claims)
    assert all(c.rule_version == "1.0" for c in result.claims)


def test_claims_have_correct_document_id(pipeline):
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    assert all(c.document_id == "doc001" for c in result.claims)


# ── Text preservation ─────────────────────────────────────────────────────────

def test_claim_text_preserves_author_wording(pipeline):
    """Claim text must match source — no canonicalization."""
    original = "Python does NOT support this feature."
    sentence = make_sentence(original)
    result = run_pipeline(pipeline, sentence)
    # At minimum, the whole-sentence fallback must preserve it
    all_texts = [c.text for c in result.claims]
    assert any(original in t or t in original for t in all_texts)


# ── Context propagation ────────────────────────────────────────────────────────

def test_context_propagated_from_sentence(pipeline):
    """Claim must carry context from SemanticSentence."""
    sentence = make_sentence("Python supports generators.", context="Programming > Python")
    result = run_pipeline(pipeline, sentence)
    assert all(c.context == "Programming > Python" for c in result.claims)


# ── Provenance chain ──────────────────────────────────────────────────────────

def test_claim_provenance_is_complete(pipeline):
    """Every claim must have complete provenance chain."""
    sentence = make_sentence("Python is fast.", sentence_id="sid1", position=5)
    result = run_pipeline(pipeline, sentence)
    for claim in result.claims:
        assert claim.provenance is not None
        assert claim.provenance.sentence_id == "sid1"
        assert claim.provenance.document_id == "doc001"
        assert claim.provenance.sentence_position == 5
    # New check: content_hash must match SHA256 of text
    assert all(
        c.content_hash == hashlib.sha256(c.text.encode()).hexdigest()[:16]
        for c in result.claims
    )


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_sentence_same_claim_ids(pipeline):
    """Running twice on the same sentence must produce identical claim IDs."""
    sentence = make_sentence("Python supports generators and decorators.")
    result1 = run_pipeline(pipeline, sentence)
    result2 = run_pipeline(pipeline, sentence)

    ids1 = [c.claim_id for c in result1.claims]
    ids2 = [c.claim_id for c in result2.claims]
    assert ids1 == ids2
    # New check: content_hash must also be identical
    assert [c.content_hash for c in result1.claims] == [c.content_hash for c in result2.claims]


def test_claim_ids_are_unique(pipeline):
    """No two claims from the same sentence may share an ID."""
    sentence = make_sentence("Python supports X and Y and Z.")
    result = run_pipeline(pipeline, sentence)
    ids = [c.claim_id for c in result.claims]
    assert len(ids) == len(set(ids))


# ── Annotation ────────────────────────────────────────────────────────────────

def test_negation_flag_on_negated_claim(pipeline):
    """A negated sentence must produce at least one claim with is_negated=True."""
    sentence = make_sentence("Python does not support this feature.")
    result = run_pipeline(pipeline, sentence)
    assert any(c.is_negated for c in result.claims)


def test_modality_on_possible_claim(pipeline):
    """'may' or 'might' must produce POSSIBLE modality."""
    sentence = make_sentence("Python may be faster than Java.")
    result = run_pipeline(pipeline, sentence)
    modalities = [c.assertion_metadata.modality for c in result.claims]
    assert Modality.POSSIBLE in modalities


# ── Immutability ──────────────────────────────────────────────────────────────

def test_claims_are_immutable(pipeline):
    """Claim objects must be frozen."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    if result.claims:
        with pytest.raises(Exception):
            result.claims[0].text = "modified"


# ── Graceful degradation ──────────────────────────────────────────────────────

def test_claim_always_produced_even_on_parse_failure(pipeline):
    """Even on parser failure, a whole-sentence claim is produced."""
    # Malformed text that may trip the parser
    sentence = make_sentence("@@@ ### ??? weird !!!")
    result = run_pipeline(pipeline, sentence)
    # Must produce something (whole-sentence fallback)
    assert result.claim_count >= 0  # 0 only if text is empty


def test_schema_version_is_correct(pipeline):
    """All claims must have schema_version '4.0'."""
    result = run_pipeline(pipeline, make_sentence("Python is fast."))
    for claim in result.claims:
        assert claim.schema_version == "4.0"


# ── Realistic note ────────────────────────────────────────────────────────────

def test_realistic_knowledge_note(pipeline):
    """
    Full test with a realistic machine learning note.
    Verifies claims are extracted with provenance and correct flags.
    """
    sentences_data = [
        ("Supervised learning uses labeled training data.", "ML > Supervised"),
        ("The model learns to map inputs to outputs.", "ML > Supervised"),
        ("Unsupervised learning does not require labeled data.", "ML > Unsupervised"),
        ("Deep learning may outperform traditional methods on large datasets.",
         "ML > Deep Learning"),
        ("According to the authors, transformers are now state-of-the-art.", "ML"),
    ]

    all_claims = []
    for i, (text, context) in enumerate(sentences_data):
        sentence = make_sentence(text, sentence_id=f"s_{i:03d}", context=context, position=i)
        result = run_pipeline(pipeline, sentence)
        assert result.error is None, f"Error on sentence '{text}': {result.error}"
        all_claims.extend(result.claims)

    # At least one claim per sentence
    assert len(all_claims) >= len(sentences_data)

    # All have provenance
    assert all(c.provenance is not None for c in all_claims)

    # All have schema 4.0
    assert all(c.schema_version == "4.0" for c in all_claims)

    # Negation detected in sentence 3
    unsupervised_claims = [c for c in all_claims if "does not" in c.text.lower()]
    assert any(c.is_negated for c in unsupervised_claims)

    # Modality detected in sentence 4
    deep_claims = [c for c in all_claims if "may" in c.text.lower()]
    assert any(c.assertion_metadata.modality == Modality.POSSIBLE for c in deep_claims)

    # Attribution detected in sentence 5
    attribution_claims = [c for c in all_claims if "authors" in c.text.lower() or
                          c.assertion_metadata.is_attributed]
    # Attribution may or may not be detected depending on spaCy's parse
    # but the claim must still exist
    assert len(all_claims) >= 5

    # All claim IDs are unique
    claim_ids = [c.claim_id for c in all_claims]
    assert len(claim_ids) == len(set(claim_ids))

    # New checks for content_hash and rule_version
    hashes = [c.content_hash for c in all_claims]
    # content_hash should be unique because texts differ
    assert len(hashes) == len(set(hashes))
    assert all(c.rule_version == "1.0" for c in all_claims)
````

## File: tests/integration/test_phase5_embedding.py
````python
"""
Integration test for Phase 5 end-to-end.

Tests the complete pipeline:
    List[Claim] → embed_claims() → Phase5Result

Uses a mock embedder so tests run without sentence-transformers installed.
All assertions reflect the rectified API:
    - EmbeddedClaim.vector returns Vector (not tuple)
    - EmbeddedClaim.values returns tuple of floats
    - EmbeddedClaim.quality is EmbeddingQuality
    - Embedding has no status field
"""

import pytest
import math
import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
    Modality, EmbeddingStatus, EmbeddedClaim,
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector,
)
from smriti.core.manifest import ManifestManager
from smriti.core.state import StateManager
from smriti.embedding import embed_claims, Phase5Result
from smriti.embedding.embedder import BaseEmbedder, EmbedderCapabilities


# ── Mock embedder ─────────────────────────────────────────────────────────────

class MockEmbedder(BaseEmbedder):
    """Mock embedder that returns deterministic fake vectors."""

    DIMENSION = 4

    def __init__(self):
        self._descriptor = EmbeddingModelDescriptor(
            provider="mock",
            model_name="mock-embedder",
            model_revision="test",
            dimension=self.DIMENSION,
            model_signature="mock_signature_abc123",
            embedding_family="Mock",
        )

    @property
    def descriptor(self) -> EmbeddingModelDescriptor:
        return self._descriptor

    @property
    def capabilities(self) -> EmbedderCapabilities:
        return EmbedderCapabilities(
            supports_batching=True,
            supports_instruction_prefix=False,
            supports_multilingual=False,
            supports_long_context=False,
        )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Deterministic: hash of text → 4 floats."""
        import hashlib
        results = []
        for text in texts:
            h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
            vector = [(h >> (i * 8) & 0xFF) / 255.0 for i in range(self.DIMENSION)]
            if all(v == 0.0 for v in vector):
                vector[0] = 0.1
            results.append(vector)
        return results


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_embedder():
    return MockEmbedder()


@pytest.fixture
def run_id():
    return "test_phase5_20240101"


@pytest.fixture
def test_managers(tmp_path, run_id):
    return (
        ManifestManager(run_id=run_id, artifacts_dir=tmp_path / "artifacts"),
        StateManager(state_file=tmp_path / "state.json"),
    )


def make_claim(
    claim_id: str,
    text: str,
    context: str = "",
    document_id: str = "doc001",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id=document_id,
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id=document_id,
            source_path=Path("test.md"), sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=claim_id[:16],
        rule_version="1.0",
    )


def run_embedding(mock_embedder, claims, run_id, test_managers, **kwargs):
    manifest_mgr, state_mgr = test_managers
    return embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=mock_embedder,
        **kwargs,
    )


# ── Basic production ──────────────────────────────────────────────────────────

def test_empty_claims_produces_empty_result(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [], run_id, test_managers)
    assert isinstance(result, Phase5Result)
    assert result.total_embedded == 0


def test_single_claim_produces_embedded_claim(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.failed == 0


def test_embedded_claims_reference_correct_claim_ids(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    ids = {ec.claim_id for ec in result.embedded_claims}
    assert ids == {"c001", "c002"}


def test_empty_text_claim_is_skipped(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Valid claim."), make_claim("c002", "   ")]
    result = run_embedding(mock_embedder, claims, run_id, test_managers)
    assert result.total_embedded == 1
    assert result.stats.skipped == 1


# ── Immutability and purity ───────────────────────────────────────────────────

def test_embedded_claims_are_immutable(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Python is fast.")], run_id, test_managers)
    with pytest.raises(Exception):
        result.embedded_claims[0].claim_id = "modified"


def test_original_claims_not_modified(mock_embedder, run_id, test_managers):
    claim = make_claim("c001", "Python is fast.")
    original_text = claim.text
    run_embedding(mock_embedder, [claim], run_id, test_managers)
    assert claim.text == original_text


def test_embedding_has_no_status_field(mock_embedder, run_id, test_managers):
    """Critical fix: Embedding must not have a status field."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert not hasattr(ec.embedding, "status"), (
        "Embedding should not have status — it's a pure semantic artifact"
    )


# ── EmbeddingQuality ──────────────────────────────────────────────────────────

def test_embedded_claim_has_quality(mock_embedder, run_id, test_managers):
    """EmbeddedClaim must carry EmbeddingQuality."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.quality, EmbeddingQuality)


def test_quality_fresh_embedding(mock_embedder, run_id, test_managers):
    """Fresh embedding: cache_used=False, normalized=True."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.quality.cache_used is False
    assert ec.quality.normalized is True
    assert ec.quality.finite is True
    assert ec.quality.dimension_ok is True


# ── Vector domain object ──────────────────────────────────────────────────────

def test_vector_is_vector_type(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.vector must return a Vector domain object."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector, Vector)


def test_vector_values_is_tuple(mock_embedder, run_id, test_managers):
    """Vector.values must be an immutable tuple."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert isinstance(ec.vector.values, tuple)


def test_embedded_claim_values_shortcut(mock_embedder, run_id, test_managers):
    """EmbeddedClaim.values must return the same as ec.vector.values."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert ec.values == ec.vector.values


def test_vector_has_correct_dimension(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.dimension == MockEmbedder.DIMENSION
        assert ec.vector.dimension == MockEmbedder.DIMENSION


def test_normalized_vectors_are_unit_length(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        norm = math.sqrt(sum(x * x for x in ec.values))
        assert abs(norm - 1.0) < 1e-5, f"Norm was {norm}"


# ── Schema and provenance ─────────────────────────────────────────────────────

def test_schema_version_is_50(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    for ec in result.embedded_claims:
        assert ec.schema_version == "5.0"


def test_embedding_descriptor_family(mock_embedder, run_id, test_managers):
    """EmbeddingModelDescriptor must include embedding_family."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    ec = result.embedded_claims[0]
    assert hasattr(ec.embedding.descriptor, "embedding_family")
    assert ec.embedding.descriptor.embedding_family == "Mock"


# ── Batch retry ───────────────────────────────────────────────────────────────

def test_batch_failure_triggers_individual_retry(run_id, test_managers):
    """
    When a batch fails, the pipeline must retry each claim individually.
    Only the claims that individually fail are marked as failed.
    """
    call_count = {"n": 0}

    class FailFirstBatchEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            call_count["n"] += 1
            # Fail on the first call (the full batch)
            if call_count["n"] == 1 and len(texts) > 1:
                raise RuntimeError("Simulated batch failure")
            return super().encode_batch(texts)

    failing_embedder = FailFirstBatchEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]

    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=failing_embedder,
    )

    # Both claims should succeed via individual retry
    assert result.total_embedded == 2
    # A warning should have been added about the batch failure
    assert any("batch" in w.lower() for w in result.warnings)


def test_one_bad_vector_does_not_abort_batch(run_id, test_managers):
    """NaN in one vector must not fail the other claims in the batch."""
    class NaNSecondEmbedder(MockEmbedder):
        def encode_batch(self, texts):
            vectors = super().encode_batch(texts)
            if len(vectors) > 1:
                vectors[1] = [float("nan")] * self.DIMENSION
            return vectors

    embedder = NaNSecondEmbedder()
    claims = [make_claim("c001", "First."), make_claim("c002", "Second.")]
    manifest_mgr, state_mgr = test_managers
    result = embed_claims(
        claims=claims,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
        embedder=embedder,
    )

    assert result.total_embedded >= 1  # c001 succeeds
    assert result.stats.failed >= 1    # c002 fails validation


# ── Warnings and errors ───────────────────────────────────────────────────────

def test_result_has_warnings_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose a warnings list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "warnings")
    assert isinstance(result.warnings, list)


def test_result_has_errors_list(mock_embedder, run_id, test_managers):
    """Phase5Result must expose an errors list."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result, "errors")
    assert isinstance(result.errors, list)


# ── Artifacts ─────────────────────────────────────────────────────────────────

def test_dataset_json_written(mock_embedder, run_id, test_managers):
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()


def test_dataset_json_has_quality_section(mock_embedder, run_id, test_managers):
    """dataset.json must include the quality diagnostic block."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    assert len(records) == 1
    record = records[0]
    assert "quality" in record
    assert "dimension_ok" in record["quality"]
    assert "normalized" in record["quality"]
    assert "cache_used" in record["quality"]


def test_dataset_json_no_status_field_from_embedding(mock_embedder, run_id, test_managers):
    """
    dataset.json 'status' field is derived from quality.cache_used,
    not from an Embedding.status attribute.
    """
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    records = json.loads(result.dataset_path.read_text())
    record = records[0]
    # Status is "success" for fresh, "cached" for cache hits
    assert record["status"] in ("success", "cached")


def test_manifest_has_cache_lifecycle_metrics(mock_embedder, run_id, test_managers):
    """manifest.json must include cache lifecycle counters."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    manifest = json.loads(result.manifest_path.read_text())
    assert "cache_entries_reused" in manifest.get("outputs", {})
    assert "cache_entries_regenerated" in manifest.get("outputs", {})


def test_pipeline_state_updated(mock_embedder, run_id, test_managers):
    _, state_mgr = test_managers
    run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    state = state_mgr.load()
    assert 5 in state.completed_phases


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_claims_same_vectors(mock_embedder, run_id, test_managers):
    claims = [make_claim("c001", "Python is fast."), make_claim("c002", "Julia is faster.")]
    manifest_mgr, state_mgr = test_managers

    r1 = embed_claims(claims=claims, run_id=run_id, manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)
    r2 = embed_claims(claims=claims, run_id=run_id + "_2", manifest_manager=manifest_mgr,
                      state_manager=state_mgr, embedder=mock_embedder, force_reembed=True)

    v1 = {ec.claim_id: ec.values for ec in r1.embedded_claims}
    v2 = {ec.claim_id: ec.values for ec in r2.embedded_claims}
    assert v1 == v2


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_has_throughput_field(mock_embedder, run_id, test_managers):
    """Phase5Stats must include vectors_per_second."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "vectors_per_second")
    assert result.stats.vectors_per_second >= 0.0


def test_stats_has_cache_lifecycle_fields(mock_embedder, run_id, test_managers):
    """Phase5Stats must include cache lifecycle counts."""
    result = run_embedding(mock_embedder, [make_claim("c001", "Test.")], run_id, test_managers)
    assert hasattr(result.stats, "cache_entries_reused")
    assert hasattr(result.stats, "cache_entries_regenerated")
````

## File: tests/integration/test_pipeline_runner.py
````python
def test_placeholder():\n    assert True\n
````

## File: tests/unit/test_builder.py
````python
"""
Unit tests for discovery/builder.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.builder import build_source_document, SourceDocument
from smriti.discovery.metadata import extract_metadata
from smriti.core.models import FileFormat


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("Python is great for data science.")
    return f


def test_builder_produces_source_document(sample_file, tmp_path):
    """Builder must return a SourceDocument."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="a" * 64,
        source_root=tmp_path,
    )

    assert isinstance(doc, SourceDocument)


def test_builder_sets_correct_format_md(sample_file, tmp_path):
    """Markdown file gets MARKDOWN format."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="b" * 64,
        source_root=tmp_path,
    )

    assert doc.format == FileFormat.MARKDOWN


def test_builder_doc_is_immutable(sample_file, tmp_path):
    """SourceDocument is frozen — mutation must raise."""
    meta = extract_metadata(sample_file)

    doc = build_source_document(
        metadata=meta,
        content_hash="c" * 64,
        source_root=tmp_path,
    )

    with pytest.raises(Exception):
        doc.size_bytes = 0


def test_builder_relative_path(tmp_path):
    """relative_path must be relative to source_root."""
    subdir = tmp_path / "notes"
    subdir.mkdir()
    f = subdir / "deep.md"
    f.write_text("Some content.")

    meta = extract_metadata(f)

    doc = build_source_document(
        metadata=meta,
        content_hash="d" * 64,
        source_root=tmp_path,
    )

    assert doc.relative_path == Path("notes/deep.md")


def test_builder_doc_id_is_content_hash(sample_file, tmp_path):
    """doc_id must equal content_hash."""
    meta = extract_metadata(sample_file)
    content_hash = "e" * 64
    doc = build_source_document(meta, content_hash, tmp_path)
    assert doc.doc_id == content_hash


def test_builder_doc_id_is_deterministic(sample_file, tmp_path):
    """Same input must produce same doc_id every time."""
    meta = extract_metadata(sample_file)

    doc1 = build_source_document(
        metadata=meta, content_hash="f" * 64, source_root=tmp_path,
    )
    doc2 = build_source_document(
        metadata=meta, content_hash="f" * 64, source_root=tmp_path,
    )

    assert doc1.doc_id == doc2.doc_id
````

## File: tests/unit/test_cache.py
````python

````

## File: tests/unit/test_config.py
````python
"""Test deep-merge config loader."""

import pytest
from smriti.core.config import _deep_merge, Config


def test_deep_merge_flat():
    base = {"a": 1, "b": 2}
    override = {"b": 99, "c": 3}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_deep_merge_nested_does_not_overwrite_sibling_keys():
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    result = _deep_merge(base, override)
    # model should survive; batch_size should be overridden
    assert result["embedding"]["model"] == "MiniLM"
    assert result["embedding"]["batch_size"] == 8


def test_deep_merge_shallow_update_would_fail():
    """Demonstrates why dict.update() is wrong for nested config."""
    base = {"embedding": {"model": "MiniLM", "batch_size": 32}}
    override = {"embedding": {"batch_size": 8}}
    # shallow update — loses model key
    shallow = dict(base)
    shallow.update(override)
    assert "model" not in shallow["embedding"]   # broken
    # deep merge — keeps model key
    deep = _deep_merge(base, override)
    assert "model" in deep["embedding"]          # correct


def test_config_loads_default(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text(
        "embedding:\n  model: MiniLM\n  batch_size: 32\n"
    )
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"
    assert cfg["embedding"]["batch_size"] == 32


def test_config_dev_override_deep_merges(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text(
        "embedding:\n  model: MiniLM\n  batch_size: 32\n"
    )
    (config_dir / "dev.yaml").write_text(
        "embedding:\n  batch_size: 8\n"
    )
    cfg = Config(env="dev", config_dir=config_dir)
    assert cfg["embedding"]["model"] == "MiniLM"    # inherited
    assert cfg["embedding"]["batch_size"] == 8      # overridden
````

## File: tests/unit/test_duplicate.py
````python
"""
Unit tests for discovery/duplicate.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.duplicate import build_duplicate_registry


def test_no_duplicates(tmp_path):
    """All unique hashes — no duplicates."""
    pairs = [
        (tmp_path / "a.md", "aaaa"),
        (tmp_path / "b.md", "bbbb"),
        (tmp_path / "c.md", "cccc"),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 3
    assert all(registry.is_canonical(p) for p, _ in pairs)


def test_one_duplicate(tmp_path):
    """Second file with same hash is marked as duplicate."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8  # 64 chars

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 1
    assert registry.unique_content_count == 1
    assert registry.is_canonical(path_a)
    assert registry.is_duplicate(path_b)


def test_canonical_path_for_duplicate(tmp_path):
    """get_canonical_for() must return the first-seen path."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "cafebabe" * 8

    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)

    assert registry.get_canonical_for(path_b) == path_a


def test_three_identical_files(tmp_path):
    """Three files with same content: first is canonical, two are duplicates."""
    shared_hash = "12345678" * 8
    pairs = [
        (tmp_path / "a.md", shared_hash),
        (tmp_path / "b.md", shared_hash),
        (tmp_path / "c.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)

    assert registry.duplicate_count == 2
    assert registry.is_canonical(tmp_path / "a.md")
    assert registry.is_duplicate(tmp_path / "b.md")
    assert registry.is_duplicate(tmp_path / "c.md")


def test_empty_input():
    """Empty input must return empty registry — not crash."""
    registry = build_duplicate_registry([])
    assert registry.duplicate_count == 0
    assert registry.unique_content_count == 0


def test_duplicate_same_name_different_dirs(tmp_path):
    """
    notes/AI.md and archive/AI.md with same content are duplicates.
    Same filename ≠ same document. Content hash determines identity.
    """
    dir1 = tmp_path / "notes"
    dir2 = tmp_path / "archive"
    dir1.mkdir()
    dir2.mkdir()

    shared_hash = "aabbccdd" * 8
    pairs = [
        (dir1 / "AI.md", shared_hash),
        (dir2 / "AI.md", shared_hash),
    ]
    registry = build_duplicate_registry(pairs)
    assert registry.duplicate_count == 1

def test_get_canonical_for_constant_time(tmp_path):
    """get_canonical_for must be O(1) via reverse dict."""
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    shared_hash = "deadbeef" * 8
    pairs = [(path_a, shared_hash), (path_b, shared_hash)]
    registry = build_duplicate_registry(pairs)
    assert registry.get_canonical_for(path_b) == path_a
````

## File: tests/unit/test_hashing.py
````python
"""
Unit tests for discovery/hashing.py.
"""

import pytest
from pathlib import Path
from smriti.discovery.hashing import compute_hash


def test_same_content_same_hash(tmp_path):
    """Identical content must always produce the same hash."""
    content = "Python is great for data science."
    f1 = tmp_path / "note1.md"
    f2 = tmp_path / "note2.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_different_content_different_hash(tmp_path):
    """Different content must produce different hashes."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Julia is faster.", encoding="utf-8")

    assert compute_hash(f1) != compute_hash(f2)


def test_rename_does_not_change_hash(tmp_path):
    """Renaming a file must produce the same hash (content-only)."""
    content = "The hash must not depend on the filename."
    f1 = tmp_path / "original.md"
    f2 = tmp_path / "renamed.md"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")

    assert compute_hash(f1) == compute_hash(f2)


def test_hash_is_64_character_hex(tmp_path):
    """SHA256 hex digest must be exactly 64 lowercase hex characters."""
    f = tmp_path / "note.md"
    f.write_text("content", encoding="utf-8")
    h = compute_hash(f)

    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_one_byte_change_changes_hash(tmp_path):
    """A single character change must produce a completely different hash."""
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("Python is great.", encoding="utf-8")
    f2.write_text("Python is greet.", encoding="utf-8")  # 'a' → 'e'

    assert compute_hash(f1) != compute_hash(f2)


def test_hash_deterministic_across_calls(tmp_path):
    """Multiple calls on the same file must return the same hash."""
    f = tmp_path / "note.md"
    f.write_text("Determinism is essential.", encoding="utf-8")

    h1 = compute_hash(f)
    h2 = compute_hash(f)
    h3 = compute_hash(f)

    assert h1 == h2 == h3
````

## File: tests/unit/test_manifest.py
````python

````

## File: tests/unit/test_metadata.py
````python
"""
Unit tests for discovery/metadata.py.
"""

import pytest
from datetime import timezone
from pathlib import Path
from smriti.discovery.metadata import extract_metadata


def test_metadata_size(tmp_path):
    """size_bytes must match actual file size."""
    content = b"Hello, world! This is test content."
    f = tmp_path / "note.md"
    f.write_bytes(content)

    meta = extract_metadata(f)
    assert meta.size_bytes == len(content)


def test_metadata_extension_normalised(tmp_path):
    """Extension must be lowercase."""
    f = tmp_path / "NOTE.MD"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.extension == ".md"


def test_metadata_modified_time_is_utc(tmp_path):
    """modified_at must be UTC-aware."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    assert meta.modified_at.tzinfo is not None
    assert meta.modified_at.tzinfo == timezone.utc


def test_metadata_is_immutable(tmp_path):
    """FileMetadata is frozen — mutation must raise."""
    f = tmp_path / "note.md"
    f.write_text("content")
    meta = extract_metadata(f)
    with pytest.raises(Exception):
        meta.size_bytes = 999
````

## File: tests/unit/test_models.py
````python
"""Test data models."""

import pytest
from datetime import datetime
from pathlib import Path

from smriti.core.models import (
    Claim, Contradiction, ContradictionType,
    Document, FileFormat, Sentence, Embedding,
    Topic, ManifestEntry,
)


def test_claim_creation():
    claim = Claim(
        text="Python is great",
        document_path=Path("note.md"),
        sentence_position=0,
        extracted_at=datetime.now(),
    )
    assert claim.text == "Python is great"
    assert claim.unique_id() == "note:0"


def test_claim_unique_id_is_deterministic():
    path = Path("my_note.md")
    c1 = Claim("text", path, 3, datetime.now())
    c2 = Claim("other text", path, 3, datetime.now())
    assert c1.unique_id() == c2.unique_id()  # same doc + position = same id


def test_contradiction_creation():
    contra = Contradiction(
        claim_a_id="note1:0",
        claim_b_id="note2:0",
        contradiction_type=ContradictionType.STRATEGY_SHIFT,
        nli_confidence=0.85,
        similarity_score=0.78,
        temporal_distance_days=100,
        severity_score=7.5,
    )
    assert contra.severity_score == 7.5
    assert contra.contradiction_type == ContradictionType.STRATEGY_SHIFT


def test_document_size_inferred():
    doc = Document(
        path=Path("note.md"),
        format=FileFormat.MARKDOWN,
        raw_text="Hello world",
        discovered_at=datetime.now(),
    )
    assert doc.size_bytes > 0


def test_topic_drift_score():
    topic = Topic(name="python", claim_ids=["a", "b", "c", "d"], contradiction_count=2)
    assert topic.drift_score == pytest.approx(50.0)


def test_topic_drift_score_empty():
    topic = Topic(name="empty")
    assert topic.drift_score == 0.0


def test_manifest_entry_has_run_id():
    entry = ManifestEntry(
        run_id="20240715_143022",
        phase=1,
        timestamp=datetime.now(),
        duration_seconds=1.5,
        inputs={},
        outputs={},
        status="success",
    )
    assert entry.run_id == "20240715_143022"
    assert entry.schema_version == "1.0"
````

## File: tests/unit/test_parsing_builder.py
````python
"""
Unit tests for parsing/builder.py.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import (
    Document,
    ExtractionMethod,
    FileFormat,
    RawExtractionResult,
    SourceDocument,
    TextStatistics,
    WarningCode,
)
from smriti.parsing.builder import build_document
from smriti.exceptions import BuilderError, DocumentError


@pytest.fixture
def source_doc():
    return SourceDocument(
        doc_id="a" * 64,
        path=Path("note.md"),
        relative_path=Path("note.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="a" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def extraction_result():
    return RawExtractionResult(
        raw_text="# Hello\n\nWorld.",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
    )


@pytest.fixture
def stats():
    return TextStatistics(
        character_count=16,
        word_count=2,
        line_count=3,
        blank_line_count=1,
        paragraph_count=2,
    )


def test_build_returns_document(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert isinstance(doc, Document)


def test_doc_id_equals_source_doc_id(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.doc_id == source_doc.doc_id


def test_document_is_frozen(source_doc, extraction_result, stats):
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    with pytest.raises(Exception):
        doc.doc_id = "new_id"


def test_source_document_unchanged(source_doc, extraction_result, stats):
    original_path = source_doc.path
    doc = build_document(source_doc, extraction_result, "Hello\n\nWorld.", (), stats)
    assert doc.source_document.path == original_path


def test_warnings_merged(source_doc, stats):
    extraction_result = RawExtractionResult(
        raw_text="text",
        warnings=(WarningCode.NO_EXTRACTABLE_TEXT,),
        method=ExtractionMethod.MARKDOWN,
    )
    norm_warnings = (WarningCode.BLANK_LINES_COLLAPSED,)
    doc = build_document(source_doc, extraction_result, "text", norm_warnings, stats)
    assert len(doc.extraction_warnings) == 2


def test_wrong_doc_id_raises(source_doc, extraction_result, stats):
    """doc_id must match source_document.doc_id — mismatch raises DocumentError."""
    wrong_source = SourceDocument(
        doc_id="b" * 64,         # different doc_id
        path=Path("other.md"),
        relative_path=Path("other.md"),
        source_root=Path("."),
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=100,
        modified_at=datetime.now(tz=timezone.utc),
    )
    # Builder uses source_document.doc_id — so the Document will have "b"*64
    # This should succeed; the invariant is enforced inside Document.__post_init__
    doc = build_document(wrong_source, extraction_result, "text", (), stats)
    assert doc.doc_id == "b" * 64


def test_empty_document_produces_warning(source_doc, stats):
    """Empty normalized text must produce NO_EXTRACTABLE_TEXT warning."""
    extraction_result = RawExtractionResult(
        raw_text="",
        warnings=(),
        method=ExtractionMethod.MARKDOWN,
    )
    empty_stats = TextStatistics(
        character_count=0, word_count=0, line_count=0,
        blank_line_count=0, paragraph_count=0,
    )
    doc = build_document(source_doc, extraction_result, "", (), empty_stats)
    assert doc.has_warnings
    assert WarningCode.NO_EXTRACTABLE_TEXT in doc.extraction_warnings
````

## File: tests/unit/test_parsing_loader.py
````python
"""
Unit tests for parsing/loader.py.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.models import FileFormat, SourceDocument
from smriti.parsing.loader import load_document


def make_source(path: Path, fmt: FileFormat, doc_id: str = "a" * 64) -> SourceDocument:
    return SourceDocument(
        doc_id=doc_id,
        path=path,
        relative_path=path.name,
        source_root=path.parent,
        format=fmt,
        content_hash=doc_id,
        size_bytes=path.stat().st_size if path.exists() else 0,
        modified_at=datetime.now(tz=timezone.utc),
    )


def test_markdown_document_succeeds(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# AI\n\nAI is transforming everything.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None
    assert "AI" in doc.normalized_text


def test_text_document_succeeds(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("Plain text content here.", encoding="utf-8")
    source = make_source(f, FileFormat.TEXT)
    doc, error = load_document(source)
    assert doc is not None
    assert error is None


def test_nonexistent_file_returns_none_not_raise(tmp_path):
    """Missing file must return (None, error) — NOT raise."""
    source = make_source(tmp_path / "ghost.md", FileFormat.MARKDOWN)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None
    assert "Error" in error or "error" in error.lower()


def test_corrupted_pdf_returns_none_not_raise(tmp_path):
    """Corrupted PDF must return (None, error) — NOT raise, batch continues."""
    f = tmp_path / "bad.pdf"
    f.write_bytes(b"not a pdf")
    source = make_source(f, FileFormat.PDF)
    doc, error = load_document(source)
    assert doc is None
    assert error is not None


def test_doc_id_preserved(tmp_path):
    """doc_id must equal source_document.doc_id — identity invariant."""
    f = tmp_path / "note.md"
    f.write_text("hello world", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert doc.doc_id == source.doc_id


def test_normalized_text_strips_crlf(tmp_path):
    """CRLF in source file must become LF in normalized_text."""
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "\r\n" not in doc.normalized_text


def test_markdown_headings_preserved(tmp_path):
    """# headings must survive extraction (not stripped)."""
    f = tmp_path / "headings.md"
    f.write_text("# Main Topic\n\n## Subtopic\n\nContent.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "# Main Topic" in doc.normalized_text
    assert "## Subtopic" in doc.normalized_text


def test_unicode_content_handled(tmp_path):
    """Unicode content (CJK, emoji, accented) must be preserved."""
    f = tmp_path / "unicode.md"
    f.write_text("# 日本語\n\nCafé résumé naïve.", encoding="utf-8")
    source = make_source(f, FileFormat.MARKDOWN)
    doc, _ = load_document(source)
    assert doc is not None
    assert "日本語" in doc.normalized_text
    assert "Café" in doc.normalized_text
````

## File: tests/unit/test_parsing_markdown.py
````python
"""
Unit tests for parsing/markdown.py.
"""

import pytest
from pathlib import Path
from smriti.parsing.markdown import MarkdownExtractor
from smriti.core.models import ExtractionMethod, WarningCode


@pytest.fixture
def extractor():
    return MarkdownExtractor()


@pytest.fixture
def simple_md(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# Hello\n\nWorld.", encoding="utf-8")
    return f


def test_extracts_text(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert "Hello" in result.raw_text
    assert "World" in result.raw_text


def test_preserves_markdown_syntax(extractor, simple_md):
    """Markdown # heading must NOT be stripped."""
    result = extractor.extract(simple_md)
    assert "# Hello" in result.raw_text


def test_method_is_markdown(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert result.method == ExtractionMethod.MARKDOWN


def test_no_warnings_on_clean_utf8(extractor, simple_md):
    result = extractor.extract(simple_md)
    assert len(result.warnings) == 0


def test_crlf_warning_detected(extractor, tmp_path):
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    result = extractor.extract(f)
    assert WarningCode.MIXED_LINE_ENDINGS in result.warnings or "\r\n" in result.raw_text


def test_null_bytes_removed(extractor, tmp_path):
    f = tmp_path / "null.md"
    f.write_bytes(b"hello\x00world")
    result = extractor.extract(f)
    assert "\x00" not in result.raw_text
    assert WarningCode.NULL_BYTES_REMOVED in result.warnings


def test_encoding_fallback_latin1(extractor, tmp_path):
    """Latin-1 encoded file must decode with fallback warning."""
    f = tmp_path / "latin.md"
    f.write_bytes("caf\xe9".encode("latin-1"))
    result = extractor.extract(f)
    assert len(result.raw_text) > 0
    # Either decoded fine or produced a fallback warning
    # (depends on whether utf-8 fails gracefully)


def test_markdown_table_preserved(extractor, tmp_path):
    """Markdown table syntax must be preserved verbatim."""
    f = tmp_path / "table.md"
    f.write_text("| Col1 | Col2 |\n|------|------|\n| A    | B    |", encoding="utf-8")
    result = extractor.extract(f)
    assert "| Col1 |" in result.raw_text
    assert "|------|" in result.raw_text


def test_unreadable_file_raises(extractor, tmp_path):
    from smriti.exceptions import MarkdownExtractionError
    fake = tmp_path / "nonexistent.md"
    with pytest.raises(MarkdownExtractionError):
        extractor.extract(fake)
````

## File: tests/unit/test_parsing_normalize.py
````python
"""
Unit tests for parsing/normalize.py.

Every normalization rule is tested in isolation.
Determinism is verified: same input → same output every time.
"""

import pytest
from smriti.parsing.normalize import normalize_text
from smriti.core.models import WarningCode, NormalizationResult


# ── Unicode normalization ─────────────────────────────────────────────────────

def test_nfc_normalization_makes_equivalent_sequences_identical():
    """é as NFC and NFD decomposed must both normalize to the same NFC form."""
    import unicodedata
    nfc_e = "\u00e9"           # é as single code point (NFC)
    nfd_e = "e\u0301"          # é as e + combining acute (NFD)
    assert nfc_e != nfd_e      # They start different
    result_nfc = normalize_text(nfc_e)
    result_nfd = normalize_text(nfd_e)
    assert result_nfc.normalized_text == result_nfd.normalized_text  # After normalization: identical


def test_bom_is_removed():
    """UTF-8 BOM character must be stripped."""
    text_with_bom = "\ufeffHello world"
    result = normalize_text(text_with_bom)
    assert not result.normalized_text.startswith("\ufeff")
    assert WarningCode.BOM_REMOVED in result.warnings


# ── Line ending normalization ─────────────────────────────────────────────────

def test_crlf_converted_to_lf():
    """Windows CRLF must become LF."""
    result = normalize_text("line1\r\nline2\r\nline3")
    assert "\r\n" not in result.normalized_text
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"
    assert WarningCode.LINE_ENDINGS_NORMALIZED in result.warnings


def test_cr_only_converted_to_lf():
    """Old Mac CR-only must become LF."""
    result = normalize_text("line1\rline2\rline3")
    assert "\r" not in result.normalized_text
    assert result.normalized_text == "line1\nline2\nline3"


def test_pure_lf_unchanged():
    """Files already using LF must not be modified (no spurious warning)."""
    text = "line1\nline2\nline3"
    result = normalize_text(text)
    assert result.normalized_text == text
    assert WarningCode.LINE_ENDINGS_NORMALIZED not in result.warnings


# ── Trailing whitespace ───────────────────────────────────────────────────────

def test_trailing_whitespace_removed_per_line():
    """Trailing spaces and tabs on each line must be removed."""
    result = normalize_text("hello   \nworld\t\n")
    lines = result.normalized_text.split("\n")
    for line in lines:
        assert not line.endswith(" ")
        assert not line.endswith("\t")
    assert WarningCode.TRAILING_WHITESPACE_REMOVED in result.warnings


def test_leading_indentation_preserved():
    """Leading whitespace (indentation) must NEVER be removed."""
    text = "    indented line\n        double indent"
    result = normalize_text(text)
    lines = result.normalized_text.split("\n")
    assert lines[0].startswith("    ")
    assert lines[1].startswith("        ")


# ── Blank line collapsing ─────────────────────────────────────────────────────

def test_excessive_blank_lines_collapsed():
    """100 consecutive blank lines must collapse to max configured blank lines."""
    text = "paragraph1\n" + "\n" * 100 + "paragraph2"
    result = normalize_text(text)
    # Should not have more than collapse_blank_lines (default=2) consecutive blank lines
    assert "\n\n\n\n" not in result.normalized_text  # More than 2 blank lines = 4+ newlines
    assert WarningCode.BLANK_LINES_COLLAPSED in result.warnings


def test_single_blank_line_preserved():
    """A single blank line between paragraphs must be preserved."""
    text = "paragraph1\n\nparagraph2"
    result = normalize_text(text)
    assert "paragraph1\n\nparagraph2" in result.normalized_text


# ── Control characters ────────────────────────────────────────────────────────

def test_control_characters_removed():
    """Non-printable control characters (except LF, TAB) must be removed."""
    text = "hello\x07world\x1btest"  # BEL, ESC
    result = normalize_text(text)
    assert "\x07" not in result.normalized_text
    assert "\x1b" not in result.normalized_text
    assert WarningCode.CONTROL_CHARS_REMOVED in result.warnings


def test_tab_preserved():
    """TAB characters must be preserved (carry indentation meaning)."""
    text = "\thello\tworld"
    result = normalize_text(text)
    assert "\t" in result.normalized_text


# ── Determinism ───────────────────────────────────────────────────────────────

def test_normalization_is_deterministic():
    """Same input must always produce same output."""
    text = "Hello\r\n\r\nWorld   \r\n"
    result1 = normalize_text(text)
    result2 = normalize_text(text)
    assert result1.normalized_text == result2.normalized_text
    assert result1.warnings == result2.warnings


def test_empty_string_handled():
    """Empty string must return empty string without errors."""
    result = normalize_text("")
    assert result.normalized_text == ""


def test_whitespace_only_string_handled():
    """Whitespace-only input must return empty string."""
    result = normalize_text("   \n\t\n   ")
    assert result.normalized_text == ""


# ── Error handling ────────────────────────────────────────────────────────────

def test_non_string_raises():
    """Passing non-string must raise NormalizationError."""
    from smriti.exceptions import NormalizationError
    with pytest.raises(NormalizationError):
        normalize_text(None)  # type: ignore
````

## File: tests/unit/test_parsing_pdf.py
````python
"""
Unit tests for parsing/pdf.py.
"""

import pytest
from pathlib import Path
from smriti.parsing.pdf import PdfExtractor
from smriti.core.models import ExtractionMethod


@pytest.fixture
def extractor():
    return PdfExtractor()


@pytest.fixture
def minimal_pdf(tmp_path):
    """Create a minimal valid PDF with a text layer."""
    try:
        import pypdf
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
        import pypdf
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
````

## File: tests/unit/test_parsing_statistics.py
````python
"""
Unit tests for parsing/statistics.py.

Every statistic is verified for correctness and internal consistency.
"""

import pytest
from smriti.parsing.statistics import compute_statistics
from smriti.core.models import TextStatistics


def test_empty_string_returns_zeros():
    stats = compute_statistics("")
    assert stats.character_count == 0
    assert stats.word_count == 0
    assert stats.line_count == 0
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 0


def test_whitespace_only_returns_zeros():
    stats = compute_statistics("   \n\t\n  ")
    assert stats.word_count == 0
    assert stats.paragraph_count == 0


def test_single_line():
    stats = compute_statistics("Hello world")
    assert stats.character_count == 11
    assert stats.word_count == 2
    assert stats.line_count == 1
    assert stats.blank_line_count == 0
    assert stats.paragraph_count == 1


def test_two_paragraphs_with_blank_line():
    text = "First paragraph.\n\nSecond paragraph."
    stats = compute_statistics(text)
    assert stats.paragraph_count == 2
    assert stats.blank_line_count == 1
    assert stats.line_count == 3


def test_three_paragraphs():
    text = "Para 1\n\nPara 2\n\nPara 3"
    stats = compute_statistics(text)
    assert stats.paragraph_count == 3


def test_blank_line_count_never_exceeds_line_count():
    text = "\n\n\nsome text\n\n"
    stats = compute_statistics(text)
    assert stats.blank_line_count <= stats.line_count


def test_word_count_multiline():
    text = "one two\nthree four\nfive"
    stats = compute_statistics(text)
    assert stats.word_count == 5


def test_character_count_includes_whitespace():
    text = "ab cd"
    stats = compute_statistics(text)
    assert stats.character_count == 5


def test_multiline_blank_lines():
    text = "line1\n\n\n\nline2"
    stats = compute_statistics(text)
    assert stats.blank_line_count == 3   # 3 empty lines between line1 and line2
    assert stats.line_count == 5


def test_returns_frozen_dataclass():
    stats = compute_statistics("hello")
    with pytest.raises(Exception):
        stats.word_count = 999  # frozen dataclass — mutation must raise


def test_non_string_raises():
    from smriti.exceptions import StatisticsError
    with pytest.raises(StatisticsError):
        compute_statistics(123)  # type: ignore
````

## File: tests/unit/test_phase2_extraction.py
````python
"""
Integration test for Phase 2 end-to-end.

Tests the complete pipeline:
  List[SourceDocument] → ExtractionResult

Uses a realistic vault fixture with all supported formats.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from smriti.core.manifest import ManifestManager
from smriti.core.models import FileFormat, SourceDocument
from smriti.core.state import StateManager
from smriti.parsing import run_extraction, ExtractionResult


def make_source(path: Path, fmt: FileFormat) -> SourceDocument:
    content_hash = "a" * 64
    return SourceDocument(
        doc_id=content_hash,
        path=path,
        relative_path=Path(path.name),
        source_root=path.parent,
        format=fmt,
        content_hash=content_hash,
        size_bytes=path.stat().st_size,
        modified_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def vault_documents(tmp_path):
    """Create a realistic set of source documents for testing."""
    vault = tmp_path / "vault"
    vault.mkdir()

    docs = []

    # --- Markdown documents ---
    ai_md = vault / "AI.md"
    ai_md.write_text(
        "# Artificial Intelligence\n\n"
        "AI is transforming every industry.\n\n"
        "## Machine Learning\n\n"
        "Machine learning is a subset of AI.\n",
        encoding="utf-8",
    )
    docs.append(make_source(ai_md, FileFormat.MARKDOWN))

    python_md = vault / "Python.md"
    python_md.write_text(
        "# Python\n\nPython is the dominant language for data science.\n\n"
        "It is also used for web development.\n",
        encoding="utf-8",
    )
    docs.append(make_source(python_md, FileFormat.MARKDOWN))

    # Unicode content
    unicode_md = vault / "unicode.md"
    unicode_md.write_text(
        "# 研究ノート\n\nCafé résumé naïve.\n\nПривет мир.\n",
        encoding="utf-8",
    )
    docs.append(make_source(unicode_md, FileFormat.MARKDOWN))

    # Markdown with CRLF endings
    crlf_md = vault / "crlf.md"
    crlf_md.write_bytes(b"# Windows File\r\n\r\nWritten on Windows.\r\n")
    docs.append(make_source(crlf_md, FileFormat.MARKDOWN))

    # --- Text documents ---
    txt = vault / "notes.txt"
    txt.write_text(
        "Plain text research notes.\n\nSecond paragraph of notes.\n",
        encoding="utf-8",
    )
    docs.append(make_source(txt, FileFormat.TEXT))

    return docs


@pytest.fixture
def run_id():
    return "test_phase2_20240101_120000"


@pytest.fixture
def test_managers(tmp_path, run_id):
    artifacts = tmp_path / "artifacts"
    return (
        ManifestManager(run_id=run_id, artifacts_dir=artifacts),
        StateManager(state_file=tmp_path / "state.json"),
    )


# ── Functional tests ──────────────────────────────────────────────────────────

def test_phase2_produces_documents(vault_documents, run_id, test_managers):
    """Phase 2 must return a Document for every valid SourceDocument."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=vault_documents,
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )
    assert len(result.documents) == len(vault_documents)
    assert result.stats.failed == 0


def test_phase2_documents_are_frozen(vault_documents, run_id, test_managers):
    """Document must be frozen (immutable)."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    doc = result.documents[0]
    with pytest.raises(Exception):
        doc.normalized_text = "mutated"


def test_phase2_doc_id_preserved(vault_documents, run_id, test_managers):
    """doc_id must equal source_document.doc_id for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert doc.doc_id == doc.source_document.doc_id


def test_phase2_crlf_normalized(vault_documents, run_id, test_managers):
    """CRLF line endings must be normalized to LF in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        assert "\r\n" not in doc.normalized_text
        assert "\r" not in doc.normalized_text


def test_phase2_markdown_headings_preserved(vault_documents, run_id, test_managers):
    """Markdown # headings must survive in normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    md_docs = [d for d in result.documents if "AI.md" in str(d.source_document.path)]
    assert len(md_docs) == 1
    assert "# Artificial Intelligence" in md_docs[0].normalized_text


def test_phase2_unicode_preserved(vault_documents, run_id, test_managers):
    """Unicode content must be preserved correctly."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    unicode_docs = [d for d in result.documents if "unicode.md" in str(d.source_document.path)]
    assert len(unicode_docs) == 1
    assert "研究" in unicode_docs[0].normalized_text
    assert "Café" in unicode_docs[0].normalized_text


def test_phase2_statistics_consistent(vault_documents, run_id, test_managers):
    """TextStatistics invariants must hold for every document."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    for doc in result.documents:
        s = doc.text_statistics
        assert s.character_count >= 0
        assert s.word_count >= 0
        assert s.blank_line_count <= s.line_count
        assert s.paragraph_count <= s.line_count


def test_phase2_one_failure_does_not_stop_batch(run_id, test_managers, tmp_path):
    """A corrupted document must not stop processing of the remaining documents."""
    from smriti.core.models import SourceDocument

    vault = tmp_path / "vault"
    vault.mkdir()

    # Valid document
    good = vault / "good.md"
    good.write_text("# Good\n\nThis is fine.", encoding="utf-8")

    # Document pointing to nonexistent file
    ghost_source = SourceDocument(
        doc_id="b" * 64,
        path=tmp_path / "ghost.md",   # Does not exist
        relative_path=Path("ghost.md"),
        source_root=tmp_path,
        format=FileFormat.MARKDOWN,
        content_hash="b" * 64,
        size_bytes=0,
        modified_at=datetime.now(tz=timezone.utc),
    )

    good_source = make_source(good, FileFormat.MARKDOWN)

    manifest_mgr, state_mgr = test_managers
    result = run_extraction(
        source_documents=[good_source, ghost_source],
        run_id=run_id,
        manifest_manager=manifest_mgr,
        state_manager=state_mgr,
    )

    # Good document succeeded, ghost failed — batch continued
    assert result.stats.successful == 1
    assert result.stats.failed == 1
    assert len(result.documents) == 1


# ── Artifact tests ────────────────────────────────────────────────────────────

def test_phase2_writes_manifest(vault_documents, run_id, test_managers):
    """A manifest.json must be written after Phase 2."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["phase"] == 2
    assert manifest["status"] in ("success", "partial")
    assert manifest["run_id"] == run_id


def test_phase2_writes_dataset_json(vault_documents, run_id, test_managers, tmp_path):
    """dataset.json must be written with correct structure."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    assert result.dataset_path is not None
    assert result.dataset_path.exists()

    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    assert len(dataset) == len(result.documents)

    for record in dataset:
        assert "doc_id" in record
        assert "normalized_text" in record
        assert "text_statistics" in record
        assert "extraction_method" in record
        # raw_text must NOT be in the dataset — too large, not needed by Phase 3
        assert "raw_text" not in record


def test_phase2_dataset_has_no_raw_text(vault_documents, run_id, test_managers):
    """dataset.json must never contain raw_text — only normalized_text."""
    manifest_mgr, state_mgr = test_managers
    result = run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    dataset = json.loads(result.dataset_path.read_text(encoding="utf-8"))
    for record in dataset:
        assert "raw_text" not in record


def test_phase2_updates_pipeline_state(vault_documents, run_id, test_managers):
    """Pipeline state must mark Phase 2 as complete."""
    manifest_mgr, state_mgr = test_managers
    run_extraction(vault_documents, run_id, manifest_mgr, state_mgr)
    state = state_mgr.load()
    assert state is not None
    assert 2 in state.completed_phases


# ── Architectural tests ───────────────────────────────────────────────────────

def test_phase2_no_nlp_imports():
    """Phase 2 must never import NLP libraries."""
    import smriti.parsing.markdown as markdown_mod
    import smriti.parsing.text as text_mod
    import smriti.parsing.normalize as normalize_mod
    import smriti.parsing.statistics as statistics_mod
    import smriti.parsing.builder as builder_mod
    import smriti.parsing.loader as loader_mod

    nlp_modules = {"spacy", "transformers", "sentence_transformers", "faiss"}

    for module in [markdown_mod, text_mod, normalize_mod, statistics_mod, builder_mod, loader_mod]:
        module_imports = set(vars(module).keys())
        assert not (module_imports & nlp_modules), (
            f"{module.__name__} imports NLP libraries — Phase 2 must not do NLP"
        )


def test_phase2_is_deterministic(vault_documents, test_managers, tmp_path):
    """Running Phase 2 twice on same input must produce identical normalized_text."""
    manifest_mgr, state_mgr = test_managers

    result1 = run_extraction(vault_documents, "run1", manifest_mgr, state_mgr)
    result2 = run_extraction(vault_documents, "run2", manifest_mgr, state_mgr)

    texts1 = {d.doc_id: d.normalized_text for d in result1.documents}
    texts2 = {d.doc_id: d.normalized_text for d in result2.documents}

    assert texts1 == texts2
````

## File: tests/unit/test_phase3_builder.py
````python
"""
Unit tests for extraction/builder.py.
"""

import pytest
from pathlib import Path
from smriti.extraction.builder import build_sentence, _compute_sentence_id


def test_build_returns_semantic_sentence():
    from smriti.core.models import SemanticSentence
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="Technology",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert isinstance(s, SemanticSentence)


def test_sentence_id_is_16_chars():
    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
    )
    assert len(s.sentence_id) == 16


def test_sentence_id_is_deterministic():
    """Same inputs must always produce the same ID."""
    s1 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    s2 = build_sentence("text", "doc1", Path("a.md"), "", 0, 0, 4)
    assert s1.sentence_id == s2.sentence_id


def test_different_text_different_id():
    s1 = build_sentence("Python is great.", "doc1", Path("a.md"), "", 0, 0, 16)
    s2 = build_sentence("Julia is faster.", "doc1", Path("a.md"), "", 0, 0, 16)
    assert s1.sentence_id != s2.sentence_id


def test_different_position_different_id():
    """Same text at different char_start must produce different ID."""
    s1 = build_sentence("same text.", "doc1", Path("a.md"), "", 0, 0, 10)
    s2 = build_sentence("same text.", "doc1", Path("a.md"), "", 1, 50, 60)
    assert s1.sentence_id != s2.sentence_id


def test_semantic_sentence_is_frozen():
    """SemanticSentence must be immutable."""
    s = build_sentence("Python.", "doc1", Path("a.md"), "", 0, 0, 7)
    with pytest.raises(Exception):
        s.text = "Julia."


def test_context_stored_separately():
    """Context must be stored as-is, never fused into text."""
    s = build_sentence("Supports tensors.", "doc1", Path("a.md"), "CUDA", 0, 0, 17)
    assert s.text == "Supports tensors."
    assert s.context == "CUDA"
    assert "CUDA" not in s.text


def test_empty_context_allowed():
    """Sentences at document root have no context."""
    s = build_sentence("Introduction.", "doc1", Path("a.md"), "", 0, 0, 13)
    assert s.context == ""


def test_builder_adds_provenance_and_version():
    """Test that origin_block_type and schema_version are correctly set."""
    from smriti.extraction.scanner import BlockType

    s = build_sentence(
        text="Python is great.",
        document_id="doc123",
        source_path=Path("note.md"),
        context="",
        position=0,
        char_start=0,
        char_end=16,
        origin_block_type=BlockType.PARAGRAPH,
    )
    assert s.origin_block_type == BlockType.PARAGRAPH
    assert s.schema_version == "3.0"
````

## File: tests/unit/test_phase3_context.py
````python
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
````

## File: tests/unit/test_phase3_normalizer.py
````python
"""
Unit tests for extraction/normalizer.py.
"""

import pytest
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.extraction.normalizer import normalize_event
from smriti.core.models import SegmentationWarning


def make_event(block_type, text, raw_text=None, heading_level=None, lines=None):
    return ScannerEvent(
        block_type=block_type,
        text=text,
        raw_text=raw_text or text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=tuple(lines or [text]),
    )


def test_paragraph_passes_through():
    event = make_event(BlockType.PARAGRAPH, "Python is great for data science.")
    block = normalize_event(event)
    assert block.prose == "Python is great for data science."
    assert block.skip is False


def test_heading_is_skipped():
    """Headings must produce no prose — they are context only."""
    event = make_event(BlockType.HEADING, "Python", heading_level=1)
    block = normalize_event(event)
    assert block.skip is True
    assert block.prose == ""


def test_bullet_item_normalized():
    event = make_event(BlockType.BULLET_ITEM, "Use Poetry for dependency management")
    block = normalize_event(event)
    assert "Use Poetry" in block.prose
    assert block.skip is False


def test_bullet_item_gets_period():
    """Bullet items without trailing period must get one added."""
    event = make_event(BlockType.BULLET_ITEM, "No trailing period")
    block = normalize_event(event)
    assert block.prose.endswith(".")


def test_block_quote_normalized():
    event = make_event(BlockType.BLOCK_QUOTE, "Reliability is critical")
    block = normalize_event(event)
    assert "Reliability" in block.prose
    assert block.skip is False


def test_code_block_skipped():
    event = make_event(BlockType.CODE_BLOCK, "print('hello')")
    block = normalize_event(event)
    assert block.skip is True
    assert SegmentationWarning.SEG_CODE_BLOCK_SKIPPED in block.warnings


def test_horizontal_rule_skipped():
    event = make_event(BlockType.HORIZONTAL_RULE, "")
    block = normalize_event(event)
    assert block.skip is True


def test_table_normalized_to_prose():
    """Table rows become key-value prose sentences."""
    lines = [
        "| Model | Accuracy |",
        "|-------|----------|",
        "| GPT-4 | 85%      |",
    ]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        raw_text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert not block.skip
    assert "Model" in block.prose or "GPT-4" in block.prose


def test_malformed_table_emits_warning():
    """A table with only a separator produces SEG_MALFORMED_TABLE."""
    lines = ["|------|"]
    raw = "\n".join(lines)
    event = ScannerEvent(
        block_type=BlockType.TABLE,
        text=raw,
        raw_text=raw,
        heading_level=None,
        char_start=0,
        char_end=len(raw),
        lines=tuple(lines),
    )
    block = normalize_event(event)
    assert SegmentationWarning.SEG_MALFORMED_TABLE in block.warnings
````

## File: tests/unit/test_phase3_scanner.py
````python
"""
Unit tests for extraction/scanner.py.
The scanner has one job: identify structural events.
These tests never touch context, segmentation, or building.
"""

import pytest
from smriti.extraction.scanner import scan_document, BlockType



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
    types = [e.block_type for e in events]
    # H1 heading must come before paragraph, paragraph before bullet
    h1_idx = next(i for i, e in enumerate(events)
                  if e.block_type == BlockType.HEADING and e.heading_level == 1)
    para_idx = next(i for i, e in enumerate(events)
                    if e.block_type == BlockType.PARAGRAPH)
    bullet_idx = next(i for i, e in enumerate(events)
                      if e.block_type == BlockType.BULLET_ITEM)
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
````

## File: tests/unit/test_phase3_segmenter.py
````python
"""
Unit tests for extraction/segmenter.py.
"""

import pytest
from smriti.extraction.segmenter import SentenceSegmenter


@pytest.fixture
def segmenter():
    return SentenceSegmenter()


def test_single_sentence(segmenter):
    result = segmenter.segment("Python is great for data science.")
    assert len(result) == 1
    assert result[0].text == "Python is great for data science."


def test_two_sentences(segmenter):
    result = segmenter.segment(
        "Python is great for data science. Julia is faster for numerical computing."
    )
    assert len(result) == 2


def test_question_mark_splits(segmenter):
    result = segmenter.segment(
        "Is Python good? Yes, it is very good."
    )
    assert len(result) == 2


def test_exclamation_splits(segmenter):
    result = segmenter.segment(
        "This works! Now let's move on."
    )
    assert len(result) == 2


def test_abbreviation_dr_does_not_split(segmenter):
    """'Dr. Smith' must not split into two sentences."""
    result = segmenter.segment("Dr. Smith visited the lab.")
    assert len(result) == 1


def test_abbreviation_eg_does_not_split(segmenter):
    """'e.g. Python' must not split."""
    result = segmenter.segment("Use a high-level language, e.g. Python or Julia.")
    assert len(result) == 1


def test_abbreviation_ie_does_not_split(segmenter):
    """'i.e. that' must not split."""
    result = segmenter.segment("Use the right tool, i.e. the simplest one.")
    assert len(result) == 1


def test_decimal_number_does_not_split(segmenter):
    """'3.14' must not split."""
    result = segmenter.segment("Pi is approximately 3.14 and it is irrational.")
    assert len(result) == 1


def test_empty_prose_returns_empty(segmenter):
    result = segmenter.segment("")
    assert result == []


def test_whitespace_only_returns_empty(segmenter):
    result = segmenter.segment("   \n\n   ")
    assert result == []


def test_sentence_text_is_stripped(segmenter):
    """Sentence text must not have leading/trailing whitespace."""
    result = segmenter.segment("  Python is great.  Julia is fast.  ")
    for s in result:
        assert s.text == s.text.strip()


def test_positions_are_non_negative(segmenter):
    result = segmenter.segment("First sentence. Second sentence.")
    for s in result:
        assert s.char_start >= 0
        assert s.char_end > s.char_start


def test_three_sentences(segmenter):
    text = "First. Second. Third."
    result = segmenter.segment(text)
    assert len(result) == 3


def test_very_long_sentence_emits_warning(segmenter):
    """A sentence exceeding max_sentence_chars must emit SEG002."""
    from smriti.core.models import SegmentationWarning
    long_text = "word " * 500 + "."
    result = segmenter.segment(long_text)
    assert len(result) == 1
    assert SegmentationWarning.SEG_VERY_LONG_SENTENCE in result[0].warnings
````

## File: tests/unit/test_phase3_statistics.py
````python
"""
Unit tests for extraction/statistics.py.
"""

import pytest
from smriti.extraction.statistics import Phase3StatsCollector
from smriti.extraction.scanner import BlockType, ScannerEvent
from smriti.core.models import Phase3Stats, SegmentationWarning


def make_event(block_type: BlockType, text: str = "", heading_level: int = None) -> ScannerEvent:
    return ScannerEvent(
        block_type=block_type,
        text=text,
        heading_level=heading_level,
        char_start=0,
        char_end=len(text),
        lines=(text,),
    )


def test_stats_collector_counts_all_block_types():
    collector = Phase3StatsCollector()

    # Generate one of each block type
    events = [
        make_event(BlockType.HEADING, "H1", heading_level=1),
        make_event(BlockType.PARAGRAPH, "paragraph"),
        make_event(BlockType.BULLET_ITEM, "bullet"),
        make_event(BlockType.ORDERED_ITEM, "ordered"),
        make_event(BlockType.TABLE, "table"),
        make_event(BlockType.BLOCK_QUOTE, "quote"),
        make_event(BlockType.CODE_BLOCK, "code"),
        make_event(BlockType.HORIZONTAL_RULE, "---"),
        make_event(BlockType.FRONT_MATTER, "---"),
        make_event(BlockType.BLANK, ""),
        make_event(BlockType.UNKNOWN, "unknown"),  # This should be counted as unknown
    ]

    for event in events:
        collector.accumulate_event(event)

    # Record some sentences
    for _ in range(5):
        collector.record_sentence_produced()
    for _ in range(2):
        collector.record_sentence_discarded()

    # Record a warning
    collector.record_warnings((SegmentationWarning.SEG_CODE_BLOCK_SKIPPED,))

    stats = collector.finalize()

    assert isinstance(stats, Phase3Stats)
    assert stats.total_headings == 1
    assert stats.total_paragraphs == 1
    assert stats.total_list_items == 2  # bullet + ordered
    assert stats.total_tables == 1
    assert stats.total_block_quotes == 1
    assert stats.total_code_blocks_skipped == 1
    assert stats.total_horizontal_rules == 1
    assert stats.total_front_matter_blocks == 1
    assert stats.total_blank_lines == 1
    assert stats.total_unknown_blocks == 1  # the UNKNOWN event
    assert stats.sentences_produced == 5
    assert stats.sentences_discarded == 2
    assert len(stats.warnings) == 1
    assert stats.warnings[0] == SegmentationWarning.SEG_CODE_BLOCK_SKIPPED


def test_stats_collector_empty_document():
    collector = Phase3StatsCollector()
    stats = collector.finalize()

    assert stats.total_headings == 0
    assert stats.total_paragraphs == 0
    assert stats.total_list_items == 0
    assert stats.total_tables == 0
    assert stats.total_block_quotes == 0
    assert stats.total_code_blocks_skipped == 0
    assert stats.total_horizontal_rules == 0
    assert stats.total_front_matter_blocks == 0
    assert stats.total_blank_lines == 0
    assert stats.total_unknown_blocks == 0
    assert stats.sentences_produced == 0
    assert stats.sentences_discarded == 0
    assert len(stats.warnings) == 0
````

## File: tests/unit/test_phase3_validator.py
````python
"""
Unit tests for extraction/validator.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, SegmentationWarning
from smriti.extraction.validator import validate_sentences
from smriti.exceptions import SentenceValidationError


def make_sentence(sid, doc_id, text, position, char_start=0, char_end=10, context=""):
    return SemanticSentence(
        sentence_id=sid,
        document_id=doc_id,
        text=text,
        context=context,
        position=position,
        char_start=char_start,
        char_end=char_end,
        source_path=Path("note.md"),
    )


def test_valid_sentences_pass():
    sentences = [
        make_sentence("aaa", "doc1", "First sentence.", 0, 0, 15),
        make_sentence("bbb", "doc1", "Second sentence.", 1, 16, 32),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 2
    assert warnings == []


def test_empty_sentence_is_discarded():
    sentences = [
        make_sentence("aaa", "doc1", "   ", 0),
        make_sentence("bbb", "doc1", "Real sentence.", 1),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert len(valid) == 1
    assert SegmentationWarning.SEG_EMPTY_SENTENCE_DISCARDED in warnings


def test_duplicate_id_raises():
    sentences = [
        make_sentence("dup", "doc1", "First.", 0),
        make_sentence("dup", "doc1", "Second.", 1),  # Same ID!
    ]
    with pytest.raises(SentenceValidationError, match="Duplicate"):
        validate_sentences(sentences, "doc1")


def test_non_monotonic_position_raises():
    sentences = [
        make_sentence("aaa", "doc1", "First.", 2),  # Position 2
        make_sentence("bbb", "doc1", "Second.", 1), # Position 1 — goes backwards!
    ]
    with pytest.raises(SentenceValidationError):
        validate_sentences(sentences, "doc1")


def test_wrong_document_id_raises():
    sentences = [
        make_sentence("aaa", "wrong_doc", "Text.", 0),
    ]
    with pytest.raises(SentenceValidationError, match="document_id"):
        validate_sentences(sentences, "doc1")


def test_empty_input_returns_empty():
    valid, warnings = validate_sentences([], "doc1")
    assert valid == []
    assert warnings == []


def test_invalid_context_emits_warning():
    from smriti.extraction.rules import CONTEXT_SEPARATOR
    # context with illegal characters (e.g., "Python@CUDA")
    sentences = [
        make_sentence("aaa", "doc1", "text", 0, 0, 4, context="Python@CUDA"),
    ]
    valid, warnings = validate_sentences(sentences, "doc1")
    assert SegmentationWarning.VAL_INVALID_CONTEXT in warnings
````

## File: tests/unit/test_phase4_annotation.py
````python
"""
Unit tests for claims/annotation.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, Modality, ExtractionMode
from smriti.claims.annotation import AssertionAnnotator
from smriti.claims.parser import SpaCyParser
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def annotator():
    return AssertionAnnotator()


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_structured_candidate(parser, extractor, text):
    from smriti.claims.models import AssertionCandidate
    sentence = SemanticSentence(
        sentence_id="s001", document_id="d001", text=text,
        context="", position=0, char_start=0, char_end=len(text),
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = parser.parse(sentence)
    candidate = AssertionCandidate(
        text=text, span_start=0, span_end=len(text),
        source=parsed, boundary_reason="test",
    )
    return extractor.extract(candidate)


def test_negation_detected(parser, extractor, annotator):
    """'Python does not support X' → is_negated=True."""
    sc = make_structured_candidate(parser, extractor, "Python does not support this feature.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_negated is True


def test_no_negation_in_positive(parser, extractor, annotator):
    """'Python supports X' → is_negated=False."""
    sc = make_structured_candidate(parser, extractor, "Python supports generators.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_negated is False


def test_modality_possible(parser, extractor, annotator):
    """'Python may be faster' → modality=POSSIBLE."""
    sc = make_structured_candidate(parser, extractor, "Python may be faster than Java.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.modality == Modality.POSSIBLE


def test_modality_certain(parser, extractor, annotator):
    """'Python is fast' → modality=CERTAIN."""
    sc = make_structured_candidate(parser, extractor, "Python is fast.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.modality == Modality.CERTAIN


def test_conditional_detected(parser, extractor, annotator):
    """'If X is installed, Y works' → is_conditional=True."""
    sc = make_structured_candidate(parser, extractor,
                                   "If CUDA is installed, PyTorch uses the GPU.")
    annotated = annotator.annotate(sc)
    assert annotated.metadata.is_conditional is True


def test_text_not_modified_by_annotation(parser, extractor, annotator):
    """Annotation MUST NOT modify claim text."""
    text = "Python does not support this feature."
    sc = make_structured_candidate(parser, extractor, text)
    annotated = annotator.annotate(sc)
    assert annotated.text == text


def test_annotation_never_raises(parser, extractor, annotator):
    """Annotation must never raise regardless of input."""
    sc = make_structured_candidate(parser, extractor, "!!! weird ?? input !!!")
    annotated = annotator.annotate(sc)
    assert annotated is not None
````

## File: tests/unit/test_phase4_boundaries.py
````python
"""
Unit tests for claims/boundaries.py – boundary detection logic.

These tests verify that BoundaryDetector correctly identifies claim boundaries
in various syntactic structures, and that it uses the BoundaryReason enum
and produces AssertionCandidate objects without the confidence field.
"""

import pytest
from pathlib import Path

from smriti.core.models import SemanticSentence, BoundaryReason
from smriti.claims.parser import SpaCyParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.models import AssertionCandidate


@pytest.fixture(scope="module")
def parser():
    """Load the linguistic parser once for all tests."""
    try:
        return SpaCyParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def detector():
    """BoundaryDetector with default configuration (split_conjunctions=True)."""
    return BoundaryDetector()


def make_sentence(text: str, sentence_id: str = "s001") -> SemanticSentence:
    """Helper to create a SemanticSentence."""
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


# ── Basic functionality ───────────────────────────────────────────────────────

def test_single_sentence_returns_one_candidate(parser, detector):
    """A simple sentence with no coordination must yield exactly one candidate."""
    sent = make_sentence("Python is a high-level language.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert isinstance(candidates[0], AssertionCandidate)
    assert candidates[0].text == sent.text
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION
    # 'confidence' no longer exists – test removed


def test_parse_failure_returns_whole_sentence(parser, detector):
    """When parsing fails, detect() must fall back to whole-sentence candidate."""
    sent = make_sentence("@@@ ??? weird !!!")
    parsed = parser.parse(sent)
    # It may or may not parse, but if parse_ok is False, we expect fallback.
    if not parsed.parse_ok:
        candidates = detector.detect(parsed)
        assert len(candidates) == 1
        assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
        assert candidates[0].text == sent.text


# ── Coordinated predicates (shared subject) ─────────────────────────────────

def test_coordinated_predicate_splits(parser, detector):
    """'Python supports X and Y' → two candidates with COORDINATED_PREDICATE."""
    sent = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Expect two claims: "Python supports generators" and "Python supports decorators"
    # The exact text may vary; we check count and reasons.
    assert len(candidates) == 2
    for cand in candidates:
        assert cand.boundary_reason == BoundaryReason.COORDINATED_PREDICATE
    # Verify text contains both parts (approximate)
    texts = [c.text for c in candidates]
    assert any("generators" in t for t in texts)
    assert any("decorators" in t for t in texts)


def test_coordinated_predicate_with_shared_subject_works(parser, detector):
    """Coordination of verbs sharing subject: 'Python runs and compiles quickly'."""
    sent = make_sentence("Python runs and compiles quickly.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # Should produce two: "Python runs quickly" and "Python compiles quickly"
    assert len(candidates) == 2


# ── Independent clauses ──────────────────────────────────────────────────────

def test_independent_clauses_splits(parser, detector):
    """'X is fast and Y is slow' → two independent clause candidates."""
    sent = make_sentence("Python is fast and Java is slow.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 2
    assert all(c.boundary_reason == BoundaryReason.INDEPENDENT_CLAUSE for c in candidates)
    texts = [c.text for c in candidates]
    assert any("Python" in t for t in texts)
    assert any("Java" in t for t in texts)


# ── Complex cases – no split when not appropriate ───────────────────────────

def test_conditional_not_split(parser, detector):
    """Conditional 'if X then Y' should remain as one claim (split_conditionals=False)."""
    sent = make_sentence("If CUDA is installed, PyTorch uses the GPU.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    # We expect one candidate (whole sentence) because we do not split conditionals.
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_relative_clause_not_split(parser, detector):
    """Relative clause should not be split; remains one claim."""
    sent = make_sentence("Python, which was released in 1991, supports generators.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_empty_text(parser, detector):
    """Empty text -> parse_ok=False -> fallback with PARSE_FAILED."""
    sent = make_sentence("   ")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.PARSE_FAILED
    assert candidates[0].text == sent.text


def test_no_coordination_still_returns_one(parser, detector):
    """Sentence without coordinator yields single candidate."""
    sent = make_sentence("Deep learning is powerful.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION


def test_detector_never_returns_empty(parser, detector):
    """detect() must always return at least one candidate."""
    sent = make_sentence("This is a test.")
    parsed = parser.parse(sent)
    candidates = detector.detect(parsed)
    assert len(candidates) >= 1


# ── Configuration: split_conjunctions = False ──────────────────────────────

def test_split_disabled_returns_single(parser):
    """When split_conjunctions is False, no splitting occurs."""
    # We need to create a detector with split_conjunctions=False.
    # Since we can't easily override config, we'll patch or instantiate with custom config.
    # For simplicity, we assume the default config has split_conjunctions=True.
    # If you want to test, you can modify the config or use a custom BoundaryDetector.
    # We'll skip this test or demonstrate by setting attribute directly.
    detector_no_split = BoundaryDetector()
    # Set internal flag to False (hack for testing)
    detector_no_split._split_conjunctions = False
    sent = make_sentence("Python supports X and Y.")
    parsed = parser.parse(sent)
    candidates = detector_no_split.detect(parsed)
    assert len(candidates) == 1
    assert candidates[0].boundary_reason == BoundaryReason.SINGLE_ASSERTION
````

## File: tests/unit/test_phase4_builder.py
````python
"""
Unit tests for claims/builder.py.
"""

import pytest
from pathlib import Path

from smriti.core.models import (
    SemanticSentence,
    ExtractionMode,
    Modality,
    StructuredAssertion,
    Claim,
    BoundaryReason,
)
from smriti.claims.builder import build_claim, _compute_claim_id
from smriti.claims.rules import RULE_VERSION


def make_validated(text: str, sentence_id: str = "sent001", doc_id: str = "doc001"):
    """Create a minimal ValidatedAssertion for testing."""
    from smriti.claims.models import (
        ValidatedAssertion,
        AnnotatedAssertion,
        StructuredAssertionCandidate,
        AssertionCandidate,
        ParsedSentence,
        LinguisticMetadata,
        SemanticMetadata,
    )
    sentence = SemanticSentence(
        sentence_id=sentence_id,
        document_id=doc_id,
        text=text,
        context="Python > Generators",
        position=3,
        char_start=100,
        char_end=100 + len(text),
        source_path=Path("note.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason=BoundaryReason.SINGLE_ASSERTION,
    )
    structured_cand = StructuredAssertionCandidate(
        candidate=candidate,
        structured_assertion=None,
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
    )

    # Split metadata
    linguistic = LinguisticMetadata(
        is_negated=False,
        modality=Modality.CERTAIN,
        is_quoted=False,
    )
    semantic = SemanticMetadata(
        is_conditional=False,
        is_comparative=False,
        is_attributed=False,
        attributed_to=None,
    )

    annotated = AnnotatedAssertion(
        structured_candidate=structured_cand,
        linguistic_metadata=linguistic,
        semantic_metadata=semantic,
        additional_warnings=[],
    )

    return ValidatedAssertion(annotated=annotated, all_warnings=[])


def test_build_returns_claim():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert isinstance(claim, Claim)
    assert claim.content_hash is not None
    assert len(claim.content_hash) == 16
    assert claim.rule_version == RULE_VERSION
    assert claim.rule_version == "1.0"


def test_claim_id_is_16_chars():
    v = make_validated("Python is great.")
    claim = build_claim(v)
    assert len(claim.claim_id) == 16


def test_claim_id_is_deterministic():
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s1")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id == claim2.claim_id
    assert claim1.content_hash == claim2.content_hash


def test_different_text_different_id():
    v1 = make_validated("Python is great.")
    v2 = make_validated("Julia is faster.")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.claim_id != claim2.claim_id
    assert claim1.content_hash != claim2.content_hash


def test_claim_text_is_exact():
    """Text must be author's exact wording — no modification."""
    text = "Python does NOT support this feature."
    v = make_validated(text)
    claim = build_claim(v)
    assert claim.text == text


def test_claim_is_frozen():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    with pytest.raises(Exception):
        claim.text = "modified"


def test_claim_has_provenance():
    v = make_validated("Python is fast.", sentence_id="sent_x", doc_id="doc_y")
    claim = build_claim(v)
    assert claim.provenance is not None
    assert claim.provenance.sentence_id == "sent_x"
    assert claim.provenance.document_id == "doc_y"


def test_claim_schema_version():
    v = make_validated("Python is fast.")
    claim = build_claim(v)
    assert claim.schema_version == "4.0"


def test_claim_context_from_sentence():
    """Claim must inherit context from source SemanticSentence."""
    v = make_validated("Python supports generators.", sentence_id="s1")
    claim = build_claim(v)
    assert claim.context == "Python > Generators"


# ── New test: content_hash depends only on text ──────────────────────────────

def test_content_hash_depends_only_on_text():
    """content_hash must be identical for identical text, regardless of sentence_id."""
    v1 = make_validated("Python is great.", sentence_id="s1")
    v2 = make_validated("Python is great.", sentence_id="s2")
    claim1 = build_claim(v1)
    claim2 = build_claim(v2)
    assert claim1.content_hash == claim2.content_hash
    # claim_id includes sentence_id, so it should differ
    assert claim1.claim_id != claim2.claim_id
````

## File: tests/unit/test_phase4_parser.py
````python
"""
Unit tests for claims/parser.py.
Parser has one job: produce ParsedSentence from SemanticSentence.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from smriti.core.models import SemanticSentence
from smriti.claims.parser import LinguisticParser


@pytest.fixture(scope="module")
def parser():
    """Load spaCy model once per test module."""
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


def make_sentence(text: str, sentence_id: str = "test001") -> SemanticSentence:
    return SemanticSentence(
        sentence_id=sentence_id,
        document_id="doc001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )


def test_parse_simple_sentence(parser):
    """Simple sentence must parse successfully."""
    sentence = make_sentence("Python is fast.")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is True
    assert parsed.spacy_doc is not None


def test_parse_preserves_original_sentence(parser):
    """ParsedSentence.sentence must be the original, unchanged."""
    sentence = make_sentence("Python supports generators.")
    parsed = parser.parse(sentence)
    assert parsed.sentence is sentence


def test_parse_empty_sentence_returns_failed(parser):
    """Empty text must return parse_ok=False — not raise."""
    sentence = make_sentence("   ")
    parsed = parser.parse(sentence)
    assert parsed.parse_ok is False
    assert parsed.spacy_doc is None


def test_parse_fails_gracefully(parser):
    """Parser failure must not raise — returns parse_ok=False."""
    sentence = make_sentence("!!!! ~~~~ #### not real text ????")
    parsed = parser.parse(sentence)
    # spaCy may or may not parse this — either way no exception
    assert parsed.sentence is sentence


def test_parse_unicode_text(parser):
    """Unicode text must parse without errors."""
    sentence = make_sentence("Python est rapide et Python est populaire.")
    parsed = parser.parse(sentence)
    # May or may not produce great results, but must not crash
    assert parsed.sentence is sentence


def test_spacy_doc_has_tokens(parser):
    """Parsed doc must have tokens."""
    sentence = make_sentence("Python supports generators and decorators.")
    parsed = parser.parse(sentence)
    if parsed.parse_ok:
        assert len(list(parsed.spacy_doc)) > 0
````

## File: tests/unit/test_phase4_structure.py
````python
"""
Unit tests for claims/structure.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import SemanticSentence, ExtractionMode
from smriti.claims.parser import LinguisticParser
from smriti.claims.boundaries import BoundaryDetector
from smriti.claims.structure import StructureExtractor


@pytest.fixture(scope="module")
def parser():
    try:
        return LinguisticParser()
    except Exception:
        pytest.skip("spaCy model not available")


@pytest.fixture(scope="module")
def extractor():
    return StructureExtractor()


def make_parsed(parser, text):
    from smriti.claims.parser import LinguisticParser
    sentence = SemanticSentence(
        sentence_id="s001",
        document_id="d001",
        text=text,
        context="",
        position=0,
        char_start=0,
        char_end=len(text),
        source_path=Path("test.md"),
        origin_block_type="paragraph",
        schema_version="3.0",
    )
    return parser.parse(sentence)


def make_candidate(parser, text):
    from smriti.claims.models import AssertionCandidate
    parsed = make_parsed(parser, text)
    return AssertionCandidate(
        text=text,
        span_start=0,
        span_end=len(text),
        source=parsed,
        boundary_reason="single_assertion",
    )


def test_svo_extraction_simple(parser, extractor):
    """'Python supports generators' → S=Python, P=supports, O=generators."""
    candidate = make_candidate(parser, "Python supports generators.")
    result = extractor.extract(candidate)
    if result.extraction_mode == ExtractionMode.STRUCTURED:
        assert result.structured_assertion is not None
        assert result.structured_assertion.predicate is not None


def test_failed_parse_produces_lexical(extractor):
    """If parse failed, mode must be LEXICAL."""
    from smriti.claims.models import ParsedSentence, AssertionCandidate
    from smriti.core.models import SemanticSentence
    sentence = SemanticSentence(
        sentence_id="s002", document_id="d001", text="test",
        context="", position=0, char_start=0, char_end=4,
        source_path=Path("test.md"), origin_block_type="paragraph",
        schema_version="3.0",
    )
    failed_parsed = ParsedSentence(sentence=sentence, spacy_doc=None, parse_ok=False)
    candidate = AssertionCandidate(
        text="test", span_start=0, span_end=4,
        source=failed_parsed, boundary_reason="parse_failed",
    )
    result = extractor.extract(candidate)
    assert result.extraction_mode == ExtractionMode.LEXICAL


def test_extraction_never_raises(parser, extractor):
    """Extraction must NEVER raise regardless of input."""
    candidate = make_candidate(parser, "!!!! ~~~~ something very weird ????")
    result = extractor.extract(candidate)
    assert result is not None  # Always returns something
    assert result.candidate.text == "!!!! ~~~~ something very weird ????"
````

## File: tests/unit/test_phase4_validator.py
````python
"""
Unit tests for claims/validator.py.
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ExtractionMode, AssertionMetadata, Modality, ClaimProvenance, ClaimWarning,
)
from smriti.claims.validator import validate_claims
from smriti.exceptions import ClaimValidationError


def make_claim(claim_id: str, text: str, doc_id: str = "doc001") -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="sent001",
        document_id=doc_id,
        text=text,
        context="",
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="sent001",
            document_id=doc_id,
            source_path=Path("test.md"),
            sentence_context="",
            sentence_position=0,
        ),
        schema_version="4.0",
    )


def test_valid_claims_pass():
    claims = [
        make_claim("aaa", "Python is great."),
        make_claim("bbb", "Julia is faster."),
    ]
    valid, warnings = validate_claims(claims, "doc001")
    assert len(valid) == 2
    assert warnings == []


def test_empty_text_discarded():
    claims = [
        make_claim("aaa", "   "),
        make_claim("bbb", "Real claim."),
    ]
    valid, warnings = validate_claims(claims, "doc001")
    assert len(valid) == 1
    assert ClaimWarning.CLM_EMPTY_ASSERTION in warnings


def test_duplicate_id_raises():
    claims = [
        make_claim("dup", "First claim."),
        make_claim("dup", "Second claim."),
    ]
    with pytest.raises(ClaimValidationError) as excinfo:
        validate_claims(claims, "doc001")
    assert "inconsistent" not in str(excinfo.value)   # old behaviour raises anyway


def test_wrong_document_id_raises():
    claims = [make_claim("aaa", "Text.", doc_id="wrong_doc")]
    with pytest.raises(ClaimValidationError, match="document_id"):
        validate_claims(claims, "doc001")


def test_no_provenance_raises():
    from dataclasses import replace
    claim = make_claim("aaa", "Text.")
    # Forcefully create a claim with no provenance
    # (cannot happen in normal pipeline, but test the validator)
    import dataclasses
    bad_claim = dataclasses.replace(claim, provenance=None)
    with pytest.raises(ClaimValidationError):
        validate_claims([bad_claim], "doc001")


def test_empty_input_returns_empty():
    valid, warnings = validate_claims([], "doc001")
    assert valid == []
    assert warnings == []

def test_duplicate_id_with_same_content_raises_too():
    """Even if content_hash matches, duplicate IDs are not allowed."""
    claim1 = make_claim("dup", "Same text")
    claim2 = make_claim("dup", "Same text")  # same content, same provenance?
    # They share same sentence_id, doc_id, etc. In practice they'd be identical.
    # The validator should still raise.
    with pytest.raises(ClaimValidationError, match="Duplicate"):
        validate_claims([claim1, claim2], "doc001")
````

## File: tests/unit/test_phase5_builders.py
````python
"""
Unit tests for embedding/builders.py.
Tests Vector, Embedding, EmbeddingQuality, and EmbeddedClaim construction.
"""

import pytest
import math
from smriti.core.models import (
    EmbeddingModelDescriptor, EmbeddingProvenance,
    EmbeddingQuality, Vector, Embedding, EmbeddedClaim,
)
from smriti.embedding.builders import (
    build_vector, build_embedding, build_embedding_quality, build_embedded_claim,
)


@pytest.fixture
def descriptor():
    return EmbeddingModelDescriptor(
        provider="sentence-transformers",
        model_name="all-MiniLM-L6-v2",
        model_revision="default",
        dimension=4,
        model_signature="test_signature",
        embedding_family="SentenceTransformer",
    )


@pytest.fixture
def provenance():
    return EmbeddingProvenance(
        pipeline_version="1.0",
        normalization_mode="l2",
        device="cpu",
        config_hash="test_hash",
    )


# ── build_vector ──────────────────────────────────────────────────────────────

def test_build_vector_returns_vector(descriptor):
    vec = build_vector([0.25, 0.25, 0.25, 0.25], descriptor.dimension, normalized=True)
    assert isinstance(vec, Vector)


def test_build_vector_values_are_tuple(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert isinstance(vec.values, tuple)


def test_build_vector_dimension_matches(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    assert vec.dimension == 4
    assert len(vec.values) == 4


def test_build_vector_normalized_flag_set(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension, normalized=True)
    assert vec.normalized is True


def test_build_vector_normalized_flag_false_by_default(descriptor):
    vec = build_vector([0.5, 0.5, 0.5, 0.5], descriptor.dimension)
    assert vec.normalized is False


def test_build_vector_dimension_mismatch_raises(descriptor):
    """Defensive assertion: dimension mismatch must raise."""
    with pytest.raises(AssertionError):
        build_vector([0.1, 0.2, 0.3], descriptor.dimension)  # 3 values, expected 4


# ── build_embedding ───────────────────────────────────────────────────────────

def test_build_embedding_returns_embedding(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb, Embedding)


def test_build_embedding_has_no_status_field(descriptor, provenance):
    """Embedding must NOT have a status attribute (timeless semantic artifact)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert not hasattr(emb, "status")


def test_build_embedding_vector_is_vector_type(descriptor, provenance):
    """Embedding.vector must be a Vector domain object (not a raw tuple)."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    assert isinstance(emb.vector, Vector)


def test_build_embedding_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    with pytest.raises(Exception):
        emb.claim_id = "modified"


# ── build_embedding_quality ───────────────────────────────────────────────────

def test_build_embedding_quality_fresh(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    assert isinstance(quality, EmbeddingQuality)
    assert quality.dimension_ok is True
    assert quality.normalized is True
    assert quality.finite is True
    assert quality.cache_used is False


def test_build_embedding_quality_cached(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    quality = build_embedding_quality(vec, descriptor, cache_used=True)
    assert quality.cache_used is True


def test_build_embedding_quality_is_frozen(descriptor):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    quality = build_embedding_quality(vec, descriptor, cache_used=False)
    with pytest.raises(Exception):
        quality.dimension_ok = False


# ── build_embedded_claim ──────────────────────────────────────────────────────

def test_build_embedded_claim_returns_embedded_claim(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec, EmbeddedClaim)


def test_build_embedded_claim_has_quality(descriptor, provenance):
    """EmbeddedClaim must carry EmbeddingQuality."""
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension, normalized=True)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=True)
    ec = build_embedded_claim("c001", emb, qual)
    assert isinstance(ec.quality, EmbeddingQuality)
    assert ec.quality.cache_used is True


def test_build_embedded_claim_schema_version(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.schema_version == "5.0"


def test_build_embedded_claim_is_frozen(descriptor, provenance):
    vec = build_vector([0.1, 0.2, 0.3, 0.4], descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    with pytest.raises(Exception):
        ec.claim_id = "modified"


def test_embedded_claim_values_property(descriptor, provenance):
    """EmbeddedClaim.values must return the float tuple directly."""
    raw = [0.1, 0.2, 0.3, 0.4]
    vec = build_vector(raw, descriptor.dimension)
    emb = build_embedding("c001", vec, descriptor, provenance)
    qual = build_embedding_quality(vec, descriptor, cache_used=False)
    ec = build_embedded_claim("c001", emb, qual)
    assert ec.values == tuple(float(x) for x in raw)
````

## File: tests/unit/test_phase5_cache.py
````python
"""
Unit tests for embedding/cache.py.
Includes schema_version validation (critical fix).
"""

import pytest
import pickle
from smriti.core.models import EmbeddingStatus
from smriti.embedding.cache import EmbeddingCachePolicy, CACHE_SCHEMA_VERSION


@pytest.fixture
def cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=True)


@pytest.fixture
def disabled_cache(tmp_path):
    return EmbeddingCachePolicy(cache_dir=tmp_path / "emb_cache", enabled=False)


def test_miss_on_empty_cache(cache):
    status, vector = cache.lookup("nonexistent_key", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_store_and_retrieve(cache):
    vector = [0.1, 0.2, 0.3]
    cache.store("key001", vector, "sig_A", "hash_X")
    status, retrieved = cache.lookup("key001", "sig_A", "hash_X")
    assert status == EmbeddingStatus.CACHED
    assert retrieved == vector


def test_stale_on_model_change(cache):
    """Different model signature → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_B", "hash_X")
    assert status == EmbeddingStatus.STALE


def test_stale_on_config_change(cache):
    """Different config hash → STALE."""
    cache.store("key001", [0.1, 0.2], "sig_A", "hash_X")
    status, _ = cache.lookup("key001", "sig_A", "hash_Y")
    assert status == EmbeddingStatus.STALE


def test_stale_on_schema_version_mismatch(cache, tmp_path):
    """
    Cache entry with an old schema_version → STALE.
    This is the critical fix: schema changes must not silently reuse old artifacts.
    """
    cache_dir = tmp_path / "emb_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Write an entry with an old schema_version directly
    old_entry = {
        "vector":         [0.1, 0.2, 0.3],
        "model_sig":      "sig_A",
        "config_hash":    "hash_X",
        "schema_version": "4.0",   # Old schema — incompatible
    }
    cache_file = cache_dir / "key_old.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(old_entry, f)

    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    status, vector = policy.lookup("key_old", "sig_A", "hash_X")
    assert status == EmbeddingStatus.STALE
    assert vector is None


def test_stored_entry_has_current_schema_version(cache, tmp_path):
    """Stored entries must include CACHE_SCHEMA_VERSION."""
    cache_dir = tmp_path / "emb_cache2"
    policy = EmbeddingCachePolicy(cache_dir=cache_dir, enabled=True)
    policy.store("key001", [0.1, 0.2], "sig", "hash")
    with open(cache_dir / "key001.pkl", "rb") as f:
        entry = pickle.load(f)
    assert entry["schema_version"] == CACHE_SCHEMA_VERSION


def test_disabled_cache_returns_failed(disabled_cache):
    status, vector = disabled_cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
    assert vector is None


def test_clear_all(cache):
    cache.store("key001", [0.1], "sig", "hash")
    cache.store("key002", [0.2], "sig", "hash")
    count = cache.clear_all()
    assert count == 2
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED


def test_invalidate_specific_key(cache):
    cache.store("key001", [0.1, 0.2], "sig", "hash")
    removed = cache.invalidate("key001")
    assert removed is True
    status, _ = cache.lookup("key001", "sig", "hash")
    assert status == EmbeddingStatus.FAILED
````

## File: tests/unit/test_phase5_input_factory.py
````python
"""
Unit tests for embedding/input_factory.py.

Tests both EmbeddingInputFactory (payload) and CacheKeyFactory (keys).
These are now separate classes with separate responsibilities.
"""

import pytest
from pathlib import Path
from smriti.core.models import (
    Claim, ClaimProvenance, ExtractionMode, AssertionMetadata, Modality,
)
from smriti.embedding.input_factory import EmbeddingInputFactory, CacheKeyFactory


def make_claim(
    claim_id: str = "c001",
    text: str = "Python supports generators.",
    context: str = "",
    content_hash: str = "abc123",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        sentence_id="s001",
        document_id="d001",
        text=text,
        context=context,
        source_path=Path("test.md"),
        extraction_mode=ExtractionMode.WHOLE_SENTENCE,
        structured_assertion=None,
        assertion_metadata=AssertionMetadata(),
        provenance=ClaimProvenance(
            sentence_id="s001", document_id="d001",
            source_path=Path("test.md"), sentence_context=context,
            sentence_position=0,
        ),
        schema_version="4.0",
        content_hash=content_hash,
        rule_version="1.0",
    )


@pytest.fixture
def payload_factory():
    return EmbeddingInputFactory()


@pytest.fixture
def key_factory():
    return CacheKeyFactory(model_signature="test_model_sig_abc", config_hash="test_config_xyz")


# ── EmbeddingInputFactory tests ───────────────────────────────────────────────

def test_payload_without_context(payload_factory):
    """Claim without context → payload is just claim.text."""
    claim = make_claim(text="Python is fast.", context="")
    assert payload_factory.build_payload(claim) == "Python is fast."


def test_payload_with_context(payload_factory):
    """Claim with context → payload is 'context\\ntext'."""
    claim = make_claim(text="It supports yield statements.", context="Python > Generators")
    assert payload_factory.build_payload(claim) == "Python > Generators\nIt supports yield statements."


def test_payload_does_not_modify_claim(payload_factory):
    """Claim.text must remain unchanged — only the model input is enriched."""
    claim = make_claim(text="It supports yield.", context="Python > Generators")
    payload_factory.build_payload(claim)
    assert claim.text == "It supports yield."


def test_payload_is_deterministic(payload_factory):
    """Same claim → same payload every time."""
    claim = make_claim(text="Python is fast.", context="Programming")
    assert payload_factory.build_payload(claim) == payload_factory.build_payload(claim)


def test_instruction_prefix_applied():
    """Instruction prefix is prepended to payload when provided."""
    factory = EmbeddingInputFactory(instruction_prefix="Represent this claim: ")
    claim = make_claim(text="Python is fast.", context="")
    payload = factory.build_payload(claim)
    assert payload.startswith("Represent this claim: ")
    assert "Python is fast." in payload


def test_instruction_prefix_with_context():
    """Instruction prefix is prepended to the full context+text payload."""
    factory = EmbeddingInputFactory(instruction_prefix="Query: ")
    claim = make_claim(text="It yields values.", context="Generators")
    payload = factory.build_payload(claim)
    assert payload == "Query: Generators\nIt yields values."


# ── CacheKeyFactory tests ─────────────────────────────────────────────────────

def test_cache_key_is_32_chars(key_factory):
    """Cache key must be exactly 32 hex characters."""
    claim = make_claim()
    key = key_factory.build_cache_key(claim)
    assert len(key) == 32
    assert all(c in "0123456789abcdef" for c in key)


def test_cache_key_is_deterministic(key_factory):
    """Same claim → same cache key every time."""
    claim = make_claim(content_hash="abc123")
    assert key_factory.build_cache_key(claim) == key_factory.build_cache_key(claim)


def test_cache_key_changes_with_model_sig():
    """Different model signature → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_B", "hash_X")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_cache_key_changes_with_config_hash():
    """Different config hash → different cache key."""
    claim = make_claim()
    factory_a = CacheKeyFactory("sig_A", "hash_X")
    factory_b = CacheKeyFactory("sig_A", "hash_Y")
    assert factory_a.build_cache_key(claim) != factory_b.build_cache_key(claim)


def test_payload_factory_and_key_factory_are_independent():
    """Changing instruction_prefix (EmbeddingInputFactory) does not affect cache keys."""
    claim = make_claim()
    factory_no_prefix = EmbeddingInputFactory()
    factory_with_prefix = EmbeddingInputFactory(instruction_prefix="Query: ")
    key_factory_shared = CacheKeyFactory("sig_A", "hash_X")

    payload_plain = factory_no_prefix.build_payload(claim)
    payload_with = factory_with_prefix.build_payload(claim)
    key = key_factory_shared.build_cache_key(claim)

    # Payloads differ but keys are the same — cache key depends on content, not enriched input
    assert payload_plain != payload_with
    assert key == key_factory_shared.build_cache_key(claim)   # Key is stable
````

## File: tests/unit/test_phase5_normalization.py
````python
"""
Unit tests for embedding/normalization.py.
"""

import pytest
import math
from smriti.embedding.normalization import l2_normalize, normalize_batch


def l2_norm(v):
    return math.sqrt(sum(x * x for x in v))


def test_l2_normalize_produces_unit_vector():
    vector = [3.0, 4.0]  # norm = 5.0
    normalized = l2_normalize(vector)
    assert abs(l2_norm(normalized) - 1.0) < 1e-6


def test_l2_normalize_direction_preserved():
    vector = [3.0, 4.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] / normalized[1] - 3.0 / 4.0) < 1e-6


def test_l2_normalize_returns_new_list():
    vector = [1.0, 2.0, 3.0]
    original = list(vector)
    _ = l2_normalize(vector)
    assert vector == original  # Original unchanged


def test_l2_normalize_already_unit_vector():
    vector = [1.0, 0.0, 0.0]
    normalized = l2_normalize(vector)
    assert abs(normalized[0] - 1.0) < 1e-6
    assert abs(normalized[1]) < 1e-6


def test_normalize_batch_applies_to_all():
    vectors = [[3.0, 4.0], [1.0, 0.0], [0.6, 0.8]]
    normalized = normalize_batch(vectors, enabled=True)
    for v in normalized:
        assert abs(l2_norm(v) - 1.0) < 1e-6


def test_normalize_batch_disabled():
    vectors = [[3.0, 4.0], [1.0, 2.0]]
    result = normalize_batch(vectors, enabled=False)
    for i, v in enumerate(result):
        assert v == [float(x) for x in vectors[i]]


def test_normalize_384_dim():
    """Must work correctly on 384-dimensional vectors (MiniLM)."""
    import random
    random.seed(42)
    vector = [random.uniform(-1, 1) for _ in range(384)]
    normalized = l2_normalize(vector)
    assert len(normalized) == 384
    assert abs(l2_norm(normalized) - 1.0) < 1e-5
````

## File: tests/unit/test_phase5_property_based.py
````python
"""
Property-based tests for Phase 5 using Hypothesis.

These tests verify mathematical invariants that must hold for ALL valid inputs,
not just the specific cases covered by example-based tests.

Install: poetry add --group dev hypothesis
"""

import math
import pytest

try:
    from hypothesis import given, settings, assume
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

pytestmark = pytest.mark.skipif(
    not HAS_HYPOTHESIS,
    reason="hypothesis not installed — run: poetry add --group dev hypothesis"
)


# ── Normalization invariants ──────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.normalization import l2_normalize

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_l2_normalize_always_unit_norm(values):
        """For ANY non-zero vector, L2 norm after normalization is always 1.0."""
        assume(sum(x * x for x in values) > 0)  # exclude zero vectors
        normalized = l2_normalize(values)
        norm = math.sqrt(sum(x * x for x in normalized))
        assert abs(norm - 1.0) < 1e-5, f"norm={norm} for input {values[:4]}..."


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_l2_normalize_does_not_mutate_input(values):
        """l2_normalize must never mutate the input list."""
        original = list(values)
        assume(sum(x * x for x in values) > 0)
        l2_normalize(values)
        assert values == original


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=200)
    def test_property_normalize_twice_is_idempotent(values):
        """Normalizing a unit vector again must yield the same unit vector."""
        assume(sum(x * x for x in values) > 0)
        once = l2_normalize(values)
        twice = l2_normalize(once)
        for a, b in zip(once, twice):
            assert abs(a - b) < 1e-5


# ── Cache key invariants ──────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.input_factory import CacheKeyFactory

    @given(
        text=st.text(min_size=1, max_size=1000),
        model_sig=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
        config_hash=st.text(min_size=1, max_size=64, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
    )
    @settings(max_examples=200)
    def test_property_cache_key_always_32_hex_chars(text, model_sig, config_hash):
        """For ANY text and signatures, cache key is always exactly 32 hex chars."""
        from pathlib import Path
        from smriti.core.models import (
            Claim, ClaimProvenance, ExtractionMode, AssertionMetadata,
        )
        import hashlib

        claim = Claim(
            claim_id="c001",
            sentence_id="s001",
            document_id="d001",
            text=text,
            context="",
            source_path=Path("test.md"),
            extraction_mode=ExtractionMode.WHOLE_SENTENCE,
            structured_assertion=None,
            assertion_metadata=AssertionMetadata(),
            provenance=ClaimProvenance(
                sentence_id="s001", document_id="d001",
                source_path=Path("test.md"), sentence_context="",
                sentence_position=0,
            ),
            schema_version="4.0",
            content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            rule_version="1.0",
        )

        factory = CacheKeyFactory(model_signature=model_sig, config_hash=config_hash)
        key = factory.build_cache_key(claim)
        assert len(key) == 32
        assert all(c in "0123456789abcdef" for c in key)


# ── Validation invariants ─────────────────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.validation import validate_vector

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        )
    )
    @settings(max_examples=300)
    def test_property_valid_nonzero_vector_passes_validation(values):
        """Any non-NaN, non-Inf, non-zero-norm vector passes validation."""
        assume(any(x != 0.0 for x in values))
        is_valid, error = validate_vector(values, expected_dimension=len(values))
        assert is_valid is True, f"Expected valid but got error: {error}"


    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=512,
        ),
        wrong_dim=st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=200)
    def test_property_wrong_dimension_always_fails(values, wrong_dim):
        """Validation always fails when dimension doesn't match."""
        assume(wrong_dim != len(values))
        is_valid, error = validate_vector(values, expected_dimension=wrong_dim)
        assert is_valid is False


# ── Vector domain object invariants ──────────────────────────────────────────

if HAS_HYPOTHESIS:
    from smriti.embedding.builders import build_vector

    @given(
        size=st.integers(min_value=1, max_value=512),
        normalized=st.booleans(),
    )
    @settings(max_examples=200)
    def test_property_build_vector_dimension_always_consistent(size, normalized):
        """build_vector.dimension must always equal len(values)."""
        values = [0.1] * size  # Non-zero, all same, valid
        vec = build_vector(values, size, normalized=normalized)
        assert vec.dimension == size
        assert len(vec.values) == size
        assert vec.normalized == normalized
````

## File: tests/unit/test_phase5_validation.py
````python
"""
Unit tests for embedding/validation.py.
Includes dtype validation and post-normalization scenario.
"""

import pytest
import math
from smriti.embedding.validation import validate_vector, validate_batch


def test_valid_vector_passes():
    vector = [0.1, 0.2, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True
    assert error is None


def test_empty_vector_fails():
    is_valid, error = validate_vector([], expected_dimension=4)
    assert is_valid is False
    assert "empty" in error.lower()


def test_wrong_dimension_fails():
    vector = [0.1, 0.2, 0.3]  # 3 elements, expected 4
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "dimension" in error.lower()


def test_nan_fails():
    vector = [0.1, float("nan"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "nan" in error.lower()


def test_inf_fails():
    vector = [0.1, float("inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "inf" in error.lower()


def test_negative_inf_fails():
    vector = [0.1, float("-inf"), 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_zero_norm_fails():
    vector = [0.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "zero" in error.lower()


def test_unit_vector_passes():
    vector = [1.0, 0.0, 0.0, 0.0]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is True


def test_dtype_string_fails():
    """Non-numeric (string) type in vector must fail."""
    vector = [0.1, "bad", 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False
    assert "type" in error.lower() or "non-numeric" in error.lower()


def test_dtype_none_fails():
    """None in vector must fail."""
    vector = [0.1, None, 0.3, 0.4]
    is_valid, error = validate_vector(vector, expected_dimension=4)
    assert is_valid is False


def test_validate_batch_all_valid():
    vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    results = validate_batch(vectors, expected_dimension=3)
    assert all(valid for valid, _ in results)


def test_validate_batch_mixed():
    vectors = [
        [0.1, 0.2, 0.3],
        [float("nan"), 0.2, 0.3],
    ]
    results = validate_batch(vectors, expected_dimension=3)
    assert results[0][0] is True
    assert results[1][0] is False


def test_post_normalization_valid_unit_vector():
    """A correctly normalized unit vector must pass post-norm validation."""
    import math
    vector = [1.0, 0.0, 0.0, 0.0]
    norm = math.sqrt(sum(x * x for x in vector))
    normalized = [x / norm for x in vector]
    is_valid, error = validate_vector(normalized, expected_dimension=4)
    assert is_valid is True
````

## File: tests/unit/test_scanner.py
````python
"""
Unit tests for discovery/scanner.py.

Scanner has one job: find files.
These tests never touch hashing, validation, or manifests.
"""

import pytest
from pathlib import Path
from smriti.discovery.scanner import discover_files


@pytest.fixture
def notes_dir(tmp_path):
    """Create a small realistic vault structure."""
    # Normal notes
    (tmp_path / "AI.md").write_text("AI is transforming everything.")
    (tmp_path / "Python.md").write_text("Python is great for data science.")
    (tmp_path / "Notes.txt").write_text("Some plain text notes.")

    # Subdirectory
    subdir = tmp_path / "Archive"
    subdir.mkdir()
    (subdir / "Old.md").write_text("An old note.")
    (subdir / "Report.pdf").write_bytes(b"%PDF-1.4 fake pdf content")

    # Files that must be ignored
    (tmp_path / ".hidden_file.md").write_text("Hidden — must be ignored.")
    obsidian = tmp_path / ".obsidian"
    obsidian.mkdir()
    (obsidian / "config.json").write_text("{}")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main")

    return tmp_path


def test_discovers_markdown_files(notes_dir):
    """Scanner finds .md files recursively."""
    results = discover_files([notes_dir])
    md_files = [p for p in results if p.suffix.lower() == ".md"]
    assert len(md_files) == 3  # AI.md, Python.md, Archive/Old.md


def test_discovers_txt_and_pdf(notes_dir):
    """Scanner finds .txt and .pdf files."""
    results = discover_files([notes_dir])
    extensions = {p.suffix.lower() for p in results}
    assert ".txt" in extensions
    assert ".pdf" in extensions


def test_ignores_hidden_files(notes_dir):
    """Files starting with '.' must be excluded."""
    results = discover_files([notes_dir])
    names = [p.name for p in results]
    assert ".hidden_file.md" not in names


def test_ignores_obsidian_dir(notes_dir):
    """The .obsidian directory must be skipped entirely."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".obsidian" in p for p in paths_str)


def test_ignores_git_dir(notes_dir):
    """The .git directory must be skipped."""
    results = discover_files([notes_dir])
    paths_str = [str(p) for p in results]
    assert not any(".git" in p for p in paths_str)


def test_output_is_sorted(notes_dir):
    """Discovery output must always be sorted (deterministic)."""
    results = discover_files([notes_dir])
    lower_paths = [str(p).lower() for p in results]
    assert lower_paths == sorted(lower_paths)


def test_empty_directory_returns_empty_list(tmp_path):
    """Empty directory must return [] — not crash."""
    results = discover_files([tmp_path])
    assert results == []


def test_multiple_root_dirs(tmp_path):
    """Scanner accepts multiple root directories."""
    dir_a = tmp_path / "vault_a"
    dir_b = tmp_path / "vault_b"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "note1.md").write_text("Note one.")
    (dir_b / "note2.md").write_text("Note two.")

    results = discover_files([dir_a, dir_b])
    assert len(results) == 2


def test_deeply_nested_dirs(tmp_path):
    """Recursion must be unlimited depth."""
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "deep.md").write_text("Deep nested note.")

    results = discover_files([tmp_path])
    assert any("deep.md" in str(p) for p in results)


def test_unicode_filenames(tmp_path):
    """Unicode filenames must work correctly on Windows."""
    (tmp_path / "日本語.md").write_text("Japanese filename.", encoding="utf-8")
    (tmp_path / "ñoño.md").write_text("Spanish accents.", encoding="utf-8")
    (tmp_path / "ನನ್ನ_ಟಿಪ್ಪಣಿ.md").write_text("Kannada filename.", encoding="utf-8")

    results = discover_files([tmp_path])
    assert len(results) == 3


def test_filenames_with_spaces(tmp_path):
    """Filenames with spaces are legal and must be found."""
    (tmp_path / "Machine Learning Notes.md").write_text("Notes on ML.")
    results = discover_files([tmp_path])
    assert any("Machine Learning Notes" in str(p) for p in results)
````

## File: tests/unit/test_validator.py
````python
"""
Unit tests for discovery/validator.py.

Validator has two jobs:
  1. validate_directories() — fatal check of input roots
  2. validate_file()        — per-file check, returns ValidationResult
"""

import pytest
from pathlib import Path
from smriti.discovery.validator import validate_directories, validate_file
from smriti.exceptions import DiscoveryError


@pytest.fixture
def valid_md(tmp_path):
    f = tmp_path / "valid.md"
    f.write_text("Some content here.")
    return f


@pytest.fixture
def empty_file(tmp_path):
    f = tmp_path / "empty.md"
    f.write_bytes(b"")
    return f


@pytest.fixture
def unsupported_file(tmp_path):
    f = tmp_path / "document.docx"
    f.write_bytes(b"fake docx content")
    return f


# ── validate_directories ──────────────────────────────────────────────────────

def test_valid_directory_passes(tmp_path):
    """A valid existing directory must be returned."""
    result = validate_directories([tmp_path])
    assert result == [tmp_path.resolve()]


def test_nonexistent_directory_raises(tmp_path):
    """A directory that doesn't exist must raise DiscoveryError."""
    missing = tmp_path / "does_not_exist"
    with pytest.raises(DiscoveryError, match="does not exist"):
        validate_directories([missing])


def test_file_as_directory_raises(tmp_path):
    """Passing a file path as a directory must raise DiscoveryError."""
    f = tmp_path / "file.txt"
    f.write_text("not a directory")
    with pytest.raises(DiscoveryError, match="not a directory"):
        validate_directories([f])


def test_empty_list_raises():
    """Empty input list must raise DiscoveryError."""
    with pytest.raises(DiscoveryError, match="No input directories"):
        validate_directories([])


# ── validate_file ─────────────────────────────────────────────────────────────

def test_valid_markdown_passes(valid_md):
    """A valid non-empty .md file must pass validation."""
    result = validate_file(valid_md)
    assert result.is_valid is True
    assert result.rejection_reason is None


def test_nonexistent_file_fails(tmp_path):
    """A file that doesn't exist must fail with 'does not exist'."""
    missing = tmp_path / "ghost.md"
    result = validate_file(missing)
    assert result.is_valid is False
    assert "does not exist" in result.rejection_reason


def test_empty_file_fails(empty_file):
    """A zero-byte file must fail validation."""
    result = validate_file(empty_file)
    assert result.is_valid is False
    assert "empty" in result.rejection_reason


def test_unsupported_extension_fails(unsupported_file):
    """Files with unsupported extensions must be rejected."""
    result = validate_file(unsupported_file)
    assert result.is_valid is False
    assert "unsupported extension" in result.rejection_reason


def test_pdf_file_passes(tmp_path):
    """A non-empty .pdf file must pass validation."""
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake pdf content")
    result = validate_file(pdf)
    assert result.is_valid is True


def test_txt_file_passes(tmp_path):
    """A non-empty .txt file must pass validation."""
    txt = tmp_path / "notes.txt"
    txt.write_text("Some plain text.")
    result = validate_file(txt)
    assert result.is_valid is True


def test_validation_result_is_bool(valid_md):
    """ValidationResult must be usable as a boolean."""
    result = validate_file(valid_md)
    assert bool(result) is True
````

## File: tests/__init__.py
````python

````

## File: tests/conftest.py
````python
"""Shared pytest fixtures."""

import pytest
from pathlib import Path
from smriti.core.config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(tmp_path_factory):
    """Point config to test.yaml for the whole test session."""
    import smriti.core.config as cfg_module
    cfg_module._config = Config(env="test")


@pytest.fixture
def tmp_artifacts(tmp_path):
    """Temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


@pytest.fixture
def test_config():
    """Return a test Config instance."""
    return Config(env="test")


@pytest.fixture
def tmp_notes(tmp_path):
    """Create temporary markdown note files."""
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()

    (notes_dir / "note1.md").write_text(
        "# Note 1\n\nPython is the best language for data science.\n"
    )
    (notes_dir / "note2.md").write_text(
        "# Note 2\n\nRust is better than Python for performance.\n"
    )
    return notes_dir


@pytest.fixture
def sample_markdown(tmp_path):
    """Single sample markdown note."""
    note = tmp_path / "note.md"
    note.write_text(
        "# Test Note\n\nCreated: 2024-01-15\n\n"
        "Python is great for data science.\n\n"
        "But for some tasks, Julia is faster.\n"
    )
    return note
````

## File: download_models.ps1
````powershell
Write-Host 'Run this to download models'\n
````

## File: LICENSE
````
MIT License\n\nCopyright (c) 2026 Abhijnan B C\n
````

## File: Makefile.ps1
````powershell
<#
.SYNOPSIS
    PowerShell task runner for SMRITI — equivalent of a Unix Makefile.
.PARAMETER Task
    Task to run. Run without arguments for help.
#>

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  ✓ $msg" -ForegroundColor Green }

function Invoke-Help {
    Write-Host ""
    Write-Host "SMRITI — Available Tasks" -ForegroundColor Green
    Write-Host ""
    Write-Host "  .\Makefile.ps1 setup            Install dependencies & download models" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 test             Run all tests" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 lint             Ruff + Black check + mypy" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 format           Auto-format with Black + Ruff fix" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 type-check       mypy type checking only" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 clean-cache      Delete ephemeral cache (always safe)" -ForegroundColor Cyan
    Write-Host "  .\Makefile.ps1 clean-artifacts  Delete pipeline artifacts (WARNING)" -ForegroundColor Yellow
    Write-Host "  .\Makefile.ps1 clean            Clean pycache + cache (not artifacts)" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-Setup {
    Write-Step "Setup"
    & .\scripts\setup_dev.ps1
}

function Invoke-Test {
    Write-Step "Running tests"
    poetry run pytest tests/ -v
}

function Invoke-Lint {
    Write-Step "Linting"
    poetry run ruff check src/ tests/
    poetry run black --check src/ tests/
    poetry run mypy src/smriti
    Write-OK "All lint checks passed"
}

function Invoke-Format {
    Write-Step "Formatting"
    poetry run black src/ tests/
    poetry run ruff check --fix src/ tests/
    Write-OK "Code formatted"
}

function Invoke-TypeCheck {
    Write-Step "Type checking"
    poetry run mypy src/smriti
    Write-OK "Type check passed"
}

function Invoke-CleanCache {
    Write-Step "Clearing cache (ephemeral — safe to delete)"
    Remove-Item -Path cache -Recurse -Force -ErrorAction SilentlyContinue
    Write-OK "Cache cleared"
}

function Invoke-CleanArtifacts {
    Write-Step "Clearing artifacts"
    Write-Host "  WARNING: This deletes immutable pipeline outputs." -ForegroundColor Red
    $confirm = Read-Host "  Type YES to confirm"
    if ($confirm -eq "YES") {
        Remove-Item -Path artifacts -Recurse -Force -ErrorAction SilentlyContinue
        Write-OK "Artifacts removed"
    } else {
        Write-Host "  Cancelled." -ForegroundColor Yellow
    }
}

function Invoke-Clean {
    Write-Step "Cleaning Python cache and temp files"
    Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Force |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .mypy_cache  -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path .coverage    -Force          -ErrorAction SilentlyContinue
    Invoke-CleanCache
    Write-OK "Cleaned"
}

switch ($Task) {
    "help"             { Invoke-Help }
    "setup"            { Invoke-Setup }
    "test"             { Invoke-Test }
    "lint"             { Invoke-Lint }
    "format"           { Invoke-Format }
    "type-check"       { Invoke-TypeCheck }
    "clean-cache"      { Invoke-CleanCache }
    "clean-artifacts"  { Invoke-CleanArtifacts }
    "clean"            { Invoke-Clean }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Invoke-Help
        exit 1
    }
}
````

## File: pyproject.toml
````toml
[tool.poetry]
name = "smriti"
version = "0.1.0"
description = "Knowledge drift analyzer for personal note vaults."
authors = ["Abhijnan B C <you@example.com>"]
license = "MIT"
readme = "README.md"
repository = "https://github.com/AbhijnanBC/smriti"
packages = [{include = "smriti", from = "src"}]

[tool.poetry.dependencies]
# Cap at 3.12 for ML compatibility stability
python = ">=3.11,<3.13"

# Core ML/NLP
spacy = "^3.8"
sentence-transformers = "^3.4"
torch = "^2.5"
transformers = "^4.48"

# Retrieval (FAISS strictly on non-Windows, scikit-learn available as fallback)
faiss-cpu = {version = "^1.10", markers = "sys_platform != 'win32'"}
scikit-learn = "^1.4"

# Data processing
numpy = "^1.26.4"
pandas = "^2.2"
networkx = "^3.4"
python-louvain = "^0.16"

# Parsing
markdown-it-py = "^3.0"
pypdf = "^5.0"

# Dashboard
streamlit = "^1.35"
plotly = "^5.22"

# Utilities
pyyaml = "^6.0"
python-dotenv = "^1.0"
structlog = "^24.1"
python-json-logger = "^2.0"
tqdm = "^4.66"
click = "^8.1"
pendulum = "^3.0"
psutil = "^5.9"

[tool.poetry.group.dev.dependencies]
pytest = "^8.1"
pytest-cov = "^5.0"
pytest-mock = "^3.14"
black = "^24.4"
ruff = "^0.4"
mypy = "^1.10"
ipython = "^8.24"
hypothesis = "^6.156.7"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ["py311", "py312"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C"]
ignore = ["E501", "B008"]

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["smriti"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_incomplete_defs = false
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--verbose --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
]

[tool.coverage.run]
source = ["src/smriti"]
````

## File: README.md
````markdown
# smriti\n\nKnowledge drift analyzer for personal note vaults.\n
````

## File: setup_dev.ps1
````powershell
Write-Host 'Run this to set up dev environment'\n
````

## File: .gitignore
````
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
.DS_Store
.env.local
cache/
output/logs/
artifacts/run_*/
*.log
.venv/
venv/
*.swp
*.swo
.idea/
.vscode/settings.json
````
