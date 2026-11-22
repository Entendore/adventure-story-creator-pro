@echo off
REM Adventure Story Creator Pro - Launcher (Windows)
cd /d "%~dp0"

if not exist "venv" (
    echo Virtual environment not found. Run setup_project.sh first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python src\main.py %*
