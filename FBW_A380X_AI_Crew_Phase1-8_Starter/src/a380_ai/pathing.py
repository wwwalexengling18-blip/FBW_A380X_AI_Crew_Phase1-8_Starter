from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_NAME = "A380X_AICrew"


def _expand_percent_vars(path_str: str) -> str:
    out = path_str
    for k, v in os.environ.items():
        out = out.replace(f"%{k}%", v)
    return os.path.expandvars(out)


USER_TOOLS_ROOT = Path(_expand_percent_vars(r"%USERPROFILE%\Documents\FBW_A380_Tools"))
USER_APP_DIR = USER_TOOLS_ROOT / APP_NAME


def bundled_base() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def ensure_user_dirs() -> dict[str, Path]:
    root = USER_APP_DIR
    cfg = root / "config"
    sops = root / "sops"
    logs = root / "logs"
    for p in [root, cfg, sops, logs]:
        p.mkdir(parents=True, exist_ok=True)
    return {"root": root, "config": cfg, "sops": sops, "logs": logs}


def ensure_seed_files() -> None:
    b = bundled_base()
    u = ensure_user_dirs()
    seed_pairs = [
        (b / "config" / "app_config.yaml", u["config"] / "app_config.yaml"),
        (b / "config" / "lvar_map_template.yaml", u["config"] / "lvar_map_template.yaml"),
        (b / "sops" / "fbw_a380x_gate_to_gate.yaml", u["sops"] / "fbw_a380x_gate_to_gate.yaml"),
    ]
    for src, dst in seed_pairs:
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
