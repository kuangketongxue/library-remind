; ============================================================================
; RestReminder Installer Script for Inno Setup
; 编译命令: iscc RestReminder.iss
; ============================================================================

#define MyAppName "休息提醒"
#define MyAppVersion "6.1.7"
#define MyAppPublisher "CrazyStudio"
#define MyAppURL "https://github.com/binlo/rest-reminder"
#define MyAppExeName "RestReminder.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".reminder"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Basic settings
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Output
OutputDir=..\build\installer
OutputBaseFilename=RestReminder-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
; UI
WizardStyle=modern
SetupIconFile=..\cute_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
; Version info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=休息提醒 - 专注力管理挂件
VersionInfoCopyright=Copyright (C) 2025 CrazyStudio
; Languages
LanguageDetectionMethod=locale
; Misc
ShowTasksTreeLines=yes
ShowUndisplayableLanguages=yes
DisableDirPage=no
DisableProgramGroupPage=no
; Signing (uncomment if you have a code signing certificate)
; SignedUninstaller=yes
; SignTool=signtool

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop shortcut
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
; Start menu
Name: "startmenu"; Description: "创建开始菜单快捷方式"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
; Quick launch (optional)
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Icon
Source: "..\cute_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; License
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; Readme (optional)
Source: "..\README.zh.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Start menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\cute_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\文档"; Filename: "{app}\README.zh.md"
; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\cute_icon.ico"; Tasks: desktopicon

[Run]
; Run application after installation (optional, checked by default)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Registry]
; File association (optional)
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocName}"; ValueData: ""; Flags: uninsdeletevalue
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName} File"; Flags: uninsdeletekey
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\cute_icon.ico,0"
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Code]
// Helper functions
function IsAdminInstallMode: Boolean;
begin
  Result := IsAdminLoggedOn;
end;

// Initialize wizard pages
procedure InitializeWizard();
begin
  // Customize welcome page if needed
end;

// Final page checkboxes
var
  RunCheckBox: TCheckBox;
  InfoCheckBox: TCheckBox;

procedure InitializeSetupPage();
begin
  // Add checkboxes to the Finished page
  RunCheckBox := WizardForm.FinishedPage.CreateCheckBox;
  RunCheckBox.Caption := '运行 {#MyAppName}';
  RunCheckBox.Checked := True;
  RunCheckBox.Top := WizardForm.FinishedPage.SurfaceRect.Top + 20;
  RunCheckBox.Left := WizardForm.FinishedPage.SurfaceRect.Left + 20;
  RunCheckBox.Width := WizardForm.FinishedPage.SurfaceRect.Right - RunCheckBox.Left - 20;
  
  InfoCheckBox := WizardForm.FinishedPage.CreateCheckBox;
  InfoCheckBox.Caption := '查看重要更新信息！！';
  InfoCheckBox.Checked := False;
  InfoCheckBox.Top := RunCheckBox.Top + RunCheckBox.Height + 8;
  InfoCheckBox.Left := RunCheckBox.Left;
  InfoCheckBox.Width := RunCheckBox.Width;
end;

// Handle "Next" button on the Finished page
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Run the application if checkbox is checked
    if RunCheckBox.Checked then
    begin
      ShellExec('open', ExpandConstant('{app}\{#MyAppExeName}'), '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;
    
    // Show info if checkbox is checked
    if InfoCheckBox.Checked then
    begin
      MsgBox('休息提醒 v{#MyAppVersion}' + #13#10 + #13#10 +
             '主要更新：' + #13#10 +
             '• 修复了设置保存时的崩溃问题' + #13#10 +
             '• 优化了 AI 报告的主题一致性' + #13#10 +
             '• 更新了关于页的 AI 服务信息' + #13#10 + #13#10 +
             '详细更新日志请访问：' + #13#10 + '{#MyAppURL}',
             mbInformation, MB_OK);
    end;
  end;
end;

// Initialize on first page
procedure InitializeWizard();
begin
  InitializeSetupPage();
end;
