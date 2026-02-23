from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class WasimStatus:
    available: bool
    reason: str


class WASimBridge:
    """
    Phase 4 Starter:
    - prüft nur, ob ein Python-Client importiert werden kann
    - echte Verbindung / Events folgen, sobald dein verifiziertes Mapping feststeht
    """
    def __init__(self, logger: logging.Logger) -> None:
        self.log = logger
        self._import_error: Optional[Exception] = None
        self._available = False
        try:
            # Kein harter Importname erzwungen – je nach Installation unterschiedlich.
            import importlib
            for name in ["WASimCommander", "wasimcommander", "WASimClient"]:
                try:
                    importlib.import_module(name)
                    self._available = True
                    break
                except Exception:
                    continue
        except Exception as e:
            self._import_error = e

    def status(self) -> WasimStatus:
        if self._available:
            return WasimStatus(True, "WASim Python API importierbar")
        if self._import_error:
            return WasimStatus(False, f"WASim Importfehler: {self._import_error}")
        return WasimStatus(False, "Kein WASim Python Modul gefunden (ok im Starter)")

    def send_event(self, event_name: str, value: Any = None) -> bool:
        self.log.info("[WASIM-STUB] Event %s value=%s", event_name, value)
        return False

    def read_lvar(self, lvar_name: str) -> Any:
        self.log.info("[WASIM-STUB] LVar lesen %s", lvar_name)
        return None
