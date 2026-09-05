@echo off
echo ============================================================
echo Starting AI Teacher - Human-Like Adaptive AI Educator
echo AI Innovation Hackathon 2026
echo ============================================================

start "AI Teacher Backend (FastAPI)" cmd /k "python backend/run_backend.py"
timeout /t 3 /nobreak >nul

start "AI Teacher Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo AI Teacher backend running at: http://127.0.0.1:8000
echo AI Teacher frontend running at: http://localhost:5173
echo.
pause
