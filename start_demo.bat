@echo off
echo ============================================================
echo    InvoiceShield - Starting Backend and Frontend
echo ============================================================
echo.

REM Check if backend is already running
echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is already running at http://localhost:8000
    echo.
) else (
    echo Starting backend server...
    echo Backend will run at http://localhost:8000
    echo.
    start "InvoiceShield Backend" cmd /k "uvicorn app.main:app --reload"
    timeout /t 3 /nobreak >nul
)

echo Starting frontend server...
echo Frontend will run at http://localhost:3000
echo.
cd frontend
start "InvoiceShield Frontend" cmd /k "python serve.py"

echo.
echo ============================================================
echo    InvoiceShield is ready!
echo ============================================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Browser should open automatically.
echo Press any key to close this window...
pause >nul
