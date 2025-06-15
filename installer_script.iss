
[Setup]
AppName=ArchManager
AppVersion=1.0.0
AppPublisher=Sua Empresa
DefaultDirName={autopf}\ArchManager
OutputBaseFilename=ArchManager-1.0.0-setup
OutputDir=C:\Users\Gabri\OneDrive\Documentos\Codes\Projetos VSCode\Biblioteca\ArchManager
Compression=lzma2
SolidCompression=yes
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}";
[Files]
Source: "C:\Users\Gabri\OneDrive\Documentos\Codes\Projetos VSCode\Biblioteca\ArchManager\dist\ArchManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\ArchManager"; Filename: "{app}\ArchManager.exe"
Name: "{autodesktop}\ArchManager"; Filename: "{app}\ArchManager.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ArchManager.exe"; Description: "{cm:LaunchProgram,ArchManager}"; Flags: nowait postinstall skipifsilent
