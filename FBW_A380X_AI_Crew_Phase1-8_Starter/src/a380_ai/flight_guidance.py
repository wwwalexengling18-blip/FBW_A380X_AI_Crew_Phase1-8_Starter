from __future__ import annotations

import logging
from typing import Any, Dict

from .state_detector import AircraftState


class FlightGuidanceHooks:
    """
    Phase 7 Platzhalter:
    Hier kommen spaeter Taxi-/AP-/PID/vJoy-Logiken rein.
    Im Starter loggen wir nur, welche Guidance-Hooks je State aktiv wären.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.log = logger
        self._last_state_code = None

    def on_state(self, state: AircraftState, snapshot: Dict[str, Any]) -> None:
        if state.code == self._last_state_code:
            return
        self._last_state_code = state.code
        if state.code in {"TAXI", "TAKEOFF_ROLL"}:
            self.log.info("[PHASE7] Ground Guidance aktiv: Taxi/Lineup Monitoring")
        elif state.code in {"CLIMB_OR_DEPARTURE", "ENROUTE", "APPROACH"}:
            self.log.info("[PHASE7] Flight Guidance Hook aktiv: AP/Managed-Modes Monitoring")
        elif state.code in {"COLD_DARK", "POWERED_GROUND", "SHUTDOWN"}:
            self.log.info("[PHASE7] Ground Ops Hook aktiv: Turnaround/Shutdown Monitoring")
