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