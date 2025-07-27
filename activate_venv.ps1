# Activate venv script for Agentic AI project
# This script activates the virtual environment for the project

Write-Host "🚀 Activating Agentic AI venv environment..." -ForegroundColor Green

# Check if venv exists
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    # Activate the virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    Write-Host "📍 Project: Agentic AI Revenue Assistant" -ForegroundColor Cyan
    Write-Host "🐍 Python version:" -ForegroundColor Yellow
    python --version
    Write-Host ""
    Write-Host "📦 Key packages installed:" -ForegroundColor Yellow
    pip list | findstr -i "streamlit pandas crewai"
    Write-Host ""
    Write-Host "🔧 Ready for development! Available commands:" -ForegroundColor Cyan
    Write-Host "  streamlit run src/main.py --server.port 8502" -ForegroundColor White
    Write-Host "  python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080" -ForegroundColor White
    Write-Host "  task-master list" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Virtual environment not found at .\venv\" -ForegroundColor Red
    Write-Host "💡 Please run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "💡 Then run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}
