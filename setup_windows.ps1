# Windows PowerShell Setup Script for Agentic AI Revenue Assistant
# Run this script in PowerShell as Administrator if needed

Write-Host "🚀 Setting up Agentic AI Revenue Assistant for Windows..." -ForegroundColor Green

# Check Python installation
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.12 from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "🔨 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️ Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📥 Installing project dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Some dependencies failed to install. Check the output above." -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host "🔑 Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ No .env file found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your API keys before running the application!" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Install Playwright browsers for E2E testing
Write-Host "🎭 Setting up Playwright for testing..." -ForegroundColor Yellow
python -m playwright install --with-deps

# Setup complete
Write-Host ""
Write-Host "🎉 Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Edit .env file with your OpenRouter API key" -ForegroundColor Cyan
Write-Host "2. Test the app: python run_tests.py check" -ForegroundColor Cyan
Write-Host "3. Run the app: streamlit run src/main.py --server.port 8502" -ForegroundColor Cyan
Write-Host "4. Run full tests: python run_tests.py all" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Yellow 