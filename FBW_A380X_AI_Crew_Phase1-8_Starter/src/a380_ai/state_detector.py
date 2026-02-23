from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AircraftState:
    code: str
    reason: str


class AircraftStateDetector:
    """
    Phase 2: erkennt grob den Flugzeugzustand aus gelesenen Sensorwerten.
    Regeln sind bewusst konservativ, damit sie im Dummy- und Real-Modus stabil laufen.
    """

    def __init__(self) -> None:
        self._last: Optional[AircraftState] = None

    def detect(self, snapshot: Dict[str, Any]) -> AircraftState:
        on_ground = bool(snapshot.get("on_ground", False))
        alt = float(snapshot.get("altitude_ft", 0) or 0)
        ias = float(snapshot.get("ias_kt", 0) or 0)
        engines = bool(snapshot.get("engines_running", False))
        apu = bool(snapshot.get("apu_master", False))
        ext_power = bool(snapshot.get("ext_power", False))
        parking_brake = bool(snapshot.get("parking_brake", False))
        gear_down = bool(snapshot.get("gear_down", True))

        if on_ground and not engines and not apu and parking_brake and alt < 5:
            st = AircraftState("COLD_DARK", "Am Boden, Triebwerke AUS, APU AUS, Parkbremse gesetzt")
        elif on_ground and not engines and (apu or ext_power):
            st = AircraftState("POWERED_GROUND", "Bodenbetrieb mit APU oder externer Versorgung")
        elif on_ground and engines and parking_brake:
            st = AircraftState("ENGINES_RUNNING_STAND", "Triebwerke laufen, Parkbremse gesetzt")
        elif on_ground and engines and not parking_brake and ias < 50:
            st = AircraftState("TAXI", "Am Boden rollend")
        elif on_ground and engines and not parking_brake and ias >= 50:
            st = AircraftState("TAKEOFF_ROLL", "Startlauf erkannt")
        elif (not on_ground) and alt < 10000 and not gear_down:
            st = AircraftState("CLIMB_OR_DEPARTURE", "Airborne unter 10.000 ft")
        elif (not on_ground) and alt >= 10000:
            st = AircraftState("ENROUTE", "Airborne enroute")
        elif (not on_ground) and gear_down and alt < 5000:
            st = AircraftState("APPROACH", "Gear down / Anflug")
        elif on_ground and not engines and parking_brake:
            st = AircraftState("SHUTDOWN", "Nach dem Flug, Parkbremse gesetzt")
        else:
            st = AircraftState("TRANSITION", "Übergangszustand")

        self._last = st
        return st
