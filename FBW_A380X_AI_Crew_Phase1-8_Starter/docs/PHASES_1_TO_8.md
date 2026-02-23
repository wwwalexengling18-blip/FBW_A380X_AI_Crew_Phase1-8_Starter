# A380X KI Roadmap Phase 1-8

Dieses Paket startet bereits mit einem lauffähigen **Phase-1/2/3/6/8 Starter** und Platzhaltern für **Phase 4/5/7**.

## Phase 1 – Lesen & Loggen
- `src/a380_ai/sim_backend.py`
- `src/a380_ai/logging_setup.py`

## Phase 2 – State Detection
- `src/a380_ai/state_detector.py`

## Phase 3 – SOP State Machine
- `src/a380_ai/state_machine.py`
- `sops/fbw_a380x_gate_to_gate.yaml`

## Phase 4 – FBW Mapping (LVars/H-Events)
- `src/a380_ai/lvar_mapping.py`
- `src/a380_ai/wasim_bridge.py`
- `config/lvar_map_template.yaml`

## Phase 5 – Action Executor (Retry/Timeout)
- `src/a380_ai/action_executor.py`

## Phase 6 – Doctor
- `src/a380_ai/doctor.py`

## Phase 7 – Flight Guidance Hooks
- `src/a380_ai/flight_guidance.py`

## Phase 8 – Build/Setup/GitHub
- `.github/workflows/build_setup_exe.yml`
- `installer/A380X_AI_Setup.iss`

## Test-Befehle (lokal)
- `python src/main.py doctor`
- `python src/main.py list-steps`
- `python src/main.py run --demo --max-seconds 60`
