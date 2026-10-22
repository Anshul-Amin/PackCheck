# PackCheck Windows PowerShell Setup Script
Write-Host "Setting up PackCheck environment on Windows..." -ForegroundColor Cyan

# 1. Create virtual environment if missing
if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment (.venv)..."
    python -m venv .venv
}

# 2. Activate virtual environment
Write-Host "Activating virtual environment..."
& .venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
Write-Host "Installing pinned dependencies from requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Copy .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..."
    Copy-Item .env.example .env
    Write-Host "Remember to add your GEMINI_API_KEY to .env (from aistudio.google.com)" -ForegroundColor Yellow
}

# 5. Run tests
Write-Host "Running automated tests..."
python -m pytest tests/ -v

Write-Host "`nSetup complete! Run the app with: python tasks.py run" -ForegroundColor Green
