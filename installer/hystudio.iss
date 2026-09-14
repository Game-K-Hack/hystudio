; Installateur de HyStudio (Inno Setup 6), compile par build_exe.py :
;   ISCC /DAppVersion=1.0.0 /DSourceDir=...\dist\HyStudio /DOutputDir=...\dist /DIconFile=...\hystudio.ico hystudio.iss
;
; Installation par utilisateur (%LOCALAPPDATA%\Programs\HyStudio), sans droits
; administrateur : la mise a jour depuis le logiciel se fait sans fenetre UAC.
; Une mise a jour remplace le programme (HyStudio.exe, _internal) et rien d'autre :
; projets (Documents\HyStudio), modeles et cache (%LOCALAPPDATA%\HyStudio) ne sont
; jamais dans le dossier installe, et la desinstallation ne les supprime pas.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
; identifiant fixe : les versions suivantes se reconnaissent et s'installent par-dessus
AppId={{7B3E4C2A-9D51-4F6B-A8E0-3C1D2B5F9A47}
AppName=HyStudio
AppVersion={#AppVersion}
AppVerName=HyStudio {#AppVersion}
AppPublisher=Game-K-Hack
AppPublisherURL=https://github.com/Game-K-Hack/hystudio
AppSupportURL=https://github.com/Game-K-Hack/hystudio/issues
AppUpdatesURL=https://github.com/Game-K-Hack/hystudio/releases
VersionInfoVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\HyStudio
DefaultGroupName=HyStudio
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputDir}
OutputBaseFilename=HyStudio-{#AppVersion}-Setup
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\HyStudio.exe
UninstallDisplayName=HyStudio
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; HyStudio ouvert : l'installateur le ferme proprement avant de remplacer les fichiers
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; bibliotheques de la version precedente : evite de garder des fichiers perimes.
; Seul le dossier du programme est concerne.
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\HyStudio"; Filename: "{app}\HyStudio.exe"
Name: "{autodesktop}\HyStudio"; Filename: "{app}\HyStudio.exe"; Tasks: desktopicon

[Run]
; installation normale : case « Lancer HyStudio » en fin d'assistant
Filename: "{app}\HyStudio.exe"; Description: "{cm:LaunchProgram,HyStudio}"; Flags: nowait postinstall skipifsilent
; mise a jour depuis le logiciel (/SILENT /LAUNCH) : relance automatique
Filename: "{app}\HyStudio.exe"; Flags: nowait; Check: LaunchAfterUpdate

[Code]
function LaunchAfterUpdate: Boolean;
begin
  Result := WizardSilent and (Pos('/LAUNCH', Uppercase(GetCmdTail)) > 0);
end;
