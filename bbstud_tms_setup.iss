; ----------------------------------------------------------------------
; BBSTUD Transport Management System – Installer Script
; ----------------------------------------------------------------------

[Setup]
; Application details
AppName=BBSUTSD Transport Management System
AppVersion=1.0
AppPublisher=Benazir Bhutto Shaheed University of Technology & Skills Development
AppPublisherURL=https://www.bbsutsd.edu.pk
AppSupportURL=https://www.bbsutsd.edu.pk
AppUpdatesURL=https://www.bbsutsd.edu.pk

; Default installation folder (Program Files\BBSUTSD-TMS)
DefaultDirName={autopf}\BBSUTSD-TMS
; Start Menu folder name
DefaultGroupName=BBSUTSD Transport
; Allow only one instance of the installer
DisableWelcomePage=no
; Require administrator privileges (needed for writing to Program Files)
PrivilegesRequired=admin
; Modern wizard style
WizardStyle=modern

; Output directory for the compiled installer
OutputDir=installer
; Output installer file name
OutputBaseFilename=BBSUTSD-TMS_Setup_1.0
; Use solid LZMA2 compression for best size
Compression=lzma2
SolidCompression=yes

; Uninstaller icon (shown in Control Panel)
UninstallDisplayIcon={app}\BBSUTSD-TMS.exe
; (Optional) Installer wizard icon – replace with your .ico file if available
; SetupIconFile=resources\images\university_logo.ico

[Files]
; 1. Copy all application files (PyInstaller output) into the installation folder
Source: "dist\BBSUTSD-TMS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Copy the seed database to the user's AppData folder, but only if it doesn't already exist
Source: "dist\BBSUTSD-TMS\_internal\transport_db.db"; DestDir: "{userappdata}\BBSUTSD-TMS"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall
; The 'uninsneveruninstall' flag ensures that the database is never removed during uninstallation,
; preserving user data even if the application is uninstalled.

[Icons]
; Desktop shortcut
Name: "{commondesktop}\BBSUTSD Transport"; Filename: "{app}\BBSUTSD-TMS.exe"; WorkingDir: "{userappdata}\BBSUTSD-TMS"; IconFilename: "{app}\BBSUTSD-TMS.exe"
; Start Menu shortcut
Name: "{group}\BBSUTSD Transport Management"; Filename: "{app}\BBSUTSD-TMS.exe"; WorkingDir: "{userappdata}\BBSUTSD-TMS"
; Uninstall shortcut in Start Menu
Name: "{group}\Uninstall BBSUTSD TMS"; Filename: "{uninstallexe}"

[Run]
; Optionally launch the application after installation
Filename: "{app}\BBSUTSD-TMS.exe"; Description: "Launch BBSTUD TMS"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Keep user data – we do NOT delete AppData contents.
; Add any cleanup if needed in future versions.