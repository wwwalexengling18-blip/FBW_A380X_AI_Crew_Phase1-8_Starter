from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from .models import SOPPhase, SOPStep


class GateToGateStateMachine:
    def __init__(self, phases: List[SOPPhase], logger: logging.Logger, auto_complete_manual: bool = True) -> None:
        self.phases = phases
        self.log = logger
        self.auto_complete_manual = auto_complete_manual
        self.phase_idx = 0
        self.step_idx = 0
        self.current_step_started_at: Optional[float] = None
        self.finished = False

    def current(self) -> Tuple[Optional[SOPPhase], Optional[SOPStep]]:
        if self.finished or self.phase_idx >= len(self.phases):
            return None, None
        phase = self.phases[self.phase_idx]
        if self.step_idx >= len(phase.steps):
            return phase, None
        return phase, phase.steps[self.step_idx]

    def start_current_step(self) -> None:
        phase, step = self.current()
        if not phase or not step:
            return
        if self.current_step_started_at is None:
            self.current_step_started_at = time.time()
            self.log.info("PHASE [%s] %s", phase.id, phase.title)
            self.log.info("STEP  [%s] %s", step.id, step.title)
            if step.description:
                self.log.info("      %s", step.description)

    def _step_timed_out(self, step: SOPStep) -> bool:
        if self.current_step_started_at is None:
            return False
        return (time.time() - self.current_step_started_at) > step.timeout_sec

    def _condition_met(self, step: SOPStep, snapshot: Dict[str, Any]) -> bool:
        c = step.condition
        mode = (c.mode or "manual").lower()

        if mode == "manual":
            return self.auto_complete_manual and self.current_step_started_at is not None and (time.time() - self.current_step_started_at) >= 0.5

        if mode == "timer":
            sec = c.seconds or 1
            return self.current_step_started_at is not None and (time.time() - self.current_step_started_at) >= sec

        if mode == "sensor":
            if c.key is None:
                return False
            val = snapshot.get(c.key)
            if c.equals is not None:
                return val == c.equals
            if c.min_value is not None and (val is None or float(val) < float(c.min_value)):
                return False
            if c.max_value is not None and (val is None or float(val) > float(c.max_value)):
                return False
            return True

        if mode == "any_of":
            # supported via action args + manual for now (placeholder)
            return self.auto_complete_manual

        return False

    def tick(self, snapshot: Dict[str, Any]) -> Tuple[Optional[SOPPhase], Optional[SOPStep], str]:
        phase, step = self.current()
        if self.finished:
            return None, None, "finished"

        if phase is None:
            self.finished = True
            return None, None, "finished"

        # Phase can have no steps
        if step is None:
            self.phase_idx += 1
            self.step_idx = 0
            self.current_step_started_at = None
            if self.phase_idx >= len(self.phases):
                self.finished = True
                self.log.info("Alle SOP-Phasen abgeschlossen.")
                return None, None, "finished"
            return self.current()

        self.start_current_step()

        if self._condition_met(step, snapshot):
            self.log.info("OK    [%s] abgeschlossen", step.id)
            self.step_idx += 1
            self.current_step_started_at = None
            if self.step_idx >= len(phase.steps):
                self.log.info("PHASE [%s] fertig", phase.id)
            return phase, step, "step_completed"

        if self._step_timed_out(step):
            self.log.warning("TIMEOUT [%s] -> weiter zur nächsten Stufe", step.id)
            self.step_idx += 1
            self.current_step_started_at = None
            return phase, step, "step_timeout"

        return phase, step, "waiting"
