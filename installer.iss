; IC Authenticator - Inno Setup Installer Script
; Professional Windows Installer with Python Environment & Dependencies

#define MyAppName "IC Authenticator"
#define MyAppVersion "3.0.2"
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
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; Dependencies
Source: "requirements_production.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "install_dependencies.py"; DestDir: "{app}"; Flags: ignoreversion

; Test Images
Source: "test_images\*"; DestDir: "{app}\test_images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: quicklaunchicon

[Run]
; Install Python if needed (with better parameters for silent install)
Filename: "{tmp}\python_installer.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_pip=1 Include_tcltk=0"; StatusMsg: "Installing Python 3.11 (this may take a few minutes)..."; Flags: waituntilterminated; Check: NeedsPythonInstall

; Wait for Python PATH to be available and refresh environment
Filename: "cmd.exe"; Parameters: "/c timeout /t 5"; Flags: runhidden waituntilterminated; Check: NeedsPythonInstall

; Run the robust dependency installer (use cmd.exe to find python in PATH) - HIDDEN
Filename: "cmd.exe"; Parameters: "/c python ""{app}\install_dependencies.py"""; WorkingDir: "{app}"; StatusMsg: "Installing dependencies (10-20 minutes, please be patient)..."; Flags: runhidden waituntilterminated; Check: HasPythonAfterInstall

; Launch application after install (checked by default)
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
  PythonPath: String;

{ Check if Python is already installed }
function HasPython(): Boolean;
var
  ResultCode: Integer;
  PythonVer: String;
begin
  Result := False;
  
  // Try to run python --version
  if Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      Log('Python found via PATH');
      Result := True;
      Exit;
    end;
  end;
  
  // Try common installation paths
  if FileExists(ExpandConstant('{autopf}\Python311\python.exe')) then
  begin
    Log('Python found at: {autopf}\Python311');
    PythonPath := ExpandConstant('{autopf}\Python311');
    Result := True;
    Exit;
  end;
  
  if FileExists(ExpandConstant('{localappdata}\Programs\Python\Python311\python.exe')) then
  begin
    Log('Python found at: {localappdata}\Programs\Python\Python311');
    PythonPath := ExpandConstant('{localappdata}\Programs\Python\Python311');
    Result := True;
    Exit;
  end;
  
  Log('Python not found');
end;

{ Check if Python is available after installation }
function HasPythonAfterInstall(): Boolean;
var
  ResultCode: Integer;
  RetryCount: Integer;
begin
  Result := False;
  RetryCount := 0;
  
  // Retry a few times as PATH may need to refresh
  while (not Result) and (RetryCount < 5) do
  begin
    Sleep(1000); // Wait 1 second between retries
    
    // Try python command
    if Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      if ResultCode = 0 then
      begin
        Log('Python available via PATH after install');
        Result := True;
        Exit;
      end;
    end;
    
    // Try full path
    if FileExists(ExpandConstant('{autopf}\Python311\python.exe')) then
    begin
      Log('Python found at: {autopf}\Python311');
      PythonPath := ExpandConstant('{autopf}\Python311');
      Result := True;
      Exit;
    end;
    
    RetryCount := RetryCount + 1;
  end;
  
  if not Result then
    Log('Python not available after installation attempts');
end;

{ Determine if Python installation is needed }
function NeedsPythonInstall(): Boolean;
begin
  Result := not HasPython();
  if Result then
    Log('Python installation needed')
  else
    Log('Python already installed, skipping installation');
end;

{ Get the Python installation path }
function GetPythonPath(Param: String): String;
begin
  if PythonPath <> '' then
    Result := PythonPath
  else if FileExists(ExpandConstant('{autopf}\Python311\python.exe')) then
    Result := ExpandConstant('{autopf}\Python311')
  else if FileExists(ExpandConstant('{localappdata}\Programs\Python\Python311\python.exe')) then
    Result := ExpandConstant('{localappdata}\Programs\Python\Python311')
  else
    Result := 'python'; // Fallback to PATH
end;

{ Get Python download URL }
function GetPythonDownloadURL(): String;
begin
  Result := 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe';
end;

{ Download Python installer }
procedure DownloadPython();
var
  DownloadPage: TDownloadWizardPage;
  ErrorMessage: String;
begin
  DownloadPage := CreateDownloadPage('Downloading Python', 'Downloading Python 3.11 installer...', nil);
  DownloadPage.Clear;
  DownloadPage.Add(GetPythonDownloadURL(), 'python_installer.exe', '');
  DownloadPage.Show;
  try
    try
      DownloadPage.Download;
      Log('Python installer downloaded successfully');
    except
      ErrorMessage := GetExceptionMessage;
      if DownloadPage.AbortedByUser then
      begin
        Log('Python download was aborted by user');
        MsgBox('Installation cannot continue without Python. Please ensure you have an internet connection and try again.', mbError, MB_OK);
        Abort;
      end
      else
      begin
        Log('Python download failed: ' + ErrorMessage);
        MsgBox('Failed to download Python installer: ' + ErrorMessage + #13#10#13#10 + 
               'Please check your internet connection and try again.', mbError, MB_OK);
        Abort;
      end;
    end;
  finally
    DownloadPage.Hide;
  end;
end;

{ Initialize wizard }
procedure InitializeWizard();
begin
  PythonPath := '';
  PythonInstallPage := CreateOutputProgressPage('Checking Requirements', 'Checking for Python installation...');
end;

{ Handle installation steps }
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    PythonInstallPage.SetText('Checking Python installation...', '');
    PythonInstallPage.Show;
    try
      if not HasPython() then
      begin
        PythonInstallPage.SetText('Python not found.', 'Downloading Python 3.11...');
        PythonInstallPage.SetProgress(0, 100);
        DownloadPython();
        PythonInstallPage.SetText('Python downloaded.', 'Python will be installed next...');
        PythonInstallPage.SetProgress(100, 100);
      end
      else
      begin
        PythonInstallPage.SetText('Python found!', 'Using existing Python installation.');
        PythonInstallPage.SetProgress(100, 100);
      end;
      Sleep(1000);
    finally
      PythonInstallPage.Hide;
    end;
  end;
end;

{ Initialize setup }
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if 64-bit Windows
  if not Is64BitInstallMode then
  begin
    MsgBox('This application requires 64-bit Windows 10 or later.' + #13#10#13#10 + 
           'Your system is not compatible.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Display welcome message
  if MsgBox('IC Authenticator will now be installed.' + #13#10#13#10 + 
            'This installer will:' + #13#10 +
            '  • Install Python 3.11 (if not already installed)' + #13#10 +
            '  • Install required dependencies (PyQt5, OpenCV, EasyOCR, etc.)' + #13#10 +
            '  • Create desktop shortcuts' + #13#10#13#10 +
            'The installation may take several minutes depending on your internet speed.' + #13#10#13#10 +
            'Do you want to continue?', mbInformation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end;
end;
