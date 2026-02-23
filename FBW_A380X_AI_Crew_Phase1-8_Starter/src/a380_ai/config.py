from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class AppConfig:
    raw: Dict[str, Any]

    @property
    def sim(self) -> Dict[str, Any]:
        return self.raw.get("sim", {})

    @property
    def paths(self) -> Dict[str, Any]:
        return self.raw.get("paths", {})

    @property
    def features(self) -> Dict[str, Any]:
        return self.raw.get("features", {})

    @property
    def automation(self) -> Dict[str, Any]:
        return self.raw.get("automation", {})

    @property
    def sop(self) -> Dict[str, Any]:
        return self.raw.get("sop", {})


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def load_config(path: Path) -> AppConfig:
    return AppConfig(raw=load_yaml(path))
