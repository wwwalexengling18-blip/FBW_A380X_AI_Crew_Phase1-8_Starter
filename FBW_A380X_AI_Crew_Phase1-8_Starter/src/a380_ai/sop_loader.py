from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from .models import ActionSpec, SOPPhase, SOPStep, StepCondition


def _condition_from_dict(d: Dict[str, Any]) -> StepCondition:
    return StepCondition(
        mode=str(d.get("mode", "manual")),
        key=d.get("key"),
        equals=d.get("equals"),
        min_value=d.get("min_value"),
        max_value=d.get("max_value"),
        seconds=d.get("seconds"),
    )


def _action_from_dict(d: Dict[str, Any]) -> ActionSpec:
    return ActionSpec(
        kind=str(d.get("kind", "noop")),
        name=d.get("name"),
        value=d.get("value"),
        unit=d.get("unit"),
        args=d.get("args", {}) or {},
    )


def load_sop(path: Path) -> List[SOPPhase]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    phases_in = data.get("phases", [])
    phases: List[SOPPhase] = []

    for p in phases_in:
        steps: List[SOPStep] = []
        for s in p.get("steps", []):
            steps.append(
                SOPStep(
                    id=str(s["id"]),
                    title=str(s["title"]),
                    description=str(s.get("description", "")),
                    action=_action_from_dict(s.get("action", {}) or {}),
                    condition=_condition_from_dict(s.get("condition", {}) or {}),
                    tags=list(s.get("tags", []) or []),
                    timeout_sec=int(s.get("timeout_sec", 120)),
                )
            )
        phases.append(SOPPhase(id=str(p["id"]), title=str(p["title"]), steps=steps))
    return phases
