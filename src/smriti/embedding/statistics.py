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

from smriti.core.models import Phase5Stats
from smriti.embedding.models import EmbeddingStatus


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
        self._batch_sizes: list[int] = []
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
        avg_batch = sum(self._batch_sizes) / len(self._batch_sizes) if self._batch_sizes else 0.0

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
        import os

        import psutil

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
