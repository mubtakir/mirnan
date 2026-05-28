@echo off
chcp 65001 >nul
title mirnan V7 - Physics Orchestrator
cd /d "%~dp0"
set PYTHONPATH=%~dp0

echo.
echo ======================================
echo   mirnan V7 - Physics Orchestrator
echo   DCCF + PPM + AMFS + 16 Arabic Meters
echo ======================================
echo.
echo  1. CLI - Terminal Interface
echo  2. Web - Browser (http://127.0.0.1:8000)
echo  3. Run Tests (pytest - 108 checks)
echo  4. Physics Report (quick demo)
echo  5. Poetic Demo (poetry example)
echo  6. Exit
echo.

set /p CHOICE="Select (1-6): "

if "%CHOICE%"=="1" (
    echo.
    echo Starting CLI...
    python cli.py -i
    pause
    goto :eof
)
if "%CHOICE%"=="2" (
    echo.
    echo Starting server at http://127.0.0.1:8000
    echo Press Ctrl+C to stop.
    echo.
    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    pause
    goto :eof
)
if "%CHOICE%"=="3" (
    echo.
    pytest tests/ -v
    pause
    goto :eof
)
if "%CHOICE%"=="4" (
    echo.
    python cli.py "السلام عليكم" --mode quantum --report
    pause
    goto :eof
)
if "%CHOICE%"=="5" (
    echo.
    python cli.py "يا ليت قومي يعلمون" --mode poetic --meter kamil --report
    pause
    goto :eof
)
if "%CHOICE%"=="6" (
    exit /b
)

echo.
echo Invalid choice.
pause