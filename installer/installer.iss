; Inno Setup script — prproj-to-path-copy
; Gera o instalador .exe a partir do bundle gerado pelo PyInstaller (dist/prproj-to-path-copy/).
;
; Pre-requisitos:
;   1) PyInstaller ja rodou: dist/prproj-to-path-copy/ existe
;   2) assets/icon.ico existe
;
; Uso:
;   & "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\installer.iss

#define MyAppName        "prproj-to-path-copy"
#define MyAppVersion     "0.1.0"
#define MyAppPublisher   "lucasftas"
#define MyAppURL         "https://github.com/lucasftas/app-prproj-to-path-copy"
#define MyAppExeName     "prproj-to-path-copy.exe"
#define MyAppSourceDir   "..\dist\prproj-to-path-copy"

[Setup]
AppId={{A8B2C4D6-E8F0-4A2B-8C4D-6E8F0A2B4C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist\installer
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} — consolidador de midias do Premiere
VersionInfoProductName={#MyAppName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Todo o bundle do PyInstaller (pasta onedir)
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
