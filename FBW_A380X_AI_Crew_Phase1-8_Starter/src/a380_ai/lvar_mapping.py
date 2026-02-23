from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class LVarMapping:
    events: Dict[str, str]
    lvars: Dict[str, str]
    raw: Dict[str, Any]

    @property
    def ready(self) -> bool:
        # Simple heuristic: no PLACEHOLDER values left in event map
        vals = list(self.events.values()) + list(self.lvars.values())
        if not vals:
            return False
        return all("PLACEHOLDER" not in str(v) for v in vals)


def load_lvar_mapping(config_dir: Path) -> LVarMapping:
    primary = config_dir / "lvar_map.yaml"
    fallback = config_dir / "lvar_map_template.yaml"
    path = primary if primary.exists() else fallback
    data: Dict[str, Any] = {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        data = {}
    return LVarMapping(
        events=dict(data.get("events", {}) or {}),
        lvars=dict(data.get("lvars", {}) or {}),
        raw=data or {},
    )
