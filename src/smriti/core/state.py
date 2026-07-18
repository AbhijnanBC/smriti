"""
Pipeline state for resuming interrupted runs.
Stores: which phases completed, when they started, current position.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog

from smriti.core.paths import STATE_FILE
from smriti.core.models import PipelineState


logger = structlog.get_logger(__name__)


class StateManager:
    """Persist and restore pipeline state across interruptions."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def start_run(self) -> PipelineState:
        """Initialize a new pipeline run and persist it."""
        state = PipelineState(started_at=datetime.now(), current_phase=1)
        self.save(state)
        logger.info("pipeline run started", started_at=state.started_at.isoformat())
        return state

    def complete_phase(self, phase: int) -> None:
        """Mark a phase as completed and advance current_phase."""
        state = self.load()
        if state:
            if phase not in state.completed_phases:
                state.completed_phases.append(phase)
            state.current_phase = phase + 1
            self.save(state)
            logger.info("phase marked complete", phase=phase)

    def load(self) -> Optional[PipelineState]:
        """Load existing state. Returns None if no state file found."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, encoding="utf-8") as f:
                data = json.load(f)
            return PipelineState(
                started_at=datetime.fromisoformat(data["started_at"]),
                current_phase=data.get("current_phase", 1),
                completed_phases=data.get("completed_phases", []),
            )
        except Exception as e:
            logger.error("state load failed", error=str(e))
            return None

    def save(self, state: PipelineState) -> None:
        """Persist state to disk."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "started_at": state.started_at.isoformat(),
                    "current_phase": state.current_phase,
                    "completed_phases": state.completed_phases,
                },
                f,
                indent=2,
            )

    def clear(self) -> None:
        """Clear saved state (use before a fresh run)."""
        if self.state_file.exists():
            self.state_file.unlink()
        logger.info("state cleared")