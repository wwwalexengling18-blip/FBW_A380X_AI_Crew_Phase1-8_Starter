# FBW A380X AI Crew — Gate-to-Gate Starter (MSFS 2024)

Dieses Paket ist ein **One-ZIP Starterprojekt** für deine A380X-KI:
- **Phase 1:** Lesen & Loggen (stabil)
- **Phase 2:** State Detection (Cold & Dark, Taxi, Enroute ...)
- **Phase 3:** SOP State Machine (Gate-to-Gate YAML)
- **Phase 4/5:** FBW Mapping + Action Executor (Starter/Platzhalter)
- **Phase 6:** Doctor (Diagnose)
- **Phase 7:** Flight Guidance Hooks (Starter)
- **Phase 8:** GitHub Build + Setup.exe

## Schnellstart
1. `A380X_AI_Install.cmd`
2. `A380X_AI_Doctor.cmd`
3. `A380X_AI_Run.cmd`

## Demo-Test (ohne echten Sim)
`A380X_AI_Run.cmd` startet im Auto-Modus. Für einen reinen Demo-Lauf lokal:
`python src/main.py run --demo --max-seconds 90`

## Wichtig für echte FBW-Schalter
Die Datei `config/lvar_map_template.yaml` enthält **Platzhalter**.
Für echtes Schalten brauchst du ein verifiziertes Mapping in:
- `config/lvar_map.yaml`

## GitHub / Setup.exe
Der Workflow `.github/workflows/build_setup_exe.yml` baut automatisch:
- Portable Build (`A380X_AI_Portable`)
- Installer (`A380X_AI_Setup`)

Der Workflow erkennt jetzt automatisch, ob du die Dateien direkt im Repo-Root
oder in einem Unterordner hochgeladen hast.
