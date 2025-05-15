# Simple restart script for the stock screener application
# Usage: Run this script from the project root in PowerShell

# Configure ports
$BACKEND_PORT = 8002
$FRONTEND_PORT = 3000

# Kill any existing processes
Write-Host "Stopping any running processes..." -ForegroundColor Cyan
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name npm -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object { $_.Name -eq "powershell" -and ($_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*npm start*") } | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Set the environment variable for the frontend
Write-Host "Creating frontend environment file..." -ForegroundColor Cyan
Set-Content -Path "web-frontend/.env" -Value "REACT_APP_API_BASE=http://localhost:$BACKEND_PORT" -Force

# Start backend in a new window
Write-Host "Starting backend on port $BACKEND_PORT..." -ForegroundColor Cyan
Start-Process "powershell" -ArgumentList "-Command cd web-backend; .\venv\Scripts\activate; python -m uvicorn main:app --port $BACKEND_PORT"

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting frontend on port $FRONTEND_PORT..." -ForegroundColor Cyan
Start-Process "powershell" -ArgumentList "-Command cd web-frontend; npm start"

Write-Host @"

Application started!
==================
Backend: http://localhost:$BACKEND_PORT
Frontend: http://localhost:$FRONTEND_PORT

You can verify the backend is working by visiting:
http://localhost:$BACKEND_PORT/docs
"@ -ForegroundColor Green 