[Setup]
AppName=Roman Clock
AppVersion=1.0
DefaultDirName={autopf}\RomanClock
DefaultGroupName=Roman Clock
OutputDir=.
OutputBaseFilename=RomanClockInstaller
SetupIconFile=clock.ico

[Files]
Source: "dist\rrtctw.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Roman Clock"; Filename: "{app}\rrtctw.exe"
Name: "{commondesktop}\Roman Clock"; Filename: "{app}\rrtctw.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
