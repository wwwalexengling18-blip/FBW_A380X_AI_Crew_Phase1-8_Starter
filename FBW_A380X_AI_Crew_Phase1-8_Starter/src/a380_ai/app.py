from __future__ import annotations

import argparse

from .config import load_config
from .controller import A380AICrewController
from .doctor import run_doctor
from .logging_setup import configure_logging
from .pathing import ensure_seed_files, ensure_user_dirs
from .sim_backend import create_backend
from .sop_loader import load_sop


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="A380X_AICrew")
    sub = p.add_subparsers(dest="cmd", required=False)

    run = sub.add_parser("run", help="Gate-to-Gate Controller starten")
    run.add_argument("--demo", action="store_true", help="Erzwinge Dummy-Modus")
    run.add_argument("--max-seconds", type=int, default=0, help="Optionales Zeitlimit")
    run.add_argument("--verbose", action="store_true")
    run.add_argument("--no-auto-manual", action="store_true", help="Manuelle Schritte nicht auto-completen")

    doc = sub.add_parser("doctor", help="Systemdiagnose")
    doc.add_argument("--verbose", action="store_true")

    sub.add_parser("list-steps", help="SOP Schritte anzeigen")
    return p


def main() -> int:
    ensure_seed_files()
    dirs = ensure_user_dirs()
    parser = build_parser()
    args = parser.parse_args()

    cmd = args.cmd or "run"
    logger = configure_logging(dirs["logs"], verbose=getattr(args, "verbose", False))

    config_path = dirs["config"] / "app_config.yaml"
    sop_path = dirs["sops"] / "fbw_a380x_gate_to_gate.yaml"
    cfg = load_config(config_path)

    if cmd == "doctor":
        print(run_doctor())
        return 0

    phases = load_sop(sop_path)

    if cmd == "list-steps":
        for phase in phases:
            print(f"\n[{phase.id}] {phase.title}")
            for i, step in enumerate(phase.steps, start=1):
                print(f"  {i:02d}. {step.id} - {step.title}")
        return 0

    sim_mode = "dummy" if getattr(args, "demo", False) else str(cfg.sim.get("backend", "auto"))
    backend = create_backend(sim_mode, logger)
    controller = A380AICrewController(
        backend=backend,
        phases=phases,
        logger=logger,
        config_dir=dirs["config"],
        read_hz=int(cfg.sim.get("read_hz", 10)),
        write_hz=int(cfg.sim.get("write_hz", 5)),
        startup_delay_sec=int(cfg.sim.get("startup_delay_sec", 15)),
        auto_complete_manual=not bool(getattr(args, "no_auto_manual", False)),
    )
    return controller.run(max_seconds=int(getattr(args, "max_seconds", 0)))
