@echo off
title SourceIQ — Local Development Launcher
echo =====================================================================
echo   SourceIQ — AI Answers. Verifiable Sources.
echo   Launching Local Development Environment (Native Windows)
echo =====================================================================
echo.

:: 1. Launch Backend in new window
echo [*] Starting FastAPI Backend (http://127.0.0.1:8000)...
start "SourceIQ Backend (FastAPI)" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:: 2. Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

:: 3. Launch Frontend in new window
echo [*] Starting Next.js Frontend (http://localhost:3000)...
start "SourceIQ Frontend (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo =====================================================================
echo   Services are running!
echo   - Backend API Docs:   http://127.0.0.1:8000/docs
echo   - Frontend Web App:   http://localhost:3000
echo   - Health Check:       http://127.0.0.1:8000/api/v1/health
echo =====================================================================
echo Press any key to close this launcher launcher window...
pause >nul
