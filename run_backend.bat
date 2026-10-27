@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Interview Accelerator Backend (FastAPI)...
echo URL: http://127.0.0.1:8005
echo Docs: http://127.0.0.1:8005/docs
echo ========================================================
"C:\Users\Sonu\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8005 --reload
pause
