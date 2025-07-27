# Start Lead Intelligence Agent on Port 8502
# This script starts the main Lead Intelligence Agent application
# Port 8502 is used to avoid conflicts with Agent Collaboration Dashboard (port 8501)

Write-Host "🤖 Starting Lead Intelligence Agent..." -ForegroundColor Green
Write-Host "📊 Port: 8502" -ForegroundColor Cyan
Write-Host "🔗 URL: http://localhost:8502" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "🔑 Loading environment variables..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^(.+)=(.+)$") {
            $varName = $Matches[1]
            $varValue = $Matches[2]
            [Environment]::SetEnvironmentVariable($varName, $varValue, "Process")
        }
    }
    Write-Host "✅ Environment variables loaded" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting Lead Intelligence Agent on port 8502..." -ForegroundColor Green
Write-Host "   Access at: http://localhost:8502" -ForegroundColor Cyan
Write-Host ""

# Start the Streamlit application on port 8502
streamlit run src/main.py --server.port 8502 --server.address localhost
