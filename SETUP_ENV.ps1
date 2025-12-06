# PowerShell script to set up a clean Python 3.11 virtual environment
# Usage: Run in project root:  .\SETUP_ENV.ps1

param(
    [string]$PythonVersion = "3.11",
    [string]$EnvName = "venv"
)

Write-Host "[+] Checking for 'py' launcher" -ForegroundColor Cyan
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $pyLauncher) {
    Write-Host "[!] 'py' launcher not found. Install Python from https://www.python.org" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Creating virtual environment with Python $PythonVersion" -ForegroundColor Cyan
py -$PythonVersion -m venv $EnvName
if (-not (Test-Path $EnvName)) {
    Write-Host "[!] Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Activating virtual environment" -ForegroundColor Cyan
$activate = Join-Path $EnvName "Scripts\Activate.ps1"
. $activate

Write-Host "[+] Upgrading pip" -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "[+] Installing core dependencies" -ForegroundColor Cyan
pip install -r requirements.txt --no-cache-dir

Write-Host "[+] Verifying critical imports" -ForegroundColor Cyan
python - <<'EOF'
modules = ["flask","tensorflow","cv2","pandas","reportlab","PIL"]
for m in modules:
    try:
        __import__(m)
        print(f"[OK] {m}")
    except Exception as e:
        print(f"[FAIL] {m}: {e}")
EOF

Write-Host "[+] Environment setup completed." -ForegroundColor Green
Write-Host "Run the app:  python app.py" -ForegroundColor Yellow
