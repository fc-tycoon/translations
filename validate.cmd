@echo off
setlocal

REM One-click validator for Windows.
REM Uses PowerShell with ExecutionPolicy Bypass so non-technical contributors can run it.

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%validate.ps1"
set EXITCODE=%ERRORLEVEL%

if not %EXITCODE%==0 (
	echo.
	echo Validation failed. See errors above.
)

pause

exit /b %EXITCODE%
