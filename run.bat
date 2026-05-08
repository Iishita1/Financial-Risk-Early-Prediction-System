@echo off
REM Quick start script for Financial Health Check App

echo.
echo ========================================
echo  Financial Health Check App
echo ========================================
echo.

REM Check if Flask is installed
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements-app.txt
)

echo.
echo Starting app...
echo.
echo ========================================
echo  App running at: http://localhost:5000
echo  Press Ctrl+C to stop
echo ========================================
echo.

python app.py
