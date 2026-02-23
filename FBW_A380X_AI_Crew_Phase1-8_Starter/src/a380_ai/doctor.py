from __future__ import annotations

import os
import platform
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .pathing import USER_APP_DIR


def _read_installed_packages_path(usercfg: Path) -> Optional[Path]:
    try:
        text = usercfg.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    m = re.search(r'InstalledPackagesPath\s+"([^"]+)"', text)
    if not m:
        return None
    return Path(m.group(1))


def _candidate_usercfg_paths() -> List[Path]:
    appdata = Path(os.environ.get("APPDATA", ""))
    localapp = Path(os.environ.get("LOCALAPPDATA", ""))
    cands = [
        appdata / "Microsoft Flight Simulator 2024" / "Packages" / "UserCfg.opt",
        appdata / "Microsoft Flight Simulator 2024" / "UserCfg.opt",
        localapp / "Packages" / "Microsoft.Limitless_8wekyb3d8bbwe" / "LocalCache" / "UserCfg.opt",
        localapp / "Packages" / "Microsoft.FlightSimulator_8wekyb3d8bbwe" / "LocalCache" / "UserCfg.opt",
    ]
    return [c for c in cands if str(c) != "."]


def detect_community_folder() -> Tuple[Optional[Path], List[str]]:
    notes: List[str] = []
    for p in _candidate_usercfg_paths():
        if p.exists():
            notes.append(f"UserCfg gefunden: {p}")
            ip = _read_installed_packages_path(p)
            if ip:
                community = ip / "Community"
                notes.append(f"InstalledPackagesPath erkannt: {ip}")
                return community, notes
            notes.append("InstalledPackagesPath nicht lesbar")
    notes.append("Kein passender UserCfg.opt automatisch gefunden")
    return None, notes


def run_doctor() -> str:
    lines: List[str] = []
    lines.append("=== FBW A380X AI Crew Doctor ===")
    lines.append(f"Python: {platform.python_version()} ({sys.executable})")
    lines.append(f"OS: {platform.platform()}")
    lines.append(f"Arbeitsordner: {USER_APP_DIR}")

    # config and phase modules
    checks = [
        USER_APP_DIR / "config" / "app_config.yaml",
        USER_APP_DIR / "config" / "lvar_map_template.yaml",
        USER_APP_DIR / "sops" / "fbw_a380x_gate_to_gate.yaml",
        USER_APP_DIR / "logs",
    ]
    for p in checks:
        lines.append(f"[{'OK' if p.exists() else 'MISS'}] {p}")

    phase_modules = [
        "state_detector.py (Phase 2)",
        "action_executor.py (Phase 4/5)",
        "flight_guidance.py (Phase 7)",
        "doctor.py (Phase 6)",
    ]
    for m in phase_modules:
        lines.append(f"[INFO] Modul enthalten: {m}")

    try:
        import yaml  # type: ignore
        _ = yaml
        lines.append("[OK] PyYAML installiert")
    except Exception as e:
        lines.append(f"[MISS] PyYAML fehlt: {e}")

    try:
        import SimConnect  # type: ignore
        _ = SimConnect
        lines.append("[OK] SimConnect Python-Paket gefunden (optional)")
    except Exception:
        lines.append("[INFO] SimConnect Python-Paket nicht gefunden (optional, Starter nutzt Dummy-Modus)")

    community, notes = detect_community_folder()
    for n in notes:
        lines.append(f"[INFO] {n}")

    if community:
        lines.append(f"[{'OK' if community.exists() else 'MISS'}] Community-Ordner: {community}")
        if community.exists():
            fbw_candidates = [community / "fbw-a380x", community / "flybywire-aircraft-a380-842"]
            wasim = community / "wasimcommander-module"
            found_fbw = [p for p in fbw_candidates if p.exists()]
            if found_fbw:
                lines.append(f"[OK] FBW A380X Addon erkannt: {found_fbw[0]}")
            else:
                lines.append("[MISS] FBW A380X Addon nicht im Community-Ordner gefunden")
            if wasim.exists():
                lines.append(f"[OK] WASimCommander Modul erkannt: {wasim}")
                scfg = wasim / "modules" / "server_conf.ini"
                lines.append(f"[{'OK' if scfg.exists() else 'MISS'}] server_conf.ini: {scfg}")
            else:
                lines.append("[MISS] wasimcommander-module nicht im Community-Ordner gefunden")
    else:
        lines.append("[MISS] Community-Ordner konnte nicht automatisch erkannt werden")

    for hint in [
        USER_APP_DIR / "logs" / "a380_ai.log",
        USER_APP_DIR / "config" / "lvar_map.yaml",
    ]:
        lines.append(f"[INFO] Erwarteter Pfad: {hint}")

    lines.append("")
    lines.append("Roadmap / Naechster Schritt:")
    lines.append("Phase 1: run --demo testen (stabile Logs)")
    lines.append("Phase 2: States pruefen (COLD_DARK/TAXI/ENROUTE)")
    lines.append("Phase 4/5: lvar_map.yaml mit echten FBW Events fuellen")
    lines.append("Phase 8: GitHub Action -> Setup EXE bauen")
    return "\n".join(lines)
