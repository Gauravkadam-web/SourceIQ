# ==============================================================================
# SourceIQ — Local Development Launcher (PowerShell)
# Launches native FastAPI backend and Next.js frontend concurrently.
# ==============================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  SourceIQ — AI Answers. Verifiable Sources." -ForegroundColor White
Write-Host "  Launching Local Development Environment (Native Windows)" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start FastAPI Backend in a new window
Write-Host "[*] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3

# 2. Start Next.js Frontend in a new window
Write-Host "[*] Launching Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\frontend'; npm run dev"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  SourceIQ Services Active:" -ForegroundColor White
Write-Host "  - Frontend Web UI:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Backend API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "  - Health Check:     http://127.0.0.1:8000/api/v1/health" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
