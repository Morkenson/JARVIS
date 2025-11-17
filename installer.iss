; Inno Setup Script for Jarvis
; Run this with Inno Setup Compiler to create the installer

[Setup]
AppName=Jarvis Voice Assistant
AppVersion=1.0.0
AppPublisher=Your Name
AppPublisherURL=https://github.com/yourusername/JARVIS
DefaultDirName={autopf}\Jarvis
DefaultGroupName=Jarvis
OutputDir=dist
OutputBaseFilename=JarvisSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
SetupIconFile=
WizardImageFile=
WizardSmallImageFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Include the executable
Source: "dist\Jarvis.exe"; DestDir: "{app}"; Flags: ignoreversion

; Include all files from dist directory (works for both one-file and one-dir builds)
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Additional files
Source: "tts.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "version.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "Updater.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "GUI\UpdateDialog.py"; DestDir: "{app}\GUI"; Flags: ignoreversion

[Icons]
Name: "{group}\Jarvis"; Filename: "{app}\Jarvis.exe"
Name: "{group}\{cm:UninstallProgram,Jarvis}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Jarvis"; Filename: "{app}\Jarvis.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Jarvis"; Filename: "{app}\Jarvis.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Jarvis.exe"; Description: "{cm:LaunchProgram,Jarvis}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  // Create .env file from template if it doesn't exist
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Copy env.example to .env if .env doesn't exist
    if not FileExists(ExpandConstant('{app}\.env')) then
      FileCopy(ExpandConstant('{app}\env.example'), ExpandConstant('{app}\.env'), False);
  end;
end;

