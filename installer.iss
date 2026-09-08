; Inno Setup script for FBR Invoice Checker
; Compile with: ISCC.exe installer.iss

#define MyAppName "FBR Invoice Checker"
; Override at compile time with: ISCC installer.iss /DMyAppVersion=X.Y
#ifndef MyAppVersion
  #define MyAppVersion "2.1"
#endif
#define MyAppPublisher "Codium Edge"
#define MyAppExeName "InvoiceChecker.exe"

[Setup]
AppId={{8F3B2C41-6A2E-4C1D-9E7A-1B5D2F9C4A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=FBR_Invoice_Checker_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; No "skipifsilent" so an auto-update's /VERYSILENT install also relaunches the app.
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\FBR Invoice Checker"
