# GitHub Upload Checkliste

1. Repo erstellen (öffentlich oder privat)
2. Alle Dateien hochladen
3. `Actions` Tab öffnen
4. Workflow `Build Setup EXE` starten
5. Artifact `A380X_AI_Setup` herunterladen
6. Setup auf Windows ausführen
7. Danach `Doctor` starten und prüfen:
   - FBW A380X im Community-Ordner
   - `wasimcommander-module` im Community-Ordner
   - Logs werden geschrieben

## Für echte FBW-Schaltersteuerung

- `config/lvar_map_template.yaml` kopieren zu `config/lvar_map.yaml`
- Platzhalter durch echte LVars/H-Events ersetzen
- Danach die entsprechenden `fbw_event` Actions im Code anbinden
