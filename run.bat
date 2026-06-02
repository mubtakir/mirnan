@echo off
title mirnan V8
cd /d "%~dp0"
set PYTHONPATH=%~dp0

cls
echo.
echo ============================================
echo   mirnan V8 - Partonic Resonance
echo ============================================
echo.
echo   1. CLI - Interactive Terminal
echo   2. Web UI - http://127.0.0.1:8000
echo   3. Physics Demo - Full Evaluation
echo   4. Physics Trace - Step by Step
echo   5. Physics Validation
echo   6. Run Tests (123 checks)
echo   7. Exit
echo.

set /p CHOICE="Select option: "

if "%CHOICE%"=="1" call :cli
if "%CHOICE%"=="2" call :web
if "%CHOICE%"=="3" call :demo
if "%CHOICE%"=="4" call :trace
if "%CHOICE%"=="5" call :validate
if "%CHOICE%"=="6" call :tests
if "%CHOICE%"=="7" exit /b
echo Invalid.
pause
goto :eof

:cli
python cli.py -i
pause
exit /b

:web
echo Starting server at http://127.0.0.1:8000
echo Press Ctrl+C to stop.
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
pause
exit /b

:demo
python physics_demo.py --full --prompt "alsalam alaykum" --max-words 8
pause
exit /b

:trace
set /p P="Enter prompt: "
if "%P%"=="" set P=alsalam alaykum
python physics_demo.py --prompt "%P%" --max-words 6
pause
exit /b

:validate
python physics_demo.py --validate --compare
pause
exit /b

:tests
pytest tests/ -v
pause
exit /b
