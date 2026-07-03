@echo off
REM ===========================================================================
REM  LDS Generator - one-click desktop setup
REM
REM  Installs uv (if needed), syncs the Python environment, and launches the app.
REM  Installs ONLY Python dependencies. Does NOT install Ollama or download any
REM  model weights - the optional model fallback is separate and opt-in (see
REM  docs/background.md).
REM ===========================================================================

echo Checking for uv...
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "UV=uv"
    goto :sync
)

echo Installing uv...
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"

REM A fresh install adds uv to PATH for FUTURE sessions only, so locate the
REM binary directly for this run.
if exist "%USERPROFILE%\.local\bin\uv.exe" (
    set "UV=%USERPROFILE%\.local\bin\uv.exe"
) else (
    echo.
    echo uv was installed but could not be found on PATH.
    echo Close this window, open a new one, and run setup.bat again.
    pause
    exit /b 1
)

:sync
echo Syncing environment...
%UV% sync
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo uv sync failed. See the error above.
    pause
    exit /b 1
)

echo.
echo Setup complete.
echo   Run the CLI:   uv run lds --help
echo   Launch the UI: uv run python -m lds.webapp.app   (available from Phase 6)
pause
