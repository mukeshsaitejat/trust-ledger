@echo off
echo ============================================================
echo    InvoiceShield - Starting Backend and Frontend
echo ============================================================
echo.

REM Start backend
echo Starting backend server...
cd backend
start "InvoiceShield Backend" cmd /k "uvicorn app.main:app --reload"
cd ..

timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend-react
start "InvoiceShield Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ============================================================
echo    InvoiceShield is starting!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Servers are starting in separate windows...
echo.
pause
