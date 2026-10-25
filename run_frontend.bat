@echo off
cd /d "%~dp0frontend"
echo ========================================================
echo Starting Interview Accelerator Frontend (Vite + React)...
echo URL: http://127.0.0.1:5173
echo ========================================================
call npm run dev -- --host 127.0.0.1 --port 5173
pause
