"""
governance.py — Resource governance for Phase 6 discovery pipeline.

Prevents runaway resource consumption on large vaults or misconfigured runs.

Limits enforced:
    max_pairs:        Maximum number of candidate pairs to process through NLI.
    max_gpu_memory_gb: Maximum GPU memory allocation (0 = CPU only).
    max_batch_size:   Maximum NLI batch size.
    timeout_seconds:  Maximum wall-clock time for the entire Phase 6 run.
    cancel_on_limit:  If True, abort when any limit is exceeded. If False, truncate.

Rules:
    ✅ Limits read from config (never hard-coded)
    ✅ Truncation is deterministic (sorted by cosine_similarity desc)
    ✅ Resource violations are logged and raised as ResourceLimitExceeded
    ❌ Never modifies evidence or relationships
"""

from __future__ import annotations

import time
from typing import List, Optional
import structlog

from smriti.core.config import get_config
from smriti.core.models import CandidatePair
from smriti.exceptions import ResourceLimitExceeded

logger = structlog.get_logger(__name__)


class ResourceLimits:
    """Holds all resource limits for one Phase 6 run."""

    def __init__(self) -> None:
        config = get_config()
        gov_cfg = config.get("resource_governance", {})

        self.max_pairs: int = gov_cfg.get("max_pairs", 100_000)
        self.max_gpu_memory_gb: float = gov_cfg.get("max_gpu_memory_gb", 0.0)
        self.max_batch_size: int = gov_cfg.get("max_batch_size", 64)
        self.timeout_seconds: float = gov_cfg.get("timeout_seconds", 3600.0)
        self.cancel_on_limit: bool = gov_cfg.get("cancel_on_limit", False)


class ResourceGovernor:
    """
    Enforces resource limits during Phase 6.
    Instantiate once per run; call check_* methods at critical points.
    """

    def __init__(self, limits: Optional[ResourceLimits] = None) -> None:
        self._limits = limits or ResourceLimits()
        self._start_time = time.monotonic()
        logger.info(
            "resource governor initialized",
            max_pairs=self._limits.max_pairs,
            timeout_seconds=self._limits.timeout_seconds,
            cancel_on_limit=self._limits.cancel_on_limit,
        )

    def enforce_pair_limit(
        self,
        candidates: List[CandidatePair],
    ) -> List[CandidatePair]:
        """
        Enforce max_pairs limit on the candidate list.

        If cancel_on_limit=True and limit exceeded: raises ResourceLimitExceeded.
        If cancel_on_limit=False: returns the top max_pairs by cosine_similarity.
        """
        if len(candidates) <= self._limits.max_pairs:
            return candidates

        if self._limits.cancel_on_limit:
            raise ResourceLimitExceeded(
                f"Candidate pairs ({len(candidates)}) exceeded max_pairs "
                f"({self._limits.max_pairs}). Aborting. "
                f"Increase resource_governance.max_pairs or reduce top_k."
            )

        logger.warning(
            "pair limit exceeded, truncating",
            total=len(candidates),
            limit=self._limits.max_pairs,
        )
        # Truncate to top pairs by cosine similarity (deterministic)
        sorted_candidates = sorted(
            candidates, key=lambda c: c.cosine_similarity, reverse=True
        )
        return sorted_candidates[: self._limits.max_pairs]

    def check_timeout(self) -> None:
        """
        Check if the timeout has been exceeded.
        Raises ResourceLimitExceeded if so.
        """
        elapsed = time.monotonic() - self._start_time
        if elapsed > self._limits.timeout_seconds:
            raise ResourceLimitExceeded(
                f"Phase 6 timeout exceeded: {elapsed:.1f}s > "
                f"{self._limits.timeout_seconds:.1f}s. "
                f"Increase resource_governance.timeout_seconds or reduce vault size."
            )

    def clamp_batch_size(self, requested: int) -> int:
        """Return min(requested, max_batch_size)."""
        clamped = min(requested, self._limits.max_batch_size)
        if clamped < requested:
            logger.warning(
                "batch size clamped by resource governor",
                requested=requested, clamped=clamped,
            )
        return clamped