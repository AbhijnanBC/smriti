"""
model_provenance.py — Real HuggingFace model revision/checkpoint resolution.

Replaces hardcoded placeholder provenance values (model_revision="default",
checkpoint_sha="") with the actual commit hash of the locally cached model
snapshot, so that EmbeddingModelDescriptor / InferenceMetadata capture
genuine reproducibility provenance instead of a fabricated constant.

Resolution strategy (best-effort, never raises — always returns a string):
    1. Read `_commit_hash` off the loaded transformers model's config object.
       `transformers` sets this automatically when a model is loaded from
       the local HF cache or the hub (see
       transformers.configuration_utils.PretrainedConfig.from_pretrained).
    2. Fall back to `huggingface_hub.scan_cache_dir()`, matching the repo_id
       and reading that revision's commit_hash directly off the local cache
       index — reliable because HF caches snapshots keyed by commit SHA
       under `~/.cache/huggingface/hub/models--<org>--<name>/snapshots/<sha>/`.
    3. If neither is available (offline, cache cleared, custom path), return
       "unknown" rather than fabricating a value.

checkpoint_sha is a second, independent provenance signal: the SHA256 of
the model's actual weight file on disk. It is content-addressable in a way
the git revision is not — it changes if and only if the weight bytes
change, whereas a repo commit could touch only metadata/README files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

_WEIGHT_FILE_CANDIDATES = ("model.safetensors", "pytorch_model.bin")


def resolve_hf_revision(hf_config: object | None, model_name: str) -> str:
    """
    Resolve the real HF commit hash for a loaded transformers model.

    Args:
        hf_config: The `.config` object of the loaded transformers model
                   (e.g. `sentence_transformer[0].auto_model.config` or
                   `cross_encoder.model.config`), or None if unavailable.
        model_name: The HF repo id (e.g. "sentence-transformers/all-MiniLM-L6-v2").

    Returns:
        The commit SHA if it can be determined, else "unknown".
    """
    commit_hash = getattr(hf_config, "_commit_hash", None)
    if commit_hash:
        return commit_hash

    try:
        from huggingface_hub import scan_cache_dir

        cache_info = scan_cache_dir()
        for repo in cache_info.repos:
            if repo.repo_id != model_name:
                continue
            for revision in repo.revisions:
                if revision.commit_hash:
                    return revision.commit_hash
    except Exception:
        pass

    return "unknown"


def resolve_checkpoint_sha(model_name: str, revision: str) -> str:
    """
    Best-effort content-addressable checksum of the model's primary weight
    file, computed from the locally cached snapshot.

    Returns "" if the local HF cache can't be located, the revision's
    snapshot has no recognized weight file, or hashing fails for any
    reason — never fabricates a value.
    """
    try:
        from huggingface_hub import scan_cache_dir

        cache_info = scan_cache_dir()
        for repo in cache_info.repos:
            if repo.repo_id != model_name:
                continue
            for hf_revision in repo.revisions:
                if revision and revision != "unknown" and hf_revision.commit_hash != revision:
                    continue
                snapshot_dir = Path(hf_revision.snapshot_path)
                for candidate in _WEIGHT_FILE_CANDIDATES:
                    weight_path = snapshot_dir / candidate
                    if weight_path.is_file():
                        return _sha256_file(weight_path)
    except Exception:
        pass

    return ""


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
