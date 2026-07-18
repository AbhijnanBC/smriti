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