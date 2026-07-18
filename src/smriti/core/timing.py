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