param(
  [switch]$OneFile
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python nicht gefunden."
}

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

if ($OneFile) {
  pyinstaller --noconfirm --clean --name A380X_AICrew --onefile --console `
    --add-data "config;config" `
    --add-data "sops;sops" `
    src/main.py
} else {
  pyinstaller --noconfirm --clean --name A380X_AICrew --onedir --console `
    --add-data "config;config" `
    --add-data "sops;sops" `
    src/main.py
}

$iscc = "${env:ProgramFiles(x86)}\\Inno Setup 6\\ISCC.exe"
if (Test-Path $iscc) {
  & $iscc ".\\installer\\A380X_AI_Setup.iss"
} else {
  Write-Host "ISCC.exe nicht gefunden. Inno Setup installieren und Script erneut ausführen."
}
