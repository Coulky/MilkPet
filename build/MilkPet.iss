; Milk Pet Installer Script
; Compile with Inno Setup
; Download: https://jrsoftware.org/isdl.php

#define MyAppName "Milk Pet"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MilkPet"
#define MyAppExeName "MilkPet.exe"
#define MyAppDataDir "_internal"
#define MyAppSourceDir "dist\MilkPet"
#define MyUninstallExeName "uninstall.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=MilkPet_Setup_{#MyAppVersion}
SetupIconFile=assets\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=6.1sp1
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
UninstallFilesDir={app}\{#MyAppDataDir}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{#MyAppSourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSourceDir}\{#MyAppDataDir}\*"; DestDir: "{app}\{#MyAppDataDir}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "https://github.com/milkpet"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{app}\{#MyAppDataDir}\{#MyUninstallExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletevalue

[UninstallDelete]
; Delete application files but keep user data
Type: files; Name: "{app}\{#MyAppExeName}"
Type: files; Name: "{app}\{#MyAppDataDir}\{#MyUninstallExeName}"
Type: files; Name: "{app}\{#MyAppDataDir}\uninstall.log"
Type: dirifempty; Name: "{app}\{#MyAppDataDir}"
Type: dirifempty; Name: "{app}"

[UninstallRun]
; No additional uninstall steps needed