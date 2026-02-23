@echo off
setlocal ENABLEDELAYEDEXPANSION
title A380X AI Crew - Install

set "REPO_DIR=%~dp0"
set "TARGET_ROOT=%USERPROFILE%\Documents\FBW_A380_Tools"
set "TARGET_DIR=%TARGET_ROOT%\A380X_AICrew"

echo ============================================
echo   FBW A380X AI Crew - Installation
echo ============================================
echo Repo:   %REPO_DIR%
echo Ziel:   %TARGET_DIR%
echo.

if not exist "%TARGET_ROOT%" mkdir "%TARGET_ROOT%"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [1/5] Dateien kopieren...
robocopy "%REPO_DIR%" "%TARGET_DIR%" /E /NFL /NDL /NJH /NJS /NP /XD ".git" ".venv" "dist" "build" >nul

echo [2/5] Python prüfen...
where python >nul 2>nul
if errorlevel 1 (
  echo FEHLER: Python wurde nicht gefunden.
  echo Bitte Python installieren und erneut starten.
  goto :END
)

echo [3/5] Virtuelle Umgebung erstellen...
if not exist "%TARGET_DIR%\.venv\Scripts\python.exe" (
  python -m venv "%TARGET_DIR%\.venv"
)

echo [4/5] Abhaengigkeiten installieren...
call "%TARGET_DIR%\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%TARGET_DIR%\requirements.txt"

echo [5/5] Doctor Test...
python "%TARGET_DIR%\src\main.py" doctor

echo.
echo Installation fertig.
echo Danach starten mit: A380X_AI_Run.cmd
echo.

:END
echo Fenster bleibt offen.
cmd /k
