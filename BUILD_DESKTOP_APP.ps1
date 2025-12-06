# ========================================
# AI Skin Analysis - Desktop App Builder
# ========================================
# This script builds a standalone Windows executable

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   AI Skin Analysis - Desktop App Builder" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

# Install PyInstaller if not present
Write-Host "Checking PyInstaller installation..." -ForegroundColor Green
pip list | Select-String "pyinstaller" -Quiet
if (-not $?) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the application
Write-Host ""
Write-Host "Building desktop application..." -ForegroundColor Green
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

pyinstaller --clean skin_app.spec

# Check if build was successful
if (Test-Path "dist\SkinAnalysisApp\SkinAnalysisApp.exe") {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "   BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your desktop app is ready at:" -ForegroundColor Cyan
    Write-Host "  dist\SkinAnalysisApp\SkinAnalysisApp.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test the app by running the exe file" -ForegroundColor White
    Write-Host "2. Create a desktop shortcut for easy access" -ForegroundColor White
    Write-Host "3. The entire 'dist\SkinAnalysisApp' folder can be copied to any Windows PC" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "BUILD FAILED - Check error messages above" -ForegroundColor Red
    Write-Host ""
}

pause
