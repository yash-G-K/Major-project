@echo off
REM ========================================
REM AI Skin Analysis - One-Click Launcher
REM ========================================

title AI Skin Analysis Application

echo ================================================
echo    AI Skin Analysis - Starting Application
echo ================================================
echo.

REM Activate virtual environment
echo Activating environment...
call .venv\Scripts\activate.bat

REM Start the Flask application
echo Starting web server...
echo.
echo ================================================
echo Application will open in your browser shortly
echo Access URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Start browser after 3 seconds
start /B timeout /t 3 /nobreak >nul && start http://localhost:5000

REM Run the application
python app.py

pause
