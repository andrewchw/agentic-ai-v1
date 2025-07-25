#!/usr/bin/env powershell

# ========================================
# SECURE ENVIRONMENT SETUP SCRIPT
# Agentic AI Revenue Assistant
# ========================================

Write-Host "🔐 Setting up secure environment..." -ForegroundColor Green

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "⚠️  Found existing .env file" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "❌ Setup cancelled. Please manually update your .env file." -ForegroundColor Red
        exit 1
    }
}

# Get API key from user
Write-Host ""
Write-Host "🔑 Please enter your OpenRouter API key:" -ForegroundColor Cyan
Write-Host "   You can get one from: https://openrouter.ai/keys" -ForegroundColor Gray
$apiKey = Read-Host -MaskInput

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ API key cannot be empty!" -ForegroundColor Red
    exit 1
}

# Validate API key format
if (-not $apiKey.StartsWith("sk-or-v1-")) {
    Write-Host "⚠️  Warning: API key doesn't match expected OpenRouter format (sk-or-v1-...)" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "❌ Setup cancelled." -ForegroundColor Red
        exit 1
    }
}

# Create .env file
$envContent = @"
# OpenRouter API Configuration
OPENROUTER_API_KEY=$apiKey

# LiteLLM Configuration
LITELLM_LOG=INFO

# CrewAI Configuration
ENABLE_PREMIUM_BACKUP=true

# Security Settings
ENVIRONMENT=development
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host ""
Write-Host "✅ Environment file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🔒 SECURITY REMINDERS:" -ForegroundColor Yellow
Write-Host "   • .env file is already in .gitignore" -ForegroundColor Gray
Write-Host "   • Never commit API keys to git repositories" -ForegroundColor Gray
Write-Host "   • Rotate your API keys regularly" -ForegroundColor Gray
Write-Host "   • Monitor your OpenRouter usage at https://openrouter.ai/activity" -ForegroundColor Gray
Write-Host ""

# Set environment variables for current session
$env:OPENROUTER_API_KEY = $apiKey
$env:LITELLM_LOG = "INFO"
$env:ENABLE_PREMIUM_BACKUP = "true"

Write-Host "🚀 Environment variables set for current session!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   streamlit run src\main.py" -ForegroundColor Gray
Write-Host ""
