from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepCondition:
    mode: str = "manual"
    key: Optional[str] = None
    equals: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    seconds: Optional[int] = None


@dataclass
class ActionSpec:
    kind: str = "noop"
    name: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SOPStep:
    id: str
    title: str
    description: str = ""
    action: ActionSpec = field(default_factory=ActionSpec)
    condition: StepCondition = field(default_factory=StepCondition)
    tags: List[str] = field(default_factory=list)
    timeout_sec: int = 120


@dataclass
class SOPPhase:
    id: str
    title: str
    steps: List[SOPStep] = field(default_factory=list)


@dataclass
class Snapshot:
    values: Dict[str, Any]
