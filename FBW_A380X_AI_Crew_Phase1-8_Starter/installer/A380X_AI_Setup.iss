#define MyAppName "A380X AI Crew"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "OpenAI + User Custom Repo"
#define MyAppExeName "A380X_AICrew.exe"

[Setup]
AppId={{E1E1E1E1-1A38-4A80-8A38-000000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\A380X AI Crew
DefaultGroupName=A380X AI Crew
DisableProgramGroupPage=yes
Compression=lzma
SolidCompression=yes
OutputDir=..\dist_installer
OutputBaseFilename=A380X_AI_Crew_Setup
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\\dist\\A380X_AICrew\\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\\docs\\*"; DestDir: "{app}\\docs"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\\A380X AI Crew"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\\A380X AI Crew Doctor"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "doctor"
Name: "{group}\\A380X AI Crew SOP Schritte"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "list-steps"
Name: "{autodesktop}\\A380X AI Crew"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,A380X AI Crew}"; Flags: nowait postinstall skipifsilent
