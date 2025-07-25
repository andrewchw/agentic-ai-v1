# Launch Agentic AI Revenue Assistant with CrewAI Support
# This script ensures the Streamlit app runs in the venv environment where CrewAI is installed

Write-Host "🚀 Launching Agentic AI Revenue Assistant with CrewAI Support..." -ForegroundColor Green
Write-Host "📁 Working Directory: $(Get-Location)" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Set OpenRouter API key for CrewAI integration (load from .env file)
Write-Host "🔑 Loading OpenRouter API key from .env file..." -ForegroundColor Yellow
# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^OPENROUTER_API_KEY=(.+)$") {
            $env:OPENROUTER_API_KEY = $Matches[1]
            Write-Host "✅ OpenRouter API key loaded from .env file" -ForegroundColor Green
        }
    }
} else {
    Write-Host "⚠️  .env file not found - please ensure OPENROUTER_API_KEY is set" -ForegroundColor Yellow
}

# Verify CrewAI installation
Write-Host "🧪 Verifying CrewAI installation..." -ForegroundColor Yellow
python -c "
try:
    import crewai
    from crewai_integration_bridge import process_agent_collaboration_with_crewai
    print('✅ CrewAI integration ready!')
    print(f'CrewAI version: {crewai.__version__}')
except Exception as e:
    print(f'❌ CrewAI issue: {e}')
    exit(1)
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎯 Starting Streamlit application with CrewAI support..." -ForegroundColor Green
    streamlit run src/main.py --server.port 8501 --server.address localhost
} else {
    Write-Host "❌ CrewAI verification failed. Please check installation." -ForegroundColor Red
    pause
}
