#define MyAppName "Student Roster"
#define MyAppVersion "1.4.2"
#define MyAppPublisher "Danish Khan"
#define MyAppExeName "Student Roster.exe"

[Setup]
AppId={{A82C7C72-CC23-4D98-AD7C-8BC53680D142}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Student Roster
DefaultGroupName=Student Roster
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=StudentRoster-Setup-1.4.2-x64
SetupIconFile=app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\Student Roster\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Student Roster"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Student Roster"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Student Roster"; Flags: nowait postinstall skipifsilent