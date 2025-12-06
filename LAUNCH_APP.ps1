# ========================================
# AI Skin Analysis - One-Click Launcher
# ========================================

$Host.UI.RawUI.WindowTitle = "AI Skin Analysis Application"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   AI Skin Analysis - Starting Application" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Start the Flask application
Write-Host "Starting web server..." -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Application will open in your browser shortly" -ForegroundColor White
Write-Host "Access URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Start browser after 3 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:5000"
} | Out-Null

# Run the application
python app.py
