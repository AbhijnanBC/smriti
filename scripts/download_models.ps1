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