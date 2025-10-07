; IC Authenticator - Inno Setup Installer Script
; Professional Windows Installer with Python Environment

#define MyAppName "IC Authenticator"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "IC Detection"
#define MyAppURL "https://github.com/Ross0907/Ic_detection"
#define MyAppExeName "ICAuthenticator.exe"

[Setup]
; Application Info
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation Paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=ICAuthenticator_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

; System Requirements
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
WizardSizePercent=100
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main Executable
Source: "ICAuthenticator.exe"; DestDir: "{app}"; Flags: ignoreversion

; Python Application Files
Source: "gui_classic_production.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "final_production_authenticator.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "enhanced_preprocessing.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "database_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "marking_validator.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "working_web_scraper.py"; DestDir: "{app}"; Flags: ignoreversion

; Configuration & Data Files
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8n.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

; Dependencies
Source: "requirements_production.txt"; DestDir: "{app}"; Flags: ignoreversion

; Test Images
Source: "test_images\*"; DestDir: "{app}\test_images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: quicklaunchicon

[Run]
; Install Python if needed
Filename: "{tmp}\python_installer.exe"; Parameters: "/quiet InstallAllUsers=0 PrependPath=1"; StatusMsg: "Installing Python 3.11..."; Flags: waituntilterminated; Check: NeedsPythonInstall

; Install Python dependencies
Filename: "python"; Parameters: "-m pip install --upgrade pip"; WorkingDir: "{app}"; StatusMsg: "Upgrading pip..."; Flags: runhidden waituntilterminated; Check: HasPython
Filename: "python"; Parameters: "-m pip install -r ""{app}\requirements_production.txt"""; WorkingDir: "{app}"; StatusMsg: "Installing dependencies (this may take several minutes)..."; Flags: runhidden waituntilterminated; Check: HasPython

; Launch application after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\ic_authentication.db"
Type: filesandordirs; Name: "{app}\datasheet_cache"
Type: filesandordirs; Name: "{app}\final_production_debug"
Type: filesandordirs; Name: "{app}\debug_preprocessing"
Type: filesandordirs; Name: "{app}\production_debug"

[Code]
var
  PythonInstallPage: TOutputProgressWizardPage;

function HasPython(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function NeedsPythonInstall(): Boolean;
begin
  Result := not HasPython();
end;

function GetPythonDownloadURL(): String;
begin
  Result := 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe';
end;

procedure DownloadPython();
var
  DownloadPage: TDownloadWizardPage;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
  DownloadPage.Clear;
  DownloadPage.Add(GetPythonDownloadURL(), 'python_installer.exe', '');
  DownloadPage.Show;
  try
    try
      DownloadPage.Download;
    except
      if DownloadPage.AbortedByUser then
        Log('Python download was aborted by user')
      else
        SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
    end;
  finally
    DownloadPage.Hide;
  end;
end;

procedure InitializeWizard();
begin
  PythonInstallPage := CreateOutputProgressPage('Checking Python', 'Checking for Python installation...');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    PythonInstallPage.SetText('Checking Python installation...', '');
    PythonInstallPage.Show;
    try
      if not HasPython() then
      begin
        PythonInstallPage.SetText('Python not found. Downloading Python 3.11...', '');
        DownloadPython();
      end
      else
      begin
        PythonInstallPage.SetText('Python found!', '');
      end;
    finally
      PythonInstallPage.Hide;
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if 64-bit Windows
  if not Is64BitInstallMode then
  begin
    MsgBox('This application requires 64-bit Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end;
end;
