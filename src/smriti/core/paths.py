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