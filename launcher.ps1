# --- Steam Vault Launcher (Windows) ---
# Dica: Se o script não executar, abra o PowerShell como Admin e rode:
# Set-ExecutionPolicy RemoteSigned

$VENV_DIR = "venv"

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python not found! Please install Python 3 from python.org" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Pause
    Exit
}

# Create Venv if missing
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $VENV_DIR
}

# Activate Venv
# PowerShell activation script path
$ActivateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
}
else {
    Write-Host "Error: Virtual environment activation script not found." -ForegroundColor Red
    Pause
    Exit
}

# Install Dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    pip install -r requirements.txt
    Write-Host "Dependencies satisfied." -ForegroundColor Green
}
catch {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    Pause
    Exit
}

# Run Application
python main.py
Pause
