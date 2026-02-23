from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


class SimBackendBase:
    name = "base"

    def connect(self) -> bool:
        return True

    def close(self) -> None:
        return None

    def read_snapshot(self) -> Dict[str, Any]:
        raise NotImplementedError

    def execute_action(self, action_kind: str, name: Optional[str], value: Any = None, **kwargs: Any) -> bool:
        raise NotImplementedError


@dataclass
class DummyFlightState:
    tick: int = 0
    phase_index: int = 0
    altitude_ft: float = 0.0
    ias_kt: float = 0.0
    on_ground: bool = True
    engines_running: bool = False
    beacon_on: bool = False
    seatbelts_on: bool = False
    parking_brake: bool = True
    ap1_on: bool = False
    gear_down: bool = True
    spoilers_armed: bool = False
    flaps_config: int = 0
    ext_power: bool = True
    apu_master: bool = False
    aircraft_loaded: bool = False


class DummySimBackend(SimBackendBase):
    name = "dummy"

    def __init__(self, logger: logging.Logger) -> None:
        self.log = logger
        self.state = DummyFlightState()
        self._connected = False
        self._start = time.time()

    def connect(self) -> bool:
        self._connected = True
        self.log.info("Dummy backend verbunden.")
        return True

    def close(self) -> None:
        self._connected = False

    def read_snapshot(self) -> Dict[str, Any]:
        self.state.tick += 1
        # Startup / aircraft ready
        if time.time() - self._start > 3:
            self.state.aircraft_loaded = True

        # Simple progression to make sensor-based conditions work in demo
        t = self.state.tick
        if t > 20:
            self.state.apu_master = True
        if t > 30:
            self.state.beacon_on = True
        if t > 40:
            self.state.engines_running = True
            self.state.ext_power = False
        if t > 50:
            self.state.flaps_config = 1
            self.state.spoilers_armed = True
        if t > 60:
            self.state.parking_brake = False
        if t > 70:
            self.state.ias_kt = min(170, self.state.ias_kt + 8)
        if t > 75:
            self.state.on_ground = False
        if t > 76:
            self.state.altitude_ft = min(35000, self.state.altitude_ft + 1800)
            self.state.gear_down = False
        if t > 95:
            self.state.ap1_on = True
            self.state.seatbelts_on = True
            self.state.flaps_config = 0
        if t > 130:
            self.state.altitude_ft = max(3000, self.state.altitude_ft - 2200)
        if t > 145:
            self.state.gear_down = True
            self.state.flaps_config = 3
        if t > 155:
            self.state.on_ground = True
            self.state.altitude_ft = 0
            self.state.ias_kt = max(0, self.state.ias_kt - 15)
        if t > 165:
            self.state.parking_brake = True
            self.state.engines_running = False
            self.state.beacon_on = False
            self.state.seatbelts_on = False

        return {
            "sim_connected": self._connected,
            "aircraft_loaded": self.state.aircraft_loaded,
            "on_ground": self.state.on_ground,
            "engines_running": self.state.engines_running,
            "beacon_on": self.state.beacon_on,
            "seatbelts_on": self.state.seatbelts_on,
            "parking_brake": self.state.parking_brake,
            "apu_master": self.state.apu_master,
            "ext_power": self.state.ext_power,
            "ap1_on": self.state.ap1_on,
            "gear_down": self.state.gear_down,
            "spoilers_armed": self.state.spoilers_armed,
            "flaps_config": self.state.flaps_config,
            "ias_kt": round(self.state.ias_kt, 1),
            "altitude_ft": round(self.state.altitude_ft, 1),
            "clock": time.time(),
        }

    def execute_action(self, action_kind: str, name: Optional[str], value: Any = None, **kwargs: Any) -> bool:
        self.log.info("[DUMMY ACTION] %s | %s = %s | %s", action_kind, name, value, kwargs if kwargs else "-")
        return True


class AutoBackend(SimBackendBase):
    # Phase 1 Starter: erkennt optional SimConnect-Paket und faellt sonst sauber auf Dummy zurück.
    name = "auto"

    def __init__(self, logger: logging.Logger) -> None:
        self.log = logger
        self._dummy = DummySimBackend(logger)
        self._connected = False
        self._simconnect_available = False
        self._simconnect_error = None
        try:
            import SimConnect  # type: ignore # optional package
            _ = SimConnect
            self._simconnect_available = True
        except Exception as e:  # pragma: no cover
            self._simconnect_error = e

    def connect(self) -> bool:
        # This starter repo intentionally falls back to Dummy mode unless you implement the exact SimConnect/WASim client.
        if self._simconnect_available:
            self.log.warning(
                "SimConnect-Python wurde gefunden, aber die FBW A380X LVar/H-Event Integration muss projekt-spezifisch gemappt werden. "
                "Starte vorerst in Dummy/Diagnose-Modus."
            )
        else:
            self.log.info("SimConnect-Python nicht gefunden -> Dummy-Modus.")
        self._connected = self._dummy.connect()
        return self._connected

    def close(self) -> None:
        self._dummy.close()

    def read_snapshot(self) -> Dict[str, Any]:
        return self._dummy.read_snapshot()

    def execute_action(self, action_kind: str, name: Optional[str], value: Any = None, **kwargs: Any) -> bool:
        return self._dummy.execute_action(action_kind, name, value, **kwargs)


def create_backend(mode: str, logger: logging.Logger) -> SimBackendBase:
    mode = (mode or "auto").lower().strip()
    if mode == "dummy":
        return DummySimBackend(logger)
    return AutoBackend(logger)
