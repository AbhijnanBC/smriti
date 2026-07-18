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