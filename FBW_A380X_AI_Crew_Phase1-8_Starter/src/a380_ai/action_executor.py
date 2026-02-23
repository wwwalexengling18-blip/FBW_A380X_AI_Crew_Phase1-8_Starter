from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .lvar_mapping import LVarMapping
from .models import SOPStep
from .sim_backend import SimBackendBase
from .wasim_bridge import WASimBridge


@dataclass
class ActionResult:
    ok: bool
    mode: str
    detail: str


class ActionExecutor:
    """
    Phase 4/5:
    - übersetzt SOP-Aktionen auf SimConnect/FBW-Events
    - führt Retries aus
    - fällt sauber auf Logging zurück, wenn Mapping noch Platzhalter enthält
    """

    def __init__(
        self,
        backend: SimBackendBase,
        wasim: WASimBridge,
        mapping: LVarMapping,
        logger: logging.Logger,
        write_hz: int = 5,
        retries: int = 2,
    ) -> None:
        self.backend = backend
        self.wasim = wasim
        self.mapping = mapping
        self.log = logger
        self.write_hz = max(1, int(write_hz))
        self.retries = max(0, int(retries))

    def _resolve_fbw_event(self, logical_name: Optional[str]) -> Optional[str]:
        if not logical_name:
            return None
        if logical_name in self.mapping.events:
            return self.mapping.events[logical_name]
        # tiny convenience aliases
        alias_map = {
            "flaps_takeoff": self.mapping.events.get("flaps_1"),
            "flaps_up_schedule": self.mapping.events.get("flaps_up"),
            "engine_masters_on": self.mapping.events.get("engine1_master_on"),
            "after_landing_cleanup": self.mapping.events.get("flaps_up"),
        }
        return alias_map.get(logical_name)

    def execute_once(self, step: SOPStep) -> ActionResult:
        a = step.action
        kind = (a.kind or "noop").lower()

        if kind in {"noop", "manual"}:
            self.log.info("[ACTION] noop/manual: %s", a.name or step.id)
            return ActionResult(True, "noop", "no operation")

        if kind == "event":
            ok = self.backend.execute_action("event", a.name, a.value, unit=a.unit, **(a.args or {}))
            return ActionResult(bool(ok), "simconnect_event", f"{a.name}={a.value}")

        if kind == "fbw_event":
            target = self._resolve_fbw_event(a.name)
            if not target:
                self.log.warning("[ACTION] Kein FBW-Mapping fuer %s (Template noch offen?)", a.name)
                self.backend.execute_action("fbw_event_unmapped", a.name, a.value, unit=a.unit, **(a.args or {}))
                return ActionResult(False, "fbw_event_unmapped", str(a.name))

            if "PLACEHOLDER" in str(target):
                self.log.warning("[ACTION] Platzhalter-Event fuer %s -> %s", a.name, target)
                self.backend.execute_action("fbw_event_placeholder", target, a.value, unit=a.unit, **(a.args or {}))
                return ActionResult(False, "fbw_event_placeholder", target)

            # Starter nutzt noch kein echtes WASim senden -> zuerst Stub loggen, dann backend loggen
            self.wasim.send_event(target, a.value)
            self.backend.execute_action("fbw_event", target, a.value, unit=a.unit, **(a.args or {}))
            return ActionResult(True, "fbw_event", target)

        # unknown kinds -> still log
        ok = self.backend.execute_action(kind, a.name, a.value, unit=a.unit, **(a.args or {}))
        return ActionResult(bool(ok), "raw", f"{kind}:{a.name}")

    def execute_with_retry(self, step: SOPStep) -> ActionResult:
        delay = 1.0 / float(self.write_hz)
        last = ActionResult(False, "none", "not run")
        for attempt in range(self.retries + 1):
            last = self.execute_once(step)
            if last.ok:
                if attempt > 0:
                    self.log.info("[ACTION] Retry erfolgreich (%s) fuer %s", attempt, step.id)
                return last
            if attempt < self.retries:
                self.log.warning("[ACTION] Retry %s/%s fuer %s", attempt + 1, self.retries, step.id)
                time.sleep(delay)
        return last
