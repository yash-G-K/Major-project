@echo off
echo Starting AI Skin Analysis Application...
echo.

REM Change to the project directory
cd /d "c:\Users\ASUS\OneDrive\Desktop\major project\full major project"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment and start the app
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -r requirements.txt >nul 2>&1

echo.
echo ========================================
echo    AI Skin Analysis Application
echo ========================================
echo.
echo Application starting on: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo ========================================
echo.

python app.py

pause