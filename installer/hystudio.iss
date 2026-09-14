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
; identifiant de l'application ; un autre identifiant (/DAppIdValue=...) sert aux installations d'essai
#ifndef AppIdValue
  #define AppIdValue "{{7B3E4C2A-9D51-4F6B-A8E0-3C1D2B5F9A47}"
#endif

[Setup]
; identifiant fixe : les versions suivantes se reconnaissent et s'installent par-dessus
AppId={#AppIdValue}
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
; association des fichiers .hysp : l'Explorateur est prevenu du changement
ChangesAssociations=yes
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

[CustomMessages]
english.AssocHysp=Open .hysp project files with HyStudio
french.AssocHysp=Ouvrir les fichiers de projet .hysp avec HyStudio
spanish.AssocHysp=Abrir los archivos de proyecto .hysp con HyStudio
german.AssocHysp=.hysp-Projektdateien mit HyStudio öffnen
italian.AssocHysp=Apri i file di progetto .hysp con HyStudio
russian.AssocHysp=Открывать файлы проектов .hysp в HyStudio
japanese.AssocHysp=.hysp プロジェクトファイルを HyStudio で開く
korean.AssocHysp=.hysp 프로젝트 파일을 HyStudio로 열기
english.ProjectType=HyStudio project
french.ProjectType=Projet HyStudio
spanish.ProjectType=Proyecto HyStudio
german.ProjectType=HyStudio-Projekt
italian.ProjectType=Progetto HyStudio
russian.ProjectType=Проект HyStudio
japanese.ProjectType=HyStudio プロジェクト
korean.ProjectType=HyStudio 프로젝트
english.FileAssoc=File associations:
french.FileAssoc=Associations de fichiers :
spanish.FileAssoc=Asociaciones de archivos:
german.FileAssoc=Dateizuordnungen:
italian.FileAssoc=Associazioni dei file:
russian.FileAssoc=Сопоставления файлов:
japanese.FileAssoc=ファイルの関連付け:
korean.FileAssoc=파일 연결:

[Tasks]
Name: "assoc"; Description: "{cm:AssocHysp}"; GroupDescription: "{cm:FileAssoc}"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Registry]
; association par utilisateur (HKA = HKCU sans droits administrateur), retiree a la desinstallation
Root: HKA; Subkey: "Software\Classes\.hysp\OpenWithProgids"; ValueType: string; ValueName: "HyStudio.Project"; ValueData: ""; Flags: uninsdeletevalue; Tasks: assoc
Root: HKA; Subkey: "Software\Classes\.hysp"; ValueType: string; ValueName: ""; ValueData: "HyStudio.Project"; Flags: uninsdeletevalue; Tasks: assoc
Root: HKA; Subkey: "Software\Classes\HyStudio.Project"; ValueType: string; ValueName: ""; ValueData: "{cm:ProjectType}"; Flags: uninsdeletekey; Tasks: assoc
Root: HKA; Subkey: "Software\Classes\HyStudio.Project\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\HyStudio.exe,0"; Tasks: assoc
Root: HKA; Subkey: "Software\Classes\HyStudio.Project\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\HyStudio.exe"" ""%1"""; Tasks: assoc
Root: HKA; Subkey: "Software\Classes\Applications\HyStudio.exe\SupportedTypes"; ValueType: string; ValueName: ".hysp"; ValueData: ""; Flags: uninsdeletekey; Tasks: assoc

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
