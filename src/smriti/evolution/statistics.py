"""statistics.py — Phase 7 execution telemetry. Observes. Never influences."""

from __future__ import annotations

import time
from smriti.core.models import Phase7Stats


class Phase7StatsCollector:
    """Mutable statistics accumulator for Phase 7."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._construction_start: float | None = None
        self._construction_end: float | None = None
        self._enrichment_start: float | None = None
        self._enrichment_end: float | None = None
        self._input_relationships = 0
        self._filtered = 0
        self._nodes = 0
        self._edges = 0
        self._partitions = 0
        self._contradiction_boundaries = 0
        self._evolution_chains = 0
        self._unresolved = 0
        self._validation_passed = False

    def record_input(self, total: int, filtered: int) -> None:
        self._input_relationships = total
        self._filtered = filtered

    def record_construction_start(self) -> None:
        self._construction_start = time.monotonic()

    def record_construction_end(self, nodes: int, edges: int) -> None:
        self._construction_end = time.monotonic()
        self._nodes = nodes
        self._edges = edges

    def record_enrichment_start(self) -> None:
        self._enrichment_start = time.monotonic()

    def record_enrichment_end(
        self, partitions: int, contradiction_boundaries: int,
        evolution_chains: int, unresolved: int,
    ) -> None:
        self._enrichment_end = time.monotonic()
        self._partitions = partitions
        self._contradiction_boundaries = contradiction_boundaries
        self._evolution_chains = evolution_chains
        self._unresolved = unresolved

    def record_validation_passed(self) -> None:
        self._validation_passed = True

    def finalize(self) -> Phase7Stats:
        total = time.monotonic() - self._start
        construction_time = (
            (self._construction_end - self._construction_start)
            if self._construction_start and self._construction_end else 0.0
        )
        enrichment_time = (
            (self._enrichment_end - self._enrichment_start)
            if self._enrichment_start and self._enrichment_end else 0.0
        )
        return Phase7Stats(
            input_relationships=self._input_relationships,
            input_filtered=self._filtered,
            nodes_created=self._nodes,
            edges_created=self._edges,
            partitions_created=self._partitions,
            contradictions_as_boundaries=self._contradiction_boundaries,
            evolution_chains_detected=self._evolution_chains,
            unresolved_conflicts=self._unresolved,
            construction_time_seconds=round(construction_time, 4),
            enrichment_time_seconds=round(enrichment_time, 4),
            total_time_seconds=round(total, 4),
            validation_passed=self._validation_passed,
        )