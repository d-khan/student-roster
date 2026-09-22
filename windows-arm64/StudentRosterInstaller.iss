#define MyAppName "Student Roster"
#define MyAppVersion "1.4.2"
#define MyAppPublisher "Student Roster"
#define MyAppExeName "Student Roster.exe"

[Setup]
AppId={{D22AC1EF-907E-4B0D-A823-8BBD9DA64041}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Student Roster
DefaultGroupName=Student Roster
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=StudentRoster-Setup-1.4.2
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\Student Roster.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=arm64 x64compatible
ArchitecturesInstallIn64BitMode=arm64 x64compatible
CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\Student Roster\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Student Roster"; Filename: "{app}\Student Roster.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Student Roster"; Filename: "{app}\Student Roster.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\Student Roster.exe"; Description: "Launch Student Roster"; Flags: nowait postinstall skipifsilent
