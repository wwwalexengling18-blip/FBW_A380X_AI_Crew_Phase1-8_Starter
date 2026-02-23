from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from .action_executor import ActionExecutor
from .flight_guidance import FlightGuidanceHooks
from .lvar_mapping import load_lvar_mapping
from .models import SOPPhase, SOPStep
from .sim_backend import SimBackendBase
from .state_detector import AircraftStateDetector
from .state_machine import GateToGateStateMachine
from .wasim_bridge import WASimBridge


class A380AICrewController:
    def __init__(
        self,
        backend: SimBackendBase,
        phases: List[SOPPhase],
        logger: logging.Logger,
        config_dir,
        read_hz: int = 10,
        write_hz: int = 5,
        startup_delay_sec: int = 15,
        auto_complete_manual: bool = True,
    ) -> None:
        self.backend = backend
        self.log = logger
        self.read_hz = max(1, int(read_hz))
        self.write_hz = max(1, int(write_hz))
        self.startup_delay_sec = max(0, int(startup_delay_sec))
        self.sm = GateToGateStateMachine(phases=phases, logger=logger, auto_complete_manual=auto_complete_manual)
        self._started = time.time()
        self._last_action_step_id: Optional[str] = None
        self._last_state_code: Optional[str] = None

        # Phase 2 / 4 / 5 / 7 hooks
        self.detector = AircraftStateDetector()
        self.wasim = WASimBridge(logger)
        self.mapping = load_lvar_mapping(config_dir)
        self.executor = ActionExecutor(
            backend=backend,
            wasim=self.wasim,
            mapping=self.mapping,
            logger=logger,
            write_hz=self.write_hz,
        )
        self.guidance = FlightGuidanceHooks(logger)

    def _aircraft_ready(self, snapshot: Dict[str, Any]) -> bool:
        if (time.time() - self._started) < self.startup_delay_sec:
            return False
        return bool(snapshot.get("sim_connected")) and bool(snapshot.get("aircraft_loaded"))

    def _dispatch_step_action(self, step: SOPStep) -> None:
        if self._last_action_step_id == step.id:
            return
        result = self.executor.execute_with_retry(step)
        self.log.info("[ACTION] %s -> %s (%s)", step.id, "OK" if result.ok else "WAIT/MAP", result.detail)
        self._last_action_step_id = step.id

    def run(self, max_seconds: int = 0) -> int:
        if not self.backend.connect():
            self.log.error("Backend-Verbindung fehlgeschlagen.")
            return 2

        ws = self.wasim.status()
        self.log.info("WASim Status: %s (%s)", "OK" if ws.available else "INFO", ws.reason)
        self.log.info("LVar-Mapping bereit: %s", "JA" if self.mapping.ready else "NEIN (Template/Platzhalter)")

        self.log.info(
            "Controller gestartet (read_hz=%s, write_hz=%s, startup_delay=%ss)",
            self.read_hz, self.write_hz, self.startup_delay_sec
        )
        dt = 1.0 / float(self.read_hz)
        end_at = (time.time() + max_seconds) if max_seconds and max_seconds > 0 else None

        try:
            while True:
                snap = self.backend.read_snapshot()

                if end_at and time.time() >= end_at:
                    self.log.info("Zeitlimit erreicht -> sauberer Stop.")
                    return 0

                if not self._aircraft_ready(snap):
                    remain = max(0, self.startup_delay_sec - int(time.time() - self._started))
                    self.log.info("Warte auf Aircraft Ready... (Delay/Init) %ss", remain)
                    time.sleep(dt)
                    continue

                state = self.detector.detect(snap)
                if state.code != self._last_state_code:
                    self._last_state_code = state.code
                    self.log.info("[STATE] %s | %s", state.code, state.reason)
                self.guidance.on_state(state, snap)

                phase, step = self.sm.current()
                if self.sm.finished:
                    self.log.info("Gate-to-Gate Ablauf beendet.")
                    return 0

                if step is not None:
                    self._dispatch_step_action(step)

                self.sm.tick(snap)

                if end_at and time.time() >= end_at:
                    self.log.info("Zeitlimit erreicht -> sauberer Stop.")
                    return 0

                time.sleep(dt)
        except KeyboardInterrupt:
            self.log.warning("Manuell abgebrochen.")
            return 130
        finally:
            self.backend.close()
