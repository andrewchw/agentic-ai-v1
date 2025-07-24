# Launch Agentic AI Revenue Assistant with CrewAI Support
# This script ensures the Streamlit app runs in the venv environment where CrewAI is installed

Write-Host "🚀 Launching Agentic AI Revenue Assistant with CrewAI Support..." -ForegroundColor Green
Write-Host "📁 Working Directory: $(Get-Location)" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Set OpenRouter API key for CrewAI integration
Write-Host "🔑 Setting OpenRouter API key for CrewAI..." -ForegroundColor Yellow
$env:OPENROUTER_API_KEY="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"

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
