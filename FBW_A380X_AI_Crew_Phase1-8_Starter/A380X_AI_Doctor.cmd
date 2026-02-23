@echo off
setlocal
title A380X AI Crew - Doctor

set "ROOT=%USERPROFILE%\Documents\FBW_A380_Tools\A380X_AICrew"

if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo FEHLER: Installation nicht gefunden.
  echo Bitte zuerst A380X_AI_Install.cmd ausfuehren.
  goto :END
)

call "%ROOT%\.venv\Scripts\activate.bat"
cd /d "%ROOT%"
python src\main.py doctor

:END
echo.
echo Fenster bleibt offen.
cmd /k
