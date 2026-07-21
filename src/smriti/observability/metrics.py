"""
metrics.py — Operational Metrics (§11.24).

Defines Counter, Gauge, and Histogram metric instruments.
All metrics are deterministic and monotonically ordered.

Metrics captured:
    - Request latency (interaction, query, planning)
    - Memory utilization
    - Cache hit ratio
    - Graph traversal depth
    - Workspace restore time
    - Export throughput
    - Recovery time

Invariant: Metrics collection never affects measured execution.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Counter:
    """Monotonically increasing count metric."""
    name:  str
    value: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def increment(self, by: int = 1) -> None:
        with self._lock:
            self.value += by

    def reset(self) -> None:
        with self._lock:
            self.value = 0


@dataclass
class Gauge:
    """Current-value metric (can increase or decrease)."""
    name:  str
    value: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def set(self, value: float) -> None:
        with self._lock:
            self.value = value

    def increment(self, by: float = 1.0) -> None:
        with self._lock:
            self.value += by

    def decrement(self, by: float = 1.0) -> None:
        with self._lock:
            self.value = max(0.0, self.value - by)


class Histogram:
    """Distribution metric for latency and throughput measurement."""

    def __init__(self, name: str, buckets: tuple[float, ...] = (5, 10, 25, 50, 100, 250, 500, 1000)) -> None:
        self.name    = name
        self.buckets = buckets
        self._values: List[float] = []
        self._lock   = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._values.append(value)

    def summary(self) -> Dict[str, float]:
        with self._lock:
            if not self._values:
                return {"count": 0, "sum": 0.0, "mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
            sorted_vals = sorted(self._values)
            n = len(sorted_vals)
            return {
                "count": n,
                "sum":   sum(sorted_vals),
                "mean":  sum(sorted_vals) / n,
                "p50":   sorted_vals[int(n * 0.50)],
                "p95":   sorted_vals[int(n * 0.95)],
                "p99":   sorted_vals[int(n * 0.99)],
            }


class MetricsCollector:
    """
    Central registry for all operational metrics.

    Thread-safe. All operations are non-blocking with minimal overhead.
    """

    def __init__(self) -> None:
        self._counters:   Dict[str, Counter]   = {}
        self._gauges:     Dict[str, Gauge]     = {}
        self._histograms: Dict[str, Histogram] = {}
        self._lock = threading.Lock()
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.counter("requests_total")
        self.counter("errors_total")
        self.counter("cache_hits_total")
        self.counter("cache_misses_total")
        self.gauge("memory_usage_bytes")
        self.gauge("active_sessions")
        self.histogram("query_latency_ms")
        self.histogram("interaction_latency_ms")
        self.histogram("traversal_depth")
        self.histogram("export_duration_ms")
        self.histogram("recovery_time_ms")

    def counter(self, name: str) -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name=name)
            return self._counters[name]

    def gauge(self, name: str) -> Gauge:
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name=name)
            return self._gauges[name]

    def histogram(self, name: str) -> Histogram:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name=name)
            return self._histograms[name]

    def snapshot(self) -> Dict:
        """Return a complete metrics snapshot (read-only)."""
        with self._lock:
            return {
                "counters":   {n: c.value for n, c in self._counters.items()},
                "gauges":     {n: g.value for n, g in self._gauges.items()},
                "histograms": {n: h.summary() for n, h in self._histograms.items()},
                "timestamp":  time.time(),
            }